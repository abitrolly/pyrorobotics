""" The main Pyro robot object, and support functions


 This file contains the class that represents a computer controlled
 physical agent (robot). A robot is a bunch of drivers that offer
 senses and controllers
 -----------------------------
 Main interfaces:
 .get()             - interface to robot, sensors
 .move(), .translate(), .rotate(), .motors(), .stop() - controls

 Units of measure for sense, map, and motors:
 -------------------------------------------
 ROBOTS - unit is given interms of robot's diameter
 METERS - meters
 CM     - centimeters
 MM     - millimeters
 SCALED - scaled [-1,1]
 RAW    - right from the sensor
"""

import pyro.gui.console as console
import pyro.system as system
from pyro.geometry import Polar, distance
from pyro.robot.device import *
import math, string, time, os

def ellipses(things):
    if isinstance(things, (type((1,)), type([1,]))):
        return ellipses_help(things)
    else:
        return things

def makePerty(nums):
    str = "["
    for i in nums:
        if i == -1:
            str += " ... "
        elif str[-1] not in ["[", " "]:
            str += ", %s" % i
        else:
            str += "%s" % i
    return str + "]"

def ellipses_help(things):
    if len(things) < 3:
        return things
    if type(things[0]) != type(1):
        return things
    done = things[0:3]
    for i in range(3,len(things)):
        seq = done[-3:] + [things[i]]
        if seq[-4] + 3 == seq[-3] + 2 == seq[-2] + 1 == seq[-1]:
            done[-2:] = [-1, seq[-1]]
        elif done[-1] + 1 == things[i] and done[-2] == -1:
            done[-1] = things[i]
        else:
            done = done + [things[i]]
    return makePerty(done)

def expand(part):
    """
    Takes a part of a path and parses it for simple syntax. Expands:
    -  inclusive range
    :  slice range
    ,  AND
    """
    #print "expand=", part
    retvals = []
    if type(part) == type(1):
        return part
    elif isinstance(part, (type((1,)), type([1,]))):
        return part
    else:
        if type(part) != type(""):
            raise AttributeError, "path part should be an int, list, tuple, or string keyword"
    # else, it had better be a string
    if part.find(",") >= 0:
        subparts = map(string.strip, part.split(","))
    else:
        subparts = [string.strip(part),]
    for s in subparts:
        if s.count(":") == 1:
            rangeVals = map(string.strip, s.split(":"))
            if rangeVals[0].isdigit() and rangeVals[0].isdigit():
                retvals.extend(range(int(rangeVals[0]), int(rangeVals[1])))
            else:
                if s.isdigit():
                    retvals.append( int(s) )
                else:
                    retvals.append( s )
        elif s.count("-") == 1:
            rangeVals = map(string.strip, s.split("-"))
            #print "rangeVals", rangeVals
            if rangeVals[0].isdigit() and rangeVals[0].isdigit():
                retvals.extend(range(int(rangeVals[0]), int(rangeVals[1]) + 1))
            else:
                if s.isdigit():
                    retvals.append( int(s) )
                else:
                    retvals.append( s )
        else:
            if s.isdigit():
                retvals.append( int(s) )
            else:
                retvals.append( s )
    if len(retvals) == 1:
        return retvals[0]
    else:
        return retvals

class DeviceWrapper:
    def __init__(self, robot):
        self.robot = robot

    def _set(self, path, value):
        return self.robot._setDevice(path, value)

    def _get(self, path, showstars = 0):
        return self.robot._getDevice(path, showstars)

