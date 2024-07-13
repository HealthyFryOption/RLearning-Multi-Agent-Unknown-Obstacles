import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm


# Example usage
if __name__ == "__main__":
    # jsonFile = filePath + "NMrecord_1.json"
    # title = input("Title: ")

    filePath = "./Analysis/"
    MainDirectory = "./Track/NM/"
    ModeDirectory = "F with Obstacle/"
    MapDirectory = "medium/"
    jsonFile = "NMRecord_1.json"

    title = "Pure Q-Learning"
    # title = "Q-Learning with Firefly"
    # title = "Q-Learning with Firefly On-Demand (Obstacles)"
    
    mapTitle = " Medium Complexity Map"

    title = title + mapTitle

    with open(MainDirectory + ModeDirectory +MapDirectory + jsonFile, 'r') as dataFile:
        data = json.load(dataFile)

    # Extract stages and agent IDs
    stages = sorted(data.keys())
    agent_ids = {entry["id"] for stage in data.values() for entry in stage}

    # Create a colormap
    num_colors = 30 # dealing with only 30 colours

    colourMapping = cm.get_cmap('tab20b', 20)
    colourMapping2 = cm.get_cmap('tab20c', 20)

    # plt.rcParams["font.size"] = 2

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
        # color = colors(i // 2)  # Use the same color for two consecutive lines
        if i < 20:
            color = colourMapping(i)
        else:
            color = colourMapping2(i - 20)

        # color = colors(i)  
        # style = line_styles[i % 2]  # Alternate line styles
        # widthSize = 1.5 if style == '--' else 1
        # plt.plot(stages, agent_runs[agent_id], linestyle=style, marker='o', markersize=7, linewidth=widthSize, label=f'Instance {agent_id}', color=color)
        plt.plot(stages, agent_runs[agent_id], marker='o', markersize=7, linewidth=1, label=f'Instance {agent_id}', color=color)

    plt.xlabel('Epoch')
    plt.ylabel('Number of Iterations')
    plt.title(title)
    # plt.yscale('log')  # Apply logarithmic scale to the y-axis
    plt.grid(True)
    
    # Adjust legend
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    plt.legend(unique_labels.values(), unique_labels.keys(), loc='upper left', bbox_to_anchor=(1, 1), ncol=1, fontsize='small')

    # Save the plot to a file
    plt.savefig(f'{title}.png')
    plt.show()