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
        self.lasttime = 0
        self.count = 0

    def direction(self, value):
        if value < 0:
            return -1
        else:
            return 1

    def update(self):
        self.count += 1
        if self.count == 50:
            currtime = time.mktime(time.localtime())
            print "================================Loop in", (currtime - self.lasttime)/50.0, "seconds."
            self.count = 0
            self.lasttime =  time.mktime(time.localtime())
            
        close_dist = self.getRobot().getMin().distance 
        close_angl = self.getRobot().getMin().angle / math.pi
        print "Closest distance is:", close_dist
        self.IF(Fuzzy(1.0, 3.0) << close_dist, 'translate', 0)
        self.IF(Fuzzy(1.0, 3.0) << close_dist, 'rotate', \
                -self.direction(close_angl) * 1)

class state1 (State):
    def init(self):
        self.add(StraightBehavior(1))
        self.add(Avoid(1))
        print "initialized state", self.name

    def onActivate(self):
        self.count = 0

    def update(self):
        print "State 1"
        if self.count == 0:
            self.goto("state2")
        else:
            self.count += 1

class state2 (State):
    def init(self):
        self.add(StopBehavior(1))
        print "initialized state", self.name

    def update(self):
        print "State 2"
        # save the current readings
        self.behaviorEngine.history[1]['speed'] = self.behaviorEngine.robot.senseData['speed']
        self.behaviorEngine.history[1]['ir'] = self.behaviorEngine.robot.senseData['ir']
        self.goto("state3")

class state3 (State):
    def init(self):
        print "initialized state", self.name
        self.count = 0

    def onActivate(self):
        self.count += 1

    def update(self):
        print "State 3"
        self.behaviorEngine.camera.snap("som2/snap-%d.pgm" % self.count) # can name the file right here
        # save IR, motors
        fp = open("som2/snap-%d.dat" % self.count, "w")
        fp.write("translate=%f\n" % self.behaviorEngine.history[2]['translate'])
        fp.write("rotate=%f\nspeed=" % self.behaviorEngine.history[2]['rotate'])
        for s in self.behaviorEngine.history[2]['speed']:
            fp.write("%d " % s)
        fp.write("\nir=")
        for s in self.behaviorEngine.history[2]['ir']:
            fp.write("%d " % s)
        fp.write("\n")
        fp.close()
        self.goto("state1")

def INIT(engine): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active
    brain.add(state2()) # non active
    brain.add(state3()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    brain.init()

    import pyro.camera
    brain.camera = pyro.camera.Camera()

    return brain
