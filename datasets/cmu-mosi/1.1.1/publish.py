import os

import audb
import audeer

from define import name
from define import previous_version
from define import version


build_dir = audeer.path("./build")
repository = audb.repository(name, previous_version)

# Do not depend on a previous version,
# to force re-publishing with one archive per media file.
previous_version = None
# This also requires to remove any dependency table
# from a previous version
dependency_table = os.path.join(build_dir, "db.parquet")
if os.path.exists(dependency_table):
    os.remove(dependency_table)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
    num_workers=8,
)
