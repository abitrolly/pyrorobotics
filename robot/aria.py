# Defines AriaRobot, a subclass of robot

from pyro.robot import *
from pyro.robot.service import Service, ServiceError, Device
from AriaPy import Aria, ArRobot, ArSerialConnection, ArTcpConnection, \
     ArRobotParams, ArGripper, ArSonyPTZ, ArVCC4
from math import pi, cos, sin
from os import getuid
import time

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

    def __init__(self, robot, type = "sony"):
        # here, robot is the robot.device
        AriaService.__init__(self, robot, "ptz")
        if type == "sony":
            self.dev = ArSonyPTZ(self.robot)
        elif type == "canon":
            self.dev = ArVCC4(self.robot)
        else:
            raise TypeError, "invalid type: '%s'" % type

    def init(self):
        # this should NOT happen until the robot is connected:
        self.dev.init()
        
    def setPose(self, *args):
        if len(args) == 3:
            pan, tilt, zoom = args[0], args[1], args[2]
        elif len(args[0]) == 3:
            pan, tilt, zoom = args[0][0], args[0][1], args[0][2]
        else:
            raise AttributeError, "setPose takes pan, tilt, and zoom"
        retval1 = self.pan(pan)
        retval2 = self.pan(tilt)
        retval3 = self.pan(zoom)
        return [retval1, retval2, retval3]

    def getPose(self):
        return [self.getPan(), self.getTilt(), self.getZoom()]

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

class AriaSensor(Device):
    def __init__(self, params, device):
        Device.__init__(self)
        self.params = params
        self.device = device
        self.data['type'] = 'range'

