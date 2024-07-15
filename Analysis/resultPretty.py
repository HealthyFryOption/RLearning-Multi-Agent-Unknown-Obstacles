import json
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns


def plot_data_distribution(data, trimmedMean, title, confidence_interval=0.68):
    runs = data

    median = np.median(runs)

    # Plot the data distribution
    plt.figure(figsize=(12, 6))
    bin_width = 50
    max_val = np.max(runs)
    min_val = np.min(runs)
    num_bins = int((max_val - min_val) / bin_width) + 1
    sns.histplot(runs, bins=num_bins, kde=True, color='blue', alpha=0.6, label='Iterations')

    # Mark the mean, median, and standard deviation
    plt.axvline(trimmedMean, color='orange', linestyle='-', linewidth=2, label='Trimmed Mean (10%)')
    plt.axvline(median, color='green', linestyle='-', linewidth=2, label='Median')

    plt.text(0.99, 0.8, f'Median: {"{:.2f}".format(median)}', ha='right', va='bottom', transform=plt.gca().transAxes, bbox=dict(facecolor='green', alpha=0.5))
    plt.text(0.99, 0.75, f'Trimmed Mean (10%): {"{:.2f}".format(trimmedMean)}', ha='right', va='bottom', transform=plt.gca().transAxes, bbox=dict(facecolor='orange', alpha=0.5))

    # Customize the plot
    plt.title(title)
    plt.xlabel('Iterations Of Instance(s)')
    plt.ylabel('Frequency')
    plt.legend()

    # plt.savefig(f'{title}.png', bbox_inches='tight')

    plt.show()

def averageAfterZScoreOutlier(data, threshold=3):
    mean = np.mean(data)
    std_dev = np.std(data)

    print([abs((x - mean) / std_dev) for x in data])

    dataP = [x for x in data if abs((x - mean) / std_dev) < threshold]

    return sum(dataP) / len(dataP)

def medianTrimmedMean(runs, trim_percent=0.1):
    median = np.median(runs)
    trimmedMean = stats.trim_mean(runs, proportiontocut=trim_percent)

    return median, trimmedMean

if __name__ == "__main__":
    MainDirectory = "./Track/NM/"
    ModeDirectory = "F with Obstacle/"
    MapDirectory = "high/"
    jsonFile = "NMRecord_1.json"

    title = ""
    epoch = " "
    mapTitle = " "

    title = title + epoch + mapTitle

    with open(MainDirectory + ModeDirectory +MapDirectory + jsonFile, 'r') as dataFile:
        data = json.load(dataFile)["8"]

    data = sorted(data, key=lambda x: x['id'])
    runsOnly = [dataRun['runs'] for dataRun in data]

    median, trimmedMean = medianTrimmedMean(runsOnly.copy())
    plot_data_distribution(runsOnly.copy(), trimmedMean, title, 0.68)

    cumRuns = 0
    max = 0
    maxID = 0
    min = float('inf')

    for dataRun in data:
        cumRuns += dataRun['runs']

        if dataRun["runs"] < min:
            minID = dataRun['id']
            min = dataRun["runs"]
        if dataRun["runs"] > max:
            maxID = dataRun['id']
            max = dataRun["runs"]

        print(f"{dataRun['id']} {dataRun['runs']} {'Yes' if dataRun['reachedGoal'] else 'No'}")

    print("\n")
    print(f"Cumulative Runs: {cumRuns}")

    print(f"Max: {max}")
    print(f"Max ID: {maxID}\n")

    print(f"Min: {min}")
    print(f"Min ID: {minID}\n")

    print(f"Mean: {sum(runsOnly) / len(runsOnly)}")
    print(f"Median: {median}")
    print(f"Trimmed Mean (10%): {trimmedMean}")