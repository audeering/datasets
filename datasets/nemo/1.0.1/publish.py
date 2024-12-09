import audb


version = "1.0.1"
previous_version = "1.0.0"
repository = audb.repository("nemo", previous_version)
audb.publish("./build", version, repository, previous_version=previous_version)
