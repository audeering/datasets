# Version 1.0.0

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

To publish the data
download them from
[here](https://github.com/fschmid56/cpjku_dcase23/tree/main/datasets/dirs)
to the folder `1.0.0/dirs`,
rename the files 
`B&O_BM2.wav` and `B&O_BM6.wav`
to `BandO_BM2.wav` and `BandO_BM6.wav`,
and run:

```bash
$ python convert.py
$ python publish.py
```
