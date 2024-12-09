import audb
import audeer


name = 'cmu-mosi'
previous_version = '1.0.0'
version = '1.0.2'
build_dir = '../build'
repository = audb.repository(name, previous_version)

build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Update header metadata
db.license = 'CC-BY-NC-4.0'
db.license_url = 'https://creativecommons.org/licenses/by-nc/4.0/'
db.author = (
    'Amir Zadeh, '
    'Rown Zellers, '
    'Eli Pincus, '
    'Louis-Philippe Morency'
)
db.organization = 'MultiComp Lab, Carnegie Mellon University '
db.description = (
    'Opinion-level annotated corpus of sentiment '
    'and subjectivity analysis in online videos. '
    'The dataset is annotated with labels for subjectivity, '
    'sentiment intensity, '
    'per-frame and per-opinion. '
    'Reference: '
    'https://arxiv.org/abs/1606.06259'
)
db.save(build_dir)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
