
import types, random

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
        #print keyword, type(deviceDict[keyword])
        if type(deviceDict[keyword]) == types.InstanceType:
            # HACK: to make it so range is an alias link
            if keyword == "range" and showstars:
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
    #if isinstance(retval, (type((1,)), type([1,]))):
    #    retval.sort()
    return retval

class WindowError(AttributeError):
    """ Device Window Error """

class DeviceError(AttributeError):
    """ Used to signal device problem """

class Device:
    """ A basic device class """

    def __init__(self, deviceType = 'unspecified', visible = 0):
        self.devData = {}
        self.devDataFunc = {} # not currently working
        self.subDataFunc = {}
        self.groups = {}
        self.printFormat = {}
        self.dev = 0
        self.devData["active"] = 1
        self.devData["visible"] = visible
        self.devData["type"] = deviceType
        self.devData["state"] = "stopped"
        #self.devData["object"] = self
        if visible:
            self.makeWindow()
        self.setup()

    def setup(self):
        pass
    
    def getGroupNames(self, pos):
        retval = []
        for key in self.groups:
            if self.groups[key] != None:
                if pos in self.groups[key]:
                    retval.append( key )
        return retval

    def rawToUnits(self, raw, noise = 0.0):
        # first, add noise, if you want:
        units = self.devData["units"]
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
        if self.devData["rawunits"] == "MM":
            if units == "MM":
                return raw
            else:
                raw = raw / 1000.0
        elif self.devData["rawunits"] == "RAW":
            if units == "RAW":
                return raw
            # else going to be problems!
        elif self.devData["rawunits"] == "CM":
            if units == "CM":
                return raw
            else:
                raw = raw / 100.0
        elif self.devData["rawunits"] == "METERS":
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
        return self.devData["visible"]
    def setVisible(self, value):
        self.devData["visible"] = value
        return "Ok"
    def getActive(self):
        return self.devData["active"]
    def setActive(self, value):
        self.devData["active"] = value
        return "Ok"
    def startDevice(self):
        self.devData["state"] = "started"
        return self
    def stopDevice(self):
        self.devData["state"] = "stopped"
        return "Ok"
    def makeWindow(self):
        pass
    def updateWindow(self):
        pass
    def getDeviceData(self):
        return {}
    def getDeviceState(self):
        return self.devData["state"]
    def updateDevice(self):
        pass
    def postSet(self, keyword):
        pass
    def preGet(self, pathList):
        pass
    def _set(self, path, value):
        if path[0] in self.devData:
            self.devData[path[0]] = value
            self.postSet(path[0])
        else:
            raise AttributeError, "invalid item to set: '%s'" % path[0]
                
    def _get(self, path, showstars = 0):
        #print "path=", path
        if len(path) == 0:
            # return all of the things a sensor can show
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
            if showstars and path[0] in self.printFormat:
                return self.printFormat[path[0]]
            else:
                self.preGet(path[0])
                return self.devData[path[0]]
        elif len(path) == 1 and path[0] in self.devDataFunc:
            if showstars and path[0] in self.printFormat:
                return self.printFormat[path[0]]
            else:
                # return a value/ function with no argument
                self.preGet(path[0])
                return self.devDataFunc[path[0]]()
        # otherwise, dealing with numbers or group
        if len(path) == 1: # no specific data request
            #tmp = self.subData.copy()
            #tmp.update( self.subDataFunc )
            return deviceDirectoryFormat(self.subDataFunc, 0)
        else: # let's get some specific data
            keys = path[0]
            elements = path[1]
            if elements == "*":
                elements = self.subDataFunc.keys() #+ self.subData.keys()
            # if keys is a collection:
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
                self.preGet(elements) 
                return self.subDataFunc[elements](keys)
            # 1 key many elements
            elif type(keys) == type(1):
                self.preGet(elements)
                mydict = {}
                for e in elements:
                    mydict[e] = self.subDataFunc[e](keys)
                return mydict
            # many keys 1 element
            elif type(elements) == type(""):
                self.preGet(elements)
                retval = []
                if keys != None:
                    for i in keys:
                        retval.append( self.subDataFunc[elements](i))
                return retval
            # many keys many elements
            else:
                self.preGet(elements)
                retval = []
                if keys != None:
                    for i in keys:
                        mydict = {}
                        for e in elements:
                            mydict[e] = self.subDataFunc[e](i)
                        retval.append( mydict )
                return retval

