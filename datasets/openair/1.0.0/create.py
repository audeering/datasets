import os
import numpy as np
import shutil
from pathlib import Path
import audformat


build_dir = 'data_openair/' # Compute5
# usinal-del-arte has b-format & stereo but b-format is monochannel wavs
rooms = [
        ('1st-baptist-nashville', 2.59),
        ('alcuin-college-university-york', 1.61),
        ('hamilton-mausoleum', 12.45),
        ('saint-lawrence-church-molenbeek-wersbeek-belgium', 1.57),
        ('st-patricks-church-patrington', 1.83),
        ('arthur-sykes-rymer-auditorium-university-york', 0.39),
        ('heslington-church-vaa-group-2', 1.75),
        ('shrine-and-parish-church-all-saints-north-street-_', 1.7),
        # ''st-patricks-church-patrington (1)'
        ('central-hall-university-york', 1.11),
        ('hoffmann-lime-kiln-langcliffeuk', 0.93),
        # 'slinky-ir',
        # 'st-patricks-church-patrington-model', 1.79),
        ('creswell-crags', 0.73),
        ('innocent-railway-tunnel', 3.72),
        ('spokane-womans-club', 2.52),
        ('terrys-factory-warehouse', 10.22),
        # 'creswell-crags (1)'',
        ('jack-lyons-concert-hall-university-york', 1.89),
        ('sports-centre-university-york', 6.81),
        ('terrys-typing-room', 2.98),
        ('dixon-studio-theatre-university-york', 1.09),
        ('koli-national-park-summer', 2.1),
        ('spring-lane-building-university-york', 1.38),
        ('trollers-gill', 0.47),
        ('elveden-hall-suffolk-england', 4.26),
        ('koli-national-park-winter', 1.06),
        ('stairway-university-york', 1.23),
        ('tvisongur-sound-sculpture-iceland-model', 1.93),
        ('falkland-palace-bottle-dungeon', 1.6),
        # ''koli-national-park-winter (1)'',
        ('st-andrews-church', 1.22),
        ('tyndall-bruce-monument', 1.74),
        ('falkland-palace-royal-tennis-court', 6.41),
        ('lady-chapel-st-albans-cathedral', 2.49),
        ('st-georges-episcopal-church', 2.58),
        ('usina-del-arte-symphony-hall', 2.08),
        # 'falkland-palace-royal-tennis-court (1)'',
        ('maes-howe', 0.58),
        ('st-margarets-church-national-centre-early-music', 1.49),
        # 'waveguide-web-example-audio',
        ('genesis-6-studio-live-room-drum-set', 0.21),
        ('newgrange', 0.25),
        ('st-margarets-church-ncem-5-piece-band-spatial-measurements', 1.35),
        ('york-guildhall-council-chamber', 0.93),
        ('gill-heads-mine', 0.88),
        ('r1-nuclear-reactor-hall', 5.43),
        ('st-marys-abbey-reconstruction', 13.73),
        ('york-minster', 8.4),
        # 'grad-tts',
        ('ron-cooke-hub-university-york', 1.53),
        ('st-matthews-church-walsall', 1.82)
]


df = []

wav_dir = build_dir + 'wav/'
if not os.path.exists(build_dir):
    Path(wav_dir).mkdir(parents=True, exist_ok=True)

for r, rt60 in rooms:

    orig_dir = '/data/dkounadis/cache/openAIR_impulse_responses/' +  r + '/'
    print(orig_dir)

    cont = os.listdir(orig_dir)
    if 'stereo' in cont:
        audio_format = 'stereo'
    elif 'b-format' in cont:
        audio_format = 'b-format'
    elif 'mono' in cont:
        audio_format = 'mono'

    for wav in os.listdir(orig_dir + audio_format + '/'):
        f = r.replace('-','_') + '__' + audio_format + '__' + wav
        shutil.copyfile(orig_dir + audio_format + '/' + wav, wav_dir + f)
        df.append([f, rt60])

db = audformat.Database(
    name='openair',
    author=(
        'joseph.rees-jones@york.ac.uk,'
        'damian.murphy@york.ac.uk'),
    organization=(
      'The Open AIR Library is developed and maintained by:'
       'Damian Murphy and Joe Rees-Jones'
       'Audiolab, Department of Electronics, University of York'
    ),
    license='CC-BY-4.0',
    # license_url='https://creativecommons.org/',
    source=(
        'https://www.openair.hosted.york.ac.uk/?page_id=36'
    ),
    usage='commercial',
    description=(
        'Impulse Responses (IR) '
        'and Reverberation Time (RT60) '
        'for different rooms. '
        'RT is given in seconds at 500Hz. '
        'Openair also has BRIRs and RT60s for '
        '31.25Hz, 62.5Hz, 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, 4kHz, 8kHz, 16kHz. '
        'Original IRs are either in B-format (4 channels) '
        'or in Stereo '
        'or in Mono. '
        'Sampling rates vary between 96kHz, 44.1kHz and 48kHz.'
    ),
)


db.schemes['reverberation-time'] = audformat.Scheme(
    'float',
    description='Reverberation time RT60 @ 500Hz',
)

rir_files = [f for f, rt60 in df]
rts = [rt60 for f, rt60 in df]

index = audformat.filewise_index([f'wav/{f}' for f in rir_files])
db['rir'] = audformat.Table(
    index,
    description=(
        'Impulse responses and reverberation time RT60 (in seconds) at 500Hz'
    ),
)

db['rir']['reverberation-time'] = audformat.Column(
    scheme_id='reverberation-time'
)
db['rir']['reverberation-time'].set(rts)

db.save(build_dir)
