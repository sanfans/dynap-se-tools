# DESCRIPTION: Contains a class that represent a pattern of inputs to DYNAP-se

import numpy as np
import matplotlib.pyplot as plt
from DYNAPSETools.classes.InputEvent import InputEvent

class InputPattern:
    """Class that represent a pattern of inputs to DYNAP-se
    """

    def __init__(self, name, isiBase = 90.0):
        """Return a new InputPattern object

Parameters
----------
name : string. Name of the pattern (useful for debug)
isiBase : int. Time base for time event generation.
    Every delay is represented as multiple of this base. Knowing that an isiBase = 90 correspond to 1 us
    a delay = 10 -> 10 * isiBase = 10 us
    With isiBase = 900 a delay = 10 -> 10 * isiBase = 100 us
"""

        self.name = name

        # Set spike base timing
        self.isiBase = isiBase # Base for the timing of the spikes
        self.isiForUs = 90.0 # ISI to have 1 us resolution
        self.isiRatio = self.isiBase / self.isiForUs

        # Generate (address, time) event arrays
        self.eventList = np.array([])
        self.tSig = np.array([])
        self.ySig = np.array([])

### ===========================================================================
    def single_event(self, virtualSourceCoreId, neuronAddress, coreDest, fireFreq = None, firePeriod = None):
        """Create a single address and time step for a specified neuron and a certain interspike interval
        
Parameters
----------
virtualSourceCoreId : int. Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
neuronAddress : int. Represent the address of the virtual neuron that will generate the event
coreDest : int (4 bit hot coded, from 0 to 15). Represent the destination cores in which the spike will be routed
fireFreq : int [Hz]. Firing frequency you want to achieve ; event delay is calculate as 1/frequency
firePeriod : float [s]. Event delay (after delay the event is generated)

Examples
--------
- single_event(1, 15, 0, firePeriod = 0.1)
- single_event(2, 1, 0, fireFreq = 50)
"""

        if (firePeriod == None) & (fireFreq != None):
            time = np.ceil((1.0 / fireFreq ) * 1e+6 / self.isiRatio) #/*In ISI units*/
        elif (firePeriod != None) & (fireFreq == None):
            time = np.ceil(firePeriod * 1e+6 / self.isiRatio) #/*In ISI units*/
        else:
            errorString = "Error while creating event {}, specify or fire frequency or fire period: ".format(self.name)
            raise NameError(errorString)
            
        # Create event
        self.eventList = np.append(self.eventList, InputEvent(virtualSourceCoreId, neuronAddress, coreDest, time = time))

### ===========================================================================
    def multiple_events(self, virtualSourceCoreId, neuronAddress, coreDest, absTimes = None, fireFreq = None, firePeriod = None):
        """Create multiple events for specified neurons and times.
        
It is possible to specify a sequence of absolute times for the spikes (absTimes)
It is possible to specify a sequence of firing frequencies for the spikes (fireFreq)
It is possible to specify a sequence of firing periods for the spikes (firePeriod)

Parameters
----------
virtualSourceCoreId : list of ints. Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
neuronAddress : list of ints. Represent the address of the virtual neuron that will generate the event
coreDest : list of ints (4 bit hot coded, from 0 to 15). Represent the destination cores in which the spike will be routed
absTimes : list of floats [s]. Represent the absolute times for spikes, interspike interval is derived automatically
fireFreq : list of ints [Hz]. Firing frequency you want to achieve ; event delay is calculate as 1/frequency
firePeriod : float [s]. Event delay (after delay the event is generated)

Examples
--------
- sparse_events([1, 1, 1], [15, 15, 15], [0, 0, 0], absTimes = [20e-3, 40e-3, 60e-3])
- sparse_events([1, 1, 1], [15, 15, 15], [0, 0, 0], fireFreq = [50, 50, 50])
- sparse_events([1, 1, 1], [15, 15, 15], [0, 0, 0], firePeriod = [20e-3, 20e-3, 20e-3])
"""
        
        # Find which type of event series must be generated
        freq = False
        period = False
        
        # Extract from absolute times the firePeriods
        if absTimes != None:
            firePeriod = []
            diff = np.diff(absTimes)
            firePeriod.append(absTimes[0])
            firePeriod.extend(diff)
            
        if fireFreq != None:
            freq = True
        elif firePeriod != None:
            period = True
        else:
            errorString = "Error while creating event, specify or fire frequency or fire period: "
            raise NameError(errorString)
        
        # Scan the fireFreq or firePeriod vector and create all events
        for idx, addr in enumerate(neuronAddress):
            if freq:
                self.single_event(virtualSourceCoreId[idx], addr, coreDest[idx], fireFreq = fireFreq[idx])
            else:
                self.single_event(virtualSourceCoreId[idx], addr, coreDest[idx],  firePeriod = firePeriod[idx])

