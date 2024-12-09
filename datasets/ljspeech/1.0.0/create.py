import pandas as pd

import audeer
import audformat


build_dir = audeer.path("./build")
src_dir = audeer.path("./LJSpeech-1.1")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)


db = audformat.Database(
    "ljspeech",
    source="https://keithito.com/LJ-Speech-Dataset",
    usage="unrestricted",
    languages=["eng"],
    description=(
        "LJSpeech consists of 13,100 short audio clips "
        "of a single speaker reading passages from 7 non-fiction books. "
        "A transcription is provided for each clip. "
        "Clips vary in length from 1 to 10 seconds "
        "and have a total length of approximately 24 hours. "
        "The texts were published between 1884 and 1964, "
        "and are in the public domain. "
        "The audio was recorded in 2016-17 by the LibriVox project "
        "and is also in the public domain. "
        "The audio clips were segmented automatically "
        "based on silences in the recording. "
        "Clip boundaries generally align with sentence or clause boundaries, "
        "but not always. "
        "The text was matched to the audio manually, "
        "and a quality assurance pass was done to ensure "
        "that the text accurately matched the words spoken in the audio. "
        "The original LibriVox recordings were distributed as 128 kbps MP3 files. "
        "As a result, they may contain artifacts introduced by the MP3 encoding."
    ),
    author="Keith Ito and Linda Johnson",
    organization="",
    license="CC0-1.0",
)

db.schemes["transcription"] = audformat.Scheme(
    "str",
    description="Words spoken by the reader.",
)
db.schemes["normalized-transcription"] = audformat.Scheme(
    "str",
    description=(
        "Transcription with numbers, ordinals, and monetary units "
        "expanded into full words."
    ),
)
# Database contains a single female speaker
db.schemes["gender"] = audformat.Scheme("str", labels=["female", "male", "other"])
db["speaker"] = audformat.MiscTable(pd.Index([0], name="speaker"))
db["speaker"]["gender"] = audformat.Column(scheme_id="gender")
db["speaker"]["gender"].set(["female"])
db.schemes["speaker"] = audformat.Scheme("int", labels="speaker")

# Read existing metadata
df = pd.read_csv(
    audeer.path(src_dir, "metadata.csv"),
    delimiter="|",
    names=["file", "transcription", "normalized-transcription"],
    index_col=0,
)
df.index = "wavs/" + df.index + ".wav"

db["files"] = audformat.Table(audformat.filewise_index(df.index))
for transcription in ["transcription", "normalized-transcription"]:
    db["files"][transcription] = audformat.Column(scheme_id=transcription)
    db["files"][transcription].set(df[transcription])
db["files"]["speaker"] = audformat.Column(scheme_id="speaker")
db["files"]["speaker"].set(0)

db.save(build_dir)

audeer.move(
    audeer.path(src_dir, "wavs"),
    audeer.path(build_dir, "wavs"),
)
