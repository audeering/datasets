import audb
VERSION = '1.0.0'
build_dir = './build'
def main():
    repository = audb.Repository(
        name='data-public-local',
        host='https://artifactory.audeering.com/artifactory',
        backend='artifactory',
    )
    audb.publish(
        build_dir,
        version=VERSION,
        repository=repository,
        num_workers=1,
        verbose=True
    )
if __name__ == '__main__':
    main()
