import pyro.robot
import types, random, exceptions
from pyro.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

def deviceDirectoryFormat(deviceDict, retdict = 1, showstars = 0): 
    """
    Takes a device directory dictionary and makes it presentable for viewing.

    Also takes a flag to indicate if it should return a dictionary (for * listings)
    or a list (for regular directory content listing).
    
    The function does two things:
      1. adds a trailing slash to those entries that point to more things
      2. replaces the objects that they point to with None, when returning a dictionary
    """
    if retdict:
        retval = {}
    else:
        retval = []
    for keyword in deviceDict:
        if keyword[0] == ".": # hidden properties
            continue
        #print keyword, type(deviceDict[keyword])
        # if this is an instance, then don't follow
        below = issubclass(deviceDict[keyword].__class__, pyro.robot.Robot) \
                or issubclass(deviceDict[keyword].__class__, pyro.robot.DeviceWrapper) \
                or issubclass(deviceDict[keyword].__class__, Device)
        #print "THINGS BELOW?:", keyword, below
        if below:
            if issubclass(deviceDict[keyword].__class__, Device) and showstars:
                keyword = "*" + keyword
            if retdict:
                retval[keyword + "/"] = None
            else:
                retval.append( keyword + "/")
        else:
            if retdict:
                retval[keyword] = deviceDict[keyword]
            else:
                retval.append( keyword )
    if isinstance(retval, (type((1,)), type([1,]))):
        retval.sort()
    return retval

class WindowError(AttributeError):
    """ Device Window Error """

class DeviceError(AttributeError):
    """ Used to signal device problem """

class DeviceGetError(AttributeError):
    """ Used to signal device get problem: item is not getable """

class DeviceSetError(AttributeError):
    """ Used to signal device set problem: item is not setable """

class SensorValue:
    """ Used in new Python range sensor interface """
    def __init__(self, device, value, pos=None,
                 geometry=None, noise=0.0):
        """
        device - an object with rawToUnits, hitX, hitY, hitZ methods
        value - the rawvalue of the device
        pos - the ID of this sensor
        geometry - (origin x, origin y, origin z, th in degrees) of ray
        noise - percentage of noise to add to reading
        """
        self.device = device
        self.value = value
        self.pos = pos
        self.geometry = geometry
        self.noise = noise
    def distance(self, unit=None): # defaults to current unit of device
        return self.device.rawToUnits(self.value,
                                      self.noise,
                                      unit)        
    def angle(self, unit="degrees"):
        if self.geometry == None:
            return None
        if unit.lower() == "radians":
            return self.geometry[3] * PIOVER180 # radians
        elif unit.lower() == "degrees":
            return self.geometry[3]
        else:
            raise AttributeError, "invalid unit = '%s'" % unit
    def position(self):
        if self.geometry == None: return (None, None, None)
        x = self.geometry[0]
        y = self.geometry[1]
        z = self.geometry[2] 
        return (x, y, z)
    def hit(self):
        x = self.device.hitX(self.pos)
        y = self.device.hitY(self.pos)
	z = self.device.hitZ(self.pos) 
        return (x, y, z)

