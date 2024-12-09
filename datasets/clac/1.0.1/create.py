import audb
import audeer
import audformat


def main():
    build_dir = audeer.mkdir('./build')
    db = audb.load_to(
        build_dir,
        'clac',
        version='1.0.0',
        only_metadata=True,
        verbose=False,
    )

    # crate new speaker scheme connected to the misc table
    db.schemes['speaker'] = audformat.Scheme(audformat.define.DataType.INTEGER, labels='speaker-metadata')

    db['files']['speaker'] = audformat.Column(scheme_id='speaker')
    db['files']['speaker'].set(db['files']['speakerID'].get())
    # rename index of misc table to speaker
    db['speaker-metadata'].index.name = 'speaker'
    db['speaker-metadata'].levels['speaker'] = db['speaker-metadata'].levels.pop('speakerID')
    # remove old 'speakerID' column and scheme
    db['files'].drop_columns(['speakerID'], inplace=True)
    db.schemes.pop('speakerID')

    db.save(build_dir)


if __name__ == '__main__':
    main()
