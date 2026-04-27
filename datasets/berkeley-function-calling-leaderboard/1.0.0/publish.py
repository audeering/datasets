import audb


build_dir = "build"

repository = audb.Repository(
    name="audb-public",
    host="s3.dualstack.eu-north-1.amazonaws.com",
    backend="s3",
)
audb.publish(
    build_dir,
    "1.0.0",
    repository,
    previous_version=None,
    num_workers=6,
)
