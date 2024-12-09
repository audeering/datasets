import audb


build_dir = '../build'
version = '1.4.0'


repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)
audb.publish(
    build_dir,
    version=version,
    repository=repository,
    num_workers=1,
    verbose=True,
)
