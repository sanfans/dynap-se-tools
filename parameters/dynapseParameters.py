"""Contains a important parameters of Dynap-se board"""

dynapseNeuronTypes = {"sInh": 0,
                      "fInh": 1,
                      "sExc": 2,
                      "fExc": 3}

dynapseStructure = {"nNeuronsPerCore" : 256,
                    "nCoresPerChip" : 4,
                    "nChipPerDevice" : 4,
                    "virtualChipCode" : 4,
                    "nNeuronsPerChip" : 1024}