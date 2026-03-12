import filecmp
import os
import re
import shutil

import audeer
import audformat
import pandas as pd
from tqdm import tqdm

# A small number of speakers have a two-word accent label (e.g. "Australian English").
# These are hard-coded because they are the only exceptions in the dataset and no
# structural marker in the file distinguishes them from a one-word accent + region.
_TWO_WORD_ACCENTS = {"Australian English", "NewZealand English"}

# Regex to parse a flattened audio filename into its components.
# Matches filenames like "p225_001_mic1.flac" or "s5_001_mic2.flac".
_AUDIO_FILENAME_RE = re.compile(r"^([a-z][a-z0-9]*)_(\d+)_(mic[12])\.flac$")


def load_speaker_info(path: str) -> pd.DataFrame:
    """Load VCTK speaker-info.txt into a tidy DataFrame.

    The file uses irregular whitespace as delimiter. The REGION column
    may span multiple tokens (e.g., "Southern England"); an optional
    COMMENT in parentheses may appear at the end of some lines.

    Returns a DataFrame indexed by speaker id with columns:
        age, gender, accent, region, comment
    """
    rows = []
    with open(path, encoding="utf-8") as fh:
        next(fh)  # skip header line
        for raw in fh:
            line = raw.rstrip()
            if not line:
                continue
            # Detach optional parenthetical comment at line end
            m = re.search(r"\(.*\)\s*$", line)
            comment = m.group(0).strip() if m else ""
            line_clean = line[: m.start()].rstrip() if m else line
            tokens = line_clean.split()
            if len(tokens) < 3:
                continue
            # Detect two-word accent labels (e.g. "Australian English")
            if len(tokens) > 4 and f"{tokens[3]} {tokens[4]}" in _TWO_WORD_ACCENTS:
                accent = f"{tokens[3]} {tokens[4]}"
                region = " ".join(tokens[5:])
            else:
                accent = tokens[3] if len(tokens) > 3 else ""
                region = " ".join(tokens[4:]) if len(tokens) > 4 else ""
            rows.append(
                {
                    "speaker": tokens[0],
                    "age": int(tokens[1]),
                    "gender": tokens[2].lower(),
                    "accent": accent,
                    "region": region,
                    "comment": comment,
                }
            )
    return pd.DataFrame(rows).set_index("speaker")


def load_transcripts(dir_txt: str) -> dict[str, str]:
    """
    Walk all per-speaker subdirectories in 'dir_txt' and read each *.txt file
    into a dict mapping recording_id (e.g. "p225_001") to its transcript text.
    Files with no content or only whitespace are silently skipped.
    """
    transcripts: dict[str, str] = {}
    for speaker_dir in audeer.list_dir_names(dir_txt, recursive=False):
        speaker_path = os.path.join(dir_txt, speaker_dir)
        for txt_path in audeer.list_file_names(speaker_path, recursive=False):
            if not txt_path.endswith(".txt"):
                continue
            recording_id = os.path.splitext(os.path.basename(txt_path))[0]
            with open(txt_path, encoding="utf-8") as fh:
                text = fh.read().strip()
            if text:
                transcripts[recording_id] = text
    return transcripts


