# Defines AriaRobot, a subclass of robot

from pyro.robot import *
from pyro.robot.service import Service, ServiceError
from AriaPy import Aria, ArRobot, ArSerialConnection, ArTcpConnection, \
     ArRobotParams, ArGripper, ArSonyPTZ
from math import pi, cos, sin
from os import getuid

PIOVER180 = pi / 180.0
DEG90RADS = 0.5 * pi
COSDEG90RADS = cos(DEG90RADS) / 1000.0
SINDEG90RADS = sin(DEG90RADS) / 1000.0

BIT0 = 0x1
BIT1 = 0x2 
BIT2 = 0x4 
BIT3 = 0x8 
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40 
BIT7 = 0x80 
BIT8 = 0x100 
BIT9 = 0x200 
BIT10 = 0x400 
BIT11 = 0x800 
BIT12 = 0x1000 
BIT13 = 0x2000 
BIT14 = 0x4000 
BIT15 = 0x8000 

BITPOS = (BIT0, BIT1, BIT2,  BIT3,  BIT4,  BIT5,  BIT6,  BIT7,
          BIT8, BIT9, BIT10, BIT11, BIT12, BIT13, BIT14, BIT15 )

class AriaService(Service):

    def __init__(self, robot, name):
        Service.__init__(self)
        self.robot = robot
        self.name = name

    def checkService(self):
        if self.dev == 0:
            raise ServiceError, "Service '%s' not available" % self.name

    #def getServiceData(self, pos = 0):
    #    self.checkService()
    #    return self.dev.__dict__[self.name][pos]


class AriaGripperService(AriaService):
        ## Methods for gripper from Aria

    def __init__(self, robot):
        AriaService.__init__(self, robot, "gripper")
        self.dev = ArGripper(self.robot)

    def open(self):
        self.dev.gripOpen()

    def close(self):
        self.dev.gripClose() 

    def stopMoving(self):
        self.dev.gripStop()

    def liftUp(self):
        self.dev.liftUp()

    def liftDown(self):
        self.dev.liftDown()

    def liftStop(self):
        self.dev.liftStop()

    def store(self):
        self.dev.gripperStore()

    def deploy(self):
        self.dev.gripperDeploy()

    def halt(self):
        self.dev.gripperHalt()

    def getState(self):
        return self.dev.getGripState()

    def getBreakBeamState(self):
        return self.dev.getBreakBeamState()

    def isClosed(self): # FIX: add this to aria
        raise "Please define me"
    
    def isMoving(self):
        return self.dev.isGripMoving()

    def isLiftMoving(self):
        return self.dev.isLiftMoving()

    def isLiftMaxed(self):
        return self.dev.isLiftMaxed()

