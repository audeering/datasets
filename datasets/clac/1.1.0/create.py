"""
Make a new version of Clac database with:
* segmented index
* age and gender tables
* with test, train and dev splits
* i.e. age.[test|train|fev]
* balanced for gender 
* max 20 samples per speaker
"""
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import audb
import audeer
import audformat
import random
import util as util
import trainDevTestSplit as split

# make it reproducible
random.seed(23)

build_dir = audeer.mkdir("./build")
db = audb.load_to(
    build_dir,
    "clac",
    version="1.0.1",
    verbose=True,
)

# get a dataframe with age and gender
df = db["files"].get()

# get age and gender info
df["age"] = db["files"]["speaker"].get(map="age").astype("int")
df["gender"] = db["files"]["speaker"].get(map="gender")
all_gender = df.shape[0]
# remove unknown gender samples
df = df[df["gender"] != "other"]
print(f"original data: samples without unkown gender: {df.shape[0]} (was {all_gender})")

# limit to only the grandfather samples
df = df[df["task-name"] == "grandfather"]

# segment the data
savename = "df_seg.csv"
if os.path.isfile(savename):
    df_seg = audformat.utils.read_csv(savename)
else:
    df_seg = util.segment_dataframe(df, build_dir)
    df_seg.to_csv(savename)


# limit to 20 samples per speaker
savename = "df_seg_lim.csv"
if os.path.isfile(savename):
    df_seg_lim = audformat.utils.read_csv(savename)
else:
    df_seg_lim = util.limit_speakers(df_seg)
    df_seg_lim.to_csv(savename)

# create split sets
splits = {}
df_all = df_seg_lim
df_train, df_dev, df_test = split.split_df(df_all)
splits["train"] = df_train
splits["dev"] = df_dev
splits["test"] = df_test


# fill the database with new tables
age_tables_name = "age."
for split in splits.keys():
    db[f"{age_tables_name}{split}"] = audformat.Table(
        splits[split].index,
        description=f"Table selected for age and binary gender balance from the 'grandfather' task, max 20 samples per speaker.",
    )
    for field in ["speaker"]:
        db[f"{age_tables_name}{split}"][field] = audformat.Column(scheme_id=field)
        db[f"{age_tables_name}{split}"][field].set(splits[split][field])

db.save(build_dir)


def distribution(df, gender, split):
    sns.histplot(
        df[df.gender == gender]["age"].astype("float32"),
        common_bins=False,
        stat="frequency",
        kde=True,
        edgecolor=None,
        kde_kws={"cut": 3},  # hard code like in distplot()
    )
    plt.grid(alpha=0.4)
    sns.despine()
    plt.xlabel("age")
    plt.title(gender)
    # Force y ticks at integer locations
    ax = plt.gca()
    ax = plt.gca()
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))


print("testing:")
for split in splits.keys():
    df = db[f"{age_tables_name}{split}"].get()
    df = df.join(db["speaker-metadata"].get(), on="speaker")
    sn = df["speaker"].nunique()
    print(f"new {split}: {df.shape[0]}, {sn}")

    for gender in ["female", "male"]:
        distribution(df, gender, split)
        plt.tight_layout()
        plt.savefig(f"age-{split}-{gender}.png")
        plt.close()

print(db)
