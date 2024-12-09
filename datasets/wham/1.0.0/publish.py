import audb


build_dir = './build'
version = '1.0.0'
repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=None,
    num_workers=4,
)