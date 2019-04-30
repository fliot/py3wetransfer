import os
import subprocess
from unittest import TestCase
from wetransfer import TransferApi
from wetransfer.exc import TransferError

image_dir = './wetransfer/tests/images/'
images = ['we_483_lines.jpg', 'we_nytimes_copy.jpg']  # actual WeTransfer images


class TestTransfer(TestCase):
    def setUp(self):
        try:
            self.transfer_api = TransferApi(os.environ['WE_API_KEY'])

        except KeyError:
            self.skipTest('Oops. You forgot to set the WE_API_KEY.')

    def test_single_file_upload(self):
        try:
            filepath = image_dir + images[0]
            self.transfer_api.upload_file('Upload an image', filepath)

        except TransferError as e:
            self.fail('Oops. Uploading an image caused to API to raise an error: %s' % e)

    def test_multi_file_upload(self):
        try:
            filepaths = [image_dir + x for x in images]
            self.transfer_api.upload_files('Upload multiple images', filepaths)

        except TransferError as e:
            self.fail('Oops. Uploading an image caused to API to raise an error: %s' % e)

    def test_large_file_upload(self):
        def run_command(cmd, file_name):
            cmd = cmd % file_name
            subprocess.run(cmd.split(' '))

        filename = '/tmp/we_rnd.bin'
        create_random_file_sh = 'dd if=/dev/urandom of=%s count=6144 bs=1024 iflag=fullblock status=none'
        delete_random_file_sh = 'rm -rf %s'
        try:
            run_command(create_random_file_sh, filename)

            self.transfer_api.upload_file('Upload a rather large file', filename)

        except TransferError as e:
            self.fail('Oops. Uploading an image caused to API to raise an error: %s' % e)

        finally:
            run_command(delete_random_file_sh, filename)
