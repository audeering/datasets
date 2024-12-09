import pandas as pd 
import os
import shutil
import audeer
import audformat
import audiofile


build_dir=["./build/audios"]
build_dir = [os.path.expanduser(dir) for dir in build_dir]
file_names = [os.listdir(dir) for dir in build_dir ][0]
file_names = [name for name in file_names if name.endswith("wav")]


GENDER={
    "F": "female", 
    "M": "male", 
    "C": "child",
}
WORD_CORPUS={
    "A": "corpus A", 
    "B": "corpus B"
}


# create columns for DataFrame
split_file_names=[name.split("_",maxsplit=3) for name in file_names ]

emotion=[x[0].lower() for x in split_file_names]
gender=[GENDER[x[1]] for x in split_file_names]
word_corpus=[WORD_CORPUS[x[2]] for x in split_file_names]
word=[x[3].replace(".wav","") for x in split_file_names]

df=pd.DataFrame(columns=["emotion","gender","word_corpus","word"])
df["emotion"]=emotion
df["gender"]=gender
df["word_corpus"]=word_corpus
df["word"]=word


# create database
db=audformat.Database(
    name="mesd",
    source="https://data.mendeley.com/datasets/cy34mh68j9/5",
    languages=["spanish"],
    description="MESD (Mexican Emotional Speech Database) contains single-word utterances for different emotions like anger, disgust, fear, happiness, neutral, and sadness",
    license=audformat.define.License.CC_BY_4_0,
    usage=audformat.define.Usage.COMMERCIAL,
    author="Mathilde Marie Duville, Luz María Alonso-Valerdi, David Isaac Ibarra-Zarate",
)


###########
# schemes #
###########

db.schemes['emotion'] = audformat.Scheme(labels=["anger", "disgust", "fear", "happiness", "neutral", "sadness"], dtype='str')  
db.schemes["gender"]=audformat.Scheme(labels=list(GENDER.values()), dtype='str')              
db.schemes["word_corpus"]=audformat.Scheme(
    labels=list(WORD_CORPUS.values()), dtype='str',
    description="""Corpus A: words repeated across emotional prosodies and genders; 
    Corpus B: words controlled for age-of-acquisition, frequency of use, familiarity, concreteness, valence, arousal, and discrete emotion dimensionality ratings""",
)
db.schemes["word"]=audformat.Scheme( dtype='str')


##########
# tables #
##########

# create tables
index = audformat.filewise_index([os.path.join('audios', file_name) for file_name in file_names])
db["files"]=audformat.Table(index)
db["emotion.categories.desired"]=audformat.Table(index)


# set columns
db["files"]["gender"]=audformat.Column(scheme_id="gender")
db["files"]["gender"].set(df["gender"])

db["files"]["word_corpus"]=audformat.Column(scheme_id="word_corpus")
db["files"]["word_corpus"].set(df["word_corpus"])

db["files"]["word"]=audformat.Column(scheme_id="word")
db["files"]["word"].set(df["word"])


db["emotion.categories.desired"]["emotion"]=audformat.Column(scheme_id="emotion")
db["emotion.categories.desired"]["emotion"].set(df["emotion"])

# save database
db.save("./build")

# df_tmp=pd.read_csv("./build/db.files.csv")
# print(df_tmp)