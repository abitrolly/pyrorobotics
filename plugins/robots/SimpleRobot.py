# -------------------------------------------------------
# This robot is so simple, it doesn't even need to connect
# to a sim or real robot!
# -------------------------------------------------------

from pyro.robot import Robot

class SimpleRobot(Robot):
    # This method handles the engine when it tries to stop
    # the robot. 
    def act(self, action = '', value1 = '', value2 = ''):
        #print "Acting: action =", action, "v1 =", value1, "v2 =", value2
        pass
    
    def setup(self):
        # -------------------------------------------
        # These vars are assumed (currently) to exist
        # so that the engine can stop the robot:
        # -------------------------------------------
        self.dev = self
        self.senses  = {}
        self.senses['robot'] = {}
        self.senses['robot']['x'] = lambda dev: 0
        self.senses['robot']['y'] = lambda dev: 0
        self.senses['robot']['th'] = lambda dev: 0
        self.senses['robot']['stall'] = lambda dev: 0
        self.senses['self'] = self.senses['robot']
        self.senses['range'] = {}
        self.senses['range']['value'] = lambda dev, pos: 0
	self.senses['range']['count'] = lambda self: 8
	self.senses['range']['type'] = lambda self: 'range'
        self.senses['range']['maxvalue'] = lambda dev: 1.0
        self.senses['range']['units'] = lambda self: "ROBOTS"
        self.senses['range']['x'] = lambda self, pos: 0
        self.senses['range']['y'] = lambda self, pos: 0
        self.senses['range']['th'] = lambda self, pos: 0

        self.controls = {}
        # Add the basics. These are just stubs:
        self.controls['update'] = self.act
        self.controls['translate'] = self.act
        self.controls['rotate'] = self.act
        self.controls['move'] = self.act
        self.sensorSet = {'all': range(8),
                          'front' : (2, 3), 
                          'front-left' : (0, 1), 
                          'front-right' : (4, 5),
                          'front-all' : (1, 2, 3, 4),
                          'left' : (0, ), 
                          'right' : (5, ), 
                          'left-front' : (0, ), 
                          'right-front' : (5, ), 
                          'left-back' : (7, ), 
                          'right-back' : (6, ), 
                          'back-left' : (7, ), 
                          'back-right' : (6, ), 
                          'back-all' : (6, 7), 
                          'back' : (6, 7)} 

    def _draw(self,options,renderer):
        # do something to draw yourself
        pass

    def disconnect(self):
        # override so no complaining
        pass

    def getPose(self):
        return 0, 0, 0

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes no params, and returns a Robot object:
# -------------------------------------------------------

def INIT():
    return SimpleRobot()
