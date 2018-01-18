"""Contains a class that represent a neuron in the device"""

class Neuron():
    """Class that represent a neuron in the device
    """
    
    def __init__(self, chip_id, core_id, neuron_id, neuronType):
        """Return a new Neuron object

Parameters:
    chip_id (int): Chip number of the neuron
    core_id (int): Core number of the neuron
    neuron_id (int): Neuron number of the neuron
    neuronType (int): Type of Neuron (fast/slow, excitatory/inhibitory)
"""
        
        self.neuronType = neuronType
        self.weight = 0
        self.freeCAM = 64
        self.freeSRAM = 3
        self.chip_id = chip_id
        self.core_id = core_id
        self.neuron_id = neuron_id
        
### ===========================================================================
    def create_neuron_string(self):
        """Crete the connection neuron string (UxxCxxNxxx) from chip, core and neuron id
        Includes also synaptic type
        
        EX: chip_id = 0; core_id = 0; neuron_id = 1 /// return -> U00C00N001"""
            
        outString = "U{:02d}C{:02d}N{:03d}".format(self.chip_id, self.core_id, self.neuron_id)
        return outString