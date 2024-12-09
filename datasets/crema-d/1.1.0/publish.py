import audb

previous_version = '1.0.5'
version = '1.1.0'
build_dir = '../build'

repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)
audb.publish(
    build_dir,
    version=version,
    previous_version=previous_version,
    repository=repository,
    num_workers=1,
    verbose=True,
)
