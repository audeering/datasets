import audb
import audeer


build_dir = audeer.path("./build")
repository = audb.repository("quechua", "1.0.0")
audb.publish(build_dir, "1.0.1", repository, previous_version="1.0.0")
