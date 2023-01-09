import matplotlib.pyplot as plt
import numpy as np


def ucs_histogram(data_dir, data):

    scores = data['score']
    # Plot a histogram of the 'score' column
    plt.hist(scores, bins=10)

    # Set the title of the plot
    plt.title("Distribution of Scores")
    # Set the x-axis label
    plt.ylabel('Number of contributors')

    # Set the y-axis label
    plt.xlabel('Score')
    # Save the figure
    plt.savefig(data_dir + "/score_distribution_mpl")

    plt.figure()
    # Select the 'score' column from the DataFrame
    scores = data['retrieved']
    # Plot a histogram of the 'score' column
    plt.hist(scores, bins=10)
    # Set the y-axis label
    plt.ylabel('Number of contributors')
    plt.xlabel('Number of tasks completed')
    # Set the title of the plot
    plt.title("Distribution of Scores")

    # Save the figure
    plt.savefig(data_dir + "/retrieved_distribution_mpl")
    plot_scatter(data_dir, data)

def plot_scatter(data_dir, data, ):
    # Select the 'score' and 'retrieved' columns from the DataFrame
    scores = data['score']
    retrieved = data['retrieved']

    plt.figure()
    # Plot a scatterplot of 'score' vs. 'retrieved'
    plt.scatter(retrieved, scores, s=20)

    # Set the x-axis label
    plt.ylabel('Score')

    # Set the y-axis label
    plt.xlabel('Retrieved')

    # Set the title of the plot
    plt.title('Relationship between Score and Retrieved')

    # Fit a linear regression model to the data
    slope, intercept = np.polyfit(retrieved, scores, 1)

    # Create a function to generate the fitted line
    fit_fn = np.poly1d([slope, intercept])

    # Plot the fitted line
    plt.plot(retrieved, fit_fn(retrieved), '--k')

    # Save the figure
    plt.savefig(data_dir + '/score_vs_retrieved.png')
