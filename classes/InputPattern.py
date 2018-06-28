"""Contains a class that represent a pattern of inputs to DYNAP-se
"""

import numpy as np
import matplotlib.pyplot as plt
from DYNAPSETools.classes.InputEvent import InputEvent

class InputPattern:
    """Class that represent a pattern of inputs to DYNAP-se
    """

    def __init__(self, name, isiBase = 90.0, dummyNeuron = None):
        """Returns a new InputPattern object

Parameters:
    name (string): Name of the pattern (useful for debug)
    isiBase (int): Time base for time event generation.

Note:
    isiBase parameter tune the minimum and the maximum inter-spike delay that can be created
    by FPGA spike generator. The general formula to evaluate this parameters is::
    
        resolution [s] = 1/90000000 Hz * isiBase
        maxDelay [s] = resolution * 2^16 = resolution * 65535

    Common used isiBase are 90 and 900::

        isiBase = 90
        resolution = 1 us
        maxDelay = 65,535 ms

        isiBase = 900
        resolution = 10 us
        maxDelay = 655,535 ms

    isiBase must be in the range [1, 1000]

    Note that the maximum delay stated by the isiBase can be overcomed using the freeNeuron.
    See "setFreeNeuron" function for more informations
"""

        self.name = name

        # Set spike base timing
        self.isiBase = isiBase # Base for the timing of the spikes
        self.isiForUs = 90.0 # ISI to have 1 us resolution
        self.isiRatio = self.isiBase / self.isiForUs
        self.maxDelay = 2**16-1 # In ISI base
        
        # Generate (address, time) event arrays
        self.eventList = np.array([])
        self.tSig = np.array([])
        self.ySig = np.array([])
        
        # Create dummyNeuron instance
        self.dummyNeuron = dummyNeuron
        
### ===========================================================================
    def single_event(self, virtualSourceCoreId, neuronAddress, coreDest, fireFreq = None, firePeriod = None, chipDest = 0):
        """Create a single address and time step for a specified neuron and a certain interspike interval
        
Parameters:
    virtualSourceCoreId (int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddress (int): Represent the address of the virtual neuron that will generate the event
    coreDest (int): (4 bit hot coded). Represent the destination cores in which the spike will be routed
    fireFreq (float, [Hz]): Firing frequency you want to achieve ; event delay is calculate as 1/frequency
    firePeriod (float, [s]): Event delay (after delay the event is generated)

Note:
    - virtualSourceCoreId must be in the range [0, 3]
    - neuronAddress must be in the range [0, 255]
    - coreDest is a 4 bit hot coded number, must be in the range [0, 15]

Examples:
    Initialize the pattern istantiating the object::

        pattern = InputPattern(name = "pattern", isiBase = 900)

    - send a single event with 0.1s delay from virtual neuron 0 of virtual core 0, to all physical cores::
            
            virtualSourceCoreId = 1
            neuronAddress = 0
            coreDest = 15
            pattern.single_event(virtualSourceCoreId, neuronAddress, coreDest, firePeriod = 0.1)

    - send a single event with 0.02s delay (50Hz) from virtual neuron 2 of virtual core 1, to physical cores 0 and 1::
    
            virtualSourceCoreId = 1
            neuronAddress = 2
            coreDest = 3 # 0011 -> core 0 and 1
            pattern.single_event(virtualSourceCoreId, neuronAddress, coreDest, fireFreq = 50)
"""

        if (firePeriod == None) & (fireFreq != None):
            time = np.round((1.0 / fireFreq ) * 1e+6 / self.isiRatio) #/*In ISI units*/
        elif (firePeriod != None) & (fireFreq == None):
            time = np.round(firePeriod * 1e+6 / self.isiRatio) #/*In ISI units*/
        else:
            errorString = "Error while creating event {}, specify or fire frequency or fire period: ".format(self.name)
            raise NameError(errorString)
            
        # If dummy neuron specified, insert them with maximum delay until the time is not < max allowed
        if self.dummyNeuron is not None:
            while(time > self.maxDelay):
                self.eventList = np.append(self.eventList, InputEvent(self.dummyNeuron[0], self.dummyNeuron[1],
                                                                      coreDest = 0, time = self.maxDelay, chipDest = 0))
                time -= self.maxDelay
            
        # Create event
        self.eventList = np.append(self.eventList, InputEvent(virtualSourceCoreId, neuronAddress, coreDest, time = time, chipDest = chipDest))

