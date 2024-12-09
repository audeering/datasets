import audb


previous_version = None
version = '1.0.0'
build_root = 'build'

# for local testing

# repository = audb.Repository(
#     name='data',
#     host='host',
#     backend='file-system',
# )

repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)

audb.publish(
    build_root,
    version=version,
    previous_version=previous_version,
    repository=repository,
    num_workers=8,
    verbose=True,
)
