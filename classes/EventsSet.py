# DESCRIPTION: contains a class that represent a set of DYNAP-se events

import numpy as np
from matplotlib import pyplot as plt

class EventsSet:
    """A set of DYNAP-se events
    """

    def __init__(self, ts, chip_id, core_id, neuron_id):
        """Return a new EventsSet object

Parameters
----------
ts : array_like, float. Times of events
chip_id : array_like, int. Chip number of events
core_id : array_like, int. Core number of events
neuron_id : array_like, int. Neuron number of events
"""

        self.ts = ts
        self.chip_id = chip_id
        self.core_id = core_id
        self.neuron_id = neuron_id

### ===========================================================================
    def filter_events(self, chip_id, core_id, neuron_id):
        """Return a EventsSet containing only the wanted events

Filter is specified selecting certain chip_id, core_id and neuron_id
It supports only one chip at a time (so chip_id must be a integer from 0 to 3)
It could single neuron data or data from range of neurons, indipendently from each core
If neuron_id is left as "None", all neurons are selected.
If core_id is left as "None", all cores are selected.

Parameters
----------
chip_id : int. For now is only possible to filter one chip
core_id : int or list of ints. Represent the cores included in the filter
neuron_id : int, list of ints or list of lists of ints. Represent the neurons included in the filter

Returns
-------
EventsSet object : A set containing the events resulting from the filtering

Examples
--------
- chip_id = 0, core_id = np.array([0, 1]), neuron_id = np.array([[0, 100], [100, 200]])
    take chip 0, neuron from 0 to 100 of core 0 and neurons from 100 to 200 on core 1
- chip_id = 1, core_id = None, neuron_id = None
    take all neurons in all cores of chip 1
- chip_id = 2, core_id = np.array([0, 1]), neuron_id = None
    take all neurons in cores 0 and 1 of chip 2
- chip_id = 3, core_id = 0, neuron_id = 3
    take traces of neuron 3 of core 0 in chip 3
- chip_id = 0, core_id = np.array([0, 1]), neuron_id = np.array([20, 127])
    take traces of neuron 20 of core 0 and neuron 127 of core 1, in chip 0
"""
        
        #Check the core_id input to find events correlated with it*/
        filter_core_id = np.zeros(len(self.core_id), dtype = bool) # Initialization to all false
        try: # If 'for' not fails -> multiple cores
            for current_id in core_id: # Take events for all the cores
                filter_core_id = filter_core_id | (self.core_id == current_id) 
        except: # If 'for' fails -> single core
            filter_core_id = filter_core_id | (core_id == None)| (self.core_id == core_id) # Take events only for a certain core
        
        # Check the neuron_id input to find events correlated with it*/    
        filter_neuron_id = np.zeros(len(self.neuron_id), dtype = bool) # Initialization to all false
        try: # If 'for' not fails -> multiple lists (or just one)
            for core_index, neuron_list in enumerate(neuron_id):
                try: # If 'for' not fails -> multiple neurons
                    for current_id in neuron_list: # Take events only for a certain neuron and a certain core
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (self.neuron_id == current_id))
                except: # If 'for' fails -> single neuron
                    try: # If it not fails means that core_id is a list, so we have a list of single neurons
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (neuron_list == None))
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id[core_index]) & (self.neuron_id == neuron_list))
                    except: # If it fails means that core_id is a number, so we have a single list of neurons
                        filter_neuron_id = filter_neuron_id | ((self.core_id == core_id) & (self.neuron_id == neuron_list))
        except:
            filter_neuron_id = filter_neuron_id | (neuron_id == None)| (self.neuron_id == neuron_id)
            
        # Combine all filters and apply them, getting only the events that has been selected*/    
        indx_neurons = (self.chip_id == chip_id) & filter_core_id & filter_neuron_id
        try:
            return EventsSet(self.ts[indx_neurons], self.chip_id[indx_neurons], self.core_id[indx_neurons], self.neuron_id[indx_neurons])
        except:
            errorString = "Error while filtering neuron events, no spikes found, check the constrains"
            raise NameError(errorString)

