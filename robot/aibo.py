"""
Ioana Butoi and Doug Blank
Aibo client commands for talking to the Tekkotsu servers
from Python
"""

from pyro.robot import Robot
from socket import *
import struct, time, sys

def readMenu(listener, cnt):
    print "Reading %d menu entries..." % cnt
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
            print "[",self.port,"] connecting ...";
        try:
            if self.protocol == "UDP":
                self.s = socket(AF_INET, SOCK_DGRAM) # udp socket
            elif self.protocol == "TCP":
                self.s = socket(AF_INET, SOCK_STREAM) # udp socket
            self.s.connect((self.host,self.port)) # connect to server
            print "[",self.port,"] connected"
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
            print "Reading menu '%s'..." % command
            menuCount = int(self.menu_control.readUntil()) # Options count
            self.menuData[command] = readMenu(self.menu_control, menuCount)
            menuRead = command
        # --------------------------------------------------
        # Turn on raw image server if off:
        #TODO: may not need to do this; just: "!root\n", "#Name of Option\n"
        if self.menuData["TekkotsuMon"]["RawCamServer"][2] == "off":
            print "Turning on 'RawCamServer'..."
            self.menu_control.s.send( "0\n")
        # Turn on head remote control if off:
        if self.menuData["TekkotsuMon"]["Head Remote Control"][2] == "off":
            print "Turning on 'Head Remote Control'..."
            self.menu_control.s.send( "2\n")
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

        print "Aibo servers starting..."
        # TODO: what are these for:
        #wsjoints_port   =10031
        #wspids_port     =10032
        self.walk_control     = Listener(10050, self.host) # walk command
        self.head_control     = Listener(10052, self.host) # head movement
        self.estop_control    = Listener(10053, self.host) # head movement
        self.rawimage_data    = Listener(10011, self.host) # raw_image
        time.sleep(1) # let all of the servers get going...
        self.estop_control.s.send("start\n") # send "stop\n" to emergency stop the robot
        time.sleep(1) # let all of the servers get going...

        # Example movements:
        # TODO: This will be a device
        # HEAD:
        # tilt: 0 to -1 (straight ahead to down)
        # pan: -1 to 1 (right to left)
        # roll: 0 to 1 (straight ahead, to up (stretched))
        #head_control.write( makeControlCommand('t', -.4)) # see HeadPointListener.java
        #head_control.write( makeControlCommand('p', .75)) # or  HeadPointGUI.java
        #head_control.write( makeControlCommand('r', 0))
        servers = {}
        for item in self.menuData["TekkotsuMon"]:
            servers[item] = self.menuData["TekkotsuMon"][item][2] # on or off
        self.devData["servers"] = servers # allows robot.get("robot/servers"); returns dictionary

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

    def straife(self, amount):
        self.walk_control.write( makeControlCommand('s', amount)) 
        
    def move(self, translate, rotate):
        # WALK:
        # forward: -1 to 1 (backward to forward)
        # rotate: -1 to 1 (right to left)
        # straife (side-to-side) -1 to 1 :(right to left)
        #walk_control.write( makeControlCommand('f', -.3)) # see MechaController.java
        #walk_control.write( makeControlCommand('s', .25)) # or  WalkGUI.java
        #walk_control.write( makeControlCommand('r', -1)) 
        # TODO: what move command is straife?
        self.walk_control.write( makeControlCommand('f', translate)) 
        self.walk_control.write( makeControlCommand('r', rotate)) 

    def displayServers(self, menu):
        print "%s Servers:" % menu
        menuSorted = self.menuData[menu].keys()
        menuSorted.sort()
        for item in menuSorted:
            print "   %s: \"%s\"" % (item, self.menuData[menu][item][2])

    def stepVision(self):
        # this will go into a vision device; see RoboCupCamera, for example
        ## Got type=TekkotsuImage
        ## Got format=0
        ## Got compression=1
        ## Got newWidth=104
        ## Got newHeight=80
        ## Got timest=121465
        ## Got frameNum=3185
        header = rawimage_data.read(4, 'bbbb')  # \r\0\0\0
        type = rawimage_data.readUntil(chr(0)) # "TekkotsuImage"
        print "type:", type
        format = rawimage_data.read()
        print "format:", format
        compression = rawimage_data.read()
        print "compression:", compression
        newWidth = rawimage_data.read()
        print "newWidth:", newWidth
        newHeight = rawimage_data.read()
        print "newHeight:", newHeight
        timeStamp = rawimage_data.read()
        print "timeStamp:", timeStamp
        frameNum = rawimage_data.read()
        print "frameNum:", frameNum
        unknown1 = rawimage_data.read()
        print "unknown1:", unknown1
        ## Got creator=FbkImage
        ## Got chanwidth=104
        ## Got chanheight=80
        ## Got layer=3
        ## Got chan_id=0
        ## Got fmt=JPEGColor
        ## read JPEG: len=2547
        creator = rawimage_data.readUntil(chr(0)) # creator
        print "creator:", creator
        chanWidth = rawimage_data.read()
        print "chanWidth:", chanWidth
        chanHeight = rawimage_data.read()
        print "chanHeight:", chanHeight
        layer = rawimage_data.read()
        print "layer:", layer
        chanID = rawimage_data.read()
        print "chanID:", chanID
        chanWidth = rawimage_data.read()
        print "chanWidth:", chanWidth
        fmt = rawimage_data.readUntil(chr(0)) # fmt
        print "fmt:", fmt
        size = rawimage_data.read()
        print "Reading image %d bytes..." % size
        image = [0 for x in range(size)]
        for x in range(size):
            # Can't seem to read it all at once, cause it
            # isn't ready? Need to read exactly size bytes.
            image[x] = rawimage_data.s.recvfrom(1)
        # TODO: The image is in JPEG format. Need to uncompress into RGB
        # and get into a shared memory segment for Pyro vision

#TODO:

# 1. How to read sensors? Infrared, Touch, joint positions
# 2. How to change gait? Running? Walking? On knees?
# 3. Create vision C code wrapper (see RobocupCamera as example)
# 4. Make a "virtual range sensor" from vision
