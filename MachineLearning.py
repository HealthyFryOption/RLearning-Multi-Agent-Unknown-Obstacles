import numpy as np
import math
import random
import utilities as utils

class ReinforcementLearningSystem():
    def __init__(self, map_width, map_height, modelParam, actionsNextStateMovement, goalPoint, actions, 
                 alpha=0.1, gamma=0.9, epsilon=0.1, baseEpsilon=0.15):
        
        self.goalPoint = goalPoint
        self.actionsNextStateMovement = actionsNextStateMovement
        self.map_width = map_width
        self.map_height = map_height
        self.num_states = self.map_width * self.map_height
        self.obstacles = []
        self.obstacleSet = set()

        self.maxRewardFactor = 10.0

        self.actions = actions
        self.num_actions = len(actions)
        self.invalidActionPenalty = -10

        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.baseEpsilon = baseEpsilon

        self.q_table = {}
        if modelParam:
            # if given modelParam
            self.q_table = modelParam
        else:
            self.createModel()

        # self.printQTable("INITIALIZATION")

    def decreaseEpsilon(self, epsilonRate):
        self.epsilon = max(self.baseEpsilon, self.epsilon - epsilonRate)

    def returnQValue(self, state, action_index):
        return self.q_table[utils.getStateAgentDict(state)][action_index]

    def createModel(self):
        # Create Model [from 0, 0  to  mX - 1, mY - 1]
        for y in range(self.map_height):
            for x in range(self.map_width):
                key = f"{x}, {y}"
                self.q_table[key] = np.zeros((self.num_actions))

    def checkSameState(self, state1, state2):
        return state1[0] == state2[0] and state1[1] == state2[1]

    def printQTable(self, message="===== Q-TABLE ====="):
        print(message)
        keys = list(self.q_table.keys())
        for i in range(0, len(keys), 2):
            key1 = keys[i]
            key2 = keys[i+1] if i+1 < len(keys) else None  # Handle the case where the last iteration has only one key
            value1 = self.q_table[key1]
            value2 = self.q_table[key2] if key2 is not None else None

            print(f"{key1}: {value1}", end='\t')
            if key2 is not None:
                print(f"{key2}: {value2}", end='')
            print("")
        print(message)

    @property
    def model(self):
        return self.q_table

    def checkTerminate(self, position):
        return (position[0] == self.goalPoint[0]) and (position[1] == self.goalPoint[1])
    
    def reverseStateAgentDict(self, state):
        x_str, y_str = state.split(", ")
        return [int(x_str), int(y_str)]
    
    def checkNextStateValidRFS(self, next_state):
        finalHeight = self.map_height - 1
        finalWidth = self.map_width - 1

        if isinstance(next_state, str):
            next_state = self.reverseStateAgentDict(next_state)

        # Check if its out of bounds
        if(next_state[0] > finalWidth):
            return False
        elif(next_state[0] < 0):
            return False

        if(next_state[1] > finalHeight):
            return False
        elif(next_state[1] < 0):
            return False
        
        # Check if its in an obstacle
        nextStateStr = f"({next_state[0]}, {next_state[1]})"
        if nextStateStr in self.obstacleSet:
            return False
        
        return True
    
    def chooseAction(self, position):
        state = utils.getStateAgentDict(position)
        action_index = None

        if np.random.rand() < self.epsilon:            
            # Choose a random action 
            action_index = np.random.choice(self.num_actions)
        elif np.all(self.q_table[state] <= 0):
            # If all Q-values are zero or negative, choose a random action index
            action_index = np.random.choice(self.num_actions)
        else:
            # Exploit: choose the action with the highest Q-value for the current state
            # return index of max.
            action_index = np.argmax(self.q_table[state])

        if action_index == None:
            raise(f"No action found for {state}")

        # return index of action
        return action_index

    def getNextAgentState(self, currentPosition, actionIndex):
        actionMovement = self.actionsNextStateMovement[actionIndex]

        newState = [currentPosition[0] + actionMovement[0], currentPosition[1] + actionMovement[1]]
        return newState

    def rewardFunction(self, current_position, next_state, rewardParam, max_reward=1.0):
        """
        will give penalty if: 1) never moved at all 2) attempted illegal move such as out of border
        will give reward if: 1) actually moved and give reward
        """
        # Calculate the Euclidean distance between the current position and the goal position
        distance = utils.getTileDistance(current_position, self.goalPoint)
        sumOfObstacles = utils.checkSumOfObstacle(current_position, self.obstacles)
        
        if self.checkSameState(current_position, next_state):
            # Give this reward if they didn't move at all
            reward = self.invalidActionPenalty * 0.5  

        elif self.checkNextStateValidRFS(next_state):
            # Check if the next position is within the border or not in obstacle

            # Calculate the reward based on the distance
            reward = max_reward / (distance + 0.1)
            reward *= rewardParam["distance"]

            if len(self.obstacles):
                reward -= ((sumOfObstacles / len(self.obstacles)) * rewardParam["obstaclesAround"])
        else:
            # Assign a negative reward for attempting to move out of the border
            reward = self.invalidActionPenalty  # Adjust the penalty value as needed

        if self.checkTerminate(next_state):
            # If terminate state found, give a high reward
            reward *= self.maxRewardFactor

        return reward
    
    def takeActionObserve(self, currentPosition, actionIndex):
        # Used to return the next state if action taken in current position

        next_state = self.getNextAgentState(currentPosition, actionIndex)

        return next_state

    def updateQTable(self, current_state, action, reward, next_state):
        # Check if the next state is legal
        if self.checkNextStateValidRFS(next_state):

            # Calculate the maximum Q-value for the next state
            max_q_next = np.max(self.q_table[utils.getStateAgentDict(next_state)])

        else:
            # If the next state is outside the border or in obstacle, set the maximum Q-value to 0
            max_q_next = 0
        
        current_state_rep = utils.getStateAgentDict(current_state)

        self.q_table[current_state_rep][action] += self.alpha * (reward + (self.gamma * max_q_next) - self.q_table[current_state_rep][action])

