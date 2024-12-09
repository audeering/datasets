
import os
import urllib.request

import audeer


# Get database source
source = "https://zenodo.org/records/5427549/files/emoUERJ.zip?download=1"
src_dir = "build/audios"
if not os.path.exists(src_dir):
    urllib.request.urlretrieve(source, "emouerj.zip")
    audeer.extract_archive("emouerj.zip", src_dir)
