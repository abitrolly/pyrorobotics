# Defines PlayerRobot, a subclass of robot

from pyro.robot import *
from math import pi, cos, sin
import threading, time
from os import getuid
from pyro.robot.device import Device, DeviceError, SensorValue
from pyro.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS
import playerc

# todo:
# check get_pose
# dev.__dict__[name] 

class PlayerDevice(Device):
    def __init__(self, client, type, groups = {}):
        Device.__init__(self, type)
        self.groups = groups
        self.client = client
        self.handle = None
        self.index = 0
        self.name = type + ("%d" % self.index)
        self.printFormat["data"] = "<device data>"
        self.devData["data"] = None
        self.devData["noise"] = 0.0
        self.notSetables.extend( ["data"] )
        # Required:
        self.startDevice()
        if "get_geom" in self.client.__dict__:
            self.client.get_geom() # reads it into handle.pose or poses

    def preGet(self, kw):
        if kw == "pose":
            self.devData["pose"] = self.handle.pose
        elif kw == "poses":
            self.devData["poses"] = self.handle.poses[:len(self)-1]
        elif kw == "data":
            self.devData["data"] = self.getDeviceData()

    def postSet(self, keyword):
        if keyword == "pose":
            if "set_cmd_pose" in self.client.__class__.__dict__:
                self.setPose( *self.devData[keyword] )

    def startDevice(self):
        exec("self.handle = playerc.playerc_%s(self.client, %d)" %
             (self.type, self.index))
        if self.handle.subscribe(playerc.PLAYERC_ALL_MODE) != 0:
            raise playerc.playerc_error_str()
        # robot.blobfinder.blobs[0].x, y, top, left, range, right, color,
        #   area, bottom,
        # color is a pointer
        # robot.blobfinder.blob_count, height, width
    def getDeviceData(self, pos = 0):
        return self.handle.scan[0]
    def getPose(self):
        """ Move the device. x, y are in meters """
        x, y, th = self.handle.px, self.handle.py, self.handle.pa
        return x, y, th / PIOVER180
    def setPose(self, xM, yM, thDeg):
        """ Move the device. x, y are in meters """
        function = self.client.__class__.__dict__["set_cmd_pose"]
        if function != None:
            return function( self.client, xM * 1000.0, yM * 1000.0, thDeg % 360)
        else:
            raise DeviceError, "Function 'setPose' is not available for device '%s'" % self.name

class PlayerSimulationDevice(PlayerDevice):
    def __init__(self, hostname):
        self.client = playerc.playerc_client(None, hostname, 7000)
        self.client.connect()
        PlayerDevice.__init__(self, self.client, "simulation")
        self.thread = PlayerUpdater(self)
        self.thread.start()
    def setPose(self, name, x, y, deg):
        th = deg * PIOVER180
        self.handle.set_pose2d(name, x, y, th)
    def getPose(self, name):
        result, x, y, thr = self.handle.get_pose2d(name)
        if result == 0: # no errors
            return x, y, (thr / PIOVER180)
        else:
            raise "simulation.getPose() failed"

