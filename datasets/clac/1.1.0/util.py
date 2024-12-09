import auvad
import pandas as pd
import audformat
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

num_workers = 8


# plot sex distribution, age and duration
def describe_df(df):
    title = f"# samples: {df.shape[0]}, # speakers: {df.speaker.nunique()}"
    fig, axes = plt.subplots(nrows=2, ncols=2)
    df["age"].plot(kind="hist", ax=axes[0, 0], title="age")
    df["duration"].plot(kind="hist", ax=axes[0, 1], title="duration")
    df.groupby("gender")["speaker"].nunique().plot(kind="pie", ax=axes[1, 0])
    df_speakers = pd.DataFrame()
    pd.options.mode.chained_assignment = None  # default='warn'
    for s in df.speaker.unique():
        df_speaker = df[df.speaker == s]
        df_speaker["samplenum"] = df_speaker.shape[0]
        df_speakers = pd.concat([df_speakers, df_speaker.head(1)])
    df_speakers["samplenum"].value_counts().sort_index().plot(
        kind="bar",
        stacked=True,
        title=f"samples ({df.shape[0]}) per speaker ({df_speakers.shape[0]})",
        rot=0,
        ax=axes[1, 1],
    )
    fig.suptitle(title)
    plt.tight_layout()


def segment_dataframe(df, root):
    vad = auvad.Vad(num_workers=num_workers)
    dfs = []
    for file, values in tqdm(df.iterrows()):
        index = vad.process_file(file, root=root)
        dfs.append(
            pd.DataFrame(
                values.to_dict(),
                index,
            )
        )
    return audformat.utils.concat(dfs)


def segment_dataframe_segmented(df):
    vad = auvad.Vad(num_workers=num_workers)
    dfs = []
    for (file, start, end), values in tqdm(df.iterrows()):
        index = vad.process_file(file)
        dfs.append(
            pd.DataFrame(
                values.to_dict(),
                index,
            )
        )
    return audformat.utils.concat(dfs)


# df_age_all.speaker_age.plot(kind='hist')
def plot_twoagedists(df1, df2, labels):
    bins = np.linspace(0, 100, 20)
    plt.hist([df1.age.values, df2.age.values], bins, label=labels)
    plt.legend(loc="upper right")
    plt.savefig("age_dist.eps")


# plot_twoagedists(df_age_test, df_age_train, ['test', 'train'])
def plot_twodurationdists(df1, df2, labels, max):
    bins = np.linspace(0, max, 200)
    plt.hist([df1.duration_s.values, df2.duration_s.values], bins, label=labels)
    plt.legend(loc="upper right")
    plt.savefig("duration_dist.eps")


# plot_twodurationdists(df_test, df_train, ['test', 'train'], 50)
def plot_twosamplefreqs(df1, df2, labels, limit):
    test = df1.speaker.value_counts()[df1.speaker.value_counts() > 0]
    train = df2.speaker.value_counts()[df2.speaker.value_counts() > 0]
    plt.hist([train, test], bins=np.linspace(0, limit, 100), label=labels)
    plt.legend(loc="upper right")
    plt.savefig("sample_dist.png")


def limit_speakers(df, max=20):
    """
    Limit the number of samples per speaker to max.
    """
    df_ret = pd.DataFrame()
    for s in tqdm(df.speaker.unique()):
        s_df = df[df["speaker"].eq(s)]
        if s_df.shape[0] < max:
            df_ret = pd.concat([df_ret, s_df])
        else:
            df_ret = pd.concat([df_ret, s_df.sample(max)])
    return df_ret


def plot_bar_speakers_1(df1, labels):
    """ "
    Plot speaker and sample stats
    df needs to have speaker column
    """
    sn1 = df1.speaker.nunique()
    smp1 = df1.shape[0]
    vals_spk = [sn1]
    vals_smpl = [smp1]
    cols = labels
    plot = pd.DataFrame(columns=cols)
    plot.loc["speakers"] = vals_spk
    plot.loc["samples"] = vals_smpl
    ax = plot.plot(kind="bar", rot=0)
    # ax.set_ylim(-1.8, 3.7)
    # this displays the actual values
    for container in ax.containers:
        ax.bar_label(container)


def plot_bar_speakers_2(df1, df2, labels):
    """ "
    Plot speaker and sample stats
    df needs to have speaker column
    """
    sn1 = df1.speaker.nunique()
    sn2 = df2.speaker.nunique()
    smp1 = df1.shape[0]
    smp2 = df2.shape[0]
    vals_spk = [sn1, sn2]
    vals_smpl = [smp1, smp2]
    cols = labels
    plot = pd.DataFrame(columns=cols)
    plot.loc["speakers"] = vals_spk
    plot.loc["samples"] = vals_smpl
    ax = plot.plot(kind="bar", rot=0)
    # ax.set_ylim(-1.8, 3.7)
    # this displays the actual values
    for container in ax.containers:
        ax.bar_label(container)


# calc duration from segmented index
def calc_dur(x):
    starts = x[1]
    ends = x[2]
    return (ends - starts).total_seconds()


def calc_dur_seg_index(index):
    return index.to_series().map(lambda x: calc_dur(x))
