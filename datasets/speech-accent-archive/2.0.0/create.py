import os

import pandas as pd

import audeer
import audformat
import audiofile
import audresample


src_dir = 'raw'
build_dir = audeer.mkdir('build')
sampling_rate = 16000

# Convert audio data
audio_src_dir = os.path.join(src_dir, 'recordings', 'recordings')
audio_build_dir = audeer.mkdir(os.path.join(build_dir, 'wav'))

for mp3_file in audeer.list_file_names(audio_src_dir):
    basename = audeer.basename_wo_ext(mp3_file)
    wav_file = os.path.join(audio_build_dir, f'{basename}.wav')
    signal, original_rate = audiofile.read(mp3_file, always_2d=True)
    signal = audresample.resample(signal, original_rate, sampling_rate)
    audiofile.write(wav_file, signal, sampling_rate)

# Gather metadata
source = 'https://www.kaggle.com/rtatman/speech-accent-archive'
license = audformat.define.License.CC_BY_NC_SA_4_0
author = 'Rachael Tatman, Steven H. Weinberger, et al.'
organization = 'the speech accent archive'
description = (
   'This dataset contains 2138 speech samples, '
   'each from a different talker '
   'reading the same reading passage. '
   'Talkers come from 177 countries '
   'and have 214 different native languages. '
   'Each talker is speaking in English. '
   '### '
   'All read the following passage: '
   '"Please call Stella. '
   'Ask her to bring these things with her from the store: '
   'Six spoons of fresh snow peas, '
   'five thick slabs of blue cheese, '
   'and maybe a snack for her brother Bob. '
   'We also need a small plastic snake '
   'and a big toy frog for the kids. '
   'She can scoop these things into three red bags, '
   'and we will go meet her Wednesday at the train station." '
   '### '
   'This dataset was collected by many individuals '
   'under the supervision of Steven H. Weinberger. '
   'The most up-to-date version of the archive is hosted at '
   'http://accent.gmu.edu/. '
   'If you use this dataset in your work, '
   'please include the following citation: '
   'Weinberger, S. (2013). Speech accent archive. George Mason University.'
)

files = sorted(
    [
        os.path.join('wav', os.path.basename(f))
        for f in audeer.list_file_names(audio_build_dir)
    ]
)
index = audformat.filewise_index(files)

df = pd.read_csv(
    os.path.join(src_dir, 'speakers_all.csv'),
    usecols=[
        'age',
        'age_onset',
        'birthplace',
        'filename',
        'native_language',
        'sex',
        'speakerid',
        'country',
        'file_missing?',
    ],
)
# Remove missing files
df[df['file_missing?'] == False]  # noqa: E712
df = df.drop(columns='file_missing?')
df = df.rename(
    columns={
        'speakerid': 'speaker',
        'filename': 'file',
    }
)
df['file'] = 'wav/' + df['file'] + '.wav'
df.set_index('file', inplace=True)
df = df.loc[index]
# Fix wrong gender label
df.loc[df['sex'] == 'famale', 'sex'] = 'female'

duration = audeer.run_tasks(
    task_func=lambda x: pd.to_timedelta(
        audiofile.duration(os.path.join(build_dir, x)),
        unit='s',
    ),
    params=[([f], {}) for f in files],
    num_workers=12,
)

# Convert to audformat
db = audformat.Database(
    name='speech-accent-archive',
    author=author,
    organization=organization,
    license=license,
    source=source,
    usage=audformat.define.Usage.RESEARCH,
    languages=['English'],
    description=description,
)

# Media
db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=sampling_rate,
    channels=1,
)

# Schemes
db.schemes['age'] = audformat.Scheme(audformat.define.DataType.INTEGER)
db.schemes['age_onset'] = audformat.Scheme(
    audformat.define.DataType.INTEGER,
    description='Age when the speaker learned English.',
)
db.schemes['birthplace'] = audformat.Scheme(audformat.define.DataType.STRING)
db.schemes['native_language'] = audformat.Scheme(
    audformat.define.DataType.STRING
)
db.schemes['sex'] = audformat.Scheme(
    audformat.define.DataType.STRING,
    labels=['female', 'male'],
)
db.schemes['speaker'] = audformat.Scheme(audformat.define.DataType.INTEGER)
db.schemes['country'] = audformat.Scheme(
    audformat.define.DataType.STRING,
    description='Current residence.',
)
db.schemes['duration'] = audformat.Scheme(dtype=audformat.define.DataType.TIME)

# Tables
db['files'] = audformat.Table(index)

for scheme_id in db.schemes:
    db['files'][scheme_id] = audformat.Column(scheme_id=scheme_id)

db['files']['age'].set(df.age.astype(int))
db['files']['age_onset'].set(df.age_onset.astype(int))
db['files']['birthplace'].set(df.birthplace)
db['files']['native_language'].set(df.native_language)
db['files']['sex'].set(df.sex)
db['files']['speaker'].set(df.speaker)
db['files']['country'].set(df.country)
db['files']['duration'].set(duration)

# Save database to build folder
db.save(build_dir)
