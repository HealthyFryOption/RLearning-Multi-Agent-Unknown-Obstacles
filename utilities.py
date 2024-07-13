def checkNextStateValid(mapHeight, mapWidth, next_state, obstacleSet):
    finalHeight = mapHeight - 1
    finalWidth = mapWidth - 1

    if isinstance(next_state, str):
        next_state = reverseStateAgentDict(next_state)

    # Check if its out of bounds
    if(next_state[0] > finalWidth or next_state[0] < 0):
        return False

    if(next_state[1] > finalHeight or next_state[1] < 0):
        return False
    
    nextStateStr = f"({next_state[0]}, {next_state[1]})"
    if nextStateStr in obstacleSet:
        return False
    
    return True

def checkIfObstacle(state, obstacles):
    for obstacle in obstacles:
        if state[0] == obstacle.posX and state[1] == obstacle.posY:
            return True
    return False

def checkSumOfObstacle(state, obstacles):
    obstacleAround = 0
    for obstacle in obstacles:
        if state[0] == obstacle.posX and state[1] == obstacle.posY:
            obstacleAround += 1
    return obstacleAround

def getBrightnessFactor(centerState, state, radius):
    diffX = abs(centerState[0] - state[0])
    diffY = abs(centerState[1] - state[1])
    
    hammingDistance = diffX + diffY

    # Check if tile is adjacent (left, right, top, bottom)
    if hammingDistance == 1:
        return 1

    # Check if tile is diagonal or horizontal/vertical but within radius
    elif hammingDistance < radius:
        return hammingDistance / radius

    # Tile is outside the considered radius
    else:
        return 1 / radius  

def getStateAgentDict(position):
    """
        Return the dictionary string key format for a state
        'x, y'
    """
    return f"{position[0]}, {position[1]}"

def reverseStateAgentDict(state):
    """
        Reverse the dictionary string key format into a normal list
        [x, y]
    """

    x_str, y_str = state.split(", ")
    return [int(x_str), int(y_str)]

def getTileDistance(position1, position2):
    return ((position1[0] - position2[0]) ** 2 + (position1[1] - position2[1]) ** 2) ** 0.5

def checkRawCoordsSame(pos1, pos2):
        return (pos1[0] == pos2[0]) and (pos1[1] == pos2[1])