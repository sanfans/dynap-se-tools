# Dynap-se Out Decoder
## API
* [dynapseOutDecoder](dynapseOutDecoder.html) module
* [EventsSet](EventsSet.html) class

## Table of content
* [Description](#description)
* [Functionalities](#functionalities)
* [Tutorial](#tutorial)

## Description
Dynap-se contains a module called OutputFile, able to collect events from Dynap-se
and storing them in a compressed file format, called AEDAT. This functionalities
allow people to make offline analysis of data recorded from an experiment, for
example for training.

The library allow the user to import events from AEDAT file and make simple manipulations
and plots.

## Functionalities
- Import events from AEDAT file
- Create raster plots
- Filter chip and neuron events, to take only the one you need
- Extract spikes between two neuron events
- Calculate firing rate matrix

## Tutorial

In this tutorial we decode events from a recording done in Dynap-se and make some
simple elaborations.

### Import libraries
As said in the Repository README, is recommended to setup your python environment
such to have the working directory in the same parent folder as the one of the library.
As alternative, you can add the library directory to the python path.

To import the module:
```python
import DYNAPSETools.dynapseOutDecoder as DOD
``` 

We will need also numpy and matplot lib for our elaborations:

```python
import numpy as np
import matplotlib.pyplot as plt
```

### Initialization
Before starting creating the network, i suggest to write all preliminary code, like:

```python
plt.close("all") # Close all the plots that has been created
                 # in the previous run
```

### Import events
When we import the events we create an EventSet, an object containing all the informations
about the events of the registration, like chip_id, core_id, neuron_id
and time of every event. To do so, we use:

```python
fileName = "./DYNAPSETools/tutorialFiles/outTutorial.aedat"
decEvents = DOD.import_events(fileName)
```

fileName is name of the .aedat file from which you want to import the events. In this
case is a reocrding 

decEvents is the EventsSet object containing all recorded events.

Timestamp in Dynap-se are absolute times expressed in us scale and referes to the
time when the control software was started. Sometime this could be annoying and
would be better to have the recording starting from 0.

Still absolute times can be useful to stack multiple recordings
together, after having extracted event from them. However, writing:

```python
decEvents = decEvents.normalize()
```

we replace the previous EventsSet with a new normalised one.

A good idea now would be to make a raster plot of the recording.
The implemented raster plot let you see are all events in all 4 chips colored as
the colors present in Dynap-se spike visualizer (green, purple, red, yellow
respectevely for Core 0, 1, 2, 3).

According to the core from which they come from, NO MATTER WHICH IS THE CHIP, events
will be painted with these 4 colors. So, at this point, a green dot can refer to
Chip 0, 1, 2 or 3. Be aware of that:
  
```python  
decEvents.plot_events()
```

### Filter events and extract experiments
Usually what happens is that you are interested only in the activity of a limited
range of neurons present in the recording. What you need in this case is to filter
the events of the neuron you are not interested on.

To prepare a filter, we just have to create a list of neurons we want to keep,
as well as a list of cores.
For now it's not possible to filter more than one chip at a time. This means
that or you take event from all chips or just one.

In this example i filter all neurons but for the neurons in core0 and core1 of 
chip 0, the one i was using.

```python  
filterCore0 = np.arange(0, 64) # Taking neurons from 0 to 63
filterCore1 = np.arange(0, 256) # Taking neurons from 0 to 256
```
    
Now we can combine the two filters together, one for each core and apply the
filter. For cores we have jsut a list, while for neurons we have a list of lists

```python  
neuron_id_filter = [filterCore0, filterCore1]
core_id_filter = [0, 1]
decFilteredEvents = decEvents.filter_events(chip_id = 0, core_id = core_id_filter,
                                                neuron_id = neuron_id_filter) # Take only events i need
 ```
  
If now we make a new raster plot we should notice that some events were filtered away:

```python      
decFilteredEvents.plot_events()
```

Until now we have imported and filtered the events recorded from Dynap-se. Still
remains a big problem: how can be synchronize with the input we have sent? in other
words, how can we extract the analisys or, as we will call it later, the experiment
we have done?

We could certaintly manually filter the events until we are sure that the remaining
one are part of our analysis but this would change for every recording so ...
how do that automatically?

The idea is pretty simple: design the analysis such to stimulate just before and just
after our experiment two physical neurons, that will become the start trigger neuron and the
stop trigger neuron. Then, from the recorded event list, extract the events
present between this two neurons. In other words, start and stop trigger works
as synchronizers for the analysis, determining the timing borders in which that
happened. 

Starting from the previous EventsSet, we separate each experiment from the other
one, collecting them in a list. What we will obtain is a list of EventsSet objects, each one
containing only the events belonging to a certain experiment.
Start and Stop trigger neurons are included in the set, so that we have the
same starting and ending times to help for future analysis

```python    
extractedEvents = decFilteredEvents.isolate_events_sets(startTriggerNeuron = (0, 0, 128),
                                                        stopTriggerNeuron = (0, 0, 192),
                                                        maxNumber = 5)
```

In this case i suppose to use two neurons: neurons 128 and 192 of core 0, chip 0 to encode
respectively the start and stop experiment. Before sending the actual input, i send an event
to the start neuron, as well as just after the input has finished (or after a certain delay).
extractedEvetns is a list of EventsSet with all the experiments that are present between start
neuron event and stop neuron event.

Note that we have set the maxNumber parameter on isolate_events_sets function. This means that in the list
we will have a maximum 5 EventsSet, if the algorithm can find more or equal this number. 

TIt is possible to plot automatically all the EventsSet that has been extracted in the following way:

```python   
DOD.plot_events(*extractedEvents)_
```

5 figures will be opened, plotting all the events contained in the 5 extracted EventsSet. Try changing
maxNumber parameter and see the effect in the plots (put it None to extract all experiments).

It is possible to plot a certain extracted experiment in the following way:

```python 
extractedEvents[2].plot_events()
```

In this case i plot the events of the second eexperiment in the list

### Example of events post processing
Now, for example, we suppose we want to calculate, for every extracted experiment, the firing
rate matrix associated to the EventsSet. To do so, we can use the following code:

```python
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
```

In this code we simply create an empty list of time and firing rate matrixes. The time will contain the
end times of every time bin in which the firing rate is evaluated. Every matrix, instead, contains
a matrix where in every line are present the firing rates of a the neurons for all the time bins.

In general the timeBins are the same if the experiments lenghts are the same. If this is the case,
it is possible to transform the list of matrixes and times in arrays. In this way is much simpler
operating with these data.

In case the lenght of each experiment is different, this transformation cannot be done and the
conversion in array will raise an error. In this case is necessary to work with the lists or
try to find a set of experiments with the same lenght.