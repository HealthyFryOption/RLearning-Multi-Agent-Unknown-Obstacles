# Reinforcement Learning for Multi-Agent Coordination in Environments with Unknown Obstacles

## What is the project about
This repository is used to test out 2D tile-based simulations for multi-agent Q-Learning that is implemented with Firefly Algorithm's concepts via Netlogo. The base code is all written in Python.

It is used to experiment the feasability of implementing Cooperative Q-Learning Multi-Agent systems with concepts of brightness borrowed from the Firefly Algorithm. Ultimately, to study how a chosen Bio-Inspired algorithm will influence cooperativeness between agents as well as training efficiency through gauging iterations needed for agents to reach a goal point.

The Firefly Algorithm concept is implemented via the creation of POIs (Points of Interest). Where every iteration, agents will shine "brightness" values that covers tiles around its center. The further the brightness is from the center, the lower the value. When brightess value from different agents collides, POIs are created. This is used during reward calculation process, where the POIs brightness values stacked by various agents' brightness are added should an agent previous state before transition be a POI.

## Pre-Requisites
1) Download NetLogo and all its related programs. The version during the development of this project is Netlogo 6.4.0
2) Create a NetLogo file / instance
3) Pip install all required libraries from requirements.txt via
   ```
   pip install -r ./requirements.txt
   ```
4) Create the following empty folders in the directory:
   * Model
   * Recording
   * Records
   * Track
   * Track/NM
5) Create a .env file, containing the variable name netlogoHomeDirectory and netLogoModelFile:
   * netlogoHomeDirectory contains the path to your locally downloaded Netlogo program
   * netLogoModelFile contains the path and name of your Netlogo created File / Instance

## Usage Manual
All training / simulation runs relies on the parameters set in setting.json. Documentation related to the setting.json's fields are provided inside setting documentation named "settingDoc.txt"

1) To run the system
   ```
   python Main.py
   ```

2) It will ask whether to use a New or Old model. Any old trained models must be placed inside Model directory. Key in 'Y' if desired to run simulations with a trained model. The system will then require a version number. Provide related version number. For example, provide '2' to use model_2.json. Should you want to run simulations without a pre-trained model, Key in 'N'. Once the simulation end, if a model is saved it will automatically be added into Model directory, with a version number accompanying it. The version number given is the highest version number currently existing inside the directory, incremented by 1. 

3) If the simulation is running under multi-simulations, at the last iteration, all instances will save their recording of simulation inside Recording directory as mp4 files with the format {instance number}_record.mp4 in multi-simulation mode, or NEW_record.mp4 in non multi-simulation mode.

4) Any new map to be created must be created inside mapDesigns.json following the format of
   ```
   "mapName":{
      "mapWidth": int value,
      "mapHeight":  int value,
      "map":[
         [...]
         [...]
       ]
   }

   Within the [...], will be numbers with values:
      * 0: blank / open tiles
      * 1: obstacle
      * 2: agent
      * 9: goal point
   ```

5) Analysis folder contains data graphing code which will be used to graph out data stored in directory Track/NM.
   Note changes can be made, and NM stands for 'New Model'. Customize code as desired.
