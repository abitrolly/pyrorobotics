from __future__ import generators
import pyrobot.robot
import types, random, exceptions, math
from pyrobot.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

class WindowError(AttributeError):
    """ Device Window Error """

class DeviceError(AttributeError):
    """ Used to signal device problem """

class SensorValue:
    """ Used in new Python range sensor interface """
    def __init__(self, device, value, pos=None,
                 geometry=None, noise=0.0):
        """
        device - an object with rawToUnits, hitX, hitY, hitZ methods
        value - the rawvalue of the device
        pos - the ID of this sensor
        geometry - (origin x, origin y, origin z, th, arc in degrees) of ray
        noise - percentage of noise to add to reading
        """
        self._dev = device
        self.rawValue = self._dev.rawToUnits(value, noise, "RAW") # raw noisy value
        self.value = self.distance() # noisy value in default units
        self.pos = pos
        self.geometry = geometry
        self.noise = noise
    def distance(self, unit=None): # defaults to current unit of device
        # uses raw value; this will change if noise > 0
        return self._dev.rawToUnits(self.rawValue,
                                      0.0,
                                      unit)
    def angle(self, unit="degrees"):
        if self.geometry == None:
            return None
        if unit.lower() == "radians":
            return self.geometry[3] # radians
        elif unit.lower() == "degrees":
            return self.geometry[3] / PIOVER180 # degrees
        else:
            raise AttributeError, "invalid unit = '%s'" % unit
    def position(self):
        if self.geometry == None: return (None, None, None)
        return (self.geometry[0], self.geometry[1], self.geometry[2])
    def hit(self):
        if self.geometry == None: return (None, None, None)
        return (self.hitX(), self.hitY(), self.hitZ())
    def hitX(self):
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.cos(thr) * dist
    def hitY(self):
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.sin(thr) * dist
    def hitZ(self):
        return self.geometry[2]

class Device:
    """ A basic device class """

    def __init__(self, deviceType = 'unspecified', visible = 0):
        self.window = 0
        self.groups = {}
        self.active = 1
        self.visible = visible
        self.type = deviceType
        self.state = "stopped"
        self.title = deviceType
        self.setup()
        if visible:
            self.makeWindow()

    def getSensorValue(self, pos):
        """
        Should be overloaded by device implementations to return a
        SensorValue object.
        """
        return None

    def __iter__(self):
        """ Used to iterate through values of device """
        length = 0
        try: length = len(self)
        except: pass
        for pos in range(length):
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
        elif type(item) == types.TupleType:
            return [self.getSensorValue(p) for p in item]
        elif type(item) == types.IntType:
            return self.getSensorValue(item)
        elif type(item) == types.SliceType:
            step = 1
            if item.step:
                step = item.step
            return [self.getSensorValue(p) for p in xrange(item.start, item.stop, step)]
        else:
            raise AttributeError, "invalid device[%s]" % item

    def setTitle(self, title):
        self.title = title

    def setup(self):
        pass
    
    def getGroupNames(self, pos):
        retval = []
        for key in self.groups:
            if self.groups[key] != None:
                if pos in self.groups[key]:
                    retval.append( key )
        return retval
    def setMaxvalue(self, maxvalue):
        self.maxvalueraw = self.rawToUnits(maxvalue, units="UNRAW")
        return self.maxvalueraw
    def getMaxvalue(self):
        return self.rawToUnits(self.maxvalueraw)
    def rawToUnits(self, raw, noise = 0.0, units=None):
        # what do you want the return value in?
        if units == None:
            units = self.units.upper()
        else:
            units = units.upper()
        # if UNRAW, then you want to do the inverse
        if units == "UNRAW": # go from default to raw
            meters = None
            if self.units.upper() == "ROBOTS":
                meters = raw * self.radius
            elif self.units.upper() == "SCALED":
                return raw * float(self.maxvalueraw)
            elif self.units.upper() == "RAW":
                return raw
            elif (self.units.upper() == "METERS" or
                  self.units.upper() == "METERS"):
                meters = raw
            elif self.units.upper() == "CM":
                meters = raw / 100.0
            elif self.units.upper() == "MM":
                meters = raw / 1000.0
            else:
                raise AttributeError, "can't convert from units"
            # now, have it in meters, want to go to rawunits:
            if (self.rawunits.upper() == "METERS" or
                self.rawunits.upper() == "M"):
                return meters
            elif self.rawunits.upper() == "CM":
                return meters * 100.0
            elif self.rawunits.upper() == "MM":
                return meters * 1000.0
            else:
                raise AttributeError, "can't convert to rawunits"
        # next, add noise, if you want:
        if noise > 0:
            if random.random() > .5:
                raw += (raw * (noise * random.random()))
            else:
                raw -= (raw * (noise * random.random()))
        # keep it in range:
        raw = min(max(raw, 0.0), self.maxvalueraw)
        if units == "RAW":
            return raw
        elif units == "SCALED":
            return raw / float(self.maxvalueraw)
        # else, it is in some metric unit.
        # now, get it into meters:
        if self.rawunits.upper() == "MM":
            if units == "MM":
                return raw 
            else:
                raw = raw / 1000.0
        elif self.rawunits.upper() == "RAW":
            if units == "RAW":
                return raw
            # else going to be problems!
        elif self.rawunits.upper() == "CM":
            if units == "CM":
                return raw
            else:
                raw = raw / 100.0
        elif (self.rawunits.upper() == "METERS" or
              self.rawunits.upper() == "M"):
            if units == "METERS" or units == "M":
                return raw
            # else, no conversion necessary
        else:
            raise AttributeError, "device can't convert '%s' to '%s': use M, CM, MM, ROBOTS, SCALED, or RAW" % (self.rawunits, units)
        # now, it is in meters. convert it to output units:
        if units == "ROBOTS":
            return raw / self.radius # in meters
        elif units == "MM":
            return raw * 1000.0
        elif units == "CM":
            return raw * 100.0 
        elif units == "METERS" or units == "M":
            return raw 
        else:
            raise TypeError, "Units are set to invalid type '%s': use M, CM, MM, ROBOTS, SCALED, or RAW" % units

    def getVisible(self):
        return self.visible
    def setVisible(self, value):
        self.visible = value
        if self.window:
            if value:
                self.window.wm_deiconify()
            else:
                self.window.withdraw()
        return "Ok"
    def getActive(self):
        return self.active
    def setActive(self, value):
        self.active = value
        return "Ok"
    def startDevice(self):
        self.state = "started"
        return self
    def stopDevice(self):
        self.state = "stopped"
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
        return self.state
    def updateDevice(self):
        pass
    def postSet(self, keyword):
        pass
    def preGet(self, pathList):
        pass
