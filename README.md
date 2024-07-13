# RL-Multi-Agent-Unknown-Obstacles

## What is the project about
This repository is used to test out 2D tile-based simulations for multi-agent Q-Learning that is implemented with Firefly Algorithm's concepts via Netlogo. The base code is all written in Python.

It is used to experiment the feasability of implementing Cooperative Q-Learning Multi-Agent systems with concepts of brightness borrowed from the Firefly Algorithm. Ultimately, to gauge how good does the Bio-Inspired algorithm increase cooperativeness between agents as well as improve training efficiency by lowering iterations needed for agents to reach a goal point.

## Pre-Requisites
1) Download NetLogo and all its related programs. The version during the development of this project is Netlogo 6.4.0
2) Create a netlogo file / instance.
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
   Note changes can be made, and NM stands for 'New Model'. Customize as desired.
