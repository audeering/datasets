import os

import numpy as np

import audeer
import audformat


build_dir = audeer.mkdir('../build')

db = audformat.Database(
    name='air',
    author=(
        'Marco Jeub, '
        'Magnus Schäfer, '
        'Hauke Krüger, '
        'Christoph Matthias Nelke, '
        'Christophe Beaugeant, '
        'Peter Vary'
    ),
    organization=(
        'Institue of Communication Systems, '
        'RWTH Aachen University'
    ),
    license='MIT',
    license_url='https://opensource.org/licenses/MIT',
    source=(
        'https://www.iks.rwth-aachen.de/en/research/tools-downloads/databases/'
        'aachen-impulse-response-database/'
    ),
    usage='commercial',
    description=(
        'The Aachen Impulse Response (AIR) database '
        'is a set of impulse responses that were measured '
        'in a wide variety of rooms. '
        'The initial aim of the AIR database '
        'was to allow for realistic studies of signal processing algorithms '
        'in reverberant environments '
        'with a special focus on hearing aids applications. '
        'The first version was published in 2009 '
        'and offers binaural room impulse responses (BRIR) '
        'measured with a dummy head in different locations '
        'with different acoustical properties, '
        'such as reverberation time and room volume. '
        'Besides the evaluation of dereverberation algorithms '
        'and perceptual investigations of reverberant speech, '
        'this part of the database allows for the investigation '
        'of head shadowing influence '
        'since all recordings where made with and without the dummy head. '
        'In a first update, '
        'the database was extended to BRIRs with various azimuth angles '
        'between head and desired source. '
        'This further allows '
        'to investigate (binaural) direction-of-arrival (DOA) algorithms '
        'as well as the influence of signal processing algorithms '
        'on the binaural cues. '
        'Since dereverberation can also be applied to telephone speech, '
        'the latest extension includes (dual-channel) impulse responses '
        'between the artificial mouth of a dummy head '
        'and a mock-up phone. '
        'The measurements were carried out in compliance '
        'with the ITU standards '
        'for both the hand-held '
        'and the hands-free position. '
        'Additional microphone configurations were added '
        'in the latest extension. '
        'For the third big extension, '
        'the IKS has carried out measurements '
        'of binaural room impulse responses in the Aula Carolina Aachen. '
        'The former church with a ground area of 570m² '
        'and a high ceiling shows very strong reverberation effects. '
        'The database will successively be extended '
        'to further application scenarios. '
    ),
)

# Media
db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=48000,
    channels=2,
)

# Schemes
db.schemes['azimuth'] = audformat.Scheme(
    'float',
    description='Azimuth of dummy head',
)
db.schemes['distance'] = audformat.Scheme(
    'float',
    description=(
        'Distance in meters '
        'between microphone and loudspeaker'
    ),
)
db.schemes['mode'] = audformat.Scheme(
    labels=['hand-held', 'hands-free'],
    description='Position of phone',
)
db.schemes['reverberation-time'] = audformat.Scheme(
    'float',
    description='Reverberation time RT60',
)

db.schemes['room'] = audformat.Scheme(
    labels={
        'aula_carolina': {
            'room length': None,
            'room width': None,
            'room height': None,
            'wall surface': None,
            'floor cover': None,
            'furniture': None,
        },
        'bathroom': {
            'room length': None,
            'room width': None,
            'room height': None,
            'wall surface': None,
            'floor cover': None,
            'furniture': None,
        },
        'booth': {
            'room length': 3.0,
            'room width': 1.8,
            'room height': 2.2,
            'wall surface': 'custom-made low reflective panels',
            'floor cover': 'carpet',
            'furniture': '',
        },
        'corridor': {
            'room length': None,
            'room width': None,
            'room height': None,
            'wall surface': None,
            'floor cover': None,
            'furniture': None,
        },
        'kitchen': {
            'room length': None,
            'room width': None,
            'room height': None,
            'wall surface': None,
            'floor cover': None,
            'furniture': None,
        },
        'lecture': {
            'room length': 10.8,
            'room width': 10.9,
            'room height': 3.15,
            'wall surface': '3x glass windows, 1x concrete wall',
            'floor cover': 'parquet',
            'furniture': 'wooden tables, chairs',
        },
        'office': {
            'room length': 5.0,
            'room width': 6.4,
            'room height': 2.9,
            'wall surface': 'glass windows, concrete',
            'floor cover': 'carpet',
            'furniture': 'wooden desk, shelves, chairs',
        },
        'meeting': {
            'room length': 8.0,
            'room width': 5.0,
            'room height': 3.1,
            'wall surface': 'glass windows, concrete',
            'floor cover': 'carpet',
            'furniture': 'wooden conference table, bookshelfs',
        },
        'stairway': {
            'room length': None,
            'room width': None,
            'room height': None,
            'wall surface': None,
            'floor cover': None,
            'furniture': None,
        },
    },
    description='Recording rooms',
)
files = audeer.list_file_names(
    os.path.join(build_dir, 'data'),
    basenames=True,
)

