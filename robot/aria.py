# Defines AriaRobot, a subclass of robot

from pyro.robot import *
from pyro.geometry import *
from pyro.robot.device import Device, DeviceError
from AriaPy import Aria, ArRobot, ArSerialConnection, ArTcpConnection, \
     ArRobotParams, ArGripper, ArSonyPTZ, ArVCC4
from math import pi, cos, sin
from os import getuid
import time

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

class AriaSensor(Device):
    def __init__(self, params, device, type):
        Device.__init__(self, type)
        self.params = params
        self.dev = device

class AriaDevice(Device):
    def __init__(self, robot, type):
        Device.__init__(self, type)
        self.robot = robot

class AriaGripperDevice(AriaDevice):
        ## Methods for gripper from Aria

    def __init__(self, robot):
        AriaDevice.__init__(self, robot, "gripper")
        self.dev = ArGripper(self.robot)
        self.startDevice()

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

class AriaPTZDevice(AriaDevice):
    ## Methods for PTZ from Aria

    def __init__(self, robot, type = "sony"):
        # here, robot is the lowlevel robot.dev driver
        AriaDevice.__init__(self, robot, "ptz")
        self.devData["model"] = type
        if type == "sony":
            self.dev = ArSonyPTZ(self.robot)
        elif type == "canon":
            self.dev = ArVCC4(self.robot)
        else:
            raise TypeError, "invalid type: '%s'" % type
        self.dev.init()
        self.startDevice()

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

class AriaSonar(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device, "sonar")
        self.devData['maxvalueraw'] = 2.99
        self.devData['units']    = "ROBOTS"
        self.devData['maxvalue'] = self.getSonarMaxRange() # FIX: this should change when you change units
        self.devData["count"] = self.params.getNumSonar()
        if self.devData["count"] == 16:
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
        self.subDataFunc['ox']    = lambda pos: self.params.getSonarX(pos)
        self.subDataFunc['oy']    = lambda pos: self.params.getSonarY(pos)
        self.subDataFunc['oz']    = lambda pos: 0.03
        self.subDataFunc['th']    = lambda pos: self.params.getSonarTh(pos) * PIOVER180
        self.subDataFunc['thr']    = lambda pos: self.params.getSonarTh(pos)
        self.subDataFunc['arc']   = lambda pos: (7.5 * PIOVER180)
        self.subDataFunc['x']     = lambda pos: self.dev.getSonarReading(pos).getLocalX()
        self.subDataFunc['y']     = lambda pos: self.dev.getSonarReading(pos).getLocalY()
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.getSonarRange(pos)
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = lambda pos: self.getGroupNames(pos)
        self.startDevice()

    def getSonarRange(self, pos):
        return self.rawToUnits(self.dev.getSonarRange(pos) / 1000.0)

    def getSonarMaxRange(self):
        return self.rawToUnits(2.99)

    def rawToUnits(self, raw):
        val = min(max(raw, 0.0), self.devData['maxvalueraw'])
        units = self.devData["units"]
        if units == "ROBOTS":
            return val / 0.75 # Pioneer is about .5 meters diameter
        elif units == "MM":
            return val * 1000.0
        elif units == "CM":
            return (val) * 100.0 # cm
        elif units == "METERS" or units == "RAW":
            return (val) 
        elif units == "SCALED":
            return val / self.devData['maxvalueraw']
        else:
            raise 'InvalidType', "Units are set to invalid type"

class AriaLaser(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device, "laser")
        self.devData['maxvalue'] = 15.0 # FIX
        self.devData['units']    = "ROBOTS"
        self.devData["count"] = self.params.getNumLaser()
        self.devData["x"] = self.params.getLaserX()
        self.devData["y"] = self.params.getLaserY()
        self.devData["th"] = self.params.getLaserTh()
        if self.devData["count"] == 181:
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
        self.subDataFunc['oz']    = lambda pos: 0.03
        self.subDataFunc['th']    = lambda pos: self.params.getLaserTh(pos) * PIOVER180
        self.subDataFunc['thr']    = lambda pos: self.params.getLaserTh(pos)
        self.subDataFunc['arc']   = lambda pos: 1.0
        self.subDataFunc['x']     = lambda pos: 0.0 #
        self.subDataFunc['y']     = lambda pos: 0.0 #
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.dev.getSonarRange(pos) # METERS? FIX: make in units
        self.subDataFunc['pos']   = lambda pos: pos
        self.startDevice()

