# WeTransfer V2 Upload wrapper
Built by myself for Python 3, because I didn't find such thing already written anywhere else...

# Requisites
python > 3.5
pip install python-magic

Based on current [WeTransfer V2 API][wetransferdoc]

# Usage
```sh
from py3wetransfer import Py3WeTransfer
x = Py3WeTransfer("xA8ZYoVox57QfxX77hjQ2AI7hqO6l9M4tqv8b57c", "transfer")
print( x.upload_file("test.zip", "test upload") )
>> "https://we.tl/t-ajQpdqGxco"
```

   [wetransferdoc]: < : https://developers.wetransfer.com/documentation>
