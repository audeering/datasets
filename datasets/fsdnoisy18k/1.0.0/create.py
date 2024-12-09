import pandas as pd

import audb
import audeer
import audformat


build_root = audeer.mkdir('build')
audio_root = 'audio'


description = (
   'FSDnoisy18k is an audio dataset collected with the aim of fostering '
   'the investigation of label noise in sound event classification. '
   'It contains 42.5 hours of audio across 20 sound classes, '
   'including a small amount of manually-labeled data and '
   'a larger quantity of real-world noisy data. '
   'FSDnoisy18k contains 18,532 audio clips (42.5h) '
   'unequally distributed in the 20 classes drawn from the AudioSet Ontology. '
   'The audio clips are of variable length ranging from 300ms to 30s, '
   'and each clip has a single ground truth label (singly-labeled data). '
   'Files are released under either CC-BY or CC0. '
   'The individual license for each clip is available from the files table. '
   'FSDnoisy18k is an expandable dataset that features a per-class '
   'varying degree of types and amount of label noise. '
   'The dataset allows investigation of label noise '
   'as well as other approaches, from semi-supervised learning, '
   'e.g., self-training to learning with minimal supervision.'
)

db = audformat.Database(
    name='fsdnoisy18k',
    author='Eduardo Fonseca, Mercedes Collado, Manoj Plakal, Daniel P. W. Ellis, Frederic Font, Xavier Favory, and Xavier Serra',
    license='CC-BY-3.0',
    license_url = 'https://creativecommons.org/licenses/by/3.0/',
    source='http://www.eduardofonseca.net/FSDnoisy18k/',
    usage=audformat.define.Usage.UNRESTRICTED,
    description=description,
)

# Parse meta information

splits = ['test', 'train']
licenses = {
    'CC-BY-3.0': 'http://creativecommons.org/licenses/by/3.0/',
    'CC0-1.0': 'http://creativecommons.org/publicdomain/zero/1.0/',
}

doc = pd.read_csv('doc/LICENSE-INDIVIDUAL-CLIPS.csv')
doc = doc.drop_duplicates(subset='fname')  # some files are twice
doc = doc.set_index('fname').squeeze()
doc = doc.map({v: k for k, v in licenses.items()})


def to_audioset_label(label):
    r"""Convert audioset label

    https://research.google.com/audioset/ontology/

    """
    if label == 'Dishes_and_pots_and_pans':
        return 'Dishes, pots, and pans'
    elif label == 'Walk_or_footsteps':
        return 'Walk, footsteps'
    return label.replace('_', ' ')


meta = {}
for split in splits:
    df = pd.read_csv(f'meta/{split}.csv')
    df.label = df.label.map(to_audioset_label)
    df['license'] = doc[df.fname].values
    df.fname = f'{audio_root}/{split}/' + df.fname
    df = df.set_index('fname')
    df.index.name = 'file'
    meta[split] = df


labels = sorted(meta['test']['label'].unique())
files = audformat.utils.union([df.index for df in meta.values()])


# Get additional label information from audioset

audioset_schemes = audb.info.schemes(
    'audioset',
    version='1.2.1',
    load_tables=False,
)
categories = {}
for label in labels:
    categories[label] = audioset_schemes['categories'].labels[label]


# Schemes

db.schemes['categories'] = audformat.Scheme(
    labels=categories,
    description='20 classes drawn from AudioSet Ontology.'
)
db.schemes['license'] = audformat.Scheme(
    labels=licenses,
    description='Licenses clips are released under.'
)
db.schemes['manually_verified'] = audformat.Scheme(
    'bool',
    description=(
        'Boolean flag to indicate whether the clip belongs '
        'to the clean portion (True), or to the '
        'noisy portion (False) of the train set.'
    ),
)
db.schemes['noisy_small'] = audformat.Scheme(
    'bool',
    description=(
        'Boolean flag to indicate whether the clip belongs '
        'to the noisy_small portion (True) of the train set.'
    ),
)

# Media

db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=44100,
    channels=1,
)

# Splits

db.splits['train'] = audformat.Split(
    audformat.define.SplitType.TRAIN,
    description=(
        'The train set is composed of 17,585 clips (41.1h) '
        'unequally distributed among the 20 classes. '
        'It features a clean subset and a noisy subset. '
        'In terms of number of clips their proportion is 10%/90%, '
        'whereas in terms of duration the proportion '
        'is slightly more extreme (6%/94%). '
        'The per-class percentage of clean data within '
        'the train set is also imbalanced, '
        'ranging from 6.1% to 22.4%. '
        'The number of audio clips per class ranges from 51 to 170, '
        'and from 250 to 1000 in the clean and noisy subsets, respectively. '
        'Further, a noisy small subset is defined, '
        'which includes an amount of (noisy) data comparable '
        '(in terms of duration) to that of the clean subset.'
    )
)
db.splits['test'] = audformat.Split(
    audformat.define.SplitType.TEST,
    description=(
        'The test set is composed of 947 clips (1.4h) that '
        'belong to the clean portion of the data. '
        'Its class distribution is similar to that '
        'of the clean subset of the train set. '
        'The number of per-class audio clips in the test set ranges from 30 to 72. '
        'The test set enables a multi-class classification problem.'
    )
)

# Tables

index = audformat.filewise_index(files)
db['files'] = audformat.Table(
    index,
    media_id='microphone',
)

db['files']['license'] = audformat.Column(scheme_id='license')

for split, df in meta.items():

    db[split] = audformat.Table(
        df.index,
        split_id=split,
        media_id='microphone',
    )
    db[split]['label'] = audformat.Column(scheme_id='categories')
    db[split]['label'].set(df.label)

    if split == 'train':
        db[split]['manually_verified'] = audformat.Column(scheme_id='manually_verified')
        db[split]['manually_verified'].set(df.manually_verified)
        db[split]['noisy_small'] = audformat.Column(scheme_id='noisy_small')
        db[split]['noisy_small'].set(df.noisy_small)

    db['files']['license'].set(df.license, index=df.index)


# Save to disk

db.save(build_root)
