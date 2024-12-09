# emodb 1.1.0

Publishes the initial public version of `emodb`
as it can be found at
http://emodb.bilderbar.info/download/download.zip

## Publish

To publish execute the following steps:

```bash
$ virtualenv --python=python3 ${HOME}/.envs/emodb
$ source ${HOME}/.envs/emodb/bin/activate
$ pip install -r requirements.txt.lock
$ python download.py
$ python create.py
$ python publish.py
```
