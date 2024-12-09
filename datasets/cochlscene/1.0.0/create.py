import os

import audeer
import audformat


build_root = audeer.mkdir('build')

description = (
   'Cochl Acoustic Scene Dataset (CochlScene), '
   'is an acoustic scene dataset whose recordings are fully '
   'collected from crowdsourcing participants. '
   'Most of the initial plans and guidelines for the processes '
   'were provided by the researchers in the field of '
   'audio signal processing and machine learning including the authors, '
   'and the actual process was performed by using '
   'the crowdsourcing platform developed by SelectStar, '
   'a Korean crowdsourcing data company. '
   'During the process, the initial plans were reinforced '
   'and modified from the discussion about '
   'the actual difficulty in the collection process. '
   'After extracting the subset of the total collections '
   'considering the purpose of the data, we collected '
   '76,115 10 seconds files in 13 different '
   'acoustic scenes from 831 participants.'
)
audformat.define.License.CC_BY_NC_SA_4_0
db = audformat.Database(
    name='cochlscene',
    author='Il-Young Jeong, Jeongsoo Park',
    license='CC-BY-SA-3.0',
    license_url = 'https://creativecommons.org/licenses/by-sa/3.0/',
    source='https://zenodo.org/record/7080122/',
    usage=audformat.define.Usage.UNRESTRICTED,
    description=description,
)

# Parse meta information

splits = ['dev', 'test', 'train']
labels = [
    'Bus',
    'Cafe',
    'Car',
    'CrowdedIndoor',
    'Elevator',
    'Kitchen',
    'Park',
    'ResidentialArea',
    'Restaurant',
    'Restroom',
    'Street',
    'Subway',
    'SubwayStation',
]

# Schemes

db.schemes['scene'] = audformat.Scheme(
    labels=labels,
    description='13 acoustic scene classes.'
)


# Media

db.media['microphone'] = audformat.Media(
    format='wav',
    sampling_rate=44100,
    channels=1,
)

# Tables

for split in splits:

    files = []
    values = []

    for label in labels:
        folder = f'build/{split}/{label}'
        names = audeer.list_file_names(
            folder,
            basenames=True,
        )
        files.extend([f'{folder}/{name}' for name in names])
        values.extend([label] * len(names))

    db.splits[split] = audformat.Split(split)
    db[split] = audformat.Table(
        audformat.filewise_index(files),
        split_id=split,
        media_id='microphone',
    )
    db[split]['scene'] = audformat.Column(scheme_id='scene')
    db[split]['scene'].set(values)

# Save to disk

db.save(build_root)
