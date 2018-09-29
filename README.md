# WeTransfer V2 Upload wrapper

This module allows you to use WeTransfer services directly, from python 3.x.

It is based on current WeTransfer API V2: https://developers.wetransfer.com/documentation

Install though Pypi:
```sh
pip install py3wetransfer
```

# Functional features
  - Transfer API
https://wetransfer.github.io/wt-api-docs/index.html#transfer-api

  - Board API
https://wetransfer.github.io/wt-api-docs/index.html#board-api

# Usage
**Before starting, make sure you have an API key acquired from [Developers Portal](https://developers.wetransfer.com/).**

To initialize the client, you need to use your own api key. 

# Transfer

**upload_file**

Simply send your file
```python
from py3wetransfer import Py3WeTransfer

x = Py3WeTransfer("<my-very-personal-api-key>")

print( x.upload_file("test.zip", "test upload") )
>> "https://we.tl/t-ajQpdqGxco"
```

**upload_files**

Send several files
```python
from py3wetransfer import Py3WeTransfer

x = Py3WeTransfer("<my-very-personal-api-key>")

print( x.upload_files( ["file1.zip", "file2.zip"] , "test upload") )
>> "https://we.tl/t-ajQpdqGxco"
```

# Board

**Manage board**

```python
from py3wetransfer import Py3WeTransfer

x = Py3WeTransfer("<my-very-personal-api-key>")

[ board_id, board_url ] = x.create_new_board("test board")

print(board_url)
>> "https://we.tl/t-ajQpdqGxco"

# add links
x.add_links_to_board( board_id, [{"url": "https://wetransfer.com/", "title": "WeTransfer"}] )

# add files
x.add_files_to_board( board_id, ["test1.png", "test2.jpg"] )

# retrieve the board object 
# https://wetransfer.github.io/wt-api-docs/index.html#retrieve-boards-information
board_object = x.get_board( board_id )
```

# Debug
```python
import logging
from py3wetransfer import Py3WeTransfer

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
py3wetransfer_log = logging.getLogger("py3wetransfer")
py3wetransfer_log.setLevel(logging.DEBUG)
py3wetransfer_log.propagate = True

x = Py3WeTransfer("xA8ZYoVox57QfxX77hjQ2AI7hqO6l9M4tqv8b57c")

print( x.upload_file("test.zip", "test upload") )
...
```

If you want to see complete http traffic:
```python
import logging
from py3wetransfer import Py3WeTransfer

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
py3wetransfer_log = logging.getLogger("py3wetransfer")
py3wetransfer_log.setLevel(logging.DEBUG)
py3wetransfer_log.propagate = True

x = Py3WeTransfer("xA8ZYoVox57QfxX77hjQ2AI7hqO6l9M4tqv8b57c")

print( x.upload_file("test.zip", "test upload") )
...
```

# Testing authentication
If you need to test authentication validity
```python
from py3wetransfer import Py3WeTransfer

x = Py3WeTransfer("xA8ZYoVox57QfxX77hjQ2AI7hqO6l9M4tqv8b57c")

if x.isAuthentified() : print("we are authentified")
```

# Additionnal authentication parameters
WeTransfer asks officially for a valid "domain_user_id"/"user_identifier" in their API documentation, but in practise, it perfectly works without providing it, but you can also provide it if you really want...
```python
from py3wetransfer import Py3WeTransfer

x = Py3WeTransfer( "xA8ZYoVox57QfxX77hjQ2AI7hqO6l9M4tqv8b57c", 
                     user_identifier="81940232-9857-4cf7-b685-7a404faf5205")

print( x.upload_file("test.zip", "test upload") )
>> "https://we.tl/t-ajQpdqGxco"
```
