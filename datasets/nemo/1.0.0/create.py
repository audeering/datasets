import pandas as pd
import audformat
import os


build_dir="./build/audios"
file_names=os.listdir(build_dir)
filenames_without_extension=[file.replace(".wav","") for file in file_names]
split_names=[file.split("_") for file in filenames_without_extension]

def get_sentence(file):
    file_without_extension=file[:len(file)-4]
    sentence_number=file_without_extension.split("_")[-1]
    sentence_number=int(sentence_number)
    return sentence_number

# create DataFrame
df=pd.read_csv('./download/nEMO-main/data.tsv',sep = '\t') 
df.rename(columns={'file_id': 'file', "speaker_id":"speaker"}, inplace=True)
df["sentence"]=df["file"].apply(get_sentence)
df["emotion"]=df["emotion"].apply(lambda x: "surprise" if x=="surprised" else x)
df["speaker"]=df.speaker.apply(lambda speaker: speaker.strip())
df.set_index("file",inplace=True)


# create Database
db=audformat.Database(
    name="nemo",
    source="https://aclanthology.org/2024.lrec-main.1059",
    languages=["pol"],
    description=
    """nEMO is a polish dataset with emotional speech. It contains over 3 hours of 
    emotional speech in 6 categories: anger, fear, happiness, sadness, surprise 
    and neutral. The audios were created by nine speakers""",
    license=audformat.define.License.CC_BY_NC_SA_4_0,
    usage=audformat.define.Usage.RESEARCH,
    author="Christop, Iwona",
)


###########
# schemes #
###########

# region schemes
raw_text=df.raw_text.unique().tolist()
normalized_text=df.normalized_text.unique().tolist()

db.schemes["age"] = audformat.Scheme(audformat.define.DataType.INTEGER)
db.schemes["emotion"] = audformat.Scheme(labels=["anger", "sadness", "surprise", "happiness", "fear", "neutral"], dtype='str')  
db.schemes["raw_text"]=audformat.Scheme(labels=raw_text,dtype="str")
db.schemes["normalized_text"]=audformat.Scheme(labels=normalized_text,dtype="str")
db.schemes["gender"]=audformat.Scheme(labels=["male","female"],dtype="str")
# endregion schemes


#################
#  misc tables  #
#################

# region tables
# speaker table
speaker_index=pd.Index(df["speaker"].unique(), name="speaker")     
df_speaker=pd.DataFrame(
    index=speaker_index,
    columns=["gender", "age"],
    data=df.groupby('speaker')[['gender', "age"]].agg(pd.Series.mode) 
)
db["speaker"] = audformat.MiscTable(speaker_index)
db["speaker"]["gender"] = audformat.Column(scheme_id="gender")
db["speaker"]["age"]= audformat.Column(scheme_id="age")
db['speaker'].set(df_speaker.to_dict(orient='list'))

# sentence table
sentence_index=pd.Index(df["sentence"].unique(), name="sentence")     
df_sentence=pd.DataFrame(
    index=sentence_index,
    columns=["raw_text","normalized_text"],
    data=df.groupby('sentence')[["raw_text","normalized_text"]].agg(pd.Series.mode) 
)
db["sentence"] = audformat.MiscTable(sentence_index)
db["sentence"]["raw_text"] = audformat.Column(scheme_id="raw_text")
db["sentence"]["normalized_text"] = audformat.Column(scheme_id="normalized_text")
db['sentence'].set(df_sentence.to_dict(orient='list'))

# misc tables as scheme
db.schemes['speaker'] = audformat.Scheme(labels="speaker", dtype= "object") # pandas interprets strings as object => (dtype="object")
db.schemes['sentence'] = audformat.Scheme(labels="sentence", dtype= "int") 

##########
# tables #
##########

# files Table
index=audformat.filewise_index([os.path.join('audios', file_name) for file_name in df.index])
db["files"]=audformat.Table(index)
for column in ["speaker","sentence"]:
    db["files"][column]=audformat.Column(scheme_id=column)
    db["files"][column].set(df[column])

# emotion table
db["emotion.categories.test.gold_standard"]=audformat.Table(index)
db["emotion.categories.test.gold_standard"]["emotion"]=audformat.Column(scheme_id="emotion")
db["emotion.categories.test.gold_standard"]["emotion"].set(df["emotion"])
# endregion tables

db.save("./build")
