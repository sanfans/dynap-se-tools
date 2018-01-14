"""Contains a class that represent a population of neuron in the device
"""

import numpy as np
import sys
import warnings
from DYNAPSETools.classes.Neuron import Neuron

class Population():
    """Class that represent a population of neuron with certain characteristics
    """
    
### ===========================================================================
    def __init__(self, deviceParam, name, chip_id = 0, core_id = 0, start_neuron = 0, size = 0, neuronType = None, shape = None, neurons_id = None):
        """Return a new Population object

Parameters:
    deviceParam (tuple of ints (int, int, int)): Parameters of the device that is used (chipsPerDevice, coresPerChip, neuronsPerCore)
    name (string): Name of the population (useful for debug)
    chip_id (int): Chip id in which the population is located
    core_id (int): Core id in which the population is located
    start_neuron (int): Neuron id where to start allocating neurons for the population.
    size (int): Dimension of the population
    neuronType (string):\n
    - sInh -> slow inhibitory (code 0)
    - fInh -> fast inhibitory (code 1)
    - sExc -> slow excitatory (code 2)
    - fExc -> fast excitatory (code 3)

    shape (tuple of ints (int, int)): Shape of the population matrix (numRows, numColumns)
    neurons_id (list of int): Permit to specify a list of neuron id that are chosen for the population.
        Pay attention that it will overwrite start_neuron and size

All this parameters can also be not specified (except for deviceParam and name).
Neurons can be added in a second time
"""
        
        # Set population parameters
        self.deviceParam = deviceParam
        self.name = name

        # Initialize other parameters
        self.lastChipId = 0
        self.lastCoreId = 0
        self.lastNeuronId = 0
        self.shape = ()
        
        # Define neuron type dictionary
        # "sInh" -> slow inhibitory (code 0)
        # "fInh" -> fast inhibitory (code 1)
        # "sExc" -> slow excitatory (code 2)
        # "fExc" -> fast excitatory (code 3)
        self.neuronTypeDict = {"sInh": 0, "fInh": 1, "sExc": 2, "fExc": 3}
        
        # Create neuron list
        self.neurons = np.array([])

        # If neurons are specified, generated them
        if (size != 0) | (neurons_id != None):
            self.add_neurons(size, chip_id, core_id, start_neuron, neuronType, neurons_id)

        # If shape is specified, change shape of the neuron array
        if shape != None:
            self.change_population_shape(rows = shape[0], columns = shape[1])
        
### ===========================================================================
    def add_neurons(self, size, chip_id = None, core_id = None, start_neuron = None, neuronType = None, neurons_id = None):
        """Permit to add neurons inside the population. Every new group of neurons is appended to the existing neuron list

If chip_id, core_id and neuron_id are not specified, they are set to the one belonging to the last neuron added to the population

Parameters:
    size (int): Dimension of the population
    chip_id (int): Chip id in which the population is located
    core_id (int): Core id in which the population is located
    start_neuron (int): Neuron id where to start allocating neurons for the population.
    neuronType (string):\n
    - sInh -> slow inhibitory (code 0)
    - fInh -> fast inhibitory (code 1)
    - sExc -> slow excitatory (code 2)
    - fExc -> fast excitatory (code 3)
    neurons_id (list of int): Permit to specify a list of neuron id that are chosen for the population.
        Pay attention that it will overwrite start_neuron and size

Returns:
    array of obj Neurons: Neurons that has been added to the global population
"""
        
        population = np.array([])
        
        if neuronType != None:
            try:
                neuronType = self.neuronTypeDict[neuronType]
            except:
                errorString = "Error in population {} , cannot decode neuron type: ".format(self.name)
                errorString += "Specified neuron ({}) type does not match any of default ones".format(neuronType) 
                raise NameError(errorString)
        
        # Check if to restore last neuron address or start from a new neuron
        if chip_id == None:
            chip_id = self.lastChipId
        if core_id == None:
            core_id = self.lastCoreId
        if neurons_id != None:
            if isinstance(neurons_id, int):
                neurons_id = [neurons_id]
            neurons = np.array(neurons_id)
        elif start_neuron != None:
            neurons = np.arange(start_neuron, start_neuron + size)
        else:
            neurons = np.arange(self.lastNeuronId, self.lastNeuronId + size)
            
        # Sweep over all neurons
        for neuron_id in neurons:
            
            # Check if there is an overflow of neuron_id or core_id or chip_id
            # and increase core or chip accordingly
            incCoreId = int(neuron_id / self.deviceParam[2])
            new_neuron_id = neuron_id % self.deviceParam[2]
            new_core_id = core_id + incCoreId
            incChipId = int(new_core_id / self.deviceParam[1])
            new_core_id = new_core_id % self.deviceParam[1]
            new_chip_id = chip_id + incChipId
            
            # Print warnings when there is a change of chip or core
            if((incChipId > 0) | (incCoreId > 0)):
                warningString = ("Warning in population {}, Neuron id overflow: ").format(self.name)
                warningString += ("Neuron U{:d}C{:d}N{:d} trasformed to U{:d}C{:d}N{:d}").format(
                    chip_id, core_id, neuron_id, new_neuron_id, new_core_id, new_chip_id)
                warnings.warn(warningString)
            
            # Raise an error if the new chip_id is outside the limits of the chips 
            # note that virtual chip = deviceParam[0] is used for send inputs to chip from external
            if((chip_id != self.deviceParam[0]) & (new_chip_id >= self.deviceParam[0])):
                errorString = "Error in population {} , String creation failed: ".format(self.name)
                errorString += "Neuron U{:d}C{:d}N{:d} does not fit in the boundaries of the chips".format(chip_id, core_id, neuron_id)
                raise NameError(errorString)
            
            # Create the neuron with the selected address and, eventually, type of synapse
            try:
                if neuronType == None:
                    n = Neuron(new_chip_id, new_core_id, new_neuron_id, -1)
                else:
                    n = Neuron(new_chip_id, new_core_id, new_neuron_id, neuronType)
                # Append neuron
                population = np.append(population, n)
            except:
                print(sys.exc_info()[0])
                raise
        
        # Store index of the next neuron after the last, in order to restart from it with a new population
        self.lastChipId = new_chip_id
        self.lastCoreId = new_core_id
        self.lastNeuronId = new_neuron_id + 1
        
        # Update neurons and shape
        self.neurons = np.append(self.neurons, population)
        self.neurons = self.neurons.reshape((1, np.size(self.neurons)))
        self.shape = np.shape(self.neurons)
        
        return population
    
