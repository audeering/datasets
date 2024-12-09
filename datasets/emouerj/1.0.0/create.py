import os
import pandas as pd
import audformat

build_dir="./build/audios/emoUERJ"
file_names=os.listdir(build_dir)
split_names=[(f[0],f[0:3],f[3],int(f[4:6])) for f in file_names if f.endswith(".wav")]

gender={
    "m":"male",
    "w":"female",
}
emotion={
    "h":"happiness",
    "a":"anger",
    "s":"sadness",
    "n":"neutral",
}

# create df
df=pd.DataFrame(columns=["gender","speaker","emotion","take"]) 
df["gender"]=[x[0] for x in split_names]
df["speaker"]=[x[1] for x in split_names]
df["emotion"]=[x[2] for x in split_names]
df["take"]=[x[3] for x in split_names]

# change types/values
df["gender"]=df["gender"].apply(lambda x:gender[x])
df["emotion"]=df["emotion"].apply(lambda x: emotion[x])

speaker_to_gender=dict(zip(df["speaker"],df["gender"]))

# create Database
db=audformat.Database(
    name="emouerj",
    source="https://zenodo.org/records/5427549",
    languages=["portuguese"],
    description="emoUERJ contains recordings of 10 portuguese sentences pronounced by 8 speakers in 4 emotions: happiness,anger,sadness,neutral.",
    license=audformat.define.License.CC_BY_4_0,
    usage=audformat.define.Usage.COMMERCIAL,
    author="Rodrigo Gregory Bastos Germano, Michel Pompeu Tcheou, Felipe da Rocha Henriques, Sergio Pinto Gomes Junior",
)

# region schemes
unique_speakers=df["speaker"].unique().tolist()
unique_takes=df["take"].unique().tolist()

db.schemes['emotion'] = audformat.Scheme(labels=["happiness","anger","sadness","neutral"], dtype='str')  
db.schemes["gender"]=audformat.Scheme(labels=["male","female"], dtype='str')              
db.schemes["take"]=audformat.Scheme(labels=unique_takes, dtype='int')              
# endregion schemes

# region tables
# misc table
speaker_index=pd.Index(df["speaker"].unique(), name="speaker")      # create DataFrame for speakers
df_speaker=pd.DataFrame(
    index=speaker_index,
    columns=["gender"],
    data=df.groupby('speaker')['gender'].agg(pd.Series.mode)
)
db["speaker"] = audformat.MiscTable(speaker_index)
db["speaker"]["gender"] = audformat.Column(scheme_id="gender")
db['speaker'].set(df_speaker.to_dict(orient='list'))

# misc table as scheme
db.schemes['speaker'] = audformat.Scheme(labels="speaker", dtype= "object") # needs to be object, as strings are usually stored as object dtype by pandas

# tables
index = audformat.filewise_index([os.path.join('audios/emoUERJ', file_name) for file_name in file_names])
db["files"]=audformat.Table(index)
db["emotion.categories.desired"]=audformat.Table(index)

db["files"]["take"]=audformat.Column(scheme_id="take")
db["files"]["take"].set(df["take"])

db["files"]["speaker"]=audformat.Column(scheme_id="speaker")
db["files"]["speaker"].set(df["speaker"])

db["emotion.categories.desired"]["emotion"]=audformat.Column(scheme_id="emotion")
db["emotion.categories.desired"]["emotion"].set(df["emotion"])
# endregion tables

db.save("./build",storage_format="parquet")
