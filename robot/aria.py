# Defines AriaRobot, a subclass of robot

from pyro.robot import *
from pyro.geometry import *
from pyro.robot.device import Device, DeviceError
from AriaPy import Aria, ArRobot, ArSerialConnection, ArTcpConnection, \
     ArRobotParams, ArGripper, ArSonyPTZ, ArVCC4
try:
    import ArAudio
except:
    ArAudio = 0
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

class AriaAudioDevice(AriaDevice):
    def __init__(self, robot):
        AriaDevice.__init__(self, robot, "audio")
        self.audio = ArAudio()
        self.audio.init()
        self.devData["data"] = ""
        self.devData["listening?"] = 0
        self.devData["speaking?"] = 0
        self.devData["speak"] = None
        self.devData["listen"] = None
        self.devData["play"] = None
        self.notSetables.extend( ["data", "listening?", "speaking?"] )
        self.notGetables.extend( ["speak", "listen", "play"] )

    def preGet(self, item):
        if item == "data":
            self.devData["data"] = self.audio.getPhrase()
        elif item == "listening":
            self.devData["listening?"] = self.audio.amListening()
        elif item == "speaking":
            self.devData["speaking?"] = self.audio.amSpeaking()

    def postSet(self, item, value):
        if item == "speak":
            self.audio.speak(value)
        elif item == "listen":
            self.audio.setListen(value)
        elif item == "play":
            self.audio.play(value) # filename
            