### ===========================================================================
    def isolate_events_sets(self, startTriggerNeuron, stopTriggerNeuron, maxNumber = None):
        """Isolate events between start trigger neuron and the stop trigger neuron
        
A good way to synchronize with DYNAP-se is using two neurons to trigger the start and the end of the experiment:
- send a spike to a neuron that will represent my starting trigger
- send the experiment input spikes after small delay (1 ms should be enough)
- send a spike to a neuron that will represent my ending trigger
Then this function can be used to filter all events but for the ones that are between this two neurons

Parameters
----------
startTriggerNeuron : tuple of ints (chip id, core id, neuron id). Neuron which events triggers the start of the experiment
stopTriggerNeuron : tuple of ints (chip id, core id, neuron id). Neuron which events trigger the end of the experiment
maxNumber : max number of experiments that can be extracted from the Set of events

Returns
-------
list of EventsSet objects : Each item represent a set of events included in one experiment

Examples
--------
- startTriggerNeuron = (0, 2, 64), stopTriggerNeuron = (0, 2, 128)
    take all experiments included between neuron 64 (chip id = 0, core id = 2) and neuron 128 (chip id = 0, core id = 2)
- startTriggerNeuron = (1, 3, 64), stopTriggerNeuron = (1, 3, 128), maxNumber = 5
    take up to 5 experiments included between neuron 64 (chip id = 1, core id = 3) and neuron 128 (chip id = 1, core id = 3)
"""
        
        # If absolute index, convert to tuple containing (core, neuron id)
        #if not isinstance(startTriggerNeuron, collections.Iterable):
        #    startTriggerCore = (int) (startTriggerNeuron / 256)
        #    startTriggerNeuron = (startTriggerCore, startTriggerNeuron % (256 * startTriggerCore))
        #if not isinstance(stopTriggerNeuron, collections.Iterable):
        #    stopTriggerCore = (int) (stopTriggerNeuron / 256)
        #    stopTriggerNeuron = (stopTriggerCore, stopTriggerNeuron % (256 * stopTriggerCore))
        
        # Find the index of the start trigger neurons or stop trigger neurons
        startTriggerIndexes = np.where((self.chip_id == startTriggerNeuron[0]) &
                                       (self.core_id == startTriggerNeuron[1]) &
                                       (self.neuron_id == startTriggerNeuron[2]))[0]
        stopTriggerIndexes = np.where((self.chip_id == stopTriggerNeuron[0]) &
                                      (self.core_id == stopTriggerNeuron[1]) &
                                      (self.neuron_id == stopTriggerNeuron[2]))[0]

        # Setup experiment list
        experiments = []

        # Sweep over all requested experiments number
        startTrigger = 0
        stopTrigger = 0

        # Initialize the number of experiments to be taken
        counter = 0
        if maxNumber == None:
            limit = 0
        else:
            limit = maxNumber

        while ((maxNumber == None) | (counter < limit)):
            try:
                # Calculate the start and stop trigger of the current experiment
                startTrigger = startTriggerIndexes[startTriggerIndexes >= stopTrigger][0] # Start trigger should happen after the previous end trigger
                stopTrigger = stopTriggerIndexes[stopTriggerIndexes >= startTrigger][0] # End trigger should happen after start trigger

                # Filter the spikes information according to the previous range (the +1 is in order to take also the trigger spike)
                ts_event = self.ts[startTrigger:(stopTrigger+1)]
                neuron_id_event = self.neuron_id[startTrigger:(stopTrigger+1)]
                core_id_event = self.core_id[startTrigger:(stopTrigger+1)]
                chip_id_event = self.chip_id[startTrigger:(stopTrigger+1)]

                # Append experiment and increment counter
                experiments.append(EventsSet(ts_event, chip_id_event, core_id_event, neuron_id_event))
                counter = counter + 1
            except:
                break;

        # Check if there are experiments in the list
        if len(experiments) == 0:
            errorString = "Error while extracting experiments, cannot find any valid one: "
            errorString += "Check start and stop trigger neurons, or maxNumber value"
            raise NameError(errorString)
        else:
            return experiments