class FireflyAlgo():
    def __init__(self, mapHeight, mapWidth, obstacles, obstacleSet, onlyObstaclesMode=False, poiRadius=1, k=0.05, maxValue=0.1, debug=False, draw=False):
        self.k = k
        self.maxValue = maxValue
        self.debug = debug

        self.mapHeight = mapHeight
        self.mapWidth = mapWidth
        self.obstacles = obstacles
        self.obstacleSet = obstacleSet
        
        self.poiRadius = poiRadius
        self.onlyObstaclesMode = onlyObstaclesMode

        self.tilesToConsider = {}
        self.tilesBrightness = {}
        self.previousBrightness = []
        self.validBrightness = {}

    def getSurroundingTiles(self, tile, iterations):
        tilesToUpdate = []
        xTile = tile[0]
        yTile = tile[1]

        for i in range(iterations):
            area = i + 1

            if(iterations > 1 and area <= iterations):
                displace = 1
                for k in range(area - 1, 0, -1):
                    tilesToUpdate.append((xTile - k, yTile + displace)) # top left
                    tilesToUpdate.append((xTile - k, yTile - displace)) # bottom left

                    tilesToUpdate.append((xTile + k, yTile + displace)) # top right
                    tilesToUpdate.append((xTile + k, yTile - displace)) # nottom right

                    displace += 1
            
            tilesToUpdate.append((xTile, yTile + area)) # top
            tilesToUpdate.append((xTile, yTile - area)) # bottom
            tilesToUpdate.append((xTile - area, yTile)) # left
            tilesToUpdate.append((xTile + area, yTile)) # right

        return tilesToUpdate, [tileUpdate for tileUpdate in tilesToUpdate if utils.checkNextStateValid(self.mapHeight, self.mapWidth, tileUpdate, self.obstacleSet)]


    def updateBrightnessForTile(self, tileToUpdate, targetPosition):

        # tileToUpdate is the nextstate of agents

        distanceFromTarget = utils.getTileDistance(tileToUpdate, targetPosition)
        brightness = self.maxValue * math.exp(-self.k * distanceFromTarget)
        iterations = min(self.poiRadius, int(brightness * 10))

        if not iterations:
            # if 0 iterations, meaning brightness is 0 or below 0.1
            return

        # Return surrounding tiles
        surroudingTiles, validSurroundingTiles = self.getSurroundingTiles(tileToUpdate, iterations)

        if self.onlyObstaclesMode:
            gotObstacle = False
            
            for tile in surroudingTiles:
                if utils.checkIfObstacle(tile, self.obstacles):
                    gotObstacle = True
                    break

            if not gotObstacle:
                # does not have at least one tile has an obstacle
                return

        for surroundingTileToUpdate in validSurroundingTiles:
            # Get string ref
            surroundingTileToUpdateStr = utils.getStateAgentDict(surroundingTileToUpdate)

            if surroundingTileToUpdateStr in self.tilesToConsider:
                self.tilesToConsider[surroundingTileToUpdateStr] += 1
                self.tilesBrightness[surroundingTileToUpdateStr] += (brightness * utils.getBrightnessFactor(tileToUpdate, surroundingTileToUpdate, iterations))
            else:
                self.tilesToConsider[surroundingTileToUpdateStr] = 1
                self.tilesBrightness[surroundingTileToUpdateStr] = (brightness * utils.getBrightnessFactor(tileToUpdate, surroundingTileToUpdate, iterations))
    
    def updateValidTiles(self):
        for tileKey in self.tilesToConsider:

            # Is a POI
            if self.tilesToConsider[tileKey] > 1:
                self.validBrightness[tileKey] = self.tilesBrightness[tileKey]

    def getBrightness(self, tile):
        # tile is previous state
        tileStr = utils.getStateAgentDict(tile)
        
        if tileStr in self.tilesToConsider:
            # Is a POI
            if self.tilesToConsider[tileStr] > 1:
                return self.tilesBrightness[tileStr]
        
        # Is not a POI
        return 0

    def resetFireflyTiles(self):
        self.previousBrightness = []
        
        if self.debug:
            self.previousBrightness = [utils.reverseStateAgentDict(tile) for tile in self.tilesBrightness]
        else:
            self.previousBrightness = [utils.reverseStateAgentDict(tile) for tile in self.validBrightness]
        
        self.validBrightness = {}
        self.tilesToConsider = {}
        self.tilesBrightness = {}