"""The module contains functions that permit to create networks of neurons and write connections on a .txt file.
This last one can be used by cAER NETPARSER module to implement them in DYNAP-se
"""

import numpy as np
import sys
import collections
import warnings
from copy import copy
from matplotlib import pyplot as plt
from scipy.stats import bernoulli

from DYNAPSETools.classes.Population import Population

### ===========================================================================
def connect_populations(p1, p2, Plot = True, connType = 'bernoulli', **connParams):
    """Generate the connections between two different population of neurons

Parameters:
    p1 (obj Population): Source population
    p2 (obj Population): Destination population
    Plot (bool, optional): If True the connectivity between the two population is printed in the following way
        ::

            destination        
                n1  n2  n3  n4
            n1  x   3   1   x
            n2  x   x   x   x
            n3  x   x   x   x   source
            n4  x   3   3   3

        The number represent the connnection dynamics (x stays for no connection):\n
        - *sInh* -> slow inhibitory (code 0)
        - *fInh* -> fast inhibitory (code 1)
        - *sExc* -> slow excitatory (code 2)
        - *fExc* -> fast excitatory (code 3)

    connType (string, optional): Type of the connection:\n
        - *deterministic* : a specified fraction (f) of destination neurons is connected to the source neurons
        - *bernoulli* : connection between two neurons depend on a certain specified probability (p)
        - *gaussian* : connection between two neurons has a probability defined by this distribution

        ::

            P = k * np.exp(-(D**2) / (2*(r**2))) where:
            D is the Euclidean distance between two neurons
            r and k are two tuning parameters of the distribution

    connParams** (dict of param): connection parameters:\n
        - connType = "deterministic" -> f = ... ; f fraction of connection
        - connType = "bernoulli" -> p = ... ; p probability of connection
        - connType = "gaussian" -> k = ..., r = ... ; k and r parameters of the distribution

Returns:
    dict, obj Neuron : Dictionary containing all connections encoded as SOURCE NEURON (Key) = DESTINATION NEURON (Item)
"""
    
    # Initialize connections (p1 -> p2)
    if Plot:
        print("\nCONNECTIVITY MAP OF {}->{}".format(p1.name, p2.name))
    connections = {}
    connections[p1.name] = p2.name # Population connection strings
    
    p1Neurons = p1.neurons.flatten()
    p2Neurons = p2.neurons.flatten()
    
    print(connType + " " + str(len(connParams)))
    # If connection is matrix (connectivity matrix)
    if (connType == 'matrix') & (len(connParams) == 1):
        matrix = connParams.get('m')
        # Check if matrix dimensions are right
        if(np.shape(matrix)[0] != np.size(p1Neurons)):
            errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(p1.name, p2.name)
            errorString += "matrix lines {} must be equal to p1 size {}".format(np.shape(matrix)[0], np.size(p1.neurons))
            raise NameError(errorString)
        elif(np.shape(matrix)[1] != np.size(p2Neurons)):
            errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(p1.name, p2.name)
            errorString += "matrix columns {} must be equal to p2 size {}".format(np.shape(matrix)[1], np.size(p2Neurons))
            raise NameError(errorString)
        # Sweep over all extracted connections from matrix and apply them to neurons
        matrixConnections = np.argwhere(matrix != 0)
        for srcIdx, destIdx in matrixConnections:
            srcNeuron = p1Neurons[srcIdx]
            destNeuron = p2Neurons[destIdx]
            destNeuron.weight = int(matrix[srcIdx, destIdx])
            connections[copy(srcNeuron)] = copy(destNeuron)
            
        return connections
    
    # If Connection is deterministic (certain number of neuron connected)
    # must be handled in a different way
    if (connType == 'deterministic') & (len(connParams) == 1):
        neuronsToConnect = int(np.floor(connParams.get("f") * np.size(p2Neurons)))
        # Sweep over all source neurons
        for srcNeuron in p1Neurons:
            # Choose the neurons to connect
            neuronsIndexes = generate_n_rand_num(0, np.size(p2Neurons), neuronsToConnect)
            # Sweep over destination neurons
            for index, destNeuron in enumerate(p2Neurons):
                # if i have to connect, create an instance in connection dictionary
                if index in neuronsIndexes:
                    connections[copy(srcNeuron)] = copy(destNeuron)
                    if Plot:
                        print(srcNeuron.neuronType, end = '')
                elif Plot:
                    print('x', end = '')
            if Plot:
                print('')
        # No need to check the other connections type
        return connections

    # Sweep over all neurons of both populations (p2 receive connections)
    for srcNeuron in p1Neurons:
        for destNeuron in p2Neurons:
            try:
                # Calculate if connect or not according to prob distributions
                if (connType == 'bernoulli') & (len(connParams) == 1):
                    connect = bernoulli.rvs(connParams.get("p"))
                elif (connType == 'gaussian') & (len(connParams) == 2):
                    # Calculate positions of source and destination neurons
                    posP1 = np.where(p1.neurons == srcNeuron)
                    posP2 = np.where(p2.neurons == destNeuron)
                    # Euclidean distance D = sqrt((r2 - r1)^2 + (c2 - c1)^2)
                    # r is the row in the matrix, c is the column in the matrix
                    D = np.sqrt((posP2[0][0] - posP1[0][0])**2 + (posP2[1][0] - posP1[1][0])**2)
                    # Gaussian distribution probability P = k*e^(-D^2/(2*r^2))
                    k = connParams.get("k")
                    r = connParams.get("r")
                    P = k * np.exp(-(D**2) / (2*(r**2)))
                    # Use bernoulli to determine if connect or not
                    connect = bernoulli.rvs(P)
                else:
                    raise
                # If the random number created is 1 -> connect neurons (and update rams and cams), otherwise print 'x'
                if(connect):
                    connections[copy(srcNeuron)] = copy(destNeuron)
                    if Plot:
                        print(srcNeuron.neuronType, end = '')
                elif Plot:
                    print('x', end = '')
            except:
                errorString = "Error while connecting populations {} -> {}, Cannot connect: ".format(p1.name, p2.name)
                errorString += "Specified connection type or connection parameters not valid"
                raise NameError(errorString)
        if Plot:
            print('')
    return connections

