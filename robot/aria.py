# Defines AriaRobot, a subclass of robot

from pyro.robot import *
from AriaPy import Aria, ArRobot, ArSerialConnection, ArTcpConnection, \
     ArRobotParams
from math import pi
from os import getuid

PIOVER180 = pi / 180.0

class AriaRobot(Robot):
    def __init__(self, name = "Aria"):
        Robot.__init__(self, name, "aria") # robot constructor
        self.inform("Loading Aria robot interface...")
        self.connect()
        self.sensorSet = {'all': range(16),
                          'front': (3, 4),
                          'front-left' : (1,2,3),
                          'front-right' : (4, 5, 6),
                          'front-all' : (1,2, 3, 4, 5, 6),
                          'left' : (0, 15), 
                          'right' : (7, 8), 
                          'left-front' : (0,), 
                          'right-front' : (7, ),
                          'left-back' : (15, ),
                          'right-back' : (8, ),
                          'back-right' : (9, 10, 11),
                          'back-left' : (12, 13, 14), 
                          'back' : (11, 12),
                          'back-all' : ( 9, 10, 11, 12, 13, 14)}
        self.z = 0
        self.senses = {}
        simulated = self.simulated
	# robot senses (all are functions):
        self.senses['robot'] = {}
        self.senses['robot']['simulator'] = lambda dev, x = simulated: x
        self.senses['robot']['stall'] = self.getStallValue
        self.senses['robot']['x'] = self.getX
        self.senses['robot']['y'] = self.getY
        self.senses['robot']['z'] = self.getZ
        self.senses['robot']['th'] = self.getTh # in degrees
        self.senses['robot']['thr'] = self.getThr # in radians
	self.senses['robot']['type'] = lambda dev: dev.getRobotType()
        self.senses['robot']['units'] = lambda dev: 'METERS'
        if name != 'Aria':
            self.senses['robot']['name'] = lambda dev, x = name: name
        else:
            self.senses['robot']['name'] = lambda dev: dev.getRobotName()
	self.senses['sonar'] = {}
	self.senses['sonar']['count'] = lambda dev: dev.getNumSonar()
	self.senses['sonar']['type'] = lambda dev: 'range'

	# location of sensors' hits:
        self.senses['sonar']['ox'] = 0 # self.light_ox
        self.senses['sonar']['oy'] = lambda dev, pos: 0 # self.light_oy
	self.senses['sonar']['oz'] = lambda dev, pos: 0.03 # meters
        self.senses['sonar']['value'] = lambda dev, pos: self.getSonarRangeDev(dev, pos)
        self.senses['sonar']['maxvalue'] = lambda dev: 0 # self.getSonarMaxRange
        self.senses['sonar']['flag'] = lambda dev, pos: 0 # self.getSonarFlag
        self.senses['sonar']['units'] = lambda dev: "ROBOTS"

	# location of origin of sensors:
        self.senses['sonar']['x'] = lambda dev, pos: self.params.getSonarX(pos)
        self.senses['sonar']['y'] = lambda dev, pos: self.params.getSonarY(pos)
	self.senses['sonar']['z'] = lambda dev, pos: 0.03
        self.senses['sonar']['th'] = lambda dev, pos: 0 # self.light_th
        # in radians:
        self.senses['sonar']['arc'] = lambda dev, pos, \
                                      x = (15 * pi / 180) : x

        # bumper sensors
	self.senses['bumper'] = {}
        self.senses['bumper']['type'] = lambda dev: 'tactile'
        self.senses['bumper']['count'] = lambda dev: 0
        self.senses['bumper']['x'] = lambda dev, pos: 0
        self.senses['bumper']['y'] = lambda dev, pos: 0
        self.senses['bumper']['z'] = lambda dev, pos: 0
        self.senses['bumper']['th'] = lambda dev, pos: 0 
        self.senses['bumper']['value'] = lambda dev, pos: 0

        # gripper sensors
	self.senses['gripper'] = {}
        self.senses['gripper']['type'] = lambda dev: 'special'
        self.senses['gripper']['frontbeam'] = lambda dev, pos: 0
        self.senses['gripper']['backbeam'] = lambda dev, pos: 0
        self.senses['gripper']['status'] = lambda dev, pos: 0

        # Make a copy, for default:
        self.senses['range'] = self.senses['sonar']
        self.senses['self'] = self.senses['robot']

        console.log(console.INFO,'aria sense drivers loaded')

        self.controls['move'] = self.moveDev
        self.controls['translate'] = self.translateDev
        self.controls['rotate'] = self.rotateDev
        self.controls['update'] = self.update
        self.controls['localize'] = self.localize
        self.controls['gripper'] = self.setGripper

        console.log(console.INFO,'aria control drivers loaded')
        self.SanityCheck()
        self.dev.runAsync(1)
	self.update() 
        self.inform("Done loading Aria robot.")

    def setGripper(self, dev, option):
        pass

    def translateDev(self, dev, translate_velocity):
        dev.setVel((int)(translate_velocity * 1100.0))

    def rotateDev(self, dev, rotate_velocity):
        print "Rotating:", rotate_velocity
        dev.setRotVel((int)(rotate_velocity * 75.0))

    def moveDev(self, dev, translate_velocity, rotate_velocity):
        print "movDev: Moving:", translate_velocity, rotate_velocity
        dev.setVel((int)(translate_velocity * 1100.0))
        dev.setRotVel((int)(rotate_velocity * 75.0))

    def translate(self, translate_velocity):
        print "translate: Translating:", translate_velocity
        self.dev.setVel((int)(translate_velocity * 1100.0))

    def rotate(self, rotate_velocity):
        print "rotate: Rotating:", rotate_velocity
        self.dev.setRotVel((int)(rotate_velocity * 75.0))

    def move(self, translate_velocity, rotate_velocity):
        print "move: Moving:", translate_velocity, rotate_velocity
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.setRotVel((int)(rotate_velocity * 75.0))

    def getStallValue(dev):
        return dev.getStallValue()

    def getX(self, dev):
        return self.x

    def getY(self, dev):
        return self.y

    def getZ(self, dev):
        return self.z

    def getTh(self, dev):
        return self.th

    def getThr(self, dev):
        return self.thr

    def update(self):
        self.x = self.dev.getX() / 1000.0
        self.y = self.dev.getY() / 1000.0
        self.th = self.dev.getTh()
        self.thr = self.th * PIOVER180
    
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
        Aria.init()
        self.dev = ArRobot()
        self.conn = ArTcpConnection()
        print "Attempting to open TCP port at localhost:%d..." % (8000 + getuid())
        self.conn.setPort("localhost", 8000 + getuid())
        self.dev.setDeviceConnection(self.conn)
        if (self.dev.blockingConnect() != 1):
            # could not connect to TCP; let's try a serial one
            # this is a real robot
            print "Attempting to open Serial TTY port..."
            self.conn = ArSerialConnection()
            self.conn.setPort()
            self.dev.setDeviceConnection(self.conn)
            if (self.dev.blockingConnect() != 1):
                raise "FailedConnection"
        self.simulated = 1 # how do you tell?
        self.params = self.dev.getRobotParams()
        # now, can say self.params.getSonarX(4)
        self.localize(0.0, 0.0, 0.0)

    def localize(self, x = 0.0, y = 0.0, th = 0.0):
        self.diffX = x - self.dev.getX()
        self.diffY = y - self.dev.getY()
        self.diffTh = th - self.dev.getTh()

    def disconnect(self):
        print "Disconnecting..."
        self.dev.disconnect()

    def getSonarRangeDev(self, dev, pos):
        return self.rawToUnits(dev, self.dev.getSonarRange(pos) / 1000.0, 'sonar')

    def getSonarMaxRange(self, dev):
        return self.rawToUnits(dev, 2.99, 'sonar')

    def rawToUnits(self, dev, raw, name):
        if name == 'sonar':
            val = min(max(raw, 0.0), 2.99)
        else:
            raise 'InvalidType', "Type is invalid"
        if self.senses[name]['units'](dev) == "ROBOTS":
            return val / 0.75 # Pioneer is about .5 meters diameter
        elif self.senses[name]['units'](dev) == "MM":
            return val * 1000.0
        elif self.senses[name]['units'](dev) == "CM":
            return (val) * 100.0 # cm
        elif self.senses[name]['units'](dev) == "METERS" or \
             self.senses[name]['units'](dev) == "RAW":
            return (val) 
        elif self.senses[name]['units'](dev) == "SCALED":
            return val / 2.99
        else:
            raise 'InvalidType', "Units are set to invalid type"

    
if __name__ == '__main__':
    myrobot = AriaRobot()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()