### ===========================================================================
    def plot_events(self, ax = None):
        """Raster plot of events included in the current EventsSet

The colors has been chosen to be clearly visible and to match the DYNAP-se core color enconding:
- core 0: green
- core 1: magenta
- core 2: red
- core 3: yellow
Note that there is no distinguish between different chips events

Parameters
----------
title : string. Title of the current plot
ax : pyplot subplot object. Graph in which events will be plotted. If None, a new figure is created

Returns
-------
fig : figure handle of the created figure, if generated
ax : axis handle of the created plot
handles : list of handles of created line (every plot)
"""

        fig = None

        # If no subplot is specified, create new plot
        if ax == None: 
            fig = plt.figure()
            ax = fig.add_subplot(111)

        handles = []
        # Plot different cores with different colors
        for core in range(4):
            indx_core = np.where((self.core_id == core))[0] # Search for events of a core
            
            if core == 0:
                color = 'g'
            elif core == 1:
                color = 'm'
            elif core == 2:
                color = 'r'
            else:
                color = 'y'
                
            handle, = ax.plot(self.ts[indx_core], self.neuron_id[indx_core] + 256 * core, linestyle = 'None', marker = 'o', color = color)
            handles.append(handle)

        return fig, ax, handles

### ===========================================================================
    def calculate_firing_rate_matrix(self, numBins, totNeurons):
        """Derive a firing rate matrix starting from the current EventSet
        
Data have the following form:
TIME
- timeSteps -> [t0 t0+tBin t0+2tBin ... tn-tBin]
    tBin is the temporal step in which firing rate is evaluated (tBin = (tn - t0) / numBins))
- neuronsFireRate (fr stays for firing rate at a certain time step (0...1...2...ecc.)
    neuron0    fr0 fr1 fr2 ... frn
    neuron1    fr0 fr1 fr2 ... frn
    ...
    neuron1023 fr0 fr1 fr2 ... frn

Parameters
----------
numBins : int. Number of intervals in which firing rate must be evaluated
totNeurons : int. Maximum number of neurons for which firing rate is calculated

Returns
-------
timeSteps : array_like, float. Time steps in which firing rate has been calculated
neuronsFireRate: array of arrays, float. Contain firing rate for every neuron and for every time step
"""
        
        # Initialize vectors
        timeSteps = []
        #neuronSpikes = [[] for count in np.arange(totNeurons)]
        neuronsFireRate = [[] for count in np.arange(totNeurons)]
        absoluteNeurons = (self.chip_id * 1024) + (self.core_id * 256) + self.neuron_id

        # Calculate time bins
        timeBins, binSize = np.linspace(self.ts[0], self.ts[-1], numBins + 1, retstep = True)
        timeBins = [(timeBins[i], timeBins[i + 1]) for i in range(len(timeBins) - 1)]
        
        # Sweep over the time bins and calculate spikes and firing rate
        for timeBin in timeBins:
            timeSteps.append(timeBin[0])
            # Initialize to 0 the firing rate of all neurons
            for pos in np.arange(totNeurons): 
                #neuronSpikes[pos].append(0)
                neuronsFireRate[pos].append(0)
            # Find the spikes in the time Bin
            spanInterval = np.where((self.ts >= timeBin[0]) & (self.ts < timeBin[1]))[0]
            # Span the spikes and increment the spike counter in the neuron list
            for pos in spanInterval:
                #neuronSpikes[absoluteNeurons[pos]][-1] += 1
                try:
                    neuronsFireRate[absoluteNeurons[pos]][-1] += 1
                except:
                    pass
            for pos in range(totNeurons): # Do the average in all neurons
                #neuronFireRate[pos][-1] = neuronSpikes[pos][-1] / (binSize / 1e6)
                neuronsFireRate[pos][-1] = neuronsFireRate[pos][-1] / (binSize / 1e6)

        return np.array(timeSteps), np.array(neuronsFireRate)

### ===========================================================================
    def normalize(self):
        """Normalize the time of the current EventSet

The time of the first event is set to 0. The subsequent are changed accordingly

Returns
-------
EventsSet objects. A new normalized EventSet
"""
        return EventsSet(self.ts - self.ts[0], self.chip_id, self.core_id, self.neuron_id)