### ===========================================================================
    def constant_freq(self, virtualSourceCoreId, neuronAddress, coreDest, fireFreq, initDelay, duration):
        """Create addresses and time steps for a constant firing frequency of a certain duration
         
Parameters
----------
virtualSourceCoreId : int. Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
neuronAddress : int. Represent the address of the virtual neuron that will generate the event
coreDest : int (4 bit hot coded, from 0 to 15). Represent the destination cores in which the spike will be routed
fireFreq : int [Hz]. Desidered Firing frequency
initDelay : float [s]. Delay of the first event
duration : float [s]. Duration of the event pattern

Examples
--------
Create spike with 50Hz frequency, initial delay of 1/50 s and 1 s duration
- constant_freq(1, 15, 0, 50, 1/50, 1)
"""

        # Generate (address, time) event list
        addresses = []
        times = []
        
        freqPhase = (1.0 / duration) # in Hz
        
        # Insert the first initial spike after an initial delay
        self.single_event(virtualSourceCoreId, neuronAddress, coreDest, firePeriod = initDelay)
        
        # Repeat (address, time) to occupy the whole duration of the frequency phase duration*/ 
        num_events = int(np.floor(fireFreq / freqPhase))       
        for event in range(num_events):
            self.single_event(virtualSourceCoreId, neuronAddress, coreDest, fireFreq = fireFreq)

### ===========================================================================
    def linear_freq_modulation(self, virtualSourceCoreId, neuronAddress, coreDest, freqStart, freqStop, freqSteps, freqPhaseDuration, initDelay):
        """Create addresses and time steps for a linear firing frequency modulation
        
The modulation starts at <freqStart> and stops at <freqStop>, with <freqSteps> number of steps
of duration <freqPhaseDuration>
It is possible to specify an initial delay of the first spike changing <initDelay>

Parameters
----------
virtualSourceCoreId : int. Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
neuronAddress : int. Represent the address of the virtual neuron that will generate the event
coreDest : int (4 bit hot coded, from 0 to 15). Represent the destination cores in which the spike will be routed
freqStart : int [Hz]. Starting modulation frequency
freqStop : int [Hz]. Stop modulation frequency
freqSteps : int [Hz]. Number of steps of the modulation frequency
freqPhaseDuration: float [s]. Duration of each frequency step
initDelay : float [s]. Delay of the first event

Examples
--------
modulation from 50Hz to 100Hz with 6 steps (50, 60, 70, 80, 90, 100)Hz, 100ms of duration of each step, zero initial delay
- linear_freq_modulation(1, 15, 0, 50, 100, 6, 0.1, 0)
"""
        
        # Generate (address, time) event list
        freqPhase = (1.0 / freqPhaseDuration) # in Hz
        freqs = np.linspace(freqStart, freqStop, freqSteps) # in Hz
        
        # Insert the first initial spike after an initial delay
        self.single_event(virtualSourceCoreId, neuronAddress, coreDest, firePeriod = initDelay)
        
        # Step on all frequencies and create (address, time) events list
        for freq in freqs:
            # Repeat (address, time) to occupy the whole duration of the frequency phase duration*/ 
            num_events_this_freq = int(np.floor(freq / freqPhase))
            for event in range(num_events_this_freq):
                self.single_event(virtualSourceCoreId, neuronAddress, coreDest, fireFreq = freq)