def build_files_dataframe(
    idx_files: pd.Index,
    dir_txt: str,
    df_speakers: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a file-level DataFrame aligned to 'idx_files'.

    For each audio file the function derives:
      - ''speaker''        speaker ID parsed from the filename
      - ''microphone''     recording microphone ("mic1" / "mic2") from filename suffix
      - ''transcription''  utterance text from the matching .txt file, or NaN if absent

    Speaker-level attributes (age, gender, language, accent, region) are joined
    from 'df_speakers'.

    Args:
        idx_files:   sorted Pandas Index of relative audio file paths.
        dir_txt:     root directory of the per-speaker transcript sub-directories.
        df_speakers: DataFrame indexed by speaker id (output of load_speaker_info).

    Returns:
        DataFrame indexed by file path with columns:
        speaker, microphone, age, gender, language, accent, region, transcription.
    """
    transcripts = load_transcripts(dir_txt)

    rows = []
    for file_path in tqdm(idx_files, desc="Building file metadata", unit="file"):
        fname = os.path.basename(file_path)
        m = _AUDIO_FILENAME_RE.match(fname)
        if m is None:
            raise ValueError(f"Unexpected filename format: {fname!r}")
        speaker, utterance_num, microphone = m.group(1), m.group(2), m.group(3)
        recording_id = f"{speaker}_{utterance_num}"
        rows.append(
            {
                "file": file_path,
                "speaker": speaker,
                "recording_id": recording_id,
                "microphone": microphone,
                "transcription": transcripts.get(recording_id),  # NaN if missing
            }
        )

    df = pd.DataFrame(rows).set_index("file")

    # Join speaker-level metadata (age, gender, language, accent, region)
    df = df.join(
        df_speakers[["age", "gender", "language", "accent", "region"]], on="speaker"
    )

    return df


def flatten_files(dir_in: str, dir_out: str) -> pd.Index:
    """
    Extract all files from the speaker-based subdirectories and put them all in
    a plain directory. Check if there are colliding file names.
    If the output directory already exists: validate that the therein
    contained, flattened-out files are matching the ones in the input directory.

    Returns a Pandas Index with the absolute file paths.
    """
    files = []
    # Collect all source files first to check for name collisions across speakers
    source_files = {}

    for speaker_dir in audeer.list_dir_names(dir_in, recursive=False):
        speaker_path = os.path.join(dir_in, speaker_dir)
        if not os.path.isdir(speaker_path):
            continue

        for file_path in audeer.list_file_names(speaker_path, recursive=False):
            file_name = os.path.basename(file_path)
            if file_name in source_files:
                raise FileExistsError(
                    f"File name collision: {file_name} found in both "
                    f"{os.path.dirname(source_files[file_name])} and {speaker_path}"
                )
            source_files[file_name] = file_path

    dir_out_populated = os.path.isdir(dir_out) and bool(
        audeer.list_file_names(dir_out, recursive=False)
    )

    if dir_out_populated:
        # Validate existing files
        for file_name, source_file in tqdm(
            source_files.items(), desc="Validating files", unit="file"
        ):
            target_file = os.path.join(dir_out, file_name)
            if not os.path.exists(target_file):
                raise FileNotFoundError(
                    f"Validation failed: {file_name} missing from {dir_out}"
                )
            if not filecmp.cmp(source_file, target_file, shallow=True):
                raise ValueError(
                    f"Validation failed: {file_name} in {dir_out} "
                    f"differs from source {source_file}"
                )
            files.append(target_file)
    else:
        audeer.mkdir(dir_out)
        for file_name, source_file in tqdm(
            source_files.items(), desc="Copying files", unit="file"
        ):
            target_file = os.path.join(dir_out, file_name)
            shutil.copy2(source_file, target_file)
            files.append(target_file)

    return pd.Index(sorted(files), name="file")


def main():
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    directory_dataset = "VCTK-Corpus-0.92"
    extracted_files = os.path.join(data_path, "extracted", directory_dataset)
    speaker_audio_dirs = os.path.join(extracted_files, "wav48_silence_trimmed")
    db_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build")
    # Audio files are copied into the build dir so audb.publish can find them
    # at paths relative to db_root (e.g. flac/p225_001_mic1.flac).
    flattened_files = os.path.join(db_root, "flac")

    audeer.mkdir(db_root)

    ### General definitions ###
    lang_en = audformat.utils.map_language("eng")
    dct_gender_map = {
        "f": audformat.define.Gender.FEMALE,
        "m": audformat.define.Gender.MALE,
    }
    description = (
        "The CSTR's VCTK Corpus (Centre for Speech Technology Voice Cloning Toolkit) "
        "includes speech data uttered by 110 English speakers with "
        "various accents. Each speaker reads out about 400 sentences, which were "
        "selected from a newspaper, the rainbow passage and an elicitation paragraph "
        "used for the speech accent archive. The newspaper texts were taken from Herald "
        "Glasgow, with permission from Herald & Times Group. Each speaker has a "
        "different set of the newspaper texts selected based a greedy algorithm that "
        "increases the contextual and phonetic coverage. The details of the text "
        "selection algorithms are described in the following paper: C. Veaux, J. "
        'Yamagishi and S. King, "The voice bank corpus: Design, collection and data '
        "analysis of a large regional accent speech database,"
        "https://doi.org/10.1109/ICSDA.2013.6709856 The rainbow passage and elicitation "
        "paragraph are the same for all speakers. The rainbow passage can be found at "
        "International Dialects of English Archive: "
        "(http://web.ku.edu/~idea/readings/rainbow.htm). The elicitation paragraph is "
        "identical to the one used for the speech accent archive "
        "(http://accent.gmu.edu). The details of the the speech accent archive can be "
        "found at http://www.ualberta.ca/~aacl2009/PDFs/WeinbergerKunath2009AACL.pdf All "
        "speech data was recorded using an identical recording setup: an omni-"
        "directional microphone (DPA 4035) and a small diaphragm condenser microphone "
        "with very wide bandwidth (Sennheiser MKH 800), 96kHz sampling frequency at 24 "
        "bits and in a hemi-anechoic chamber of the University of Edinburgh. (However, "
        "two speakers, p280 and p315 had technical issues of the audio recordings using "
        "MKH 800). All recordings were converted into 16 bits, were downsampled to 48 "
        "kHz, and were manually end-pointed. This corpus was originally aimed for HMM-"
        "based text-to-speech synthesis systems, especially for speaker-adaptive HMM-"
        "based speech synthesis that uses average voice models trained on multiple "
        "speakers and speaker adaptation technologies. This corpus is also suitable for "
        "DNN-based multi-speaker text-to-speech synthesis systems and neural waveform "
        "modeling. The dataset was was referenced in the Google DeepMind work on "
        "WaveNet: https://arxiv.org/pdf/1609.03499.pdf . Please note while text files "
        "containing transcripts of the speech are provided for 109 of the 110 "
        "recordings, in the '/txt' folder, the 'p315' text was lost due to a hard disk "
        "error."
    )
    author = "Junichi Yamagishi, Christophe Veaux, Kirsten MacDonald"
    organization = (
        "University of Edinburgh; Centre for Speech Technology Research (CSTR)"
    )

    db = audformat.Database(
        name="cstr-vctk",
        source="https://datashare.ed.ac.uk/handle/10283/2950",
        usage=audformat.define.Usage.COMMERCIAL,
        description=description,
        license=audformat.define.License.CC_BY_4_0,
        languages=[lang_en],
        license_url="https://datashare.ed.ac.uk/bitstream/handle/10283/3443/license_text.txt",
        author=author,
        organization=organization,
    )


    ### Speaker metadata ###
    labels_path = os.path.join(extracted_files, "speaker-info.txt")
    df_speakers = load_speaker_info(labels_path)
    df_speakers["gender"] = df_speakers["gender"].map(dct_gender_map)
    df_speakers["language"] = lang_en


    ### Media ###
    # Two microphones were used per speaker session:
    #   mic1 -> DPA 4035 omni-directional
    #   mic2 -> Sennheiser MKH 800 small-diaphragm condenser
    # (p280 and p315 had technical issues with MKH 800 / mic2)
    db.media["mic1"] = audformat.Media(
        format="flac",
        sampling_rate=48_000,
        channels=1,
        bit_depth=16,
        type=audformat.define.MediaType.AUDIO,
        description="DPA 4035 omni-directional microphone",
    )
    db.media["mic2"] = audformat.Media(
        format="flac",
        sampling_rate=48_000,
        channels=1,
        bit_depth=16,
        type=audformat.define.MediaType.AUDIO,
        description="Sennheiser MKH 800 small-diaphragm condenser microphone",
    )


    ### Schemes ###
    db.schemes["recording_id"] = audformat.Scheme(
        dtype=audformat.define.DataType.STRING,
        description="ID of the recording itself, since 2 microphones were used simultaneously",
    )
    db.schemes["speaker"] = audformat.Scheme(
        dtype=audformat.define.DataType.STRING,
        description="Speaker ID",
    )
    db.schemes["age"] = audformat.Scheme(
        dtype=audformat.define.DataType.INTEGER,
        description="Speaker age",
    )
    db.schemes["gender"] = audformat.Scheme("str", labels=list(dct_gender_map.values()))
    db.schemes["language"] = audformat.Scheme("str", labels=[lang_en])
    db.schemes["accent"] = audformat.Scheme(
        dtype=audformat.define.DataType.STRING,
        description="Speaker accent",
    )
    db.schemes["region"] = audformat.Scheme(
        dtype=audformat.define.DataType.STRING,
        description="Speaker region of origin",
    )
    db.schemes["transcription"] = audformat.Scheme(
        audformat.define.DataType.STRING,
        description="File-level transcriptions from the database",
    )
    db.schemes["microphone"] = audformat.Scheme(
        dtype=audformat.define.DataType.STRING,
        labels=["mic1", "mic2"],
        description=(
            "Recording microphone: "
            "mic1 = DPA 4035 (omni-directional), "
            "mic2 = Sennheiser MKH 800 (small-diaphragm condenser)"
        ),
    )


    ### Speaker misc table ###
    db["speaker"] = audformat.MiscTable(df_speakers.index)
    db["speaker"]["age"] = audformat.Column(scheme_id="age")
    db["speaker"]["gender"] = audformat.Column(scheme_id="gender")
    db["speaker"]["language"] = audformat.Column(scheme_id="language")
    db["speaker"]["accent"] = audformat.Column(scheme_id="accent")
    db["speaker"]["region"] = audformat.Column(scheme_id="region")
    db["speaker"].set(
        df_speakers[["age", "gender", "language", "accent", "region"]].to_dict(
            orient="list"
        )
    )


    ### File-wise table ###
    table_id = "files"

    # Copy all audio files into build/flac/ in a flat hierarchy.
    # Returns absolute-style paths; strip the db_root prefix so the index
    # contains paths relative to the build dir (e.g. flac/p225_001_mic1.flac).
    idx_files = flatten_files(dir_in=speaker_audio_dirs, dir_out=flattened_files)
    idx_files = pd.Index(idx_files.str.removeprefix(db_root + os.sep), name="file")

    db[table_id] = audformat.Table(index=audformat.filewise_index(idx_files.tolist()))

    # Build the file-wise metadata DataFrame (speaker attributes + transcripts)
    dir_txt = os.path.join(extracted_files, "txt")
    df_files = build_files_dataframe(
        idx_files=idx_files,
        dir_txt=dir_txt,
        df_speakers=df_speakers,
    )

    # Assign the column schemes to the file-wise table
    db[table_id]["recording_id"] = audformat.Column(scheme_id="recording_id")
    db[table_id]["recording_id"].set(df_files["recording_id"])

    db[table_id]["speaker"] = audformat.Column(scheme_id="speaker")
    db[table_id]["speaker"].set(df_files["speaker"])

    db[table_id]["age"] = audformat.Column(scheme_id="age")
    db[table_id]["age"].set(df_files["age"])

    db[table_id]["gender"] = audformat.Column(scheme_id="gender")
    db[table_id]["gender"].set(df_files["gender"])

    db[table_id]["language"] = audformat.Column(scheme_id="language")
    db[table_id]["language"].set(df_files["language"])

    db[table_id]["accent"] = audformat.Column(scheme_id="accent")
    db[table_id]["accent"].set(df_files["accent"])

    db[table_id]["region"] = audformat.Column(scheme_id="region")
    db[table_id]["region"].set(df_files["region"])

    db[table_id]["transcription"] = audformat.Column(scheme_id="transcription")
    db[table_id]["transcription"].set(df_files["transcription"])

    db[table_id]["microphone"] = audformat.Column(scheme_id="microphone")
    db[table_id]["microphone"].set(df_files["microphone"])

    db.save(db_root)


if __name__ == "__main__":
    main()
