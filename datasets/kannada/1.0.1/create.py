import audb
import audeer


build_dir = audeer.path("./build")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

db = audb.load_to(build_dir, "kannada", version="1.0.0", only_metadata=True)
db.source = "https://doi.org/10.5281/zenodo.6345106"
db.save(build_dir)