### ===========================================================================
    def multiple_events(self, virtualSourceCoreId, neuronAddress, coreDest, absTimes = None, fireFreq = None, firePeriod = None, chipDest = 0):
        """Create multiple events for specified neurons and times.
        
Parameters:
    virtualSourceCoreId (array, int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddress (array, int): Represent the address of the virtual neuron that will generate the event
    coreDest (array, int): (4 bit hot coded). Represent the destination cores in which the spike will be routed
    absTimes (array, float [s]): Represent the absolute times for spikes, interspike interval is derived automatically
    fireFreq (array, float [Hz]): Firing frequency you want to achieve ; event delay is calculate as 1/frequency
    firePeriod (array, float [s]): Event delay (after delay the event is generated)

Note:
    With this function is possible to create a custom pattern of spikes in three ways:

    1. Defining a sequence of absolute times for the spikes (absTimes), for example: 1.1s, 1.2s, 1.3s
    2. Defining a sequence of firing frequencies for the spikes (fireFreq), for example: 50Hz, 20Hz, 10Hz
    3. Defining a sequence of firing periods for the spikes (firePeriod), for example: 0.1s, 0.2s, 0.3s

    - virtualSourceCoreId must be in the range [0, 3]
    - neuronAddress must be in the range [0, 255]
    - coreDest is a 4 bit hot coded number, must be in the range [0, 15]

Examples:
    Initialize the pattern istantiating the object::

        pattern = InputPattern(name = "pattern", isiBase = 900)

    - The following three examples create a pattern of three spikes with 20ms interspike interval
        using three different approaches. The spikes come from virtual neuron 2 of virtual core 1,
        and are sent to physical cores 0 and 2::

            virtualSourceCoreId = [1, 1, 1]
            neuronAddress = [2, 2, 2]
            coreDest = [5, 5, 5] # 0101 -> core 0 and 2

            pattern.multiple_events(virtualSourceCoreId, neuronAddress, coreDest,
                                    absTimes = [20e-3, 40e-3, 60e-3])
            pattern.multiple_events(virtualSourceCoreId, neuronAddress, coreDest,
                                    fireFreq = [50, 50, 50])
            pattern.multiple_events(virtualSourceCoreId, neuronAddress, coreDest,
                                    firePeriod = [20e-3, 20e-3, 20e-3])
"""
        
        # Find which type of event series must be generated
        freq = False
        period = False
        
        # Extract from absolute times the firePeriods
        if absTimes is not None:
            firePeriod = []
            diff = np.diff(absTimes)
            firePeriod.append(absTimes[0])
            firePeriod.extend(diff)
            
        if fireFreq is not None:
            freq = True
        elif firePeriod is not None:
            period = True
        else:
            errorString = "Error while creating event, specify or fire frequency or fire period: "
            raise NameError(errorString)
        
        # Adapt chip_id vector to the length of the other parameters...if remains 0 can create problems when not specifying it
        if np.size(chipDest) == 1:
            chipDest = [chipDest] * len(coreDest)

        # Scan the fireFreq or firePeriod vector and create all events
        for idx, addr in enumerate(neuronAddress):
            if freq:
                self.single_event(virtualSourceCoreId[idx], addr, coreDest[idx], fireFreq = fireFreq[idx], chipDest = chipDest[idx])
            else:
                self.single_event(virtualSourceCoreId[idx], addr, coreDest[idx],  firePeriod = firePeriod[idx], chipDest = chipDest[idx])

