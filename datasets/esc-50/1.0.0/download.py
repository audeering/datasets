import os
import shutil
import tempfile
import urllib.request

import audeer


# Get database source
source = 'https://github.com/karoldvl/ESC-50/archive/master.zip'
archive_name = 'esc-50.zip'
build_root = audeer.mkdir('build')

if not os.path.exists(archive_name):
    urllib.request.urlretrieve(source, archive_name)

with tempfile.TemporaryDirectory() as root:
    audeer.extract_archive(archive_name, root, verbose=True)
    shutil.move(audeer.path(root, 'ESC-50-master', 'audio'), build_root)
    shutil.move(audeer.path(root, 'ESC-50-master', 'meta', 'esc50.csv'), '.')
