#
#
# a constant from C
#
# - stephen -
#

import testc 

class Pi:
    def __init__(self):
        self.pi = testc.new_Pi()

    def __float__(self):
        return testc.Pi_value_get(self.pi)
