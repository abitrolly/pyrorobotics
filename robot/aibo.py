"""
Ioana Butoi and Doug Blank
Aibo client commands for talking to the Tekkotsu servers
from Python
"""

from socket import *
import struct, time, sys

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

def readMenu(listener, cnt):
    print "Reading %d menu entries..." % cnt
    retval = {}
    for line in range(cnt):
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

try:
    robotIP = sys.argv[1]
except:
    robotIP = "165.106.240.98"
#---------------------------------------------------
menu_control     = Listener(10020,robotIP) # menu controls
menu_control.s.send("!reset\n") # reset menu
menu_control.s.send("TekkotsuMon\n") # go to monitor menu
menuData = {}
# --------------------------------------------------
menuRead = None
while menuRead != 'TekkotsuMon':
    command = menu_control.readUntil()
    while command in ["refresh", "pop", "push"]:
        command = menu_control.readUntil()
    print "Reading menu '%s'..." % command
    menuCount = int(menu_control.readUntil()) # Options count
    menuData[command] = readMenu(menu_control, menuCount)
    menuRead = command
# --------------------------------------------------
# Turn on raw image server if off:
if menuData["TekkotsuMon"]["RawCamServer"][2] == "off":
    print "Turning on 'RawCamServer'..."
    menu_control.s.send( "RawCamServer\n")
# Turn on head remote control if off:
if menuData["TekkotsuMon"]["Head Remote Control"][2] == "off":
    print "Turning on 'Head Remote Control'..."
    menu_control.s.send( "2\n")
# Turn on walk remote control:
if menuData["TekkotsuMon"]["Walk Remote Control"][2] == "off":
    print "Turning on 'Walk Remote Control'..."
    menu_control.s.send( "3\n")
# TODO: those commands probably left a lot to read on the port
# but, so what for now? We aren't currently going back to the
# menus.

print "Aibo servers starting..."
time.sleep(2)
#estopControl_port=10053
#wsjoints_port=10031
#wspids_port=10032
walk_control     = Listener(10050, robotIP, "UDP") # walk command
head_control     = Listener(10052, robotIP, "UDP") # head movement
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

head_control.s.write( makeControlCommand('t', 0)) # see HeadPointListener.java
head_control.s.write( makeControlCommand('p', 0)) # or  HeadPointGUI.java
head_control.s.write( makeControlCommand('r', 0)) 

walk_control.s.write( makeControlCommand('f', 0)) # see MechaController.java
walk_control.s.write( makeControlCommand('s', 0)) # or  WalkGUI.java
walk_control.s.write( makeControlCommand('r', 0)) 

rawimage_data   = Listener(10011, robotIP) # raw_image
# now, just process image data. This should be in a thread:
while 1:
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
    # The image is in JPEG format. Need to uncompress into RGB
    # and get into a shared memory segment for Pyro vision
