import os

import audb
import audeer
import audformat


name = 'cough-speech-sneeze'
version = '2.0.1'
previous_version = '2.0.0'
build_dir = audeer.mkdir('../build')
repository = audb.repository(name, previous_version)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Fix license
db.license = 'CC-BY-4.0'
db.license_url = audformat.core.define.LICENSE_URLS[db.license]

# Add authors
db.author = (
    'S Amiriparian, '
    'S Pugachevskiy, '
    'N Cummins, '
    'D Hantke, '
    'J Pohjalainen, '
    'G Keren, '
    'Schuller, BW'
)

db.save(build_dir)

# Force republishing of media files as single ZIP files
previous_version = None
os.remove(os.path.join(build_dir, 'db.csv'))

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
