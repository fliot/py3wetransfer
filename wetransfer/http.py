from abc import ABC, abstractmethod
import json
import logging
import requests
from .exc import TransferError

LOG = logging.getLogger("wetransfer")
LOG.addHandler(logging.NullHandler())
LOG.setLevel(logging.INFO)


def http_response(func):
    def wrapper_http_response(*args, **kwargs):
        """
        The wrapper calls the original function, then uses the response object
        to create a <status_code, body> tuple for further use.
        If a keyword argument called 'status' is found, it is used to check the
        status code. If the actual status code does not equal the expected one,
        an error will be raised. Used for get, put, post.
        """
        expected_status = None
        if 'status' in kwargs:
            expected_status = kwargs['status']
            del kwargs['status']

        r = func(*args, **kwargs)
        LOG.debug(r.text)
        status = r.status_code
        body = json.loads(r.text)
        if expected_status is not None and expected_status != status:
            LOG.error(status, body['message'])
            raise TransferError('%d: %s' % (status, body['message']))

        return status, body

    return wrapper_http_response


class HttpClient(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def authorization_headers(self):
        pass

    @abstractmethod
    def endpoint(self, address):
        pass

    @http_response
    def get(self, address):
        """
        convenience method to GET
        :param address: URL endpoint
        :return: response object
        """
        headers = self.authorization_headers()
        LOG.info('GET Address: %s' % address)
        LOG.debug('Headers: %s' % headers)
        return requests.get(self.endpoint(address), headers=headers)

    @http_response
    def post(self, address, **kwargs):
        """from wetransfer.exc import WeTransferError

        Convenience method to POST
        :param address: URL endpoint
        :param kwargs: headers, data, etc.
        :return: response object
        """
        kwargs['headers'] = self.authorization_headers()
        LOG.info('POST Address: %s' % address)
        LOG.debug('Headers: %s' % kwargs['headers'])
        return requests.post(self.endpoint(address), **kwargs)

    @http_response
    def put(self, address, **kwargs):
        """
        Convenience method to PUT
        :param address: URL endpoint
        :param kwargs: headers
        :return: response object
        """
        kwargs['headers'] = self.authorization_headers()
        LOG.info('PUT Address: %s' % address)
        LOG.debug('Headers: %s' % kwargs['headers'])
        return requests.put(self.endpoint(address), **kwargs)
