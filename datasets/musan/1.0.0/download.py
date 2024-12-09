import os
import shutil

import audeer


build_dir = audeer.mkdir('./build')
url = 'https://www.openslr.org/resources/17/musan.tar.gz'
current_dir = os.path.dirname(os.path.realpath(__file__))

archive = audeer.download_url(url, current_dir, verbose=True)
audeer.extract_archive(archive, current_dir, verbose=True)
for folder in ['music', 'noise', 'speech']:
    src = os.path.join(current_dir, 'musan', folder)
    dst = os.path.join(build_dir, folder)
    shutil.move(src, dst)
