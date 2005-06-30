""" The main Pyrobot robot object, and support functions


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

import pyrobot.gui.console as console
import pyrobot.system as system
from pyrobot.geometry import Polar, distance
from pyrobot.robot.device import *
import math, string, time, os, sys, types

if float(sys.version[0:3]) < 2.4:
    False = 0
    True  = 1

if not os.environ.has_key('PYROBOT'):
    raise AttributeError, "PYROBOT not defined: export PYROBOT=/usr/local/pyrobot"

def commas(lyst):
    retval = ""
    for i in lyst:
        if retval:
            retval += ", '%s'" % i
        else:
            retval = "'%s'" % i
    return retval

class Robot:
    """
    The base robot class. This class is the basis of all robots.
    """
    def __init__(self, **kwargs):
        """
        The main robot object. Access the last loaded devices here, plus all of
        the robot-specific fields (such as x, y, and th). Use
        robot.move(translate, rotate) to move the robot. If you need to initialize
        things, call setup().
        """
        self.brain = None
        self.timestamp = time.time()
        self.builtinDevices = [] # list of built-in devices
        self.supportedFeatures = [] # meta devices
        self.devices = []
        # some default values:
        self.stall = 0
        self.x = 0
        self.y = 0
        self.th = 0
        self.thr = 0
        # user init:
        self.setup(**kwargs)

    def getAll(self, thing = None, toplevel = "robot", indent = 0):
        if thing == None: thing = self
        dictable = 0
        try:
            thing.__dict__
            dictable = 1
        except: pass
        if dictable:
            if toplevel == "robot":
                print "%s%s:" % (" " * indent, toplevel)
            else:
                print "%s%s:" % (" " * indent, "." + toplevel)
            dictkeys = thing.__dict__.keys()
            dictkeys.sort()
            for item in dictkeys:
                if item[0] == "_":
                    pass # skip it; private
                elif type(thing.__dict__[item]) in [types.FunctionType, types.LambdaType, types.MethodType]:
                    pass # skip it; function
                else:
                    if item in self.devices:
                        count = 0
                        for i in thing.__dict__[item]:
                            self.displayDevice(i, indent + 3, count)
                            count += 1
                    elif type(thing.__dict__[item]) == type({}): # dict
                        print "%s%-15s = {%s}" % (" " * (indent + 3), "." + item, commas(thing.__dict__[item].keys()))
                    elif type(thing.__dict__[item]) == type(''): # string
                        print "%s%-15s = '%s'" % (" " * (indent + 3), "." + item, thing.__dict__[item])
                    else:
                        print "%s%-15s = %s" % (" " * (indent + 3), "." + item, thing.__dict__[item])
        else:
            if type(thing) == type(''):
                print "%s%-15s = '%s'" % (" " * indent, "." + toplevel, thing)
            else:
                print "%s%-15s = %s" % (" " * indent, "." + toplevel, thing)
        return "Ok"
    def displayDevice(self, device, indent = 0, count = 0):
        toplevel = "%s[%d]" % (device.type, count)
        self.getAll(device, toplevel, indent)

    def localize(self, x = 0, y = 0, th = 0):
        console.log(console.WARNING, "need to override LOCALIZE in robot")

    def moveDir(self, dir):
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

    def update(self):
        self.updateDevices()

    def updateDevices(self):
        self.timestamp = time.time()
        for deviceType in self.devices:
            for device in self.__dict__[deviceType]:
                if device.active:
                    device.updateDevice()

    # Need to define these:

    def connect(self): pass
    def disconnect(self): pass

    def move(self, translate, rotate):
        pass

    def translate(self, val):
        pass

    def rotate(self, val):
        pass

    # -------------------- Angle and Distance functions:

    def getAngleToAngle(self, phi): # phi is in radians
        '''
        Given an angle in radians (0 front, to left to PI), what is the
        shortest way to turn there?  returns -PI to PI, neg to right,
        to use with turning
        '''
        theta = self.thr
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
        return self.getAngleToPoints(x, y, self.x, self.y)
                                     
    def getAngleToPoints(self, x1, y1, x2, y2):
        p = Polar()
        p.setCartesian(x1 - x2, y1 - y2) # range pi to -pi
        if (p.t < 0.0):
            phi = p.t + 2 * math.pi # 0 to pi to left; 0 to -pi to right
        else:
            phi = p.t;
        return self.getAngleToAngle(phi)

    def getDistanceToPoint(self, x, y):
        return distance(x, y, self.x, self.y)

    # ------------------------- Device functions:

    def getNextDeviceNumber(self, devname):
        """
        robot.sonar[0]
        """
        if devname not in self.__dict__:
            self.devices.append( devname ) # keep track of all of the loaded types
            self.__dict__[devname] = [None]
            return 0
        else:
            self.__dict__[devname].append( None )
            return len(self.__dict__[devname]) - 1

    def startDevice(self, item, **args):
        dev = self.startDevices(item, **args)
        if len(dev) < 1:
            raise AttributeError, ("unknown device: '%s'" % item)
        else:
            return dev[0]
        
    def startDevices(self, item, override = False, **args):
        """ Load devices: dict, list, builtin name, or filename """
        # Item can be: dict, list, or string. string can be name or filename
        if type(item) == type({}):
            # this is the only one that does anything
            retval = []
            for dev in item.keys():
                deviceNumber = self.getNextDeviceNumber(dev)
                console.log(console.INFO,"Loading device %s[%d]..." % (dev, deviceNumber))
                self.__dict__[dev][deviceNumber] = item[dev]
                item[dev].setTitle( dev + "[" + str(deviceNumber) + "]" )
                retval.append(item[dev]) # return object
            return retval
        elif item in self.builtinDevices: # built-in name
            # deviceBuiltin returns dictionary
            deviceList = self.startDeviceBuiltin(item)
            if type(deviceList) == type("device"): # loaded it here, from the robot
                return [ deviceList ]
            else:
                return self.startDevices( deviceList, **args ) # dict of objs
        elif isinstance(item, (type((1,)), type([1,]))):
            retval = []
            for i in item:
                retval.append( self.startDevice(i, **args) )
            return retval
        else: # from a file
            file = item
            if file[-3:] != '.py':
                file = file + '.py'
            if system.file_exists(file):
                return self.startDevices( system.loadINIT(file, self), **args )
            elif system.file_exists(os.getenv('PYROBOT') + \
                                    '/plugins/devices/' + file): 
                return self.startDevices( system.loadINIT(os.getenv('PYROBOT') + \
                                                   '/plugins/devices/'+ \
                                                   file, self), **args)
            else:
                print 'Device file not found: ' + file
                return []

    def startDeviceBuiltin(self, item):
        """ This method should be overloaded """
        raise AttributeError, "no such builtin device '%s'" % item

    def stopDevice(self, item):
        self.__dict__[item].stopDevice()

    def getDevice(self, item):
        if item in self.__dict__:
            return self.__dict__[item][0]
        else:
            raise AttributeError, "unknown device '%s'" % item

    def getDevices(self):
        return self.devices

    def getSupportedDevices(self):
        return self.builtinDevices

    def supports(self, feature):
        return (feature in self.supportedFeatures)

    def requires(self, feature):
        if isinstance(feature, (list, tuple)):
            if len(feature) == 0:
                return 1
            if len(feature) > 0:
                if self.requires(feature[0]):
                    return self.requires(features[1:])
        if feature in self.supportedFeatures:
            return 1
        elif feature in self.devices:
            return 1
        else:
            raise ImportError, "robot does not currently have '%s' loaded." % feature

    def hasA(self, dtype):
        """
        FIXME: meaning changes if allow 0 position. Need another call
        to determine number?
        """
        if dtype in self.devices:
            return 1
        else:
            return 0

    def removeDevice(self, item, number = None):
        if number == None: # remove all
            print "removing all", item, "devices..."
            if item in self.__dict__:
                for device in self.__dict__[item]:
                    device.setVisible(0)
                    device.setActive(0)
                    device.destroy()
                del self.__dict__[item]
            else:
                raise AttributeError,"no such device: '%s'" % item
        else:
            print "removing %s[%d] device..." % (item, number)
            if item in self.__dict__:
                device = self.__dict__[item][number]
                device.setVisible(0)
                device.setActive(0)
                device.destroy()
                del self.__dict__[item][number]
            else:
                raise AttributeError,"no such device: %s[%d]" % (item, number)
        return "Ok"
        
    def destroy(self):
        """
        This method removes all of the devices. Called by the system.
        """
        for item in self.__dict__:
            self.removeDevice(item)

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

    def setRangeSensor(self, name, index = 0):
        """
        Change the default range sensor. By default the range sensor
        is set to be sonar, if a robot has it, or laser, if it has it,
        or IR if a robot has it. Otherwise, it is not set.

        Takes the name of a range sensor, and an optional index identifier.
        An index of 0 is used if not given.

        Examples:

        >>> robot.setRangeSensor("sonar")
        >>> robot.setRangeSensor("laser", 1)

        returns "Ok" on success, otherwise raises an exception.
        """
        self.range = self.__dict__[name][index]
        return "Ok"

if __name__ == "__main__":
    r = Robot()
