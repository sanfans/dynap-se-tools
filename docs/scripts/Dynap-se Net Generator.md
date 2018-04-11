# Dynap-se Net Generator
## API
* [dynapseNetGenerator](dynapseNetGenerator.html) module
* [DeviceConnections](DeviceConnections.html) class
* [DevicePopulation](DevicePopulation.html) class
* [DeviceNeuron](DeviceNeuron.html) class

## Table of content
* [Description](#description)
* [Functionalities](#functionalities)
* [Tutorial](#tutorial)

## Description
DYNAP-se control software cAER contains an useful module called netParser.
This module allows the user to implement networks in Dynap-se directly writing them
in a .txt, using a userfriendly format.
In this way is easy to construct and check the connections
that has been performed. However manual approach works for simple networks
that does not require fancy probability evaluations or strange connectivity shapes.

For complex networks an higher level of abstraction is required. This part of Dynap-se
tools take care of this functionality of cAER, trying to help the user using high
level structures as Population and Connections in order to create the final .txt file
with all the connections that must be written on Dynap-se.

An example of a .txt connections file is the following:

```
#!======================================== Connecting InputLayer->MiddleLayer
U04C00N001->3-1-U00C01N000
U04C00N001->3-1-U00C01N001
U04C00N001->3-1-U00C01N002
#!======================================== Connecting MiddleLayer->OutputLayer
U00C02N000->3-1-U00C03N016
U00C02N001->3-1-U00C03N016
U00C02N002->3-1-U00C03N016
```

Every line is a connection between a source neuron (on the left of the arrow,
i.e. U04C00N001) and a destination one (on the right of the arrow, i.e. U00C01N000).
Connection type and weight are specified just after the arrow, i.e. 3-1 (3 is the type
and 1 is the connection weight).

The library, moreover, try to create a bridge between Brian2 network simulation software
and Dynap-se, creating a compatibility between them. From a Brian2 network it is
possible, with few lines, transform in a loadable Dynap-se network.

## Functionalities
* Create network for Dynap-se using high level concept as Population and Connection
* Use the power of Brian2 to create complex connectivity, and than translate them into
  Dynap-se one.

## Tutorial
This tutorial explain a reasonable way of using Dynap-se net generator module
to create interconnected networks of neurons. During the tutorial we will create
a network with a total of 20 neurons organized in the following way:

- InputLayer: 1 input neuron coming from Dynap-se virtual chip
- MiddleLayer: 1 column of 10 neurons connected to the input
- OutputLayer: 2 neuron connected to the MiddleLayer with a certain connectivity

In a first approach we will define biologically plausible connections. This means that
every neuron will have an associated type, excitatory/inhibitory. The connections
that a neuron can perform depend esclusively on his type. If excitatory,
will be excitatory, if inhibitory, will be inhibitory. The topology of the network
will be:

- InputLayer: excitatory
- MiddleLayer: first 50% excitatory, second 50% inhibitory
- OutputLayer: excitatory (not really important since there are no recurrent connections)

The same network will be created in different ways, according the situation in which you are in:
1. You want to create the network from scratch
2. You have a Brian2 network already created
3. You have an NCSBrian2 network already created

In the second part we will break biology rules, allowing our excitatory input neuron
be inhibitory for some of MiddleLayer neurons. This is possible in Dynap-se but
leads to networks that are not biologically plausible.

### Import libraries
As said in the Repository README, is recommended to setup your python environment
such to have the working directory in the same parent folder as the one of the library.
As alternative, you can add the library directory to the python path.

To import the module:
```python
import DYNAPSETools.dynapseNetGenerator as DNG
``` 

We will need also numpy and matplot lib for our elaborations:
```python
import numpy as np
import matplotlib.pyplot as plt
```

### Initialization
Before starting creating the network, i suggest to write all preliminary code, like:

```python
np.random.seed(0) # Set seed for the random number generation
plt.close("all") # Close all the plots that has been created
                 # in the previous run
```

### Create Network from scratch (Method 1)
#### Create populations
In this section we start creating the populations we need for the network and
locate them inside Dynap-se board:
- InputLayer: Virtual Chip (U = 4), Core 0 (C = 0), Neuron 1 (N = 1) 
- MiddleLayer: Physical Chip 0 (U = 0), Core 0 (C = 0), 10 Neurons starting from
  position 0
- OutputLayer: Physical Chip 0 (U = 0), Core 1 (C = 1), Neurons 16 and 32

We start from the InputLayer population. This will be a population present in 
the virtual chip, so not physically present in Dynap-se. It can be used to
create spike patterns with certain timings, and send them to physical populations.

```python
U, C, start_neuron = 4, 0, 1
size = 1
InputLayer = DNG.DevicePopulation(name = "InputLayer",
                                  chip_id = U, core_id = C,
                                  start_neuron = start_neuron,
                                  size = size, neuronsType = "fExc")
```

A possible alternative to define the population is using neurons_id parameter:

```python
U, C, N = 4, 0, 1
InputLayer = DNG.DevicePopulation(name = "InputLayer",
                                  chip_id = U, core_id = C,
                                  neurons_id = N, neuronsType = "fExc")
```

The type of neuron if "fExc" (fast excitatory), one of 4 available in Dynap-se.

In the same way as before we define the MiddleLayer population:

```python
U, C, start_neuron = 0, 1, 0
size = 10
MiddleLayer = DNG.DevicePopulation(name = "MiddleLayer",
                                   chip_id = U, core_id = C,
                                   start_neuron = start_neuron, size = size)
```

Differently as before, here we have not specified a population type. For default
configuration, it will be set as fast excitatory. But we want 50% excitatory
and 50% random inhibitory. How can be procede? We can select manually which
neurons we want as excitatory and which inhibitory:

```python
neuronsIndexes = [5, 6, 7, 8, 9] # Choose neurons
MiddleLayer[neuronsIndexes]["neuronsType"] = "fInh" # Set to fast inhibitory
```

With this method we are extracting a portion of the MiddleLayer population, i.e.
```MiddleLayer[neuronsIndexes]```, assigning the property "neuronsType" of the neurons in
this portion to fast inhibitory.

In this way we set 5 neurons to fInh. As alternative, if we wanted random indexes
for the inhibitory neurons, here is an example:

```python
populationIndexes = np.arange(0, size) # From 0 to size - 1
# Get a shuffled list
neuronsIndexes = np.random.permutation(populationIndexes)
# Take half of them
neuronsIndexes = neuronsIndexes[:int(size / 2)]
# Set to fast inhibitory
MiddleLayer[neuronsIndexes]["neuronsType"] = "fInh" 
```

We can now create the OutputLayer:

```python
U, C = 0, 1
N = [16, 32]
OutputLayer = DNG.DevicePopulation(name = "OutputLayer",
                                   chip_id = U, core_id = C, neurons_id = N,
                                   neuronsType = "fExc")
```

In this case we have specified the neurons id directly with neurons_id parameter.
Given the separation between the two neurons, it would have been impossible to do it
using just "start_neuron" and "size" parameters.

#### Create Connections
Now is time to create connections between the neurons. To do so, we have to create
a DeviceConnection object for each pair of populations we want to connect. The way
in which connections are specified is very simple and, unfortunately, not flexible.
If you want more flexibility, consider moving to Method 2 of defining a network i.e.
creating a brian2 network.

To create a connection you have to specify 3 arrays:

- i : vector containing the source connections neurons id
- j : vector containing the destination connections neurons id
- w : vector containing the weight of the connections

They must have the same lenght, equal to the number of connections you want to perform.

Connections between InputLayer and MiddleLayer are all to all:

```python
size = 10 # 10 connections
# i = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] -> the only input neuron
i = np.zeros(size)
# j = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] -> all MiddleLayer neurons
j = np.arange(size)
# all weights equal to 1 
w = np.ones(size) 
InputLayerToMiddleLayer = DNG.DeviceConnections(sourcePop = InputLayer,
                                                targetPop = MiddleLayer,
                                                i = i, j = j, w = w)
```

Connections between MiddleLayer and OutputLayer are manually specified. First 5
neurons of MiddleLayer are connected to neuron 0 of OutputLayer, the other ones
to neuron 1 of OutputLayer:

```python
i =  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # All Middle neurons
j = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1] # Half to 0 and half to 1
w = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # all weights equal to 1
MiddleLayerToOutputLayer = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 i = i, j = j, w = w)
```

Now that we have the connections, we have to write them in the output txt file.
To do so, go to [Write Connections](#write-connections-on-output-file) section.

### Create Network from Brian2 one (Method 2)
### Initialization
In order to create a network starting from Brian2 one, we should first import brian2
module:

```python
from brian2 import start_scope, Network, NeuronGroup, Synapses,\
SpikeGeneratorGroup, SpikeMonitor, metre, second, volt, mV, ms, us,\
defaultclock, prefs
```

Usually i import from Brian2 only the objects that i need.

Moreover add this instruction:

```python
prefs.codegen.target = "numpy"
```

To prevent Brian2 using C++ compilation, if you have not the libraries installed on your pc.


#### Convert populations
With respect to method 1, here we have already populations and connections specified, but 
we need to place them in Dynap-se. To do so, we use the same functions as in method 1,
but we don't define some informations, because already contained in the Brian2
population object.

Before going on, i assume that are present population objects specified as here below
(... indicate custom user settings):

```python
brianInputLayer = NeuronGroup(1, ...)
brianMiddleLayer = NeuronGroup(10, ...)
brianOutputLayer = NeuronGroup(2, ...)
```

and the topology of MiddleLayer is defined as here below:

```python
middleLayerInhNeurons = [5, 6, 7, 8, 9]
```

Here is an example of Brian2 code that perform the same connections as in Method 1,
with the same populations. In this case, since no simulation is performed, no neuron
model has been defined. Pay attention that, instead, a weight value "w" in the model must
appear in Synapses model, otherwise no weight is set for the device connections.

```python
# Populations definition
brianInputLayer = NeuronGroup(1, model = "", name='brianInputLayer')
brianMiddleLayer = NeuronGroup(10, model = "", name='brianMiddleLayer')
brianOutputLayer = NeuronGroup(2, model = "", name='brianOutputLayer')

middleLayerInhNeurons = [5, 6, 7, 8, 9]

# Connections definition
brianInputLayerTobrianMiddleLayer = Synapses(brianInputLayer,
                                             brianMiddleLayer,
                                             model = "w : 1",
                                             name = "brianInputLayerTobrianMiddleLayer")
brianInputLayerTobrianMiddleLayer.connect(True)
brianInputLayerTobrianMiddleLayer.w = 1

brianMiddleLayerTobrianOutputLayer = Synapses(brianMiddleLayer,
                                              brianOutputLayer,
                                              model = "w : 1",
                                              name = "brianInputLayerTobrianMiddleLayer")
brianMiddleLayerTobrianOutputLayer.connect(condition = "i < 5 and j == 0")
brianMiddleLayerTobrianOutputLayer.connect(condition = "i >= 5 and j == 1")
brianMiddleLayerTobrianOutputLayer.w = 1
```

To convert them in Dynap-se 2 population, we can use the same code as for Method 1,
this time using neuronsObj option:

```python
U, C, N = 4, 0, 1
InputLayer = DNG.DevicePopulation(neuronsObj = brianInputLayer,
                                  chip_id = U, core_id = C,
                                  neurons_id = N,
                                  neuronsType = "fExc")

U, C, start_neuron = 0, 1, 0
size = 10
MiddleLayer = DNG.DevicePopulation(neuronsObj = brianMiddleLayer,
                                   chip_id = U, core_id = C,
                                   start_neuron = start_neuron)

# Set to fast inhibitory
MiddleLayer[middleLayerInhNeurons]["neuronsType"] = "fInh" 

U, C = 0, 1
N = [16, 32]
OutputLayer = DNG.DevicePopulation(neuronsObj = brianOutputLayer,
                                   chip_id = U, core_id = C,
                                   neurons_id = N,
                                   neuronsType = "fExc")
```

As you can notice, comparing with Method 1, we don't specify any "size" and "name"
parameter. In fact, these values are already encoded inside the brian2 population object,
indicated with the "neuronsObj" parameter. All we need to specify is the location
in Dynap-se of the first neuron of the population, or the list of neurons we want
to select. In this last case we should make sure that the lenght of the list is equal
to the population size.

At this point, we can go on converting the connections

#### Convert connections
Converting brian2 connections is pretty simple. We should just specify, for each connection,
which Device population are involved, and supply the link to the brian2 synapse object.
The following code does this for the two synapses objects:

```python
InputLayerToMiddleLayer = DNG.DeviceConnections(sourcePop = InputLayer,
                                                targetPop = MiddleLayer,
                                                synapsesObj = brianInputLayerTobrianMiddleLayer)

MiddleLayerToOutputLayer = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 synapsesObj = brianMiddleLayerTobrianOutputLayer)
```

Now that we have the connections, we have to write them in the output txt file.
To do so, go to [Write Connections](#write-connections-on-output-file) section.

### Create Network from NCSBrian2 one (Method 3)
If your network is defined using the NCSBrian2, no problem. Follow the steps of Method 2,
substituting accordingly:

- NeuronGroup object with the corrispondend Neurons object of NCSBrian2 library
- Synapses object with the corrispondent Connection object of NCSBrian2 library

### Non biologically plausible connections
Now lets suppose we want to create some connections and be able to specify their
type, indipendenly from the type of the source connection neuron. For example, we
want to connect the first 5 neurons of MiddleLayer, that are excitatory neurons,
to neuron 1 of OutputLayer, with inhibitory connections. To do so, we can procede in
different ways:

- Create connections manually, like Method 1. This can be also applied when using Method 2 or 3
- Create new synapse object and create connetions through brian2, as in Method 2

#### Method 1
Proceeding as done for the connections of method 1, we can create this new connections

```python
i =  [0, 1, 2, 3, 4] # First half Middle Layer neurons
j = [1, 1, 1, 1, 1] # All to neuron 1 of Output Layer
w = [1, 1, 1, 1, 1] # all weights equal to 1
MiddleLayerToOutputLayer2 = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                 targetPop = OutputLayer,
                                                 i = i, j = j, w = w,
                                                 connTypes = "fInh")
```

With respect to the other connections performed, in this case we specify the
"connTypes" parameter, forcing the first 5 neurons (excitatory) to create an
inhibitory connection with neuron 1 of OutputLayer.

#### Method 2
Supposing that the new connections between MiddleLayer and OutputLayer are
included in the brian2 network, as shown in the code below:

```python
brianMiddleLayerTobrianOutputLayer2 = Synapses(brianMiddleLayer,
                                               brianOutputLayer, model = "w : 1",
                                               name = "brianMiddleLayerTobrianOutputLayer2")
brianMiddleLayerTobrianOutputLayer2.connect(condition = "i < 5 and j == 1")
brianMiddleLayerTobrianOutputLayer2.w = 1
```

We can simply add the new inhibitory connections as done for Method 2, specifying this
time the connTypes parameter such to obtain fast inhibitory connections:

```python
MiddleLayerToOutputLayer2 = DNG.DeviceConnections(sourcePop = MiddleLayer,
                                                  targetPop = OutputLayer,
                                                  synapsesObj = brianMiddleLayerTobrianOutputLayer2,
                                                  connTypes = "fInh")
```

### Write connections on output file
To write the created connections in the output file, procede in the following way:

```python
DNG.write_connections(InputLayerToMiddleLayer, MiddleLayerToOutputLayer, brianMiddleLayerTobrianOutputLayer2
                      fileName = "NetGenTutorial.txt")
```

An output file will be written in the folder where are you working in with python