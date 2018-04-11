"""Creates the input event pattern for the tutorial network. It generates:
- 5 seconds of 1Hz sinusoidal wave (5 periods) events
- 5 seconds of 2Hz sinusoidal wave (10 period) events
"""

import DYNAPSETools.dynapseSpikesGenerator as DSG
import numpy as np
import matplotlib.pyplot as plt

plt.close("all") # Close all the plots that has been created
                 # in the previous run

isiBase = 900 # Setting isiBase for all patterns


### Create InputPatterns
# Create pattern
Pattern1 = DSG.InputPattern(name = "Pattern1", isiBase = isiBase)

# Choose virtual neuron address
C, N = 0, 1

# Define pattern
Pattern1.single_event(virtualSourceCoreId = C,
                      neuronAddress = N,
                      coreDest = 15,
                      firePeriod = 0.5)

# Create pattern
Pattern2 = DSG.InputPattern(name = "Pattern2", isiBase = isiBase)

# Choose virtual neuron address and parameters
firePeriod = [0.2, 0.4, 0.1, 0.5]
C = [1, 1, 1, 1]
N = [1, 1, 1, 1]
coreDest = [15, 15, 15, 15]

# Define pattern
Pattern2.multiple_events(virtualSourceCoreId = C,
                         neuronAddress = N,
                         coreDest = coreDest,
                         absTimes=None, fireFreq=None,
                         firePeriod = firePeriod)

# Create pattern
Pattern3 = DSG.InputPattern(name = "Pattern3", isiBase = isiBase)

# Choose virtual neuron address
C, N = 0, 1

# Define pattern
Pattern3.constant_freq(virtualSourceCoreId = C,
                       neuronAddress = N,
                       coreDest = 15,
                       fireFreq = 50,
                       initDelay = 0.5,
                       duration = 0.5)

# Create pattern
Pattern4 = DSG.InputPattern(name = "Pattern4", isiBase = isiBase)

# Define sinusoidal signal with 1000 samples
freq = 1
t = np.linspace(0, 1, 1000)
y = np.sin(2*np.pi*freq*t)

# Choose virtual neuron addresses
C, NUp, NDw = 2, 5, 6 

# Define pattern
Pattern4.threshold_encoder(virtualSourceCoreId = C,
                           neuronAddressUpCH = NUp,
                           neuronAddressDwCH = NDw,
                           coreDest = 15,
                           threshold = 0.05,
                           t = t, y = y,
                           noiseVar = 0,
                           initDelay = 0.5)


finalPattern = (Pattern1, Pattern3, Pattern2, Pattern1)
DSG.plot_spikes(*finalPattern)
plt.legend()

finalPattern = (Pattern1, Pattern2, Pattern3, Pattern4)
DSG.plot_spikes(*finalPattern)
plt.legend()