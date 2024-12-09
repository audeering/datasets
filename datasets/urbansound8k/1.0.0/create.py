import os

import pandas as pd

import audeer
import audformat
import audiofile


build_root = audeer.mkdir('build')
audio_root = 'audio'


description = (
   'The UrbanSound8k dataset contains '
   '8732 labeled sound excerpts (<=4s) '
   'of urban sounds from 10 classes. '
   'All excerpts are taken from field recordings '
   'uploaded to Freesound. '
   'The files are pre-sorted into ten folds. '
   'The sampling rate, bit depth, '
   'and number of channels are the same '
   'as those of the original file uploaded '
   'to Freesound and may vary from file to file. '
)

db = audformat.Database(
    name='urbansound8k',
    author='Justin Salamon, Christopher Jacoby, Juan Pablo Bello',
    license='CC-BY-NC-3.0',
    license_url = 'https://creativecommons.org/licenses/by-nc/3.0/',
    source='https://urbansounddataset.weebly.com',
    usage=audformat.define.Usage.RESEARCH,
    description=description,
)

# Parse meta information

meta = pd.read_csv('metadata/UrbanSound8K.csv')
meta = meta.set_index('slice_file_name')
meta = meta.sort_index()

files = 'audio/fold' + \
    meta.fold.astype('str') + '/' + \
    meta.index

index = audformat.filewise_index(files)

# Schemes

db.schemes['category'] = audformat.Scheme(
    labels=sorted(meta['class'].unique().tolist()),
    description='10 sound categories.'
)
db.schemes['clip_id'] = audformat.Scheme(
    'int',
    description=(
        'The Freesound ID of the recording from '
        'which this excerpt (slice) is taken.'
    )
)
db.schemes['fold'] = audformat.Scheme(
    labels=sorted(meta.fold.unique().tolist()),
    description=(
        'The fold number (1-10) to which '
        'this file has been allocated.'
    )
)
salience = {
    1: 'foreground',
    2: 'background',
}
db.schemes['salience'] = audformat.Scheme(
    labels=salience,
    description=(
        'A (subjective) salience rating of the sound.'
    ),
)


# Media

db.media['microphone'] = audformat.Media(
    type=audformat.define.MediaType.AUDIO,
    format='wav',
)

# Tables

db['files'] = audformat.Table(
    index,
    media_id='microphone',
)

db['files']['category'] = audformat.Column(scheme_id='category')
db['files']['category'].set(meta['class'])

db['files']['clip_id'] = audformat.Column(scheme_id='clip_id')
db['files']['clip_id'].set(meta.fsID)

db['files']['fold'] = audformat.Column(scheme_id='fold')
db['files']['fold'].set(meta.fold)

db['files']['salience'] = audformat.Column(scheme_id='salience')
db['files']['salience'].set(meta['salience'])

# Asserts

# check number of files
assert len(db.files) == 8732
assert len(db['files']) == 8732

# check labels and meta data
df = db['files'].get().sample(10)
for file, y in df.iterrows():

    clip_id = os.path.basename(file)

    # check segment
    path = audeer.path(build_root, file)
    assert os.path.exists(path)
    dur = audiofile.duration(path)
    assert round(dur, 2) == round(meta['end'][clip_id] - meta['start'][clip_id], 2)

    # check labels
    assert y['category'] == meta['class'][clip_id]
    assert y['clip_id'] == meta['fsID'][clip_id]
    assert y['fold'] == meta['fold'][clip_id]
    assert y['salience'] == meta['salience'][clip_id]

# Save to disk

db.save(build_root)
