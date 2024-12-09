# Speech Accent Archive 2.0.0

## Preparation

Create and activate Python virtual environment:

```bash
$ virtualenv --python=python3 ${HOME}/.envs/speech-accent-archive
$ source ${HOME}/.envs/speech-accent-archive/bin/activate
```

## Download

Create a Kaggle account and download the data
from https://www.kaggle.com/rtatman/speech-accent-archive
into a ``raw`` folder.

## Conversion to audformat

```bash
$ python create.py
```

## Publish

```bash
$ python publish.py
```