### ===========================================================================
    def constant_freq(self, virtualSourceCoreId, neuronAddress, coreDest, fireFreq, initDelay, duration, chipDest = 0):
        """Create addresses and time steps for a constant firing frequency of a certain duration
         
Parameters:
    virtualSourceCoreId (int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddress (int): Represent the address of the virtual neuron that will generate the event
    coreDest (int, 4 bit hot coded): Represent the destination cores in which the spike will be routed
    fireFreq (float, [Hz]): Desidered Firing frequency
    initDelay (float, [s]): Delay of the first event
    duration (float, [s]): Duration of the event pattern

Note:
    - virtualSourceCoreId must be in the range [0, 3]
    - neuronAddress must be in the range [0, 255]
    - coreDest is a 4 bit hot coded number, must be in the range [0, 15]

Examples:
    Initialize the pattern istantiating the object::

        pattern = InputPattern(name = "pattern", isiBase = 900)

    Create spike with 50Hz frequency, initial delay of 1/50 s and 1 s duration,
    from virtual neuron 22 of virtual core 3, to physical cores 0, 1 and 2::
            
        virtualSourceCoreId = 3
        neuronAddress = 22
        coreDest = 7 # 0111 -> core 0, 1 and 2
        pattern.constant_freq(virtualSourceCoreId, neuronAddress, coreDest,
                              fireFreq = 50, initDelay = 1/50, duration = 1)     
"""
        
        freqPhase = (1.0 / duration) # in Hz
        
        # Insert the first initial spike after an initial delay
        self.single_event(virtualSourceCoreId, neuronAddress, coreDest, firePeriod = initDelay, chipDest = chipDest)
        
        # Repeat (address, time) to occupy the whole duration of the frequency phase duration*/ 
        num_events = int(np.round(fireFreq / freqPhase))       
        for event in range(num_events):
            self.single_event(virtualSourceCoreId, neuronAddress, coreDest, fireFreq = fireFreq, chipDest = chipDest)

### ===========================================================================
    def linear_freq_modulation(self, virtualSourceCoreId, neuronAddress, coreDest, freqStart, freqStop, freqSteps, freqPhaseDuration, initDelay, chipDest = 0):
        """Create addresses and time steps for a linear firing frequency modulation
        
Parameters:
    virtualSourceCoreId (int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddress (int): Represent the address of the virtual neuron that will generate the event
    coreDest (int, 4 bit hot coded): Represent the destination cores in which the spike will be routed
    freqStart (float): Starting modulation frequency
    freqStop (float): Stop modulation frequency
    freqSteps (int): Number of steps of the modulation frequency
    freqPhaseDuration (float, [s]): Duration of each frequency step
    initDelay (float, [s]): Delay of the first event

Note:
    The modulation starts at <freqStart> and stops at <freqStop>, with <freqSteps> number of steps
    of duration <freqPhaseDuration>.

    It is possible to specify an initial delay of the first spike changing <initDelay>

    - virtualSourceCoreId must be in the range [0, 3]
    - neuronAddress must be in the range [0, 255]
    - coreDest is a 4 bit hot coded number, must be in the range [0, 15]

Examples:
    Initialize the pattern istantiating the object::

        pattern = InputPattern(name = "pattern", isiBase = 900)

    Create spikes from 50Hz to 100Hz with 6 steps (50, 60, 70, 80, 90, 100)Hz, 100ms of duration of each step,
    initial delay of 0.5s and 1s duration, from virtual neuron 5 of virtual core 0, to physical core 3::

        virtualSourceCoreId = 0
        neuronAddress = 5
        coreDest = 8 # 1000 -> core 3
        pattern.linear_freq_modulation(virtualSourceCoreId, neuronAddress, coreDest,
                                       freqStart = 50,  freqStop = 100, freqSteps = 6,
                                       freqPhaseDuration = 0.1, initDelay = 0.5) 
"""
        
        # Generate (address, time) event list
        freqPhase = (1.0 / freqPhaseDuration) # in Hz
        freqs = np.linspace(freqStart, freqStop, freqSteps) # in Hz
        
        # Insert the first initial spike after an initial delay
        self.single_event(virtualSourceCoreId, neuronAddress, coreDest, firePeriod = initDelay, chipDest = chipDest)
        
        # Step on all frequencies and create (address, time) events list
        for freq in freqs:
            # Repeat (address, time) to occupy the whole duration of the frequency phase duration*/ 
            num_events_this_freq = int(np.round(freq / freqPhase))
            for event in range(num_events_this_freq):
                self.single_event(virtualSourceCoreId, neuronAddress, coreDest, fireFreq = freq, chipDest = chipDest)

