import audb

version = '1.1.0'
build_dir = './build'

repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)
audb.publish(
    build_dir,
    version=version,
    repository=repository,
    num_workers=8,
    verbose=True,
)
