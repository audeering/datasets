import os
import shutil

import pandas as pd

import audb
import audeer
import audformat
import audiofile as af


# Helpers
emotion_mapping = {
    'W': 'anger',
    'L': 'boredom',
    'E': 'disgust',
    'A': 'fear',
    'F': 'happiness',
    'T': 'sadness',
    'N': 'neutral',
}
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
scheme_mapping = {
    "emotion":"emotion",
    "emotion.confidence":"confidence",
    "emotion.naturalness":"naturalness",
    "speaker":"speaker",
    "duration":"duration",
    "transcription":"transcription",
    "gender":"gender",
    "language":"language",
}
def convert_german_float(x):
    x = float(x.replace(",", "."))
    return x/100
# Prepare functions for getting information from file names
def parse_names(names, from_i, to_i, is_number=False, mapping=None):
    for name in names:
        key = name[from_i:to_i]
        if is_number:
            key = int(key)
        yield mapping[key] if mapping else key

# Some constants

name = 'emodb'
previous_version = '1.4.1'
build_dir = './build'
build_dir = audeer.mkdir(build_dir)
folder_audio = "audio"
folder_laryngo = "laryngo"

# Preparation

# Remove the "xx" in the name from all new files
file_list = os.listdir("audio")
for folder in [folder_audio, folder_laryngo]:
    for f in file_list:
        f_new = f.replace("xx.wav", ".wav")
        os.rename(os.path.join(folder, f), os.path.join(folder, f_new))

# Parse the list with label agreements and naturalness
annotations = pd.read_csv("listener_judgements.txt", sep="\t", index_col="sample", encoding="ISO-8859-1")
# Align the index with database index
annotations = annotations.set_index(annotations.index.to_series()\
                                    .map(lambda x: "wav/"+x))
list_cols = ["recognized", "natural"]
for col in list_cols:
    annotations[col] = annotations[col].map(lambda x: convert_german_float(x))
annotations = annotations.rename(columns={"recognized":"emotion.confidence",\
                                          "natural":"emotion.naturalness"})

# Get the new files
file_list_all = os.listdir(folder_audio)

# Get the old files
db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    cache_root=None,
    verbose=True,
)
file_list_exist = db.files.values
files_exist = [f.replace("wav/", "") for f in file_list_exist]
# Which files are new?
file_list_new = list(set(file_list_all) - set(files_exist))
# Copy the new files to their folders
laryngo_dir = audeer.mkdir(os.path.join(build_dir, folder_laryngo))
for f in file_list_new:
    shutil.copyfile(os.path.join(folder_audio, f), os.path.join(build_dir, "wav", f))
print(f"copied {len(file_list_new)} new audio files to emodb.")
for f in file_list_all:
    shutil.copyfile(os.path.join(folder_laryngo, f),\
                    os.path.join(build_dir, laryngo_dir, f))
print(f"copied {len(file_list_all)} laryngogram files to emodb.")

# Collect the information
files_new = [f"wav/{f}" for f in file_list_new]
index_new = audformat.filewise_index(files_new)
names = [audeer.basename_wo_ext(f) for f in file_list_all]
emotions = list(parse_names(names, from_i=5, to_i=6, mapping=emotion_mapping))
speakers = list(parse_names(names, from_i=0, to_i=2, is_number=True))
durations = audeer.run_tasks(
    task_func=lambda x: pd.to_timedelta(
        af.duration(os.path.join(folder_audio, x)),
        unit='s',
    ),
    params=[([f], {}) for f in file_list_all],
    num_workers=12,
)
transcriptions = list(parse_names(names, from_i=2, to_i=5))
# Make a dataframe from all new information
dict_all = {"emotion":emotions, "speaker":speakers, "duration":durations,\
             "transcription":transcriptions}
df_all = pd.DataFrame(dict_all, index=names)
df_all = df_all.set_index(df_all.index.to_series().map(lambda x: f"wav/{x}.wav"))
cols = ["emotion.naturalness", "emotion.confidence"]
for col in cols:
    df_all[col] = "na"
    for ind_id, row in df_all.iterrows():
            val = annotations.loc[ind_id, col]
            df_all.loc[ind_id, col] = val
# Add a new scheme for naturalness
db.schemes['naturalness'] = audformat.Scheme(
    audformat.define.DataType.FLOAT,
    minimum=0,
    maximum=1,
    description='Naturalness of the emotional expression.',
)
# Fill tha tables
# Files table:
df_files = db["files"].get()
df_new_files = df_all[df_all.index.isin(index_new)]
df_old_files = df_all[df_all.index.isin(df_files.index)]
df_files = pd.concat([df_files, df_new_files[["duration", "speaker", "transcription"]]])
df_files.index.name = "file"
db['files'] = audformat.Table(df_files.index)
for col in ["duration", "transcription", "speaker"]:
    db['files'][col] = audformat.Column(scheme_id=scheme_mapping[col])
    db['files'][col].set(df_files[col])