class PlayerSonarDevice(PlayerDevice):
    def __init__(self, client):
        PlayerDevice.__init__(self, client, "sonar")
        while len(self) == 0: pass
        if len(self) == 16:
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
        else:
            self.groups= {'all': range(len(self))}
        self.devData['units']    = "ROBOTS"
        # What are the raw units?
        # Anything that you pass to rawToUnits should be in these units
        self.devData["rawunits"] = "METERS"
        self.devData['maxvalueraw'] = 8.0 # meters
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # ----------------------------------------------------------
        # All of the rest of the measures are relative to units, given in rawunits:
        # see also postSet below
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])
        self.devData["noise"] = 0.05 # 5 percent
        # These are per reading:
        self.subDataFunc['ox']    = lambda pos: self.sonarGeometry[pos][0]
        self.subDataFunc['oy']    = lambda pos: self.sonarGeometry[pos][1]
        self.subDataFunc['oz']    = lambda pos: self.rawToUnits(300) # rawunits
        self.subDataFunc['thr']   = lambda pos:self.sonarGeometry[pos][2] * PIOVER180 # radians
        self.subDataFunc['th']    = lambda pos:self.sonarGeometry[pos][2] # degrees
        self.subDataFunc['arc']   = lambda pos: (7.5 * PIOVER180) # radians
        self.subDataFunc['x']     = self.hitX
        self.subDataFunc['y']     = self.hitY
	self.subDataFunc['z']     = self.hitZ
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.handle.scan[pos], self.devData["noise"])
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group'] = self.getGroupNames

    def __len__(self):
        return self.handle.scan_count
    def getSensorValue(self, pos):
        return SensorValue(self, self.handle.scan[pos], pos,
                           (self.handle.poses[pos][0],
                            self.handle.poses[pos][1],
                            0.03,
                            self.handle.poses[pos][2]/PIOVER180),
                           self.devData["noise"])

    def postSet(self, keyword):
        """ Anything that might change after a set """
        self.devData['maxvalue'] = self.rawToUnits(self.devData["maxvalueraw"])

    def hitX(self, pos):
        thr = (self.sonarGeometry[pos][2] + 90.0) * PIOVER180 # + 90
        dist = self.rawToUnits(self.client.sonar[0][pos])
        x = self.rawToUnits(self.sonarGeometry[pos][0])
        return cos(thr) * dist

    def hitY(self, pos):
        thr = (self.sonarGeometry[pos][2] - 90.0) * PIOVER180 # - 90
        dist = self.rawToUnits(self.client.sonar[0][pos])
        y = self.rawToUnits(self.sonarGeometry[pos][1])
        return sin(thr) * dist
    def hitZ(self, pos):
        return .03

class PlayerLaserDevice(PlayerDevice):
    def __init__(self, client):
        PlayerDevice.__init__(self, client, "laser")
        while len(self) == 0: pass # wait for data to be loaded
        count = len(self)
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
        self.devData['units']    = "ROBOTS"
        self.devData["noise"]    = 0.01
        # -------------------------------------------
        self.devData["rawunits"] = "METERS"
        self.devData['maxvalueraw'] = 8.0 # rawunits
        # -------------------------------------------
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # ----------------------------------------------------------
        # MM to units:
        self.devData["maxvalue"] = self.rawToUnits(self.devData['maxvalueraw'])
        # -------------------------------------------
        self.devData['index'] = 0 # self.client.laser.keys()[0] FIX
        self.devData["count"] = count
        self.subDataFunc['ox']    = lambda pos: 0
        self.subDataFunc['oy']    = lambda pos: 0
        self.subDataFunc['oz']    = lambda pos: 0
        # FIX: the index here should come from the "index"
        self.subDataFunc['th']    = lambda pos: self.client.laser[0][0][0] + (self.client.laser[0][0][2] * pos) # in degrees
        self.subDataFunc['arc']   = lambda pos: self.client.laser[0][0][2] # in degrees
        self.subDataFunc['x']     = self.hitX
        self.subDataFunc['y']     = self.hitY
	self.subDataFunc['z']     = self.hitZ
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.handle.scan[pos][0], self.devData["noise"])
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = self.getGroupNames

    def __len__(self):
        return self.handle.scan_count
    def getSensorValue(self, pos):
        return SensorValue(self, self.handle.scan[pos][0], pos,
                           (self.handle.pose[0],
                            self.handle.pose[1],
                            0.03,
                            pos - 90),
                           self.devData["noise"])

    def postSet(self, keyword):
        """ Anything that might change after a set """
        self.devData["maxvalue"] = self.rawToUnits(self.devData['maxvalueraw'])

    def hitX(self, pos):
        th = self.client.laser[0][0][0] + (self.client.laser[0][0][2] * pos)
        thr = th * PIOVER180
        dist = self.client.laser[0][1][pos] / 1000.0 # METERS
        return cos(thr) * dist
    def hitY(self, pos):
        th = self.client.laser[0][0][0] + (self.client.laser[0][0][2] * pos)
        thr = th * PIOVER180
        dist = self.client.laser[0][1][pos] / 1000.0 # METERS
        return sin(thr) * dist
    def hitZ(self, pos):
        return 0.03 # meters

