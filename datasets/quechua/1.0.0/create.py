import audformat
import audb
import pandas as pd
import numpy as np
import openpyxl as xl
import os
build_dir="./build"
labels_dir="./download/Labels/Labels/"
raters=["Rater01",  "Rater02",  "Rater03",  "Rater04"]
data_dir="./download/Data/Data/"
script_dir="./download/Script/"
MAX_STD=0.5


# region DataFrames
goldstandard_df=pd.read_csv(os.path.join(labels_dir,"Labels.csv"))
arousal_df=pd.read_csv(os.path.join(labels_dir,"Arousal.csv"))
dominance_df=pd.read_csv(os.path.join(labels_dir,"Dominance.csv"))
valence_df=pd.read_csv(os.path.join(labels_dir,"Arousal.csv"))
files_df=pd.read_excel(os.path.join(data_dir,"Data.xlsx"), sheet_name="map")
speaker_map=dict(zip(files_df["Audio"],files_df["Actor"]))

def change_columns(cur_df):
    # rename columns to fit our conventions
    # add speaker table 
    if not "Actor" in cur_df.columns:
        cur_df["speaker"]=cur_df["Audio"].apply(lambda audio: speaker_map[audio])
    cur_df=cur_df.rename(columns={
        "N1":"Rater01",
        "N2":"Rater02",
        "N3":"Rater03",
        "N4":"Rater04",
        "Arousal":"arousal",
        "Dominance":"dominance",
        "Valence":"valence",
        "Emotion":"emotion",
        "Actor": "speaker",
    })

    # create new index (& add file-extension)
    extended_filenames=cur_df["Audio"].apply(lambda file_number: str(file_number) + ".wav")
    new_index=pd.Index(extended_filenames,name="file")
    cur_df=cur_df.set_index(new_index)

    # remove file "22415.wav", since Rater03 annotated it incorrectly
    cur_df=cur_df[cur_df["Audio"]!=22415]

    # remove file "11817.wav" since it has an invalid "File" value
    cur_df=cur_df[cur_df["Audio"]!=11817]

    # remove files "14197.wav" and "20888.wav" for invalid speaker id
    cur_df=cur_df[~cur_df["Audio"].isin([14197,20888])]
    return cur_df

# scaling function
def min_max_scale(x, source_range, target_range):
    if pd.isna(x) or pd.isnull(x):
        return np.nan
    x=float(x)
    x_scaled = (x - source_range[0]) * (target_range[1] - target_range[0])
    x_scaled = x_scaled / (source_range[1] - source_range[0])
    x_scaled = target_range[0] + x_scaled
    return x_scaled

arousal_df = change_columns(arousal_df)
dominance_df = change_columns(dominance_df)
valence_df = change_columns(valence_df)
goldstandard_df=change_columns(goldstandard_df)
files_df=change_columns(files_df)

# correct mistake by original authors
goldstandard_df.at["22210.wav", "valence"]=((-22210/5) + valence_df[valence_df.index=="22210.wav"].mean(
        axis=1,
        skipna=True,
        numeric_only=True)
    ).tolist()[0]

# add gender
gender_dict={
    "a1":"female",
    "a2":"male",
    "a3":"female",
    "a4":"female",
    "a5":"male",
    "a6":"male",
}
files_df["gender"]=files_df["speaker"].apply(lambda sp: gender_dict[sp])
# change emotion labels to fit our coventions
emotion_map={
    'happy':'happiness',
    'sleepy':"sleepiness",
    'calm':'calmness',
    'excited':"exitement",
    'angry':'anger',
    'bored':'boredom',
    "anger":"anger",
    "boredom":"boredom",
    "sadness":"sadness",
    "fear":"fear",
    "neutral":"neutral",
}
files_df["emotion"]=files_df["emotion"].apply(lambda emo: emotion_map[emo])
files_df["sentence"]=files_df["File"].apply(lambda file: file[3:7])

# correct typo (mistake made by original authors)
files_df["sentence"]=files_df["sentence"].apply(lambda id: "T043" if id=="To43" else id )
# endregion dataframes

