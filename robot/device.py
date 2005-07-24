from __future__ import generators
import pyrobot.robot
import types, random, exceptions, math, Tkinter
from pyrobot.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

class DeviceWindow(Tkinter.Toplevel):
    def __init__(self, device, title = None):
        import pyrobot.system.share as share
        if not share.gui:
            share.gui = Tkinter.Tk()
            share.gui.withdraw()
        Tkinter.Toplevel.__init__(self, share.gui)
        self._dev = device
        self.wm_title(title)
        self.widgets = {}
        if self._dev:
            self._dev.visible = 1
        self._dev.addWidgets(self)
    def update(self):
        pass
    def addButton(self, name, text, command):
        self.widgets[name] = Tkinter.Button(self, text=text, command=command)
        self.widgets[name].pack(fill="both", expand="y")
    def addLabel(self, name, text):
        self.widgets[name] = Tkinter.Label(self, text=text)
        self.widgets[name].pack(fill="both", expand="y")
    def updateWidget(self, name, value):
        self.widgets[name+".entry"].delete(0,'end')
        self.widgets[name+".entry"].insert(0,value)        
    def addData(self, name, text, value):
        frame = Tkinter.Frame(self)
        frame.pack(fill="both", expand="y")
        self.widgets[name + ".label"] = Tkinter.Label(frame, text=text)
        self.widgets[name + ".label"].pack(side="left")
        self.widgets[name + ".entry"] = Tkinter.Entry(frame, bg="white")
        self.widgets[name + ".entry"].insert(0, value)
        self.widgets[name + ".entry"].pack(side="right", fill="both", expand="y")
    def destroy(self):
        if self._dev:
            self._dev.visible = 0
        self.withdraw()

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
    def _hit(self):
        if self.geometry == None: return (None, None, None)
        return (self._hitX(), self._hitY(), self._hitZ())
    def _hitX(self):
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.cos(thr) * dist
    def _hitY(self):
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.sin(thr) * dist
    def _hitZ(self):
        return self.geometry[2]
    hit = property(_hit)

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
    # Properties to make getting all values easy:
    def _getValue(self):
        return [s.value for s in self]
    value = property(_getValue)
    def _getPos(self):
        return [s.pos for s in self]
    pos = property(_getPos)
    def _getGeometry(self):
        return [s.geometry for s in self]
    geometry = property(_getGeometry)
    def _getRawValue(self):
        return [s.rawValue for s in self]
    rawValue = property(_getRawValue)
    def _getHit(self):
        return [s.hit for s in self]
    rawValue = property(_getHit)
    def _getNoise(self):
        return [s.noise for s in self]
    noise = property(_getNoise)
    # Methods to make getting all values easy:
    def distance(self, *args, **kwargs):
        return [s.distance(*args, **kwargs) for s in self]
    def angle(self, *args, **kwargs):
        return [s.angle(*args, **kwargs) for s in self]

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
            if item.stop >= len(self): stop = len(self) - 1
            else:                      stop = item.stop
            step = 1
            if item.step:
                step = item.step
            return [self.getSensorValue(p) for p in xrange(item.start, stop, step)]
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
    def setMaxvalue(self, value):
        self.maxvalueraw = self.rawToUnits(value, units="UNRAW")
        return "Ok"
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
                meters = raw * (self.radius * 2)
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
            return raw / (self.radius * 2) # in meters
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
    # gui methods
    def addWidgets(self, window):
        pass
    def makeWindow(self):
        if self.window:
            self.window.deiconify()
            self.visible = 1
        else:
            self.window = DeviceWindow(self, self.title)
