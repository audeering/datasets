"""
Add age.[train|dev|test] tables with speaker information
consists of randomly selected 20 emotionally neutral samples per speaker
all tables being age/gender balanced
"""

import random
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import audb
import audeer
import audformat
import util
import trainDevTestSplit

# make it reproducible
random.seed(23)

image_dir = "images/"


def main():
    name = "crema-d"
    previous_version = "1.2.0"

    build_dir = "./build"
    build_dir = audeer.mkdir(build_dir)

    audb.load_to(
        build_dir,
        name,
        version=previous_version,
        num_workers=8,
        only_metadata=True,
        verbose=True,
    )
    db = audformat.Database.load(build_dir)

    # get age, gender and emotion info
    df = db["files"].get()
    df_emo = pd.concat(
        [
            db["emotion.categories.train"].get(),
            db["emotion.categories.dev"].get(),
            db["emotion.categories.test"].get(),
        ]
    )
    df["age"] = db["files"]["speaker"].get(map="age").astype("int")
    df["gender"] = db["files"]["speaker"].get(map="sex")
    #    df["duration"] = df.index.to_series().map(lambda x: audiofile.duration(x))
    df = df[df["gender"] != "other"]
    df = df[df["corrupted"] != True]
    # make a dataframe for 20 samples per speaker
    df_lim = util.limit_speakers(df)
    # make a dataframe for emotionally neutral samples
    df["emotion"] = df_emo["emotion.0"].values
    df_neut = df[df.emotion.isin(["neutral"])]
    # make a dataframe for emotionally neutral samples , limited to 20 samples
    df_neut_lim = util.limit_speakers(df_neut)

    # create split sets for samples from all emotions
    splits_emo = {}
    df_train, df_dev, df_test = trainDevTestSplit.split_df(df_lim)
    splits_emo["train"] = df_train
    splits_emo["dev"] = df_dev
    splits_emo["test"] = df_test
    # create split sets for neutral samples
    splits_neut = {}
    df_train, df_dev, df_test = trainDevTestSplit.split_df(df_neut_lim)
    splits_neut["train"] = df_train
    splits_neut["dev"] = df_dev
    splits_neut["test"] = df_test

    # fill the database with new tables
    age_tables_name = "age."
    age_tables_emotional_name = "age.emotional."
    for split in splits_emo.keys():
        db[f"{age_tables_name}{split}"] = audformat.Table(
            splits_neut[split].index,
            description=f"Table selected for age and binary gender balance from the emotionally neutral samples,  limited to 20 samples per speaker.",
        )
        for field in ["speaker"]:
            db[f"{age_tables_name}{split}"][field] = audformat.Column(scheme_id=field)
            db[f"{age_tables_name}{split}"][field].set(splits_neut[split][field])
        db[f"{age_tables_emotional_name}{split}"] = audformat.Table(
            splits_emo[split].index,
            description=f"Table selected for age and binary gender balance from all samples, limited to 20 samples per speaker.",
        )
        for field in ["speaker"]:
            db[f"{age_tables_emotional_name}{split}"][field] = audformat.Column(scheme_id=field)
            db[f"{age_tables_emotional_name}{split}"][field].set(splits_emo[split][field])

    db.save(build_dir)
    print(db)



    print("testing:")
    res_dir = audeer.mkdir("results")
    for split in splits_neut.keys():
        df = db[f"{age_tables_name}{split}"].get()
        df["gender"] = db["files"]["speaker"].get(map="sex")
        df["age"] = db["files"]["speaker"].get(map="age").astype("int")
        sn = df["speaker"].nunique()
        print(f"new {split}: {df.shape[0]}, {sn}")

        util.distribution(df, split)
        plt.tight_layout()
        plt.savefig(f"{res_dir}/{split}.png")
        plt.close()

if __name__ == "__main__":
    main()
