#
# This file contains the class that represents a computer controlled
# physical agent (robot). A robot is a bunch of drivers that offer
# senses and controllers
#
# - stephen -
#
# -----------------------------
# Main interfaces:
# .get()             - interface to robot, sensors

import pyro.gui.console as console
from pyro.geometry import Polar, distance
import math

# Units of measure for sense, map, and motors:
# -------------------------------------------
# ROBOTS - unit is given interms of robot's diameter
# METERS - meters
# CM     - centimeters
# MM     - millimeters
# SCALED - scaled [-1,1]
# RAW    - right from the sensor

def expand(part):
    """
    Takes a part of a path and parses it for simple syntax. Expands:
    -  inclusive range
    :  slice range
    ,  AND
    """
    retvals = []
    if part.find(",") >= 0:
        subparts = part.split(",")
    else:
        subparts = [part,]
    for s in subparts:
        if s.count(":") == 1:
            rangeVals = s.split(":")
            if rangeVals[0].isdigit() and rangeVals[0].isdigit():
                retvals.extend(range(int(rangeVals[0]), int(rangeVals[1])))
            else:
                if s.isdigit():
                    retvals.append( int(s) )
                else:
                    retvals.append( s )
        elif s.count("-") == 1:
            rangeVals = s.split("-")
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
                        
class Robot:
    """
    this be the one.
    """
    def __init__(self, **kwargs):
        """
        if you extend Robot please call this function!
        If you need to initialize things, call setup()
        """
        self.service = {}
        self.supports = {}
        self.data = {}
        self.dataFunc = {}
        self.service["robot"] = self
        # user init:
        self.setup(**kwargs)

    def __getattr__(self, path):
        return self.get(path)

    def __repr__(self):
        return "Robot name = '%s', type = '%s'" % (self.get("/robot/name"),
                                                   self.get("/robot/type"))

    def disconnect(self):
        console.log(console.WARNING, "need to override DISCONNECT in robot")

    def localize(self, x = 0, y = 0, th = 0):
        console.log(console.WARNING, "need to override LOCALIZE in robot")

    def inform(self, msg):
        console.log(console.INFO, msg)
        
    def set(self, path, value):
	"""
        A method to set the above get.
	"""
        pass # tell the object to set a value

    def _get(self, pathList):
        pass

    def get(self, device, *args):
	"""
	this is designed to be the main interface to the robot
	and its parts. There is one assumed piece, self.dev that
	is the actual pointer to the robot device
	"""
        if device[0] == "/":
            path = device.split("/")
            # remove extra slashes
            while path.count("") > 0:
                path.remove("")
        else: # given in device, args form
            path = [device,]
            path.extend( args )
        # parse path parts for dashes, colons, and commas
        finalPath = []
        for part in path:
            finalPath.append(expand( part ) )
        if len(finalPath) == 0:
            return self.service.keys()
        elif finalPath[0] in self.service:
            return self.service[finalPath[0]]._get(finalPath[1:])
        elif finalPath[0] == '*':
            return self.service
        else:
            raise AttributeError, "'%s' is not a service of robot" % finalPath[0]

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
        for service in self.getServices():
            if self.getService(service).active:
                self.getService(service).updateService()

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
        theta = self.get("/robot/thr/")
        if (phi > theta):  # turn left
            phi = phi - theta;
        else: # // turn right
            phi = (theta - phi) * -1.0;
        if (phi > math.pi): # // oops, shorter to turn other direction
            phi = (2 * math.pi - phi) * -1.0;
        if (phi < -math.pi): #// oops, shorter to turn other direction
            phi = (2 * math.pi + phi);
        return phi

    def getAngleToPoint(self, x, y):
        return self.getAngleToPoints(x, y, \
                                     self.senses['robot']['x'](self.dev), \
                                     self.senses['robot']['y'](self.dev))
                                     
    def getAngleToPoints(self, x1, y1, x2, y2):
        p = Polar()
        p.setCartesian(x1 - x2, y1 - y2) # range pi to -pi
        if (p.t < 0.0):
            phi = p.t + 2 * math.pi # 0 to pi to left; 0 to -pi to right
        else:
            phi = p.t;
        return self.getAngleToAngle(phi)

    def getDistanceToPoint(self, x, y):
        return distance(x, y, \
                        self.senses['robot']['x'](self.dev), \
                        self.senses['robot']['y'](self.dev))


    # ------------------------- Service functions:

    def startServices(self, item):
        """ Alias for startService() """
        return self.startService(item)
        
    def startService(self, item):
        """ Load a service: dict, list, or name or filename """
        import pyro.system as system
        import os
        # Item can be: dict, list, or string. string can be name or filename
        if type(item) == type({}):
            retval = []
            for service in item.keys():
                console.log(console.INFO,"Loading service '%s'..." % service)
                if self.service.has_key(service):
                    print "Service is already running: '%s'" % service
                    retval.append( self.service[service] )
                else:
                    retval.append(item[service].startService())
                if item[service].getServiceState() == "started":
                    self.service[service] = item[service]
                    if service not in self.senses.keys():
                        self.senses[service] = self.service[service]
                else:
                    print "service '%s' not available" % service
                    retval.append( None )
            return retval
        elif type(item) == type([0,]) or \
             type(item) == type((0,)):
            # list of services
            retval = []
            for service in item:
                retval.append(self.startService(service))
            return retval
        elif self.supportsService(item): # built-in name
            if self.service.has_key(item):
                print "Service is already running: '%s'" % item
                return [self.service[item]]
            console.log(console.INFO,"Loading service '%s'..." % item)
            retval = self.supports[item].startService()
            if self.supports[item].getServiceState() == "started":
                self.service[item] = self.supports[item]
                self.senses[item] = self.service[item]
            else:
                print "service '%s' not available" % item
            return [retval]
        else: # from a file
            file = item
            if file[-3:] != '.py':
                file = file + '.py'
            if system.file_exists(file):
                return self.startService( system.loadINIT(file, self) )
            elif system.file_exists(os.getenv('PYRO') + \
                                    '/plugins/services/' + file): 
                return self.startService( system.loadINIT(os.getenv('PYRO') + \
                                                   '/plugins/services/'+ \
                                                   file, self))
            else:
                print 'Service not found: ' + file
                return []

    def stopService(self, item):
        self.getService(self, item).stopService()

    def supportsService(self, item):
        return self.supports.has_key(item)

    def getService(self, item):
        if self.service.has_key(item):
            return self.service[item]
        else:
            raise AttributeError, "unknown service '%s'" % item

    def getServiceDevice(self, item):
        if self.service.has_key(item):
            return self.service[item].dev
        else:
            raise AttributeError, "unknown service '%s'" % item

    def getServiceData(self, item, *args):
        if self.service.has_key(item):
            return self.service[item].getServiceData(*args)
        else:
            raise AttributeError, "unknown service '%s'" % item

    def getServices(self):
        #return self.service.keys()
        return []

    def getSupportedServices(self):
        return self.supports.keys()

    def hasService(self, item):
        return self.service.has_key(item)

    def removeService(self, item):
        self.service[item].visible = 0
        self.service[item].active = 0
        self.service[item].destroy()
        del self.service[item]

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
