# Note: the File F_02_MONIKA_S_2_SURPRISE_3].wav  breaks conventions (last value '3]' isn't numeric)
# also the sentencenumbers 'S_1', 'S_2', 'S_3', ...  will be converted into the corresponding numeric values 


import pandas as pd 
import os
import shutil
import audeer
import audformat
import audiofile


build_dir=["./build/audios"]
build_dir = [os.path.expanduser(dir) for dir in build_dir]
file_names = [os.listdir(dir) for dir in build_dir ][0]
file_names_with_extension=file_names
file_names = [name.replace(".wav","") for name in file_names if name.endswith("wav")]
print(file_names_with_extension[1])

GENDER={
    "F":"female",
    "M":"male",
}

EMOTION= {
    'ANGRY': 'anger', 
    'DISGUST': 'disgust',
    'FEAR': 'fear',
    'HAPPY': 'happiness', 
    'NEUTRAL': 'neutral', 
    'SAD': 'sadness', 
    'SURPRISE': 'surprise'
}


# create DataFrame
split_file_names=[name.split("_") for name in file_names]

gender=[GENDER[x[0]] for x in split_file_names]
speaker=[x[1] for x in split_file_names]
speaker_name=[x[2] for x in split_file_names]
#sentence_number=[f"{x[3]}_{x[4]}" for x in split_file_names]   
sentence_number=[x[4] for x in split_file_names]
emotion=[EMOTION[x[5]] for x in split_file_names]
take_number=[x[6].replace("]","") for x in split_file_names]

index = audformat.filewise_index([os.path.join('audios', file_name) for file_name in file_names_with_extension])
df=pd.DataFrame(index=index,columns=["gender","speaker","speaker_name","sentence_number","emotion","take_number"])

# set DataFrame columns
df['gender']=gender
df['speaker']=speaker
df['speaker_name']=speaker_name
df['sentence_number']=sentence_number
df['emotion']=emotion
df['take_number']=take_number


# create database
db=audformat.Database(
    name="subesco",
    source="https://zenodo.org/records/4526477",
    languages="bengali",
    description="SUBESCO is an audio-only emotional speech corpus of 7000 sentence-level utterances of the Bangla language. The corpus contains 7:40:40h of audio and was evaluated by 50 raters. The emotions are Anger, Disgust, Fear, Happiness, Neutral, Sadness and Surprise.",
    license=audformat.define.License.CC_BY_4_0,    
    usage=audformat.define.Usage.COMMERCIAL,
    author="Sadia Sultana",
)




    ###########
    # schemes #
    ###########

db.schemes["gender"]=audformat.Scheme(labels=list(GENDER.values()), dtype='str') 
db.schemes["speaker_name"]=audformat.Scheme(dtype='str')
db.schemes['sentence_number'] = audformat.Scheme(audformat.define.DataType.INTEGER)
db.schemes['emotion'] = audformat.Scheme(labels=list(EMOTION.values()), dtype='str')  
db.schemes['take_number']=audformat.Scheme(audformat.define.DataType.INTEGER)


    ##########
    # splits #
    ##########

# manually select speaker names
train_names=["BASHIR","SHUKANTO","NIPUN","FAHMEE","JOYEETA","CHAITY","SHUMANTA","BIBHAS","PRASUN","SMITA","SWARNALI","MOUNI"]
dev_names=["SIMI","ILIAS","EVAN","OISHI"]
test_names=["DURANTO","SIBLY","TITHI","MONIKA"]

# create DataFrames for each split
test_df=pd.DataFrame()
train_df=pd.DataFrame()
dev_df=pd.DataFrame()

# function sets dataframe values according to specified list of speaker names
def my_split(x_df,names):
    for name in names:
        x_df=pd.concat([x_df,df[df.speaker_name==name]])#,ignore_index=False)
    return x_df

# set Dataframe values
test_df=my_split(test_df,test_names)
train_df=my_split(train_df,train_names)
dev_df=my_split(dev_df,dev_names)


splits_dict={"test": test_df,"dev": dev_df,"train": train_df}

# creates & sets Tebles for each split type
for split in splits_dict.keys():
    this_df=splits_dict[split]

    # create splits
    db.splits[split] = audformat.Split(type=split)

    # create Table
    db[f'emotion.categories.{split}.desired'] = audformat.Table(
            index=this_df.index, 
            split_id=split, 
        )

    # create & set column
    db[f'emotion.categories.{split}.desired']["emotion"]=audformat.Column(scheme_id='emotion')
    db[f'emotion.categories.{split}.desired']["emotion"].set(this_df["emotion"])


    ###############
    # misc tables #
    ###############


speaker_index=pd.Index(df["speaker_name"].unique(), name="speaker")
df_speaker=pd.DataFrame(
    index=speaker_index,
    columns=["gender"],
    data=df.groupby('speaker_name')['gender'].agg(pd.Series.mode)
)
# print(df_speaker)

db['speaker'] = audformat.MiscTable(speaker_index)
db['speaker']['gender'] = audformat.Column(scheme_id='gender')

# misc table as scheme
db['speaker'].set(df_speaker.to_dict(orient='list'))

db.schemes['speaker'] = audformat.Scheme(labels="speaker", dtype= "object")

# set table values
# df_speaker=df[["gender","speaker_name"]]


    ##########
    # tables #
    ##########

# create tables
db["files"]=audformat.Table(index)
# db["emotion.categories.desired"]=audformat.Table(index)

# set columns 
db["files"]["speaker"]=audformat.Column(scheme_id="speaker")
db["files"]["speaker"].set(df["speaker_name"])

db["files"]["sentence_number"]=audformat.Column(scheme_id="sentence_number")
db["files"]["sentence_number"].set(df["sentence_number"])

db["files"]["take_number"]=audformat.Column(scheme_id="take_number")
db["files"]["take_number"].set(df["take_number"])

# db["emotion.categories.desired"]["emotion"]=audformat.Column(scheme_id="emotion")
# db["emotion.categories.desired"]["emotion"].set(df["emotion"])




# save db in build folder
db.save("./build")
