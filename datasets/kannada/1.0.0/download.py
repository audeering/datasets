
import os
import urllib.request

import audeer


# Get database source
source = "https://zenodo.org/api/records/6345107/files-archive"
src_dir = "build/audios"
if not os.path.exists(src_dir):
    urllib.request.urlretrieve(source, "kannada.zip")
    audeer.extract_archive("kannada.zip", src_dir)
