import audb
import audeer


def update_db(name, previous_version, version, build_dir):
    repository = audb.repository(name, previous_version)
    build_dir = audeer.mkdir(build_dir)

    db = audb.load_to(
        build_dir,
        name,
        version=previous_version,
        num_workers=5,
    )

    # add license information
    db.license = 'Open Data Commons Open Database License (ODbL) v1.0'
    db.license_url = 'http://opendatacommons.org/licenses/odbl/1.0/'

    # add authors
    db.author = (
        'Houwei Cao, '
        'David G. Cooper, '
        'Michael K. Keutmann, '
        'Ruben C. Gur, '
        'Ani Nenkova, '
        'Ragini Verma, '
        'Samantha L Moore, '
        'Adam Savitt'
    )

    db.save(build_dir)

    audb.publish(
        build_dir,
        version,
        repository,
        previous_version=previous_version,
    )


if __name__ == '__main__':
    name = 'crema-d'
    previous_version = '1.0.3'
    version = '1.0.5'
    build_dir = '../build'

    update_db(name=name,
              previous_version=previous_version,
              version=version,
              build_dir=build_dir)
