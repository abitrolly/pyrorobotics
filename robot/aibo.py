"""
Ioana Butoi and Doug Blank
Aibo client commands for talking to the Tekkotsu servers
from Python
"""

from pyro.robot import Robot
from pyro.robot.device import Device
from socket import *
import struct, time, sys

def makeControlCommand(control, amt):
    # HEAD: control is tilt 't', pan 'p', or roll 'r'
    # WALK: control is forward 'f', strafe 's', and rotate 'r'
    return struct.pack('<bf', ord(control), amt) 

class Listener:
    def __init__(self, port, host, protocol = "TCP"):
        self.port = port
        self.host = host
        self.protocol = protocol
        self.runConnect()

    def runConnect(self):
        print >> sys.stderr, "[",self.port,"] connecting ...",
        try:
            if self.protocol == "UDP":
                self.s = socket(AF_INET, SOCK_DGRAM) # udp socket
            elif self.protocol == "TCP":
                self.s = socket(AF_INET, SOCK_STREAM) # udp socket
            done = 0
            while not done:
                try:
                    self.s.connect((self.host,self.port)) # connect to server
                    #self.s.settimeout(1)
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

    def clear(self):
        #try:
        #    while 1:
        #        self.s.recvfrom(4096)
        #except:
        #    pass # socket timeout
        pass

class AiboHeadDevice(Device):
    def __init__(self, robot):
        Device.__init__(self, "ptz")
        self.robot = robot
        # Turn on head remote control if off:
        self.robot.setRemoteControl("Head Remote Control", "on")
        time.sleep(1) # pause for a second
        self.dev   = Listener(10052, self.robot.host) # head movement
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

def readMenu(listener, cnt):
    # print "Reading %d menu entries..." % cnt
    retval = {}
    posDict = {}
    pos = 0
    for line in range(cnt):
        # TODO: what are these?
        x = listener.readUntil() # a number?
        y = listener.readUntil() # selected
        try:
            x, y = int(x), int(y)
        except:
            print "error:", (x, y)
        item = listener.readUntil() # item name
        explain = listener.readUntil() # explain
        if item[0] == "#":   # on
            retval[item[1:]] = "on"
            posDict[item[1:]] = pos
        elif item[0] == "-": # off
            retval[item[1:]] = "off"
            posDict[item[1:]] = pos
        else:                # off
            retval[item] = "off"
            posDict[item] = pos
        pos += 1
    return (retval, posDict)

