"""
Pyro module for interfacing with the Robocup Server.

TODO: need localize that would triangulate from flags/landmarks OR
      need someother way of dead reckoning (for x, y, th)
      need to make unique colors of lines and objects
      need to make laser sensor have more than single angle hits
"""
from socket import *
from pyro.robot import Robot
from pyro.robot.device import Device
from random import random
from time import sleep
from math import pi, sin, cos
import threading

PIOVER180 = pi / 180.0

class ReadUDP(threading.Thread):
    """
    A thread class for reading UDP data.
    """
    BUF = 10000
    def __init__(self, robot):
        """
        Constructor, setting initial variables
        """
        self.robot = robot
        self._stopevent = threading.Event()
        self._sleepperiod = 0.0
        threading.Thread.__init__(self, name="ReadUDP")
        
    def run(self):
        """
        overload of threading.thread.run()
        main control loop
        """
        while not self._stopevent.isSet():
            data, addr = self.robot.socket.recvfrom(self.BUF)
            if len(data) > 0:
                self.robot.processMsg(parse(data), addr)
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        """
        Stop the thread
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

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

class RobocupTruthDevice(Device):
    """ A Truth Device for the Robocup robot"""
    def __init__(self, robot):
        Device.__init__(self, "truth")
        self.robot = robot
        self.devData["pose"] = (0, 0)
    def postSet(self, item):
        if item == "pose":
            self.robot.sendMsg("(move %f %f)" % (self.devData["pose"][0], self.devData["pose"][1] ))
            
class RobocupLaserDevice(Device):
    def __init__(self, robot):
        Device.__init__(self, "laser")
        self.robot = robot
        count = 90
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
        self.devData["noise"]    = 0.0
        # -------------------------------------------
        self.devData["rawunits"] = "METERS"
        self.devData['maxvalueraw'] = 100.0
        # -------------------------------------------
        # These are fixed in meters: DO NOT CONVERT ----------------
        self.devData["radius"] = 0.750 # meters
        # ----------------------------------------------------------
        # MM to units:
        self.devData["maxvalue"] = self.rawToUnits(self.devData['maxvalueraw'])
        # -------------------------------------------
        self.devData['index'] = 0 # self.dev.laser.keys()[0] FIX
        self.devData["count"] = count
        self.subDataFunc['ox']    = lambda pos: 0
        self.subDataFunc['oy']    = lambda pos: 0
        self.subDataFunc['oz']    = lambda pos: 0
        # FIX: the index here should come from the "index"
        self.subDataFunc['th']    = lambda pos: pos - 45 # in degrees
        self.subDataFunc['thr']   = lambda pos: (pos - 45) * PIOVER180 
        self.subDataFunc['arc']   = lambda pos: 1
        self.subDataFunc['x']     = self.getX
        self.subDataFunc['y']     = self.getY
	self.subDataFunc['z']     = lambda pos: 0.03 # meters
        self.subDataFunc['value'] = lambda pos: self.rawToUnits(self.getVal(pos), self.devData["noise"]) 
        self.subDataFunc['pos']   = lambda pos: pos
        self.subDataFunc['group']   = self.getGroupNames

    def postSet(self, keyword):
        """ Anything that might change after a set """
        self.devData["maxvalue"] = self.rawToUnits(self.devData['maxvalueraw'])

    def updateDevice(self):
        self.values = [self.devData["maxvalueraw"]] * self.devData["count"]
        try:
            see = self.robot.get("robot/see")
        except:
            print "waiting for Robocup laser to come online..."
            return # not ready yet
        see.sort(lambda x,y: cmp(y[1],x[1]))
        # compute hits
        # TODO: make these hits a little wider; just one degree right now
        for item in see:
            # item is something like: [['f', 'c'], 14, 36, 0, 0]
            if len(item) >= 3: # need distance, angle
                if item[0][0] == 'f' and item[0][1] == 'l' or \
                       item[0][0] == 'f' and item[0][1] == 'b' or \
                       item[0][0] == 'f' and item[0][1] == 't' or \
                       item[0][0] == 'f' and item[0][1] == 'r':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[pos] = item[1]
                elif item[0][0] == 'p':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[ pos ] = item[1]
                elif item[0][0] == 'b':
                    pos = min(max(int(item[2]) + 45,0),89)
                    self.values[ pos ] = item[1]
                    
    def getVal(self, pos):
        return self.values[pos] # zero based, from right

    def getX(self, pos):
        thr = (pos - 45.0) * PIOVER180
        dist = self.getVal(pos) # METERS
        return cos(thr) * dist

    def getY(self, pos):
        thr = (pos - 45.0) * PIOVER180
        dist = self.getVal(pos) # METERS
        return sin(thr) * dist

class RobocupRobot(Robot):
    """ A robot to interface with the Robocup simulator. """
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
        self.devData["address"] = (self.devData["host"], self.devData["port"])
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.reader = ReadUDP(self)
        self.reader.start()
        msg = "(init %s (version 9.0)" % self.devData["name"]
        if goalie:
            msg += "(goalie)"
        msg += ")" 
        self.socket.sendto(msg, self.devData["address"])
        # wait to get the real address
        while self.devData["address"][1] == self.devData["port"]: pass
        self.devData["builtinDevices"] = ["truth", "laser"]
        self.startDevice("truth")
        self.startDevice("laser")
        self.set("/devices/truth0/pose", (random() * 100 - 50,
                                          random() * 20 - 10))
        self.devDataFunc["range"] = self.get("/devices/laser0/object")
        # default values for all robots:
        self.devData["stall"] = 0
        self.devData["x"] = 0.0
        self.devData["y"] = 0.0
        self.devData["th"] = 0.0
        self.devData["thr"] = 0.0
        # Can we get these from robocup?
        self.devData["radius"] = 0.75
        self.devData["type"] = "Robocup"
        self.devData["subtype"] = 0
        self.devData["units"] = "METERS"
        self.localize(0, 0, 0)
        self.update()
        
    def startDeviceBuiltin(self, item):
        if item == "truth":
            return {"truth": RobocupTruthDevice(self)}
        if item == "laser":
            return {"laser": RobocupLaserDevice(self)}
        else:
            raise AttributeError, "robocup robot does not support device '%s'" % item
        
    def sendMsg(self, msg, address = None):
        if address == None:
            address = self.devData["address"]
        self.socket.sendto(msg + chr(0), address)

    def disconnect(self):
        self.stop()
        self.socket.close()

    def messageHandler(self, message):
        """ Write your own message handler here. """
        if message[0] == "hear":
            print "heard message:", message[1:]

    def processMsg(self, msg, addr):
        self.lastHistory = self.historyNumber % self.historySize
        if len(msg):
            self.history[self.lastHistory] = msg
            self.historyNumber += 1
            if msg[0] == "init":
                self.devData[msg[0]] = msg[1:]
                self.devData["address"] = addr
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

