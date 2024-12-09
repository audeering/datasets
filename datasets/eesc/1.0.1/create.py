import audb
import audeer


build_dir = audeer.path("./build")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

db = audb.load_to(build_dir, "eesc", version="1.0.0", only_metadata=True)
db.source = ""
db.license_url = "https://creativecommons.org/licenses/by/3.0/deed.en"
db.save(build_dir)
