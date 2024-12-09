import os
import shutil
import audeer

# define directories, etc.
destination_dir="./build/audios"
source_dirs=["~/Downloads/SUBESCO"]
source_dirs = [os.path.expanduser(source_dir) for source_dir in source_dirs]
all_audio_files = []


# filter for wav files in source directory
for source_dir in source_dirs:
    all_files = os.listdir(source_dir)
    audio_files = [file for file in all_files if file.endswith('.wav')]
    all_audio_files.extend(audio_files)

# copy-function
def copy_audio(file):
    src_file = audeer.safe_path(os.path.join(source_dir, file))
    dst_file = audeer.safe_path(os.path.join(destination_dir, file))
    audeer.mkdir(os.path.dirname(dst_file))
    shutil.copyfile(src_file, dst_file)

# call copy-function
for file in all_audio_files:
    copy_audio(file)
