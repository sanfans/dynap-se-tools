import DYNAPSETools.dynapseOutDecoder as DOD
import numpy as np
import matplotlib.pyplot as plt

plt.close("all")

fileName = "./DYNAPSETools/tutorialFiles/outTutorial.aedat"
decEvents = DOD.import_events(fileName)
decEvents = decEvents.normalize()
decEvents.plot_events()
filterCore0 = np.arange(0, 193) # Taking neurons from 0 to 63
filterCore1 = np.arange(0, 256) # Taking neurons from 0 to 256
neuron_id_filter = [filterCore0, filterCore1]
core_id_filter = [0, 1]
decFilteredEvents = decEvents.filter_events(chip_id = 0, core_id = core_id_filter,
                                            neuron_id = neuron_id_filter) # Take only events i need
decFilteredEvents.plot_events()
extractedEvents = decFilteredEvents.isolate_events_sets(startTriggerNeuron = (0, 0, 128),
                                                        stopTriggerNeuron = (0, 0, 192),
                                                        maxNumber = 5)
DOD.plot_events(extractedEvents)
extractedEvents[2].plot_events()

# Create empty lists
timeStepsArray = []
firingRateMatrixes = []

for experiment in extractedEvents:
    # Filter events taking events from 0 to the last event before stop trigger
    # (i take all useful events)
    timeSteps, neuronsFireRate = experiment.calculate_firing_rate_matrix(totNeurons = 1024,
                                                                         timeBin = 0.2)
                                                                         
    timeStepsArray.append(timeSteps)
    firingRateMatrixes.append(neuronsFireRate)

# Transform into array
timeStepsArray = np.array(timeSteps)
firingRateMatrixes = np.array(firingRateMatrixes)
