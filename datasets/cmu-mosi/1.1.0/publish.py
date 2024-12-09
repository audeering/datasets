import pandas as pd

import audb
import audeer
import audformat


name = 'cmu-mosi'
previous_version = '1.0.2'
version = '1.1.0'
build_dir = '../build'

build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Add gender information
db.schemes['gender'] = audformat.Scheme(dtype='str', labels=['female', 'male'])
db['files'] = audformat.Table(index=db.files, media_id='microphone')
db['files']['gender'] = audformat.Column(scheme_id='gender')
df = pd.read_csv('gender.csv', index_col='file')
db['files']['gender'].set(df.gender.values, index=df.index)
db.save(build_dir)

repository = audb.repository(name, previous_version)
audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
