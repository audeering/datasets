import os
import urllib.request
import audeer
import shutil

# Get database source
source = "https://figshare.com/ndownloader/files/37361143"
src_dir = "download"
if not os.path.exists(src_dir):
    urllib.request.urlretrieve(source, "quechua.zip")
    audeer.extract_archive("quechua.zip", src_dir)

target_dir=os.path.expanduser("./build/audios")
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
audio_dir="download/Audios"
all_files=os.listdir(audio_dir)
print(target_dir)
for file in all_files:
    shutil.move(os.path.join(audio_dir,file),target_dir)
