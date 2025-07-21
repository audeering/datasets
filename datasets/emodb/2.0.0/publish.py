import audb

previous_version = '1.4.1'
version = '2.0.0'
build_dir = './build'

repository = audb.Repository(
    name='audb-public',
    host='s3.dualstack.eu-north-1.amazonaws.com',
    backend='s3',
)
audb.publish(
    build_dir,
    version=version,
    previous_version=previous_version,
    repository=repository,
    num_workers=1,
    verbose=True,
)
