import audb
import audeer
import audformat


name = 'crema-d'
previous_version = '1.1.0'

build_dir = '../build'
build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    cache_root=None,
    verbose=True
)

# Fix usage and add remark to description
db.usage = audformat.define.Usage.COMMERCIAL
db.description += (
    ' '
    'When using the database commercially, '
    'the database must be referenced '
    'together with its license.'
)
db.save(build_dir)