class AriaGripperDevice(AriaDevice):
        ## Methods for gripper from Aria

    def __init__(self, robot):
        AriaDevice.__init__(self, robot, "gripper")
        self.dev = ArGripper(self.robot)
        self.startDevice()
        self.devData[".help"] = """.set('/robot/gripper/command', VALUE) where VALUE is: open, close, stop, up,\n""" \
                                """     down, store, deploy, halt.\n""" \
                                """.get('/robot/gripper/KEYWORD') where KEYWORD is: state, breakBeamState,\n""" \
                                """     isClosed, isMoving, isLiftMoving, isLiftMaxed"""
        # "command" is already in notGetables of Device
        #self.notGetables.extend( ["command"] )
        self.notSetables.extend( ["state", "breakBeamState", "isClosed",
                                  "isMoving", "isLiftMoving", "isLiftMaxed"] )
        self.devData.update( {"state": None, "breakBeamState": None, "isClosed": None,
                              "isMoving": None, "isLiftMoving": None, "isLiftMaxed": None} )

    def postSet(self, keyword):
        if keyword == "command":
            if self.devData["command"] == "open":
                self.dev.gripOpen() 
            elif self.devData["command"] == "close":
                self.dev.gripClose() 
            elif self.devData["command"] == "stop":
                self.dev.gripStop()
            elif self.devData["command"] == "up":
                self.dev.liftUp()
            elif self.devData["command"] == "down":
                self.dev.liftDown()
            elif self.devData["command"] == "store":
                self.dev.gripperStore() 
            elif self.devData["command"] == "deploy":
                self.dev.gripperDeploy()
            elif self.devData["command"] == "halt":
                self.dev.gripperHalt()
            else:
                raise AttributeError, "invalid command to ptz: '%s'" % keyword

    def preGet(self, keyword):
        if keyword == "state":
            self.devData[keyword] = self.dev.getGripState() # help!
        elif keyword == "breakBeamState":
            self.devData[keyword] = self.getBreakBeamState()
        elif keyword == "isClosed":
            self.devData[keyword] = self.isClosed()
        elif keyword == "isMoving":
            self.devData[keyword] = self.dev.isGripMoving() #ok
        elif keyword == "isLiftMoving":
            self.devData[keyword] = self.dev.isLiftMoving() # ok
        elif keyword == "isLiftMaxed":
            self.devData[keyword] = self.dev.isLiftMaxed() # ok

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

    def __init__(self, robot, model = "sony"):
        # here, robot is the lowlevel robot.dev driver
        AriaDevice.__init__(self, robot, "ptz")
        self.devData["model"] = model
        if model == "sony":
            self.dev = ArSonyPTZ(self.robot)
        elif model == "canon":
            self.dev = ArVCC4(self.robot)
        else:
            raise TypeError, "invalid model: '%s'" % model
        self.dev.init()
        self.devData["pose"] = self.getPose()
        self.devData[".help"] = """.set('/robot/ptz/COMMAND', VALUE) where COMMAND is: pose, pan, tilt, zoom.\n""" \
                                """.get('/robot/ptz/KEYWORD') where KEYWORD is: pose\n"""
        self.notGetables.extend (["tilt", "pan", "zoom"])
        self.devData.update( {"tilt": None, "pan": None,
                              "zoom": None, "command": None, "pose": None} )
        self.startDevice()

    def preGet(self, keyword):
        if keyword == "pose": # make sure it is the current pose
            self.devData["pose"] = self.getPose()

    def postSet(self, keyword):
        if keyword == "pose":
            self.setPose( self.devData[keyword] )
        elif keyword == "pan":
            self.pan( self.devData[keyword] )
        elif keyword == "tilt":
            self.tilt( self.devData[keyword] )
        elif keyword == "zoom":
            self.zoom( self.devData[keyword] )

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
        self.devData['units']    = "ROBOTS" # current report units
        # This is fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # ----------------------------------------------------------
        # What are the raw units of "value"?
        self.devData["rawunits"] = "MM"
        self.devData['maxvalueraw'] = 2990 # in rawunits
        # ----------------------------------------------------------
        # This should change when you change units:
        # (see postSet below)
        # in rawunits
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])
        # X,Y,Z are in meters
        # ----------------------------------------------------------
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
        elif self.params.getNumSonar() == 32:
            # may really only be 24!
            # 0  - 7  front, bottom
            # 8  - 15 back, bottom
            # 16 - 23 front, top 
            # 24 - 31 back , top 24   25 26   27 28   29 30  31 (FIX: add these to back groups)
            self.groups = {'all': range(32),
                           'front': (3, 4, 19, 20),
                           'front-left' : (1,2,3, 17, 18, 19),
                           'front-right' : (4, 5, 6, 20, 21, 22),
                           'front-all' : (1,2, 3, 4, 5, 6, 17, 18, 19, 20, 21, 22),
                           'left' : (0, 15, 16), 
                           'right' : (7, 8, 23), 
                           'left-front' : (0, 16), 
                           'right-front' : (7, 23),
                           'left-back' : (15,),
                           'right-back' : (8,),
                           'back-right' : (9, 10, 11),
                           'back-left' : (12, 13, 14), 
                           'back' : (11, 12),
                           'back-all' : ( 9, 10, 11, 12, 13, 14)}
        else:
            print "Pyro warning: Need to define sensor groups for sonars with %d sensors" % self.params.getNumSonar()
            self.groups = {'all': range(self.params.getNumSonar())}
        self.subDataFunc['ox']    = lambda pos: self.params.getSonarX(pos)
        self.subDataFunc['oy']    = lambda pos: self.params.getSonarY(pos)
        self.subDataFunc['oz']    = lambda pos: 0.03
        self.subDataFunc['th']    = lambda pos: self.params.getSonarTh(pos) # degrees
        self.subDataFunc['thr']    = lambda pos: self.params.getSonarTh(pos) * PIOVER180
        self.subDataFunc['arc']   = lambda pos: (7.5 * PIOVER180)
        self.subDataFunc['x']     = lambda pos: self.dev.getSonarReading(pos).getLocalX()
        self.subDataFunc['y']     = lambda pos: self.dev.getSonarReading(pos).getLocalY()
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.dev.getSonarRange(pos))
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = lambda pos: self.getGroupNames(pos)
        self.startDevice()

    def postSet(self, keyword):
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])

