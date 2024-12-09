import audb
import audeer
import audformat

name = 'ravdess'
previous_version = '1.0.1'
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

split_mapping = {
    'train': audformat.define.SplitType.TRAIN,
    'dev': audformat.define.SplitType.DEVELOP,
    'test': audformat.define.SplitType.TEST
}

# For a gender balanced split close to 60%-20%-20%: train - 16, dev - 4 , test - 4
speaker_splits = {
    'train': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '18'],
    'dev': ['16', '17', '19', '20'],
    'test': ['21', '22', '23', '24']
}

full_files_df = db['files'].get()
full_emotions_df = db['emotion'].get()

for split, speakers in speaker_splits.items():

    db.splits[split] = audformat.Split(type=split_mapping[split],
                                       description=f'Unofficial speaker-independent {split} split')
    for vocal_channel in ['speech', 'song']:
        split_files_df = full_files_df[full_files_df['speaker'].isin(speakers)]
        split_files_df = split_files_df[split_files_df['vocal channel'] == vocal_channel]
        split_index = split_files_df.index

        split_emotion_df = full_emotions_df.loc[split_index, :]

        db[f'emotion.{vocal_channel}.{split}'] = audformat.Table(split_index, split_id=split)
        db[f'emotion.{vocal_channel}.{split}']['emotion'] = audformat.Column(scheme_id='emotion')
        db[f'emotion.{vocal_channel}.{split}']['emotion'].set(split_emotion_df['emotion'])
        db[f'emotion.{vocal_channel}.{split}']['emotional intensity'] = audformat.Column(
            scheme_id='emotional intensity')
        db[f'emotion.{vocal_channel}.{split}']['emotional intensity'].set(split_emotion_df['emotional intensity'])

db.drop_tables('emotion')


db.save(build_dir)
