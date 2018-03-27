""" The module contains functions that allows to retrieve and display output .aedat files
"""

import struct
import numpy as np
from matplotlib import pyplot as plt
from DYNAPSETools.classes.EventsSet import EventsSet

### ===========================================================================
def import_events(fileName):
    """Read events from the from cAER aedat 3.0 file format

Parameters:
    fileName (string): Name (with path) of the source .aedat file

Returns:
    obj EventsSet: A set containing the events imported from the file

Note:
    Events has the following structure:

    +------------+------------+-----------+-----------+-----------+ 
    | Vect       | Event 0    |  Event 1  | Event 2   | Event ... |
    +============+============+===========+===========+===========+ 
    | chip_id    | 0          | 1         | 3         | ...       | 
    +------------+------------+-----------+-----------+-----------+ 
    | core_id    | 0          | 3         | 1         | ...       |
    +------------+------------+-----------+-----------+-----------+ 
    | neuron_id  | 1          | 100       | 255       | ...       | 
    +------------+------------+-----------+-----------+-----------+
    | ts         | 150000     | 150064    | 150128    | ...       |
    +------------+------------+-----------+-----------+-----------+
        
    the same structure is for special events

    Time is absolute (first value is not zero), and expressed in [us] units

Example:
    - Retrieve events from .aedat::
        
        set = import_events("recording.aedat") # event set of the recording
"""
       
    try:
        file = open(fileName, "rb")
    except:
        errorString = "Error while reading file {} , file doesn't exist: ".format(fileName)
        raise NameError(errorString)
        
    done_reading = False
    
    # skip comment header of file
    skip_header(file)
    
    # prepare lists
    core_id_tot = []
    chip_id_tot = []
    neuron_id_tot = []
    ts_tot  = []
    # special events
    spec_type_tot = []
    spec_ts_tot = []
    
    while(done_reading == False): # cycle on all the packets inside the file
        try:
            core_id, chip_id, neuron_id, ts, spec_type, spec_ts = read_packet(file)
            core_id_tot.extend(np.array(core_id))
            chip_id_tot.extend(np.array(chip_id))
            neuron_id_tot.extend(np.array(neuron_id))
            ts_tot.extend(np.array(ts))
            spec_type_tot.extend(np.array(spec_type))
            spec_ts_tot.extend(np.array(spec_ts))
        except NameError:
            file.close()
            done_reading = True
    
    
    # make all arrays
    core_id_tot = np.array(core_id_tot)
    chip_id_tot = np.array(chip_id_tot)
    neuron_id_tot = np.array(neuron_id_tot)
    ts_tot = np.array(ts_tot)

    return EventsSet(ts_tot, chip_id_tot, core_id_tot, neuron_id_tot)

### ===========================================================================
def skip_header(file):
    """Skip the standard header of the recording file

Parameters:
    file (obj file handle): handle of the recording file
"""
        
    line = file.readline()
    while line.startswith(b'#'):
        if ( line == b'#!END-HEADER\r\n'):
            break
        else:
            line = file.readline()
                
