
import types, random

def serviceDirectoryFormat(serviceDict, retdict = 1, showstars = 0):
    """
    Takes a service directory dictionary and makes it presentable for viewing.

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
    for keyword in serviceDict:
        #print keyword, type(serviceDict[keyword])
        if type(serviceDict[keyword]) == types.InstanceType:
            # HACK: to make it so range is an alias link
            if keyword == "range" and showstars:
                keyword = "*" + keyword
            if retdict:
                retval[keyword + "/"] = None
            else:
                retval.append( keyword + "/")
        else:
            if retdict:
                retval[keyword] = serviceDict[keyword]
            else:
                retval.append( keyword )
    return retval

class WindowError(AttributeError):
    """ Service Window Error """

class ServiceError(AttributeError):
    """ Used to signal service problem """

class Service:
    """ A basic service class """

    def __init__(self, serviceType = 'unspecified', visible = 0):
        self.devData = {}
        self.devDataFunc = {} # not currently working
        self.subDataFunc = {}
        self.groups = {}
        self.dev = 0
        self.devData["active"] = 1
        self.devData["visible"] = visible
        self.devData["type"] = serviceType
        self.devData["state"] = "stopped"
        if visible:
            self.makeWindow()
        self.setup()

    def getGroupNames(self, pos):
        retval = []
        for key in self.groups:
            if self.groups[key] != None:
                if pos in self.groups[key]:
                    retval.append( key )
        return retval

    def rawToUnits(self, raw, noise = 0.0):
        # first, get everything into meters:
        if self.devData["rawunits"] == "MM":
            raw = raw / 1000.0
        elif self.devData["rawunits"] == "METERS":
            pass # ok
        else:
            raise AttributeError, "service can't work in rawunits as %s" % self.devData["rawunits"]
        if noise > 0:
            if random.random() > .5:
                raw += (raw * (noise * random.random()))
            else:
                raw -= (raw * (noise * random.random()))
        val = min(max(raw, 0.0), self.devData["maxvalueraw"])
        units = self.devData["units"]
        if units == "ROBOTS":
            return val / self.devData["radius"] 
        elif units == "MM":
            return val * 1000.0
        elif units == "CM":
            return (val) * 100.0 # cm
        elif units == "METERS" or units == "RAW":
            return (val) 
        elif units == "SCALED":
            return val / self.devData["maxvalueraw"]
        else:
            raise TypeError, "Units are set to invalid type"

    def setup(self):
        pass

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

    def startService(self):
        self.devData["state"] = "started"
        return self

    def stopService(self):
        self.devData["state"] = "stopped"
        return "Ok"

    def makeWindow(self):
        raise WindowError, "No Service Window Defined"

    def updateWindow(self):
        raise WindowError, "No Service Window Defined"

    def getServiceData(self):
        return {}

    def getServiceState(self):
        return self.devData["state"]

    def updateService(self):
        pass

    def postSet(self):
        pass

    def preGet(self, keyword):
        pass

    def _set(self, path, value):
        if path[0] in self.devData:
            self.devData[path[0]] = value
            self.postSet()
        else:
            raise AttributeError, "invalid item to set: '%s'" % path[0]
                
    def _get(self, path, showstars = 0):
        #print "path=", path
        self.preGet(path)
        if len(path) == 0:
            # return all of the things a sensor can show
            tmp = self.devData.copy()
            tmp.update( self.devDataFunc )
            if showstars:
                tmp.update( dict([("*" + key + "/", self.groups[key]) for key in self.groups]))
            else:
                tmp.update( dict([(key + "/", self.groups[key]) for key in self.groups]))
            return serviceDirectoryFormat(tmp, 0)
        elif len(path) == 1 and path[0] in self.devData:
            # return a value
            return self.devData[path[0]]
        elif len(path) == 1 and path[0] in self.devDataFunc:
            # return a value/ function with no argument
            return self.devDataFunc[path[0]]()
        # otherwise, dealing with numbers or group
        if len(path) == 1: # no specific data request
            #tmp = self.subData.copy()
            #tmp.update( self.subDataFunc )
            return serviceDirectoryFormat(self.subDataFunc, 0)
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
                return self.subDataFunc[elements](keys)
            # 1 key many elements
            elif type(keys) == type(1):
                mydict = {}
                for e in elements:
                    mydict[e] = self.subDataFunc[e](keys)
                return mydict
            # many keys 1 element
            elif type(elements) == type(""):
                retval = []
                if keys != None:
                    for i in keys:
                        retval.append( self.subDataFunc[elements](i))
                return retval
            # many keys many elements
            else:
                retval = []
                if keys != None:
                    for i in keys:
                        mydict = {}
                        for e in elements:
                            mydict[e] = self.subDataFunc[e](i)
                        retval.append( mydict )
                return retval