### ===========================================================================
    def define_neurons_types(self, frac, type):
        """Assign a neuron type to a fraction of the population neurons
        
Neuron are selected from the population according to a uniform distribution, from the one that have no type assigned yet.
If the fraction is bigger than the left number of neurons, all remaining neurons are selected.

Parameters:
    frac (float): Fraction of population subjected to type assignment
    type (string):\n
    - sInh -> slow inhibitory (code 0)
    - fInh -> fast inhibitory (code 1)
    - sExc -> slow excitatory (code 2)
    - fExc -> fast excitatory (code 3)

Print:
    It prints the actual population fraction that has been assigned to a certain type.
    Can be different to the desidered one due to rounding
"""
        
        remainingNeurons = np.array([neuron for neuron in self.neurons.flatten() if neuron.neuronType == -1])
        if np.size(remainingNeurons) == 0:
            errorString = ("Warning in population {}, All neurons has already a type: ").format(self.name)
            errorString += ("Fraction {:f} cannot be assigned to type {}").format(frac, type)
            raise NameError(errorString)
            
        np.random.shuffle(remainingNeurons)
        neuronsToTake = int(np.ceil(frac * np.size(self.neurons)))
        print("Information in population {}, Actual fraction of {:f} (asked for {:f}) assigned to {}".format(
            self.name, neuronsToTake / np.size(self.neurons), frac, type))

        for neuron in remainingNeurons[0:neuronsToTake]:
            neuron.neuronType = self.neuronTypeDict[type]

        if neuronsToTake > np.size(remainingNeurons):
            warningString = ("Warning in population {}, Insufficient number of neurons: ").format(self.name)
            warningString += ("Type {} has been assigned to fraction {:f} instead of {:f}").format(
                type, np.size(remainingNeurons) / np.size(self.neurons), frac)
            warnings.warn(warningString)
        
### ===========================================================================
    def print_population(self):
        """Permit to display the properties of the neuron in the population, with the specified population shape
        """
        
        print("\nPOPULATION {} NEURON TYPE MAP".format(self.name))
        for i in np.arange(self.shape[0]):
            for j in np.arange(self.shape[1]):
                print(self.neurons[i][j].neuronType, end = '')
            print('')
        
#        neuronStringList = []
#        for neuron in self.neurons.flatten():
#            neuronStringList.append(neuron.create_neuron_string(enSynType = True))
#        neuronStringList = np.reshape(np.array(neuronStringList), np.shape(self.neurons))      
#        print(neuronStringList)
#        return neuronStringList
             
### ===========================================================================
    def change_population_shape(self, rows, columns):
        """Permit to change the shape of the population array.

This could be really useful to abstract the theoretical population geometry
from the actual distribution of the neuron in the device

Parameters:
    rows (int): number of rows of the new population
    columns (int): number of columns of the new population
"""
        
        # New shape
        shape = (rows, columns)
        
        # Change shape
        try:
            self.neurons = self.neurons.reshape(tuple(shape))
            self.shape = shape
            
        except:
            errorString = "Error in population {} , Shape modification failed: ".format(self.name)
            errorString += "Specified shape ({:d},{:d}) not match with the population size ({:d})".format(shape[0],
                            shape[1], np.size(self.neurons))
            raise NameError(errorString)
