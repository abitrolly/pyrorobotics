
import types

def serviceDirectoryFormat(serviceDict, retdict = 1):
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
            if keyword == "range":
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
        self.devDataFunc = {}
        self.groups = {}
        self.dev = 0
        self.devData["active"] = 1
        self.devData["visible"] = visible
        self.devData["type"] = serviceType
        self.devData["state"] = "stopped"
        if visible:
            self.makeWindow()
        self.setup()

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

    def _set(self, path, value):
        if path[0] in self.devData:
            self.devData[path[0]] = value
        else:
            raise AttributeError, "invalid item to set: '%s'" % path[0]
                
    def _get(self, path):
        #print "path=", path
        if len(path) == 0:
            # return all of the things a sensor can show
            tmp = self.devData.copy()
            tmp.update( dict([("*" + key + "/", self.groups[key]) for key in self.groups]))
            return serviceDirectoryFormat(tmp, 0)
        elif len(path) == 1 and path[0] in self.devData:
            # return a value
            return self.devData[path[0]]
        # otherwise, dealing with numbers or group
        if len(path) == 1: # no specific data request
            return serviceDirectoryFormat(self.devDataFunc, 0)
        else: # let's get some specific data
            keys = path[0]
            elements = path[1]
            if elements == "*":
                elements = self.devDataFunc.keys() 
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
                return self.devDataFunc[elements](keys)
            # 1 key many elements
            elif type(keys) == type(1):
                mydict = {}
                for e in elements:
                    mydict[e] = self.devDataFunc[e](keys)
                return mydict
            # many keys 1 element
            elif type(elements) == type(""):
                retval = []
                for i in keys:
                    retval.append( self.devDataFunc[elements](i))
                return retval
            # many keys many elements
            else:
                retval = []
                for i in keys:
                    mydict = {}
                    for e in elements:
                        mydict[e] = self.devDataFunc[e](i)
                    retval.append( mydict )
                return retval

