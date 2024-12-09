import os
import pandas as pd
import audformat

build_dir="./build/audios"
file_names=os.listdir(build_dir)
file_names_without_ending=[file[0:8] for file in file_names]
split_names=[f.split("-") for f in file_names_without_ending ]

speaker_gender={
    1 :"female",
    2 :"female",
    3 :"female",
    4 :"male",
    5 :"female",
    6 :"male",
    7 :"female",
    8 :"female",
    9: "female",
    10:"female",
    11:"female",
    12:"male",
    13:"male",
}
speaker_age={
    1 : 45,
    2 : 20,
    3 : 21,
    4 : 47,
    5 : 48,
    6 : 20,
    7 : 20,
    8 : 45,
    9:  21,
    10: 12,
    11: 12,
    12: 17,
    13: 26,
}
emotion={
    "01": "anger",
    "02": "sadness",
    "03": "surprise",
    "04": "happiness",
    "05": "fear",
    "06": "neutral",
}

df_index=pd.Index(file_names,name="file")
df=pd.DataFrame(columns=["speaker","emotion","sentence","age","gender"],index=df_index) 
df["speaker"]=[int(x[0] )for x in split_names]
df["emotion"]=[emotion[x[1]] for x in split_names]
df["sentence"]=[int(x[2]) for x in split_names]
df["age"]=[speaker_age[sp] for sp in df["speaker"]]
df["gender"]=[speaker_gender[sp] for sp in df["speaker"]]

# create Database
db=audformat.Database(
    name="kannada",
    source="https://zenodo.org/records/6345107/6345107.zip",
    languages=["kannada"],
    description="This database contains six different sentences, pronounced by thirteen people (four male and nine female) in six emotions (anger, sadness, surprise, happiness, fear, neutral).",
    license=audformat.define.License.CC_BY_4_0,
    usage=audformat.define.Usage.COMMERCIAL,
    author="Vishakha Agrawal",
)

###########
# schemes #
###########

# region schemes
speakers=df["speaker"].unique().tolist()
sentences=df["sentence"].unique().tolist()
ages=df["age"].unique().tolist()

# db.schemes["speaker"]=audformat.Scheme(labels=speakers,dtype="int")
db.schemes['emotion'] = audformat.Scheme(labels=["anger", "sadness", "surprise", "happiness", "fear", "neutral"], dtype='str')  
db.schemes["age"]=audformat.Scheme(labels=ages,dtype="int")
db.schemes["sentence"]=audformat.Scheme(labels=sentences,dtype="int")
db.schemes["gender"]=audformat.Scheme(labels=["male","female"],dtype="str")
# endregion schemes

##########
# splits #
##########

# region splits
test_speakers=[4,7,9,13]
train_speakers=df[~df.speaker.isin(test_speakers)]["speaker"].tolist()

test_df=df[df.speaker.isin(test_speakers)]
train_df=df[df.speaker.isin(train_speakers)]

train_test={
    "train":train_df,
    "test":test_df,
}
# endregion splits

#################
# (misc) tables #
#################

# region tables
# misc table
speaker_index=pd.Index(df["speaker"].unique(), name="speaker")      # create DataFrame for speakers
df_speaker=pd.DataFrame(
    index=speaker_index,
    columns=["gender","age"],
    data=df.groupby('speaker')[['gender','age']].agg(pd.Series.mode) # needs to be in two brackets
)
db["speaker"] = audformat.MiscTable(speaker_index)
db["speaker"]["gender"] = audformat.Column(scheme_id="gender")
db["speaker"]["age"] = audformat.Column(scheme_id="age")
db['speaker'].set(df_speaker.to_dict(orient='list'))

# misc table as scheme
db.schemes['speaker'] = audformat.Scheme(labels="speaker", dtype= "int")

# tables
index = audformat.filewise_index([os.path.join('audios', file_name) for file_name in file_names])
db["files"]=audformat.Table(index)

for column in ["speaker","sentence"]:
    db["files"][column]=audformat.Column(scheme_id=column)
    db["files"][column].set(df[column])

for split in ["train","test"]:
    this_df=train_test[split]
    this_index=pd.Index([os.path.join('audios', file_name) for file_name in this_df.index.tolist()], name="file") 
    db.splits[split] = audformat.Split(type=split)

    db[f"emotion.categories.{split}.desired"]=audformat.Table(this_index, split_id=split) 
    db[f"emotion.categories.{split}.desired"]["emotion"]=audformat.Column(scheme_id="emotion")
    db[f"emotion.categories.{split}.desired"]["emotion"].set(this_df["emotion"])
# endregion tables

db.save("./build")
