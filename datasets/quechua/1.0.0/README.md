# 1.0.0

## Installation

Please install the requirements as follows:

```bash
$ virtualenv --python="/usr/bin/python3.10" "${HOME}/.envs/quechua"
$ source "${HOME}/.envs/quechua/bin/activate"
$ pip install -r requirements.txt.lock
```

## Usage

To publish the data run:

```bash
$ python download.py
$ python create.py
$ python publish.py
```