class AriaLaser(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device, "laser")
        self.devData['units']    = "ROBOTS"
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # What are the raw units of "value"? CHECK to see if MM is correct
        self.devData["rawunits"] = "MM"
        self.devData['maxvalueraw'] = 15000
        # ----------------------------------------------------------
        # This should change when you change units:
        # (see postSet below)
        # in rawunits
        self.devData['maxvalue'] = self.rawToUnits(self.devData['maxvalueraw'])
        # X,Y,Z are in meters
        # ----------------------------------------------------------
        self.devData["x"] = self.params.getLaserX()
        self.devData["y"] = self.params.getLaserY()
        self.devData["th"] = self.params.getLaserTh()
        # Compute groups based on count:
        self.devData["count"] = self.params.getNumLaser()
        count = self.devData["count"]
        part = int(count/8)
        start = 0
        posA = part
        posB = part * 2
        posC = part * 3
        posD = part * 4
        posE = part * 5
        posF = part * 6
        posG = part * 7
        end = count
        self.groups = {'all': range(count),
                       'right': range(0, posB),
                       'left': range(posF, end),
                       'front': range(posC, posE),
                       'front-right': range(posB, posD),
                       'front-left': range(posD, posF),
                       'front-all': range(posB, posF),
                       'right-front': range(posA, posB),
                       'right-back': range(start, posA),
                       'left-front': range(posF,posG),
                       'left-back': range(posG,end),
                       'back-right': [],
                       'back-left': [],
                       'back': [],
                       'back-all': []}
        # for each laser pos:
        self.subDataFunc['oz']    = lambda pos: 0.03
        self.subDataFunc['th']    = lambda pos: self.params.getLaserTh(pos) * PIOVER180
        self.subDataFunc['thr']    = lambda pos: self.params.getLaserTh(pos)
        self.subDataFunc['arc']   = lambda pos: 1.0
        self.subDataFunc['x']     = lambda pos: 0.0 #
        self.subDataFunc['y']     = lambda pos: 0.0 #
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.dev.getSonarRange(pos)) 
        self.subDataFunc['pos']   = lambda pos: pos
        self.startDevice()

    def postSet(self, keyword):
        self.devData['maxvalue'] = self.rawToUnits(self.devData['maxvalueraw'])

class AriaBumper(AriaSensor):
    def __init__(self,  params, device):
        AriaSensor.__init__(self, params, device, "bumper")
        self.devData['maxvalue'] = 1.0 
        self.devData['units']    = "RAW"
        self.devData["all"]   = self.getBumpersAll()
        self.devData["count"] = self.params.numFrontBumpers() + self.params.numRearBumpers()
        self.groups = {'all': range(self.devData["count"])}
        self.subDataFunc['pos']     = lambda pos: pos
        self.subDataFunc['value']   = self.getBumpers
        self.startDevice()

    def preGet(self, keyword):
        if keyword == "all":
            self.devData["all"] = self.getBumpersAll()

    def getBumpers(self, pos):
        self.getBumpersAll()[pos]

    def getBumpersAll(self):
        # bumpers: front first, numbers 1 - 5
        retval = []
        if self.params.haveFrontBumpers():
            for i in range(1, 6):
                retval.append( self.dev.getStallValue() >> 8 & BITPOS[i] )
        if self.params.haveRearBumpers():
            for i in range(1, 6):
                retval.append( self.dev.getStallValue() & BITPOS[i] )
        return retval

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
        self.devData['name'] = name #self.dev.getRobotName()
        self.dev.runAsync(1)
        self.devData["builtinDevices"] = ["gripper", "ptz-sony", "ptz-canon"]
        if ArAudio:
            self.devData["builtinDevices"].append( "audio" )
        if self.params.getNumSonar() > 0:
            self.devData["builtinDevices"].append( "sonar" )
            deviceName = self.startDevice("sonar")
            self.devDataFunc["range"] = self.get("/devices/%s/object" % deviceName)
            self.devDataFunc["sonar"] = self.get("/devices/%s/object" % deviceName)
        if self.params.getLaserPossessed():
            self.devData["builtinDevices"].append( "laser" )
            deviceName = self.startDevice("laser")
            self.devDataFunc["range"] = self.get("/devices/%s/object" % deviceName)
            self.devDataFunc["laser"] = self.get("/devices/%s/object" % deviceName)
        if self.params.numFrontBumpers() + self.params.numRearBumpers() > 0:
            self.devData["builtinDevices"].append( "bumper" )
            deviceName = self.startDevice("bumper")
        self.update()
        self.inform("Done loading Aria robot.")
    def __del__(self):
        self.disconnect()
    def startDeviceBuiltin(self, item):
        if item == "sonar":
            return {"sonar": AriaSonar(self.params, self.dev)}
        elif item == "laser":
            return {"laser": AriaLaser(self.params, self.dev)}
        elif item == "bumper":
            return {"bumper": AriaBumper(self.params, self.dev)}
        elif item == "ptz-sony":
            return {"ptz": AriaPTZDevice(self.dev, model = "sony")}
        elif item == "ptz-canon":
            return {"ptz": AriaPTZDevice(self.dev, model = "canon")}
        elif item == "gripper":
            return {"gripper": AriaGripperDevice(self.dev)}
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


