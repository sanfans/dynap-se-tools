"""Contains a class that represent a population of neuron in the device
"""

import numpy as np
import sys
import warnings
from DYNAPSETools.classes.DeviceNeuron import DeviceNeuron
from DYNAPSETools.parameters.dynapseParam import dynapseNeuronTypes, dynapseStructure

class DevicePopulation():
    """Class that represent a population of neuron with certain characteristics
    """
    
### ===========================================================================
    def __init__(self, neuronsObj = None, name = "Population", chip_id = 0, core_id = 0, start_neuron = 0, size = 1, neurons_id = None, neuronsType = "fExc"):
        """Return a new DevicePopulation object

Parameters:
    neuronsObj (NeuronGroup obj): brian2 population object containing the neuron you want to create in Dynap-se
    name (string): Name of the population (useful for debug)
    chip_id (int): Chip id in which the population is located
    core_id (int): Core id in which the population is located
    start_neuron (int): Neuron id where to start allocating neurons for the population.
    size (int): Dimension of the population
    neurons_id (list of int): Permit to specify a list of neuron id that are chosen for the population.
    Pay attention that it will overwrite start_neuron and size
    neuronType (string):\n
    - sInh -> slow inhibitory (code 0)
    - fInh -> fast inhibitory (code 1)
    - sExc -> slow excitatory (code 2)
    - fExc -> fast excitatory (code 3)

All this parameters can also be not specified, look at the default values
"""
        
        # Set population parameters
        if neuronsObj != None:
            self.neuronsObj = neuronsObj
            self.name = neuronsObj.name
            self.size = neuronsObj.stop
        else:
            self.name = name
            self.size = size
        
        # Create neuron list
        self.neurons = np.array([])

        # If neurons are specified, generated them
        self.set_neurons(chip_id = chip_id, core_id = core_id, start_neuron = start_neuron,
                         neurons_id = neurons_id, neuronsType = neuronsType)

    def __getitem__(self, key):
        """Returns a new Population object

The new population neurons are taken from the original one, filtered according to key value

Parameters:
    key (list or slice): a slice or list of neuron index you want to take from the original population

Returns:
    DevicePopulation obj: Population obtained from the slicing
"""
        subPop = DevicePopulation()
        subPop.name = self.name
        subPop.neurons = self.neurons[key]
        return subPop

    def __setitem__(self, key, value):
        """Set a parameter inside the population

Parameters:
    key (string): name of the parameter\n
    - "name": new name for the population
    - "neuronsType": change type of all neurons

    value (according to key): value that must be set for key parameter
"""
        if key == "name":
            self.name = value
        elif key == "neuronsType":
            try:
                value = dynapseNeuronTypes[value]
            except:
                errorString = "Error in population {} , cannot decode neuron type: ".format(self.name)
                errorString += "Specified neuron type ({}) does not match any of default ones".format(neuronsType) 
                raise NameError(errorString)
            for neuron in self.neurons:
                neuron.neuronType = value
        else:
            errorString = "Error setting item of population {} , Failed to set it: ".format(self.name)
            errorString += "Parameter not present"
            raise NameError(errorString)

### ===========================================================================
    def set_neurons(self, chip_id = 0, core_id = 0, start_neuron = 0, neurons_id = None, neuronsType = "fExc"):
        """Permit to add neurons inside the population. Every new group of neurons is appended to the existing neuron list

If chip_id, core_id and neuron_id are not specified, they are set to the one belonging to the last neuron added to the population

Parameters:
    chip_id (int): Chip id in which the population is located
    core_id (int): Core id in which the population is located
    start_neuron (int): Neuron id where to start allocating neurons for the population.
    neurons_id (list of int): Permit to specify a list of neuron id that are chosen for the population.
    Pay attention that it will overwrite start_neuron and size
    neuronType (string):\n
    - sInh -> slow inhibitory (code 0)
    - fInh -> fast inhibitory (code 1)
    - sExc -> slow excitatory (code 2)
    - fExc -> fast excitatory (code 3)

Returns:
    array of obj Neurons: Neurons that has been added to the global population
"""
        
        population = np.array([])
        
        try:
            neuronsType = dynapseNeuronTypes[neuronsType]
        except:
            errorString = "Error in population {} , cannot decode neuron type: ".format(self.name)
            errorString += "Specified neuron type ({}) does not match any of default ones".format(neuronsType) 
            raise NameError(errorString)
        
        # Check if use neuron list of not
        if neurons_id is not None:
            if isinstance(neurons_id, int):
                neurons_id = [neurons_id]
            neurons = np.array(neurons_id)
        else:
            neurons = np.arange(start_neuron, start_neuron + self.size)
            
        # Sweep over all neurons
        for neuron_id in neurons:
            # Check if there is an overflow of neuron_id or core_id or chip_id
            # and increase core or chip accordingly
            structure = dynapseStructure
            incCoreId = int(neuron_id / structure["nNeuronsPerCore"])
            new_neuron_id = neuron_id % structure["nNeuronsPerCore"]
            new_core_id = core_id + incCoreId
            incChipId = int(new_core_id / structure["nCoresPerChip"])
            new_core_id = new_core_id % structure["nCoresPerChip"]
            new_chip_id = chip_id + incChipId
            
            # Print warnings when there is a change of chip or core
            if((incChipId > 0) | (incCoreId > 0)):
                warningString = ("Warning in population {}, Neuron id overflow: ").format(self.name)
                warningString += ("Neuron U{:d}C{:d}N{:d} trasformed to U{:d}C{:d}N{:d}").format(
                    chip_id, core_id, neuron_id, new_neuron_id, new_core_id, new_chip_id)
                warnings.warn(warningString)
            
            # Raise an error if the new chip_id is outside the limits of the chips 
            # note that virtual chip = deviceParam[0] is used for send inputs to chip from external
            if(new_chip_id >= structure["nChipPerDevice"]):
                if (chip_id != structure["nChipPerDevice"]):
                    errorString = "Error in population {} , String creation failed: ".format(self.name)
                    errorString += "Neuron U{:d}C{:d}N{:d} does not fit in the boundaries of the chips".format(chip_id, core_id, neuron_id)
                    raise NameError(errorString)
            
            # Create the neuron with the selected address and, eventually, type of synapse
            try:
                n = DeviceNeuron(new_chip_id, new_core_id, new_neuron_id, neuronsType)
                # Append neuron
                population = np.append(population, n)
            except:
                print(sys.exc_info()[0])
                raise
        
        # Update neurons and shape
        self.neurons = np.append(self.neurons, population)
        
        return population