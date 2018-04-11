###############################################################################
###############################################################################
# THIS FILE CONTAINS ALL INSTRUCTIONS THAT ARE EXPLAINED IN THE TUTORIAL
# ON THE WEB SITE OF THE REPOSITORY. FOLLOW THAT TO HAVE A COMPLETE EXPLANATION
###############################################################################
###############################################################################

import DYNAPSETools.dynapseNetGenerator as DNG
import numpy as np
import matplotlib.pyplot as plt
from brian2 import start_scope, Network, NeuronGroup, Synapses,\
SpikeGeneratorGroup, SpikeMonitor, metre, second, volt, mV, ms, us,\
defaultclock, prefs

np.random.seed(0) # Set seed for the random number generation
plt.close("all") # Close all the plots that has been created before
prefs.codegen.target = "numpy"

############ BRIAN2 NETWORK
# Populations definition
brianInputLayer = NeuronGroup(1, model = "", name='brianInputLayer')
brianMiddleLayer = NeuronGroup(10, model = "", name='brianMiddleLayer')
brianOutputLayer = NeuronGroup(2, model = "", name='brianOutputLayer')

middleLayerInhNeurons = [5, 6, 7, 8, 9]

# Connections definition
brianInputLayerTobrianMiddleLayer = Synapses(brianInputLayer,
                                             brianMiddleLayer,
                                             model = "w : 1",
                                             name = "brianInputLayerTobrianMiddleLayer")
brianInputLayerTobrianMiddleLayer.connect(True)
brianInputLayerTobrianMiddleLayer.w = 1

brianMiddleLayerTobrianOutputLayer = Synapses(brianMiddleLayer,
                                              brianOutputLayer,
                                              model = "w : 1",
                                              name = "brianInputLayerTobrianMiddleLayer")
brianMiddleLayerTobrianOutputLayer.connect(condition = "i < 5 and j == 0")
brianMiddleLayerTobrianOutputLayer.connect(condition = "i >= 5 and j == 1")
brianMiddleLayerTobrianOutputLayer.w = 1

brianMiddleLayerTobrianOutputLayer2 = Synapses(brianMiddleLayer,
                                               brianOutputLayer, model = "w : 1",
                                               name = "brianMiddleLayerTobrianOutputLayer2")
brianMiddleLayerTobrianOutputLayer2.connect(condition = "i < 5 and j == 1")
brianMiddleLayerTobrianOutputLayer2.w = 1

############ CONVERSION TO DYNAPSE
# Place populations
U, C, N = 4, 0, 1
InputLayer = DNG.DevicePopulation(neuronsObj = brianInputLayer,
                                  chip_id = U, core_id = C,
                                  neurons_id = N,
                                  neuronsType = "fExc")

U, C, start_neuron = 0, 1, 0
size = 10
MiddleLayer = DNG.DevicePopulation(neuronsObj = brianMiddleLayer,
                                   chip_id = U, core_id = C,
                                   start_neuron = start_neuron)

# Set to fast inhibitory
MiddleLayer[middleLayerInhNeurons]["neuronsType"] = "fInh" 

# Convert connections
U, C = 0, 1
N = [16, 32]
OutputLayer = DNG.DevicePopulation(neuronsObj = brianOutputLayer,
                                   chip_id = U, core_id = C,
                                   neurons_id = N,
                                   neuronsType = "fExc")

InputLayerToMiddleLayer = DNG.DeviceConnections(sourcePop = InputLayer,
                                                targetPop = MiddleLayer,
                                                synapsesObj = brianInputLayerTobrianMiddleLayer)

MiddleLayerToOutputLayer = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 synapsesObj = brianMiddleLayerTobrianOutputLayer)

MiddleLayerToOutputLayer2 = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                  targetPop = OutputLayer,
                                                  synapsesObj = brianMiddleLayerTobrianOutputLayer2,
                                                  connTypes = "fInh")

DNG.write_connections(InputLayerToMiddleLayer, MiddleLayerToOutputLayer, MiddleLayerToOutputLayer2,
                      fileName = "NetGenTutorialBrian2.txt")