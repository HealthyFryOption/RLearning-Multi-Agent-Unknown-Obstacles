import pynetlogo

import traceback
import json
import numpy as np
import re

import threading, multiprocessing, queue
import time 
import itertools

from sys import exit
from msvcrt import getch
from os import listdir, getenv
from dotenv import load_dotenv

load_dotenv()

from SytemEnvironment import MainInterface
from MachineLearning import ReinforcementLearningSystem

# ===== Initialization =====
netlogoHomeDirectory = getenv("netlogoHomeDirectory")
netlogoModel = "./" + getenv("netLogoModelFile")
dataJsonFile = './setting.json'

miscDirectory = './Miscs/'
mapDesignFile = "mapDesigns.json"
modelDirectory = './Model/'
recordDirectory = './Records/'
recordingDirectory = './Recording/'

modelNamePrefix = "model_"
recordNamePrefix = "record_"

modelPattern = r".*model_(\d+)\.json"
recordPattern = r".*record_(\d+)\.json"

with open(dataJsonFile, 'r') as jsonF:
    systemSetting = json.load(jsonF)

selectedMap = systemSetting["selectedMap"]

with open(miscDirectory + mapDesignFile, 'r') as mapF:
    mapSettings = json.load(mapF)

goalReached = False
mapSettings = mapSettings[selectedMap]
frameRate = systemSetting["frameRate"]
multiConfig = systemSetting["multi"]
actions = systemSetting["actions"]
runWithGUI = systemSetting["runWithGUI"]
actionsNextStateMovement = systemSetting["actionsNextStateMovement"]

rewardParamSet = {}
if(systemSetting["fireflySettings"]["fireflyMode"]):
    rewardParamSet = systemSetting["rewardParam"]
else:
    # Note firefly Mode
    rewardParamSet = systemSetting["rewardParamNormal"]

map = mapSettings["map"][::-1] # reverse the map order in JSON design
mapWidth = mapSettings["mapWidth"]
mapHeight = mapSettings["mapHeight"]
mapStartHeight = 0
mapStartWidth = 0

modelParam = {}

# Map Objects
obstacles = []
agents = []
# ===== Initialization =====


# ===== System Run Variables / Processes =====
key = ""
pause = True
running = True
# ===== System Run Variables =====


# ===== System Run-Functions =====
def keyboardThread():
    # For multi-threading use of capturing keyboard inputs
    global key
    global running

    while running:
        key = getch().decode("utf-8")

def spinCursorAnimation():
    for cursor in itertools.cycle('|/-\\'):
        yield cursor

def pauseDelta():
    # Pause loop by delta time and set frameRate
    start_time = time.time()
    elapsed_time = time.time() - start_time
    remaining_time = max(0, frameRate - elapsed_time)
    time.sleep(remaining_time)

def saveModel(modelParam=None, extraName=""):
    # Get list of files in the directory
    files = listdir(modelDirectory)

    # Extract version numbers from file names
    versions = [int(re.search(modelPattern, file_name).group(1)) for file_name in files if re.search(modelPattern, file_name)]

    # Find the highest version number
    highest_version = (max(versions) if versions else 0) + 1

    print("Converting to JSON")
    data_json = {}
    if modelParam:
        data_json = {key: value.tolist() for key, value in modelParam.items()}
    else:
        data_json = {key: value.tolist() for key, value in nlMap.returnModel().items()}

    # Save trained model
    print("Saving trained model")

    # Write dictionary to JSON file
    with open(modelDirectory + f'{extraName}model_{highest_version}.json', 'w') as json_file:
        json.dump(data_json, json_file)

    print(f"Saved trained model as {modelNamePrefix}{highest_version}")

def saveRecords(records, extraName=""):
    files = listdir(recordDirectory)

    # Extract version numbers from file names
    versions = [int(re.search(recordPattern, file_name).group(1)) for file_name in files if re.search(recordPattern, file_name)]

    # Find the highest version number
    highest_version = (max(versions) if versions else 0) + 1

    with open(recordDirectory + f'{extraName}record_{highest_version}.json', 'w') as json_file:
        json.dump(records, json_file)

    print(f"Saved record as {recordNamePrefix}{highest_version}")

# ===== System Run-Functions =====


