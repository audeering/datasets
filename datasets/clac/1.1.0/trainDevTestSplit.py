# import json
import pandas as pd
import audb
from split_utils import optimize_traindevtest_split, binning


def split_df(df):
    # seed, dev and test proportion, number of different splits
    seed = 42
    dev_size = 0.2
    test_size = 0.2
    k = 30

    # targets
    age = df["age"].to_numpy()
    age = binning(age, nbins=5)

    # on which variable to split
    speaker = df["speaker"].to_numpy()

    # on which variables (targets, groupings) to stratify
    stratif_vars = {
        "age": age,
        "gender": df["gender"].to_numpy(),
    }

    # weights for all stratify_on variables and
    # and for dev and test proportion match. Give target
    # variable AGE more weight than groupings.
    weight = {"emotion": 2, "gender": 1, "size_diff": 10}

    # find optimal dev and test indices DEV_I and TEST_I in DF
    # info: dict with goodness of split information
    train_i, dev_i, test_i, info = optimize_traindevtest_split(
        X=df,
        y=age,
        split_on=speaker,
        stratify_on=stratif_vars,
        weight=weight,
        dev_size=dev_size,
        test_size=test_size,
        k=k,
        seed=seed,
    )

    print("dev split of DF:")
    print(df.iloc[dev_i])
    print("dev split of target variable:")
    print(age[dev_i])
    print("goodness of split:")
    print(info)
    return (df.iloc[train_i], df.iloc[dev_i], df.iloc[test_i])
