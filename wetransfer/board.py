import json
import logging
from .base import WeTransferBase
from .file import File

LOG = logging.getLogger("wetransfer")
LOG.addHandler(logging.NullHandler())
LOG.setLevel(logging.INFO)


class Board(WeTransferBase):

    def get_board(self, board_id):
        """
        Get a board based on board_id
        :param board_id: board id
        :return: board information
        """
        _, body = self.get('boards/%s' % board_id, status=200)
        return body

    def create_new_board(self, name):
        """
        Create a new board
        :param name: Name of new board
        :return: id, url tuple
        """
        data = {'name': name}
        LOG.debug(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        _, body = self.post('boards', data=json.dumps(data), status=201)
        return body['id'], body['url']

    def add_links_to_board(self, board_id, data):
        """
        Add links to a board. The data must be a list containing of link objects, with
        a link object being a dict with a title and a url.
        :param board_id: Board id
        :param data: Data
        :return: Board info (see get_board())
        """
        self.post('boards/%s/links' % board_id, data=json.dumps(data), status=201)
        return self.get_board(board_id)

    def __complete_file_upload_board(self, board_id, file_id):
        """
        Mark the file upload as complete
        :param board_id: Board id
        :param file_id: File id
        :return: None
        """
        self.put('boards/%s/files/%s/upload-complete' % (board_id, file_id), status=202)

    def __request_upload_url_board(self, board_id, file_id, part_number, multipart_upload_id):
        """
        Request special upload url, which is tailored for AWS S3
        :param board_id: Board id
        :param file_id: File id
        :param part_number: part number
        :param multipart_upload_id: multipart upload id
        :return: url
        """
        _, body = self.get('boards/%s/files/%s/upload-url/%s/%s' %
                           (board_id, file_id, part_number, multipart_upload_id),
                           status=200)
        return body['url']

    def add_files_to_board(self, board_id, filepaths):
        """
        Add files to board
        :param board_id: Board id
        :param filepaths: list of filepaths
        :return:
        """
        files = [File(filepath) for filepath in filepaths]
        data = [{'name': file.name, 'size': file.size} for file in files]
        LOG.debug(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        _, body = self.post('boards/%s/files' % board_id, data=json.dumps(data), status=201)

        LOG.debug(json.dumps(body, sort_keys=True, indent=4, separators=(',', ': ')))

        upload_plans = body
        for i in range(len(upload_plans)):
            file = files[i]
            upload_plan = upload_plans[i]
            multipart = upload_plan['multipart']
            part_number = 1
            with open(file.path, 'rb') as fh:
                while True:
                    bytes_read = fh.read(multipart['chunk_size'])
                    if not bytes_read:  # empty string?
                        break

                    url = self.__request_upload_url_board(board_id, upload_plan['id'], part_number, multipart['id'])
                    self.s3_file_upload(url, bytes_read)
                    part_number += 1

            self.__complete_file_upload_board(board_id, upload_plan['id'])

        return self.get_board(board_id)
