import audb


DB_ROOT = './build'


repository = audb.Repository(
    name='data-public',
    host='https://audeering.jfrog.io/artifactory',
    backend='artifactory',
)
audb.publish(
    DB_ROOT,
    version='1.1.0',
    repository=repository,
    num_workers=1,
    verbose=True,
)
