from socket import *
from pyro.robot import Robot
from pyro.robot.device import Device
from random import random
from math import pi, sin, cos

PIOVER180 = pi / 180.0

def lookup(thing):
    """ Returns ASCII, color, width, height """
    if thing[0] == 'f': # flag
        return "F", "red", 1, 10
    elif thing[0] == 'b': # ball
        return "B", "white", 3, 3
    elif thing[0] == 'l': # line
        return None, None, None, None
    elif thing[0] == 'p': # player
        return "P", "yellow", 3, 3
    elif thing[0] == 'g': # goal
        return "G", "blue", 1, 10 # FIX: make my goal different
    else:
        print "unknown thing:", thing
        return None, None, None, None

def makeDict(pairs):
    """ Turns list of [name, value] pairs into a dict {name: value, ...} or {name: [values], ...}"""
    dict = {}
    for item in pairs:
        if len(pairs) == 2:
            dict[item[0]] = item[1]
        else:
            dict[item[0]] = item[1:] # list of rest
    return dict

def lex(str):
    """ Simple lexical analizer for Lisp-like parser."""
    retval = []
    currentword = ""
    for ch in str:
        if ch == "(":
            if currentword:
                retval.append(currentword)
            retval.append("(")
            currentword = ""
        elif ch == ")":
            if currentword:
                retval.append(currentword)
            retval.append(")")
            currentword = ""
        elif ch == " ":
            if currentword:
                retval.append(currentword)
            currentword = ""
        elif ord(ch) == 0:
            pass
        else:
            currentword += ch
    if currentword:
        retval.append(currentword)
    return retval

def parse(str):
    """ Lisp-like parser. Takes str, returns Python list. """
    lexed = lex(str)
    stack = []
    currentlist = []
    for symbol in lexed:
        if symbol == "(":
            stack.append( currentlist )
            currentlist = []
        elif symbol == ")":
            if len(stack) == 0:
                print "too many closing parens:", str
                return []
            currentlist, temp = stack.pop(), currentlist
            currentlist.append( temp )
        else:
            if symbol.isalpha():
                currentlist.append( symbol )
            elif symbol.isdigit():
                currentlist.append( int(symbol) )
            else:
                try:
                    # doesn't get "drop_ball" above
                    # in the isalpha test
                    currentlist.append( float(symbol) )
                except:
                    if len(symbol) > 1 and symbol[0] == '"' and symbol[-1] == '"':
                        symbol = symbol[1:-1]
                    currentlist.append( symbol )
    if len(stack) != 0:
        print "missing ending paren:", str
        return []
    return currentlist[0]

class TruthDevice(Device):
    """ A Truth Device for the Robocup robot"""
    def __init__(self, dev, type = "truth"):
        Device.__init__(self, type)
        self.dev = dev
        self.devData["pose"] = (0, 0)
    def postSet(self, item):
        if item == "pose":
            self.dev.sendMsg("(move %f %f)" % (self.devData["pose"][0], self.devData["pose"][1] ))
            