### ===========================================================================
def read_packet(file, debug = False):
    """Read DYNAP-se packet from cAER aedat 3.0 file format
     
Parameters:
    file (obj, file handle): handle of the recording file
    debug (bool, optional): print debug data

Returns:
    (tuple): tuple containing:

        - **core_id_tot** (*list, int*): Contains the core id of the events in the packet
        - **chip_id_tot** (*list, int*): Contains the chip id of the events in the packet
        - **neuron_id_tot** (*list, int*): Contains the neuron id of the events in the packet
        - **ts_tot** (*list, float*): Contains the time of the events in the packet
        - **spec_type_tot** (*list, int*): Contains the types of the special events in the packet
        - **spec_ts_tot** (*list, float*): Contains the time of special events in the packet

Note:
    Events has the following structure:

    +------------+------------+-----------+-----------+-----------+ 
    | Vect       | Event 0    |  Event 1  | Event 2   | Event ... |
    +============+============+===========+===========+===========+ 
    | chip_id    | 0          | 1         | 3         | ...       | 
    +------------+------------+-----------+-----------+-----------+ 
    | core_id    | 0          | 3         | 1         | ...       |
    +------------+------------+-----------+-----------+-----------+ 
    | neuron_id  | 1          | 100       | 255       | ...       | 
    +------------+------------+-----------+-----------+-----------+
    | ts         | 150000     | 150064    | 150128    | ...       |
    +------------+------------+-----------+-----------+-----------+
        
    the same structure is for special events

    Time is absolute (first value is not zero), and expressed in [us] units
"""
        
    # raise Exception at end of file
    data = file.read(28)
    if(len(data) <= 0):
        print("Read all data\n")
        raise NameError('END OF DATA')
    
    
    # read header
    eventtype = struct.unpack('H', data[0:2])[0]
    eventsource = struct.unpack('H', data[2:4])[0]
    eventsize = struct.unpack('I', data[4:8])[0]
    eventoffset = struct.unpack('I', data[8:12])[0]
    eventtsoverflow = struct.unpack('I', data[12:16])[0]
    eventcapacity = struct.unpack('I', data[16:20])[0]
    eventnumber = struct.unpack('I', data[20:24])[0]
    eventvalid = struct.unpack('I', data[24:28])[0]
    next_read = eventcapacity * eventsize  # we now read the full packet
    data = file.read(next_read)    
    counter = 0  # eventnumber[0]
    #spike events
    core_id_tot = []
    chip_id_tot = []
    neuron_id_tot = []
    ts_tot =[]
    #special events
    spec_type_tot =[]
    spec_ts_tot = []
    
    if(eventtype == 0):
        spec_type_tot =[]
        spec_ts_tot = []
        while(data[counter:counter + eventsize]):  # loop over all event packets
            special_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
            spec_type = (special_data >> 1) & 0x0000007F
            spec_type_tot.append(spec_type)
            spec_ts_tot.append(timestamp)
            if(spec_type == 6 or spec_type == 7 or spec_type == 9 or spec_type == 10):
                print (timestamp, spec_type)
            counter = counter + eventsize        
    elif(eventtype == 12):
        while(data[counter:counter + eventsize]):  # loop over all event packets
            aer_data = struct.unpack('I', data[counter:counter + 4])[0]
            timestamp = struct.unpack('I', data[counter + 4:counter + 8])[0]
            core_id = (aer_data >> 1) & 0x0000001F
            chip_id = (aer_data >> 6) & 0x0000003F
            neuron_id = (aer_data >> 12) & 0x000FFFFF
            core_id_tot.append(core_id)
            chip_id_tot.append(chip_id)
            neuron_id_tot.append(neuron_id)
            ts_tot.append(timestamp)
            counter = counter + eventsize
            if(debug):          
                print("chip id "+str(chip_id)+'\n')
                print("core_id "+str(core_id)+'\n')
                print("neuron_id "+str(neuron_id)+'\n')
                print("timestamp "+str(timestamp)+'\n')
                print("####\n")
    return core_id_tot, chip_id_tot, neuron_id_tot, ts_tot, spec_type_tot, spec_ts_tot

### ===========================================================================
def plot_events(eventsSetList):
    """Raster plot of events included in the current EventsSet

Parameters:
    eventsSetList (list of obj EventSet): List of event sets that must be printed

Returns:
    (tuple): tuple containing:

        - **figList** (*list of fig handles*): To modify properties of the figure
        - **axList** (*list of ax handles*): To modify properties of the plot
        - **handlesList** (*list of lines handles*): To create custom legends
 
Example:
    - Retrieve and plot events from .aedat::
        
        set1 = import_events("recording1.aedat") # event set of the recording
        set2 = import_events("recording2.aedat") # event set of the recording
        figList, axList, handlesList = plot_events([set1, set2]) # plot events
        axList[0].set_title("Raster plot Recording 1")
        axList[0].set_xlabel('time [us]')
        axList[0].set_ylabel('Neuron id')
        axList[1].set_title("Raster plot Recording 2")
        axList[1].set_xlabel('time [us]')
        axList[1].set_ylabel('Neuron id')
"""

    # Initialize lists
    figList = []
    axList = []
    handlesList = []

    # Sweep over event list and plot every one of them
    for eventSet in eventsSetList:
        fig, ax, handles = eventSet.plot_events()
        figList.append(fig)
        axList.append(ax)
        handlesList.append(handles)

    return figList, axList, handlesList