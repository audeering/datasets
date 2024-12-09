import os

import numpy as np

import audeer
import audiofile


data_dir = '../build/data'

files = audeer.list_file_names(data_dir)

# Rooms
name = 'air_binaural'
rooms = [
    'booth',
    'lecture',
    'aula_carolina',
    'meeting',
    'office',
    'stairway',
]
for room in rooms:
    files_l = [f for f in files if f'{name}_{room}_0' in f]
    files_r = [f for f in files if f'{name}_{room}_1' in f]
    for file_l, file_r in zip(files_l, files_r):
        out_file = file_l.replace(f'{name}_{room}_0', f'{name}_{room}')
        signal_l, fs_l = audiofile.read(file_l, always_2d=True)
        signal_r, fs_r = audiofile.read(file_r, always_2d=True)
        assert fs_l == fs_r
        signal = np.concatenate([signal_l, signal_r])
        os.remove(file_l)
        os.remove(file_r)
        audiofile.write(out_file, signal, fs_l)

# Phones
name = 'air_phone'
rooms = [
    'bathroom',
    'corridor',
    'kitchen',
    'lecture',
    'lecture1',
    'meeting',
    'office',
    'stairway',
    'stairway1',
    'stairway2',
]
for room in rooms:
    files_l = [
        f for f in files if f'{name}_{room}_' in f
        and f.endswith('_0.wav')
    ]
    files_r = [
        f for f in files if f'{name}_{room}_' in f
        and f.endswith('_1.wav')
    ]
    for file_l, file_r in zip(files_l, files_r):
        out_file = file_l.replace(f'_0.wav', f'.wav')
        signal_l, fs_l = audiofile.read(file_l, always_2d=True)
        signal_r, fs_r = audiofile.read(file_r, always_2d=True)
        assert fs_l == fs_r
        signal = np.concatenate([signal_l, signal_r])
        os.remove(file_l)
        os.remove(file_r)
        audiofile.write(out_file, signal, fs_l)

# Phones BT
name = 'air_phone_BT'
rooms = [
    'corridor',
    'office',
    'stairway',
]
for room in rooms:
    files_l = [
        f for f in files if f'{name}_{room}_' in f
        and f.endswith('_0.wav')
    ]
    files_r = [
        f for f in files if f'{name}_{room}_' in f
        and f.endswith('_1.wav')
    ]
    for file_l, file_r in zip(files_l, files_r):
        out_file = file_l.replace(f'_0.wav', f'.wav')
        signal_l, fs_l = audiofile.read(file_l, always_2d=True)
        signal_r, fs_r = audiofile.read(file_r, always_2d=True)
        assert fs_l == fs_r
        signal = np.concatenate([signal_l, signal_r])
        os.remove(file_l)
        os.remove(file_r)
        audiofile.write(out_file, signal, fs_l)
