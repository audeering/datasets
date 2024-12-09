import audb
import audeer
import audformat


def main():

    name = 'esc-50'
    previous_version = '1.0.0'

    build_dir = 'build'
    build_dir = audeer.mkdir(build_dir)

    audb.load_to(
        build_dir,
        name,
        version=previous_version,
        only_metadata=True,
        verbose=True,
    )
    db = audformat.Database.load(build_dir)

    db.usage = audformat.define.Usage.RESEARCH
    db.media['microphone'].type = audformat.define.MediaType.AUDIO

    db.save(build_dir)


if __name__ == '__main__':
    main()
