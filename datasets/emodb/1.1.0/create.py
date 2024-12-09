import os
import shutil

import audeer
import audformat
import audiofile as af
import pandas as pd


src_dir = 'src'
build_dir = audeer.mkdir('build')


# Prepare functions for getting information from file names
def parse_names(names, from_i, to_i, is_number=False, mapping=None):
    for name in names:
        key = name[from_i:to_i]
        if is_number:
            key = int(key)
        yield mapping[key] if mapping else key


# Gather metadata
description = (
   'Berlin Database of Emotional Speech. '
   'A German database of emotional utterances '
   'spoken by actors '
   'recorded as a part of the DFG funded research project '
   'SE462/3-1 in 1997 and 1999. '
   'Recordings took place in the anechoic chamber '
   'of the Technical University Berlin, '
   'department of Technical Acoustics. '
   'It contains about 500 utterances '
   'from ten different actors '
   'expressing basic six emotions and neutral.'
)

files = sorted(
    [os.path.join('wav', f) for f in os.listdir(os.path.join(src_dir, 'wav'))]
)
names = [audeer.basename_wo_ext(f) for f in files]

emotion_mapping = {
    'W': 'anger',
    'L': 'boredom',
    'E': 'disgust',
    'A': 'fear',
    'F': 'happiness',
    'T': 'sadness',
    'N': 'neutral',
}
emotions = list(parse_names(names, from_i=5, to_i=6, mapping=emotion_mapping))

y = pd.read_csv(
    os.path.join(src_dir, 'erkennung.txt'),
    usecols=['Satz', 'erkannt'],
    index_col='Satz',
    delim_whitespace=True,
    encoding='Latin-1',
    decimal=',',
    converters={'Satz': lambda x: os.path.join('wav', x)},
    squeeze=True,
)
y = y.loc[files]
y = y.replace(to_replace=u'\xa0', value='', regex=True)
y = y.replace(to_replace=',', value='.', regex=True)
confidences = y.astype('float').values

male = audformat.define.Gender.MALE
female = audformat.define.Gender.FEMALE
language = audformat.utils.map_language('de')
speaker_mapping = {
    3: {'gender': male, 'age': 31, 'language': language},
    8: {'gender': female, 'age': 34, 'language': language},
    9: {'gender': male, 'age': 21, 'language': language},
    10: {'gender': female, 'age': 32, 'language': language},
    11: {'gender': male, 'age': 26, 'language': language},
    12: {'gender': female, 'age': 30, 'language': language},
    13: {'gender': male, 'age': 32, 'language': language},
    14: {'gender': female, 'age': 35, 'language': language},
    15: {'gender': male, 'age': 25, 'language': language},
    16: {'gender': female, 'age': 31, 'language': language},
}
speakers = list(parse_names(names, from_i=0, to_i=2, is_number=True))

transcription_mapping = {
    'a01': 'Der Lappen liegt auf dem Eisschrank.',
    'a02': 'Das will sie am Mittwoch abgeben.',
    'a04': 'Heute abend könnte ich es ihm sagen.',
    'a05': 'Das schwarze Stück Papier befindet sich da oben neben dem '
           'Holzstück.',
    'a07': 'In sieben Stunden wird es soweit sein.',
    'b01': 'Was sind denn das für Tüten, die da unter dem Tisch '
           'stehen.',
    'b02': 'Sie haben es gerade hochgetragen und jetzt gehen sie '
           'wieder runter.',
    'b03': 'An den Wochenenden bin ich jetzt immer nach Hause '
           'gefahren und habe Agnes besucht.',
    'b09': 'Ich will das eben wegbringen und dann mit Karl was '
           'trinken gehen.',
    'b10': 'Die wird auf dem Platz sein, wo wir sie immer hinlegen.',
}
transcriptions = list(parse_names(names, from_i=2, to_i=5))

durations = audeer.run_tasks(
    task_func=lambda x: pd.to_timedelta(
        af.duration(os.path.join(src_dir, x)),
        unit='s',
    ),
    params=[([f], {}) for f in files],
    num_workers=12,
)

# Convert to audformat
db = audformat.Database(
    name='emodb',
    author=(
        'Felix Burkhardt, '
        'Astrid Paeschke, '
        'Miriam Rolfes, '
        'Walter Sendlmeier, '
        'Benjamin Weiss'
    ),
    organization='audEERING',
    license=audformat.define.License.CC0_1_0,
    source='http://emodb.bilderbar.info/download/download.zip',
    usage=audformat.define.Usage.UNRESTRICTED,
    languages=[language],
    description=description,
    meta={
        'pdf': (
            'http://citeseerx.ist.psu.edu/viewdoc/'
            'download?doi=10.1.1.130.8506&rep=rep1&type=pdf'
        ),
    },
)

# Media
db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=16000,
    channels=1,
)

# Raters
db.raters['gold'] = audformat.Rater()

# Schemes
db.schemes['emotion'] = audformat.Scheme(
    labels=[str(x) for x in emotion_mapping.values()],
    description='Six basic emotions and neutral.',
)
db.schemes['confidence'] = audformat.Scheme(
    audformat.define.DataType.FLOAT,
    minimum=0,
    maximum=1,
    description='Confidence of emotion ratings.',
)
db.schemes['speaker'] = audformat.Scheme(
    labels=speaker_mapping,
    description=(
        'The actors could produce each sentence as often as '
        'they liked and were asked to remember a real '
        'situation from their past when they had felt this '
        'emotion.'
    ),
)
db.schemes['transcription'] = audformat.Scheme(
    labels=transcription_mapping,
    description='Sentence produced by actor.',
)
db.schemes['duration'] = audformat.Scheme(dtype=audformat.define.DataType.TIME)

# Tables
index = audformat.filewise_index(files)
db['files'] = audformat.Table(index)

db['files']['duration'] = audformat.Column(scheme_id='duration')
db['files']['duration'].set(durations, index=index)

db['files']['speaker'] = audformat.Column(scheme_id='speaker')
db['files']['speaker'].set(speakers)

db['files']['transcription'] = audformat.Column(scheme_id='transcription')
db['files']['transcription'].set(transcriptions)

db['emotion'] = audformat.Table(index)
db['emotion']['emotion'] = audformat.Column(
    scheme_id='emotion',
    rater_id='gold',
)
db['emotion']['emotion'].set(emotions)
db['emotion']['emotion.confidence'] = audformat.Column(
    scheme_id='confidence',
    rater_id='gold',
)
db['emotion']['emotion.confidence'].set(confidences / 100.0)

# Save database to build folder
shutil.copytree(
    os.path.join(src_dir, 'wav'),
    os.path.join(build_dir, 'wav'),
)
db.save(build_dir)
