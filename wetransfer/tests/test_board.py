import os
import unittest
from wetransfer import BoardApi
from wetransfer.exc import TransferError

image_dir = './wetransfer/tests/images/'
images = ['we_483_lines.jpg', 'we_nytimes_copy.jpg']  # actual WeTransfer images

unittest.TestLoader.sortTestMethodsUsing = None


class TestBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        We only want to create a single board for all tests in this file, which is why
        we use the classmethod setUpClass.
        """
        cls.board_id = None

        try:
            cls.board_api = BoardApi(os.environ['WE_API_KEY'])
        except KeyError:
            super().skipTest('Oops. You forgot to set the WE_API_KEY.')

        try:
            board_id, board_url = cls.board_api.create_new_board('test board')
            cls.board_id = board_id

        except TransferError as e:
            super().fail('Oops. Uploading an image caused to API to raise an error: %s' % e)

    def test_add_links(self):
        links = [{
            'title': 'Google',
            'url': 'https://google.com',
        }, {
            'title': 'WeTransfer',
            'url': 'https://wetransfer.com',
        }]

        try:
            self.board_api.add_links_to_board(self.board_id, links)

        except TransferError as e:
            self.fail('Oops. Adding links to board caused API to raise an error: %s' % e)

    def test_add_files(self):
        filepaths = [image_dir + x for x in images]

        try:
            self.board_api.add_files_to_board(self.board_id, filepaths)

        except TransferError as e:
            self.fail('Oops. Adding files to board caused API to raise an error: %s' % e)

    def test_get_board(self):
        try:
            board_info = self.board_api.get_board(self.board_id)

            self.assertEqual('test board', board_info['name'])

            items = board_info['items']
            self.assertEqual(4, len(items), 'Oops. Expected a total of 4 items.')

            links = [x for x in items if x['type'] == 'link']
            files = [x for x in items if x['type'] == 'file']

            self.assertEqual(2, len(links), 'Oops. Expected a total of 2 links.')
            self.assertEqual(2, len(files), 'Oops. Expected a total of 2 files.')

        except TransferError as e:
            self.fail('Oops. Getting board info caused API to raise an error: %s' % e)