### ===========================================================================
    def threshold_encoder(self, virtualSourceCoreId, neuronAddressUpCH, neuronAddressDwCH, coreDest, threshold, t, y, noiseVar, initDelay, chipDest = 0):
        """Create spikes with variable frequency, in the form of a specified function      
        
Parameters:
    virtualSourceCoreId (int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddressUpCH (int): Represent the address of the virtual neuron that will generate the event on Up channel
    neuronAddressDwCH (int): Represent the address of the virtual neuron that will generate the event on Up channel
    coreDest (int, 4 bit hot coded): Represent the destination cores in which the spike will be routed
    threshold (int): Theshold that triggers the generation of the spike
    t (float, [s]): Time vector of the signal
    y (float): Value vector of the signal
    noiseVar (float, [s]): Variance of a gaussian distribution from which noise is applied to event times
    initDelay (float, [s]): Delay of the first event

Note:
    A spike is generated when the signal does a step up or step down bigger than the threshold <threshold>.

    Spikes are encoded in two channels (<neuronAddressUpCH> and <neuronAddressDwCH>)
    according to the direction of the jump (depending on the slope of the signal):\n
    - deltaY > threshold --> Up channel spike
    - deltaY < -threshold --> Dw channel spike

    It is possible to specify an initial delay of the first spike changing <initDelay>
    It is possible to specify the variance <noiseVar> of a Gaussian noise added to the spike times
        
    Note that the algorithm does not constrain the firing frequencies to a minimum or maximum,
    but they depend on the signal and the threshold. Minimum and maximum
    firing rates are calculated and printed (<TODO>)

    - virtualSourceCoreId must be in the range [0, 3]
    - neuronAddressUpCH must be in the range [0, 255]
    - neuronAddressDwCH must be in the range [0, 255]

    coreDest is a 4 bit hot coded number, must be in the range [0, 15]
    
Note:
    The pattern must avoid negative delays. Hence jitter is removed samples that create negative times

Examples:
    Initialize the pattern istantiating the object::

        pattern = InputPattern(name = "pattern", isiBase = 900)

    - 1 s of 2 Hz sinewave converted in spikes with a threshold of 0.05, no jitter and initial delay of 0.1s.
      Spikes come 2 neurons: Up channel from virtual neuron 20 of virtual core 0,
      Down channel from virtual neuron 21 of virtual core 0, and are routed to physical core 1::

        virtualSourceCoreId = 0
        neuronAddressUpCH = 20
        neuronAddressDwCH = 21
        coreDest = 1 # 0001 -> core 1
        
        t = np.arange(0, 1, 1e-6)
        y = np.sin(2 * np.pi * 1 * t)
        pattern.threshold_encoder(virtualSourceCoreId, neuronAddressUpCH, neuronAddressDwCH,
                                   threshold = 0.05, t = t, y = y,
                                   noiseVar = 0, initDelay = 0.1)
"""
        
        # Initialization
        t = t - t[0] # Time normalization
        t = t*1e6 # Transform in us scale\
        
        if initDelay != None:
            t = t + initDelay * 1e6
            
        self.tSig = t
        self.ySig = y
        
        spikeTimes = []
        spikeAddresses = []
                
        # Insert the first spike after an initial delay*/
        if initDelay != None:
            spikeTimes.append(initDelay)
            if y[1] >= y[0]: # Positive slope
                spikeAddresses.append(neuronAddressUpCH)
            else: # Negative slope
                spikeAddresses.append(neuronAddressDwCH)

        # Scan the whole sinewave and create spikes
        lastSpikeIndex = 0
        for idy, valy in enumerate(y):
            if (valy - y[lastSpikeIndex]) >= threshold: # If signal goes up of a quantity higher than threshold
                # Evaluate interspike interval
                time = t[idy] / 1e6
                # Apply noise
                noise = np.random.uniform(low = -noiseVar, high = noiseVar)
                time = time + noise
                if(time < 0):
                    time = time - noise
                # Create event
                spikeTimes.append(time)
                spikeAddresses.append(neuronAddressUpCH)
                lastSpikeIndex = idy
                    
            elif (valy - y[lastSpikeIndex]) <= -(threshold): # If signal goes dows of a quantity higher than threshold
                # Evaluate interspike interval
                time = t[idy] / 1e6
                # Apply noise
                noise = np.random.uniform(low = -noiseVar, high = noiseVar)
                time = time + noise
                if(time < 0):
                    time = time - noise
                # Create event
                spikeTimes.append(time)
                spikeAddresses.append(neuronAddressDwCH)
                lastSpikeIndex = idy
        
        # Reorder the times and addresses if noiseVar is different from 0 because is not guaranteed that the time list 
        # is ordered. It would fail writing the output file
        if(noiseVar != 0):
            sortedPair = sorted(zip(spikeTimes, spikeAddresses))
            spikeTimes = [x for x,_ in sortedPair]
            spikeAddresses = [x for _,x in sortedPair]
        
        virtualSourceCoreIds = [virtualSourceCoreId]*len(spikeTimes)
        coreDests = [coreDest]*len(spikeTimes)
        chipDests = [chipDest]*len(spikeTimes)
        
        self.multiple_events(virtualSourceCoreIds, spikeAddresses, coreDests,
                             absTimes = spikeTimes, chipDest = chipDests)

        # Calculate and print maximum and minimum firing frequencies obtained
        #absTime = [0] * len(self.eventList)
        #absTime[0] = self.eventList[0].time
        
        #for idx, event in enumerate(self.eventList[1:]):
        #    absTime[idx + 1] = absTime[idx] + event.time
        #upPos = [True for event in self.eventList if event.neuronAddress == neuronAddressUpCH]

        #upChTimes = np.array(absTime)[np.where(self.eventList.neuronAddress == neuronAddressUpCH)]
        #dwChTimes = np.array(absTime)[np.where(self.eventList.neuronAddress == neuronAddressDwCH)]
        
        #maxUpChFrequency = 1e6 / (np.min(np.diff(upChTimes)) * self.isiRatio) 
        #minUpChFrequency = 1e6 / (np.max(np.diff(upChTimes)) * self.isiRatio)
        #maxDwChFrequency = 1e6 / (np.min(np.diff(dwChTimes)) * self.isiRatio)
        #minDwChFrequency = 1e6 / (np.max(np.diff(dwChTimes)) * self.isiRatio)
        #print('=======================================')
        #print("MAX Up channel frequency: %.5f Hz" % np.round(maxUpChFrequency))
        #print("min Up channel frequency: %.5f Hz" % np.round(minUpChFrequency))
        #print('MAX Dw channel frequency: %.5f Hz' % np.round(maxDwChFrequency))
        #print('min Dw channel frequency: %.5f Hz' % np.round(minDwChFrequency))
        #print('=======================================')
        