# == RIRs ==
rir_files = [
    f for f in files
    if f.startswith('air_binaural')
    and f.split('_')[3] == '0'
]
index = audformat.filewise_index([f'data/{f}' for f in rir_files])
db['rir'] = audformat.Table(
    index,
    description=(
        'Impulse responses measured with '
        'Beyerdynamic MM1 omnidirectional condenser measurement microphones. '
        'RME Octamic II microphone amplifier '
        'in combination with RME Multifac II. '
        'The distance between both microphones was 0.17 m. '
        'The height of the loudspeaker and the microphones was 1.2 m. '
        'As loudspeaker a Genelec 8130 was used. '
        'The dummy head was simply removed for this measurement.'
    ),
)
rooms = [f.split('_')[2] for f in rir_files]
db['rir']['room'] = audformat.Column(scheme_id='room')
db['rir']['room'].set(rooms)
# Distances and reverberation times as given in the paper
# and the Matlab source code
# https://www.iks.rwth-aachen.de/fileadmin/publications/jeub09a.pdf
distances = [
    0.5, 1.0, 1.5,  # booth
    2.25, 4.0, 5.56, 7.1, 8.68, 10.2,  # lecture
    1.45, 1.7, 1.9, 2.25, 2.8,  # meeting
    1.0, 2.0, 3.0,  # office
]
rts = [
    0.08, 0.11, 0.18,  # booth
    0.70, 0.72, 0.79, 0.80, 0.81, 0.83,  # lecture
    0.21, 0.22, 0.21, 0.24, 0.25,  # meeting
    0.37, 0.44, 0.48,  # office
]
db['rir']['distance'] = audformat.Column(scheme_id='distance')
db['rir']['distance'].set(distances)
db['rir']['reverberation-time'] = audformat.Column(
    scheme_id='reverberation-time'
)
db['rir']['reverberation-time'].set(rts)

# == BRIRs ==
brir_files = [
    f for f in files
    if f.startswith('air_binaural')
    and f not in rir_files
]
index = audformat.filewise_index([f'data/{f}' for f in brir_files])
db['brir'] = audformat.Table(
    index,
    description=(
        'Binaural impulse responses measured with '
        'HMS II.3 artificial head by HEAD Acoustics, '
        'using Beyerdynamic MM1 omnidirectional condenser '
        'measurement microphones. '
        'RME Octamic II microphone amplifier '
        'in combination with RME Multifac II. '
        'Microphones were positioned close to the pinna '
        'at 1 cm from the ear canal.'
        'The distance between both microphones was 0.17 m. '
        'The height of the loudspeaker and the microphones was 1.2 m. '
        'As loudspeaker a Genelec 8130 was used. '
        'The dummy head was simply removed for this measurement.'
    ),
)
rooms = [
    f.split('_')[2]
    if 'aula_carolina' not in f
    else 'aula_carolina'
    for f in brir_files
]
db['brir']['room'] = audformat.Column(scheme_id='room')
db['brir']['room'].set(rooms)
# Distances and azimuth angles as given in the paper
# and the Matlab source code
# https://www.iks.rwth-aachen.de/fileadmin/publications/jeub09a.pdf
distances = [
    1, 2, 3, 3, 3, 3, 3, 5, 15, 20, np.NaN,  # aula_carolina
    0.5, 1.0, 1.5,  # booth
    2.25, 4.0, 5.56, 7.1, 8.68, 10.2,  # lecture
    1.45, 1.7, 1.9, 2.25, 2.8,  # meeting
    1.0, 2.0, 3.0,  # office
]
distances += [1] * 13  # stairway
distances += [2] * 13  # stairway
distances += [3] * 13  # stairway
azimuths = [
    90, 90, 0, 135, 180, 45, 90, 90, 90, 90, 90,  # aula_carolina
    90, 90, 90,  # booth
    90, 90, 90, 90, 90, 90,  # lecture
    90, 90, 90, 90, 90,  # meeting
    90, 90, 90,  # office
]
# stairway
azimuths += [0, 105, 120, 135, 15, 150, 165, 180, 30, 45, 60, 75, 90] * 3
db['brir']['distance'] = audformat.Column(scheme_id='distance')
db['brir']['distance'].set(distances)
db['brir']['distance'] = audformat.Column(scheme_id='azimuth')
db['brir']['distance'].set(azimuths)

# == Phone ==
phone_files = [f for f in files if f.startswith('air_phone')]
index = audformat.filewise_index([f'data/{f}' for f in phone_files])
db['phone'] = audformat.Table(
    index,
    description=(
        'Stereo phone impulse responses measured with '
        'Beyerdynamic MM1 omnidirectional condenser measurement microphones. '
        'RME Octamic II microphone amplifier '
        'in combination with RME Multifac II. '
        'As loudspeaker a Genelec 8130 was used. '
        'Microphones were placed 2 cm apart '
        'in front of a mock-up phone. '
        'The phone was mounted on the HMS II.3 artificial head '
        'by HEAD Acoustics, '
        'or at the free-hands reference point.'
    ),
)
rooms = [f.split('_')[-2] for f in phone_files]
rooms = [r[:-1] if r[-1] in ['1', '2'] else r for r in rooms]
db['phone']['room'] = audformat.Column(scheme_id='room')
db['phone']['room'].set(rooms)
modes = [f.split('_')[-1][:-4] for f in phone_files]
modes = ['hands-free' if m == 'hfrp' else 'hand-held' for m in modes]
db['phone']['mode'] = audformat.Column(scheme_id='mode')
db['phone']['mode'].set(modes)

db.save(build_dir)