class Device:
    """ A basic device class """

    def __init__(self, deviceType = 'unspecified', visible = 0):
        self.devData = {}
        self.window = 0
        self.devDataFunc = {} # not currently working
        self.subDataFunc = {}
        self.groups = {}
        self.printFormat = {}
        # things in this list can NOT be set() by user:
        self.notSetables    = ['x','y','z','th','thr','model','type','subtype','rawunits','count','maxvalue','ox','oy','oz',".state",".help"] 
        # things in this list can NOT be be get() by user:
        self.notGetables = ["command"]
        #self.notGetables = [] 
        self.dev = 0
        self.devData[".active"] = 1
        self.devData[".visible"] = visible
        self.devData["type"] = deviceType
        self.devData[".state"] = "stopped"
        #self.devData["object"] = self
        if visible:
            self.makeWindow()
        self.setup()

    def getSensorValue(self, pos):
        """
        Should be overloaded by device implementations to return a
        SensorValue object.
        """
        return None

    def __iter__(self):
        """ Used to iterate through values of device """
        for pos in range(len(self)):
            yield self.getSensorValue(pos)
        raise exceptions.StopIteration

    def __getitem__(self, item):
        if type(item) == types.StringType:
            if "groups" in self.__dict__ and item in self.__dict__["groups"]:
                positions = self.__dict__["groups"][item]
                retval = []
                for p in positions:
                    retval.append( self.getSensorValue(p) )
                return retval
            else: # got a string, but it isn't a group name
                raise AttributeError, "invalid device groupname '%s'" % item
        elif type(item) == types.IntType:
            return self.getSensorValue(item)
        elif type(item) == types.SliceType:
            retval = []
            step = 1
            if item.step:
                step = item.step
            for p in range(item.start, item.stop, step):
                retval.append( self.getSensorValue(p) )
            return retval
        else:
            raise AttributeError, "invalid device[%s]" % item

    def __getattr__(self, attr):
        """ Overides default get attribute to return devData if exists """
        if attr in self.devData:
            return self.devData[attr]
        elif attr in self.__dict__:
            return self.__dict__[attr]
        elif "groups" in self.__dict__ and attr in self.__dict__["groups"]:
            return self.__dict__["groups"][attr]
        else:
            raise AttributeError, ("'<type %s>' object has no attribute '%s'" % (self.__class__.__name__, attr))

    def setTitle(self, title):
        pass

    def setup(self):
        pass
    
    def getGroupNames(self, pos):
        retval = []
        for key in self.groups:
            if self.groups[key] != None:
                if pos in self.groups[key]:
                    retval.append( key )
        return retval

    def rawToUnits(self, raw, noise = 0.0, units=None):
        if units == None:
            units = self.devData["units"].upper()
        else:
            units = units.upper()
        # first, add noise, if you want:
        if noise > 0:
            if random.random() > .5:
                raw += (raw * (noise * random.random()))
            else:
                raw -= (raw * (noise * random.random()))
        # keep it in range:
        raw = min(max(raw, 0.0), self.devData["maxvalueraw"])
        if units == "RAW":
            return raw
        elif units == "SCALED":
            return raw / self.devData["maxvalueraw"]
        # else, it is in some metric unit.
        # now, get it into meters:
        if self.devData["rawunits"].upper() == "MM":
            if units == "MM":
                return raw
            else:
                raw = raw / 1000.0
        elif self.devData["rawunits"].upper() == "RAW":
            if units == "RAW":
                return raw
            # else going to be problems!
        elif self.devData["rawunits"].upper() == "CM":
            if units == "CM":
                return raw
            else:
                raw = raw / 100.0
        elif self.devData["rawunits"].upper() == "METERS":
            if units == "METERS":
                return raw
            # else, no conversion necessary
        else:
            raise AttributeError, "device can't convert '%s' to '%s'" % (self.devData["rawunits"], units)
        # now, it is in meters. convert it to output units:
        if units == "ROBOTS":
            return raw / self.devData["radius"] # in meters
        elif units == "MM":
            return raw * 1000.0
        elif units == "CM":
            return raw * 100.0 
        elif units == "METERS":
            return raw 
        else:
            raise TypeError, "Units are set to invalid type '%s'" % units

    def getVisible(self):
        return self.devData[".visible"]
    def setVisible(self, value):
        self.devData[".visible"] = value
        if self.window:
            if value:
                self.window.wm_deiconify()
            else:
                self.window.withdraw()
        return "Ok"
    def getActive(self):
        return self.devData[".active"]
    def setActive(self, value):
        self.devData[".active"] = value
        return "Ok"
    def startDevice(self):
        self.devData[".state"] = "started"
        return self
    def stopDevice(self):
        self.devData[".state"] = "stopped"
        return "Ok"
    def makeWindow(self):
        pass
    def destroy(self):
        if self.window:
            self.window.destroy()
    def updateWindow(self):
        pass
    def getDeviceData(self):
        return {}
    def getDeviceState(self):
        return self.devData[".state"]
    def updateDevice(self):
        pass
    def postSet(self, keyword):
        pass
    def preGet(self, pathList):
        pass
    def _set(self, path, value):
        if len(path) == 1 and path[0] in self.devData:
            if path[0] in self.notSetables:
                raise DeviceSetError, ("%s is not setable" % path[0])
            self.devData[path[0]] = value
            self.postSet(path[0])
        else:
            raise AttributeError, "invalid item to set: '%s'" % path
                
    def _get(self, path, showstars = 0):
        if len(path) == 0:
            # return all of the things a sensor can get
            tmp = self.devData.copy()
            tmp.update( self.devDataFunc )
            if showstars:
                tmp.update( dict([("*" + key + "/", self.groups[key]) for key in self.groups]))
            else:
                tmp.update( dict([(key + "/", self.groups[key]) for key in self.groups]))
            return deviceDirectoryFormat(tmp, 0)
        elif len(path) == 1 and path[0] == "object":
            return self
        elif len(path) == 1 and path[0] in self.devData:
            # return a value
            #print "HERE", path[0], showstars
            if showstars and path[0] in self.printFormat:
                #print "RETURNING", self.printFormat[path[0]]
                return self.printFormat[path[0]]
            else:
                #print "RETURNING real thing",
                if path[0] in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % path[0])
                self.preGet(path[0])
                return self.devData[path[0]]
        elif len(path) == 1 and path[0] in self.devDataFunc:
            if showstars and path[0] in self.printFormat:
                return self.printFormat[path[0]]
            else:
                # return a value/ function with no argument
                if path[0] in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % path[0])
                self.preGet(path[0])
                return self.devDataFunc[path[0]]()
        # otherwise, dealing with numbers or group
        if len(path) == 1: # no specific data request
            #tmp = self.subData.copy()
            #tmp.update( self.subDataFunc )
            if type(path[0]) == type(1) and len(self.subDataFunc) > 0:
                return deviceDirectoryFormat(self.subDataFunc, 0)
            else:
                if path[0] in self.groups:
                    return deviceDirectoryFormat(self.subDataFunc, 0)
                else:
                    raise AttributeError, "no such item: '%s'" % path[0]
        else: # let's get some specific data
            keys = path[0]
            elements = path[1]
            if elements == "*":
                elements = self.subDataFunc.keys() #+ self.subData.keys()
            # if keys is a collection:
            #print "keys=", keys, "elements=", elements
            if isinstance(keys, (type((1,)), type([1,]))):
                keyList, keys = keys, []
                for k in keyList:
                    if k in self.groups.keys():
                        keys.extend( self.groups[k] )
                    else:
                        keys.append( k )
            elif keys in self.groups.keys():
                # single keyword, so just replace keys with the numeric values
                keys = self.groups[keys]
            # 4 cases:
            # 1 key 1 element
            if type(keys) == type(1) and type(elements) == type(""):
                #print "CASE 2"
                if elements in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % elements)
                self.preGet(elements) 
                return self.subDataFunc[elements](keys)
            # 1 key many elements
            elif type(keys) == type(1):
                #print "CASE 3"
                if elements in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % elements)
                self.preGet(elements)
                mydict = {}
                for e in elements:
                    mydict[e] = self.subDataFunc[e](keys)
                return mydict
            # many keys 1 element
            elif type(elements) == type(""):
                #print "CASE 4", elements
                if elements not in self.subDataFunc:
                    raise AttributeError, "no such item: '%s'" % elements
                if elements in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % elements)
                self.preGet(elements)
                retval = []
                if keys != None:
                    for i in keys:
                        retval.append( self.subDataFunc[elements](i))
                return retval
            # many keys many elements
            else:
                #print "CASE 5", elements, keys
                #if type(elements) == type(1):
                #    return keys
                if elements in self.notGetables:
                    raise DeviceGetError, ("%s is not viewable" % elements)
                self.preGet(elements)
                retval = []
                if keys != None:
                    for i in keys:
                        mydict = {}
                        for e in elements:
                            mydict[e] = self.subDataFunc[e](i)
                        retval.append( mydict )
                return retval

