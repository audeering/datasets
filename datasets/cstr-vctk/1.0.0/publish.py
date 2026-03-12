import os

import audb

build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build")
version = "1.0.0"
repository = audb.Repository(
    name="audb-public",
    host="s3.dualstack.eu-north-1.amazonaws.com",
    backend="s3",
)

audb.publish(
    build_dir,
    version,
    repository,
    num_workers=16,
    verbose=True,
    previous_version=None,
)
