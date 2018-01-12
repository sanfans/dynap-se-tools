# AUTHOR: roberto@ini.phys.ethz.ch or cattaroby93@gmail.com
#
# DATE OF CREATION: 29/9/2017

# DESCRIPTION: Example of training and reconstruction of a sinusoidal input applied
# to populations in DYNAP-se board. The complete flow is the following:
# --> SINUSOID is transformed in spikes and supplied to the neurons in DYNAP-se
# --> OUTPUT SPIKES are recorded and FIRING RATE MATRIX is obtained
# --> LINEAR REGRESSION or PSEUDO INVERSE is applied to reconstruct the INPUT SIGNAL data from the FIRING RATE MATRIX
# --> OBTAINED RECONSTRUCTION VECTOR is used to make a prevision of another set of events

### =================== IMPORT PACKAGES ================================
import numpy as np
import matplotlib.pyplot as plt
import DYNAPSETools.blaOutDecoder as decoder
import DYNAPSETools.blaSpikesFitter as fitter

plt.close("all")

### =================== IMPORT TRAINING EVENTS FROM DYNAPSE RECORDING ================================
training = decoder.import_events("DYNAPSETools/Examples/DynapseSpikesFitter_sine1.aedat")
training.plot_events() # Plot raster
training = training.filter_events(chip_id = 0, core_id = None, neuron_id = None) # Take only first chip events
training.plot_events() # Plot raster

# Extract subsets from a Event set
# start trigger: chip0, core2, neuron 64 --> (0, 2, 64)
# stop trigger: chip0, core2, neuron 128 --> (0, 2, 128)
trainingSets = training.isolate_events_sets(startTriggerNeuron = (0, 2, 64), stopTriggerNeuron = (0, 2, 128))

# Filter experiment taking only core 0 and 1
trainingSetFiltered = trainingSets[0].filter_events(chip_id = 0, core_id = [0, 1], neuron_id = None) # Filter trigger events
trainingSetFiltered = trainingSetFiltered.normalize() # First event will have time 0
trainingSetFiltered.plot_events()

# Calculate and plot firing rate matrix
timeStepsTrain, neuronsFireRateTrain = trainingSetFiltered.calculate_firing_rate_matrix(numBins = 20, totNeurons = 1024)
decoder.plot_firing_rate(timeSteps = timeStepsTrain, neuronsFireRate = neuronsFireRateTrain)

### =================== DEFINE SIGNAL SHAPE RECONSTRUCTION ================================
# Define input sinusoidal signal data
sineFreq = 1 # [Hz]
inputSignal = np.sin(2 * np.pi * sineFreq * np.array(timeStepsTrain) / 1e+6)

### =================== LEARNING WITH SKLEARN ================================
regr, coeff = fitter.sklearn_fit(matrix = neuronsFireRateTrain, target = inputSignal) # Learn weights with linear regression

### =================== LEARNING WITH PSEUDO INVERSE ================================
coeff2 = fitter.pseudo_inv_fit(matrix = neuronsFireRateTrain, target = inputSignal) # Learn weights with pseudo inverse

### =================== IMPORT TESTING SET FROM DYNAPSE RECORDING ================================
# Same elaborations done for testing set
testing = decoder.import_events("DYNAPSETools/Examples/DynapseSpikesFitter_sine2.aedat")
testing = testing.filter_events(chip_id = 0, core_id = None, neuron_id = None) # Take only first chip events
testingSets = testing.isolate_events_sets(startTriggerNeuron = (0, 2, 64), stopTriggerNeuron = (0, 2, 128)) # Take testing events
testingSetFiltered = testingSets[0].filter_events(chip_id = 0, core_id = [0, 1], neuron_id = None) # Filter trigger events
testingSetFiltered = testingSetFiltered.normalize() # First event will have time 0
testingSetFiltered.plot_events()

# Calculate and plot firing rate matrix
timeStepsTest, neuronsFireRateTest = testingSetFiltered.calculate_firing_rate_matrix(numBins = 20, totNeurons = 1024)
decoder.plot_firing_rate(timeSteps = timeStepsTest, neuronsFireRate = neuronsFireRateTest)

### =================== EVALUATE DIFFERENCE BETWEEN FIRING RATE MATRIXES ==========================
fitter.av_fireRate_matrix_diff(neuronsFireRateTrain, neuronsFireRateTest)

### =================== PREDICTION WITH SKLEARN ================================
prediction = fitter.sklearn_prevision(regr, neuronsFireRateTest)
fitter.prediction_plot(timeStepsTest, inputSignal, prediction)
fitter.prediction_performances(inputSignal, prediction)

### =================== PREDICTION WITH PSEUDO INVERSE ================================
prediction2 = fitter.pseudo_inv_prevision(coefficients = coeff2, matrix = neuronsFireRateTest)
fitter.prediction_plot(timeStepsTest, inputSignal, prediction2)
fitter.prediction_performances(inputSignal, prediction2)

plt.show()