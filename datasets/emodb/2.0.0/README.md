# 2.0.0

This update of the [Berlin EmoDB](http://database.syntheticspeech.de/)

* adds 281 previously not contained files (where less than 80% of labelers agreed on the emotion).
* adds 816 (for every audio file) [laryngograms](https://en.wikipedia.org/wiki/Electroglottograph), in wav format with 16kHz sampling rate.
* adds a "natural" value to all samples, like the "confidence" values, as the original authors asked the labelers also "how natural does this sample sound?"


## How to replicate this update:
* get a copy of the original database (contains a folder "wav_laryng" with 817 stereo files) by mailing the original authors

* Run the following commands to prepare the data:

```bash
unzip emoDB.zip
mv emoDB/wav_laryng .
mv emoDB/listener_judgements.txt .
mkdir audio
mkdir laryngo
# Extract audio channel 1 (main audio) from each WAV file
for f in wav_laryng/*wav; do sox $f audio/`basename $f` remix 1; done
# Extract audio channel 2 (laryngograph signal) from each WAV file
for f in wav_laryng/*wav; do sox $f laryngo/`basename $f` remix 2; done
```

* Install requirements, build and publish the data:

```bash
pip install -r requirements.txt.lock
python update.py
python publish.py
```
