# A Behavior-based system

from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *
from pyro.brain.behaviors.core import *  # Stop

import math
from random import random
import time

class Avoid (Behavior):
    def init(self): # called when created
        self.Effects('translate', .3) 
        self.Effects('rotate', 1)
        self.lasttime = time.mktime(time.localtime())
        self.count = 0

    def direction(self, value):
        if value < 0:
            return -1
        else:
            return 1

    def update(self):
        if self.count == 50:
            currtime = time.mktime(time.localtime())
            print "=======  1 Loop in", (currtime - self.lasttime)/50.0, "seconds."
            self.count = 0
            self.lasttime =  time.mktime(time.localtime())
        else:
            self.count += 1
            
        close_dist = self.getRobot().getMin().distance 
        close_angl = self.getRobot().getMin().angle / math.pi
        print "Closest distance is:", close_dist
        if self.getRobot().type == 'khepera':
            self.IF(Fuzzy(40.0, 60.0) << close_dist, 'translate', 0)
            self.IF(Fuzzy(40.0, 60.0) << close_dist, 'rotate', \
                    -self.direction(close_angl) * 1)
        else: # saphira, others:
            self.IF(Fuzzy(.2, 1.0) << close_dist, 'translate', 0)
            self.IF(Fuzzy(1.0, 2.0) << close_dist, 'rotate', \
                    -self.direction(close_angl) * 1)
            

class state1 (State):
    def init(self):
        self.add(StraightBehavior(1))
        self.add(Avoid(1))
        print "initialized state", self.name

def INIT(robot): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : robot.translate, \
                                'rotate' : robot.rotate, \
                                'update' : robot.update }, robot)
    # add a few states:
    brain.add(state1()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    brain.init()
    return brain
