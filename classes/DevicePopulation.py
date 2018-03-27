"""Contains a class that represent a population of neuron in the device
"""

import numpy as np
import sys
import warnings
from DYNAPSETools.classes.DeviceNeuron import DeviceNeuron
from DYNAPSETools.parameters.dynapseParameters import dynapseNeuronTypes, dynapseStructure

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
    neurons_id (list, int): Permit to specify a list of neuron id that are chosen for the population.

Note:
    All this parameters can also be not specified, look at the **default values!**

    Remember that in Dynap-se there are 4 types of connections: fast excitatory, fast inhibitory, slow excitatory and slow inhibitory.
    They can be specified insert in neuronsType one of the following strings:

    - fast excitatory: "fExc"
    - slow excitatory: "sExc"
    - fast inhibitory: "fInh"
    - slow inhibitory: "sInh"

    This function is the first step for the creation of connections between neurons in Dynap-se board. There are two ways to procede:

    1. specifying a Brian2 neuron object containing a population that you want to *transport* to Dynap-se.
        Is necessary to specify, moreover, the position of the population in the board, i.e 
        chip_id, core_id, start_neuron and eventually the neuronsType. The name is automatically imported from the
        population one
    2. specifying only chip_id, core_id, start_neuron, size and neuronsType. In this case it is possible to create connections
        in Dynap-se that are not related to any Brian2 population. Useful for **control** connections.

    In both cases, it is possible to specify a list (or only one) of neurons in **neurons_id** (i.e. [1, 3, 5]).
    They represent the indexes of the physical neurons in a core in Dynap-se (still chip_id and core_id must be specified) and they
    have the priority with respect to **start_neuron** and **size**.

Note:
    It is also compatible with **NCSBrian2Lib (Neurons object)**

Examples:
    - Create a Device population of 2 neurons from brian2. Locate it in chip 0, core 1, starting from neuron 0 (type fast excitatory)::
    
        p1 = NeuronGroup(2, "dv/dt = -v/tau : volt", name = "p1") # define neuron group with brian2
        _p1 = DevicePopulation(neuronsObj = p1, chip_id = 0, core_id = 1,
                                start_neuron = 0, neuronsType = "fExc")

    - Create without using brian2, using automatic location from size::

        _p1 = DevicePopulation(chip_id = 0, core_id = 1, start_neuron = 0,
                                size = 2, neuronsType = "fExc",
                                name = "p1")

    - Create same population but specifying the position of each neuron::

        neurons = np.array([0, 1]) # Defining the two neurons positions
        _p1 = DevicePopulation(chip_id = 0, core_id = 1,
                                neurons_id = neurons, neuronsType = "fExc",
                                name = "p1")
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
    neurons_id (list, int): Permit to specify a list of neuron id that are chosen for the population.
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
        self.size = np.size(self.neurons)

        return population
