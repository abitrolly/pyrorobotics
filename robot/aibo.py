"""
Ioana Butoi and Doug Blank
Aibo client commands for talking to the Tekkotsu servers
from Python.
"""

from pyro.robot import Robot
from pyro.robot.device import Device
from socket import *
import struct, time, sys, threading

def makeControlCommand(control, amt):
    # HEAD: control is tilt 't', pan 'p', or roll 'r'
    # WALK: control is forward 'f', strafe 's', and rotate 'r'
    return struct.pack('<bf', ord(control), amt) 

class Listener:
    """
    A class for talking to ports on Aibo. If you want to read the data off
    in the background, give this thread to ListenerThread, below.
    """
    def __init__(self, port, host, protocol = "TCP"):
        self.port = port
        self.host = host
        self.protocol = protocol
        self.runConnect()
        #self.s.settimeout(0.1)

    def runConnect(self):
        print >> sys.stderr, "[",self.port,"] connecting ...",
        try:
            if self.protocol == "UDP":
                self.s = socket(AF_INET, SOCK_DGRAM) # udp socket
            elif self.protocol == "TCP":
                self.s = socket(AF_INET, SOCK_STREAM) # tcp socket
            done = 0
            while not done:
                try:
                    self.s.connect((self.host,self.port)) # connect to server
                    done = 1
                except KeyboardInterrupt:
                    print >> sys.stderr, "aborted!"
                    return
                except:
                    print >> sys.stderr, ".",
            print >> sys.stderr, "connected!"
        except IOError, e:
            print e

    def readUntil(self, stop = "\n"):
        retval = ""
        ch = self.s.recvfrom(1)[0]
        while ch != stop:
            retval += struct.unpack('c', ch)[0]
            ch = self.s.recvfrom(1)[0]
        return retval

    def read(self, bytes = 4, format = 'l', all=False):
        data = ""
        for i in range(bytes):
            data += self.s.recvfrom(1)[0]
        if all:
            return struct.unpack(format, data)
        else:
            return struct.unpack(format, data)[0]

    def write(self, message):
        retval = self.s.send(message)
        return retval

class ListenerThread(threading.Thread):
    """
    A thread class, for ports where Aibo feeds it to us
    as fast as we can eat em!
    """
    def __init__(self, listener, callback):
        """
        Constructor, setting initial variables
        """
        self.listener = listener
        self.callback = callback
        self._stopevent = threading.Event()
        self._sleepperiod = 0.01
        threading.Thread.__init__(self, name="ListenerThread")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            self.callback(self.listener)
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

class AiboHeadDevice(Device):
    """
    Class for moving the Aibo Head unit as a Pan-Tilt-Zoom-Nod device.
    Does not implement zoom.
    """
    def __init__(self, robot):
        Device.__init__(self, "ptz")
        self.robot = robot
        # Turn on head remote control if off:
        self.robot.setRemoteControl("Head Remote Control", "on")
        time.sleep(1) # pause for a second
        self.dev   = Listener(self.robot.PORT["Head Remote Control"],
                              self.robot.host)
        self.devData["supports"] = ["pan", "tilt", "roll"]
        self.notGetables.extend (["tilt", "pan", "zoom", "roll"])
        self.pose = [0, 0, 0, 0]

    def init(self):
        self.center()

    def postGet(self, keyword):
        if keyword == "pose":
            return self.pose

    def postSet(self, keyword):
        if keyword == "pose":
            self.setPose( self.devData[keyword] )
        elif keyword == "pan":
            self.pan( self.devData[keyword] )
        elif keyword == "tilt":
            self.tilt( self.devData[keyword] )
        elif keyword == "zoom":
            self.zoom( self.devData[keyword] )
        elif keyword == "roll":
            self.roll( self.devData[keyword] )
        return "ok"

    def setPose(self, *args):
        pan, tilt, zoom, roll = 0, 0, 0, 0
        if len(args) == 3:
            pan, tilt, zoom = args[0], args[1], args[2]
        elif len(args) == 4:
            pan, tilt, zoom, roll = args[0], args[1], args[2], args[3]
        elif len(args[0]) == 3:
            pan, tilt, zoom = args[0][0], args[0][1], args[0][2]
        elif len(args[0]) == 4:
            pan, tilt, zoom, roll = args[0][0], args[0][1], args[0][2], args[0][3]
        else:
            raise AttributeError, "setPose takes pan, tilt, zoom (ignored)[, and roll]"
        self.pan( pan )
        self.tilt( tilt )
        self.zoom( zoom )
        self.roll( roll )
        return "ok"

    def zoom(self, amt):
        return "ok"

    def tilt(self, amt):
        # tilt: 0 to -1 (straight ahead to down)
        # see HeadPointListener.java
        if amt > 0:
            amt = 0
        if amt < -1:
            amt = -1
        self.dev.write( makeControlCommand('t', amt))
        self.pose[1] = amt
        return "ok"

    def pan(self, amt):
        # pan: -1 to 1 (right to left)
        # see HeadPointListener.java
        if amt > 1:
            amt = 1
        if amt < -1:
            amt = -1
        self.dev.write( makeControlCommand('p', amt)) 
        self.pose[0] = amt
        return "ok"

    def roll(self, amt):
        # roll: 0 to 1 (straight ahead, to up (stretched))
        if amt < 0:
            amt = 0
        if amt > 1:
            amt = 1
        self.dev.write( makeControlCommand('r', amt))
        self.pose[3] = amt
        return "ok"

    def center(self):
        return self.setPose(0, 0, 0, 0)

