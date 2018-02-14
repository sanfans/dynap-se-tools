# AUTHOR: roberto@ini.phys.ethz.ch or cattaroby93@gmail.com
#
# DATE OF CREATION: 15/12/2017

# DESCRIPTION: Tutorial to practise with created class

### =================== IMPORT PACKAGES ================================

import numpy as np
import matplotlib.pyplot as plt

# Import modules for create spike patterns, networks and analyse outputs
from DynapseNetGenerator import Population, connect_populations, write_connections
from SpikesGenerator import SpikesGenerator
from DynapseOutDecoder import DynapseOutDecoder

plt.close('all')

run0 = False
run1 = False
run2 = True

### =================== TUTORIAL ================================
# The tutorial aims to make the user use three modules that are useful when working with DYNAP-se:
# SpikesGenerator, DynapseNetGenerator, DynapseOutDecoder
# The first will be used to create input spike patterns that must be sent to DYNAP-se. More in detail a sinusoidal 
# wave will be encoded in the spikes of 2 virtual neurons (Up channel and Down channel). Other 2 virtual neurons will be used to make synchronization
# The second will be used to create the mapping between the virtual neurons and the physical one. More in detail 
# two populations of neurons are used: whole core 0 and whole core 1. The first will be connected to Up channel while the second one to Down channel.
# Other two neurons will receive the synchronization inputs from the virtual ones
# The third will be used to visualize results of the experiment. What will result is a spiking pattern that resemble to a sinusoidal wave

# ===================== GENERATION OF INPUTS
if run0 == True:
    spikeGen = SpikesGenerator(debug = False, fileName = "tutorialInputs.txt", figureIdx = None, isiBase = 900.0, importEvents = False)

    # Send an event to a address a neuron (neuron 3) in order to encode the START EXPERIMENT
    # In this case firePeriod is the initial delay of the spike
    spikeGen.sparse_events(virtualSourceCoreId = 0, neuronAddress = 3, coreDest = 15, firePeriod = 0.5)

    # Encode 1 period of 1Hz sinusoid in spikes on neuron 1 and 2 (all cores (coreDest = 15), source core 0) using the encoding by threshold
    # Threshold is set to 0.05
    tSig = np.arange(0, 1, 1e-6) 
    ySig = np.sin(2 * np.pi * 1 * tSig)
    spikeGen.threshold_encoder(virtualSourceCoreId = 0, neuronAddressUpCH = 1, neuronAddressDwCH = 2, coreDest = 15, 
                               threshold = 0.05, t = tSig, y = ySig, noiseVar = 0, initDelay = 1e-3, plotEn = True)

    # Send an event to address a neuron (neuron 4) in order to encode the STOP EXPERIMENT.
    spikeGen.sparse_events(virtualSourceCoreId = 0, neuronAddress = 4, coreDest = 15, firePeriod = 1e-3)

    # Plot spikes
    spikeGen.plot_spikes(title = "Tutorial inputs", myLabels = None)

    # Write stimulus file
    spikeGen.write_to_file()

# ===================== GENERATION OF NETWORK
elif run1 == True:
    # Defining chip parameters
    chipsPerDevice = 4
    coresPerChip = 4
    neuronsPerCore = 256
    chipParam = (chipsPerDevice, coresPerChip, neuronsPerCore)

    # Populations of virtual chip
    InStartTrigger = Population(chipParam = chipParam, name = "InStartTrigger",
                                chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 3)
    InUpCh = Population(chipParam = chipParam, name = "InUpCh",
                        chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 1)
    InDwCh = Population(chipParam = chipParam, name = "InDwCh",
                        chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 2)
    InStopTrigger = Population(chipParam = chipParam, name = "InStopTrigger",
                               chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 4)

    # Pools population
    StartTrigger = Population(chipParam = chipParam, name = "StartTrigger",
                              chip_id = 0, core_id = 2, neuronType = None, shape = None, neurons_id = 16)
    PoolUpCh = Population(chipParam, name = "PoolUpCh", size = 256,
                          core_id = 0, start_neuron = 0, neuronType = None, shape = None)
    PoolDwCh = Population(chipParam, name = "PoolDwCh", size = 256,
                          core_id = 1, start_neuron = 0, neuronType = None, shape = None)
    StopTrigger = Population(chipParam = chipParam, name = "StopTrigger",
                             chip_id = 0, core_id = 2, neuronType = None, shape = None, neurons_id = 64)
    # Connections
    InStartTrigger_To_StartTrigger = connect_populations(p1 = InStartTrigger, p2 = StartTrigger, connType = 'bernoulli', p = 1)
    InStopTrigger_To_StopTrigger = connect_populations(p1 = InStopTrigger, p2 = StopTrigger, connType = 'bernoulli', p = 1)
    InUpCh_To_PoolUpCh = connect_populations(p1 = InUpCh, p2 = PoolUpCh, connType = 'bernoulli', p = 1)
    InDwCh_To_PoolDwCh = connect_populations(p1 = InDwCh, p2 = PoolDwCh, connType = 'bernoulli', p = 1)

    # Write output file
    write_connections(InStartTrigger_To_StartTrigger, InStopTrigger_To_StopTrigger,
                      InUpCh_To_PoolUpCh, InDwCh_To_PoolDwCh,
                      fileName = "tutorialNetwork.txt")

# ===================== RETRIEVE EVENTS AND DISPLAY 
elif run2 == True:
    # Create Decoder object and plot raster of all events
    outDec = DynapseOutDecoder("tutorialOutputs.aedat")
    outDec.raster_plot(title = "All events")

    # Take only events of chip 0 ("None" means no filter) and plot raster
    outDec.filter_events(chip_id = 0, core_id = None, neuron_id = None)
    outDec.raster_plot(title = "Chip 0 events")

    # Filter events between start neuron fire and stop neuron fire and plot filtered events
    outDec.isolate_experiment(startTriggerNeuron = (2, 16), stopTriggerNeuron = (2, 64))
    outDec.raster_plot(title = "Experiment events (with triggers)") 

    # Filter away the start trigger and stop trigger neurons and plot filtered events
    outDec.filter_events(chip_id = 0, core_id = [0,1], neuron_id = None) 
    outDec.raster_plot(title = "Experiment events (without triggers)") 

    # Make some elaboration
    outDec.calculate_firing_rate(timeBin = 50e3) # Calculate firing rate matrix
    outDec.plot_firing_rate(title = "Firing rates", enImshow = True) # Plot firing rates