# Emotions table
df_emotion = db["emotion"].get()
df_emotion = pd.concat([df_emotion, df_new_files[["emotion", "emotion.confidence"]]])
df_emotion["emotion.naturalness"] = df_all["emotion.naturalness"].values
df_emotion.index.name = "file"
db['emotion'] = audformat.Table(df_emotion.index)
for col in ["emotion", "emotion.confidence", "emotion.naturalness"]:
    db['emotion'][col] = audformat.Column(scheme_id=scheme_mapping[col])
    db['emotion'][col].set(df_emotion[col])
# Train and test splits
splits = {"train":audformat.define.SplitType.TRAIN, \
    "test":audformat.define.SplitType.TEST}
for split in splits.keys():
    df = db[f"emotion.categories.{split}.gold_standard"].get()
    df_select = df_all[df_all.index.isin(df.index)]
    db[f'emotion.categories.{split}.gold_standard']['emotion.naturalness'] = \
          audformat.Column(scheme_id='naturalness', rater_id='gold')
    db[f'emotion.categories.{split}.gold_standard']['emotion.naturalness'].set(df_select["emotion.naturalness"].values)
#  A new table for the added files
table_new_name = "emotion.categories.ambiguous"
db[table_new_name] = audformat.Table(index_new)
for col in ["emotion", "emotion.confidence", "emotion.naturalness"]:
    df_select = df_all[df_all.index.isin(index_new)]
    db[table_new_name][col] = audformat.Column(scheme_id=scheme_mapping[col])
    db[table_new_name][col].set(df_select[col])

# Now all for the laryngograms

# Files table
new_index = df_files.index.to_series().map(lambda x: x.replace("wav/", f"{folder_laryngo}/"))
df_files = df_files.set_index(new_index)
db['laryngo.files'] = audformat.Table(df_files.index)
for col in ["duration", "transcription", "speaker"]:
    db['laryngo.files'][col] = audformat.Column(scheme_id=scheme_mapping[col])
    db['laryngo.files'][col].set(df_files[col])
df_emotion = df_emotion.set_index(df_files.index)
db['laryngo.emotion'] = audformat.Table(df_emotion.index)
for col in ["emotion", "emotion.confidence", "emotion.naturalness"]:
    db['laryngo.emotion'][col] = audformat.Column(scheme_id=scheme_mapping[col])
    db['laryngo.emotion'][col].set(df_emotion[col])

# Train and test splits
for split in splits.keys():
    df = db[f"emotion.categories.{split}.gold_standard"].get()
    df = df.set_index(df.index.to_series().\
                              map(lambda x: x.replace("wav/", f"{folder_laryngo}/")))
    db[f'laryngo.emotion.categories.{split}.gold_standard'] = audformat.Table(df.index,\
        split_id = splits[split])
    for col in ["emotion", "emotion.confidence", "emotion.naturalness"]:
        db[f'laryngo.emotion.categories.{split}.gold_standard'][col] = \
            audformat.Column(scheme_id=scheme_mapping[col], rater_id='gold')
        db[f'laryngo.emotion.categories.{split}.gold_standard'][col].set(df[col].values)
    df = db[f"emotion.categories.{split}.gold_standard"].get()
    df.set_index(df.index.to_series().\
                              map(lambda x: x.replace("wav/", f"{folder_laryngo}/")))


df = db[table_new_name].get()
df = df.set_index(df.index.to_series().\
                            map(lambda x: x.replace("wav/", f"{folder_laryngo}/")))
db[f'laryngo.{table_new_name}'] = audformat.Table(df.index)
for col in ["emotion", "emotion.confidence", "emotion.naturalness"]:
    db[f'laryngo.{table_new_name}'][col] = \
        audformat.Column(scheme_id=scheme_mapping[col], rater_id='gold')
    db[f'laryngo.{table_new_name}'][col].set(df[col].values)

# Lastly, update the description
db.description = "Berlin Database of Emotional Speech."+\
    " A German database of emotional utterances spoken by actors recorded"+\
    " as a part of the DFG funded research project SE462/3-1 in 1997 and 1999."+\
    " Recordings took place in the anechoic chamber of the Technical University"+\
    " Berlin, department of Technical Acoustics. It contains about 800 utterances"+\
    " from ten different actors expressing basic six emotions and neutral."

db.save(build_dir, storage_format=audformat.define.TableStorageFormat.CSV)
db = audformat.Database.load(build_dir)
print(db)
print("Done.")
