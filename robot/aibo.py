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
    sequence = [0] * 5
    bits = struct.pack('f', amt) # Java's FloatToIntBits
    sequence[0] = ord(control) # single char
    sequence[4] = struct.unpack('b', bits[3])[0] 
    sequence[3] = struct.unpack('b', bits[2])[0] 
    sequence[2] = struct.unpack('b', bits[1])[0] 
    sequence[1] = struct.unpack('b', bits[0])[0]
    return struct.pack('bbbbb', *sequence)

class Listener:
    def __init__(self, port = -1, host ="", protocol = "TCP"):
        self.port = port
        self.host = host
        self.protocol = protocol
        if host == "":
            self.isServer = 1
        else:
            self.isServer = 0
        if self.port == -1:
            self.isConnected = 0
        else:
            self.isConnected = 1
            self.startThread()

    def startThread(self):
        self.run()

    def run(self):
        if(self.port >=0):
            if self.isServer:
                self.runServer()
            else:
                self.runConnect()
        else:
            print "Can't start Listner without port"

    def runConnect(self):
        self.attempts = 0
        if (self.attempts == 0):
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
                    done = 1
                except KeyboardInterrupt:
                    print >> sys.stderr, "aborted!"
                    return
                except:
                    print >> sys.stderr, ".",
            print >> sys.stderr, "connected!"
        except IOError, e:
            print e
        self.attempts+=1
        #self.s.close()

    def readUntil(self, stop = "\n"):
        retval = ""
        ch = self.s.recvfrom(1)[0]
        while ch != stop:
            retval += struct.unpack('c', ch)[0]
            ch = self.s.recvfrom(1)[0]
        return retval

    def read(self, bytes = 4, format = 'l'):
        data = self.s.recvfrom(bytes)
        #print "read:", data
        return struct.unpack(format, data[0])[0]

    def write(self, message):
        retval = self.s.send(message)
        return retval

class AiboHeadDevice(Device):
    def __init__(self, robot):
        Device.__init__(self, "ptz")
        self.robot = robot
        # Turn on head remote control if off:
        if self.robot.menuData["TekkotsuMon"]["Head Remote Control"][2] == "off":
            print "Turning on 'Head Remote Control'..."
            self.robot.menu_control.s.send( "2\n")
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
    for line in range(cnt):
        # TODO: what are these?
        x = listener.readUntil() # a number?
        y = listener.readUntil() # a number?
        try:
            x, y = int(x), int(y)
        except:
            print "error:", (x, y)
        item = listener.readUntil() # item name
        explain = listener.readUntil() # explain
        if item[0] == "#":   # on
            retval[item[1:]] = [x, y, "on", explain]
        elif item[0] == "-": # off
            retval[item[1:]] = [x, y, "off", explain]
        else:                # off
            retval[item] = [x, y, "off", explain]
    return retval

class AiboRobot(Robot):
    def __init__(self, host):
        Robot.__init__(self)
        self.host = host
        #---------------------------------------------------
        self.menu_control     = Listener(10020,self.host) # menu controls
        self.menu_control.s.send("!reset\n") # reset menu (maybe should be "!root"?
        self.menu_control.s.send("TekkotsuMon\n") # go to monitor menu
        self.menuData = {}
        # --------------------------------------------------
        menuRead = None
        while menuRead != 'TekkotsuMon':
            command = self.menu_control.readUntil()
            while command in ["refresh", "pop", "push"]:
                command = self.menu_control.readUntil()
            # print "Reading menu '%s'..." % command
            menuCount = int(self.menu_control.readUntil()) # Options count
            self.menuData[command] = readMenu(self.menu_control, menuCount)
            menuRead = command
        # --------------------------------------------------
        # Turn on raw image server if off:
        #TODO: may not need to do this; just: "!root\n", "#Name of Option\n"
        # Turn on walk remote control:
        if self.menuData["TekkotsuMon"]["Walk Remote Control"][2] == "off":
            print "Turning on 'Walk Remote Control'..."
            self.menu_control.s.send( "3\n")
        if self.menuData["TekkotsuMon"]["EStop Remote Control"][2] == "off":
            print "Turning on 'EStop Remote Control'..."
            self.menu_control.s.send( "8\n")
        # TODO: those commands probably left a lot to read on the port
        # but, so what for now? We aren't currently going back to the
        # menus.
        # ######################################################################
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

        #print "Aibo servers starting..."
        # TODO: what are these for:
        #wsjoints_port   =10031
        #wspids_port     =10032
        time.sleep(1) # let the servers get going...
        self.walk_control     = Listener(10050, self.host) # walk command
        self.estop_control    = Listener(10053, self.host) # head movement
        # C code will handle image:
        #self.rawimage_data    = Listener(10011, self.host) # raw_image
        time.sleep(1) # let all of the servers get going...
        self.estop_control.s.send("start\n") # send "stop\n" to emergency stop the robot
        time.sleep(1) # let all of the servers get going...

        servers = {}
        for item in self.menuData["TekkotsuMon"]:
            servers[item] = self.menuData["TekkotsuMon"][item][2] # on or off
        self.devData["servers"] = servers # allows robot.get("robot/servers"); returns dictionary
        self.devData["builtinDevices"] = [ "ptz", "camera" ]

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
        self.walk_control.write( makeControlCommand('s', amount)) 
        
    def move(self, translate, rotate):
        # WALK:
        # forward: -1 to 1 (backward to forward)
        # rotate: -1 to 1 (right to left)
        # strafe (side-to-side) -1 to 1 :(right to left)
        #walk_control.write( makeControlCommand('f', -.3)) # see MechaController.java
        #walk_control.write( makeControlCommand('s', .25)) # or  WalkGUI.java
        #walk_control.write( makeControlCommand('r', -1)) 
        # TODO: what move command is strafe?
        self.walk_control.write( makeControlCommand('f', translate)) 
        self.walk_control.write( makeControlCommand('r', rotate)) 

    def displayServers(self, menu):
        print "%s Servers:" % menu
        menuSorted = self.menuData[menu].keys()
        menuSorted.sort()
        for item in menuSorted:
            print "   %s: \"%s\"" % (item, self.menuData[menu][item][2])

#TODO:

# 1. How to read sensors? Infrared, Touch, joint positions
# 2. How to change gait? Running? Walking? On knees?
# 3. Create vision C code wrapper (see RobocupCamera as example)
# 4. Make a "virtual range sensor" from vision

# Aibo 3D: Listens to aibo3d control commands coming in from port 10051

# World State Serializer: Sends sensor information to port 10031 and
# current pid values to port 10032