class AriaSonar(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device)
        self.data['maxvalueraw'] = 2.99
        self.data['units']    = "ROBOTS"
        self.data['maxvalue'] = self.getSonarMaxRange() # FIX: this should change when you change units
        self.data["count"] = self.params.getNumSonar()
        if self.data["count"] == 16:
            self.groups = {'all': range(16),
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
        elif self.params.getNumSonar() > 16:
            raise AttributeError, ("Need to define sensor groups for sonars "
                                   "with %d sensors" % self.params.getNumSonar())
        self.subdataFunc['ox']    = lambda pos: self.params.getSonarX(pos)
        self.subdataFunc['oy']    = lambda pos: self.params.getSonarY(pos)
        self.subdataFunc['oz']    = lambda pos: 0.03
        self.subdataFunc['th']    = lambda pos: self.params.getSonarTh(pos) * PIOVER180
        self.subdataFunc['arc']   = lambda pos: (7.5 * PIOVER180)
        self.subdataFunc['x']     = lambda pos: self.device.getSonarReading(pos).getLocalX()
        self.subdataFunc['y']     = lambda pos: self.device.getSonarReading(pos).getLocalY()
	self.subdataFunc['z']     = lambda pos: 0.03 # meters
        self.subdataFunc['value'] = lambda pos: self.getSonarRange(pos)
        self.subdataFunc['pos']   = lambda pos: pos
        self.subdataFunc['group']   = lambda pos: self.getGroupNames(pos)

    def getGroupNames(self, pos):
        retval = []
        for key in self.groups:
            if pos in self.groups[key]:
                retval.append( key )
        return retval

    def getSonarRange(self, pos):
        return self.rawToUnits(self.device.getSonarRange(pos) / 1000.0)

    def getSonarMaxRange(self):
        return self.rawToUnits(2.99)

    def rawToUnits(self, raw):
        val = min(max(raw, 0.0), self.data['maxvalueraw'])
        units = self.data["units"]
        if units == "ROBOTS":
            return val / 0.75 # Pioneer is about .5 meters diameter
        elif units == "MM":
            return val * 1000.0
        elif units == "CM":
            return (val) * 100.0 # cm
        elif units == "METERS" or units == "RAW":
            return (val) 
        elif units == "SCALED":
            return val / self.data['maxvalueraw']
        else:
            raise 'InvalidType', "Units are set to invalid type"

class AriaLaser(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device)
        self.data['maxvalue'] = 15.0 # FIX
        self.data['units']    = "ROBOTS"
        self.data["count"] = self.params.getNumLaser()
        self.data["x"] = self.params.getLaserX()
        self.data["y"] = self.params.getLaserY()
        if self.data["count"] == 181:
            self.groups = {'all': range(16),
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
        #elif self.params.getNumSonar() > 181:
        #    raise AttributeError, ("Need to define sensor groups for lasers "
        #                           "with %d sensors" % self.params.getNumSonar())
        self.subdataFunc['oz']    = lambda pos: 0.03
        self.subdataFunc['th']    = lambda pos: pos
        self.subdataFunc['arc']   = lambda pos: 1.0
        self.subdataFunc['x']     = lambda pos: self.params.getLaserX()
        self.subdataFunc['y']     = lambda pos: self.params.getLaserX()
	self.subdataFunc['z']     = lambda pos: 0.03 # meters
        self.subdataFunc['value'] = lambda pos: self.device.getSonarRange(pos) # METERS? FIX: make in units
        self.subdataFunc['pos']   = lambda pos: pos

class AriaBumper(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device)
        self.data['maxvalue'] = 1.0 
        self.data['units']    = "RAW"
        self.data["count"] = self.params.numFrontBumpers() + self.params.numRearBumpers()
        if self.data["count"] == 5:
            self.groups = {'all': range(16),
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
        elif self.data["count"] == 10:
            self.groups = {'all': range(16),
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
        elif self.params.getNumSonar() > 10:
            raise AttributeError, ("Need to define sensor groups for bumpers "
                                   "with %d sensors" % self.data["count"])
        self.subdataFunc['pos']   = lambda pos: pos
        self.subdataFunc['value']   = lambda pos: pos

##     def getBumpersPosDev(self, dev, pos):
##         return self.getBumpersDev(dev)[pos]

##     def getBumpersDev(self, dev):
##         # bumpers: front first, numbers 1 - 5
##         retval = []
##         if self.params.haveFrontBumpers():
##             for i in range(1, 6):
##                 retval.append( dev.getStallValue() >> 8 & BITPOS[i] )
##         if self.params.haveRearBumpers():
##             for i in range(1, 6):
##                 retval.append( dev.getStallValue() & BITPOS[i] )
##         return retval

class AriaRobot(Robot):
    def __init__(self, name = "Aria"):
        self.inform("Loading Aria robot interface...")
        Robot.__init__(self) # robot constructor
        self.connect()
        self.data['stall'] = 0
        self.data['x'] = 0.0
        self.data['y'] = 0.0
        self.data['z'] = 0.0
        self.data['datestamp'] = time.time()
        self.data['radius'] = self.params.getRobotRadius() / 1000.0 # in MM, convert to meters
        self.data['th'] = 0.0 # in degrees
        self.data['thr'] = 0.0 # in radians
	self.data['type'] = self.dev.getRobotType()
	self.data['subtype'] = self.params.getSubClassName()
        self.data['units'] = 'METERS' # x,y,z units
        self.data['name'] = self.dev.getRobotName()
        console.log(console.INFO,'aria sense drivers loaded')
        self.dev.runAsync(1)
        if self.params.getNumSonar() > 0:
            self.dataFunc["sonar"] = AriaSonar(self.params, self.dev)
            self.dataFunc["range"] = self.dataFunc["sonar"]
        if self.params.getLaserPossessed():
            self.dataFunc["laser"] = AriaLaser(self.params, self.dev)
            self.dataFunc["range"] = self.dataFunc["laser"]
        if self.params.numFrontBumpers() + self.params.numRearBumpers() > 0:
            self.dataFunc["bumper"] = AriaBumper(self.params, self.dev)
	self.update() 
        self.inform("Done loading Aria robot.")

    def translate(self, translate_velocity):
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.unlock()

    def rotate(self, rotate_velocity):
        self.dev.lock()
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def move(self, translate_velocity, rotate_velocity):
        print "move:", translate_velocity, rotate_velocity
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def update(self):
        self.dev.lock()
        self._update()
        self.data["x"] = self.dev.getX() / 1000.0
        self.data["y"] = self.dev.getY() / 1000.0
        self.data["th"] = (self.dev.getTh() + 360) % 360
        self.data["thr"] = self.data["th"] * PIOVER180
        self.data["stall"] = self.dev.getStallValue()
        self.dev.unlock()
    
    def enableMotors(self):
        self.dev.enableMotors()

    def disableMotors(self):
        self.dev.disableMotors()

    def disconnect(self):
        print "Disconnecting..."
        self.dev.disconnect()

    def connect(self):
        Aria.init()
        self.data["simulated"] = 1 
        self.dev = ArRobot()
        self.conn = ArTcpConnection()
        print "Attempting to open TCP port at localhost:%d..." % (8000 + getuid())
        self.conn.setPort("localhost", 8000 + getuid())
        self.dev.setDeviceConnection(self.conn)
        if (self.dev.blockingConnect() != 1):
            # could not connect to TCP; let's try a serial one
            # this is a real robot
            self.data["simulated"] = 0 
            print "Attempting to open Serial TTY port..."
            self.conn = ArSerialConnection()
            self.conn.setPort()
            self.dev.setDeviceConnection(self.conn)
            if (self.dev.blockingConnect() != 1):
                raise "FailedConnection"
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

if __name__ == '__main__':
    myrobot = AriaRobot()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()


