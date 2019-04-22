import os
from unittest import TestCase
from wetransfer import TransferApi


class TestAuthentication(TestCase):
    def setUp(self):
        try:
            self.transfer_api = TransferApi(os.environ['WE_API_KEY'])

        except KeyError:
            self.skipTest('Oops. You forgot to set the WE_API_KEY.')

    def test_authentication(self):
        self.assertTrue(self.transfer_api.is_authenticated())
