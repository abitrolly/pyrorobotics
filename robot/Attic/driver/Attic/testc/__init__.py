#
# This is an example driver for interfacing with C. It is also an example
# of a driver 'implemented as a directory'. The pure python test driver is
# is a driver 'implemented as a file'.
#
# - stephen - 
#

from pyro.robot.driver import *
import pyro.geometry as geometry
from randomvector import *
from constant import *

class TestCDriver(Driver):
    def __init__(self):
        Driver.__init__(self)

        self.senses['tc pi'] = Sense([geometry.AffineVector()],
                                     [Pi()])
        
        self.senses['tc random'] = Sense([geometry.AffineVector()],
                                               [RandomVector()])
