import audb

previous_version = '1.2.0'
version = '1.3.0'
build_dir = './build'

repository = audb.Repository(
    name="data-public",
    host="https://audeering.jfrog.io/artifactory",
    backend="artifactory",
)

audb.publish(
    build_dir,
    version=version,
    previous_version=previous_version,
    repository=repository,
    num_workers=1,
    verbose=True,
)
