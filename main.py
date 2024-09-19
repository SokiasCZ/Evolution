
# libs
import dearpygui.dearpygui as dpg
import random
from creature import Creature
from neuron import Neuron
import math



# grid functions
def printGrid():
    for i in grid:
        print(i)

def displayGrid():
    for i in range(gridY):
        for j in range(gridX):
            dpg.draw_rectangle((10 + j * 20, 10 + i * 20), (20 + j * 20, 20 + i * 20), color=(255, 255, 255), parent=simArea)

def updateGrid():
    global simArea
    if not skip:
        if dpg.does_item_exist(simArea):
            dpg.delete_item(simArea)
        with dpg.drawlist(width=920, height=920, tag="simArea", parent=gridWin) as simArea:
            dpg.draw_rectangle((10, 10), (910, 910), color=(255, 255, 255))
            dpg.draw_rectangle((aliveStartX+10, aliveStartY+10), (aliveEndX+10, aliveEndY+10), color=(0, 255, 0), fill=(0, 255, 0, 20), parent=simArea)
            for i, line in enumerate(grid):
                for j, index in enumerate(line):
                    if grid[i][j] == "w":
                        dpg.draw_rectangle((10 + j * 20, 10 + i * 20), (20 + j * 20 + 10, 20 + i * 20 + 10), color=(0, 0, 0, 0), fill=(150, 150, 150), parent=simArea)
                    elif grid[i][j] != 0:
                        dpg.draw_circle((20 + j * 20, 20 + i * 20), 10, color=(0, 0, 0, 0), fill=index.color, parent=simArea)
            showIds()

def showIds():
    global simArea
    if dpg.get_value(showIdsCb):
        for i in creatures:
            dpg.draw_text((i.pos[0] * 20 + 10, i.pos[1] * 20 + 10), text=str(i.cId), size=20, color=(0, 0, 0), parent=simArea)

# additional functions for creatures
def generateRandomHex(length):
    return ''.join(random.choice('0123456789abcdef') for i in range(length))

def readConnection(gene):
    binary = (str(bin(int(gene, 16))[2:])).rjust(32, "0")
    source = int(binary[1:8], 2)
    if binary[0] == "0": # 0 = sensory, 1 = internal
        sourceType = "sensory"
        sourceId = source % len(sensoryList)
    else:
        sourceType = "internal"
        sourceId = source % len(internalList)

    sink = int(binary[9:16], 2)
    if binary[8] == "0": # 0 = internal, 1 = action
        sinkType = "internal"
        sinkId = sink % len(internalList)
    else:
        sinkType = "action"
        sinkId = sink % len(actionList)

    #print(binary[18:])
    #print(int(binary[18:], 2)/4000)
    weight = int(binary[18:], 2) / 4000
    if binary[17] == "1":
        weight *= -1
    return sourceType, sourceId, sinkType, sinkId, weight

def genSkip():
    global skip
    skip = True
    skipFor = int(dpg.get_value(gensForSkip))
    for i in range(skipFor):
        playGeneration()
        nextGeneration()
    skip = False            

def fastGens():
    skipFor = int(dpg.get_value(gensForSkip))
    for i in range(skipFor):
        playGeneration()
        nextGeneration()