class AriaPTZService(AriaService):
    ## Methods for PTZ from Aria

    def __init__(self, robot):
        AriaService.__init__(self, robot, "ptz")
        self.dev = ArSonyPTZ(self.robot)

    ## Methods for moving camera

    def pan(self, numDegrees):
        self.dev.pan(numDegrees)

    def panRel(self, numDegrees):
        self.dev.panRel(numDegrees)

    def tilt(self, numDegrees):
        self.dev.tilt(numDegrees)

    def tiltRel(self, numDegrees):
        self.dev.tiltRel(numDegrees)        

    def panTilt(self, panDeg, tiltDeg):
        self.dev.panTilt(panDeg, tiltDeg)

    def panTiltRel(self, panDeg, tiltDeg):
        self.dev.panTiltRel(panDeg, tiltDeg)        

    def centerCamera(self):
        self.dev.panTilt(0,0)

    def zoom(self, numDegrees):
        self.dev.zoom(numDegrees)

    def zoomRel(self, numDegrees):
        self.dev.zoomRel(numDegrees)

    def getPan(self):
        return self.dev.getPan()
        
    def getTilt(self):
        return self.dev.getTilt()
        
    def getZoom(self):
        return self.dev.getZoom()

    def getRealPan(self):
        return self.dev.getRealPan()
        
    def getRealTilt(self):
        return self.dev.getRealTilt()
        
    def getRealZoom(self):
        return self.dev.getRealZoom()

    def canGetRealPanTilt(self):
        return self.dev.canGetRealPanTilt()
    
    def canGetRealZoom(self):
        return self.dev.canGetRealZoom()

    def getMaxPosPan(self):
        return self.dev.getMaxPosPan()

    def getMaxNegPan(self):
        return self.dev.getMaxNegPan()

    def getMaxPosTilt(self):
        return self.dev.getMaxPosTilt()

    def getMaxNegTilt(self):
        return self.dev.getMaxNegTilt()

    def getMaxZoom(self):
        return self.dev.getMaxZoom()

    def getMinZoom(self):
        return self.dev.getMinZoom()

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
        self.senses['robot']['stall'] = lambda dev: dev.getStallValue()
        self.senses['robot']['x'] = self.getX
        self.senses['robot']['y'] = self.getY
        self.senses['robot']['z'] = self.getZ
        self.senses['robot']['radius'] = lambda self: 250.0 # in MM
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
        self.senses['sonar']['x'] = lambda dev, pos: self.getSonarX(pos)
        self.senses['sonar']['y'] = lambda dev, pos: self.getSonarY(pos)
	self.senses['sonar']['z'] = lambda dev, pos: 0.03 # meters
        self.senses['sonar']['value'] = lambda dev, pos: self.getSonarRangeDev(dev, pos)
        self.senses['sonar']['maxvalue'] = lambda dev: self.getSonarMaxRange(dev)
        self.senses['sonar']['flag'] = lambda dev, pos: 0 # self.getSonarFlag
        self.senses['sonar']['units'] = lambda dev: "ROBOTS"

	# location of origin of sensors:
        self.senses['sonar']['ox'] = lambda dev, pos: self.params.getSonarX(pos)
        self.senses['sonar']['oy'] = lambda dev, pos: self.params.getSonarY(pos)
	self.senses['sonar']['oz'] = lambda dev, pos: 0.03
        self.senses['sonar']['th'] = lambda dev, pos: self.params.getSonarTh(pos) * PIOVER180 # self.light_th
        # in radians:
        self.senses['sonar']['arc'] = lambda dev, pos, \
                                      x = (7.5 * PIOVER180) : x

        if self.params.haveFrontBumpers() or self.params.haveRearBumpers():
            # bumper sensors
            self.senses['bumper'] = {}
            self.senses['bumper']['type'] = lambda dev: 'tactile'
            self.senses['bumper']['count'] = lambda dev: self.params.numFrontBumpers() + self.params.numRearBumpers()
            self.senses['bumper']['x'] = lambda dev, pos: 0
            self.senses['bumper']['y'] = lambda dev, pos: 0
            self.senses['bumper']['z'] = lambda dev, pos: 0
            self.senses['bumper']['th'] = lambda dev, pos: 0 
            self.senses['bumper']['value'] = lambda dev, pos: self.getBumpersPosDev(dev, pos)

        # Make a copy, for default:
        self.senses['range'] = self.senses['sonar']
        self.senses['self'] = self.senses['robot']

        console.log(console.INFO,'aria sense drivers loaded')

        self.controls['move'] = self.moveDev
        self.controls['translate'] = self.translateDev
        self.controls['rotate'] = self.rotateDev
        self.controls['update'] = self.update
        self.controls['localize'] = self.localize

        #self.supports["blob"] = PlayerService(self.dev, "blobfinder")
        #self.supports["comm"] = PlayerService(self.dev, "comms")
        self.supports["gripper"] = AriaGripperService(self.dev)
        #self.supports["power"] = PlayerService(self.dev, "power")
        #self.supports["position"] = PlayerService(self.dev, "position")
        #self.supports["sonar"] = PlayerService(self.dev, "sonar")
        #self.supports["laser"] = PlayerService(self.dev, "laser")
        self.supports["ptz"] = AriaPTZService(self.dev)
        #self.supports["gps"] = PlayerService(self.dev, "gps")
        #self.supports["bumper"] = PlayerService(self.dev, "bumper")
        #self.supports["truth"] = PlayerService(self.dev, "truth")

        console.log(console.INFO,'aria control drivers loaded')
        self.SanityCheck()
        self.dev.runAsync(1)
	self.update() 
        self.inform("Done loading Aria robot.")

    def getSonarX(self, pos):
        self.dev.lock()
        x = self.dev.getSonarReading(pos).getLocalX() 
        y = self.dev.getSonarReading(pos).getLocalY()
        self.dev.unlock()
        return (COSDEG90RADS * x - SINDEG90RADS * y)

    def getSonarY(self, pos):
        self.dev.lock()
        x = self.dev.getSonarReading(pos).getLocalX() 
        y = self.dev.getSonarReading(pos).getLocalY() 
        self.dev.unlock()
        return -(SINDEG90RADS * x - COSDEG90RADS * y)

    def translateDev(self, dev, translate_velocity):
        dev.setVel((int)(translate_velocity * 1100.0))

    def rotateDev(self, dev, rotate_velocity):
        dev.setRotVel((int)(rotate_velocity * 75.0))

    def moveDev(self, dev, translate_velocity, rotate_velocity):
        dev.lock()
        dev.setVel((int)(translate_velocity * 1100.0))
        dev.setRotVel((int)(rotate_velocity * 75.0))
        dev.unlock()

    def translate(self, translate_velocity):
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.unlock()

    def rotate(self, rotate_velocity):
        self.dev.lock()
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def move(self, translate_velocity, rotate_velocity):
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def getX(self, dev = 0):
        return self.x

    def getY(self, dev = 0):
        return self.y

    def getZ(self, dev = 0):
        return self.z

    def getTh(self, dev = 0):
        return self.th

    def getThr(self, dev = 0):
        return self.thr

    def update(self):
        self.dev.lock()
        self._update()
        self.x = self.dev.getX() / 1000.0
        self.y = self.dev.getY() / 1000.0
        self.th = (self.dev.getTh() + 360) % 360
        self.thr = self.th * PIOVER180
        self.dev.unlock()
    
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

    def localize(self, x = 0, y = 0, th = 0):
        """ x, y, th = meters, meters, degrees """
        pose = self.dev.getPose()
        pose.setPose(int(x * 1000), int(y * 1000), int(th))
        self.dev.moveTo(pose)
        # let's check to make sure:
        self.x = self.dev.getX() / 1000.0
        self.y = self.dev.getY() / 1000.0
        self.th = (self.dev.getTh() + 360) % 360
        self.thr = self.th * PIOVER180

    def disconnect(self):
        print "Disconnecting..."
        self.dev.disconnect()

    def getBumpersPosDev(self, dev, pos):
        return self.getBumpersDev(dev)[pos]

    def getBumpersDev(self, dev):
        # bumpers: front first, numbers 1 - 5
        retval = []
        if self.params.haveFrontBumpers():
            for i in range(1, 6):
                retval.append( dev.getStallValue() >> 8 & BITPOS[i] )
        if self.params.haveRearBumpers():
            for i in range(1, 6):
                retval.append( dev.getStallValue() & BITPOS[i] )
        return retval

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

    def enableMotors(self):
        self.dev.enableMotors()

    def disableMotors(self):
        self.dev.disableMotors()

if __name__ == '__main__':
    myrobot = AriaRobot()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()


