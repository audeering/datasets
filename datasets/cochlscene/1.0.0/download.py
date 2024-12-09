import os
import shutil

import audeer


build_root = audeer.mkdir('build')

files = [  # source, splits
    ('CochlScene', 5),
]

for source, splits in files:

    archive = f'{source}-unsplit.zip'
    if not os.path.exists(archive):

        archive = f'{source}.zip'
        url = f'https://zenodo.org/record/7080122/files/{archive}?download=1'
        if not os.path.exists(archive):
            audeer.download_url(url, archive, verbose=True)

        for split in range(splits):
            archive = f'{source}.z0{split + 1}'
            url = f'https://zenodo.org/record/7080122/files/{archive}?download=1'
            if not os.path.exists(archive):
                audeer.download_url(url, archive, verbose=True)

        archive = f'{source}-unsplit.zip'
        cmd = f'zip -s 0 {source}.zip --out {archive}'
        os.system(cmd)

    audeer.extract_archive(archive, '.', verbose=True)
    for folder, target in [
        ('Test', 'test'),
        ('Train', 'train'),
        ('Val', 'dev'),
    ]:
        shutil.move(f'{source}/{folder}', build_root)
        os.rename(f'{build_root}/{folder}', f'{build_root}/{target}')