# ===== Main Function For Running Netlogo Instance =====
def runInstanceNormal(id, maxIteration, newModelParam, resultQueue, recordVid):
    try:
        netLogo = pynetlogo.NetLogoLink(gui=runWithGUI, netlogo_home=netlogoHomeDirectory)
        netLogo.load_model(netlogoModel)

        # Obstacles will be form during creation of System Environment
        reinforcementSystem = ReinforcementLearningSystem(
                                mapWidth, mapHeight, newModelParam, 
                                actionsNextStateMovement, goalPoint,
                                actions, systemSetting["alpha"],
                                systemSetting["gamma"], systemSetting["epsilon"], systemSetting["baseEpsilon"]
                        )

        nlMap = MainInterface(
            netLogo, goalPoint, actions, mapWidth, mapHeight, reinforcementSystem, 
            systemSetting["fireflySettings"], rewardParamSet, 
            obstacles.copy(), agents.copy(), systemSetting["epsilonDecreaseRate"]
        )

        netLogo.command('reset-ticks')

        if recordVid:
            netLogo.command('vid:start-recorder')

        print(f"Starting Process {id}")

        thread_running = True
        goalReached = False

        # Main Loop
        while thread_running and (nlMap.iterations <= maxIteration):
            goalReached = nlMap.runFrame("")

            netLogo.command('tick')

            if recordVid:
                netLogo.command('vid:record-view ')
        
            if goalReached:
                # based on the amount of agent reached and how many agents at the start

                thread_running = False
                print("Goal point has been reached")

        mapParam = {key: np.array(value) for key, value in nlMap.returnModel().items()}

        if recordVid:
            netLogo.command(f'vid:save-recording "{recordingDirectory}{id}_record.mp4"')

        # kill_workspace() method primarily closes the connection to the NetLogo workspace and stops any ongoing simulations or processes. Thus maybe that's why processes dont stop
        netLogo.kill_workspace()

        resultQueue.put({"id":id, "mapParam":mapParam, "iterations":nlMap.iterations, "reachedGoal": goalReached})

    except Exception as e:
        print(f"Exception in process {id}: {e}")
        traceback.print_exc()

    finally:
        print(f"Process {id} is done in {nlMap.iterations} iterations")
        print(f"Preparing Process {id}'s data results")
        exit()

# ===== Main Function For Running Netlogo Instance =====

# Initialize obstacles and agents starting locations (Multi-processing requires setup outside of Main Loop)
for mapLine in map:
    for grid in mapLine:
        if grid == 1:
            # is obstacle
            obstacles.append([mapStartWidth, mapStartHeight])
        elif grid == 2:
            agents.append([mapStartWidth, mapStartHeight])
        elif grid == 9:
            goalPoint = [mapStartWidth, mapStartHeight]
        mapStartWidth += 1
    mapStartHeight += 1
    mapStartWidth = 0