class AiboRobot(Robot):
    # TODO: put listeners in a dict, referenced by name
    # Look up port here:
    PORT = {"Head Remote Control": 10052,
            "Root Control": 10020,
            "Walk Remote Control": 10050, 
            "EStop Remote Control": 10053
            }
    def __init__(self, host):
        Robot.__init__(self)
        self.host = host
        #---------------------------------------------------
        self.menu_control     = Listener(10020,self.host) # menu controls
        self.menu_control.s.send("!reset\n") # reset menu
        # --------------------------------------------------
        self.readMenu()
        # --------------------------------------------------
        self.setRemoteControl("Walk Remote Control", "on")
        self.setRemoteControl("EStop Remote Control", "on")
        self.setRemoteControl("World State Serializer", "on")
        time.sleep(1) # let the servers get going...
        self.walk_control     = Listener(10050, self.host) # walk command
        self.estop_control    = Listener(10053, self.host) # stop control
        #wsjoints_port   =10031 # world state read sensors
        #wspids_port     =10032 # world state read pids        
        self.sensor_socket    = Listener(10031, self.host) # sensors
        #self.pid_socket       = Listener(10032, self.host) # sensors
        time.sleep(1) # let all of the servers get going...
        self.estop_control.s.send("start\n") # send "stop\n" to emergency stop the robot
        time.sleep(1) # let all of the servers get going...
        self.devData["servers"] = self.menuData['TekkotsuMon']
        self.devData["builtinDevices"] = [ "ptz", "camera" ]
        self.startDevice("ptz")
        self.startDevice("camera")

        # Commands available on menu_control (port 10020):
        # '!refresh' - redisplays the current control (handy on first connecting,
        #               or when other output has scrolled it off the screen)
        # '!reset' - return to the root control
        # '!next' - calls doNextItem() of the current control
        # '!prev' - calls doPrevItem() of the current control
        # '!select' - calls doSelect() of the current control
        # '!cancel' - calls doCancel() of the current control
        # '!msg text' - broadcasts text as a TextMsgEvent
        # '!root text' - calls takeInput(text) on the root control
        # '!hello' - responds with 'hello\ncount\n' where count is the number of times
        #            '!hello' has been sent.  Good for detecting first connection after
        #            boot vs. a reconnect.
        # '!hilight [n1 [n2 [...]]]' - hilights zero, one, or more items in the menu
        # '!input text' - calls takeInput(text) on the currently hilighted control(s)
        # '!set section.key = value' - will be sent to Config::setValue(section,key,value)
        #  any text not beginning with ! - sent to takeInput() of the current control

    def readMenu(self, menu = "TekkotsuMon"):
        self.menu_control.s.send("%s\n" % menu) # go to monitor menu
        self.menuData = {}
        self.posData = {}
        menuRead = None
        while menuRead != menu:
            command = self.menu_control.readUntil()
            while command in ["refresh", "pop", "push"]:
                command = self.menu_control.readUntil()
            # print "Reading menu '%s'..." % command
            menuCount = int(self.menu_control.readUntil()) # Options count
            self.menuData[command], self.posData[command] = readMenu(self.menu_control, menuCount)
            menuRead = command

    def setRemoteControl(self, item, value):
        # "Walk Remote Control", "off"
        if self.menuData["TekkotsuMon"][item] != value:
            self.menu_control.s.send("!reset\n")
            self.menu_control.s.send("2\n") # TekkotsuMon menu
            self.menu_control.s.send("%d\n" % self.posData["TekkotsuMon"][item])
            self.menu_control.clear()
            self.menuData["TekkotsuMon"][item] = value

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
        # 0 RawCamServer: Forwards images from camera, port 10012
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
        # read sensor/pid states:
        # TODO: not quite decoding correctly:
        self.devData["timestamp"] = self.sensor_socket.read(4, "l")
        self.devData["position"] = self.sensor_socket.read(18 * 4, "<18f",all=1)
        self.devData["sensor"] = self.sensor_socket.read(6 * 4, "<6f",all=1)
        self.devData["button"] = self.sensor_socket.read(8 * 4, "<8f",all=1)
        self.devData["duties"] = self.sensor_socket.read(18 * 4, "<18f",all=1)

        self.devData["extra"] = self.sensor_socket.read(10 * 4, "<10f",all=1)

        print >> sys.stderr, "timestamp", self.devData["timestamp"]
        print >> sys.stderr, "position", self.devData["position"]
        print >> sys.stderr, "sensor", self.devData["sensor"]
        print >> sys.stderr, "button", self.devData["button"]
        print >> sys.stderr, "duties", self.devData["duties"]
        print >> sys.stderr, "extra", self.devData["extra"]

        #self.pid_socket.clear()

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

    def setWalk(self, value):
        # If you change the walk, then you have to reconnect
        # back onto the walk server
        code = {"pace":0, "walk":1, "crawl":2}
        self.walk_control.s.close()
        self.menu_control.s.send("!reset\n")
        self.menu_control.s.send("5\n") # walk editor
        self.menu_control.s.send("9\n") # load walk
        self.menu_control.s.send("%d\n" % code[value]) # walk number
        self.menu_control.s.send("0\n") # stop walk socket
        self.menu_control.s.send("0\n") # start walk socket
        self.menu_control.clear() # clear the port
        self.walk_control     = Listener(10050, self.host) # walk command

#TODO:

# 1. How to read sensors? Infrared, Touch, joint positions
# 2. How to change gait? Running? Walking? On knees?
# 3. Create vision C code wrapper (see RobocupCamera as example)
# 4. Make a "virtual range sensor" from vision

# Aibo 3D: Listens to aibo3d control commands coming in from port 10051

# World State Serializer: Sends sensor information to port 10031 and
# current pid values to port 10032