# create database
db=audformat.Database(
    "quechua",
    source="https://figshare.com/articles/media/Quechua_Collao_for_Speech_Emotion_Recognition/20292516?file=37361143",
    languages=["quechua"],
    description=(
        "quechua contains 12420 recordings of emotional speech in Quechua Collao. ",
        "Six actors were asked to read words and sentences with nine emotional categories. ",
        "Four human annotators labeled the recordings for arousal, dominance, and valence.",
    ),
    license=audformat.define.License.CC_BY_4_0,
    usage=audformat.define.Usage.COMMERCIAL,
    author="Rosa Y. G. Paccotacya-Yanque, Candy A. Huanca-Anquise, Judith Escalante-Calcina, Wilber R. Ramos-Lovon, Alvaro E. Cuno-Parari",
)

# region schemes
for dimension in ['arousal','dominance','valence']:
    db.schemes[dimension] = audformat.Scheme(
            dtype='float', minimum=0, maximum=1,
            description=f'Annotations for {dimension} (original scale: 1-5)',
        )
    db.schemes[f'{dimension}.original'] = audformat.Scheme(
            dtype='int', minimum=1, maximum=5,
            description=f'Annotations for {dimension}',
        )
    db.schemes[f'{dimension}.agreement'] = audformat.Scheme(
        dtype='float',
        description=f"Indicates how much the annotators agreed on {dimension}"
        )
db.schemes["gender"]=audformat.Scheme(
    dtype="str",
    description="gender of each speaker"
)
db.schemes['emotion'] = audformat.Scheme(
    labels=files_df["emotion"].unique().tolist(),
    dtype='str',
)
db.schemes['transcription'] = audformat.Scheme(
    dtype='str',
    description="Transcription of the sentence."
)
db.schemes['translation'] = audformat.Scheme(
    dtype='str',
    description="Spanish translation of the sentence."
)
db.schemes['is_single_word'] = audformat.Scheme(
    dtype='bool',
    description="True if the Audio contains a single word, False if it contains a whole sentence."
)
# endregion schemes

# region splits
test_speakers=["a3","a4","a5","a6"]
train_speakers=["a1","a2"]

test_df=files_df[files_df.speaker.isin(test_speakers)]
train_df=files_df[files_df.speaker.isin(train_speakers)]
train_test={
    "train":train_df,
    "test":test_df,
}
split_speakers_map={
    "train":train_speakers,
    "test":test_speakers,
}
# endregion splits

# region misc tables
speaker_dict={
    "speaker":["a1","a2","a3","a4","a5","a6"],
    "gender":["female", "male", "female", "female", "male", "male"]
}
speaker_df=pd.DataFrame(speaker_dict)
speaker_df=speaker_df.set_index("speaker")

db["speaker"] = audformat.MiscTable(speaker_df.index)
db["speaker"]["gender"]=audformat.Column(
    scheme_id="gender",
    description="The gender of the speakers was annotated by a third party.",
)
db["speaker"]["gender"].set(speaker_df["gender"])

db.schemes['speaker'] = audformat.Scheme(labels="speaker", dtype= 'object')

# MISC table for sentences
script_df=pd.DataFrame()

# get sheets
excel_file = os.path.join(script_dir,"Script.xlsx")
workbook = xl.load_workbook(excel_file)
sheets=workbook.sheetnames

for sheet in sheets:
    sheet_df=pd.read_excel(os.path.join(script_dir,"Script.xlsx"), sheet_name=sheet)
    script_df=pd.concat([script_df,sheet_df])
script_df=script_df.set_index("ID")

# filter None row  TODO: check if misc table and files table are compatible after removing this row
script_df=script_df[script_df['T'].notnull()]

# create table
db["sentence"] = audformat.MiscTable(script_df.index)

