# DESCRIPTION: Example of how to use DynapseOutDecoder functions

### =================== IMPORT PACKAGES ================================
from matplotlib import pyplot as plt
import DYNAPSETools.dynapseOutDecoder as decoder

plt.close("all")

# ====================== Import events from .aedat file
# Change the path to select your .aedat file to decode
decEvents = decoder.import_events("DYNAPSETools/Examples/DynapseOutDecoder.aedat")
decEvents.plot_events()

# Filter events taking only chip 0 ones
decFilteredEvents = decEvents.filter_events(chip_id = 0, core_id = None, neuron_id = None) # Take only first chip events
decFilteredEvents.plot_events()

# ====================== Extract subsets from a Event set
# start trigger: chip0, core2, neuron 64 --> (0, 2, 64)
# stop trigger: chip0, core2, neuron 128 --> (0, 2, 128)
extractedEvents = decFilteredEvents.isolate_events_sets(startTriggerNeuron = (0, 2, 64), stopTriggerNeuron = (0, 2, 128))

# Filter every experiment taking only core 0 and 1
extractedFilteredEvents = []
for experiment in extractedEvents:
    filteredEvents = experiment.filter_events(chip_id = 0, core_id = [0, 1], neuron_id = None) # Filter trigger events
    extractedFilteredEvents.append(filteredEvents)

# Plot every event set in the list
decoder.plot_events(extractedFilteredEvents)

# ====================== Calculate firing rate matrix
for experiment in extractedFilteredEvents:
    timeSteps, neuronsFireRate = experiment.calculate_firing_rate_matrix(numBins = 20, totNeurons = 1024)
    decoder.plot_firing_rate(timeSteps = timeSteps, neuronsFireRate = neuronsFireRate, enImshow = True)

plt.show()