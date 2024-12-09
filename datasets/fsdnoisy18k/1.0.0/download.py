import os
import shutil

import audeer


build_root = audeer.mkdir('build')
audio_root = audeer.path(build_root, 'audio')

files = [  # source, target
    ('FSDnoisy18k.doc', 'doc'),
    ('FSDnoisy18k.meta', 'meta'),
    ('FSDnoisy18k.audio_test', f'{audio_root}/test'),
    ('FSDnoisy18k.audio_train', f'{audio_root}/train'),
]

for source, target in files:
    url = f'https://zenodo.org/record/2529934/files/{source}.zip?download=1'
    archive = f'{source}.zip'
    if not os.path.exists(archive):
        audeer.download_url(url, archive, verbose=True)
    audeer.extract_archive(archive, '.', verbose=True)
    shutil.move(source, target)
