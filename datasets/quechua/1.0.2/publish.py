import audb


repository = audb.repository("quechua", "1.0.1")
audb.publish("./build", "1.0.2", repository, previous_version="1.0.1")