# create Columns
db["sentence"]["transcription"]=audformat.Column(
    scheme_id="transcription",
    description="Transcription of the sentence.",
)
db["sentence"]["translation.spa"]=audformat.Column(
    scheme_id="translation",
    description="Spanish translation of the sentence.",
)
db["sentence"]["is_single_word"]=audformat.Column(
    scheme_id="is_single_word",
    description="True if the Audio contains a single word, False if it contains a whole sentence.",
)
# set Columns
db["sentence"]["transcription"].set(script_df["Quechua "])
db["sentence"]["translation.spa"].set(script_df["Traducción (español)"])

db["sentence"]["is_single_word"].set(script_df["T"].apply(lambda x: x=="W"))

db.schemes['sentence'] = audformat.Scheme(labels="sentence", dtype= 'object')
# endregion misc tables

# region tables
train_test_dict={"arousal":arousal_df, "dominance":dominance_df, "valence":valence_df}
# scale goldstandard_df
for dimension in ["arousal", "dominance", "valence"]:
    goldstandard_df[dimension] = goldstandard_df[dimension].apply(min_max_scale,source_range=(1,5),target_range=(0,1))

# create & set files-Table
expanded_files=[os.path.join("audios",file) for file in files_df.index]
index=pd.Index(expanded_files,name="file")
db['files']=audformat.Table(index)
db["files"]["speaker"]=audformat.Column(scheme_id="speaker")
db["files"]["speaker"].set(files_df["speaker"])
db["files"]["sentence"]=audformat.Column(scheme_id="sentence")
db["files"]["sentence"].set(files_df.sentence)

# create & set Tables
for split in ["train","test"]:
    # create goldstandard-Table
    speakers=split_speakers_map[split]
    split_df=goldstandard_df[goldstandard_df["speaker"].isin(speakers)]
    db[f"emotion.dimensions.{split}.gold_standard"]=audformat.Table(split_df.index)

    for dimension in ["arousal", "dominance", "valence"]:
        df = train_test_dict[dimension]
        # remove "Audio" column
        df=df[["Rater01",  "Rater02",  "Rater03",  "Rater04","speaker"]]

        # set goldstandard-Columns
        db[f"emotion.dimensions.{split}.gold_standard"][dimension]=audformat.Column(scheme_id=dimension)
        db[f"emotion.dimensions.{split}.gold_standard"][dimension].set(split_df[dimension])

        # create dimension-Table
        speaker_index=df.speaker.isin(speakers)
        expanded_files=[os.path.join("audios",file) for file in df[speaker_index].index]
        index=pd.Index(expanded_files,name="file")
        db[f"{dimension}.{split}"]=audformat.Table(index)

        # create and set dimension-Columns
        for rater in raters:
            db[f"{dimension}.{split}"][rater]=audformat.Column(scheme_id=f'{dimension}.original')
            db[f"{dimension}.{split}"][rater].set(df[speaker_index][rater])

        df_copy=pd.DataFrame(index=df[df.speaker.isin(speakers)].index)
        # add agreement
        for rater in raters:
            df_copy[rater]=df[rater].apply(min_max_scale, source_range=(1,5),target_range=(0, 1)).astype(float)
        std=df_copy.std(axis=1, skipna=True, numeric_only=True, ddof=0)
        normalized_std=(std/MAX_STD).clip(upper=1).to_frame(name=dimension)
        db[f'emotion.dimensions.{split}.gold_standard'][f'{dimension}.agreement'] = audformat.Column(scheme_id=f'{dimension}.agreement')
        db[f'emotion.dimensions.{split}.gold_standard'][f'{dimension}.agreement'].set(
            normalized_std[dimension].apply(lambda x: 1 - x)
        )
# create and set Tables for categories
for split in ["train","test"]:
    speakers=split_speakers_map[split]
    emotions_df=files_df[files_df["speaker"].isin(speakers)]
    db[f"emotion.categories.{split}.desired"]=audformat.Table(emotions_df.index)
    db[f"emotion.categories.{split}.desired"]["emotion"]=audformat.Column(scheme_id="emotion")
    db[f"emotion.categories.{split}.desired"]["emotion"].set(emotions_df["emotion"])
# endregion tables
db.save(build_dir)
