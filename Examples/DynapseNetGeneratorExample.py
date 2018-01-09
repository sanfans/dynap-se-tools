# DESCRIPTION: functions that allows to retrieve and display output .aedat files

import matplotlib.pyplot as plt
import numpy as np
import sys
import DYNAPSETools.DynapseNetGenerator as netgen

# Initialize random seed
np.random.seed(1993)

chipsPerDevice = 4
coresPerChip = 4
neuronsPerCore = 256
deviceParam = (chipsPerDevice, coresPerChip, neuronsPerCore)

# INPUT POPULATION
InputUpCh = netgen.generate_population(deviceParam = deviceParam, name = "InputUpCh", 
                            chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 1)
InputDwCh = netgen.generate_population(deviceParam = deviceParam, name = "InputDwCh",
                            chip_id = 4, core_id = 0, neuronType = "fExc", neurons_id = 2)

## RESERVOIR POPULATION
Reservoir = netgen.generate_population(deviceParam = deviceParam, name = "Reservoir")
Reservoir.add_neurons(size = 25, chip_id = 0, core_id = 1, start_neuron = 1, neuronType = None)
# Shape as a rectangle of 5 by 5 neurons
Reservoir.change_population_shape(rows = 5, columns = 5)
# 80% excitatory, 20% inhibitory
Reservoir.define_neurons_types(frac = 0.8, type = "fExc")
Reservoir.define_neurons_types(frac = 0.2, type = "fInh")

## OUTPUT LAYER POPULATION
OutputLayerClass1 = netgen.generate_population(deviceParam = deviceParam, name = "OutputLayerClass1",
                                               chip_id = 0, core_id = 3, neuronType = "fExc", neurons_id = 16)
OutputLayerClass2 = netgen.generate_population(deviceParam = deviceParam, name = "OutputLayerClass2",
                                               chip_id = 0, core_id = 3, neuronType = "fExc", neurons_id = 32)

## PRINT POPULATIONS
InputUpCh.print_population()
InputDwCh.print_population()
Reservoir.print_population()
OutputLayerClass1.print_population()
OutputLayerClass2.print_population()

## CONNECTIONS
## =========== INPUT TO RESERVOIR
InUpChToReservoirConn = netgen.connect_populations(InputUpCh, Reservoir, connType = 'deterministic', f = 0.3)
InDwChToReservoirConn = netgen.connect_populations(InputDwCh, Reservoir, connType = 'deterministic', f = 0.3)

## =========== RECURRENT RESERVOIR
ReservoirRecConn = netgen.connect_populations(Reservoir, Reservoir, connType = 'gaussian', k = 1, r = 1)

## =========== RESERVOIR TO OUTPUT LAYER
ResToOutClass1Conn = netgen.connect_populations(Reservoir, OutputLayerClass1, connType = 'bernoulli', p = 1)
ResToOutClass2Conn = netgen.connect_populations(Reservoir, OutputLayerClass2, connType = 'bernoulli', p = 1)

## WRITE CONNECTIONS TO OUTPUT FILE
netgen.write_connections(InUpChToReservoirConn,
                         InDwChToReservoirConn,
                         ReservoirRecConn,
                         ResToOutClass1Conn,
                         ResToOutClass2Conn,
                         fileName = "DYNAPSETools/Examples/network.txt")