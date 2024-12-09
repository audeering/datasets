import pandas as pd

import audb
import audeer
import audformat


name = 'emodb'
previous_version = '1.2.0'
build_dir = './build'
build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    only_metadata=True,
    cache_root=None,
    verbose=True,
)

# Use MiscTable for speaker scheme
db.schemes['age'] = audformat.Scheme(
    'int',
    minimum=0,
    description='Age of speaker',
)
db.schemes['gender'] = audformat.Scheme(
    'str',
    labels=['female', 'male'],
    description='Gender of speaker',
)
db.schemes['language'] = audformat.Scheme(
    'str',
    description='Language of speaker',
)
labels = db.schemes['speaker'].labels
index = pd.Index(
    list(labels.keys()),
    dtype='Int64',
    name='speaker',
)
db['speaker'] = audformat.MiscTable(index)
for scheme_id in ['age', 'gender', 'language']:
    db['speaker'][scheme_id] = audformat.Column(scheme_id=scheme_id)
    db['speaker'][scheme_id].set(
        [d[scheme_id] for d in labels.values()]
    )
db.schemes['speaker'].replace_labels('speaker')

db.save(build_dir)
