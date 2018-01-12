# DESCRIPTION: contains a class that represent a set of DYNAP-se events

import numpy as np
import matplotlib.pyplot as plt
import DYNAPSETools.blaSpikesGenerator as spikegen

plt.close("all")

### =================== CREATE EVENTS FOR DYNAPSE ================================
# On fileName insert the path for your output file. Hint: create a folder "myStimulus" in cAER directory and use it to store all stimulus
# Change isiBase according to which is the spike resolution you want to get (resolution ~= isiBase * 11.11 ns)
# and the maximum delay (maxDelay ~= isiBase * 728 us). Remember to set it accordingly in cAER!
# For this example isiBase = 900 -> resolution = 10us, maxDelay = 655ms
# In general -> resolution = isiBase/90 * 11.11ns, maxDelay = 2^16 * resolution


# Create 2 sparse events (neuron 1, all cores (coreDest = 15), source core 0) with 200 ms delay between them (delay of first event is the initial one)
firstPattern = spikegen.InputPattern("firstPattern", isiBase = 900.0)
firstPattern.multiple_events(virtualSourceCoreId = [0, 0], neuronAddress = [1, 1], coreDest = [15, 15], firePeriod = [0.2, 0.2])

# Create other 2 sparse events (neuron 1, all cores (coreDest = 15), source core 0) with 200 ms delay between them and the previous one (equivalent to 5Hz)
secondPattern = spikegen.InputPattern("secondPattern", isiBase = 900.0)
secondPattern.multiple_events(virtualSourceCoreId = [0, 0], neuronAddress = [1, 1], coreDest = [15, 15], fireFreq = [5, 5])

# Create other 2 sparse events (neuron 1, all cores (coreDest = 15), source core 0) with 200 ms delay between them and the previous one (absolute times 0.2s and 0.4s)
thirdPattern = spikegen.InputPattern("thirdPattern", isiBase = 900.0)
thirdPattern.multiple_events(virtualSourceCoreId = [0, 0], neuronAddress = [1, 1], coreDest = [15, 15], absTimes = [0.2, 0.4])

# Create a constant frequency event (neuron 2, all cores (coreDest = 15), source core 0) with 50 Hz frequency, duration 1s and 500 ms delay from the previous pattern
fourthPattern = spikegen.InputPattern("fourthPattern", isiBase = 900.0)
fourthPattern.constant_freq(virtualSourceCoreId = 0, neuronAddress = 2, coreDest = 15, fireFreq = 50, initDelay = 0.5, duration = 1)

# Create a linear frequency modulation (neuron 3, all cores (coreDest = 15), source core 0) starting from 50Hz up to 100Hz in 6 steps.
# Every step has 100ms duration and there is a 500ms delay from the previous pattern
fifthPattern = spikegen.InputPattern("fifthPattern", isiBase = 900.0)
fifthPattern.linear_freq_modulation(virtualSourceCoreId = 0, neuronAddress = 3, coreDest = 15,
                                    freqStart = 50, freqStop = 100, freqSteps = 6, freqPhaseDuration = 0.1,
                                    initDelay = 0.5)

# Create 1 event (neuron 6, cores 15, source core 0) with a delay of 500 ms from the last spike
sixthPattern = spikegen.InputPattern("sixthPattern", isiBase = 900.0)
sixthPattern.single_event(virtualSourceCoreId = 0, neuronAddress = 4, coreDest = 15, firePeriod = 500e-3)

# Encode 1 period of 1Hz sinusoid in spikes on neuron 7 and 8 (all cores (coreDest = 15), source core 0) using the encoding by threshold
# Threshold is set to 0.05
tSig = np.arange(0, 1, 1e-6) 
ySig = np.sin(2 * np.pi * 1 * tSig)
seventhPattern = spikegen.InputPattern("seventhPattern", isiBase = 900.0)
seventhPattern.threshold_encoder(virtualSourceCoreId = 0, neuronAddressUpCH = 5, neuronAddressDwCH = 6, coreDest = 15, 
                                 threshold = 0.05, t = tSig, y = ySig, noiseVar = 0, initDelay = 0.5)

# Plot patterns
fig, ax, handles = spikegen.plot_spikes(firstPattern, secondPattern, thirdPattern, fourthPattern, fifthPattern, sixthPattern, seventhPattern)
# Plot settings
ax.set_xlabel('Time (us)')
ax.set_ylabel('Events and Signals')
ax.grid(b=True, which='major', color='grey', linestyle='-')
ax.grid(b=True, which='minor', color='r', linestyle='-', alpha=0.2)
ax.minorticks_on()
#ax.legend([handles], ["Ciao"])

# Control specified delays and write output file
spikegen.write_to_file(firstPattern,
                       secondPattern,
                       thirdPattern,
                       fourthPattern,
                       fifthPattern,
                       sixthPattern,
                       seventhPattern,
                       fileName = "DYNAPSETools/Examples/stimulus.txt")

plt.show()