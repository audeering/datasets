import os
import urllib.request

import audeer


# Get database source
source = 'http://emodb.bilderbar.info/download/download.zip'
src_dir = 'src'
if not os.path.exists(src_dir):
    urllib.request.urlretrieve(source, 'emodb.zip')
    audeer.extract_archive('emodb.zip', src_dir)
