"""Contains a class that represent connections between populations
"""

import numpy as np
import sys
import warnings
from DYNAPSETools.parameters.dynapseParam import dynapseNeuronTypes

class DeviceConnections():
    """Class that represent connections between populations
    """
    
### ===========================================================================
    def __init__(self, sourcePop, targetPop, connTypes = None, synapsesObj = None, i = None, j = None, w = None):
        """Return a new DeviceConnections object

It is possible to connect neurons in two different ways, in the following order of priority:
1. specifying a Brian2 synapse object. See this link: <http://brian2.readthedocs.io/en/2.0rc/user/synapses.html> for more details
2. specifying connection manually, writing i, j and w. Is the same way used by Brian2 simulator

If more than one method is specified, the one with higher priority will be applied.

Parameters:
    sourcePop (DevicePopulation obj): population that represent the source of the connection
    targetPop (DevicePopulation obj): population that represent the destination of the connection
    connTypes (string): type of the connections to be implemented (see below)
    synapseObj (Synapses obj): brian2 synapse object containing all the connections
    i (array, int): list of indexes of the source neurons to be connected (can be also a single value)
    j (array, int): list of indexes of the destination neurons to be connected (can be also a single value)
    w (array, int): list of connection weights

In Dynap-se there are 4 types of connections: fast excitatory, fast inhibitory, slow excitatory and slow inhibitory.
They can be specified insert in connType one of the following strings:
    - fast excitatory: "fExc"
    - slow excitatory: "sExc"
    - fast inhibitory: "fInh"
    - slow inhibitory: "sInh"
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
            errorString += "insufficient parameters: specify a valid synapseObj or valid i, j, w or "
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

        # Check if user specified connection types. If not, for now set to None
        # If specified only one, copy it for all connections
        # Convert connections from string to integer (format of connection type in Dynap-se)
        if connTypes is not None:
            if isinstance(connType, str):
                self.connTypes = [dynapseNeuronTypes[self.connTypes]] * len(self.i)
            else:
                self.connTypes = []
                for type in connTypes:
                    self.connTypes.append(dynapseNeuronTypes[connType])
        else:
            self.connTypes = None

        for sourceIndex, targetIndex in zip(self.i, self.j):
            self.sourceNeurons.append(self.sourcePop.neurons[int(sourceIndex)])
            self.targetNeurons.append(self.targetPop.neurons[int(targetIndex)])