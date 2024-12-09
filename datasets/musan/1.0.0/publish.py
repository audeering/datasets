import audb


build_dir = './build'
version = '1.0.0'


repository = audb.Repository(
    name='data-public',
    host='https://audeering.jfrog.io/artifactory',
    backend='artifactory',
)
audb.publish(
    build_dir,
    version=version,
    repository=repository,
    num_workers=1,
    verbose=True,
)
