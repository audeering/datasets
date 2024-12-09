import audb
import audeer


name = 'cmu-mosei'
previous_version = '1.2.2'
version = '1.2.3'
build_dir = '../build'
repository = audb.repository(name, previous_version)

build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Update header metadata
db.license_url = 'https://creativecommons.org/licenses/by-nc/4.0/'
db.save(build_dir)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