class RobocupRobot(Robot):
    """ A robot to interface with the Robocup simulator. """
    BUF = 10000
    def __init__(self, name="TeamPyro", host="localhost", port=6000,
             goalie = 0):
        Robot.__init__(self)
        self.lastTranslate = 0
        self.lastRotate = 0
        self.updateNumber = 0L
        self.historyNumber = 0L
        self.lastHistory = 0
        self.historySize = 100
        self.history = [0] * self.historySize
        self.devData["simulated"] = 1
        self.devData["name"] = name
        self.devData["host"] = host
        self.devData["port"] = port
        self.devData["continuous"] = 1
        self.devData["goalie"] = goalie
        self.address = (self.devData["host"], self.devData["port"])
        self.socket = socket(AF_INET, SOCK_DGRAM)
        msg = "(init %s (version 9.0)" % self.devData["name"]
        if goalie:
            msg += "(goalie)"
        msg += ")" 
        self.socket.sendto(msg, self.address)
        # get the real address
        self.processMsg(10)
        self.devData["builtinDevices"] = ["truth"]
        self.startDevice("truth")
        self.set("/devices/truth0/pose", (random() * 100 - 50,
                          random() * 20 - 10))
        
    def startDeviceBuiltin(self, item):
        if item == "truth":
            return {"truth": TruthDevice(self, "truth")}
        else:
            raise AttributeError, "robocup robot does not support device '%s'" % item
        
    def sendMsg(self, msg, address = None):
        if address == None:
            address = self.address
        self.socket.sendto(msg + chr(0), address)

    def getMsg(self):
        data, addr = self.socket.recvfrom(self.BUF)
        return parse(data), addr

    def disconnect(self):
        self.stop()
        self.socket.close()

    def messageHandler(self, message):
        """ Write your own message handler here. """
        if message[0] == "hear":
            print "heard message:", message[1:]

    def processMsg(self, times = 1):
        for n in range(times):
            self.lastHistory = self.historyNumber % self.historySize
            msg, addr = self.getMsg()
            if len(msg):
                self.history[self.lastHistory] = msg
                self.historyNumber += 1
                if msg[0] == "init":
                    self.devData[msg[0]] = msg[1:]
                    self.address = addr
                elif msg[0] == "server_param":
                    # next is list of pairs
                    self.devData[msg[0]] = makeDict(msg[1:])
                elif msg[0] == "player_param":
                    # next is list of pairs
                    self.devData[msg[0]] = makeDict(msg[1:])
                elif msg[0] == "player_type": # types
                    # next is list of ["id" num], pairs...
                    id = "%s:%d" % (msg[0], msg[1][1])
                    self.devData[id] = makeDict(msg[2:])
                elif msg[0] == "sense_body": # time pairs...
                    self.devData[msg[0]] = makeDict(msg[2:])
                    self.devData["sense_body:time"] = msg[1]
                elif msg[0] == "see": # time tuples...
                    self.devData[msg[0]] = msg[2:]
                    self.devData["%s:time" % msg[0]] = msg[1]
                elif msg[0] == "error":
                    print "Robocup error:", msg[1]
                elif msg[0] == "warning":
                    print "Robocup warning:", msg[1]
                elif msg[0] == "hear": # hear time who what
                    self.devData[msg[0]] = msg[2:]
                    self.devData["%s:time" % msg[0]] = msg[1]
                elif msg[0] == "score": 
                    self.devData[msg[0]] = msg[2:]
                    self.devData["%s:time" % msg[0]] = msg[1]
                else:
                    print "unhandled message in robocup.py: '%s'" % msg[0], msg
                self.messageHandler(msg)
            else:
                return

    def update(self):
        self._update()
        self.processMsg(2) # this should probably be in another thread
        if self.devData["continuous"]:
            self.keepGoing()
        self.updateNumber += 1

    def keepGoing(self):
        # only one per cycle!
        if self.lastTranslate and self.lastRotate:
            if self.updateNumber % 2:
                self.translate(self.lastTranslate)
            else:
                self.rotate(self.lastRotate)
        elif self.lastTranslate:
            self.translate(self.lastTranslate)
        elif self.lastRotate:
            self.rotate(self.lastRotate)
            
    def translate(self, translate_velocity):
        # robocup takes values between -100 and 100
        self.lastTranslate = translate_velocity
        val = translate_velocity * 100.0
        self.sendMsg("(dash %f)" % val)

    def rotate(self, rotate_velocity):
        # robocup takes degrees -180 180
        # but that is a lot of turning!
        # let's scale it back a bit
        # also, directions are backwards
        self.lastRotate = rotate_velocity
        val = -rotate_velocity * 20.0
        self.sendMsg("(turn %f)" % val)

    def move(self, translate_velocity, rotate_velocity):
        self.translate(translate_velocity)
        self.rotate(rotate_velocity)

    def getPoint( self, distance, direction): # meters, angle off center
        row = self.height - \
              self.height * cos( direction * PIOVER180 ) * distance/100.0
        col = self.width/2.0 \
              + self.width * sin( direction * PIOVER180 ) * distance/100.0
        if row < 0 or row >= self.height:
            return None, None # off screen
        if col < 0 or col >= self.width:
            return None, None # off screen
        return (int(col), int(row))

    def lookupLines( self, flagName ):
        retval = []
        for lineName in self.lines:
            if flagName in self.lines[lineName]:
                retval.append( lineName )
        return retval

    def makeImage(self, see = None):
        if see == None:
            see = self.get("robot/see")
        self.width = 40
        self.height = 30
        self.depth = 1
        self.image = [" "] * self.height * self.width * self.depth
        self.lines = {"top": ["lt", "ct", "rt"],
                      "left": ["lt", "glt", "gl", "glb", "lb"],
                      "bottom": ["lb", "cb", "rb"],
                      "right": ["rb", "grb", "gr", "grt", "rt"],
                      "Top": ["tl50", "tl40", "tl30", "tl20", "tl10", "t0",
                              "tr50", "tr40", "tr30", "tr20", "tr10"],
                      "Left": ["lt30", "lt20", "lt10", "l0",
                               "lb30", "lb20", "lb10"],
                      "Bottom": ["bl50", "bl40", "bl30", "bl20", "bl10", "b0",
                                 "br50", "br40", "br30", "br20", "br10"],
                      "Right": ["rt30", "rt20", "rt10", "r0",
                                "rb30", "rb20", "rb10"],
                      "center": ["t0", "ct", "c", "cb", "b0"],
                      "1pleft": ["plt", "plc", "plb"],  
                      "2pright": ["prt", "prc", "prb"],  
                      }
        linePoints = {}
        for s in self.lines:
            linePoints[s] = []
        # sort it on distance, further ones first
        see.sort(lambda x,y: cmp(y[1],x[1]))
        # First, go through and draw lines from flags:
        for item in see:
            # item is something like: [['f', 'c'], 14, 36, 0, 0]
            if len(item) > 2: # otherwise, can't do much without direction
                if item[0][0] == "f" or item[0][0] == "g": # it's a flag or goal
                    flagName = ""
                    for ch in item[0][1:]:
                        flagName += "%s" % ch
                    onLines = self.lookupLines( flagName )
                    for onLine in onLines:
                        # distance, direction
                        x, y = self.getPoint( item[1], item[2])
                        if x != None and y != None:
                            linePoints[onLine].append( (x, y) )
        # now, draw the lines:
        for lineName in linePoints:
            if len(linePoints[lineName]) > 0:
                points = linePoints[lineName]
                for (x,y) in points:
                    self.image[y * self.width + x] = lineName[0]
        # now, draw players, ball, and goal
        for item in see:
            if len(item) > 2: # otherwise, can't do much without direction
                itemName = ""
                for ch in item[0]:
                    itemName += "%s" % ch
                color = ""
                if itemName[0] == "p": # it's a player
                    if len(item[0]) > 1:
                        if item[0][1] == self.devData["name"]:
                            color = "Y" # my team player
                        else:
                            color = "P" # other team player
                    else:
                        color = "?" # some player?
                elif itemName == "b": # ball
                    color = "@"
                elif itemName[0] == "g": # center goal
                    color = "G"
                elif itemName == "fgrb" or \
                     itemName == "fgrt" or \
                     itemName == "fglb" or \
                     itemName == "fglt":
                    color = "G" # WHICH IS MINE?
                if color:
                    # draw box proportional to size:
                    x, y = self.getPoint( item[1], item[2])
                    if x != None and y != None:
                        self.image[y * self.width + x] = color
        for y in range(self.height):
            for x in range(self.width):
                print self.image[y * self.width + x],
            print
        print

