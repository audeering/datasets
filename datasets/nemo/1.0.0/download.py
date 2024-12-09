# https://github.com/amu-cai/nEMO/archive/refs/heads/main.zip
import os
import urllib.request
import audeer
import shutil

# Get database source
source = "https://github.com/amu-cai/nEMO/archive/refs/heads/main.zip"
src_dir = "download"
if not os.path.exists(src_dir):
    urllib.request.urlretrieve(source, "nemo.zip")
    audeer.extract_archive("nemo.zip", src_dir)

target_dir=os.path.expanduser("./build/audios")
if not os.path.exists(target_dir):
    os.makedirs(target_dir)


all_files=os.listdir("download/nEMO-main/samples")
print(target_dir)
for file in all_files:
    shutil.move(os.path.join("download/nEMO-main/samples",file),target_dir)
