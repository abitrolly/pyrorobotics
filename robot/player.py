# Defines PlayerRobot, a subclass of robot

from pyro.robot import *
from math import pi, cos, sin
from os import getuid
from pyro.robot.driver.player import *
import time

PIOVER180 = pi / 180.0
DEG90RADS = 0.5 * pi
COSDEG90RADS = cos(DEG90RADS) / 1000.0
SINDEG90RADS = sin(DEG90RADS) / 1000.0

from pyro.robot.service import Service, ServiceError

class PlayerService(Service):
    def __init__(self, dev, type, groups = {}):
        Service.__init__(self, type)
        self.groups = groups
        self.dev = dev
        self.name = type
        self.startService()

    def startService(self):
        try:
            self.dev.start(self.name)
            time.sleep(.5)
        except:
            print "Device not supported: '%s'" % self.name
            self.dev = 0
        return self

    def checkService(self):
        if self.dev == 0:
            print "Device '%s' not available" % self.name
            return 0
        return 1

    def stopService(self):
        if self.checkService():
            self.dev.stop(self.name)
            self.dev.__dict__[self.name] = {}

    def getServiceData(self, pos = 0):
        if self.checkService():
            return self.dev.__dict__[self.name][pos]

    def getServiceState(self):
        if self.checkService():
            if self.dev.__dict__[self.name] != {}:
                return "started"
            else:
                return "stopped"

    def getPose(self):
        function = self.dev.__class__.__dict__[ "get_%s_pose" % self.name]
        if function != None:
            x, y, th = function(self.dev)
            return (x / 1000.0, y / 1000.0, th % 360)
        else:
            raise ServiceError, "Function 'getPose' is not available for service '%s'" % self.name


    def setPose(self, xM, yM, thDeg):
        """ Move the device. x, y are in meters """
        function = self.dev.__class__.__dict__[ "set_%s_pose" % self.name]
        if function != None:
            return function( self.dev, xM * 1000.0, yM * 1000.0, thDeg % 360)
        else:
            raise ServiceError, "Function 'setPose' is not available for service '%s'" % self.name

class PlayerSonarService(PlayerService):
    def __init__(self, dev, name):
        PlayerService.__init__(self, dev, name)
        self.sonarGeometry = self.dev.get_sonar_geometry()
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
        # What are the raw units?
        self.devData["rawunits"] = "MM"
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # These are fixed in rawunits (above): DO NOT CONVERT:
        self.devData['maxvalueraw'] = 5000 # in rawunits
        # ----------------------------------------------------------
        # All of the rest of the measures are relative to units, given in rawunits:
        self.devData['units']    = "ROBOTS"
        self.postSet()
        self.devData["count"] = len(self.sonarGeometry)
        self.devData["noise"] = 0.05 # 5 percent
        # These are per reading:
        self.subDataFunc['ox']    = lambda pos:self.rawToUnits(self.sonarGeometry[pos][0])
        self.subDataFunc['oy']    = lambda pos:self.rawToUnits(self.sonarGeometry[pos][1])
        self.subDataFunc['oz']    = lambda pos: 0.03 # meters
        self.subDataFunc['th']    = lambda pos:self.sonarGeometry[pos][2] * PIOVER180 # radians
        self.subDataFunc['arc']   = lambda pos: (7.5 * PIOVER180) # radians
        self.subDataFunc['x']     = self.getX
        self.subDataFunc['y']     = self.getY
	self.subDataFunc['z']     = lambda pos: self.rawToUnits(0.03) # meters
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.dev.sonar[0][pos], self.devData["noise"])
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group'] = self.getGroupNames

    def postSet(self):
        """ Anything that might change after a set """
        self.devData['maxvalue'] = self.rawToUnits(self.devData['maxvalueraw'])

    def getX(self, pos):
        thr = (self.sonarGeometry[pos][2] + 90.0) * PIOVER180
        dist = self.rawToUnits(self.dev.sonar[0][pos])
        x = self.rawToUnits(self.sonarGeometry[pos][0])
        return cos(thr) * dist

    def getY(self, pos):
        thr = (self.sonarGeometry[pos][2] - 90.0) * PIOVER180
        dist = self.rawToUnits(self.dev.sonar[0][pos])
        y = self.rawToUnits(self.sonarGeometry[pos][1]) 
        return sin(thr) * dist

class PlayerLaserService(PlayerService):
    def __init__(self, dev, name):
        PlayerService.__init__(self, dev, name)
        count = int((self.dev.laser[0][0][1] - self.dev.laser[0][0][0]) / self.dev.laser[0][0][2] + 1)
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
        self.devData['maxvalueraw'] = 8.000 # meters
        self.devData['units']    = "ROBOTS"
        self.devData['maxvalue'] = 8.000
        self.devData['index'] = self.dev.laser.keys()[0]
        self.devData["count"] = count
        self.subDataFunc['ox']    = lambda pos: 0
        self.subDataFunc['oy']    = lambda pos: 0
        self.subDataFunc['oz']    = lambda pos: 0
        self.subDataFunc['th']    = lambda pos: self.dev.laser[0][0][0] + (self.dev.laser[0][0][2] * pos) # in degrees
        self.subDataFunc['arc']   = lambda pos: self.dev.laser[0][0][2] # in degrees
        self.subDataFunc['x']     = lambda pos: 0
        self.subDataFunc['y']     = lambda pos: 0
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.dev.laser[0][1][pos] / 1000.0 # fix, get in units
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = self.getGroupNames

