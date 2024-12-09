import audb
import audeer

from define import name
from define import previous_version


build_dir = audeer.path("./build")
audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)
db.save(build_dir, storage_format="parquet")
