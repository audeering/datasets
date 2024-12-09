import audb
import audeer


build_dir = audeer.path("./build")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

db = audb.load_to(build_dir, "mesd", version="1.0.0", only_metadata=True)
db.source = "https://doi.org/10.17632/cy34mh68j9.5"
db.save(build_dir, storage_format="csv")