class PlayerCommDevice(PlayerDevice):
    def __init__(self, client, name):
        PlayerDevice.__init__(self, client, name)
        self.messages = []
    
    def sendMessage(self, message):
        if self.client.comms == {}:
            print "Need to startDevice('comm') in robot: message not sent"
            return
        self.client.send_message(message)

    def getMessages(self):
        if not 'comms' in dir(self.client) or self.client.comms == {}:
            raise DeviceError, "Need to startDevice('comm') in robot"
        #if self.client.comms[0] != '':
        #    self.update() # this is update in robot
        tmp = self.messages
        # reset queue:
        self.messages = []
        return tmp

    def updateDevice(self):
        for i in self.client.comms:
            msg = self.client.get_comms()
            if msg:
                self.messages.append( msg )

class PlayerPTZDevice(PlayerDevice):

    def __init__(self, client, name):
        PlayerDevice.__init__(self, client, name)
        self.origPose = (0, 0, 120)
        self.devData[".help"] = """.set('/robot/ptz/COMMAND', VALUE) where COMMAND is: pose, pan, tilt, zoom.\n""" \
                                """.get('/robot/ptz/KEYWORD') where KEYWORD is: pose\n"""
        self.notGetables.extend (["tilt", "pan", "zoom"])
        self.devData.update( {"tilt": None, "pan": None,
                              "zoom": None, "command": None, "pose": None} )
        self.devData["supports"] = ["pan", "tilt", "zoom"]

    def preGet(self, keyword):
        if keyword == "pose": # make sure it is the current pose
            self.devData["pose"] = self.client.get_ptz()

    def postSet(self, keyword):
        if keyword == "pose":
            self.setPose( *self.devData[keyword] )
        elif keyword == "pan":
            self.pan( self.devData[keyword] )
        elif keyword == "tilt":
            self.tilt( self.devData[keyword] )
        elif keyword == "zoom":
            self.zoom( self.devData[keyword] )

    def init(self):
        self.setPose( *self.origPose )

    def setPose(self, *args):
        if len(args) == 3:
            pan, tilt, zoom = args[0], args[1], args[2]
        elif len(args[0]) == 3:
            pan, tilt, zoom = args[0][0], args[0][1], args[0][2]
        else:
            raise AttributeError, "setPose takes pan, tilt, and zoom"
        return self.client.set_ptz(pan, tilt, zoom)

    def getPose(self):
        return self.client.get_ptz()

    def pan(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(numDegrees, ptz[1], ptz[2])

    def panRel(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0] + numDegrees, ptz[1], ptz[2])

    def tilt(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0], numDegrees, ptz[2])

    def tiltRel(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0], ptz[1] + numDegrees, ptz[2])

    def panTilt(self, panDeg, tiltDeg):
        ptz = self.getPose()
        return self.client.set_ptz(panDeg, tiltDeg, ptz[2])

    def panTiltRel(self, panDeg, tiltDeg):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0] + panDeg, ptz[1] + tiltDeg, ptz[2])

    def center(self):
        return self.setPose( *self.origPose )

    def zoom(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0], ptz[1], numDegrees)

    def zoomRel(self, numDegrees):
        ptz = self.getPose()
        return self.client.set_ptz(ptz[0], ptz[1], ptz[2] + numDegrees)

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

