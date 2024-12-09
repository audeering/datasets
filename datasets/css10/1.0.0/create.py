import os

import pandas as pd

import audeer
import audformat


build_dir = audeer.path("./build")
src_dir = audeer.path("./src")
audeer.rmdir(build_dir)
audeer.mkdir(build_dir)

num_workers = 8

languages = audeer.list_dir_names(src_dir, basenames=True)
db = audformat.Database(
    "css10",
    source="https://github.com/Kyubyong/css10",
    usage="unrestricted",
    languages=[
        lang if lang != "greek" else "Greek, Modern (1453-)"
        for lang in languages
    ],
    description=(
        "CSS10 is a collection of single speaker speech data for 10 languages. "
        "Each of them consists of audio files recorded by a single volunteer "
        "and their aligned text sourced from LibriVox. "
        "The dataset contains: "  # is extended below
    ),
    author="Kyubyong Park and Thomas Mulc",
    organization="Expedia Group, U.S.A.",
    license="CC0-1.0",
)

# Transcriptions
db.schemes["transcription"] = audformat.Scheme(
    "str",
    description="Words spoken by the reader",
)
db.schemes["normalized-transcription"] = audformat.Scheme(
    "str",
    description=(
        "Transcription with numbers, ordinals, and monetary units "
        "expanded into full words"
    ),
)
# Speaker information extracted from
# https://github.com/Kyubyong/css10/blob/master/README.md
speakers = {
    "german": "Hokuspokus",
    "greek": "Rapunzelina",
    "spanish": "Tux",
    "finnish": "Harri Tapani Ylilammi",
    "french": "Gilles G. Le Blanc",
    "hungarian": "Diana Majlinger",
    "japanese": "ekzemplaro",
    "dutch": "Bart de Leeuw",
    "russian": "Mark Chulsky",
    "chinese": "Jing Li",
}
db.schemes["language"] = audformat.Scheme("str", labels=list(speakers.keys()))
db.schemes["speaker"] = audformat.Scheme("str", labels=list(speakers.values()))

files = []
metadata = {
    "transcription": [],
    "normalized-transcription": [],
    "language": [],
    "speaker": [],
}
durations = {}
for language in languages:
    df = pd.read_csv(
        audeer.path(src_dir, language, "transcript.txt"),
        sep="|",
        names=["files", "transcription", "normalized-transcription", "duration"],
    )
    durations[language] = df.duration.sum()
    db.description += (
        f"{df.duration.sum() / 60 / 60:.0f}h for {language.capitalize()}, "
    )
    files += list(df.files)
    for transcription in ["transcription", "normalized-transcription"]:
        metadata[transcription] += list(df[transcription])
    metadata["language"] += [language] * len(df)
    metadata["speaker"] += [speakers[language]] * len(df)

    # Move audio files
    folders = audeer.list_dir_names(
        audeer.path(src_dir, language),
        basenames=True,
    )
    for folder in folders:
        audeer.move(
            audeer.path(src_dir, language, folder),
            audeer.path(build_dir, folder),
        )

# Remove last ,
db.description = db.description[:-2]
db.description += "."

db["files"] = audformat.Table(audformat.filewise_index(files))
for column in ["transcription", "normalized-transcription", "language", "speaker"]:
    db["files"][column] = audformat.Column(scheme_id=column)
    db["files"][column].set(metadata[column])

db.save(build_dir)