class PlayerCommService(PlayerService):

    def __init__(self, dev, name):
        PlayerService.__init__(self, dev, name)
        self.messages = []
    
    def sendMessage(self, message):
        if self.dev.comms == {}:
            print "Need to startService('comm') in robot: message not sent"
            return
        self.dev.send_message(message)

    def getMessages(self):
        if not 'comms' in dir(self.dev) or self.dev.comms == {}:
            raise ServiceError, "Need to startService('comm') in robot"
        #if self.dev.comms[0] != '':
        #    self.update() # this is update in robot
        tmp = self.messages
        # reset queue:
        self.messages = []
        return tmp

    def updateService(self):
        for i in self.dev.comms:
            msg = self.dev.get_comms()
            if msg:
                self.messages.append( msg )

class PlayerPTZService(PlayerService):

    def __init__(self, dev, name):
        PlayerService.__init__(self, dev, name)
        self.origPose = (0, 0, 120)

    def init(self):
        self.setPose( self.origPose )

    def setPose(self, *args):
        if len(args) == 3:
            pan, tilt, zoom = args[0], args[1], args[2]
        elif len(args[0]) == 3:
            pan, tilt, zoom = args[0][0], args[0][1], args[0][2]
        else:
            raise AttributeError, "setPose takes pan, tilt, and zoom"
        return self.dev.set_ptz(pan, tilt, zoom)

    def getPose(self):
        return self.dev.get_ptz()

    def pan(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(numDegrees, ptz[1], ptz[2])

    def panRel(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0] + numDegrees, ptz[1], ptz[2])

    def tilt(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0], numDegrees, ptz[2])

    def tiltRel(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0], ptz[1] + numDegrees, ptz[2])

    def panTilt(self, panDeg, tiltDeg):
        ptz = self.getPose()
        return self.dev.set_ptz(panDeg, tiltDeg, ptz[2])

    def panTiltRel(self, panDeg, tiltDeg):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0] + panDeg, ptz[1] + tiltDeg, ptz[2])

    def centerCamera(self):
        return self.setPose( self.origPose )

    def zoom(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0], ptz[1], numDegrees)

    def zoomRel(self, numDegrees):
        ptz = self.getPose()
        return self.dev.set_ptz(ptz[0], ptz[1], ptz[2] + numDegrees)

    def getPan(self):
        ptz = self.getPose()
        return ptz[0]
        
    def getTilt(self):
        ptz = self.getPose()
        return ptz[1]
        
    def getZoom(self):
        ptz = self.getPose()
        return ptz[2]

    def getRealPan(self):
        ptz = self.getPose()
        return ptz[0]
        
    def getRealTilt(self):
        ptz = self.getPose()
        return ptz[1]
        
    def getRealZoom(self):
        ptz = self.getPose()
        return ptz[2]

    def canGetRealPanTilt(self):
        return 1

    def canGetRealZoom(self):
        return 1

    def getMaxPosPan(self):
        return 100

    def getMaxNegPan(self):
        return -100

    def getMaxPosTilt(self):
        return 30

    def getMaxNegTilt(self):
        return -30

    def getMaxZoom(self):
        return 10

    def getMinZoom(self):
        return 120

class PlayerGripperService(PlayerService):
    # Gripper functions
    #these also exist: 'gripper_carry', 'gripper_press', 'gripper_stay',

    def open(self):
        return self.dev.gripper_open() 

    def close(self):
        return self.dev.gripper_close() 

    def stopMoving(self):
        return self.dev.gripper_stop()

    def liftUp(self):
        return self.dev.gripper_up()

    def liftDown(self):
        return self.dev.gripper_down()

    def liftStop(self):
        return self.dev.gripper_stop()

    def store(self):
        return self.dev.gripper_store() 

    def deploy(self):
        return self.dev.gripper_deploy()

    def halt(self):
        return self.dev.gripper_halt()

    def getState(self):
        return self.dev.is_paddles_closed() # help!

    def getBreakBeamState(self):
        sum = 0
        sum += self.dev.is_ibeam_obstructed() * 2 #FIX: which?
        sum += self.dev.is_obeam_obstructed()
        return sum

    def isClosed(self): # FIX: add this to aria
        return self.dev.is_paddles_closed() #ok

    def isMoving(self):
        return self.dev.is_paddles_moving() #ok

    def isLiftMoving(self):
        return self.dev.is_lift_moving() # ok

    def isLiftMaxed(self):
        return self.dev.is_lift_up() # ok

