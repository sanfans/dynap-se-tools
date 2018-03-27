"""The module contains functions that permit to create networks of neurons and write connections on a .txt file.
This last one can be used by cAER NETPARSER module to implement them in DYNAP-se
"""

from DYNAPSETools.classes.DevicePopulation import DevicePopulation
from DYNAPSETools.classes.DeviceConnections import DeviceConnections

### ===========================================================================
def write_connections(*connections_lists, fileName = "network.txt"):
    """Write on a .txt file the network connections, ready to be uploaded to the final device.

Parameters:
    *connection_lists (list of connections): Contains the list of all the connections lists that must be written in the output file
    fileName (string): Name of the output .txt file

Note:
    This function write for each connection an header containing:

    - A separator: '#!======================================== '
    - A string with the name of the two populations that are connected

    This strings will be printed in the log when loading the network inside Dynap-se. For this reason is highly recommended
    to write meaningful names for the populations.
    
    Remember to put the * on the list when calling the function (see example).

Example:
    - Write a list of 2 connections to the out .txt file::

        _conn1 = DeviceConnections(...) # First connections
        _conn2 = DeviceConnections(...) # Second connections
        allConnections = (_conn1,
                          _conn2)
        fileName = "workingNetwork.txt"
        write_connections(*allConnections, fileName = fileName)
"""
    
    with open(fileName, 'w') as f:
        # Sweep over all the dictionary containing the connections
        for connections in connections_lists:
            # Write header
            f.write('#!======================================== ') # Separator
            f.write('Connecting {}->{}\n'.format(connections.sourcePop.name, connections.targetPop.name)) # Title of the connections

            # Write connections
            # In case you specified a connection type, use that. Otherwise, use the neuron type
            if connections.connTypes is not None:
                for srcNeuron, destNeuron, connType, weight in zip(connections.sourceNeurons,
                                                               connections.targetNeurons,
                                                               connections.connTypes,
                                                               connections.weights):
                    f.write('{}->{}-{}-{}\n'.format(srcNeuron.create_neuron_string(),
                                                    connType,
                                                    int(weight),
                                                    destNeuron.create_neuron_string()))
            else:
                for srcNeuron, destNeuron, weight in zip(connections.sourceNeurons,
                                                         connections.targetNeurons,
                                                         connections.weights):
                    f.write('{}->{}-{}-{}\n'.format(srcNeuron.create_neuron_string(),
                                                    srcNeuron.neuronType,
                                                    int(weight),
                                                    destNeuron.create_neuron_string()))