import audb
import audformat


build_dir = '../build'
name = 'air'
previous_version = '1.4.0'
version = '1.4.1'
repository = audb.repository(name, previous_version)


db = audb.load_to(build_dir, name, version=previous_version)

# Fix name of azimuth column,
# which is named distance at the moment
azimuth = db['brir']['distance'].get()
db['brir'].drop_columns('distance', inplace=True)
db['brir']['azimuth'] = audformat.Column(scheme_id='azimuth')
db['brir']['azimuth'].set(azimuth)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