class AiboRobot(Robot):
    """
    Class for an Aibo robot in Pyro. 
    """
    # pyro/camera/aibo/__init__.py references this:
    PORT = {"Head Remote Control": 10052,
            "Walk Remote Control": 10050, 
            "EStop Remote Control": 10053,
            "World State Serializer": 10031,
            "Raw Cam Server": 10011,
            "Seg Cam Server": 10012,
            "Main Control": 10020,
            }
    def __init__(self, host):
        Robot.__init__(self)
        self.host = host
        #---------------------------------------------------
        self.main_control     = Listener(self.PORT["Main Control"],
                                         self.host) 
        self.main_control.s.send("!reset\n") # reset menu
        # --------------------------------------------------
        self.setRemoteControl("Walk Remote Control", "on")
        self.setRemoteControl("EStop Remote Control", "on")
        self.setRemoteControl("World State Serializer", "on")
        time.sleep(1) # let the servers get going...
        self.walk_control     = Listener(self.PORT["Walk Remote Control"],
                                         self.host)
        self.estop_control    = Listener(self.PORT["EStop Remote Control"],
                                         self.host) # stop control
        #wsjoints_port   =10031 # world state read sensors
        #wspids_port     =10032 # world state read pids        
        self.sensor_socket    = Listener(self.PORT["World State Serializer"],
                                         self.host) # sensors
        self.sensor_thread    = ListenerThread(self.sensor_socket, self.readWorldState)
        self.sensor_thread.start()
        #self.pid_socket       = Listener(10032, self.host) # sensors
        time.sleep(1) # let all of the servers get going...
        self.estop_control.s.send("start\n") # send "stop\n" to emergency stop the robot
        time.sleep(1) # let all of the servers get going...
        self.devData["builtinDevices"] = [ "ptz", "camera" ]
        self.startDevice("ptz")
        #self.startDevice("camera")

        # Commands available on main_control (port 10020):
        # '!refresh' - redisplays the current control (handy on first connecting,
        #               or when other output has scrolled it off the screen)
        # '!reset' - return to the root control
        # '!next' - calls doNextItem() of the current control
        # '!prev' - calls doPrevItem() of the current control
        # '!select' - calls doSelect() of the current control
        # '!cancel' - calls doCancel() of the current control
        # '!msg text' - broadcasts text as a TextMsgEvent
        # '!root text ...' - calls takeInput(text) on the root control
        # '!hello' - responds with 'hello\ncount\n' where count is the number of times
        #            '!hello' has been sent.  Good for detecting first connection after
        #            boot vs. a reconnect.
        # '!hilight [n1 [n2 [...]]]' - hilights zero, one, or more items in the menu
        # '!input text' - calls takeInput(text) on the currently hilighted control(s)
        # '!set section.key=value' - will be sent to Config::setValue(section,key,value)
        #  any text not beginning with ! - sent to takeInput() of the current control

    def setConfig(self, item, state):
        self.main_control.s.send("!set \"%s=%s\"\n" % (item, state))

    def setRemoteControl(self, item, state):
        # "Walk Remote Control"
        # could also use "!root "TekkotsuMon" %(item)"
        if state == "off":
            item = "#" + item
        self.main_control.s.send("!select \"%s\"\n" % item)

        # Main menu:
        # 0 Mode Switch - Contains the "major" apps, mutually exclusive selection
        # 1 Background Behaviors - Background daemons and monitors
        # 2 TekkotsuMon: Servers for GUIs
        # 3 Status Reports: Displays info about the runtime environment on the console
        # 4 File Access: Access/load files on the memory stick
        # 5 Walk Edit: Edit the walk parameters
        # 6 Posture Editor: Allows you to load, save, and numerically edit the posture
        # 7 Vision Pipeline: Start/Stop stages of the vision pipeline
        # 8 Shutdown?: Confirms decision to reboot or shut down
        # 9 Help: Recurses through the menu, prints name and description of each item

        # Option 2 from Main Menu, TekkotsuMon menu:
        # 0 RawCamServer: Forwards images from camera, port 10011
        # 1 SegCamServer: Forwards segmented images from camera, port 10012
        # 2 Head Remote Control: Listens to head control commands, port 10052
        # 3 Walk Remote Control: Listens to walk control commands, port 10050
        # 4 View WMVars: Brings up the WatchableMemory GUI on port 10061
        # 5 Watchable Memory Monitor: Bidirectional control communication, port 10061
        # 6 Aibo 3D: Listens to aibo3d control commands coming in from port 10051
        # 7 World State Serializer: Sends sensor information to port 10031
        #                           and current pid values to port 10032
        # 8 EStop Remote Control

    def update(self):
        self._update()

    def readWorldState(self, socket):
        """ Used as a callback in ListenerThread for sockets that produce data fast for us to read. """
        # read sensor/pid states:
        self.devData["ws_timestamp"] = socket.read(4, "l")
        # ---
        numPIDJoints = socket.read(4, "l")
        self.devData["numPIDJoints"] = numPIDJoints # ERS7: 18
        self.devData["positionRaw"] = socket.read(numPIDJoints * 4,
                                                  "<%df" % numPIDJoints,all=1)
        # ---
        numSensors = socket.read(4, "l") # ERS7: 8
        self.devData["numSensors"] = numSensors
        self.devData["sensorRaw"] = socket.read(numSensors * 4,
                                                "<%df" % numSensors,all=1)
        # ---
        numButtons = socket.read(4, "l") # ERS7: 6
        self.devData["numButtons"] = numButtons
        self.devData["buttonRaw"] = socket.read(numButtons * 4,
                                                "<%df" % numButtons,all=1)
        # --- same number as PID joints:             # ERS7: 18
        self.devData["dutyCycleRaw"] = socket.read(numPIDJoints * 4,
                                                   "<%df" % numPIDJoints,all=1)
                
    def getJoint(self, query):
        """ Get position, dutyCycle of joint by name """
        legOffset = 0
        numLegs = 4
        jointsPerLeg = 3
        numLegJoints = numLegs*jointsPerLeg
        headOffset = legOffset+numLegJoints
        numHeadJoints = 3
        tailOffset = headOffset + numHeadJoints
        numTailJoints = 2
        mouthOffset = tailOffset + numTailJoints
        jointDict = query.split()
        pos = 0
        for joint in jointDict:
            if joint == "leg":
                pos += legOffset
            elif joint == "head":
                pos += headOffset
            elif joint == "tail":
                pos += tailOffset
            elif joint == "mouth":
                pos += mouthOffset
            elif joint == "front":
                pos += 0
            elif joint == "back":
                pos += numLegs/2*jointsPerLeg
            elif joint == "left":
                pos +=0
            elif joint == "right":
                pos += jointsPerLeg
            elif joint == "rotator":
                # moves leg forward or backward along body
                pos +=0
            elif joint == "elevator":
                # moves leg toward or away from body
                pos += 1
            elif joint == "knee":
                pos += 2
            elif joint == "tilt":
                pos +=0
            elif joint == "pan":
                pos +=1
            elif joint == "roll":
                pos +=2
            elif joint == "nod":
                pos +=2
            else:
                raise AttributeError, "no such joint: '%s'" % joint
        return self.devData["positionRaw"][pos], self.devData["dutyCycleRaw"][pos]

    def getButton(self, query):
        pos = 0
        btnDict = query.split()
        for b in btnDict:
            if b == "chin":
                pos = 4
            elif b == "head":
                pos = 5
            elif b == "body":
                pos +=6
            elif b == "front":
                pos +=0
            elif b == "middle":
                pos +=1
            elif b == "rear":
                pos +=2
            elif b == "wireless":
                pos = 9
            elif b == "paw":
                pos +=0
            elif b == "back":
                pos +=2
            elif b == "left":
                pos +=0
            elif b == "right":
                pos +=1
            else:
                raise AttributeError, "no such button: '%s'" % b
        return self.devData["buttonRaw"][pos]

    def getSensor(self, query):
        pos = 0
        sensDict = query.split()
        for s in sensDict:
            if s == "ir":
                pos +=0
            elif s == "near":
                # in mm 50-500
                pos +=0
            elif s == "far":
                # in mm 200-1500
                pos +=1
            elif s == "chest":
                # in mm 100-900
                pos +=2
            elif s == "accel":
                pos +=3
            elif s == "front-back":
                pos +=0
            elif s == "right-left":
                pos +=1
            elif s == "up-down":
                pos +=2
            elif s == "power":
                pos +=6
            elif s == "remaining":
                pos +=0
            elif s == "thermo":
                pos +=1
            elif s == "capacity":
                pos +=2
            elif s == "voltage":
                pos +=3
            elif s == "current":
                pos +=4
            else:
                raise AttributeError , "no such sensor: '%s'" % b
        return self.devData["sensorRaw"][pos]

    def startDeviceBuiltin(self, item):
        if item == "ptz":
            return {"ptz": AiboHeadDevice(self)}
        elif item == "camera":
            return self.startDevice("AiboCamera")

    def connect(self):
        self.estop_control.s.send("start\n")

    def disconnect(self):
        self.estop_control.s.send("stop\n")

    def enableMotors(self):
        self.estop_control.s.send("start\n")

    def disableMotors(self):
        self.estop_control.s.send("stop\n")

    def rotate(self, amount):
        self.walk_control.write( makeControlCommand('r', amount)) 

    def translate(self, amount):
        self.walk_control.write( makeControlCommand('t', amount)) 

    def strafe(self, amount):
        # strafe (side-to-side) -1 to 1 :(right to left)
        self.walk_control.write( makeControlCommand('s', amount)) 
        
    def move(self, translate, rotate):
        # forward: -1 to 1 (backward to forward)
        # rotate: -1 to 1 (right to left)
        self.walk_control.write( makeControlCommand('f', translate)) 
        self.walk_control.write( makeControlCommand('r', rotate))

    def destroy(self):
        self.sensor_thread.join()
        Robot.destroy(self)

    def setWalk(self, file):
        # PACE.PRM, TIGER.PRM, WALK.PRM (crawl)
        self.walk_control.s.close()
        self.main_control.s.send("!select \"%s\"\n" % "Load Walk") # forces files to be read
        self.main_control.s.send("!select \"%s\"\n" % file) # select file
        self.main_control.s.send("!select \"%s\"\n" % "#WalkControllerBehavior") # turn off
        self.main_control.s.send("!select \"%s\"\n" % "-WalkControllerBehavior") # turn on
        # If you change the walk, then you have to reconnect
        # back onto the walk server
        time.sleep(2)
        self.walk_control     = Listener(self.PORT["Walk Remote Control"],
                                         self.host) # walk command

#TODO:

# 1. How to read sensors? Infrared, Touch, joint positions
# 2. How to change gait? Running? Walking? On knees?
# 3. Make a "virtual range sensor" from vision

# Aibo 3D: Listens to aibo3d control commands coming in from port 10051

# World State Serializer: Sends sensor information to port 10031 and
# current pid values to port 10032
