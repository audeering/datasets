# Version 1.4.1

## Preparation

Create virtual environment and install dependencies:

```bash
$ virtualenv -p python3.8 venv
$ source venv/bin/activate
$ pip install -r requirements.txt.lock
```

If you have a different Python version,
you can try to install from `requirements.txt`.

## Publication

To publish the data run:

```bash
$ python publish.py
```
