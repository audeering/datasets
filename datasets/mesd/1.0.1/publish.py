import audb


repository = audb.repository("mesd", "1.0.0")
audb.publish("./build", "1.0.1", repository, previous_version="1.0.0")
