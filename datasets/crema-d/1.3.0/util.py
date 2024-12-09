import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

num_workers = 8

def distribution(df, split):
    sns.histplot(
        # df[df.gender == gender]["age"].astype("float32"),
        data = df,
        x = "age",
        hue = "gender",
        common_bins=False,
        stat="frequency",
        kde=True,
        edgecolor=None,
        kde_kws={"cut": 3},  # hard code like in distplot()
    )
    plt.grid(alpha=0.4)
    sns.despine()
    plt.xlabel("age")
    plt.title(f"Frequency of samples for {split}")
    # Force y ticks at integer locations
    ax = plt.gca()
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))


def limit_speakers(df, max=20):
    """
    Limit the number of samples per speaker to max.
    """
    df_ret = pd.DataFrame()
    for s in df.speaker.unique():
        s_df = df[df["speaker"].eq(s)]
        if s_df.shape[0] < max:
            df_ret = pd.concat([df_ret, s_df])
        else:
            df_ret = pd.concat([df_ret, s_df.sample(max)])
    return df_ret
