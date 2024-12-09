import pandas as pd

import audeer
import audformat


build_dir = './build'

db = audformat.Database(
    'wham',
    source='http://wham.whisper.ai',
    usage='research',
    languages=None,
    description=(
        'The noise audio was collected '
        'at various urban locations '
        'throughout the San Francisco Bay Area '
        'in late 2018. '
        'The environments primarily consist of restaurants, '
        'cafes, '
        'bars, '
        'and parks. '
        'Audio was recorded '
        'using an Apogee Sennheiser binaural microphone '
        'on a tripod between 1.0 and 1.5 meters off the ground. '
        'The noise dataset has been processed '
        'to remove any segments containing intelligible speech. '
        'The average clip duration is 10.5 seconds with the shortest '
        'clip being 3.4 seconds and the longest 47.7 seconds.'
    ),
    author=(
        'Gordon Wichern, '
        'Joe Antognini, '
        'Michael Flynn, '
        'Licheng Richard Zhu, '
        'Emmett McQuinn, '
        'Dwight Crow, '
        'Ethan Manilow, '
        'Jonathan Le Roux'
    ),
    license='CC-BY-NC-4.0',
)

db.splits['train'] = audformat.Split('train')
db.splits['dev'] = audformat.Split('dev')
db.splits['test'] = audformat.Split('test')

dfs = {}
dfs['train'] = pd.read_csv(audeer.path('metadata', 'noise_meta_tr.csv'))
dfs['dev'] = pd.read_csv(audeer.path('metadata', 'noise_meta_cv.csv'))
dfs['test'] = pd.read_csv(audeer.path('metadata', 'noise_meta_tt.csv'))

df = pd.concat(dfs)
df['L to R Width (cm)'] = df['L to R Width (cm)'].map(
    lambda x: float(x.split(' ')[0]) / 100
)
df['Reverberation Level'] = df['Reverberation Level'].map(
    {'l': 'low', 'm': 'medium', 'h': 'high'}
)

db.schemes['noise-band'] = audformat.Scheme(
    'int',
    labels=[0, 1, 2, 3],
    description=(
        'Pre-amp gain of the microphones '
        'was consistent between all recordings, '
        'and files were grouped by their level (noise-band) '
        'ranging from 0 (very quiet) to 3 (very loud). '
        'Care was taken to ensure that the clips were uniformly sampled '
        'across the four bands, as otherwise quieter locations '
        'would be over-represented.'
    ),
)
db.schemes['file-id'] = audformat.Scheme(
    'str',
    description=(
        'All files from the same original recording share this ID'
    )
)
db.schemes['l-to-r-width'] = audformat.Scheme(
    'float',
    labels=sorted(list(set(df['L to R Width (cm)']))),
    description=(
        'Horizontal spacing between the two microphones in m'
    ),
)
db.schemes['reverberation'] = audformat.Scheme(
    'str',
    labels=['low', 'medium', 'high'],
    description=(
        "A subjective rating indicating "
        "whether the reverberation in the space "
        "was high, "
        "medium, "
        "or low"
    ),
)
db.schemes['location'] = audformat.Scheme(
    'str',
    labels=sorted(list(set(df['Location ID']))),
    description=(
        'All files recorded in the same location share this ID'
    ),
)
db.schemes['day'] = audformat.Scheme(
    'str',
    labels=sorted(list(set(df['Location Day ID']))),
    description=(
        'All files recorded at a given location on the same day share this ID'
    ),
)

folder_mapping = {
    'train': 'tr',
    'dev': 'cv',
    'test': 'tt',
}
for split in list(db.splits):
    files = df.loc[split]['utterance_id']
    files = [f'{folder_mapping[split]}/{file}' for file in files]
    index = audformat.filewise_index(files)
    db[split] = audformat.Table(index, split_id=split)
    db[split]['noise-band'] = audformat.Column(scheme_id='noise-band')
    db[split]['noise-band'].set(df.loc[split]['Noise Band'].values)
    db[split]['file-id'] = audformat.Column(scheme_id='file-id')
    db[split]['file-id'].set(df.loc[split]['File ID'].values)
    db[split]['l-to-r-width'] = audformat.Column(scheme_id='l-to-r-width')
    db[split]['l-to-r-width'].set(df.loc[split]['L to R Width (cm)'].values)
    db[split]['reverberation'] = audformat.Column(scheme_id='reverberation')
    db[split]['reverberation'].set(df.loc[split]['Reverberation Level'].values)
    db[split]['location'] = audformat.Column(scheme_id='location')
    db[split]['location'].set(df.loc[split]['Location ID'].values)
    db[split]['day'] = audformat.Column(scheme_id='day')
    db[split]['day'].set(df.loc[split]['Location Day ID'].values)

db.save(build_dir)

# Add audio files to build dir
for folder in ['cv', 'tr', 'tt']:
    audeer.move(folder, audeer.path(build_dir, folder))