### ===========================================================================
def write_connections(*connections_lists, fileName = "network.txt"):
    """Write on a .txt file the network connections, ready to be uploaded to the final device.

Parameters:
    *connection_lists (list of dict of connections): Contains the list of all the connections lists that must be written 
    in the output file
    fileName (string, optional): Name of the output .txt file
"""
    
    with open(fileName, 'w') as f:
        # Sweep over all the dictionary containing the connections
        for connections in connections_lists:
            srcPop = list(connections.keys())[0]
            destPop = list(connections.values())[0]
            f.write('#!======================================== ') # Separator
            f.write('Connecting {}->{}\n'.format(srcPop, destPop)) # Title of the connections
            # Write connections
            for srcNeuron, destNeuron in list(connections.items())[1:]:
                f.write('{}->{}-{}-{}\n'.format(srcNeuron.create_neuron_string(),
                        srcNeuron.neuronType,
                        destNeuron.weight,
                        destNeuron.create_neuron_string()))

### ===========================================================================
def change_seed(seed):
    """Change the seed of the random generator

Parameters:
    seed (int): New seed for the random generator
"""

    np.random.seed(seed)

### ===========================================================================
def generate_n_rand_num(min, max, n):
    """Generate n random numbers between a minimum and a maximum, with no repetitions

Parameters:
    min (int): Lower limit to the random number generation
    max (int): Upper limit to the random number generation
    n (int): Number of random numbers that must be generated

Returns:
    list, ints: A list containing n random numbers
"""

    neuronsIndexes = np.arange(min, max)
    np.random.shuffle(neuronsIndexes)
    return neuronsIndexes[0:n]