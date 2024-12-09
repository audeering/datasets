import os
import shutil

import audeer
import audformat
import audiofile as af
import pandas as pd


build_root = audeer.mkdir('build')
audio_root = 'audio'


description = (
   'The ESC-50 dataset is a labeled collection of '
   '2000 environmental audio recordings suitable for '
   'benchmarking methods of environmental sound classification. '
   'The dataset consists of 5-second-long recordings organized '
   'into 50 semantical classes (with 40 examples per class) '
   'loosely arranged into 5 major categories.'
)

db = audformat.Database(
    name='esc-50',
    author='K. J. Piczak',
    license='CC-BY-NC-3.0',
    license_url = 'https://creativecommons.org/licenses/by-nc/3.0/',
    source='https://github.com/karolpiczak/ESC-50',
    usage=audformat.define.Usage.UNRESTRICTED,
    description=description,
)

# Parse meta information

meta = pd.read_csv('esc50.csv')
files = sorted(meta.filename)
files = [os.path.join(audio_root, f) for f in files]

categories = sorted(meta.category.unique().tolist())
folds = sorted(meta.fold.unique().tolist())
takes = sorted(meta['take'].unique().tolist())

# 50 categories can be further
# grouped into 5 major categories
major_categories = [
    'animals',
    'natural',
    'human',
    'interior',
    'exterior',
]

# {0: 'dog', 1: 'rooster', 2: 'pig', ...}
id_to_cat = {
    idx: cat for idx, cat in
    sorted(set(meta[['target', 'category']].itertuples(
        index=False,
        name=None,
    )))
}

# {'dog': 'animals', 'rooster': 'animals', ...}
cat_to_maj = {
    cat: major_categories[idx // 10]
    for idx, cat in id_to_cat.items()
}

# Schemes

db.schemes['category'] = audformat.Scheme(
    labels=categories,
    description='50 semantical categories.'
)
db.schemes['clip_id'] = audformat.Scheme(
    'str',
    description='ID of the original Freesound clip.'
)
db.schemes['esc10'] = audformat.Scheme(
    'bool',
    description='File belongs to the ESC-10 subset.',
)
db.schemes['fold'] = audformat.Scheme(
    labels=folds,
    description='Index of the cross-validation fold.'
)
db.schemes['major'] = audformat.Scheme(
    labels=major_categories,
    description='5 major categories.',
)
db.schemes['take'] = audformat.Scheme(
    labels=takes,
    description='Letter disambiguating between different fragments from the same Freesound clip.'
)

# Media

db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=44100,
    channels=1,
)

# Tables

index = audformat.filewise_index(files)
db['files'] = audformat.Table(
    index,
    media_id='microphone',
)

db['files']['category'] = audformat.Column(scheme_id='category')
db['files']['category'].set(meta.category)

db['files']['clip_id'] = audformat.Column(scheme_id='clip_id')
db['files']['clip_id'].set(meta.src_file)

db['files']['esc10'] = audformat.Column(scheme_id='esc10')
db['files']['esc10'].set(meta.esc10)

db['files']['fold'] = audformat.Column(scheme_id='fold')
db['files']['fold'].set(meta.fold)

db['files']['major'] = audformat.Column(scheme_id='major')
db['files']['major'].set(meta.category.map(cat_to_maj))

db['files']['take'] = audformat.Column(scheme_id='take')
db['files']['take'].set(meta['take'])

# Save to disk

db.save(build_root)