class Robot:
    """
    this be the one.
    """
    def __init__(self, **kwargs):
        """
        if you extend Robot please call this function!
        If you need to initialize things, call setup()
        """
        self.directory = {} # toplevel place for paths
        # In this list are the things that can NOT be set()ed:
        self.notSetables = ['timestamp', "builtinDevices", 'x','y','z','th','thr','stall','model','type','subtype',"simulated"] 
        # In this list are the things that can NOT be get()ed.
        self.notGetables = ['comand']
        #self.notGetables = []
        self.device = {} # what was called services
        self.devData = {} # items in /robot/ path
        self.devDataFunc = {} # function items in /robot/ path
        self.devData['timestamp'] = time.time()
        self.devData['.help'] = "The main robot object. Access the last loaded devices here, plus all of the robot-specific fields (such as x, y, and th). Use robot.move(translate, rotate) to move the robot."
        self.devData["builtinDevices"] = [] # list of built-in devices
        # toplevel:
        self.directory["robot"] = self
        self.directory["devices"] = DeviceWrapper(self)
        # user init:
        self.setup(**kwargs)

    def __repr__(self):
        retval = '---------------------------------\nRobot properties:\n---------------------------------\n'
        items = self.get("robot/")
        items.sort()
        for item in items:
            if item[-1] == "/": # more things below this
                retval += "%12s\n" % item
            else:
                retval += "%12s = %s\n" % (item, self.get("robot/%s" % item))
        return retval

    def disconnect(self):
        console.log(console.WARNING, "need to override DISCONNECT in robot")

    def localize(self, x = 0, y = 0, th = 0):
        console.log(console.WARNING, "need to override LOCALIZE in robot")

    def inform(self, msg):
        console.log(console.INFO, msg)

    def getAll(self, path = '', depth = 0):
        #print "=>" * depth, "getAll", path
        retval = ''
        pathList = self.get(path, showstars = 1)
        if isinstance(pathList, (type((1,)), type([1,]))):
            pathList.sort()
        for item in pathList:
            # HACK! 
            #print "CHECK:", path, item
            try:
                self.get("%s/%s/name" % (path, item))
                #print "%s is an object!" % item
                isDevice = 1
            except:
                #print "%s is NOT an object!" % item
                isDevice = 0
            if isDevice and "/robot/" == path[:7]:
                retval += ("   " * depth) + ("%s = <alias to \"devices/%s\">\n" % (item, self.get("%s/%s/name" % (path, item))))
                continue
            try: # may try to get a non-getable thing:
                if item[0] == "*": # a group (link), do not recur
                    item = item[1:]
                    things = ellipses(self.get("%s/%s/pos" % (path, item), showstars = 1))
                    retval += ("   " * depth) + ("%s = %s\n" % (item, things))
                    if item == "all/":
                        retval += ("   " * depth) + ("   attributes: %s\n" % self.get("%s/1" % (path,), showstars = 1))
                elif item[-1] == "/": # more things below this
                    retval += ("   " * depth) + ("%s\n" % item)
                    #print "HERE A"
                    retval += self.getAll("%s/%s" % (path, item), depth + 1)
                else:
                    #print "MORE", path, item
                    things = ellipses(self.get("%s/%s" % (path, item), showstars = 1))
                    retval += ("   " * depth) + ("%s = %s\n" % (item, things))
            except:
                retval += ("   " * depth) + ("%s - used with set()\n" % (item,))
        return retval

    def _getDevice(self, pathList, showstars = 0):
        if len(pathList) == 0:
            return deviceDirectoryFormat(self.device, 0)
        key = pathList[0]
        args = pathList[1:]
        if key in self.device:
            return self.device[key]._get(args, showstars)
        if key == '*':
            if args != []:
                raise AttributeError, "wildcard feature not implemented in directory middle"
            return deviceDirectoryFormat(self.device, 1) 
        else:
            raise AttributeError, "no such directory item '%s'" % key

    def _get(self, pathList, showstars = 0):
        #print "_get", pathList
        if len(pathList) == 0:
            tmp = self.devData.copy()
            tmp.update( self.devDataFunc )
            return deviceDirectoryFormat(tmp, 0)
        key = pathList[0]
        args = pathList[1:]
        if key in self.devData:
            if len(args) != 0:
                raise AttributeError, "extra path items '%s' after '%s'" % (args, key)
            return self.devData[key]
        elif key in self.devDataFunc:
            return self.devDataFunc[key]._get(args, showstars)
        if key == '*':
            if args != []:
                raise AttributeError, "wildcard feature not implemented in directory middle"
            tmp = self.devData.copy()
            tmp.update( self.devDataFunc )
            return deviceDirectoryFormat(tmp, 1) 
        else:
            raise AttributeError, "no such directory item '%s'" % key

    def help(self, path):
        pathList = path.split("/")
        # remove extra slashes
        while pathList.count("") > 0:
            pathList.remove("")
        if len(pathList) == 1 and pathList[0] == "devices":
            help = "Devices are where all of the peripheral attachments can be located. For example, if the robot has a set of sonar sensors, you'll find the device at robot.get('devices/sonar0'). You'll also find the same information at robot.get('robot/sonar'). Sometimes, there may be more than one device. So you may see 'devices/camera0' and 'devices/camera1' for example."
        else:
            try:
                help = self.get(path, ".help")
            except:
                help = "No such help available"
        return help

    def get(self, device = "", *args, **keywords):
	"""
	this is designed to be the main interface to the robot
	and its parts. There is one assumed piece, self.dev that
	is the actual pointer to the robot device

        Device names should not contain slashes, commas, dashes, or colons, nor have
        spaces as part of their names (actually spaces inside their names is fine).
	"""
        showstars = keywords.get("showstars", 0)
        path = device.split("/")
        # remove extra slashes
        while path.count("") > 0:
            path.remove("")
        path.extend( args )
        if len(path) > 0 and path[-1] == "help":
            return self.help(string.join(path[:-1], "/"))
        # parse path parts for dashes, colons, and commas
        finalPath = []
        for part in path:
            #if isinstance(part, (type((1,)), type([1,]))):
            #    finalPath.extend( part )
            #else:
            finalPath.append(expand( part ) )
        if len(finalPath) == 0:
            return deviceDirectoryFormat(self.directory, 0) # toplevel
        elif finalPath[0] in self.directory:
            #print "finalPath=", finalPath, self.directory
            # pass the command down
            return self.directory[finalPath[0]]._get(finalPath[1:], showstars)
        elif finalPath[0] == '*':
            return deviceDirectoryFormat(self.directory, 1)
        else:
            raise AttributeError, "'%s' is not a root directory" % finalPath[0]

    def _set(self, pathList, value):
        if len(pathList) < 1:
            raise DeviceSetError, "invalid format to set()"
        key = pathList[0]
        args = pathList[1:]
        if key in self.devData:
            if key in self.notSetables:
                raise DeviceSetError, ("%s is not setable" % key)
            self.devData[key] = value
            return "Ok"
        elif key in self.devDataFunc:
            if key in self.notSetables:
                raise DeviceSetError, ("%s is not setable" % key)
            self.devDataFunc[key]._set(args, value)
            return "Ok"
        else:
            raise DeviceSetError, "no setable directory item '%s'" % key

    def _setDevice(self, pathList, value):
        key = pathList[0]
        args = pathList[1:]
        if key in self.device:
            return self.device[key]._set(args, value)
        else:
            raise DeviceSetError, "no setable directory item '%s'" % key
        
    def set(self, device, value):
	"""
	"""
        path = device.split("/")
        # remove extra slashes
        while path.count("") > 0:
            path.remove("")
        if path[0] in self.directory:
            self.directory[path[0]]._set(path[1:], value)
            return "Ok"
        else:
            raise AttributeError, "'%s' is not a root directory" % path[0]

    def setGroup(self, sensorName, groupName, values):
        """ addGroup(sensorName, groupName, values)

        This method is used to add a named group to a sensor.

        Example:

        robot.addGroup("sonar0", "odd", (1, 3, 5))
        
        """
        device = self.getDevice(sensorName)
        device.groups[groupName] = values

    def step(self, dir):
        if dir == 'L':
            self.rotate(.2)
        elif dir == 'R':
            self.rotate(-.2)
        elif dir == 'B':
            self.translate(-.2)
        elif dir == 'F':
            self.translate(0.2)
        elif dir == 'ST':
            self.translate(0.0)
        elif dir == 'SR':
            self.rotate(0.0)

    def motors(self, leftValue, rightValue):
        """
        Move function that takes desired motor values
        and converts to trans and rotate.
        """
        trans = (rightValue + leftValue) / 2.0
        rotate = (rightValue - leftValue) / 2.0
        self.move(trans, rotate)
        
    def stop(self):
        self.move(0, 0)

    def _update(self):
        self.devData['timestamp'] = time.time()
        for device in self.getDevices():
            if self.getDevice(device).getActive():
                self.getDevice(device).updateDevice()

    # Need to define these:

    def move(self, translate, rotate):
        pass

    def translate(self, val):
        pass

    def rotate(self, val):
        pass

    def update(self):
        """
        This is a common control that isn't an act, so we pull it out
        here.
        """
        pass

    def enableMotors(self):
        pass

    def disableMotors(self):
        pass

    # -------------------- Angle and Distance functions:

    def getAngleToAngle(self, phi): # phi is in radians
        '''
        Given an angle in radians (0 front, to left to PI), what is the
        shortest way to turn there?  returns -PI to PI, neg to right,
        to use with turning
        '''
        theta = self.get("/robot/thr")
        if (phi > theta):  # turn left
            phi = phi - theta;
        else: # // turn right
            phi = (theta - phi) * -1.0;
        if (phi > math.pi): # // oops, shorter to turn other direction
            phi = (2 * math.pi - phi) * -1.0;
        if (phi < -math.pi): #// oops, shorter to turn other direction
            phi = (2 * math.pi + phi);
        return min(max(phi / math.pi, -1.0), 1.0)

    def getAngleToPoint(self, x, y):
        return self.getAngleToPoints(x, y, self.get('robot/x'), self.get('robot/y'))
                                     
    def getAngleToPoints(self, x1, y1, x2, y2):
        p = Polar()
        p.setCartesian(x1 - x2, y1 - y2) # range pi to -pi
        if (p.t < 0.0):
            phi = p.t + 2 * math.pi # 0 to pi to left; 0 to -pi to right
        else:
            phi = p.t;
        return self.getAngleToAngle(phi)

    def getDistanceToPoint(self, x, y):
        return distance(x, y, self.get('robot/x'), self.get('robot/y'))

    # ------------------------- Device functions:

    def getNextDeviceName(self, devname):
        for i in range(100):
            if ("%s%d" % (devname, i)) not in self.device:
                return ("%s%d" % (devname, i))
        raise AttributeError, "too many devices of type '%s'" % devname

    def startDevice(self, item):
        return self.startDevices(item)[0]
        
    def startDevices(self, item):
        """ Load devices: dict, list, builtin name, or filename """
        # Item can be: dict, list, or string. string can be name or filename
        if type(item) == type({}):
            # this is the only one that does anything
            retval = []
            for dev in item.keys():
                deviceName = self.getNextDeviceName(dev)
                console.log(console.INFO,"Loading device '%s'..." % deviceName)
                self.device[deviceName] = item[dev]
                item[dev].devData["name"] = deviceName
                self.devDataFunc[dev] = item[dev]
                item[dev].setTitle( deviceName )
                retval.append(deviceName)
                retval.append( None )
            return retval
        elif item in self.devData["builtinDevices"]: # built-in name
            # deviceBuiltin returns dictionary
            return self.startDevices( self.startDeviceBuiltin(item) )
        elif isinstance(item, (type((1,)), type([1,]))):
            retval = []
            for i in item:
                retval.append( self.startDevice(i) )
            return retval
        else: # from a file
            file = item
            if file[-3:] != '.py':
                file = file + '.py'
            if system.file_exists(file):
                return self.startDevices( system.loadINIT(file, self) )
            elif system.file_exists(os.getenv('PYRO') + \
                                    '/plugins/devices/' + file): 
                return self.startDevices( system.loadINIT(os.getenv('PYRO') + \
                                                   '/plugins/devices/'+ \
                                                   file, self))
            else:
                print 'Device file not found: ' + file
                return []

    def startDeviceBuiltin(self, item):
        """ This method should be overloaded """
        raise AttributeError, "no such builtin device '%s'" % item

    def stopDevice(self, item):
        self.getDevice(self, item).stopDevice()

    def getDevice(self, item):
        if self.device.has_key(item):
            return self.device[item]
        else:
            raise AttributeError, "unknown device '%s'" % item

    def getDeviceData(self, item, *args):
        if self.device.has_key(item):
            return self.device[item].getDeviceData(*args)
        else:
            raise AttributeError, "unknown device '%s'" % item

    def getDevices(self):
        return self.device.keys()

    def getSupportedDevices(self):
        return self.devData["builtinDevices"]

    def removeDevice(self, item):
        self.device[item].setVisible(0)
        self.device[item].setActive(0)
        self.device[item].destroy()
        del self.device[item]

    # Message interface:

    def sendMessage(self, message):
        raise AttributeError, "no send message interface"

    def getMessages(self):
        return []

    def setup(self, **kwargs):
        """
        Is called from __init__ so users don't have to call parent
        constructor and all the gory details.
        """
        pass

if __name__ == "__main__":
    r = Robot()
