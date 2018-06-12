"""Contains a class that represent an input event to DYNAP-se
"""

class InputEvent:
    """Class that represent an input event in DYNAP-se
    """

    def __init__(self, virtualSourceCoreId = None, neuronAddress = None, coreDest = None, address = None, time = None, chipDest = 0):
        """Return a new InputEvent object

Parameters:
    virtualSourceCoreId (int): id of the core where is located the virtual neuron
    neuronAddress (int): id of virtual source neuron
    coreDest (int, hot coded): id of the destination cores where the spike is delivered
    address (int): address of the event (for manual insertions of events)
    time (float): time delay associated with the event

Note:
    coreDest is a 16-bit hot coded number. This means that every coded bit can activate or
    deactivate a destination core, for example::

        - coreDest = 0001 -> to core 0
        - coreDest = 0010 -> to core 1
        - coreDest = 0100 -> to core 2
        - coreDest = 1000 -> to core 3

    Every combination is accepted, for example::

        - coreDest = 0011 -> to core 0 and 1
        - coreDest = 0110 -> to core 2 and 3
        - coreDest = 1111 -> to all cores
"""

        if (virtualSourceCoreId != None) & (neuronAddress != None) & (coreDest != None) & (time != None):
            self.virtualSourceCoreId = virtualSourceCoreId
            self.neuronAddress = neuronAddress
            self.chipDest = chipDest
            self.coreDest = coreDest
            self.create_address_event()
            self.time = time
        elif (address != None) & (time != None):
            self.address = address
            self.time = time
            self.decode_address_event()

### ===========================================================================
    def create_address_event(self):
        """Create an address and time for an event in the spike generator

Parameters:
    None

Note:
    The final address is composed in the following way::

        Bits:
        15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
        |---| chipDest
              |-----------------| neuronAddress
                                  |-| virtualSourceCoreId
                                      |-----| coreDest
"""
        
        self.address = (self.chipDest << 14) & 0xffff |\
                       (self.neuronAddress << 6) & 0xffff |\
                       self.coreDest & 0xf |\
                       (self.virtualSourceCoreId << 4) & 0x30
    
### ===========================================================================
    def decode_address_event(self):
        """Decode event characteristics starting from time and address

Parameters:
    None

Note:
    The final address is composed in the following way::

        Bits:
        13 12 11 10 9 8 7 6 5 4 3 2 1 0
        |-----------------| neuronAddress
                            |-| virtualSourceCoreId
                                |-----| coreDest
"""
        
        self.virtualSourceCoreId = (self.address >> 4) & 0x3
        self.coreDest = self.address & 0xf
        self.neuronAddress = (self.address >> 6) & 0xff