class PlayerGripperDevice(PlayerDevice):
    # Gripper functions
    #these also exist: 'gripper_carry', 'gripper_press', 'gripper_stay',
    def __init__(self, client, name):
        PlayerDevice.__init__(self, client, name)
        if "data" in self.devData:
            del self.devData["data"]
        if self.client.is_paddles_closed():
            self.devData["command"] = "close"
        else:
            self.devData["command"] = "open"
        self.devData[".help"] = """.set('/robot/gripper/command', VALUE) where VALUE is: open, close, stop, up,\n""" \
                                """     down, store, deploy, halt.\n""" \
                                """.get('/robot/gripper/KEYWORD') where KEYWORD is: state, breakBeamState,\n""" \
                                """     isClosed, isMoving, isLiftMoving, isLiftMaxed"""
        #self.notGetables.extend( [] )
        self.notSetables.extend( ["state", "breakBeamState", "isClosed",
                                  "isMoving", "isLiftMoving", "isLiftMaxed"] )
        self.devData.update( {"state": None, "breakBeamState": None, "isClosed": None,
                              "isMoving": None, "isLiftMoving": None, "isLiftMaxed": None} )

    def postSet(self, keyword):
        if keyword == "command":
            if self.devData["command"] == "open":
                self.devData["command"] = self.client.gripper_open() 
            elif self.devData["command"] == "close":
                self.devData["command"] = self.client.gripper_close() 
            elif self.devData["command"] == "stop":
                self.devData["command"] = self.client.gripper_stop()
            elif self.devData["command"] == "up":
                self.devData["command"] = self.client.gripper_up()
            elif self.devData["command"] == "down":
                self.devData["command"] = self.client.gripper_down()
            elif self.devData["command"] == "store":
                self.devData["command"] = self.client.gripper_store() 
            elif self.devData["command"] == "deploy":
                self.devData["command"] = self.client.gripper_deploy()
            elif self.devData["command"] == "halt":
                self.devData["command"] = self.client.gripper_halt()
            else:
                raise AttributeError, "invalid command to gripper: '%s'" % self.devData["command"]

    def preGet(self, keyword):
        if keyword == "state":
            self.devData[keyword] = self.client.is_paddles_closed() # help!
        elif keyword == "breakBeamState":
            self.devData[keyword] = self.getBreakBeamState()
        elif keyword == "isClosed":
            self.devData[keyword] = self.client.is_paddles_closed() #ok
        elif keyword == "isMoving":
            self.devData[keyword] = self.client.is_paddles_moving() #ok
        elif keyword == "isLiftMoving":
            self.devData[keyword] = self.client.is_lift_moving() # ok
        elif keyword == "isLiftMaxed":
            self.devData[keyword] = self.client.is_lift_up() # ok

    def open(self):
        return self.client.gripper_open() 

    def close(self):
        return self.client.gripper_close() 

    def stopMoving(self):
        return self.client.gripper_stop()

    def liftUp(self):
        return self.client.gripper_up()

    def liftDown(self):
        return self.client.gripper_down()

    def liftStop(self):
        return self.client.gripper_stop()

    def store(self):
        return self.client.gripper_store() 

    def deploy(self):
        return self.client.gripper_deploy()

    def halt(self):
        return self.client.gripper_halt()

    def getState(self):
        return self.client.is_paddles_closed() # help!

    def getBreakBeamState(self):
        sum = 0
        if self.client.is_ibeam_obstructed() == 8:
            sum += 2
        if self.client.is_obeam_obstructed() == 4:
            sum += 1
        return sum

    def isClosed(self): # FIX: add this to aria
        return self.client.is_paddles_closed() #ok

    def isMoving(self):
        return self.client.is_paddles_moving() #ok

    def isLiftMoving(self):
        return self.client.is_lift_moving() # ok

    def isLiftMaxed(self):
        return self.client.is_lift_up() # ok

class PlayerUpdater(threading.Thread):
    """
    """
    def __init__(self, runable):
        """
        Constructor, setting initial variables
        """
        self.runable = runable
        self._stopevent = threading.Event()
        self._sleepperiod = 0.001
        # We have to read it this fast to keep up!
        threading.Thread.__init__(self, name="PlayerUpdater")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            id = self.runable.client.read()
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class PlayerRobot(Robot):
    def __init__(self, name = "Player", port = 6665, hostname = 'localhost'):
        Robot.__init__(self) # robot constructor
        self.devData["simulated"] = 1 # FIX: how can you tell?
        self.hostname = hostname
        self.port = port
        self.name = name
        self.connect() # set self.client to player robot
        self.thread = PlayerUpdater(self)
        self.thread.start()
        # a robot with no devices will hang here!
        while self.client.get_devlist() == -1: pass
        # Make sure laser is before sonar, so if you have
        # sonar, it will be the default 'range' device
        devNameList = [playerc.playerc_lookup_name(device.code) for device in self.client.devinfos]
        self.devData["builtinDevices"] = devNameList
        if "blobfinder" in self.devData["builtinDevices"]:
            self.devData["builtinDevices"].append( "camera" )
        self.devData["builtinDevices"].append( "simulation" )
        for device in ["position", "laser", "ir", "sonar", "bumper"]:
            #is it supported? if so start it up:
            if device in devNameList:
                deviceName = self.startDevice(device)
                self.devDataFunc[device] = self.get("/devices/%s0/object" % device)
                if device == "laser":
                    self.devDataFunc["range"] = self.get("/devices/laser0/object")
                elif device == "ir":
                    self.devDataFunc["range"] = self.get("/devices/ir0/object")
                elif device == "sonar":
                    self.devDataFunc["range"] = self.get("/devices/sonar0/object")
                elif device == "position":
                    self.devData["supportedFeatures"].append( "odometry" )
                    self.devData["supportedFeatures"].append( "continuous-movement" )
        if "range" in self.devDataFunc:
            self.devData["supportedFeatures"].append( "range-sensor" )
        # try to add a simulation device from port 7000
        try:
            self.startDevice("simulation")
        except:
            self.devData["builtinDevices"].remove("simulation")
            del self.device["simulation0"]
            print "No such device 'simulation0' on port 7000!"
        # specific things about this robot type:
        self.devData["port"] = port
        self.devData["hostname"] = hostname
        # default values for all robots:
        self.devData["stall"] = 0
        self.devData["x"] = 0.0
        self.devData["y"] = 0.0
        self.devData["th"] = 0.0
        self.devData["thr"] = 0.0
        # Can we get these from player?
        self.devData["radius"] = 0.75
        self.devData["type"] = "Player"
        self.devData["subtype"] = 0
        self.devData["units"] = "METERS"
        self.devData["name"] = self.name
        self.localize(0.0, 0.0, 0.0)
        self.update()

    def destroy(self):
        self.thread.join()
        try:
            self.simulation.join()
        except:
            pass

    def startDeviceBuiltin(self, item):
