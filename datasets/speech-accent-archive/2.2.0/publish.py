import random

import pandas as pd

import audb
import audformat


random.seed(0)

name = 'speech-accent-archive'
previous_version = '2.1.0'
version = '2.2.0'
build_dir = '../build'

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

# Add a balanced test set for emotions
df = db['files'].get()
languages = sorted(list(set(df.native_language)))
# Select languages containing
# >=5 female speakers
# and >=5 male speakers
num_speakers = 5
selected_languages = []
for language in languages:
    df_language = df[df.native_language == language]
    if (
            len(df_language[df_language.sex == 'female']) >= num_speakers
            and len(df_language[df_language.sex == 'male']) >= num_speakers
    ):
        selected_languages.append(language)
# Select 5 random samples for each language and sex
selected_files = []
for language in selected_languages:
    df_language = df[df.native_language == language]
    for sex in ['female', 'male']:
        df_sex = df_language[df_language.sex == sex]
        selected_files += random.sample(list(df_sex.index), num_speakers)
index = audformat.filewise_index(selected_files)
df = db['files'].get(index=index)
df = df[['native_language', 'sex']]
# Convert to segmented table
segments = db['segments'].get(index=audformat.filewise_index(selected_files))
files = segments.index.get_level_values('file')
test_set = pd.DataFrame(
    df.loc[files].values,
    segments.index,
    columns=df.columns,
)
# Add as new table
db.splits['test'] = audformat.Split('test')
db['accent.test'] = audformat.Table(
    index=test_set.index,
    media_id='microphone',
    split_id='test',
)
db['accent.test']['tone'] = audformat.Column(
    scheme_id='tone',
    rater_id='guess',
    description='Tone of voice',
)
db['accent.test']['native_language'] = audformat.Column(
    scheme_id='native_language',
)
db['accent.test']['sex'] = audformat.Column(
    scheme_id='sex',
)
db['accent.test']['tone'].set('neutral')
db['accent.test']['native_language'].set(test_set.native_language)
db['accent.test']['sex'].set(test_set.sex)

# Update segments table to show content instead of tone
db.schemes['content'] = audformat.Scheme(
    labels=['speech'],
)
db['segments'].drop_columns('tone', inplace=True)
db['segments']['content'] = audformat.Column(
    scheme_id='content',
)
db['segments']['content'].set('speech')
db.save(build_dir)

repository = audb.repository(name, previous_version)
audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