### ===========================================================================
    def plot_spikes(self, timeShift = 0, fig = None, ax = None, plotSig = False):
        """ Plot the spikes of the current pattern

Parameters:
    color (string): Color of the pattern
    timeShift (int, optional): Add this time to all the events
    ax (ax handle, optional): Plot graph on this handle, otherwise a new figure will be created

Note:
    When plotting, different colors will be used according to the different virtual neuron addresses that are
    present in the pattern. For example virtual neuron 0 events and virtual neuron 1 events, even if in the same
    pattern, will be plotted with different colors.

    This is useful because you can, just with a glance to the plot, understand the contributions of all virtual neurons

    The label of each trace is constructed such to let you recognize who is the source, for example:

    - virtual neuron 0 of virtual core 0, to all cores (1111) -> label = "Virtual Neuron C0N1"
    - virtual neuron 20 of virtual core 1, to core 1 (0001) -> label = "Virtual Neuron C1N20"
"""

        # If no subplot is specified, create new plot
        if ax == None: 
            fig = plt.figure()
            ax = fig.add_subplot(111)
            
        # Create absolute times
        absTimes = []
        for event in self.eventList:
            try:
                absTimes.append(absTimes[-1] + event.time * self.isiRatio)
            except:
                absTimes.append(event.time * self.isiRatio + timeShift)
        absTimes = np.array(absTimes)

        # Create vector of addresses
        addresses = []
        for event in self.eventList:
            addresses.append(event.address)
        addresses = np.array(addresses)
        
        # Create set of addresses
        setAddresses = []
        for address in addresses:
            if(address not in setAddresses):
                setAddresses.append(address)
        setAddresses = np.array(list(setAddresses))
        
        # Plot separately
        handles = []
        for idx, address in enumerate(setAddresses):
            indexes = np.where(addresses == address)
            times = absTimes[indexes]
            arrowDim = 1
