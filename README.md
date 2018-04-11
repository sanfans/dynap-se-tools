# DYNAPSETools
The repository contains a set of tools that are useful to work with [DYNAP-se board](https://inilabs.com/products/dynap/).
It contains:
  * **DynapseNetGenerator** : permit to create a .txt file with encodes connections that can be programmed using [netparser](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.crkj98n9ian3) module.
  * **DynapseOutDecoder** : permit to retrieve from DYNAP-se recordings (.aedat files) spikes and plot them
  * **DynapseSpikesFitter** : permit to make training and testing starting from firing rate matrix of recordings
  * **DynapseSpikesGenerator** : permit to create a .txt file which encodes inputs that must be sent to DYNAP-se, using [FPGASpikeGen](https://inilabs.com/support/hardware/user-guide-dynap-se/#h.3prdeugulxol) module.
### How to import
* Clone the repository with git in your python work folder
* Place the script that should use this folder in the same folder of the library

To import a module write:
```python
import DYNAPSETools.dynapseNetGenerator as DNG
import DYNAPSETools.dynapseOutDecoder as DOD
import DYNAPSETools.dynapseSpikesFitter as DSF
import DYNAPSETools.dynapseSpikesGenerator as DSG
```
To use functions contained in the modules write
```python
DNG.functionToCall(...)
DOD.functionToCall(...)
DSF.functionToCall(...)
DSG.functionToCall(...)
```

### Further documentation
Written code in the library is well documented. Every module and every function has a description, complete of all input and output parameters.

At [this](https://sanfans.github.io/DYNAPSETools/_build/html/index.html) link is present the repository GitHub website with all the informations you need, as well as autogenerate code documentation, search engine and modules index visualization.

### Tutorial
Inside the repository is present a folder called "tutorialFiles". There inside are present some python scripts doing elaborations with the
library modules. They are just a collection of instructions, for a complete guide look at the online guide, below the module you
want to know more.
