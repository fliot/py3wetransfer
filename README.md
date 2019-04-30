# WeTransfer V2 Upload wrapper

This module allows you to use WeTransfer services directly, from python 3.x.

It is based on current WeTransfer API V2: https://developers.wetransfer.com/documentation

This project is forked from the py3wetransfer repository that was maintained by Francois Liot. You can still find it [here](https://github.com/fliot/py3wetransfer). It seems, however, that it is no longer maintained.

## Installation

Install through Pypi:
```sh
pip install py3-wetransfer
```

## Functional features
  - Transfer API
https://wetransfer.github.io/wt-api-docs/index.html#transfer-api

  - Board API
https://wetransfer.github.io/wt-api-docs/index.html#board-api

## Usage
**Before starting, make sure you have an API key acquired from [Developers Portal](https://developers.wetransfer.com/).**

To initialize the client, you need to use your own api key. 

### Transfer

**upload_file**

Simply send your file
```python
from wetransfer import TransferApi

x = TransferApi("<my-very-personal-api-key>")

print(x.upload_file("Test upload file", "test.zip"))
# "https://we.tl/t-ajQpdqGxco"
```

**upload_files**

Send several files
```python
from wetransfer import TransferApi

x = TransferApi("<my-very-personal-api-key>")

print(x.upload_files("Test upload files", ["file1.zip", "file2.zip"]))
# "https://we.tl/t-ajQpdqGxco"
```

### Board

**Manage board**

```python
from wetransfer import BoardApi

x = BoardApi("<my-very-personal-api-key>")

board_id, board_url = x.create_new_board("test board")

print(board_url)
# "https://we.tl/t-ajQpdqGxco"

# add links
x.add_links_to_board(board_id, [{"url": "https://wetransfer.com/", "title": "WeTransfer"}])

# add files
x.add_files_to_board(board_id, ["test1.png", "test2.jpg"])

# retrieve the board object 
# https://wetransfer.github.io/wt-api-docs/index.html#retrieve-boards-information
board_object = x.get_board(board_id)
```

### Debug
```python
import logging
from wetransfer import TransferApi

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
py3wetransfer_log = logging.getLogger('wetransfer')
py3wetransfer_log.setLevel(logging.DEBUG)
py3wetransfer_log.propagate = True

x = TransferApi("<my-very-personal-api-key>")

print(x.upload_file("test upload", "test.zip"))
# "https://we.tl/t-ajQpdqGxco"
```

If you want to see complete http traffic:

```python
import logging
from wetransfer import TransferApi

import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
py3wetransfer_log = logging.getLogger('wetransfer')
py3wetransfer_log.setLevel(logging.DEBUG)
py3wetransfer_log.propagate = True

x = TransferApi("<my-very-personal-api-key>")

print(x.upload_file("test upload", "test.zip"))
# "https://we.tl/t-ajQpdqGxco"
```

### Testing authentication

If you need to test authentication validity

```python
from wetransfer import TransferApi

x = TransferApi("<my-very-personal-api-key>")

if x.is_authenticated():
    print("we are authenticated")
```

### Additional authentication parameters

WeTransfer asks officially for a valid "domain_user_id"/"user_identifier" in their API documentation, but in practise, it works perfectly without providing it.

```python
from wetransfer import TransferApi

x = TransferApi("<my-very-personal-api-key>", 
                user_identifier="81940232-9857-4cf7-b685-7a404faf5205")

print(x.upload_file("test upload", "test.zip"))
# "https://we.tl/t-ajQpdqGxco"
```

### Unit tests

The package has a number of tests. You can run the tests by running the command `python setup.py test`. Please make sure you have defined the environment variable `WE_API_KEY`, otherwise all tests will fail. See 'Usage' above to see how you can obtain a key. You can set the key in a shell like so:

```bash
export WE_API_KEY=WvMlogNaWLubua6S5iuA5tRk6ZZDqwh6yaxOpGNa
```

This is an invalid key, so make sure to use your own key. 

Please note that the tests actually upload files, and this may take a while (depending on your internet connection). Also, running the tests counts toward your API key usage, so bear this in mind.
