"""Contains a class that represent connections between populations
"""

import numpy as np
import sys
import warnings
from DYNAPSETools.parameters.dynapseParameters import dynapseNeuronTypes

class DeviceConnections():
    """Class that represent connections between populations
    """
    
### ===========================================================================
    def __init__(self, sourcePop, targetPop, connTypes = None, synapsesObj = None, i = None, j = None, w = None):
        """Return a new DeviceConnections object

Parameters:
    sourcePop (DevicePopulation obj): population that represent the source of the connection
    targetPop (DevicePopulation obj): population that represent the destination of the connection
    connTypes (string; array, string): type of the connections to be implemented (see below)
    synapseObj (Synapses obj): brian2 synapse object containing all the connections.
    i (array, int): list of indexes of the source neurons to be connected (can be also a single value)
    j (array, int): list of indexes of the destination neurons to be connected (can be also a single value)
    w (array, int): list of connection weights

Note:
    Remember that in Dynap-se there are 4 types of connections: fast excitatory, fast inhibitory, slow excitatory and slow inhibitory.
    They can be specified insert in connType one of the following strings:

    - fast excitatory: "fExc"
    - slow excitatory: "sExc"
    - fast inhibitory: "fInh"
    - slow inhibitory: "sInh"

    With this object is possible to connect neurons in two different ways. These ways are applied with the following order of priority:

    1. specifying a Brian2 synapse object containing the connections that must be performed.
        See this link: <http://brian2.readthedocs.io/en/2.0rc/user/synapses.html> for more details on it.
        It is necessary to specify just the source population, target population and the synapse object.
        The weights are extracted directly from this last one, EVEN IF THEY ARE NEGATIVE!
    2. specifying connection manually, writing the source connections neuron on i, the destination connection neurons on j
        and the weights on w. It is the same way used by Brian2 simulator, but less flexible. If you want more flexibility,
        consider using synapse object for the connection

    If a combination of the two methods is specified (i.e. synapse_object and w), the one with higher priority will be applied.

    If no connTypes is specified, the type of connection (excitatory/inihbitory, fast/slow) are determined by the type of
    the source neurons, in a biologically plausible way (a neuron has only synapses of the same type).
    If a connType is written, the connections assume all the specified type. In this way it is possible to create non
    biological connections, i.e. a neuron that is excitatory and inhibitory at the same time.

    connTypes can be also an array of strings. In this case, every connection can be either one of the type specified before

Note:
    It is also compatible with **NCSBrian2Lib (Connections object)**

Examples:
    - Create connections between two DevicePopulations using a Synapse object::
        
        p1 = NeuronGroup(10, ...) # Define populations...
        p2 = NeuronGroup(10, ...)
        syn = Synapses(p1, p2, ...) # define synapses with brian2
        syn.connect("i == j and i < 10") # connect first 10 to first 10
        syn.w = 1
        _p1 = DevicePopulation(p1, ...) # create device populations
        _p2 = DevicePopulation(p2, ...)
        devConn = DeviceConnections(_p1, _p2, synapsesObj = syn)

    - Another possibility is to specify i, j and w::

        i = np.arange(10) # Connect first 10 of p1
        j = np.arange(10) # To first 10 of p2
        w = np.ones(10) # with unitary weights
        devConn = DeviceConnections(_p1, _p2, i = i, j = j, w = w)

    - Create biologically plausible connections::

        _p1 = DevicePopulation(p1, ..., neuronsType = "fExc") # define population types
        _p2 = DevicePopulation(p2, ..., neuronsType = "fExc")
        devConn = DeviceConnections(_p1, _p2, synapsesObj = syn) # fast excitatory connections

    - Create not biologically plausible connections::

        devConn_exc = DeviceConnections(_p1, _p2, synapsesObj = syn) # fast excitatory connections
        devConn_inh = DeviceConnections(_p1, _p2, synapsesObj = syn,
                                        connTypes = "fInh") # fast inhibitory connections
        # Same populations with both excitatory and inhibitory connections
"""

        # Save variables
        self.sourcePop = sourcePop
        self.targetPop = targetPop
        self.synapsesObj = synapsesObj
        
        # Use synapses connection indexes and weights if required
        if synapsesObj is not None:
            self.i = synapsesObj.i
            self.j = synapsesObj.j
            # If "Synapse" type -> brian2 object
            # If not -> brian2 Library object
            try: self.weights = synapsesObj.w
            except: self.weights = synapsesObj.weight
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
        
        # If there is only one element, put it in a list and convert to array (to get rid of all units)
        try: iter(self.i)
        except: self.i = np.array([self.i])
        try: iter(self.j)
        except: self.j = np.array([self.j])
        try: iter(self.weights)
        except: self.weights = np.array([self.weights])
        else: self.weights = np.array(self.weights)

        if len(self.i) != len(self.j):
            errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(self.sourcePop.name, self.targetPop.name)
            errorString += "insufficient parameters: i and j have different dimensions. There should be an i and j value for each connection you want to make"
            raise NameError(errorString)
        elif len(self.weights) != len(self.i):
            errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(self.sourcePop.name, self.targetPop.name)
            errorString += "insufficient parameters: w has a different dimension than i and j. There must be a weight value for each connection"
            raise NameError(errorString)

        # Check if user specified connection types. If not, for now set to None
        # If specified only one, copy it for all connections
        # Convert connections from string to integer (format of connection type in Dynap-se)
        if connTypes is not None:
            if isinstance(connTypes, str):
                self.connTypes = [dynapseNeuronTypes[connTypes]] * len(self.i)
            else:
                self.connTypes = []
                for type in connTypes:
                    self.connTypes.append(dynapseNeuronTypes[type])
        else:
            self.connTypes = None

        for sourceIndex, targetIndex in zip(self.i, self.j):
            self.sourceNeurons.append(self.sourcePop.neurons[int(sourceIndex)])
            self.targetNeurons.append(self.targetPop.neurons[int(targetIndex)])