import audb2


DB_ROOT = './build'


repository = audb2.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)
audb2.publish(
    DB_ROOT,
    version='2.0.0',
    repository=repository,
    num_workers=1,
    verbose=True
)
