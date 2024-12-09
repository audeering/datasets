import audb
import audeer


build_dir = audeer.mkdir("./build")

db = audb.load_to(build_dir, "quechua", version="1.0.0", only_metadata=True)
db.description = (
    "quechua contains 12420 recordings of emotional speech in Quechua Collao. "
    "Six actors were asked to read words and sentences with nine emotional categories. "
    "Four human annotators labeled the recordings for arousal, dominance, and valence."
)
db.save(build_dir)
