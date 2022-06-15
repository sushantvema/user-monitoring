import seaborn as sns


def ucs_histogram(data_dir, data):
    sns.set_style("darkgrid")
    data = data.astype({"score": float}).groupby(["uuid"]).mean()
    sns_hist = sns.histplot(
        data=data,
    )
    sns_hist.savefig(data_dir + "/ucs_distribution")