##         if item == "ptz":
##             return {"ptz": PlayerPTZDevice(self.client, "ptz")}
##         elif item == "gripper":
##             return {"gripper": PlayerGripperDevice(self.client, "gripper")}
        if item == "laser":
            return {"laser": PlayerLaserDevice(self.client)}
        elif item == "sonar":
            return {"sonar": PlayerSonarDevice(self.client)}
        elif item == "simulation":
            obj = None
            try:
                obj = PlayerSimulationDevice(self.hostname)
            except:
                pass
            return {"simulation": obj}
##         elif item == "camera":
##             if self.devData["simulated"]:
##                 return self.startDevice("BlobCamera", visible=0)
##             else:
##                 return self.startDevice("V4LCamera")
##        elif item in self.devData["builtinDevices"]:
        return {item: PlayerDevice(self.client, item)}
##        else:
##            raise AttributeError, "player robot does not support device '%s'" % item
    
    def translate(self, translate_velocity):
        self.position.handle.set_cmd_vel(translate_velocity, 0, 0, 1)
    def rotate(self, rotate_velocity):
        self.position.handle.set_cmd_vel(0, 0, rotate_velocity, 1)
    def move(self, translate_velocity, rotate_velocity):
        self.position.handle.set_cmd_vel(translate_velocity, 0, rotate_velocity, 1)
        
    def update(self):
        self._update()
        if self.hasA("position"):
            self.devData["x"] = self.devDataFunc["position"].handle.px
            self.devData["y"] = self.devDataFunc["position"].handle.py
            self.devData["thr"] = self.devDataFunc["position"].handle.pa # radians
            self.devData["th"] = self.devData["thr"] / PIOVER180
            self.devData["stall"] = self.devDataFunc["position"].handle.stall
            
    def localize(self, x = 0, y = 0, th = 0):
        """
        Set robot's internal pose to x (meters), y (meters),
        th (radians)
        """
        if self.hasA("position"):
            #self.client.set_odometry(x * 1000, y * 1000, th)
            self.x = x
            self.y = y
            self.th = th
            self.thr = self.th * PIOVER180

    def connect(self):
        print "hostname=", self.hostname, "port=", self.port
        # FIX: arbitrary time! How can we know server is up and running?
        time.sleep(1)
        self.client = playerc.playerc_client(None, self.hostname, self.port)
        retval = self.client.connect()
        while retval == -1:
            self.client = playerc.playerc_client(None, self.hostname, self.port)
            retval = self.client.connect()

    def removeDevice(self, item):
        self.devData[item].unsubscribe()
        Robot.removeDevice(self, item)
        
if __name__ == '__main__':
    myrobot = PlayerBase()
    myrobot.update()
    #myrobot.translate(.2)
    #myrobot.translate(.0)
    #myrobot.disconnect()
