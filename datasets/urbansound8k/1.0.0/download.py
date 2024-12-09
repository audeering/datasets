import shutil

import soundata

import audeer


build_root = audeer.mkdir('build')

dataset = soundata.initialize(
    'urbansound8k',
    '.',
)
dataset.download()
dataset.validate()

shutil.move(
    'audio',
    build_root,
)
