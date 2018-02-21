"""Contains a class that represent connections between populations
"""

import numpy as np
import sys
import warnings

class DeviceConnections():
    """Class that represent connections between populations
    """
    
### ===========================================================================
    def __init__(self, sourcePop, targetPop, i = None, j = None, w = None, synapsesObj = None):
        """Return a new DeviceConnections object

Manual connection works as brian2 one. See this link: <http://brian2.readthedocs.io/en/2.0rc/user/synapses.html>

Parameters:
    sourcePop (DevicePopulation obj): population that represent the source of the connection
    targetPop (DevicePopulation obj): population that represent the destination of the connection
    i (array, int): list of indexes of the source neurons to be connected (can be also a single value)
    j (array, int): list of indexes of the destination neurons to be connected (can be also a single value)
    w (array, int): list of connection weights
    synapseObj (Synapses obj, optional): brian2 synapse object containing all the connections

Pay attention that synapseObj overwrite both connections specified with i and j, and weights w
"""

        # Save variables
        self.sourcePop = sourcePop
        self.targetPop = targetPop
        self.synapsesObj = synapsesObj
        
        # Use synapses connection indexes and weights if required
        if synapsesObj is not None:
            self.i = synapsesObj.i
            self.j = synapsesObj.j
            self.weights = synapsesObj.w
        elif (i is not None) & (j is not None) & (w is not None):
            self.i = i
            self.j = j
            self.weights = w
        else:
            errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(self.sourcePop.name, self.targetPop.name)
            errorString += "insufficient parameters: specify valid i, j, w or a valid synapseObj"
            raise NameError(errorString)
        
        # Sweep over all connections indexes and retrieve neurons
        self.sourceNeurons = []
        self.targetNeurons = []
        
        # If there is only one element, put it in a list
        if isinstance(self.i, int):
            self.i = [self.i]
        if isinstance(self.j, int):
            self.j = [self.j]
        if isinstance(self.weights, int):
            self.weights = [self.weights]

        for sourceIndex, targetIndex in zip(self.i, self.j):
            self.sourceNeurons.append(self.sourcePop.neurons[int(sourceIndex)])
            self.targetNeurons.append(self.targetPop.neurons[int(targetIndex)])