import os

import pandas as pd

import audb
import audeer
import audformat


def main():
    name = 'crema-d'
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

    splits = ['train', 'dev', 'test']
    modalities = ['voice', 'face', 'multimodal', 'desired']
    emotion_label_mapping = {
        'A': 'anger',
        'D': 'disgust',
        'F': 'fear',
        'H': 'happiness',
        'N': 'neutral',
        'S': 'sadness'
    }
    emotion_labels = list(emotion_label_mapping.values())

    # Problematic samples to be removed from main tables
    # Sample has no audio
    problem_samples = ['1076/1076_MTI_SAD_XX.wav']

    # Rename speaker table to files table like on other tables
    # and add corrupted column
    files_df = db['speaker'].get()
    files_df['corrupted'] = files_df.index.isin(problem_samples)
    db.schemes['corrupted'] = audformat.Scheme(
        dtype=bool, description='Whether the audio file is corrupted'
    )
    db['files'] = audformat.Table(
        index=files_df.index
    )
    db['files']['speaker'] = audformat.Column(
        scheme_id='speaker'
    )
    db['files']['speaker'].set(
        files_df['speaker']
    )
    db['files']['corrupted'] = audformat.Column(
        scheme_id='corrupted'
    )
    db['files']['corrupted'].set(
        files_df['corrupted']
    )
    db.drop_tables(['speaker'])

    # New scheme for rater votes
    db.schemes['votes'] = audformat.Scheme(
        dtype=int, minimum=0, description='Number of times a rater voted for a label'
    )

    # Adjust scheme for emotion to include "no_agreement"
    db.schemes['emotion'] = audformat.Scheme(
        labels=sorted(emotion_labels + ['no_agreement'])
    )

    # Rename scheme for emotion.value to emotion.level to match column name
    db.schemes['emotion.level'] = audformat.Scheme(
        dtype=float, minimum=0, maximum=100, description='Level of emotional expression. A high value corresponds to a '
                                                         'strong emotional expression for the associated '
                                                         'emotion label.'
    )
    del db.schemes['emotion.value']

    current_dir = os.path.dirname(__file__)
    rater_votes_path = os.path.join(current_dir, 'tabulatedVotes.csv')
    votes_df = pd.read_csv(rater_votes_path)
    votes_df['file'] = votes_df['fileName'].apply(lambda x: os.path.join(x.split('_')[0], f'{x}.wav'))
    # Modality of the votes table is indicated by the first number of the first column
    modality_dict = {'1': 'voice', '2': 'face', '3': 'multimodal'}
    votes_df['modality'] = votes_df['Unnamed: 0'].apply(lambda x: modality_dict[str(x)[0]])
    votes_df.set_index('file', inplace=True)
    for split in splits:
        for modality in modalities:
            table = f'emotion.{modality}.{split}'
            # Treat the voice modality as the default
            if modality == 'voice':
                new_table_name = f'emotion.categories.{split}'
            else:
                new_table_name = f'emotion.categories.{modality}.{split}'
            modality_df = db[table].get()

            emotion_df = modality_df[~modality_df.index.isin(problem_samples)]
            problem_samples_df = modality_df[modality_df.index.isin(problem_samples)]

            problem_sample_post_fix = 'Samples with audio issues were removed from this table.'

            # For the 'desired' modality there is only one table per split:
            if modality == 'desired':
                if len(problem_samples_df) > 0:
                    # Remove problematic samples if existent
                    old_description = db[table].description
                    db[table].description = f'{old_description} {problem_sample_post_fix}'
                    db[table].drop_files(problem_samples, inplace=True)
                # Rename table
                db[new_table_name] = db[table]
                db.drop_tables(table)
            # For the other modalities, handle votes, winning emotion, and gold standard tables
            else:
                # Descriptions for tables
                votes_description = f'Rater votes for the {modality} modality.'
                emotion_table_description = (
                    'The emotions that were chosen the most often for '
                    f'the {modality} modality, {split} split.'
                )
                gold_standard_description = (
                    'Gold standard for emotion '
                    f'for the {modality} modality, {split} split.')
                # Add to description that we filter out problem samples
                if len(problem_samples_df) > 0:
                    votes_description = f'{votes_description} {problem_sample_post_fix}'
                    emotion_table_description = f'{emotion_table_description} {problem_sample_post_fix}'
                    gold_standard_description = f'{gold_standard_description} {problem_sample_post_fix}'

                db[f'{new_table_name}.votes'] = audformat.Table(
                    emotion_df.index, split_id=split,
                    description=votes_description
                )
                for raw_col, class_label in emotion_label_mapping.items():
                    votes = votes_df.loc[emotion_df.index]
                    votes = votes[votes['modality']==modality]
                    db[f'{new_table_name}.votes'][class_label] = audformat.Column(
                        scheme_id='votes'
                    )
                    db[f'{new_table_name}.votes'][class_label].set(
                        votes[raw_col]
                    )

                # Rename columns to make it clear each emotion was chosen equally often
                db[new_table_name] = audformat.Table(
                    index=emotion_df.index, split_id=split,
                    description=emotion_table_description
                )
                for i in range(5):
                    emo_col = 'emotion'
                    if i > 0:
                        emo_col = f'emotion.{i}'

                    # Only add column if it exists in previous version
                    if emo_col not in emotion_df.columns:
                        break
                    db[new_table_name][f'emotion.{i}'] = audformat.Column(
                        scheme_id='emotion'
                    )
                    db[new_table_name][f'emotion.{i}'].set(
                        emotion_df[emo_col]
                    )
                    db[new_table_name][f'emotion.{i}.level'] = audformat.Column(
                        scheme_id='emotion.level'
                    )
                    db[new_table_name][f'emotion.{i}.level'].set(
                        emotion_df[f'{emo_col}.level']
                    )
                # Remove table with old name
                db.drop_tables(table)

                # Add gold standard tables
                # Set gold standard to no agreement if there is more than one emotion with
                # the most number of votes
                gold_standard = emotion_df['emotion'].astype('str')
                gold_standard.loc[~emotion_df['emotion.1'].isna()] = 'no_agreement'
                gold_standard_level = emotion_df.loc[gold_standard.index, 'emotion.level']
                # Set level to None when there is no agreement
                gold_standard_level.loc[gold_standard=='no_agreement'] = None
                gold_standard_agreement = emotion_df.loc[gold_standard.index, 'emotion.agreement']
                db[f'{new_table_name}.gold_standard'] = audformat.Table(
                    gold_standard.index, split_id=split,
                    description=gold_standard_description
                )
                db[f'{new_table_name}.gold_standard']['emotion'] = audformat.Column(
                    scheme_id='emotion', description='Emotion category that was voted for most often, or no_agreement '
                                                     'if there was more than one winning category.'
                )
                db[f'{new_table_name}.gold_standard']['emotion'].set(
                    gold_standard
                )
                db[f'{new_table_name}.gold_standard']['emotion.level'] = audformat.Column(
                    scheme_id='emotion.level', description='Gold standard of the emotion level '
                                                           'for the winning emotion, '
                                                           'or None if there was more than one winning category.'
                )
                db[f'{new_table_name}.gold_standard']['emotion.level'].set(
                    gold_standard_level
                )
                db[f'{new_table_name}.gold_standard']['emotion.agreement'] = audformat.Column(
                    scheme_id='emotion.agreement', description='Rater agreement of the emotion for the winning emotion.'
                )
                db[f'{new_table_name}.gold_standard']['emotion.agreement'].set(
                    gold_standard_agreement
                )

    db.save(build_dir)


if __name__ == '__main__':
    main()
