import os

import audeer


build_dir = audeer.mkdir('../build')
current_dir = os.path.dirname(os.path.realpath(__file__))

urls = [
    'http://isophonics.net/files/irs/greathallOmni.zip',
    'http://isophonics.net/files/irs/octagonOmni.zip',
    'http://isophonics.net/files/irs/classroomOmni.zip',
]
for url in urls:
    data_dir = os.path.join(
        build_dir,
        os.path.basename(url)[:-8],
    )
    archive = audeer.download_url(url, current_dir, verbose=True)
    audeer.extract_archive(archive, data_dir, verbose=True)
    os.rename(
        os.path.join(data_dir, 'Omni'),
        os.path.join(data_dir, 'omni'),
    )
    os.remove(os.path.join(data_dir, 'LICENSE'))
