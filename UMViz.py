import seaborn as sns

def ucs_histogram(data_dir, data):
    sns.set_style("darkgrid")
    data = data.astype({"score": float}).groupby(["contributor_uuid"]).mean()
    sns_hist = sns.histplot(data=data, bins=10, stat="count", kde=True)
    sns_hist.set_title("Distribution of UCS Scores")
    sns_hist.axes.figure.savefig(data_dir + "/ucs_distribution")
