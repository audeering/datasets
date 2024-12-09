import argparse
import os

import pandas as pd

import audb
import audeer
import audformat


NAME = 'vadtoolkit'
PREVIOUS_VERSION = '1.0.0'
REPOSITORY_LOCAL = audb.Repository(
    name='data-public-local',
    host='~/audb-host',
    backend='file-system',
)
REPOSITORY_PUBLIC = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)
ROOT = audeer.mkdir('build')
SPLITS = {
    'devel': audformat.define.SplitType.DEVELOP,
    'test': audformat.define.SplitType.TEST,
    'train': audformat.define.SplitType.TRAIN,
}
VERSION = '1.1.0'


def command_line_args():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--num_workers',
        help='number of workers',
        type=int,
        default=1,
    )
    parser.add_argument(
        '--publish',
        help='publish database',
        action='store_true',
    )

    return parser


def main(args):

    TMP_ROOT = os.getcwd()
    os.chdir(ROOT)

    # load previous version

    db = audb.load_to(
        ROOT,
        'vadtoolkit',
        version=PREVIOUS_VERSION,
        num_workers=args.num_workers,
    )
    db.meta.pop('audb')

    # add missing fields

    db.author = 'Kim Jaeseok'
    db.languages = [audformat.utils.map_language('Korean')]
    db.license = 'GPLv3'
    db.license_url = 'https://www.gnu.org/licenses/gpl-3.0.en.html'
    db.organization = (
        'Speech and Audio Information Laboratory, KAIST, South Korea'
    )

    # add noise scheme

    db.schemes['noise'] = audformat.Scheme(
        labels={
            0: 'bus_stop',
            1: 'construction_site',
            2: 'park',
            3: 'room',
        },
    )

    # map file names to noise ID

    noise_map = {
        value: key for key, value in db.schemes['noise'].labels.items()
    }
    noise = [audeer.basename_wo_ext(file) for file in db['segments'].files]
    noise = [noise_map[x] for x in noise]

    # add column with noise ID

    db['segments']['noise'] = audformat.Column(scheme_id='noise')
    db['segments']['noise'].set(noise)

    db.save('.')

    if args.publish:
        repository = REPOSITORY_PUBLIC
    else:
        repository = REPOSITORY_LOCAL

    if PREVIOUS_VERSION is None:
        if os.path.exists('db.csv'):
            os.remove('db.csv')

    audb.publish(
        '.',
        VERSION,
        repository,
        num_workers=args.num_workers,
        previous_version=PREVIOUS_VERSION,
        verbose=True,
    )

    print(db)

    os.chdir(TMP_ROOT)


def cli():

    parser = command_line_args()
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    cli()
