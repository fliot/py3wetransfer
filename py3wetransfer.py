#!/usr/bin/python
# coding: utf-8

import json, logging, magic, os, requests
import http.client as http_client

mime = magic.Magic(mime=True)

class Py3WeTransfer(object):
    debug = False
    x_api_key = ""
    user_identifier = ""
    token = ""
    
    # The class "constructor" is de facto an initializer 
    def __init__(self, x_api_key, user_identifier, debug=False):
        self.x_api_key = x_api_key
        self.user_identifier = user_identifier
        self.debug = debug
        if self.debug:
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
    
    def upload_file(self, file_path, message):
        
        mime_type = mime.from_file(file_path)
        file_name = os.path.basename(file_path)
        
        if self.token == "": self.authorize()
        [transfer_id, file_id, part_numbers, chunk_size] = self.create_new_transfer(message, file_name, os.path.getsize(file_path))
        
        i = 0
        urls = []
        for part_number in range(1, part_numbers + 1):
            urls.append(self.request_upload_url(transfer_id, file_id, part_number))
        
        f = open(file_path, "rb")
        bytes_read = f.read(chunk_size)
        while bytes_read:
            self.file_upload(urls[i], file_name, mime_type, bytes_read)
            bytes_read = f.read(chunk_size)
            i += 1
        f.close()
        self.complete_file_upload(transfer_id, file_id, part_numbers)
        return self.finalize_transfer(transfer_id)
    
    def authorize(self):
        address = 'https://dev.wetransfer.com/v2/authorize'
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key }
        data    = { 'user_identifier': self.user_identifier }
        r = requests.post(address, headers=headers)
        try :
            self.token = "Bearer " + (json.loads(r.text))['token']
            if self.debug: print("authorization passed")
        except :
            print(r.text)
    
    def create_new_transfer(self, message, file_name, file_size):
        if self.token != "":
            address = 'https://dev.wetransfer.com/v2/transfers'
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "message":message, "files":[{"name":file_name, "size":file_size}] }
            r = requests.post(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            return [   (json.loads(r.text))['id'], (json.loads(r.text))['files'][0]['id'], 
                       (json.loads(r.text))['files'][0]['multipart']['part_numbers'], (json.loads(r.text))['files'][0]['multipart']['chunk_size'] ]
        else :
            if self.debug: print("unauthentified")
            return ["","",0,0]
    
    def request_upload_url(self, transfer_id, file_id, part_number):
        if self.token != "":
            address = 'https://dev.wetransfer.com/v2/transfers/%s/files/%s/upload-url/%s' % (transfer_id, file_id, part_number)
            headers={ "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            r = requests.get(address, headers=headers)
            if self.debug : print(r.text)
            return (json.loads(r.text))['url']
    
    def file_upload(self, url, file_name, mime_type, bytes_stream):
        headers = {'Content-Type': mime_type, 'File': file_name}
        r = requests.put(url, data=bytes_stream)
    
    def complete_file_upload(self, transfer_id, file_id, part_numbers):
        address = 'https://dev.wetransfer.com/v2/transfers/%s/files/%s/upload-complete' % (transfer_id, file_id)
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        data    = { "part_numbers": part_numbers }
        r = requests.put(address, headers=headers, data=json.dumps(data))
    
    def finalize_transfer(self, transfer_id):
        address = 'https://dev.wetransfer.com/v2/transfers/%s/finalize' % transfer_id
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        r = requests.put(address, headers=headers)
        return (json.loads(r.text))['url']
