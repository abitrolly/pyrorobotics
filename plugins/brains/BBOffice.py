# A Really bad example of Goto Office
# Thou shall not emulate this style... it is not reactive!
# You should make yours based on walls, doorways, etc.
# -dsb

from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *
from pyro.brain.behaviors.core import *  # Stop

import math
from random import random
import time

# A Map to the office:

#           F
#           |
#           |
#           E----------------------------------D
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                                              |
#                       B----------------------C
#                       |
# Start ----------------A
#

class Straight (Behavior):
    def init(self): 
        self.Effects('translate', .1) 
        self.Effects('rotate', .1) 

    def update(self):
        self.IF(1, 'translate', .2) 
        self.IF(1, 'rotate', 0) 

class TurnLeft (Behavior):
    def init(self):
        self.Effects('translate', .2) 
        self.Effects('rotate', .1)

    def update(self):
        self.IF(1, 'rotate', .1)
        self.IF(1, 'translate', 0) 

class TurnRight (Behavior):
    def init(self):
        self.Effects('translate', .2) 
        self.Effects('rotate', .1)

    def update(self):
        self.IF(1, 'rotate', -.1)
        self.IF(1, 'translate', 0) 

class Start (State):
    # go straight for 8 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 8.0:
            self.goto('A1')

class A1 (State):
    # turn left 90 degrees
    def init(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.getRobot().get('robot', 'th')

    def update(self):
        th = self.getRobot().get('robot', 'th')
        if angleAdd(th, - self.th) > 90: 
            self.goto('A2')

class A2 (State):
    # go straight for 1.5 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 1.5:
            self.goto('B1')

class B1 (State):
    # turn right 90 degrees
    def init(self):
        self.count = 0
        self.add(TurnRight(1))

    def onActivate(self):
        self.th = self.getRobot().get('robot', 'th')

    def update(self):
        th = self.getRobot().get('robot', 'th')
        if angleEqual(angleAdd(th, -self.th), 270)
            self.goto('B2')
            
class B2 (State):
    # go straight for 6.5 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 6.5:
            self.goto('C1')

class C1 (State):
    # turn left 90 degrees
    def init(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.getRobot().get('robot', 'th')

    def update(self):
        th = self.getRobot().get('robot', 'th')
        if angleAdd(th, - self.th) > 90: 
            self.goto('C2')

class C2 (State):
    # go straight for 8 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 8.0:
            self.goto('D1')

class D1 (State):
    # turn left 90 degrees
    def init(self):
        self.count = 0
        self.add(TurnLeft(1))

    def onActivate(self):
        self.th = self.getRobot().get('robot', 'th')

    def update(self):
        th = self.getRobot().get('robot', 'th')
        if angleAdd(th, - self.th) > 90: 
            self.goto('D2')
            
class D2 (State):
    # go straight for 12 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 12.0:
            self.goto('E1')

class E1 (State):
    # turn right 90 degrees
    def init(self):
        self.count = 0
        self.add(TurnRight(1))

    def onActivate(self):
        self.th = self.getRobot().get('robot', 'th')

    def update(self):
        th = self.getRobot().get('robot', 'th')
        if angleAdd(self.th, -th) < 270: 
            self.goto('E2')
            
class E2 (State):
    # go straight for 2 meters
    def init(self):
        self.add(Straight(1))

    def onActivate(self): # method called when activated or gotoed
        self.startX = self.getRobot().get('robot', 'x') 
        self.startY = self.getRobot().get('robot', 'y') 
        
    def update(self):
        x = self.getRobot().get('robot', 'x')
        y = self.getRobot().get('robot', 'y')
        dist = distance( self.startX, self.startY, x, y) 
        if dist > 2.0:
            self.goto('Done')

class Done(State):
    pass

def INIT(robot): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : robot.translate, \
                                'rotate' : robot.rotate, \
                                'update' : robot.update }, robot)
    # add a few states:
    brain.add(Start(1)) # active
    brain.add(A1()) # active
    brain.add(A2()) # active
    brain.add(B1()) # non active
    brain.add(B2()) # non active
    brain.add(C1()) # non active
    brain.add(C2()) # non active
    brain.add(D1()) # non active
    brain.add(D2()) # non active
    brain.add(E1()) # non active
    brain.add(E2()) # non active
    brain.add(Done()) # non active

    brain.init()
    return brain
