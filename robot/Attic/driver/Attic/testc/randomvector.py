#
# this is the guts of the testc driver. It is a python list structure
# that actually thunks to a C structure where the actual guts are.
#
#
# - stephen -
#

import testc

class RandomVector:
    def __init__(self):
        self.rv = testc.new_RandomVector()
        
    def __len__(self):
        return 3
    
    def __getitem__(self,key):
        if key == 0:
            return testc.RandomVector_x_get(self.rv)
        if key == 1:
            return testc.RandomVector_y_get(self.rv)
        if key == 2:
            return testc.RandomVector_z_get(self.rv)
        
