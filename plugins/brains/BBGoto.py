# An example of Blending
# Goto a particular Point
# D.S. Blank

from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *

class Goto (Behavior):
    def setup(self): # called when created
        self.Effects('translate', .3) 
        self.Effects('rotate', .3)
        # Hardcode a position to goto for testing:
        self.goalX = 5.0
        self.goalY = 5.0

    def update(self):
       interval = Fuzzy(0, 2.0) # meters
       right_of_goal = Fuzzy(0.1,   1.0)
       left_of_goal  = Fuzzy(-0.1, -1.0)
       # These angles are in radians:
       phi = self.robot.getAngleToPoint(self.goalX, self.goalY)
       dist = self.robot.getDistanceToPoint(self.goalX, self.goalY)
       # --------------------------------------------
       # Here is an example that does use a discontinuity, but we
       # need to decide to go to left, or right:
       # --------------------------------------------
       # Too much to the left:
       if ( phi < -0.1 ):
          too_left = left_of_goal >> phi;
          self.IF(too_left, 'rotate', - float(too_left))
       # Too much to the right:
       if ( phi > 0.1 ):
          too_right = right_of_goal >> phi
          self.IF(too_right, 'rotate', too_right)
       # Closeness?
       close = interval << dist
       self.IF(close, 'translate', 1.0 - close)
       self.IF(1.0 - float(close), 'translate', 1.0)

class Main (State):
    def setup(self):
        self.add(Goto(1))

def INIT(engine): 
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    brain.add(Main(1)) 
    return brain


