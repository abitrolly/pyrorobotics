# A Behavior-based control system

from pyro.brain.fuzzy import *
from pyro.brain.behaviors import *
from pyro.brain import select
import math, time

class Avoid (Behavior):
    """Avoid Class"""
    def setup(self): # called when created
        """setup method"""
        self.lasttime = time.time()
        self.count = 0

    def direction(self, dir, dist):
        """ computes direction given an angle"""
        if dir < 0.0:
            return 1.0 - dir
        else:
            return -1.0 - dir

    def update(self):
        if self.count == 50:
            currtime = time.time()
            #print "=======  50 Loops. Average time per loop =", (currtime - self.lasttime)/50.0, "seconds."
            self.count = 0
            self.lasttime =  time.time()
        else:
            self.count += 1
        # Normally :
        # FIX: did have close function; now what?
        close = select(min, "value", self.robot.get('/robot/range/front-all/value,th'))
        close_dist, close_angl = close["value"], close["th"]
        close_angl /= (math.pi)
        #print "Closest distance =", close_dist, "angle =", close_angl
        max_sensitive = self.robot.get('/robot/range/maxvalue') * 0.8
        self.IF(Fuzzy(0.0, max_sensitive) << close_dist, 'translate', 0.0, "TooClose")
        self.IF(Fuzzy(0.0, max_sensitive) >> close_dist, 'translate', .2, "Ok")
        self.IF(Fuzzy(0.0, max_sensitive) << close_dist, 'rotate', self.direction(close_angl, close_dist), "TooClose")
        self.IF(Fuzzy(0.0, max_sensitive) >> close_dist, 'rotate', 0.0, "Ok")

class state1 (State):
    """ sample state """
    def setup(self):
        self.add(Avoid(1, {'translate': .3, 'rotate': .3}))
        print "initialized state", self.name

def INIT(engine): # passes in robot, if you need it
    brain = BehaviorBasedBrain({'translate' : engine.robot.translate, \
                                'rotate' : engine.robot.rotate, \
                                'update' : engine.robot.update }, engine)
    # add a few states:
    brain.add(state1()) # non active

    # activate a state:
    brain.activate('state1') # could have made it active in constructor
    return brain
