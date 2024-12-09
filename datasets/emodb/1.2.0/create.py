import audb
import audeer
import audformat

name = 'emodb'
previous_version = '1.1.1'
build_dir = '../build'
build_dir = audeer.mkdir(build_dir)

audb.load_to(
    build_dir,
    name,
    version=previous_version,
    num_workers=8,
    cache_root=None,
    verbose=True
)
db = audformat.Database.load(build_dir)

speaker_splits = {
    audformat.define.SplitType.TRAIN: [3, 8, 9, 10, 11, 13],
    audformat.define.SplitType.TEST: [12, 14, 15, 16]
}

full_files_df = db['files'].get()
full_emotions_df = db['emotion'].get()

for split, speakers in speaker_splits.items():
    split_files_df = full_files_df[full_files_df['speaker'].isin(speakers)]
    split_index = split_files_df.index
    split_emotion_df = full_emotions_df.loc[split_index, :]

    db.splits[split] = audformat.Split(type=split,
                                       description=f'Unofficial speaker-independent {split} split')

    db[f'emotion.categories.{split}.gold_standard'] = audformat.Table(split_index, split_id=split)
    db[f'emotion.categories.{split}.gold_standard']['emotion'] = audformat.Column(scheme_id='emotion', rater_id='gold')
    db[f'emotion.categories.{split}.gold_standard']['emotion'].set(split_emotion_df['emotion'])
    db[f'emotion.categories.{split}.gold_standard']['emotion.confidence'] = audformat.Column(scheme_id='confidence',
                                                                                             rater_id='gold')
    db[f'emotion.categories.{split}.gold_standard']['emotion.confidence'].set(split_emotion_df['emotion.confidence'])

db.save(build_dir)
