# Defines SaphiraRobot, a subclass of robot

from pyro.robot import *
from pyro.robot.driver.saphira import *

class SaphiraRobot(Robot):
    def __init__(self, name = None, simulator = 1):
        Robot.__init__(self, name, "saphira") # robot constructor
        self.dev = new_Saphira() # create Saphira object first
        self.inform("Loading Saphira robot interface...")
        Saphira_Connect(self.dev, simulator) # connect to what?
        Robot.load_drivers(self) # queries robot
        self.sensorGroups = {'front' : [(3, 'sonar'), \
                                        (4, 'sonar')], \
                             'front-left' : [(1, 'sonar'), \
                                             (2, 'sonar'), \
                                             (3, 'sonar')], \
                             'front-right' : [(4, 'sonar'), \
                                              (5, 'sonar'), \
                                              (6, 'sonar')], \
                             'left' : [(0, 'sonar'), (15, 'sonar')], \
                             'right' : [(7, 'sonar'), (8, 'sonar')], \
                             'back-right' : [(9, 'sonar'), (10, 'sonar'), \
                                            (11, 'sonar')], \
                             'back-left' : [(12, 'sonar'), (13, 'sonar'), \
                                             (14, 'sonar')], \
                             'back' : [(11, 'sonar'), (12, 'sonar')]}
        self.senses['robot']['simulator'] = lambda self, x = simulator: x
	self.update() # Saphira_UpdatePosition(self.dev)
        self.inform("Done loading lobot.")

    def _draw(self, options, renderer): # overloaded from robot
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
        renderer.xformPush()
        renderer.color((0, 0, .7))
        for i in range(self.get('sonar', 'count')):
            y1, x1, z1 = -self.get('sonar', 'x', i), \
                         -self.get('sonar', 'y', i), \
                         self.get('sonar', 'z', i)
            #y2, x2, z2 = -self.get('sonar', 'ox', i), \
            #             -self.get('sonar', 'oy', i), \
            #             self.get('sonar', 'oz', i)
            # Those above values are off!
            # FIXME: what are the actual positions of sensor x,y?
            x2, y2, z2 = 0, 0, z1
            arc    = self.get('sonar', 'arc', i) # in radians
            renderer.ray((x1, y1, z1), (x2, y2, z2), arc)

        renderer.xformPop()        

        # end of robot
        renderer.xformPop()

    def getOptions(self): # overload 
        pass

    def connect(self):
        Saphira_Connect(self.dev)
        Saphira_Localize(0.0, 0.0, 0.0)

    def localize(self, x = 0.0, y = 0.0, z = 0.0):
        Saphira_Localize(self.dev, x, y, z)

    def disconnect(self):
        Saphira_Disconnect(self.dev)

    def loadDrivers(self):
        self.drivers.append(SaphiraSenseDriver(self))
        self.drivers.append(SaphiraControlDriver(self))


if __name__ == '__main__':
    x = SaphiraRobot('Test', 0)
    x.update()
    cm = new_CameraMover()
    CameraMover_Init(cm)
    CameraMover_Pan(cm, 45)
    x.disconnect()