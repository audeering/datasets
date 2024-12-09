#!/bin/bash
rm -rf src/
mkdir src/

curl -L -o ./german.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/german-single-speaker-speech-dataset
curl -L -o ./greek.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/greek-single-speaker-speech-dataset
curl -L -o ./spanish.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/spanish-single-speaker-speech-dataset
curl -L -o ./finnish.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/finnish-single-speaker-speech-dataset
curl -L -o ./french.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/french-single-speaker-speech-dataset
curl -L -o ./hungarian.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/hungarian-single-speaker-speech-dataset
curl -L -o ./japanese.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/japanese-single-speaker-speech-dataset
curl -L -o ./dutch.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/dutch-single-speaker-speech-dataset
curl -L -o ./russian.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/russian-single-speaker-speech-dataset
curl -L -o ./chinese.zip https://www.kaggle.com/api/v1/datasets/download/bryanpark/chinese-single-speaker-speech-dataset

mkdir src/german/
unzip german.zip -d src/german/
mdkir src/greek/
unzip greek.zip -d src/greek/
mkdir src/spanish/
unzip spanish.zip -d src/spanish/
mkdir src/finnish/
unzip finnish.zip -d src/finnish/
mkdir src/french/
unzip french.zip -d src/french/
mkdir src/hungarian/
unzip hungarian.zip -d src/hungarian/
mkdir src/japanese/
unzip japanese.zip -d src/japanese/
mkdir src/dutch/
unzip dutch.zip -d src/dutch/
mkdir src/russian/
unzip russian.zip -d src/russian/
mkdir src/chinese/
unzip chinese.zip -d src/chinese/