# ===== Main Loop =====
if __name__ == "__main__":
    print("NOW STARTING MAIN LOOP")

    if input("\nUse Old Model? (Y/N)\n").strip().capitalize() == "Y":
        version = input("Give version (INT): ")
        modelName = modelNamePrefix + version + ".json"

        # Read the JSON file (add new extra prefixes to check here). For example, NM refers to the naming format NMmodel_VERSIONNUMBER.json
        extraName = ["NM", 'L', 'M', 'H']
        index = 0

        while True:
            try:
                with open(modelDirectory + modelName, 'r') as json_file:
                    modelParam = json.load(json_file)

                print("Using Previous Model:\t" + modelName)

                break

            except FileNotFoundError:
                if index >= len(extraName):
                    raise(f"No model file was found for given version") 
                
                modelName = extraName[index] + modelName
                index += 1

        # Convert list values to NumPy arrays
        for key, value in modelParam.items():
            modelParam[key] = np.array(value)

    else:
        print("Using runs to make new model. New model will be saved into a directory called 'Model', and version number is automatically given"+
              "which is incremented by one from the highest version number found inside Model directory")

    # If Multi-Simulations are turned on
    if(multiConfig["run"]):
        print("Running Multi-Simulation(s)")

        normalRecords = {}
        numOfThread = multiConfig["threads"]
        threadsPerRound = multiConfig["threadsPerRound"]


        simulations = [{"id":id, "mapParam":modelParam, "runs":0} for id in range(numOfThread)]
        maxSimulation = multiConfig["maxSimulationEpoch"]
        
        spinner = spinCursorAnimation() # animation ascii
        
        mainLoopIter = 1

        while (mainLoopIter <= maxSimulation) and running:
            recordVid = False

            if mainLoopIter == maxSimulation:
                # Final loop, start recording every process
                recordVid = True

            normalRecords[mainLoopIter] = []
            print("LOOP: ", mainLoopIter)

            agents = []
            obstacles = []
            threadIndex = 0

            processes = {}
            resultQueue = multiprocessing.Queue()
            results = []

            threadIndex = 0
            activeThreads = 0
            resultBack = 0

            # The amount of threads per round at first
            for i in range(threadsPerRound):
                simulation = simulations[threadIndex]

                # for simulation in simulations:
                p = multiprocessing.Process(target=runInstanceNormal, args=(simulation["id"], multiConfig["maxIterationPerSimulation"], simulation["mapParam"], resultQueue, recordVid))
                p.daemon = True
                processes[simulation["id"]] = p
                p.start()

                threadIndex += 1
                activeThreads += 1
            
            while True:
                print("Running Instances: " + next(spinner), end='\r')
                if activeThreads < threadsPerRound and threadIndex < numOfThread:
                        simulation = simulations[threadIndex]

                        # for simulation in simulations:
                        p = multiprocessing.Process(target=runInstanceNormal, args=(simulation["id"], multiConfig["maxIterationPerSimulation"], simulation["mapParam"], resultQueue, recordVid))
                        p.daemon = True
                        processes[simulation["id"]] = p
                        p.start()

                        threadIndex += 1
                        activeThreads += 1
                try:
                    while True:
                        result = resultQueue.get(False)
                        results.append(result)
                        resultBack += 1

                        # Terminate process manually (NetLogo JVM won't close automatically even after calling its termination function) (Why? haha funny question!!!)
                        processes[result["id"]].terminate()
                        
                        del processes[result["id"]]
                        print(f"Process {result['id']} terminated")

                        activeThreads -= 1
                except queue.Empty:
                    pass
                
                # Give tasks a chance to put more data in
                time.sleep(0.1)    
                if not resultQueue.empty():
                    continue

                if resultBack == numOfThread:
                    break

            # print("Half processes are finished")
            time.sleep(3) 

            print("All processes are finished")

            # Set new models and save records
            for result in results:
                simulations[result["id"]]["mapParam"] = result["mapParam"]
                simulations[result["id"]]["runs"] = result["iterations"]

                normalRecords[mainLoopIter].append(
                    {
                        "id":result["id"],
                        "runs":result["iterations"],
                        "reachedGoal": result["reachedGoal"]
                    }
                )

            if mainLoopIter == maxSimulation:
                # Last loop, save top fit and their param, along with records
                saveRecords(normalRecords)
                topPerformer = min(simulations, key=lambda x: x["runs"])

                saveModel(topPerformer["mapParam"])

            mainLoopIter += 1
        
        print("Done")

    else:
        print("===== One-Run Experimental Testing on One Instance =====")
        print("Preparing Keyboard Thread")
        threads = threading.Thread(target = keyboardThread)
        threads.start()

        # Initialize NetLogo instance
        netlogoMain = pynetlogo.NetLogoLink(gui=runWithGUI, netlogo_home=netlogoHomeDirectory)
        netlogoMain.load_model(netlogoModel)

        # Obstacles will be form during creation of System Environment
        reinforcementSystem = ReinforcementLearningSystem(
                                mapWidth, mapHeight, modelParam, 
                                actionsNextStateMovement, goalPoint,
                                actions, systemSetting["alpha"],
                                systemSetting["gamma"], systemSetting["epsilon"], systemSetting["baseEpsilon"]
                        )

        nlMap = MainInterface(
            netlogoMain, goalPoint, actions, mapWidth, mapHeight, reinforcementSystem, 
            systemSetting["fireflySettings"], rewardParamSet, 
            obstacles.copy(), agents.copy(), systemSetting["epsilonDecreaseRate"]
        )

        netlogoMain.command('reset-ticks')
        netlogoMain.command('vid:start-recorder')
        
        print("One-Run Experimental Simulation Ready")

        # Main Loop
        while running:
            match key:
                case 'q':
                    running = False
                    pause = True
                    break
                case 'p':
                    pause = not pause
                    key = ""

                case "s":
                    saveModel()
                    pause = True

                case _:
                    pass
            
            if not pause:
                goalReached = nlMap.runFrame(key)
                netlogoMain.command('tick')
                netlogoMain.command('vid:record-view ')

                if goalReached:
                    running = False
                    # Wait for threads to gracefully close
                    threads.join()

                    print("Goal point has been reached")
            
        # Wait for threads to gracefully close
        threads.join()

        if input("Save Model? (Y/N)\n").capitalize() == "Y":
            print("Attempting to save model")
            saveModel()

        if input("Save Recording? (Y/N)\n").capitalize() == "Y":
            print("Attempting to save recording as NEW_record.mp4")
            netlogoMain.command(f'vid:save-recording "{recordingDirectory}NEW_record.mp4"')

        # Close the NetLogo instance
        netlogoMain.kill_workspace()