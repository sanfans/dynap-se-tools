# DESCRIPTION: Contains a class that represent an input event to DYNAP-se

class InputEvent:
    """Class that represent an input event in DYNAP-se
    """

    def __init__(self, virtualSourceCoreId = None, neuronAddress = None, coreDest = None, address = None, time = None):
        if (virtualSourceCoreId != None) & (neuronAddress != None) & (coreDest != None) & (time != None):
            self.virtualSourceCoreId = virtualSourceCoreId
            self.neuronAddress = neuronAddress
            self.coreDest = coreDest
            self.create_address_event()
            self.time = time
        elif (address != None) & (time != None):
            self.decode_address_event()
            self.address = address
            self.time = time

### ===========================================================================
    def create_address_event(self):
        """Create an address and time for an event in the spike generator
        
Bit structure:
13 12 11 10 9 8 7 6 5 4 3 2 1 0
|-----------------| neuronAddress
                    |-| virtualSourceCoreId
                        |-----| coreDest
coreDest is hard coded -> 1111 (15 decimal) means to all cores
"""
        
        self.address = (self.neuronAddress << 6) & 0xffff | self.coreDest & 0xf | (self.virtualSourceCoreId << 4) & 0x30
    
### ===========================================================================
    def decode_address_event(self):
        """Decode event characteristics starting from time and address
        
Bit structure:
13 12 11 10 9 8 7 6 5 4 3 2 1 0
|-----------------| neuronAddress
                    |-| virtualSourceCoreId
                        |-----| coreDest
coreDest is hard coded -> 1111 (15 decimal) means to all cores
"""
        
        self.virtualSourceCoreId = (address >> 4) & 0x3
        self.coreDest = address & 0xf
        self.neuronAddress = (address >> 6) & 0xff