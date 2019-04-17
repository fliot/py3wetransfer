import json
import logging
from .base import WeTransferBase
from .exc import WeTransferError

LOG = logging.getLogger("py3-wetransfer")
LOG.addHandler(logging.NullHandler())
LOG.setLevel(logging.INFO)


class Board(WeTransferBase):

    def get_board(self, board_id):
        """
        Get a board based on board_id
        :param board_id: board id
        :return: board information
        """
        status_code, body = self.get('boards/%s' % board_id)
        if status_code != 200:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        return body

    def create_new_board(self, name):
        """
        Create a new board
        :param name: Name of new board
        :return: id, url tuple
        """
        data = {'name': name}
        LOG.debug(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        status_code, body = self.post('boards', data=json.dumps(data))
        if status_code != 201:
            LOG.error(body['message'])
            raise WeTransferError(body['message'])

        return body['id'], body['url']
