import json
import logging
import requests
from .exc import WeTransferError
from .file import File
from .http import HttpClient

LOG = logging.getLogger("py3-wetransfer")
LOG.addHandler(logging.NullHandler())
LOG.setLevel(logging.INFO)


class WeTransfer(HttpClient):
    WE_ENDPOINT_DEV = 'https://dev.wetransfer.com'

    def __init__(self, api_key, user_identifier=None):
        super().__init__()

        self.__x_api_key = api_key
        self.__user_identifier = user_identifier

        self.__token = None

        self.__authorize()

    def endpoint(self, method):
        """
        Get endpoint for certain API method. Version v2.
        :param method: method to append to endpoint
        :return: endpoint for method
        """
        return '%s/%s/%s' % (self.WE_ENDPOINT_DEV, 'v2', method)

    def __base_authorization_headers(self):
        """
        Get base authorization headers.
        :return: headers
        """
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.__x_api_key
        }
        return headers

    def authorization_headers(self):
        """
        Get authorization headers.
        :return: headers
        """
        base_headers = self.__base_authorization_headers()
        headers = {'Authorization': self.__token}
        return {**headers, **base_headers}

    def __authorize(self):
        """
        Authorize user based on x-api-key only. Store returned bearer token for future use.
        :return: None
        """
        address = self.endpoint('authorize')
        headers = self.__base_authorization_headers()
        kwargs = {'headers': headers}
        if self.__user_identifier is not None:
            kwargs['data'] = {'user_identifier': self.__user_identifier}

        r = requests.post(address, **kwargs)
        body = json.loads(r.text)
        if r.status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        self.__token = 'Bearer %s' % body['token']

    def __finalize_transfer(self, transfer_id):
        """
        Finalize transfer.
        :param transfer_id: transfer id.
        :return: WeTransfer URL
        """
        status_code, body = self.put('transfers/%s/finalize' % transfer_id)
        if status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        return body['url']

    def __complete_file_upload(self, transfer_id, file_id, part_numbers):
        """
        Complete file upload.
        :param transfer_id: transfer id
        :param file_id: file id
        :param part_numbers: part numbers
        :return: None
        """
        data = {'part_numbers': part_numbers}
        LOG.debug(json.dumps(data, sort_keys=True, indent=2, separators=(',', ': ')))
        status_code, body = self.put('transfers/%s/files/%s/upload-complete' % (transfer_id, file_id),
                                     data=json.dumps(data))
        if status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

    @staticmethod
    def __s3_file_upload(url, filedata):
        """
        Convenience function to explicitly upload files to S3
        :param url: S3 endpoint
        :param filedata: actual data
        :return: None
        """
        r = requests.put(url, data=filedata)
        if r.status_code != 200:
            LOG.error(r.text)
            raise WeTransferError('Error uploading file(s) to AWS S3.')

    def __request_upload_url(self, transfer_id, file_id, part_number):
        """
        Request special upload url, which is tailored for AWS S3
        :param transfer_id: transfer id
        :param file_id: file id
        :param part_number: part number
        :return: AWS S3 upload url
        """
        status_code, body = self.get('transfers/%s/files/%s/upload-url/%s' % (transfer_id, file_id, part_number))
        if status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        return body['url']

    def __create_transfer(self, message, files):
        """
        Create a new transfer.
        :param message: Message that goes with the transfer
        :param files: An array of files
        :return:
        """
        files_stream = [{'name': file.name, 'size': file.size} for file in files]
        data = {'message': message, 'files': files_stream}

        status_code, body = self.post('transfers', data=json.dumps(data))
        if status_code != 201:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        LOG.debug(json.dumps(body, sort_keys=True, indent=2, separators=(',', ': ')))

        files_info = body['files']
        for i in range(len(files_info)):
            file_info = files_info[i]
            multipart = file_info['multipart']

            file = files[i]
            file.id = file_info['id']
            file.part_numbers = multipart['part_numbers']
            file.chunk_size = multipart['chunk_size']

        return body['id']

    def upload_files(self, message, filepaths):
        """
        Main entrypoint for this class. Pass in a message and a list of filepaths to upload.
        :param message: Message to go with uploads
        :param filepaths: A list of filepaths of files to upload
        :return: The download URL generated by WeTransfer
        """
        files = [File(filepath) for filepath in filepaths]
        transfer_id = self.__create_transfer(message, files)
        for file in files:
            part_number = 1
            with open(file.path, 'rb') as fh:
                while True:
                    bytes_read = fh.read(file.chunk_size)
                    if not bytes_read:  # empty string?
                        break

                    url = self.__request_upload_url(transfer_id, file.id, part_number)
                    self.__s3_file_upload(url, bytes_read)
                    part_number += 1

            self.__complete_file_upload(transfer_id, file.id, file.part_numbers)

        return self.__finalize_transfer(transfer_id)
