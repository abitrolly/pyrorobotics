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
        self._update()
    
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
        self.senses['robot']['name'] = lambda dev: "simple"
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
        #self.setLocation(self.senses['robot']['x'], \
        #                 self.senses['robot']['y'], \
        #                 self.senses['robot']['z'], \
        #                 self.senses['robot']['thr'] )
        renderer.xformPush()
        renderer.color((1, 0, 0))
        #print "position: (", self.get('robot', 'x'), ",",  \
        #      self.get('robot', 'y'), ")"
        
        #renderer.xformXlate((self.get('robot', 'x'), \
        #                     self.get('robot','y'), \
        #                     self.get('robot','z')))
        renderer.xformRotate(self.get('robot', 'th'), (0, 0, 1))
        
        renderer.xformXlate(( 0, 0, .15))
        
        renderer.box((-.25, .25, 0), \
                     (.25, .25, 0), \
                     (.25, -.25, 0), \
                     (-.25, .25, .35)) # d is over a, CW
        
        renderer.color((1, 1, 0))
        
        renderer.box((.13, -.05, .35), \
                     (.13, .05, .35), \
                     (.25, .05, .35), \
                     (.13, -.05, .45)) # d is over a, CW
        
        renderer.color((.5, .5, .5))
        
        # wheel 1
        renderer.xformPush()
        renderer.xformXlate((.25, .3, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .12, 12, 24)
        renderer.xformPop()
        
        # wheel 2
        renderer.xformPush()
        renderer.xformXlate((-.25, .3, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .12, 12, 24)
        renderer.xformPop()
        
        # wheel 3
        renderer.xformPush()
        renderer.xformXlate((.25, -.3, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .12, 12, 24)
        renderer.xformPop()
        
        # wheel 4
        renderer.xformPush()
        renderer.xformXlate((-.25, -.3, 0))
        renderer.xformRotate(90, (1, 0, 0))
        renderer.torus(.06, .12, 12, 24)
        renderer.xformPop()        
        
        # sonar
        #renderer.xformPush()
        #renderer.color((0, 0, .7))
        #for i in range(self.get('sonar', 'count')):
        #   y1, x1, z1 = -self.get('sonar', 'x', i), \
        #                -self.get('sonar', 'y', i), \
        #                self.get('sonar', 'z', i)
        #   #y2, x2, z2 = -self.get('sonar', 'ox', i), \
        #   #             -self.get('sonar', 'oy', i), \
        #   #             self.get('sonar', 'oz', i)
        #   # Those above values are off!
        #   # FIXME: what are the actual positions of sensor x,y?
        #   x2, y2, z2 = 0, 0, z1
        #   arc    = self.get('sonar', 'arc', i) # in radians
        #   renderer.ray((x1, y1, z1), (x2, y2, z2), arc)
        #   
        #renderer.xformPop()        
        # end of robot
        renderer.xformPop()
        
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
