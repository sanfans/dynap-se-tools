"""The module contains functions that permit to  write a .txt file with coded inputs to DYNAP-se
"""

import matplotlib.pyplot as plt
from DYNAPSETools.classes.InputPattern import InputPattern

### ===========================================================================
def import_events(fileName, name = "ImportedPattern", isiBase = 90.0):
    """Import events from an outside stimulus txt file

Parameters:
    fileName (string): Path of .txt file from which events must be imported
    name (string, optional): Name of the imported event pattern (useful for debug purpouses)
    isiBase (int, optional): Time base of the input pattern, for time event generation.

        Every delay is represented as multiple of this base. Knowing that an isiBase = 90 correspond to 1 us
        a delay = 10 -> 10 * isiBase = 10 us. With isiBase = 900 a delay = 10 -> 10 * isiBase = 100 us

Returns:
    obj InputPattern: Set of events that has been imported from input file
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
def plot_spikes(*inputPatternList):
    """Plot the spike stimuli
    
Parameters:
    *inputPatternList (list of obj InputPattern): Contains the patterns that must be plotted
"""
        
    # Create figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    handles = []

    duration = 0
    for idx, pattern in enumerate(inputPatternList):
        figtem, axtemp, handle = pattern.plot_spikes(color = "C" + str(idx), timeShift = duration, ax = ax)
        duration = duration + pattern.evaluate_duration()
        handles.append(handle)

    return fig, ax, handles

### ===========================================================================
def write_to_file(*input_patterns, fileName = "stimulus.txt"):
    """Write the stimulus on an output txt file and make controls to avoid overflow

Parameters:
    input_patterns (list of obj InputPattern): Contains all the patterns that should be written in the output file
    fileName (string, optional): Name of the output .txt file
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
                patternLenght = patternLenght + len(pattern.eventList)
                
                # Check lenght
                if(patternLenght > (2**15-1)):
                    errorString = "Error while writing pattern {}. Stimulus is too big, it will not fit in SRAM!".format(pattern.name)
                    raise NameError(errorString)
                else:
                    print("Current pattern lenght is {}. Remaining {} input events".format(patternLenght, (2**15-1) - patternLenght))
                    
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