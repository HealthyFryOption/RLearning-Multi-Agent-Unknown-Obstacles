import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Example usage
if __name__ == "__main__":
    MainDirectory = "./Track/NM/"
    ModeDirectory = "F with Obstacle/"
    MapDirectory = "medium/"
    jsonFile = "record_1.json"

    title = ""
    mapTitle = " "

    title = title + mapTitle

    with open(MainDirectory + ModeDirectory +MapDirectory + jsonFile, 'r') as dataFile:
        data = json.load(dataFile)

    # Extract stages and agent IDs
    stages = sorted(data.keys())
    agent_ids = {entry["id"] for stage in data.values() for entry in stage}

    # Create colour mappings
    colourMapping = cm.get_cmap('tab20b', 20)
    colourMapping2 = cm.get_cmap('tab20c', 20)

    # Prepare the data for plotting
    agent_runs = {agent_id: [] for agent_id in agent_ids}
    for stage in stages:
        for entry in data[stage]:
            agent_runs[entry["id"]].append(entry["runs"])
    
    # Define line styles
    line_styles = ['-', '--']
    
    # Plotting
    plt.figure(figsize=(15, 25))
    for i, agent_id in enumerate(agent_ids):
        if i < 20:
            color = colourMapping(i)
        else:
            color = colourMapping2(i - 20)

        plt.plot(stages, agent_runs[agent_id], marker='o', markersize=7, linewidth=1, label=f'Instance {agent_id}', color=color)

    plt.xlabel('Epoch')
    plt.ylabel('Number of Iterations')
    plt.title(title)
    plt.grid(True)
    
    # Adjust legend
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    plt.legend(unique_labels.values(), unique_labels.keys(), loc='upper left', bbox_to_anchor=(1, 1), ncol=1, fontsize='small')

    # Save the plot to a file
    plt.savefig(f'{title}.png')
    plt.show()