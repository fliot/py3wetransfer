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
        self.authorize()
    
    
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
    
    
    def upload_file(self, file_path, message):
        return self.upload_files([file_path], message)
    
    def upload_files(self, file_paths, message):
        # multiple uploads
        files = []
        for file_path in file_paths :
            files.append( { 'file_path': file_path,
                            'file_name': os.path.basename(file_path),
                            'file_size': os.path.getsize(file_path),
                            'mime_type': mime.from_file(file_path) } )
        
        if self.sender == "" or len(self.recipients) == 0 :
            [transfer_id, files] = self.create_new_transfer(message, files)
            
            for f in files:
                i = 1
                fr = open(f['file_path'], "rb")
                bytes_read = fr.read(f['chunk_size'])
                while bytes_read:
                    url = self.request_upload_url(transfer_id, f['file_id'], i)
                    self.file_upload(url, f['file_name'], f['mime_type'], bytes_read)
                    bytes_read = fr.read(f['chunk_size'])
                    i += 1
                fr.close()
                self.complete_file_upload(transfer_id, f['file_id'], f['part_numbers'])
            return self.finalize_transfer(transfer_id)
    
    
        else : 
            # take care, this uses wetransfer API V4, which is currently undocumented
            [transfer_id, files] = self.create_new_transfer_mail(message, files, self.sender, self.recipients, self.language)
            
            part_numbers = 0
            for f in files:
                [file_id, chunk_size] = self.request_transfer_mail(transfer_id, f['file_name'], f['file_size'])
                
                i = 1
                fr = open(f['file_path'], "rb")
                bytes_read = fr.read(f['chunk_size'])
                while bytes_read:
                    # let's use an hard coded crc, since wetransfer doesn't use this value afterward...
                    chunk_crc = 888888888
                    
                    url = self.request_upload_url_mail(transfer_id, file_id, i, f['chunk_size'] , chunk_crc)
                    self.file_upload(url, f['file_name'], f['mime_type'], bytes_read)
                    bytes_read = fr.read(f['chunk_size'])
                    i += 1
                fr.close()
                
                self.complete_file_upload_mail(transfer_id, f['file_id'], f['part_numbers'])
                part_numbers += f['part_numbers']
            return self.finalize_transfer_mail(transfer_id, part_numbers)
    
    
    def create_new_transfer(self, message, files):
        address = 'https://dev.wetransfer.com/v2/transfers'
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        files_stream = []
        for i in files: files_stream.append( { "name": i['file_name'], 'size': i['file_size'] } )
        data    = { "message":message, "files": files_stream }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.post(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        for i in range(0, len((json.loads(r.text))['files'])):
            files[i] = { 'file_path':files[i]['file_path'],
                         'file_name':files[i]['file_name'],
                         'file_size':files[i]['file_size'],
                         'mime_type':files[i]['mime_type'],
                         'file_id':(json.loads(r.text))['files'][i]['id'],
                         'part_numbers':(json.loads(r.text))['files'][0]['multipart']['part_numbers'],
                         'chunk_size':(json.loads(r.text))['files'][0]['multipart']['chunk_size'] }
        return [   (json.loads(r.text))['id'], files ]
    
    def request_upload_url(self, transfer_id, file_id, part_number):
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
    
    def create_new_transfer_mail(self, message, files, sender, recipients, language):
        address = 'https://wetransfer.com/api/v4/transfers/email'
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        files_stream = []
        for i in files: files_stream.append( { "name": i['file_name'], 'size': i['file_size'] } )
        data    = { "recipients": recipients, "message":message, "from": sender, "ui_naguage":language,
                    "domain_user_id":self.user_identifier, "files": files_stream }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.post(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        
        for i in range(0, len((json.loads(r.text))['files'])):
            files[i] = { 'file_path':files[i]['file_path'],
                         'file_name':files[i]['file_name'],
                         'file_size':files[i]['file_size'],
                         'mime_type':files[i]['mime_type'],
                         'file_id':(json.loads(r.text))['files'][i]['id'],
                         'part_numbers':( files[i]['file_size'] // (json.loads(r.text))['files'][0]['chunk_size'] ) + 1,
                         'chunk_size':(json.loads(r.text))['files'][0]['chunk_size'] }
        return [ (json.loads(r.text))['id'], files ]
    
     
    def request_transfer_mail(self, transfer_id, file_name, file_size):
        address = 'https://wetransfer.com/api/v4/transfers/%s/files' % transfer_id
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        data    = { "name": file_name, "size": file_size }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.post(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        return [ (json.loads(r.text))['id'], (json.loads(r.text))['chunk_size'] ]
    
    
    def request_upload_url_mail(self, transfer_id, file_id, part_number, chunk_size, chunk_crc):
        address = 'https://wetransfer.com/api/v4/transfers/%s/files/%s/part-put-url' % (transfer_id, file_id)
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        data    = { "chunk_number": part_number, "chunk_size": chunk_size, "chunk_crc": chunk_crc, "retries": 0 }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.post(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        return (json.loads(r.text))['url']
    
    
    def complete_file_upload_mail(self, transfer_id, file_id, part_numbers):
        address = 'https://wetransfer.com/api/v4/transfers/%s/files/%s/finalize-mpp' % (transfer_id, file_id)
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        data    = { "chunk_count": part_numbers }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.put(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        return (json.loads(r.text))['id']
    
    def finalize_transfer_mail(self, transfer_id, part_numbers):
        address = 'https://wetransfer.com/api/v4/transfers/%s/finalize' % transfer_id
        headers = { "Content-Type":"application/json", "x-api-key": self.x_api_key, "Authorization": self.token }
        data    = { "chunk_count": part_numbers }
        if self.debug : print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
        r = requests.put(address, headers=headers, data=json.dumps(data))
        if self.debug : print(r.text)
        return (json.loads(r.text))['shortened_url']
    
    
