import os

import audb
import audformat
import auvad


name = 'speech-accent-archive'
previous_version = '2.0.0'
version = '2.1.0'
current_dir = os.path.dirname(os.path.realpath(__file__))
build_dir = '../build'

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Add segments with tone annotations
vad = auvad.Vad()
os.chdir(build_dir)
segments = vad.process_index(db.files)
os.chdir(current_dir)
db.raters['guess'] = audformat.Rater(type='other')
db.schemes['tone'] = audformat.Scheme(
    labels=['neutral'],
    description='We assume that all speech has a neutral tone.',
)
db['segments'] = audformat.Table(
    index=segments,
    media_id='microphone',
)
db['segments']['tone'] = audformat.Column(
    scheme_id='tone',
    rater_id='guess',
    description='Tone of voice',
)
db['segments']['tone'].set('neutral', index=segments)
db.save(build_dir)

repository = audb.repository(name, previous_version)
audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
