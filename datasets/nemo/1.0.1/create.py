import audb
import audeer


build_dir = audeer.path("./build")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

db = audb.load_to(build_dir, "nemo", version="1.0.0", only_metadata=True)
db.description = (
    "NEMO is a polish dataset with emotional speech. "
    "It contains over 3 hours of emotional speech in 6 categories: "
    "anger, fear, happiness, sadness, surprise and neutral. "
    "The audios were created by nine speakers."
)
db.save(build_dir)