class PlayerRobot(Robot):
    def __init__(self, name = "Player", port = 6665):
        Robot.__init__(self) # robot constructor
        self.devData["simulated"] = 1
        self.port = port
        self.name = name
        self.connect() # set self.dev to player robot
        # for some basic services:
        # Make sure sonar is before laser, so if you have
        # laser, it will be the default 'range' device
        for device in ["power", "position", "sonar", "laser",
                       "bumper"]:
            #is it supported? if so start it up:
            devList = self.dev.get_device_list()
            # (('fiducial', 0, 6665), ('comms', 0, 6665), ...)
            devNameList = map(lambda triplet: triplet[0], devList)
            if device in devNameList:
                if device == "ptz":
                    self.devDataFunc[device] = PlayerPTZService(self.dev, "ptz")
                elif device == "comms":
                    self.devDataFunc[device] = PlayerCommService(self.dev, "comms")
                elif device == "gripper":
                    self.devDataFunc[device] = PlayerGripperService(self.dev, "gripper")
                elif device == "laser":
                    self.devDataFunc[device] = PlayerLaserService(self.dev, "laser")
                    self.devDataFunc["range"] = self.devDataFunc["laser"]
                elif device == "sonar":
                    self.devDataFunc[device] = PlayerSonarService(self.dev, "sonar")
                    self.devDataFunc["range"] = self.devDataFunc["sonar"]
                else:
                    self.devDataFunc[device] = PlayerService(self.dev, device)
            #self.supports["blob"] = PlayerService(self.dev, "blobfinder")
            #self.supports["power"] = PlayerService(self.dev, "power")
            #self.supports["position"] = PlayerService(self.dev, "position")
            #self.supports["sonar"] = PlayerService(self.dev, "sonar")
            #self.supports["laser"] = PlayerService(self.dev, "laser")
            #self.supports["ptz"] = PlayerPTZService(self.dev, "ptz")
            #self.supports["gps"] = PlayerService(self.dev, "gps")
            #self.supports["bumper"] = PlayerService(self.dev, "bumper")
            #self.supports["truth"] = PlayerService(self.dev, "truth")
        # default values
        self.devData["stall"] = 0
        self.devData["x"] = 0.0
        self.devData["y"] = 0.0
        self.devData["th"] = 0.0
        self.devData["thr"] = 0.0
        self.devData["noise"] = .05 # 5 % noise
        self.devData["datestamp"] = time.time()
        # Can we get these from player?
        self.devData["radius"] = 0.25
        self.devData["type"] = "Player"
        self.devData["subtype"] = 0
        self.devData["units"] = "METERS"
        self.devData["name"] = 0
        #self.devData["simulated"] = self.simulated
        self.localize(0.0, 0.0, 0.0)
        self.update()
    
    def translate(self, translate_velocity):
        self.dev.set_speed(translate_velocity * 900.0, None, None)

    def rotate(self, rotate_velocity):
        self.dev.set_speed(None, None, rotate_velocity * 65.0)

    def move(self, translate_velocity, rotate_velocity):
        self.dev.set_speed(translate_velocity * 900.0,
                           0,
                           rotate_velocity * 65.0)

    # FIX: either sonar values are changing between calls to X, Y
    # or sin/cos values are not taking into account offset from center
        
    def localX(self, pos):
        thr = (self.sonarGeometry[pos][2] + 90.0) * PIOVER180
        dist = self.rawToUnits(self.dev.sonar[0][pos], 'sonar')
        x = self.rawToUnits(self.sonarGeometry[pos][0], 'sonar')
        return cos(thr) * dist

    def localY(self, pos):
        thr = (self.sonarGeometry[pos][2] - 90.0) * PIOVER180
        dist = self.rawToUnits(self.dev.sonar[0][pos], 'sonar')
        y = self.rawToUnits(self.sonarGeometry[pos][1], 'sonar') 
        return sin(thr) * dist

    def update(self):
        self._update()
        pos, speeds, stall = self.dev.get_position()
        # (xpos, ypos, th), (xspeed, yspeed, rotatespeed), stall
        self.devData["x"] = pos[0] / 1000.0
        self.devData["y"] = pos[1] / 1000.0
        self.devData["th"] = pos[2] # degrees
        self.devData["thr"] = pos[2] * PIOVER180
        self.devData["stall"] = stall
        
    def localize(self, x = 0, y = 0, th = 0):
        """
        Set robot's internal pose to x (meters), y (meters),
        th (radians)
        """
        self.dev.set_odometry(x * 1000, y * 1000, th)
        self.x = x
        self.y = y
        self.th = th
        self.thr = self.th * PIOVER180

    def connect(self):
        self.dev = player('localhost', port=self.port)
        #self.localize(0.0, 0.0, 0.0)
        
if __name__ == '__main__':
    myrobot = PlayerBase()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()
