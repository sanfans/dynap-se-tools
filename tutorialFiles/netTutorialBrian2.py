###############################################################################
###############################################################################
# THIS FILE CONTAINS ALL INSTRUCTIONS THAT ARE EXPLAINED IN THE TUTORIAL
# ON THE WEB SITE OF THE REPOSITORY. FOLLOW THAT TO HAVE A COMPLETE EXPLANATION
###############################################################################
###############################################################################

import DYNAPSETools.dynapseNetGenerator as DNG
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0) # Set seed for the random number generation
plt.close("all") # Close all the plots that has been created before

U, C, N = 4, 0, 1
size = 1
InputLayer = DNG.DevicePopulation(name = "InputLayer",
                                   chip_id = U, core_id = C, start_neuron = N,
                                   size = size, neuronsType = "fExc")

U, C, start_neuron = 0, 1, 0
size = 10
MiddleLayer = DNG.DevicePopulation(name = "MiddleLayer",
                                   chip_id = U, core_id = C, start_neuron = start_neuron,
                                   size = size)

neuronsIndexes = [5, 6, 7, 8, 9] # Choose neurons
MiddleLayer[neuronsIndexes]["neuronsType"] = "fInh" # Set to fast inhibitory

########## For random distribution of neurons type
#populationIndexes = np.arange(0, size) # From 0 to size - 1
#neuronsIndexes = np.random.permutation(populationIndexes) # Get a shuffled list
#neuronsIndexes = neuronsIndexes[:int(size / 2)] # Take half of them
#MiddleLayer[neuronsIndexes]["neuronsType"] = "fInh" # Set to fast inhibitory

U, C = 0, 1
N = [16, 32]
OutputLayer = DNG.DevicePopulation(name = "OutputLayer",
                                   chip_id = U, core_id = C, neurons_id = N,
                                   neuronsType = "fExc")

size = 10 # 10 connections
i = np.zeros(size) # i = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] -> the only input neuron
j = np.arange(size) # j = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] -> all MiddleLayer neurons
w = np.ones(size) # all weights equal to 1
InputLayerToMiddleLayer = DNG.DeviceConnections(sourcePop = InputLayer,
                                                targetPop = MiddleLayer,
                                                i = i, j = j, w = w)

i =  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # All Middle neurons
j = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1] # Half to 0 and half to 1
w = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # all weights equal to 1
MiddleLayerToOutputLayer = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 i = i, j = j, w = w)
i =  [0, 1, 2, 3, 4] # All Middle neurons
j = [1, 1, 1, 1, 1] # Half to 0 and half to 1
w = [1, 1, 1, 1, 1] # all weights equal to 1
MiddleLayerToOutputLayer2 = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 i = i, j = j, w = w,
                                                 connTypes = "fInh")

DNG.write_connections(InputLayerToMiddleLayer, MiddleLayerToOutputLayer, MiddleLayerToOutputLayer2,
                      fileName = "NetGenTutorial.txt")