""" The module contains functions that allows to retrieve and display output .aedat files
"""

import struct
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from DYNAPSETools.classes.EventsSet import EventsSet

### ===========================================================================
def import_events(fileName):
    """Read events from the from cAER aedat 3.0 file format

OUTPUT FORMAT EXAMPLE
::

    VECT POSITION -> |       0       |        1       |       2       |
    chip_id_tot   -> |  chip 0       |  chip 1        |  chip 3       |
    core_id_tot   -> |  core 0       |  core 3        |  core 1       |
    neuron_id_tot -> |  neuron 1     |  neuron 100    |  neuron 255   |
    ts_tot        -> |  time 150000  |  time 15068    |  time 150127  |
        
the same for special events

Parameters:
    fileName (string): Name (with path) of the source .aedat file

Returns:
    obj EventsSet: A set containing the events imported from the file
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
        
OUTPUT FORMAT EXAMPLE
::

    VECT POSITION -> |       0       |        1       |       2       |
    chip_id_tot   -> |  chip 0       |  chip 1        |  chip 3       |
    core_id_tot   -> |  core 0       |  core 3        |  core 1       |
    neuron_id_tot -> |  neuron 1     |  neuron 100    |  neuron 255   |
    ts_tot        -> |  time 150000  |  time 15068    |  time 150127  |
        
the same for special events

Parameters:
    file (obj file handle): handle of the recording file
    debug (bool, optional): print debug data

Returns:
    (tuple): tuple containing:

        - **core_id_tot** (*list, int*): Contains the core id of the events in the packet
        - **chip_id_tot** (*list, int*): Contains the chip id of the events in the packet
        - **neuron_id_tot** (*list, int*): Contains the neuron id of the events in the packet
        - **ts_tot** (*list, float*): Contains the time of the events in the packet
        - **spec_type_tot** (*list, int*): Contains the types of the special events in the packet
        - **spec_ts_tot** (*list, float*): Contains the time of special events in the packet
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

### ===========================================================================
def plot_firing_rate(timeSteps, neuronsFireRate, ax = None, enPlot3d = False, enImshow = False):
        """Plot the firing rate of every neuron present in the chip
        
It is available a 3d view and a Imshow view

Parameters:
    timeSteps (array, float): Time steps in which firing rate has been calculated
    neuronsFireRate (2D array, float): Contain firing rate for every neuron and for every time step
    ax (ax handle, optional): Plot graph on this handle
    enPlot3d (bool, optional): Activate 3D visualization
    enImshow (bool, optional): Activate ImShow visualization

Returns:
    (tuple): tuple containing:

        - **figList** (*list, fig handles*): To modify properties of the figure
        - **axList** (*list, ax handles*): To modify properties of the plot
"""
        
        fig = None

        # If no subplot is specified, create new plot
        if ax == None: 
            fig = plt.figure()
            ax = fig.add_subplot(111)

        figList = []
        axList = []

        neuronsVect = np.array([(0, 256, 'g'), (256, 512, 'm'), (512, 768, 'r'), (768, 1024, 'y')])
        
        # Plot
        for minN, maxN, color in neuronsVect:
            ax.plot(timeSteps, np.transpose(neuronsFireRate[int(minN):int(maxN)]), marker = 'o', color = color)
        # Append plot handles
        axList.append(ax)
        figList.append(fig)
        
        # Plot a 3d view of the firing rate
        if enPlot3d == True:
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111, projection='3d')
            for minN, maxN, color in neuronsVect:
                X, Y = np.meshgrid(timeSteps, np.arange(int(minN), int(maxN)))
                Z = np.array(neuronsFireRate[int(minN):int(maxN)])
                ax2.plot_wireframe(X, Y, Z, rstride=1, cstride=1, color = color)
            # Append plot handles
            figList.append(fig2)    
            axList.append(ax2)
        
        # Plot the imshow of the firing rates 
        if enImshow == True:
            fig3 = plt.figure()
            ax3 = fig3.add_subplot(111)
            im = ax3.imshow(neuronsFireRate, cmap = 'hot', aspect='auto')
            plt.colorbar(im, orientation = 'vertical')
            # Append plot handles
            figList.append(fig3)
            axList.append(ax3)

### ===========================================================================        
def plot_settings(xlabel, ylabel, enLegend = True, zlabel = None, title = None):
    if title != None:
        plt.title(title)
    plt.xlabel(xlabel)  
    plt.ylabel(ylabel)
    plt.grid(b=True, which='major', color='k', linestyle='-')
    plt.grid(b=True, which='minor', color='r', linestyle='-', alpha=0.2)
    plt.minorticks_on()
    if enLegend:
        plt.legend(loc = 1)
    plt.show()