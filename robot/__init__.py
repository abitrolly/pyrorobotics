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
# .act()             - interface to motion, actions


import pyro.gui.console as console
from pyro.gui.drawable import *
from pyro.geometry.Vector import *
from pyro.geometry.Polar import *
import time
from pyro.brain.behaviors.core import distance
from math import pi

# Units of measure for sense, map, and motors:
# -------------------------------------------
# ROBOTS - unit is given interms of robot's diameter
# METERS - meters
# CM     - centimeters
# MM     - millimeters
# SCALED - scaled [-1,1]
# RAW    - right from the sensor

class Robot (Drawable):
    """
    this be the one.
    """
    def __init__(self, name = None, type = None, **kwargs):
        """
        if you extend Robot please call this function!
        If you need to initialize things, call setup()
        """
        Drawable.__init__(self, name)
        console.log(console.INFO,'Creating Robot');
        #self.data = name
        self.name = name
        self.type = type
        self.sensorGroups = {}
        self.drivers = [] # something that implements the driver interface
        self.senses  = {} # (name,type,driver,AffineVector(),reading)
        self.controls = {} # (name,type,driver,control value)
        self.service = {}
        self.supports = {}
        self.map = []
        # user init:
        self.setup(**kwargs)

    def __repr__(self):
        return "Robot name = '%s', type = '%s'" % (self.name, self.type)

    def disconnect(self):
        console.log(console.WARNING, "need to override DISCONNECT in robot")

    def localize(self, x = 0, y = 0, th = 0):
        console.log(console.WARNING, "need to override LOCALIZE in robot")

    def load_drivers(self): # call this after init!
        self.loadDrivers()
        self.loadSenses()
        self.loadControllers()
        self.SanityCheck()

    def inform(self, msg):
        # queue it up
        console.log(console.INFO, msg)
        
    def loadDrivers(self):
        """
        This is an 'abstract' function ment for child classes to overide.
        It should load the drivers that a particular robot uses.
        """
        console.log(console.ERROR,"Someone needs to implement loadDrivers in their robot extension class!");
    
    def loadSenses(self):
        """
        this is a helper function for __init__that loads the senses from
        the drivers.
        """
        for driver in self.drivers:
            sd = driver.getSenses()
            for key in sd.keys():
                console.log(console.INFO,'Adding sensor "'+key+'" from driver '+driver.__class__.__name__)
                self.senses[key] = sd[key]

    def loadControllers(self):
        """
        this is a helper function for __init__that loads the senses from
        the drivers.
        """
        for driver in self.drivers:
            cd = driver.getControls()
            for key in cd.keys():
                console.log(console.INFO,'Adding control "'+key+'" from driver '+driver.__class__.__name__)
                self.controls[key] = cd[key]
                
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
            finalPath.append(self.condense( part ) )
        # todo: store these functions in part of self
        return self.senses[finalPath[0]].get(self.dev, finalPath[1:])

    def condense(self, part):
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
                        
                    
        #if type(pos) == type("") and pos.isdigit():
        #    pos = int(pos)
                
                
                
	#if (data == None): # never used
        #    return self.senses[device]
        #elif (type(data) == type(1)): # never used
        #    return self.senses[device]['value'](self.dev, data)
	#elif (pos == None): # never used
        #    return self.senses[device][data](self.dev)
	#elif (pos == 'function'): # never used
        #    return self.senses[device][data]
	#elif type(pos) == type(1): # number
        #    return self.senses[device][data](self.dev, pos)
        #elif type(pos) == type([1,2]) or type(pos) == type((1,2)): # collection
        #    list = []
        #    for i in pos:
        #        list.append( self.senses[device][data](self.dev, i) )
        #    return self.applyFunc(device, pos, list, func)
        #elif type(pos) == type("name"): # sensor set
        #    list = []
        #    for i in self.sensorSet[pos]:
        #        list.append(self.senses[device][data](self.dev, i))
        #    return self.applyFunc(device, self.sensorSet[pos], list, func)
        #else:
        #    print "Error: pos is wrong type!"
        #    return None

    def applyFunc(self, sensor, poslist, list, func):
        if func == None:
            return list
        elif func == 'minval':
            pos = -1
            posval = 10000
            for i in range(len(list)):
                if list[i] < posval:
                    pos = poslist[i]
                    posval = list[i]
            return posval
        elif func == 'min':
            pos = -1
            posval = 10000
            for i in range(len(list)):
                if list[i] < posval:
                    pos = poslist[i]
                    posval = list[i]
            return (pos, posval)
        elif func == 'max':
            pos = -1
            posval = -10000
            for i in range(len(list)):
                if list[i] > posval:
                    pos = poslist[i]
                    posval = list[i]
            return (pos, posval)        
        elif func == 'maxval':
            pos = -1
            posval = -10000
            for i in range(len(list)):
                if list[i] > posval:
                    pos = poslist[i]
                    posval = list[i]
            return posval
        elif func == 'sum':
            sum = 0
            for i in list:
                sum += i
            return sum 
        elif func == 'close':
            dist = 10000
            angle = 0
            for i in range(len(list)):
                if list[i] < dist:
                    dist = list[i]
                    angle = self.senses[sensor]['th'](self.dev, poslist[i])
            return (dist, angle)
        elif func == 'far':
            dist = -10000
            angle = 0
            for i in range(len(list)):
                if list[i] > dist:
                    dist = list[i]
                    angle = self.senses[sensor]['th'](self.dev, poslist[i])
            return (dist, angle)
        elif func == 'avg':
            dist = 0
            for i in list:
                dist += i
            return dist / len(list)
        else:
            print "ERROR: unknown function '%s'" % func
            
    def set(self, device = 'robot', data = None, val = None):
	"""
        A method to set the above get.
	"""
	if (data == None):
            raise AttributeError, "Need value to set"
	elif (val == None):
            # this probably doesn't make sense:
            self.senses[device] = data # dictionary?
	else:
            # make it a function:
            self.senses[device][data] = lambda self, x = val: x

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

    def accelerate(self, translate, rotate):
        self.act('accelerate', translate, rotate)

    def motors(self, leftValue, rightValue):
        """
        Move function that takes desired motor values
        and converts to trans and rotate.
        """
        trans = (rightValue + leftValue) / 2.0
        rotate = (rightValue - leftValue) / 2.0
        self.move(trans, rotate)
        
    def move(self, translate, rotate):
        self.act('move', translate, rotate)

    def move_now(self, translate, rotate):
        self.act('move_now', translate, rotate)

    def stop(self):
        self.act('move', 0, 0)

    def translate(self, val):
        self.act('translate', val)

    def rotate(self, val):
        self.act('rotate', val)

    def getAngleToAngle(self, phi): # phi is in radians
        '''
        Given an angle in radians (0 front, to left to PI), what is the
        shortest way to turn there?  returns -PI to PI, neg to right,
        to use with turning
        '''
        theta = self.senses['robot']['thr'](self.dev)
        if (phi > theta):  # turn left
            phi = phi - theta;
        else: # // turn right
            phi = (theta - phi) * -1.0;
        if (phi > pi): # // oops, shorter to turn other direction
            phi = (2 * pi - phi) * -1.0;
        if (phi < -pi): #// oops, shorter to turn other direction
            phi = (2 * pi + phi);
        return phi

    def getAngleToPoint(self, x, y):
        return self.getAngleToPoints(x, y, \
                                     self.senses['robot']['x'](self.dev), \
                                     self.senses['robot']['y'](self.dev))
                                     
    def getAngleToPoints(self, x1, y1, x2, y2):
        p = Polar()
        p.setCartesian(x1 - x2, y1 - y2) # range pi to -pi
        if (p.t < 0.0):
            phi = p.t + 2 * pi # 0 to pi to left; 0 to -pi to right
        else:
            phi = p.t;
        return self.getAngleToAngle(phi)

    def getDistanceToPoint(self, x, y):
        return distance(x, y, \
                        self.senses['robot']['x'](self.dev), \
                        self.senses['robot']['y'](self.dev))

    def getObstacle(self, angle):
        # angle
        pass

    def act(self, action = None, value1 = None, value2 = None, val3 = None):
	"""
	this is designed to be the main interface to having the robot
	move. this is currently hotwired for forward/turn only
	"""
	if (action == None):
		return self.controls 
	elif (value1 == None):
		return self.controls[action]
	elif (value2 == None):
		self.controls[action](self.dev, value1)
	elif (val3 == None):
		self.controls[action](self.dev, value1, value2)
	else:
		self.controls[action](self.dev, value1, value2, val3)
        self.needToRedraw = 1

    def _update(self):
        for service in self.getServices():
            if self.getService(service).active:
                self.getService(service).updateService()

    def update(self):
        """
        This is a common control that isn't an act, so we pull it out
        here.
        """
        self.controls['update'](self.dev) # this should call _update

    def SanityCheck(self):
	if (not self.senses.has_key('robot')):
	        console.log(console.FATAL,'sense has NO robot')
	if (not self.controls.has_key('move')):
	        console.log(console.FATAL,'control has NO move')
	if (not self.controls.has_key('translate')):
	        console.log(console.FATAL,'control has NO translate')
	if (not self.controls.has_key('rotate')):
	        console.log(console.FATAL,'control has NO rotate')
	if (not self.controls.has_key('update')):
	        console.log(console.FATAL,'control has NO update')
        console.log(console.INFO,'robot sanity check completed')

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
        return self.service.keys()

    def getSupportedServices(self):
        return self.supports.keys()

    def hasService(self, item):
        return self.service.has_key(item)

    def removeService(self, item):
        self.service[item].visible = 0
        self.service[item].active = 0
        self.service[item].destroy()
        del self.service[item]

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

    def enableMotors(self):
        pass

    def disableMotors(self):
        pass