def generateBrains():
    with dpg.window(label='Brains', width=600, height=1000, pos=(1000, 0), collapsed=True):
        for i in creatures:
            with dpg.tree_node(label="Creature " + str(i.cId)):
                with dpg.tree_node(label="Sensory"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sourceType == "sensory":
                            dpg.add_text(sensoryList[sourceId].name + " -> " + actionList[sinkId].name + " " + str(weight))
                with dpg.tree_node(label="Internal"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sourceType == "internal":
                            dpg.add_text(internalList[sourceId].name + " -> " + actionList[sinkId].name + " " + str(weight))
                with dpg.tree_node(label="Action"):
                    for j in i.genes:
                        sourceType, sourceId, sinkType, sinkId, weight = readConnection(j)
                        if sinkType == "action":
                            dpg.add_text(actionList[sinkId].name + " " + str(weight))

def nextGeneration():
    global creatures, genNum, grid, currStep, killCount
    if currStep < steps:
        return
    currStep = 0
    #print(killCount)
    killCount = 0
    genNum += 1
    dpg.set_value(generationText, "Generation: " + str(genNum))
    alive = []
    for i in creatures:
        if not i.eliminated:
            alive.append(i)
    creatures.clear()
    positions = []
    if genNum >= wallGeneration:
        if buildWall:
            for i in range(wallStart, wallStart + wallLenght):
                positions.append([wallDistance, i])
                grid[i][wallDistance] = "w"
    
    for i, cre in enumerate(alive):
        cre.color = (255, 0, 0)
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        while pos in positions:
            pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        cre.pos = pos
        cre.cId = i
        if random.randrange(0, mutation) == 0:
            index = random.randrange(0, 9)
            gene = random.choice(cre.genes)
            cre.genes.remove(gene)
            newGene = gene[:index] + generateRandomHex(1) + gene[index+1:]
            cre.genes.append(newGene)

        positions.append(pos)
        creatures.append(cre)
    for i in range(numCreatures-len(creatures)):
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        while pos in positions:
            pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
        genes = random.choice(creatures).genes.copy()
        if random.randrange(0, mutation) == 0:
            index = random.randrange(0, 9)
            gene = random.choice(cre.genes)
            cre.genes.remove(gene)
            newGene = gene[:index] + generateRandomHex(1) + gene[index+1:]
            cre.genes.append(newGene)
        creatures.append(Creature(pos, genes, defaultAction, i + len(alive), len(internalList)))
    grid.clear()
    for i in range(gridY):
        column = []
        for j in range(gridX):
            column.append(0)
        grid.append(column)
    if genNum >= wallGeneration:
        if buildWall:
            for i in range(wallStart, wallStart + wallLenght):
                positions.append([wallDistance, i])
                grid[i][wallDistance] = "w"
    for i in creatures:
        grid[i.pos[1]][i.pos[0]] = i
    updateGrid()


def playGeneration():
    global currStep
    while currStep < steps:
        step()
        currStep += 1
    for i in creatures:
        if i.pos[0] >= aliveStartX/20 and i.pos[0] < aliveEndX/20 and i.pos[1] >= aliveStartY/20 and i.pos[1] < aliveEndY/20:
            i.color = (0, 255, 0)
        else:
            i.color = (255, 255, 0)
            i.eliminated = True
    updateGrid()

def step():
    global currStep
    if currStep >= steps:
        return
    for creature in creatures:
        connections = []
        #print()
        #print(creature.cId)
        toInternal = []
        toAction = []
        for connection in creature.genes:
            sourceType, sourceId, sinkType, sinkId, weight = readConnection(connection)
            #print(sourceType, sourceId, sinkType, sinkId, weight)
            if sinkType == "internal":
                toInternal.append((sourceType, sourceId, sinkType, sinkId, weight))
            elif sinkType == "action":
                toAction.append((sourceType, sourceId, sinkType, sinkId, weight))
        internalValues = {}
        for sinkInternal in toInternal:
            if sinkInternal[0] == "sensory": # source type
                value = sensoryList[sinkInternal[1]].computation(creature) * sinkInternal[4]
            elif sinkInternal[0] == "internal":
                value = creature.internalNeurons[sinkInternal[1]] * sinkInternal[4]
            if sinkInternal[3] in internalValues.keys():
                internalValues[sinkInternal[3]] += value
            else:
                internalValues[sinkInternal[3]] = value
        for neuronKey in internalValues.keys():
            creature.internalNeurons[neuronKey] = math.tanh(internalValues[neuronKey])
        actionValues = {}
        for sinkAction in toAction:
            if sinkAction[0] == "sensory":
                value = sensoryList[sinkAction[1]].computation(creature) * sinkAction[4]
            elif sinkAction[0] == "internal":
                value = creature.internalNeurons[sinkAction[1]] * sinkAction[4]
            if sinkAction[3] in actionValues.keys():
                actionValues[sinkAction[3]] += value
            else:
                actionValues[sinkAction[3]] = value
        
        action = (0, 0)
        for actionKey in actionValues.keys():
            actionValues[actionKey] = math.tanh(actionValues[actionKey])
            if actionValues[actionKey] > action[0]:
                action = (actionValues[actionKey], actionKey)
        creature.stepAction = actionList[action[1]].computation

    for creature in creatures:
        if not creature.dead:
            grid[creature.pos[1]][creature.pos[0]] = 0
            creature.stepAction(creature)
            grid[creature.pos[1]][creature.pos[0]] = creature

    currStep += 1
    updateGrid()

def showGenes(sender, app_data, user_data):
    if dpg.does_item_exist("nGenes"):
        dpg.delete_item("nGenes")

    #Encrypted genomes
    encryptedGenomes = []
    for gene in user_data.genes:
        encryptedGenomes.append(readConnection(gene))

    #NODE EDITOR
    with dpg.node_editor(label="Genes", tag="nGenes", parent="wGenesGraph", width=1000, height=800):
        #Create nodes for each gene
        neurons = {}
        for gene in encryptedGenomes:

            #Variables
            n1 = gene[0]
            n2 = gene[2]
            w = gene[4]
            n1Id = gene[1]
            n2Id = gene[3]

            
            neuron = (n1, n1Id)
            if neuron not in neurons.keys():
                neurons[neuron] = [0, 1]
            else:
                neurons[neuron][1] += 1
            neuron = (n2, n2Id)
            if neuron not in neurons.keys():
                neurons[neuron] = [1, 0]
            else:
                neurons[neuron][0] += 1
        
        for i, displayNeuron in enumerate(neurons.keys()):
            with dpg.node(label=f"{displayNeuron[1]} {displayNeuron[0]}", pos=(0, 0)):
                for i in range(neurons[displayNeuron][0]):
                    with dpg.node_attribute(label="Input",attribute_type=dpg.mvNode_Attr_Input, tag=f"input_{displayNeuron[1]}_{displayNeuron[0]}_{str(i)}"):
                        dpg.add_text("Input")
                for i in range(neurons[displayNeuron][1]):
                    with dpg.node_attribute(label="Output",attribute_type=dpg.mvNode_Attr_Output, tag=f"output_{displayNeuron[1]}_{displayNeuron[0]}_{str(i)}"):
                        dpg.add_text("Output", tag=f"label_{displayNeuron[1]}_{displayNeuron[0]}_{str(i)}")

        #Connections between neurons
        for gene in encryptedGenomes:
            n1 = gene[0]
            n2 = gene[2]
            w = gene[4]
            n1Id = gene[1]
            n2Id = gene[3]
            dpg.add_node_link(f"output_{n1Id}_{n1}_{str(neurons[(n1, n1Id)][1]-1)}", f"input_{n2Id}_{n2}_{str(neurons[(n2, n2Id)][0]-1)}")
            dpg.set_value(f"label_{n1Id}_{n1}_{str(neurons[(n1, n1Id)][1]-1)}", f"Weight: {w}")
            neurons[(n1, n1Id)][1] -= 1
            neurons[(n2, n2Id)][0] -= 1
                    
            



def genesGraph():

    #Creature Select window
    def creatureSelect():
        if dpg.does_item_exist("wCreatureSelect"):
            dpg.delete_item("wCreatureSelect")
        else:
            gGraphPos = dpg.get_item_pos("wGenesGraph")
            with dpg.window(label='Creature Select', width=600, height=1000, pos=gGraphPos, tag="wCreatureSelect", on_close=creatureSelect):
                for i in creatures:
                    dpg.add_button(label="Creature " + str(i.cId), callback=showGenes, tag="bCreature" + str(i.cId), user_data=i)

    #Node window
    with dpg.window(label='Genes Graph', width=1000, height=1000, pos=(1000, 0), tag="wGenesGraph"):

        #Menu bar
        with dpg.menu_bar():
            dpg.add_button(label="Creature Select", callback=creatureSelect, tag="bCreatureSelect")

# sensory neurons functions
def randomSensory(*args):
    return random.random()

def ageSensory(*args):
    return currStep / steps

def northDistance(creature):
    return 1 - creature.pos[1] / gridX

def southDistance(creature):
    return creature.pos[1] / gridX

def eastDistance(creature):
    return creature.pos[0] / gridY

def westDistance(creature):
    return 1 - creature.pos[0] / gridY

def hasCoat(creature):
    if creature.coat:
        return 1
    else:
        return 0

def creatureForward(creature):
    direction = creature.facing
    if direction == "north":
        for i in range(1, 4):
            if creature.pos[1] - i < 0 or grid[creature.pos[1] - i][creature.pos[0]]:
                return i / 4
    elif direction == "south":
        for i in range(1, 4):
            if creature.pos[1] + i >= gridY or grid[creature.pos[1] + i][creature.pos[0]]:
                return i / 4
    elif direction == "east":
        for i in range(1, 4):
            if creature.pos[0] + i >= gridX or grid[creature.pos[1]][creature.pos[0] + i]:
                return i / 4
    elif direction == "west":
        for i in range(1, 4):
            if creature.pos[0] - i < 0 or grid[creature.pos[1]][creature.pos[0] - i]:
                return i / 4
    return 0

# internal neuron functions
def internalCalculation(inputs):
    return math.tanh(sum(inputs))

# action neurons functions
def defaultAction(*args):
    return 0

def moveUp(creature):
    if creature.pos[1] > 0 and not grid[creature.pos[1] - 1][creature.pos[0]]:
        creature.pos[1] -= 1
        creature.facing = "north"

def moveDown(creature):
    if creature.pos[1] < gridY - 1 and not grid[creature.pos[1] + 1][creature.pos[0]]:
        creature.pos[1] += 1
        creature.facing = "south"

def moveLeft(creature):
    if creature.pos[0] > 0 and not grid[creature.pos[1]][creature.pos[0] - 1]:
        creature.pos[0] -= 1
        creature.facing = "west"

def moveRight(creature):
    if creature.pos[0] < gridX - 1 and not grid[creature.pos[1]][creature.pos[0] + 1]:
        creature.pos[0] += 1
        creature.facing = "east"

def moveRandom(creature):
    direction = random.choice(["up", "down", "left", "right"])
    if direction == "up":
        moveUp(creature)
    elif direction == "down":
        moveDown(creature)
    elif direction == "left":
        moveLeft(creature)
    elif direction == "right":
        moveRight(creature)

def awayFromWall(creature):
    if creature.pos[1] < gridY / 2:
        moveDown(creature)
    else:
        moveUp(creature)
    if creature.pos[0] < gridX / 2:
        moveRight(creature)
    else:
        moveLeft(creature)

def makeCoat(creature):
    creature.coat = True
    creature.color = (0, 0, 255)

def followCreature(creature):
    pass

def goForward(creature):
    if creature.facing == "north":
        moveUp(creature)
    elif creature.facing == "south":
        moveDown(creature)
    elif creature.facing == "east":
        moveRight(creature)
    elif creature.facing == "west":
        moveLeft(creature)

def kill(creature): # does not work rn
    global killCount
    direction = creature.facing
    if direction == "north":
        if creature.pos[1] > 0:
            if type(grid[creature.pos[1] - 1][creature.pos[0]]) == Creature:
                deadId = grid[creature.pos[1] - 1][creature.pos[0]].cId
                grid[creature.pos[1] - 1][creature.pos[0]] = 0
                killCount += 1

    elif direction == "south":
        if creature.pos[1] < gridY - 1:
            if type(grid[creature.pos[1] + 1][creature.pos[0]]) == Creature:
                deadId = grid[creature.pos[1] + 1][creature.pos[0]].cId
                grid[creature.pos[1] + 1][creature.pos[0]] = 0
                killCount += 1

    elif direction == "east":
        if creature.pos[0] < gridX - 1:
            if type(grid[creature.pos[1]][creature.pos[0] + 1]) == Creature:
                deadId = grid[creature.pos[1]][creature.pos[0] + 1].cId
                grid[creature.pos[1]][creature.pos[0] + 1] = 0
                killCount += 1

    elif direction == "west":
        if creature.pos[0] > 0:
            if type(grid[creature.pos[1]][creature.pos[0] - 1]) == Creature:
                deadId = grid[creature.pos[1]][creature.pos[0] - 1].cId
                grid[creature.pos[1]][creature.pos[0] - 1] = 0
                killCount += 1




global sensoryList, internalList, actionList
# sensory neurons
sensoryList = []
sensoryList.append(Neuron("Random", "Rnd", randomSensory, "sensory", 1))
sensoryList.append(Neuron("Age", "Age", ageSensory, "sensory", 2))
sensoryList.append(Neuron("North", "DiN", northDistance, "sensory", 3))
sensoryList.append(Neuron("South", "DiS", southDistance, "sensory", 4))
sensoryList.append(Neuron("East", "DiE", eastDistance, "sensory", 5))
sensoryList.append(Neuron("West", "DiW", westDistance, "sensory", 6))
sensoryList.append(Neuron("Coat", "Ct", hasCoat, "sensory", 7))
sensoryList.append(Neuron("Forward", "Fw", creatureForward, "sensory", 8))

# internal neuron
internalList = []
internalList.append(Neuron("internal1", "N1", internalCalculation, "internal", 1))
internalList.append(Neuron("internal2", "N2", internalCalculation, "internal", 2))
internalList.append(Neuron("internal3", "N3", internalCalculation, "internal", 3))

# action neurons
actionList = []
actionList.append(Neuron("Default", "Def", defaultAction, "action", 0))
actionList.append(Neuron("Up", "MU", moveUp, "action", 1))
actionList.append(Neuron("Down", "MD", moveDown, "action", 2))
actionList.append(Neuron("Left", "ML", moveLeft, "action", 3))
actionList.append(Neuron("Right", "MR", moveRight, "action", 4))
actionList.append(Neuron("Random", "MRn", moveRandom, "action", 5))
actionList.append(Neuron("Coat", "MCo", makeCoat, "action", 6))
#actionList.append(Neuron("Away", "AFW", awayFromWall, "action", 7))
actionList.append(Neuron("Follow", "Fol", followCreature, "action", 8))
actionList.append(Neuron("Forward", "Fw", goForward, "action", 9))
#actionList.append(Neuron("Kill", "Kll", kill, "action", 10))

global gridX, gridY, numCreatures, numOfConnections, creatures, grid, steps, currStep, genNum, mutation, buildWall, wallLenght, wallGeneration, wallStart, wallDistance
gridX = 45
gridY = 45
numCreatures = 100
numOfConnections = 10
creatures = []
mutation = 20
buildWall = False
wallLenght = 25
wallGeneration = 21
wallStart = 10
wallDistance = 10

global skip
skip = False

if gridX * gridY < numCreatures:
    print("Too many creatures for the grid")
    exit()

global killCount
killCount = 0

grid = []
steps = 300
currStep = 0
genNum = 1

global aliveStartX, aliveStartY, aliveEndX, aliveEndY
aliveStartX = 0
aliveStartY = 0
aliveEndX = 300
aliveEndY = 300

for i in range(gridY):
    column = []
    for j in range(gridX):
        column.append(0)
    grid.append(column)

positions = []
if genNum >= wallGeneration:
    if buildWall:
        for i in range(wallStart, wallStart + wallLenght):
            positions.append([wallDistance, i])
            grid[i][wallDistance] = "w"
for i in range(numCreatures):
    genes = []
    for j in range(numOfConnections):
        genes.append(generateRandomHex(8))
    pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
    while pos in positions:
        pos = [random.randrange(0, gridX), random.randrange(0, gridY)]
    creatures.append(Creature(pos, genes, defaultAction, i, len(internalList)))

for i in creatures:
    grid[i.pos[1]][i.pos[0]] = i


dpg.create_context()
dpg.create_viewport(title='Custom Title', width=1000, height=700)

with dpg.window(label='Grid', width=1000, height=1000) as gridWin:

    global simArea
    simArea = None
    """
    with dpg.drawlist(width=920, height=920) as simArea:
        dpg.draw_rectangle((10, 10), (910, 910), color=(255, 255, 255))
        dpg.draw_rectangle((aliveStartX+10, aliveStartY+10), (aliveEndX+10, aliveEndY+10), color=(0, 255, 0), fill=(0, 255, 0), parent=simArea)
    """
    generationText = dpg.add_text("Generation: " + str(genNum))
    dpg.add_button(label="Step", callback=step)
    dpg.add_button(label="Play", callback=playGeneration, pos=(50, 50))
    dpg.add_button(label="Next Gen", callback=nextGeneration, pos=(92, 50))
    dpg.add_button(label="Skip", callback=genSkip, pos=(200, 50))
    dpg.add_button(label="Fast", callback=fastGens, pos=(500, 50))
    gensForSkip = dpg.add_input_text(default_value=50, pos=(250, 50), width=50)
    showIdsCb = dpg.add_checkbox(label="Show ids", default_value=False, pos=(310, 50))
    dpg.add_button(label="Brains", callback=generateBrains, pos=(400, 50))
    dpg.add_button(label="Genes Graph", callback=genesGraph, pos=(550, 50))

        



updateGrid()
#displayGrid()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()