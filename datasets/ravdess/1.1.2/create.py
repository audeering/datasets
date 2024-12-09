import audb
import audeer
import audformat


name = 'ravdess'
previous_version = '1.1.1'

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

# Add missing license entries
db.license = 'CC-BY-NC-SA-4.0'
db.license_url = (
    'http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode'
)
db.save(build_dir)
