import pandas as pd
import audeer
import audb

name = 'cough-speech-sneeze'
previous_version = '1.0.0'
version = '2.0.0'
build_dir = '../build'
repository = audb.Repository(
    name='data-public-local',
    host='https://artifactory.audeering.com/artifactory',
    backend='artifactory',
)

build_dir = audeer.mkdir(build_dir)

db = audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
)

#loading csv file containing reevaluated labels for cough and sneeze
path_csv_reevaluation = '../20210412-102437-cough-sneeze/20210412-102437_cough-and-sneeze_annotations-cough_sneeze.csv'
df = pd.read_csv(path_csv_reevaluation)
df = df[['Media File','Answer 1','Bad File?']]

#Removing files with bad sound quality or other sounds than cough and sneeze
df = df[df['Bad File?'] == False ]  
df_cough = df[df['Answer 1'] == 'coughing']
df_sneeze = df[df['Answer 1'] == 'sneezing']

#Creating new column that matches the file name in the original csv file
df_cough['file'] = 'coughing/' + df_cough['Media File'].astype(str)
df_sneeze['file'] = 'sneezing/' + df_sneeze['Media File'].astype(str)

#loading the original csv file for the data base
df_old = pd.read_csv(build_dir +'/db.files.csv')

#seperating csv file into sub catagories
df_old_cough = df_old[df_old['category'] == 'coughing']
df_old_sneeze = df_old[df_old['category'] == 'sneezing']

#Removing cough and sneeze files with were not accepted in 2nd scoring round
for x in df_old_cough['file'].copy():
    if not df_cough['file'].str.contains(x).any():
        db.drop_files(x)
        
for x in df_old_sneeze['file'].copy():
    if not df_sneeze['file'].str.contains(x).any():
        db.drop_files(x)

db.save(build_dir)

audb.publish(
    build_dir,
    version,
    repository,
    previous_version=previous_version,
)
