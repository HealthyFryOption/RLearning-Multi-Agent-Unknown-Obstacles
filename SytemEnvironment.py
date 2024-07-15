from MachineLearning import FireflyAlgo
import utilities as utils

class WorldObjects():
    def __init__(self, posX, posY):
        self.posX = posX
        self.posY = posY

    def __str__(self):
        return f"Object TYPE: NATIVE | [{self.posX}, {self.posY}]"

    def checkColision(self, targetPosition):
        """
            Check collision between WORLDOBJECTS only
        """
        return (targetPosition.posX == self.posX ) and (targetPosition.posY == self.posY )
    
    @property
    def strRep(self):
        return f"({self.posX}, {self.posY})"

class Agent(WorldObjects):
    def __init__(self, posX, posY, ID):
        self.ID = ID
        self.reachedGoal = False

        super().__init__(posX, posY)

    def __str__(self):
        return f"Object TYPE: AGENT | [{self.posX}, {self.posY}]"

    @property
    def postion(self):
        # return {"x": self.posX, "y": self.posY}
        return (self.posX, self.posY)

    def updatePosition(self, addX, addY):
        self.posX += addX
        self.posY += addY

    def move(self, movement):
        # used for turtle movement only. After running, need to reset heading to 0
        command = f"ask turtle {self.ID} "

        match movement:
            case "f":
                command += "[ fd 1 ]"
                self.updatePosition(0, 1)
            case "b":
                command += "[ bk 1 ]" 
                self.updatePosition(0, -1)
            case "l":
                command += "[ lt 90 fd 1 ]" 
                self.updatePosition(-1, 0)
            case "r":
                command += "[ rt 90 fd 1 ]"  
                self.updatePosition(1, 0)
            case "lf":
                command += "[ lt 45 fd (sqrt 2) ]" 
                self.updatePosition(-1, 1)
            case "rf":
                command += "[ rt 45 fd (sqrt 2) ]"  
                self.updatePosition(1, 1)
            case "lb":
                command += "[ lt 135 fd (sqrt 2) ]" 
                self.updatePosition(-1, -1)
            case "rb":
                command += "[ rt 135 fd (sqrt 2) ]"  
                self.updatePosition(1, -1)
        
        return command

    def resetPosition(self):
        return f"ask turtle {self.ID} [ set heading 0 ]"

