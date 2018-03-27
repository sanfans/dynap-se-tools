"""The module contains functions that permit to  write a .txt file with coded inputs to DYNAP-se
"""

import numpy as np
import matplotlib.pyplot as plt
from DYNAPSETools.classes.InputPattern import InputPattern

### ===========================================================================
def import_events(fileName, name = "ImportedPattern.txt", isiBase = 90.0):
    """Import events from an outside stimulus txt file

Parameters:
    fileName (string): Path of .txt file from which events must be imported
    name (string, optional): Name of the imported event pattern (useful for debug purpouses)
    isiBase (int, optional): Time base of the input pattern, for time event generation.

Returns:
    obj InputPattern: Set of events that has been imported from input file

Note:
    The isiBase is a parameter that tune the resolution of the spike generator inside Dynap-se. Spike timings values,
    in fact, are multiple of this base value. For this reason, the maximum and minimum interspike interval depends on isi value::

        min delay = isiBase / 90 MHz EQUIVALENT ROUGHLY TO: min delay = isiBase * 11.11 ns
        max delay = min delay * 2^16 EQUIVALENT TO: max delay = min delay * 65535
    
    The maximum isiBase that can be set is 1000 while the minimum is 1.

    Common isiBase values are::

        isiBase = 90    -> min delay = 1us, max delay = 65.535 ms
        isiBase = 900   -> min delay = 10us, max delay = 655.35 ms

    Important note: isiBase value must match the one set in Dynap-se software interface. An eventual different leads to
    difference in timings between the wanted pattern and the generated one.
"""
        
    # Open file and read all the lines
    f = open(fileName, 'r')
    lines = f.readlines()
        
    # Read the whole file and extract addresses and times
    try:
        pattern = InputPattern(name = name, isiBase = isiBase)
        # Create event starting from address and time values
        for line in lines:
            line = line.split()[0]
            line = line.split(',')
            pattern.add_manually_event(address = int(line[0]), time = int(line[1]))
        f.close()
    except:
        f.close()
        errorString = "Error while importing pattern {} from file {}, Impossible to open file".format(name, fileName)
        raise NameError(errorString)

    return pattern

### ===========================================================================
def plot_spikes(*inputPatternList, ax = None):
    """Plot the spike stimuli
    
Parameters:
    *inputPatternList (list of obj InputPattern): Contains the patterns that must be plotted

Returns:
    (tuple): tuple containing:
        
        - **fig** (*fig handles*): To modify properties of the figure
        - **ax** (*ax handles*): To modify properties of the plot
        - **handles** (*lines handles*): To create custom legends

Note:
    The spikes colors are chosen according to their index. That means that if you create a pattern
    made with 5 spikes coming from a certain virtual neuron and other 5 coming from another
    virtual neuron, they will have a different colors. Spikes with the same address have the same
    color.

Examples:
    - Create patterns and assign some spikes::

        # Create events patterns
        p1 = DSG.InputPattern("p1", isiBase = 900.0)
        p2 = DSG.InputPattern("p2", isiBase = 900.0)
        # insert some events in the patterns
        p1.multiple_events(virtualSourceCoreId = [0, 0],
                           neuronAddress = [1, 1],
                           coreDest = [15, 15],
                           firePeriod = [0.2, 0.2])
        p2.multiple_events(virtualSourceCoreId = [0, 0],
                           neuronAddress = [1, 1],
                           coreDest = [15, 15],
                           firePeriod = [0.2, 0.2])
     
    - Insert directly the patterns for the plot::

        fig, ax, handles = DSG.plot_spikes(p1, p2)
        
    - Create a list of patterns and plot it::

        patternList = [p1, p2]
        fig, ax, handles = DSG.plot_spikes(*patternList)
"""
        
    # Create figure
    if ax == None: 
        fig = plt.figure()
        ax = fig.add_subplot(111)

    # Create a pattern that will collect all the events in the inputPatternList
    sumPattern = InputPattern(name = "sumPattern", isiBase = inputPatternList[0].isiBase)
    
    # Sweep over the patterns and add events to the sumPattern
    for pattern in inputPatternList:
        sumPattern.eventList = np.append(sumPattern.eventList, pattern.eventList)

    # Plot
    fig, ax, handles = sumPattern.plot_spikes(timeShift = 0, ax = ax)
    
    return fig, ax, handles

### ===========================================================================
def write_to_file(*input_patterns, fileName = "stimulus.txt"):
    """Write the stimulus on an output txt file and make controls to avoid overflow

Parameters:
    *input_patterns (list of obj InputPattern): Contains all the patterns that should be written in the output file
    fileName (string, optional): Name of the output .txt file

Note:
    write_to_file function check also if the specified patterns respect some particular constraints:

    - the final pattern must not be bigger than 2^15 events -> it will not fit in the SRAM
    - the minimum and maximum delay constrains must be respected by every pattern.
        this vary according to the chosen isiBase
    - delay must be positive

Examples:
    - Create patterns and assign some spikes::

        # Create events patterns
        p1 = DSG.InputPattern("p1", isiBase = 900.0)
        p2 = DSG.InputPattern("p2", isiBase = 900.0)
        # insert some events in the patterns
        p1.multiple_events(virtualSourceCoreId = [0, 0],
                           neuronAddress = [1, 1],
                           coreDest = [15, 15],
                           firePeriod = [0.2, 0.2])
        p2.multiple_events(virtualSourceCoreId = [0, 0],
                           neuronAddress = [1, 1],
                           coreDest = [15, 15],
                           firePeriod = [0.2, 0.2])
     
    - Insert directly the patterns for the plot::

        DSG.write_to_file(p1, p2, fileName = "myName.txt)
        
    - Create a list of patterns and plot it::

        patternList = [p1, p2]
        DSG.write_to_file(*patternList, fileName = "myName.txt")
"""

    # Open file and write stimulus. Some controls are performed     
    with open(fileName, 'w') as f:
        # Sweep over all patterns that has been specified
        patternLenght = 0
        for pattern in input_patterns:
            errorString = ""
            try:
                print("Checking and writing pattern {}".format(pattern.name))
                # Check pattern
                print("Current pattern lenght is {}".format(len(pattern.eventList)))
                
                patternLenght = patternLenght + len(pattern.eventList)
                # Check lenght
                if(patternLenght > (2**15-1)):
                    errorString = "Error while writing pattern {}. Stimulus is too big, it will not fit in SRAM!".format(pattern.name)
                    raise NameError(errorString)
                else:
                    print("Cumulative pattern lenght is {}. Remaining {} events".format(patternLenght, (2**15-1) - patternLenght))
                    
                # Check maximum delay and if negative
                for idx, event in enumerate(pattern.eventList):
                    if(event.time > 2**16-1):
                        errorString = "Error while writing pattern {}. Event at position {} has a delay too big ({}).".format(
                            pattern.name, idx, event.time)
                        errorString += "Consider increasing isiBase unit"
                        raise NameError(errorString)
                    elif(event.time < 0):
                        errorString = "Error while writing pattern {}. Event at position {} has negative delay ({}).".format(
                            pattern.name, idx, event.time)
                        errorString += "Consider changing jitter distribution variance"
                        raise NameError(errorString)

                # If valid, write on output file
                for event in pattern.eventList:            
                    f.write(str(int(event.address))+','+str(int(event.time))+'\n')
                print("Pattern {} succesfully written\n".format(pattern.name))
            except:
                if errorString == "":
                    errorString = "Error while writing pattern {}, cannot write it".format(pattern.name)
                raise