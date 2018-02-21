"""The module contains functions that permit to create networks of neurons and write connections on a .txt file.
This last one can be used by cAER NETPARSER module to implement them in DYNAP-se
"""

from DYNAPSETools.classes.DevicePopulation import DevicePopulation
from DYNAPSETools.classes.DeviceConnections import DeviceConnections

### ===========================================================================
def write_connections(*connections_lists, fileName = "network.txt"):
    """Write on a .txt file the network connections, ready to be uploaded to the final device.

Parameters:
    *connection_lists (list of connections): Contains the list of all the connections lists that must be written 
    in the output file
    fileName (string, optional): Name of the output .txt file
"""
    
    with open(fileName, 'w') as f:
        # Sweep over all the dictionary containing the connections
        for connections in connections_lists:
            # Write header
            f.write('#!======================================== ') # Separator
            f.write('Connecting {}->{}\n'.format(connections.sourcePop.name, connections.targetPop.name)) # Title of the connections

            # Write connections
            for srcNeuron, destNeuron, weight in zip(connections.sourceNeurons, connections.targetNeurons, connections.weights):
                f.write('{}->{}-{}-{}\n'.format(srcNeuron.create_neuron_string(),
                                                srcNeuron.neuronType,
                                                int(weight),
                                                destNeuron.create_neuron_string()))