class MainInterface():
    def __init__(self, netLogoInterface, goalPoint, actions, mapSizeWidth, mapSizeHeight, reinforcementSystem, fireflySettings, rewardParam, obstacles_init=[], agents_init=[],
                 epsilonDecreaseRate = 0.0005):
        self.netLogo = netLogoInterface
        self.iterations = 0

        self.mapSizeWidth = mapSizeWidth
        self.mapSizeHeight = mapSizeHeight

        self.goalPoint = goalPoint
        
        self.rfs = reinforcementSystem
        self.actions = actions
        self.epsilonDecreaseRate = epsilonDecreaseRate

        self.rewardParam = rewardParam
        
        self.agents = []
        self.agentReachedGoal = 0
        self.obstacles = []
        self.obstacleSet = set()
        
        # keep track of the actions that agents want to initially do. The keys are str rep of states
        #{"next_state": [{agent_id, action, current_state, next_state}, ...]}
        self.agentActionMemory = {} 

        # The finalizedUpdates of every agent and what their action and next state
        self.finalizedAgentUpdates = []

        # keep track whether the transition can actually happen, specifically if an agent can move
        # to a state unoccupied by another agent
        self.legalTranistion = {}

        self.initModelVariables()

        # Create Map Objects
        self.createObstacle(obstacles_init)
        self.createAgents(agents_init)

        self.useFirefly = fireflySettings["fireflyMode"]
        self.fireflySystem = None
        self.debugFirefly = fireflySettings["debug"]
        self.drawFireflyMode = fireflySettings["draw"]

        if self.useFirefly:
            print("NOTE: Using Firefly Algo")
            self.fireflySystem = FireflyAlgo(self.mapSizeHeight, self.mapSizeWidth, self.obstacles, self.obstacleSet, fireflySettings["onlyObstaclesMode"],
                                             poiRadius=fireflySettings["poiRadius"], k=fireflySettings["fireflyK"], maxValue=fireflySettings["fireflyMaxReward"],
                                             debug=fireflySettings["debug"]
                                )

        # Set up and draw map
        self.setUpInterface()

    def initModelVariables(self):
        for y in range(self.mapSizeHeight):
            for x in range(self.mapSizeWidth):
                key = f"{x}, {y}"

                self.agentActionMemory[key] = []
                self.legalTranistion[key] = 0
        
        self.agentActionMemory["invalid"] = []

    def resetAgentActionMemory(self):
        for new_state in self.agentActionMemory.keys():
            self.agentActionMemory[new_state] = []
            self.legalTranistion[new_state] = 0

        self.finalizedAgentUpdates = []

    def setUpInterface(self):
        # Clear all elements
        self.netLogo.command('reset-ticks')
        self.netLogo.command('clear-all')

        # Create the grid
        self.netLogo.command(f'resize-world 0 {self.mapSizeWidth - 1} 0 {self.mapSizeHeight - 1}')

        self.drawEnvironment(turtles=True)

    def drawEnvironment(self, turtles=False):
        # turtles set weather to recreate turtle
        self.netLogo.command('ask patches [set pcolor 102]')

        self.netLogo.command(f'ask patch {self.goalPoint[0]} {self.goalPoint[1]} [ set pcolor [ 0 255 0 ] ]')

        obstaclePatches = [f"[{obstacle.posX} {obstacle.posY}]" for obstacle in self.obstacles]
        if obstaclePatches:
            obstaclePatchesCommand = " ".join(obstaclePatches)
            self.netLogo.command(f'ask patches at-points [{obstaclePatchesCommand}] [ set pcolor black ]')

        if turtles:
            for agent in self.agents:
                self.netLogo.command(f"""
                            create-turtles 1 [
                                setxy (floor ({agent.posX} + 0.5)) (floor ({agent.posY} + 0.5)) 
                                set heading 0 
                                set color [ 0 155 0 ]
                                set shape "circle" 
                                set label "{agent.ID}"
                            ]
                        """)  
    
    def drawFirefly(self):
        self.netLogo.command('ask patches [ set plabel "" ]')

        prevBrightPatch = [f"[{tile[0]} {tile[1]}]" for tile in self.fireflySystem.previousBrightness]

        # Create the patch list string for previous brightness
        if prevBrightPatch:
            prevBrightPatchCommand = " ".join(prevBrightPatch)
            # Remove previous brightness in one command with if-else
            self.netLogo.command(f'ask patches at-points [{prevBrightPatchCommand}] [ set pcolor 102 ]')

        # Redraw Goal Point should it be covered by brightness previously
        self.netLogo.command(f'ask patch {self.goalPoint[0]} {self.goalPoint[1]} [ set pcolor [ 0 255 0 ] ]')

        if self.debugFirefly:
            command = []
            debugBrightTiles = self.fireflySystem.tilesBrightness
            for tile in debugBrightTiles:
                tileCoords = utils.reverseStateAgentDict(tile)
                command.append(f"ask patch {tileCoords[0]} {tileCoords[1]} [ set pcolor 25 set plabel {'{:.2f}'.format(debugBrightTiles[tile])} ]")
            self.netLogo.command(" ".join(command))

            command = []
            brightTiles = self.fireflySystem.validBrightness
            for tile in brightTiles:
                tileCoords = utils.reverseStateAgentDict(tile)
                command.append(f"ask patch {tileCoords[0]} {tileCoords[1]} [ set pcolor 44 set plabel {'{:.2f}'.format(brightTiles[tile])} ]")
            self.netLogo.command(" ".join(command))

        else:
            brightTiles = [f"[{tile[0]} {tile[1]}]" for tile in self.fireflySystem.validBrightness]
            brightTiles = {tile: utils.reverseStateAgentDict(tile) for tile in self.fireflySystem.validBrightness}
            brightTilesCommand = " ".join([f"[{coords[0]} {coords[1]}]" for coords in brightTiles.values()])
            
            if brightTiles:
                self.netLogo.command(f'ask patches at-points [{brightTilesCommand}] [ set pcolor 44 ]')

    def createObstacle(self, obstacles_init):
        for obstaclePatch in obstacles_init:
            obs = WorldObjects(obstaclePatch[0], obstaclePatch[1])
            self.obstacles.append(obs)
            self.obstacleSet.add(obs.strRep)

        # Set a connection between RFS's and System Envrionment's obstacles
        self.rfs.obstacles = self.obstacles
        self.rfs.obstacleSet = self.obstacleSet

    def createAgents(self, agents_init):
        for idx, agent in enumerate(agents_init):
            turtle_id = idx
            self.agents.append(Agent(agent[0], agent[1], turtle_id))
    
    def returnModel(self):
        return self.rfs.model

    # Loop Frame
    def runFrame(self, keyWord):
        # Choose actions for each agent
        for agent in self.agents:

            if agent.reachedGoal:
                # Ignore agents that have already reached the goal
                continue
            
            # Ask agent to choose an action based on their current position
            chosenAction = self.rfs.chooseAction(agent.postion)

            # Get the next state agent will transition to if chosen action is executed
            next_state = self.rfs.takeActionObserve(agent.postion, chosenAction)

            # Object to keep track of agent information so far
            obj =  {"agent_obj": agent, "currentQ": self.rfs.returnQValue(agent.postion, chosenAction),
                            "chosenAction": chosenAction, "current_state": agent.postion, "next_state": next_state,
                            "legal": True}
            
            if self.rfs.checkNextStateValidRFS(next_state): 
                # Add into memory of next state wanting to transition to
                self.agentActionMemory[utils.getStateAgentDict(next_state)].append(obj)

            else:
                # If out of bounds or obstacle detected, meaning their action is not legal

                obj["legal"] = False
                self.agentActionMemory["invalid"].append(obj)

        # Ensure there are no conflicting new states chosen agents want to transition to
        for new_state, agentInfos in self.agentActionMemory.items():
            if len(agentInfos) == 0:
                # No agent for this new state
                continue

            if new_state == "invalid":
                # New state for agents are invalid, so just add normally at first
                self.finalizedAgentUpdates.extend(
                    [agentInfo for agentInfo in agentInfos]
                ) 
                
            else:
                # get current max_q_value of all the agentInfos here
                max_Q_value = max([agentInfo['currentQ'] for agentInfo in agentInfos])

                # get the agent(s) that has the max q value out of all competiting agents trying to transition
                maxQAgents = [agentInfo for agentInfo in agentInfos if agentInfo['currentQ'] == max_Q_value]

                if len(agentInfos) > 1:
                    # there's more than one agent trying to get into the same new state. Set them all to their current positions if don't have max q value
                    notMaxQAgents = [agentInfo for agentInfo in agentInfos if agentInfo['currentQ'] != max_Q_value]
                    
                    # Dont allow agent that do not have maxqvalue to transition
                    for agentInfo in notMaxQAgents:
                        agentInfo["next_state"] = agentInfo["current_state"]
                    
                    self.finalizedAgentUpdates.extend(
                        notMaxQAgents
                    ) 
                
                # Get the agents with biggest value
                for i in range(len(maxQAgents)):
                    if i != 0:
                        # in case there are more than 1 agent with the same max q_value coincidentally, set the ones that are not the first element to their current state.
                        # allowing only one agent to move to contested region
                        maxQAgents[i]["next_state"] = maxQAgents[i]["current_state"]
   
                self.finalizedAgentUpdates.extend(
                    maxQAgents
                ) 

        # Shows whether there are how many finalized agents are going to be in this state. If there's more than 1, that means 1 agent is trying to transition, but
        # 1 agent already exist in that area already and their next state is a current state of theirs. Those set previously to their current state, their next_state is
        # their current state
        for agentInfo in self.finalizedAgentUpdates:
            if agentInfo["legal"]:
                self.legalTranistion[utils.getStateAgentDict(agentInfo["next_state"])] += 1

        # Final ensurance that all transitions are legal
        for agentInfo in self.finalizedAgentUpdates:
            if agentInfo["legal"]:
                # To prevent agents from transitioning to occupied states, and have state with 2 or more agents simultaneously
                if self.legalTranistion[utils.getStateAgentDict(agentInfo["next_state"])] > 1:
                    agentInfo["next_state"] = agentInfo["current_state"]

            if self.useFirefly:
                # Check if can move, yes update firefly brightness around
                if not utils.checkRawCoordsSame(agentInfo["next_state"], agentInfo["current_state"]):
                    self.fireflySystem.updateBrightnessForTile(agentInfo["next_state"], self.goalPoint)


        # Get true reward and update q-table as well as agent movements if valid
        for agentInfo in self.finalizedAgentUpdates:

            # Get their normal reward 
            agentInfo["reward"] = self.rfs.rewardFunction(agentInfo["current_state"], agentInfo["next_state"], self.rewardParam)

            if agentInfo["legal"]:
                # If next_state is legal

                # If there is some changes between current and next state (actually moved)
                if not utils.checkRawCoordsSame(agentInfo["next_state"], agentInfo["current_state"]):
                    
                    if self.useFirefly:
                        # Get POI birghtness of previous position, default to 0. The param are factors
                        agentInfo["reward"] += self.fireflySystem.getBrightness(agentInfo["current_state"]) * self.rewardParam["poi"]

                    # Actually call movement and update position
                    # Ask the agent to actually move to the new state
                    self.netLogo.command(agentInfo["agent_obj"].move(self.actions[agentInfo["chosenAction"]]))

            # Update Q-Table
            self.rfs.updateQTable(
                agentInfo["current_state"], agentInfo["chosenAction"], agentInfo["reward"], agentInfo["next_state"]
            )

            if self.rfs.checkTerminate(agentInfo["next_state"]):
                agentInfo["agent_obj"].reachedGoal = True
                self.agentReachedGoal += 1

        # Draw the environment for brightness (must draw first before resetting)
        if self.useFirefly:
            self.fireflySystem.updateValidTiles()

            if self.drawFireflyMode:
                self.drawFirefly()

        # Reset heading and face front
        self.netLogo.command(
            "ask turtles [ set heading 0 ] "
        )

        # Reset keeping memory
        self.resetAgentActionMemory()

        if self.useFirefly:
            self.fireflySystem.resetFireflyTiles()
        
        self.rfs.decreaseEpsilon(self.epsilonDecreaseRate)

        self.iterations += 1

        # Return goal reached
        return len(self.agents) == self.agentReachedGoal