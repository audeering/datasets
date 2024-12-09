import audb
import audeer
import audformat


name = 'emodb'
previous_version = '1.1.0'
version = '1.1.1'
build_dir = '../build'
repository = audb.Repository(
    name='data-public',
    host='https://audeering.jfrog.io/artifactory',
    backend='artifactory',
)

build_dir = audeer.mkdir(build_dir)

audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Fix gender labels of speakers, see
# https://github.com/audeering/emodb/issues/2
db = audformat.Database.load(build_dir)
db.schemes['speaker'].labels = {
    3: {'gender': 'male', 'age': 31, 'language': 'deu'},
    8: {'gender': 'female', 'age': 34, 'language': 'deu'},
    9: {'gender': 'female', 'age': 21, 'language': 'deu'},
    10: {'gender': 'male', 'age': 32, 'language': 'deu'},
    11: {'gender': 'male', 'age': 26, 'language': 'deu'},
    12: {'gender': 'male', 'age': 30, 'language': 'deu'},
    13: {'gender': 'female', 'age': 32, 'language': 'deu'},
    14: {'gender': 'female', 'age': 35, 'language': 'deu'},
    15: {'gender': 'male', 'age': 25, 'language': 'deu'},
    16: {'gender': 'female', 'age': 31, 'language': 'deu'},
}
db.save(build_dir)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