class AriaBumper(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device, "bumper")
        self.devData['maxvalue'] = 1.0 
        self.devData['units']    = "RAW"
        self.devData["count"] = self.params.numFrontBumpers() + self.params.numRearBumpers()
        if self.devData["count"] == 5:
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
        elif self.devData["count"] == 10:
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
                                   "with %d sensors" % self.devData["count"])
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['value']   = lambda pos: pos
        self.startDevice()

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
        Robot.__init__(self) # robot constructor
        self.connect()
        self.devData["x"] = self.dev.getX() / 1000.0
        self.devData["y"] = self.dev.getY() / 1000.0
        self.devData["th"] = (self.dev.getTh() + 360) % 360
        self.devData["thr"] = self.devData["th"] * PIOVER180
        self.devData["stall"] = self.dev.getStallValue()
        self.devData['z'] = 0.0
        self.devData['radius'] = self.params.getRobotRadius() / 1000.0 # in MM, convert to meters
	self.devData['type'] = self.dev.getRobotType()
	self.devData['subtype'] = self.params.getSubClassName()
        self.devData['units'] = 'METERS' # x,y,z units
        self.devData['name'] = self.dev.getRobotName()
        self.dev.runAsync(1)
        self.supports = []
        if self.params.getNumSonar() > 0:
            self.supports.append( "sonar" )
            deviceName = self.startDevice("sonar")
            self.devDataFunc["range"] = self.get("/devices/%s/object" % deviceName)
        if self.params.getLaserPossessed():
            self.supports.append( "laser" )
            deviceName = self.startDevice("laser")
            self.devDataFunc["range"] = self.get("/devices/%s/object" % deviceName)
        if self.params.numFrontBumpers() + self.params.numRearBumpers() > 0:
            self.supports.append( "bumper" )
            deviceName = self.startDevice("bumper")
        self.update()
        self.devData['supports'] = self.supports
        self.inform("Done loading Aria robot.")

    def startDeviceBuiltin(self, item):
        if item == "sonar":
            return {"sonar": AriaSonar(self.params, self.dev)}
        elif item == "laser":
            return {"laser": AriaLaser(self.params, self.dev)}
        elif item == "bumper":
            return {"bumper": AriaBumper(self.params, self.dev)}
        else:
            raise AttributeError, "aria robot does not support device '%s'" % item
        
    def translate(self, translate_velocity):
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.unlock()

    def rotate(self, rotate_velocity):
        self.dev.lock()
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def move(self, translate_velocity, rotate_velocity):
        #print "move:", translate_velocity, rotate_velocity
        self.dev.lock()
        self.dev.setVel((int)(translate_velocity * 1100.0))
        self.dev.setRotVel((int)(rotate_velocity * 75.0))
        self.dev.unlock()

    def update(self):
        self.dev.lock()
        self._update()
        self.devData["x"] = self.dev.getX() / 1000.0
        self.devData["y"] = self.dev.getY() / 1000.0
        self.devData["th"] = (self.dev.getTh() + 360) % 360
        self.devData["thr"] = self.devData["th"] * PIOVER180
        self.devData["stall"] = self.dev.getStallValue()
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
        self.devData["simulated"] = 1 
        self.dev = ArRobot()
        self.conn = ArTcpConnection()
        print "Attempting to open TCP port at localhost:%d..." % (8000 + getuid())
        self.conn.setPort("localhost", 8000 + getuid())
        self.dev.setDeviceConnection(self.conn)
        if (self.dev.blockingConnect() != 1):
            # could not connect to TCP; let's try a serial one
            # this is a real robot
            self.devData["simulated"] = 0 
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


