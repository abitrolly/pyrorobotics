# -------------------------------------------------------
# This robot is so simple, it doesn't even need to connect
# to a sim or real robot!
# -------------------------------------------------------

from pyro.robot import Robot

class SimpleRobot(Robot):
    # This method handles the engine when it tries to stop
    # the robot. 
    def act(self, action = '', value1 = '', value2 = ''):
        print "Acting: action =", action, "v1 =", value1, "v2 =", value2
        pass
    
    def __init__(self):
        Robot.__init__(self, "SimpleRobot", "simplerobot")
        # -------------------------------------------
        # These vars are assumed (currently) to exist
        # so that the engine can stop the robot:
        # -------------------------------------------
        self.dev = self
        self.senses  = {} 
        self.controls = {}
        # Add the basics. These are just stubs:
        self.controls['update'] = self.act
        self.controls['translate'] = self.act
        self.controls['rotate'] = self.act
        self.controls['move'] = self.act

    def _draw(self,options,renderer):
        # do something to draw yourself
        pass

    def disconnect(self):
        # override so no complaining
        pass

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes no params, and returns a Robot object:
# -------------------------------------------------------

def INIT():
    return SimpleRobot()