### ===========================================================================
    def threshold_encoder(self, virtualSourceCoreId, neuronAddressUpCH, neuronAddressDwCH, coreDest, threshold, t, y, noiseVar, initDelay):
        """Create spikes with variable frequency, in the form of a specified function      
        
A spike is generated when the signal does a step up or step down bigger than the threshold <threshold>.
The spikes are encoded in two channels (<neuronAddressUpCH> and <neuronAddressDwCH>)
according to the direction of the jump (depending on the slope of the signal):
    deltaY > threshold --> Up channel spike
    deltaY < -threshold --> Dw channel spike
It is possible to specify an initial delay of the first spike changing <initDelay>
It is possible to specify the variance <noiseVar> of a Gaussian noise added to the spike times
With <plotEn> True the signal shape is included in the list of signals to be plotted
        
Note that the algorithm does not constrain the firing frequencies to a minimum or maximum,
but they depend on the signal and the threshold. Minimum and maximum
firing rates are calculated and printed.

Parameters
----------
virtualSourceCoreId : int. Represent the ID of the virtual core where is located the virtual neuron (from 0 to 3)
neuronAddressUpCH : int. Represent the address of the virtual neuron that will generate the event on Up channel
neuronAddressDwCH : int. Represent the address of the virtual neuron that will generate the event on Up channel
coreDest : int (4 bit hot coded, from 0 to 15). Represent the destination cores in which the spike will be routed
threshold : int. Theshold that triggers the generation of the spike
t : float [s]. Time vector of the signal
y : float. Value vector of the signal
noiseVar : float. Variance of a gaussian distribution from which noise is applied to event times
initDelay : float [s]. Delay of the first event

Examples
--------
- t = np.arange(0, 1, 1e-6)
    y = np.sin(2 * np.pi * 1 * t)
    spikeGen.threshold_encoder(1, 2, 15, 0, 0.05, t, y, 0, 1e-3, plotEn = True)
"""
        
        # Initialization
        t = t - t[0] # Time normalization
        t = t*1e6 # Transform in us scale
        self.tSig = t
        self.ySig = y
        
        # Insert the first spike after an initial delay*/
        if y[1] >= y[0]: # Positive slope
            self.single_event(virtualSourceCoreId, neuronAddressUpCH, coreDest, firePeriod = initDelay)
        else: # Negative slope
            self.single_event(virtualSourceCoreId, neuronAddressDwCH, coreDest, firePeriod = initDelay)
        
        # Scan the whole sinewave and create spikes
        lastSpikeIndex = 0
        for idy, valy in enumerate(y):
            if (valy - y[lastSpikeIndex]) >= threshold: # If signal goes up of a quantity higher than threshold
                # Evaluate interspike interval
                time = (t[idy] - t[lastSpikeIndex]) / 1e6
                # Apply noise
                noise = np.int(np.random.normal(loc = 0, scale = noiseVar))
                time = time + noise
                # Create event
                self.single_event(virtualSourceCoreId, neuronAddressUpCH, coreDest, firePeriod = time)
                lastSpikeIndex = idy
                    
            elif (valy - y[lastSpikeIndex]) <= -(threshold): # If signal goes dows of a quantity higher than threshold
                # Evaluate interspike interval
                time = (t[idy] - t[lastSpikeIndex]) / 1e6
                # Apply noise
                noise = np.int(np.random.normal(loc = 0, scale = noiseVar))
                time = time + noise
                # Create event
                self.single_event(virtualSourceCoreId, neuronAddressDwCH, coreDest, firePeriod = time)
                lastSpikeIndex = idy
          
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
    def plot_spikes(self, color, timeShift = 0, ax = None):
        """
        """

        fig = None

        # If no subplot is specified, create new plot
        if ax == None: 
            fig = plt.figure()
            ax = fig.add_subplot(111)

        currTime = timeShift
        for event in self.eventList:
            handle, = ax.plot(currTime + event.time, 4 * event.virtualSourceCoreId + event.neuronAddress, linestyle = 'None', marker = 'o', color = color, label = self.name)
            currTime = currTime + event.time

        #if self.tSig != None:
        #    ax.plot(self.tSig + timeShift, self.ySig, color = color)
        return fig, ax, handle

### ===========================================================================
    def add_manually_event(self, address, time):
        """Add manually an event starting from address and time

Parameters
----------
address : int. Encoded address of the virtual neuron
time : int. Delay after which the event is generated
    It is expressed as multiple of ISIBase
"""

        np.append(self.eventList, InputEvent(address = address, time = time))

### ===========================================================================
    def evaluate_duration(self):
        """Calculate the duration of the pattern
        """

        time = 0
        for event in self.eventList:
            time = time + event.time
        return time