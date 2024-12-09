import audb
import audeer


build_dir = audeer.path("./build")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

db = audb.load_to(build_dir, "quechua", version="1.0.1", only_metadata=True)
# Use DOI for URL
db.source = "https://doi.org/10.6084/m9.figshare.20292516.v4"
# Start description with upper letter
db.description = f"{db.description[0].upper()}{db.description[1:]}"
db.save(build_dir)