#            handle = ax.quiver(times,
#                               np.zeros(len(times)),
#                               np.zeros(len(times)),
#                               arrowDim * np.ones(len(times)),
#                               color = "C" + str(idx),
#                               angles = 'xy', scale_units = 'xy', scale = 1,
#                               label = self.name)
#            ax.plot(times, arrowDim * np.ones(len(times)), linestyle  = 'None', color = "C" + str(idx), marker = '^')
            decodedEvent = InputEvent(address = address, time = 0)
            label = "Virtual Neuron C{}N{}".format(decodedEvent.virtualSourceCoreId,
                                           decodedEvent.neuronAddress)
            handle = ax.vlines(x = times, ymin = 0, ymax = arrowDim, colors = "C" + str(idx),
                              label = label)
            handles.append(handle)
        
        # Plot signal shape
        if plotSig:
            if  len(self.tSig) != []:
                handle = ax.plot(self.tSig + timeShift, self.ySig, 'k', label = self.name)
            handles.extend(handle)
        
        return fig, ax, handles

### ===========================================================================
    def insert_dummy_neuron(self, virtualSourceCoreId, neuronAddress):
        """Insert a dummy neuron that is addressed when required to create additional times
        
Parameters:
    virtualSourceCoreId (int): Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
    neuronAddress (int): Represent the address of the virtual neuron that will generate the event
    
Note:
    Do not use neuron 0 of core 0! and do not use a neuron that it may stimulate some physical neurons in the chip!
"""
        self.dummyNeuron = (virtualSourceCoreId, neuronAddress)
        
### ===========================================================================
    def add_manually_event(self, address, time):
        """Add manually an event starting from address and time

Parameters:
    address (int): Encoded address of the virtual neuron
    time (int): Delay after which the event is generated. It is expressed as multiple of isiBase
"""

        np.append(self.eventList, InputEvent(address = address, time = time))

### ===========================================================================
    def evaluate_duration(self, retSigTime = False):
        """Calculate the duration of the pattern

Returns:
    float: Duration of the whole pattern
"""

        time = 0
        for event in self.eventList:
            time = time + event.time * self.isiRatio
        
        if retSigTime:
            if len(self.tSig) != []:
                time = self.tSig[-1]

        return time