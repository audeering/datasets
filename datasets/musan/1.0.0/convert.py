import os

import pandas as pd

import audeer
import audformat
import audiofile


build_dir = audeer.mkdir('./build')

db = audformat.Database(
    name='musan',
    author='David Snyder, Guoguo Chen, Daniel Povey',
    organization=(
        'Center for Language and Speech Processing, '
        'Johns Hopkins University'
    ),
    license='CC-BY-4.0',
    source='http://www.openslr.org/17/',
    usage='commercial',
    languages=[
        'Arabic',
        'Chinese',
        'Danish',
        'Dutch',
        'English',
        'French',
        'German',
        'Hebrew',
        'Hungarian',
        'Italian',
        'Japanese',
        'Latin',
        'Polish',
        'Portuguese',
        'Russian',
        'Spanish',
        'Tagalog',
    ],
    description=(
        'The goal of this corpus is to provide data '
        'for music/speech discrimination, '
        'speech/nonspeech detection, '
        'and voice activity detection. '
        'The corpus is divided into music, speech, and noise portions. '
        'In total there are approximately 109 hours of audio. '
        'Reference: '
        'https://arxiv.org/abs/1510.08484'
    ),
)

# Media
db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=16000,
    channels=1,
)

# Schemes
db.schemes['duration'] = audformat.Scheme('time')
db.schemes['genre'] = audformat.Scheme('str')
db.schemes['artist'] = audformat.Scheme('str')
db.schemes['composer'] = audformat.Scheme('str')
db.schemes['vocals'] = audformat.Scheme(
    'bool',
    description='Indicate if vocals are present in music',
)
db.schemes['gender'] = audformat.Scheme(labels=['female', 'male'])
db.schemes['language'] = audformat.Scheme(labels=db.languages)
db.schemes['background_noise'] = audformat.Scheme('bool')

files = []

# Music tables
task = 'music'
folder = os.path.join(build_dir, task)
groups = audeer.list_dir_names(folder, basenames=True)
columns = ['genre', 'vocals', 'artist', 'composer']
dfs = []
for group in groups:
    sub_folder = os.path.join(folder, group)
    sub_files = audeer.list_file_names(sub_folder, filetype='wav')
    sub_files = [f[len(build_dir) + 1:] for f in sub_files]
    files += sub_files
    index = audformat.filewise_index(sub_files)
    db[f'{task}.{group}'] = audformat.Table(index)
    df = pd.read_csv(
        os.path.join(sub_folder, 'ANNOTATIONS'),
        delimiter=' ',
        names=['file'] + columns,
        converters={'vocals': lambda x: x == 'Y'},
        index_col='file',
    )
    df.index = f'{task}/{group}/' + df.index + '.wav'
    dfs.append(df)
    for column in columns:
        db[f'{task}.{group}'][column] = audformat.Column(scheme_id=column)
        db[f'{task}.{group}'][column].set(df[column], index=df.index)

dfs = pd.concat(dfs)
index = audformat.filewise_index(dfs.index)
db[task] = audformat.Table(index)
for column in columns:
    db[task][column] = audformat.Column(scheme_id=column)
    db[task][column].set(dfs[column])

# Speech tables
task = 'speech'
folder = os.path.join(build_dir, task)
columns = ['gender', 'language']
dfs = []
group = 'librivox'
sub_folder = os.path.join(folder, group)
sub_files = audeer.list_file_names(sub_folder, filetype='wav')
sub_files = [f[len(build_dir) + 1:] for f in sub_files]
files += sub_files
index = audformat.filewise_index(sub_files)
db[f'{task}.{group}'] = audformat.Table(index)
df = pd.read_csv(
    os.path.join(sub_folder, 'ANNOTATIONS'),
    delimiter=' ',
    names=['file'] + columns + ['garbage'],
    converters={'language': audformat.utils.map_language},
    index_col='file',
)
df['gender'] = df['gender'].map({'m': 'male', 'f': 'female'})
df.index = f'{task}/{group}/' + df.index + '.wav'
df_gender = df
dfs.append(df)
for column in columns:
    db[f'{task}.{group}'][column] = audformat.Column(scheme_id=column)
    db[f'{task}.{group}'][column].set(df[column], index=df.index)
group = 'us-gov'
sub_folder = os.path.join(folder, group)
sub_files = audeer.list_file_names(sub_folder, filetype='wav')
sub_files = [f[len(build_dir) + 1:] for f in sub_files]
files += sub_files
index = audformat.filewise_index(sub_files)
db[f'{task}.{group}'] = audformat.Table(index)
df = pd.DataFrame(index=index)
df['language'] = audformat.utils.map_language('English')
dfs.append(df)
for column in columns:
    db[f'{task}.{group}'][column] = audformat.Column(scheme_id=column)
db[f'{task}.{group}']['language'].set(df.language)

dfs = pd.concat(dfs)
index = audformat.filewise_index(dfs.index)
db[task] = audformat.Table(index)
for column in columns:
    db[task][column] = audformat.Column(scheme_id=column)
db[task]['gender'].set(df_gender.gender, index=df_gender.index)
db[task]['language'].set(dfs.language)

# Noise
task = 'noise'
folder = os.path.join(build_dir, task)
groups = audeer.list_dir_names(folder)
columns = ['background_noise']
dfs = []
group = 'free-sound'
sub_folder = os.path.join(folder, group)
sub_files = audeer.list_file_names(sub_folder, filetype='wav')
sub_files = [f[len(build_dir) + 1:] for f in sub_files]
files += sub_files
index = audformat.filewise_index(sub_files)
db[f'{task}.{group}'] = audformat.Table(index)
df = pd.DataFrame(index=index)
df['background_noise'] = False
df_background = pd.read_csv(
    os.path.join(sub_folder, 'ANNOTATIONS'),
    header=0,
    names=['file'],
    index_col='file',
)
df_background.index = f'{task}/{group}/' + df_background.index + '.wav'
df.loc[df_background.index, 'background_noise'] = True
dfs.append(df)
for column in columns:
    db[f'{task}.{group}'][column] = audformat.Column(scheme_id=column)
    db[f'{task}.{group}'][column].set(df[column])
group = 'sound-bible'
sub_folder = os.path.join(folder, group)
sub_files = audeer.list_file_names(sub_folder, filetype='wav')
sub_files = [f[len(build_dir) + 1:] for f in sub_files]
files += sub_files
index = audformat.filewise_index(sub_files)
db[f'{task}.{group}'] = audformat.Table(index)
df = pd.DataFrame(index=index)
df['background_noise'] = False
dfs.append(df)
for column in columns:
    db[f'{task}.{group}'][column] = audformat.Column(scheme_id=column)
    db[f'{task}.{group}'][column].set(df[column])

dfs = pd.concat(dfs)
index = audformat.filewise_index(dfs.index)
db[task] = audformat.Table(index)
for column in columns:
    db[task][column] = audformat.Column(scheme_id=column)
    db[task][column].set(dfs[column])

# Files table
index = audformat.filewise_index(files)
db['files'] = audformat.Table(index)
db['files']['duration'] = audformat.Column(scheme_id='duration')
durations = audeer.run_tasks(
    task_func=lambda x: pd.to_timedelta(
        audiofile.duration(os.path.join(build_dir, x)),
        unit='s',
    ),
    params=[([f], {}) for f in files],
    num_workers=8,
    progress_bar=True,
    task_description='Estimate durations',
)
db['files']['duration'].set(durations)

db.save(build_dir, storage_format='csv')
