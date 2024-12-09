import json

import audb
import audeer
import audformat

name = 'crema-d'
previous_version = '1.0.5'

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

with open('speaker_splits.json', 'r') as fp:
    speaker_splits = json.load(fp)

split_mapping = {
    'train': audformat.define.SplitType.TRAIN,
    'dev': audformat.define.SplitType.DEVELOP,
    'test': audformat.define.SplitType.TEST
}

full_speaker_df = db['speaker'].get()

full_desired_emotions_df = db['emotion'].get()
full_voice_emotions_df = db['emotion.voice'].get()
full_face_emotions_df = db['emotion.face'].get()
full_multi_emotions_df = db['emotion.multimodal'].get()

rated_emotion_tables = {
    'voice': full_voice_emotions_df,
    'face': full_face_emotions_df,
    'multimodal': full_multi_emotions_df
}
for split, speakers in speaker_splits.items():
    split_speaker_df = full_speaker_df[full_speaker_df['speaker'].isin(speakers)]
    split_index = split_speaker_df.index

    db.splits[split] = audformat.Split(type=split_mapping[split],
                                       description=f'Unofficial speaker-independent {split} split')

    split_desired_emotion_df = full_desired_emotions_df.loc[split_index, :]
    db[f'emotion.desired.{split}'] = audformat.Table(split_index, split_id=split,
                                                     description=f'Emotion the actors were asked to present, {split} split')
    db[f'emotion.desired.{split}']['emotion'] = audformat.Column(scheme_id='emotion', description='Desired emotion')
    db[f'emotion.desired.{split}']['emotion'].set(split_desired_emotion_df['emotion'])
    db[f'emotion.desired.{split}']['emotion.intensity'] = audformat.Column(scheme_id='emotion.intensity',
                                                                           description='Desired intensity of emotion')
    db[f'emotion.desired.{split}']['emotion.intensity'].set(split_desired_emotion_df['emotion.intensity'])

    for rating_type, full_rated_emotion_df in rated_emotion_tables.items():
        split_rated_emotion_df = full_rated_emotion_df.loc[split_index, :]
        db[f'emotion.{rating_type}.{split}'] = audformat.Table(split_index, split_id=split,
                                                               description=f'Perceived emotion when taking into'
                                                                           f' account the {rating_type} modality, {split} split')
        db[f'emotion.{rating_type}.{split}']['emotion'] = audformat.Column(scheme_id='emotion',
                                                                           description='Primary perceived emotion')
        db[f'emotion.{rating_type}.{split}']['emotion'].set(split_rated_emotion_df['emotion'])
        db[f'emotion.{rating_type}.{split}']['emotion.level'] = audformat.Column(scheme_id='emotion.value',
                                                                                 description='Primary perceived emotion level')
        db[f'emotion.{rating_type}.{split}']['emotion.level'].set(split_rated_emotion_df['emotion.level'])
        db[f'emotion.{rating_type}.{split}']['emotion.agreement'] = audformat.Column(scheme_id='emotion.agreement',
                                                                                     description='Annotator agreement')
        db[f'emotion.{rating_type}.{split}']['emotion.agreement'].set(split_rated_emotion_df['emotion.agreement'])

        # add additional emotions and levels
        for i in range(1, 5):
            # multimodal only has additional emotions 1-3, whereas face and voice have 1-4
            if rating_type == 'multimodal' and i == 4:
                break
            db[f'emotion.{rating_type}.{split}'][f'emotion.{i}'] = audformat.Column(scheme_id='emotion',
                                                                                    description=f'Secondary emotion (order: {i})')
            db[f'emotion.{rating_type}.{split}'][f'emotion.{i}'].set(split_rated_emotion_df[f'emotion.{i}'])
            db[f'emotion.{rating_type}.{split}'][f'emotion.{i}.level'] = audformat.Column(scheme_id='emotion.value',
                                                                                          description=f'Secondary emotion (order: {i}) level')
            db[f'emotion.{rating_type}.{split}'][f'emotion.{i}.level'].set(split_rated_emotion_df[f'emotion.{i}.level'])

db.drop_tables(['emotion', 'emotion.voice', 'emotion.face', 'emotion.multimodal'])

db.save(build_dir)
