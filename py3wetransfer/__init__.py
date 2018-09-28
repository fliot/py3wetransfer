name = "py3wetransfer"

import json, logging, magic, os, requests
import http.client as http_client

mime = magic.Magic(mime=True)

class Py3WeTransfer(object):
    debug = False
    x_api_key = ""
    user_identifier = ""
    token = ""
    sender = ""
    recipients = []
    language = "en"
    
    # The class "constructor" is de facto an initializer 
    def __init__(self, x_api_key, user_identifier="", debug=False):
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
        file_size = os.path.getsize(file_path)
        
        if self.token == "": self.authorize()
        
        if self.sender == "" or len(self.recipients) == 0 :
            [transfer_id, file_id, part_numbers, chunk_size] = self.create_new_transfer(message, file_name, file_size)
            
            i = 1
            f = open(file_path, "rb")
            bytes_read = f.read(chunk_size)
            while bytes_read:
                url = self.request_upload_url(transfer_id, file_id, i)
                self.file_upload(url, file_name, mime_type, bytes_read)
                bytes_read = f.read(chunk_size)
                i += 1
            f.close()
            self.complete_file_upload(transfer_id, file_id, part_numbers)
            return self.finalize_transfer(transfer_id)
        
        else : 
            # take care, this uses wetransfer API V4, which is currently undocumented
            [transfer_id, file_id, part_numbers, chunk_size] = self.create_new_transfer_mail(message, file_name, file_size, self.sender, self.recipients, self.language)
            [file_id, chunk_size] = self.request_transfer_mail(transfer_id, file_name, file_size)
            
            i = 1
            f = open(file_path, "rb")
            bytes_read = f.read(chunk_size)
            while bytes_read:
                # let's use an hard coded crc, since wetransfer doesn't use this value afterward...
                chunk_crc = 888888888
                
                url = self.request_upload_url_mail(transfer_id, file_id, i, chunk_size , chunk_crc)
                self.file_upload(url, file_name, mime_type, bytes_read)
                bytes_read = f.read(chunk_size)
                i += 1
            f.close()
            
            self.complete_file_upload_mail(transfer_id, file_id, part_numbers)
            return self.finalize_transfer_mail(transfer_id, part_numbers)
    
    
    def authorize(self):
        address = 'https://dev.wetransfer.com/v2/authorize'
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key }
        data    = { 'user_identifier': self.user_identifier }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.post(address, headers=headers)
        if self.debug : print(r.text)
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
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
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
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.put(address, headers=headers, data=json.dumps(data))
    
    
    def finalize_transfer(self, transfer_id):
        address = 'https://dev.wetransfer.com/v2/transfers/%s/finalize' % transfer_id
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        r = requests.put(address, headers=headers)
        return (json.loads(r.text))['url']
    
    
    
    ##################################################################################################################################
    # Warning, 
    # Bellow this, we use wetransfer API V4,
    # Which is currently undocumented, against WeTransfer's CLUF and probably subject to changes...
    ##################################################################################################################################
    def emails(self, sender, recipients, language="en") :
        print("This functionnality use automatically the WeTransfer private API V4. This is against the current WeTransfer's CLUF License. Use it only for testing purpose !")
        # initialization function
        self.sender = sender
        self.recipients = recipients
        self.language = language
    
    def create_new_transfer_mail(self, message, file_name, file_size, sender, recipients, language):
        if self.token != "":
            address = 'https://wetransfer.com/api/v4/transfers/email'
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "recipients": recipients, "message":message, "from": sender, "ui_naguage":language,
                        "domain_user_id":self.user_identifier, "files":[{"name":file_name, "size":file_size}] }
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            r = requests.post(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            
            # calculate number of chunk parts
            part_numbers = ( file_size // (json.loads(r.text))['files'][0]['chunk_size'] ) + 1
            
            return [   (json.loads(r.text))['id'], (json.loads(r.text))['files'][0]['id'],
                       part_numbers, (json.loads(r.text))['files'][0]['chunk_size'] ]
    
    
    def request_transfer_mail(self, transfer_id, file_name, file_size):
        if self.token != "":
            address = 'https://wetransfer.com/api/v4/transfers/%s/files' % transfer_id
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "name": file_name, "size": file_size }
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            r = requests.post(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            return [ (json.loads(r.text))['id'], (json.loads(r.text))['chunk_size'] ]
    
    
    def request_upload_url_mail(self, transfer_id, file_id, part_number, chunk_size, chunk_crc):
        if self.token != "":
            address = 'https://wetransfer.com/api/v4/transfers/%s/files/%s/part-put-url' % (transfer_id, file_id)
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "chunk_number": part_number, "chunk_size": chunk_size, "chunk_crc": chunk_crc, "retries": 0 }
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            r = requests.post(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            return (json.loads(r.text))['url']
    
    
    def complete_file_upload_mail(self, transfer_id, file_id, part_numbers):
        if self.token != "":
            address = 'https://wetransfer.com/api/v4/transfers/%s/files/%s/finalize-mpp' % (transfer_id, file_id)
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "chunk_count": part_numbers }
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            r = requests.put(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            return (json.loads(r.text))['id']
    
    def finalize_transfer_mail(self, transfer_id, part_numbers):
        if self.token != "":
            address = 'https://wetransfer.com/api/v4/transfers/%s/finalize' % transfer_id
            headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
            data    = { "chunk_count": part_numbers }
            if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
            r = requests.put(address, headers=headers, data=json.dumps(data))
            if self.debug : print(r.text)
            return (json.loads(r.text))['shortened_url']
    
    
