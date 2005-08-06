from __future__ import generators

"""
The device module. All devices (sonar, laser, position, etc) derive
from these.

(c) 2005, PyrobRobotics.org. Licenced under the GNU GPL.
"""

import pyrobot.robot
import types, random, exceptions, math, Tkinter
from pyrobot.geometry import PIOVER180, DEG90RADS, COSDEG90RADS, SINDEG90RADS

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"


class DeviceWindow(Tkinter.Toplevel):
    """
    An object responsible for showing device data.
    """
    def __init__(self, device, title = None):
        """Constructor for the DeviceWindow class."""
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
        """Method called to update a device."""
        pass
    def addButton(self, name, text, command):
        """Adds a button to the device view window."""
        self.widgets[name] = Tkinter.Button(self, text=text, command=command)
        self.widgets[name].pack(fill="both", expand="y")
    def addLabel(self, name, text):
        """Adds a label to the device view window."""
        self.widgets[name] = Tkinter.Label(self, text=text)
        self.widgets[name].pack(fill="both", expand="y")
    def updateWidget(self, name, value):
        """Updates the device view window."""
        try:
            self.widgets[name+".entry"].delete(0,'end')
            self.widgets[name+".entry"].insert(0,value)
        except: pass
    def addData(self, name, text, value):
        """Adds a data field to the device view window."""
        frame = Tkinter.Frame(self)
        frame.pack(fill="both", expand="y")
        try:
            self.widgets[name + ".label"] = Tkinter.Label(frame, text=text)
            self.widgets[name + ".label"].pack(side="left")
            self.widgets[name + ".entry"] = Tkinter.Entry(frame, bg="white")
            self.widgets[name + ".entry"].insert(0, value)
            self.widgets[name + ".entry"].pack(side="right", fill="both", expand="y")
        except: pass
    def destroy(self):
        """Hides the device view window."""
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
        Constructor for the SensorValue object.

        A SensorValue is created for each range device reading.

        >>> robot.sonar[0][3]
        <SensorValue>
        >>> robot.sonar[0][3].value
        2.354
        
        Methods:
           display()    - same as .value, but can change units
           angle()      - same as .geometry[3], but can change units 

        Properties:
           value    - the rawvalue of the device
           pos      - the ID of this sensor
           geometry - (origin x, origin y, origin z, th, arc in radians) of ray
           noise    - percentage of noise to add to reading
           hit      - the (x,y,z) of the position of the hit
        """
        self._dev = device
        self.rawValue = self._dev.rawToUnits(value, noise, "RAW") # raw noisy value
        self.value = self.distance() # noisy value in default units
        self.pos = pos
        self.geometry = geometry
        self.noise = noise
    def distance(self, unit=None): # defaults to current unit of device
        """Method to compute distance to the hit."""
        # uses raw value; this will change if noise > 0
        return self._dev.rawToUnits(self.rawValue,
                                      0.0,
                                      unit)
    def angle(self, unit="degrees"):
        """Method to return the angle. Can change the units of return angle."""
        if self.geometry == None:
            return None
        if unit.lower() == "radians":
            return self.geometry[3] # radians
        elif unit.lower() == "degrees":
            return self.geometry[3] / PIOVER180 # degrees
        else:
            raise AttributeError, "invalid unit = '%s'" % unit
    def _hit(self):
        """Internal get for the .hit property."""
        if self.geometry == None: return (None, None, None)
        return (self._hitX(), self._hitY(), self._hitZ())
    def _hitX(self):
        """Internal get for the .hit property."""
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.cos(thr) * dist
    def _hitY(self):
        """Internal get for the .hit property."""
        thr = self.geometry[3] # theta in radians
        dist = self.distance(unit="M") + self._dev.radius
        return math.sin(thr) * dist
    def _hitZ(self):
        """Internal get for the .hit property."""
        return self.geometry[2]
    hit = property(_hit)

class Device(object):
    """ A basic device class. All devices derive from this."""

    ### Note: Pyro5 will standardize this interface.
    ### 

    def __init__(self, deviceType = 'unspecified', visible = 0):
        """Constructor for the device class."""
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
    def _setDisabled(self, ignore):
        raise AttributeError, "This attribute is read-only"

    def _getValue(self):
        """Internal get for all of the .value properties."""
        return [s.value for s in self]
    value = property(_getValue, _setDisabled)
    def values(self, subset="set"):
        if type(subset) == int:
            return self[subset].value
        else:
            return [s.value for s in self[subset]]
    def _getPos(self):
        """Internal get for all of the .pos properties."""
        return [s.pos for s in self]
    pos = property(_getPos, _setDisabled)
    def poses(self, subset = "pos"):
        if type(subset) == int:
            return self[subset].pos
        else:
            return [s.pos for s in self[subset]]
    def _getGeometry(self):
        """Internal get for all of the .geometry properties."""
        return [s.geometry for s in self]
    geometry = property(_getGeometry, _setDisabled)
    def geometries(self, subset = "all"):
        if type(subset) == int:
            return self[subset].geometry
        else:
            return [s.geometries for s in self[subset]]
    def _getRawValue(self):
        """Internal get for all of the .rawValue properties."""
        return [s.rawValue for s in self]
    rawValue = property(_getRawValue, _setDisabled)
    def rawValues(self, subset = "all"):
        if type(subset) == int:
            return self[subset].rawValue
        else:
            return [s.rawValue for s in self[subset]]
    def _getHit(self):
        """Internal get for all of the .hit properties."""
        return [s.hit for s in self]
    hit = property(_getHit, _setDisabled)
    def hits(self, subset = "all"):
        if type(subset) == int:
            return self[subset].hit
        else:
            return [s.hit for s in self[subset]]
    def _getNoise(self):
        """Internal get for all of the .noise properties."""
        return [s.noise for s in self]
    noise = property(_getNoise, _setDisabled)
    def noises(self, subset = "all"):
        if type(subset) == int:
            return self[subset].noise
        else:
            return [s.noise for s in self[subset]]
    # Methods to make getting all values easy:
    def distance(self, *args, **kwargs):
        """
        Device-level method to get all of the distances.
        
        >>> robot.sonar[0].angle(unit="radians")
        [2.34, 1.34, .545]
        >>> robot.sonar[0]["left"].angle(unit="degrees")
        [90, 45, 180]
        """
        return [s.distance(*args, **kwargs) for s in self]
    def distances(self, subset = "all", *args, **kwargs):
        return [s.distances(*args, **kwargs) for s in self[subset]]
    def angle(self, *args, **kwargs):
        """
        Device-level method to get all of the angles. Can translate units.

        >>> robot.sonar[0][3].angle(unit="radians")
        >>> [s.angle(units="degrees") for s in robot.sonar[0]["left"]]
        """
        return [s.angle(*args, **kwargs) for s in self]
    def angles(self, subset = "all", *args, **kwargs):
        return [s.angle(*args, **kwargs) for s in self[subset]]
    def getSensorValue(self, pos):
        """
        Returns a specific SensorValue from the range device.
        """
        return None
    def __len__(self):
        # devices should overload this method if they are iterable
        return 0

    def __iter__(self):
        """ Used to iterate through SensorValues of device. """
        length = len(self)
        for pos in range(length):
            yield self.getSensorValue(pos)
        raise exceptions.StopIteration

    def __getitem__(self, item):
        """Get a SensorValue, a range, or a set."""
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
        """Sets the title of the device."""
        self.title = title

    def setup(self):
        """Use this to put setup code in (instead of in __init__)."""
        pass
    
    def getGroupNames(self, pos):
        """Return all of the groups a pos is in."""
        retval = []
        for key in self.groups:
            if self.groups[key] != None:
                if pos in self.groups[key]:
                    retval.append( key )
        return retval
    def setMaxvalue(self, value):
        """Set the maxvalue of the sensor."""
        self.maxvalueraw = self.rawToUnits(value, units="UNRAW")
        return "Ok"
    def getMaxvalue(self):
        """Get the maxvalue of the sensor."""
        return self.rawToUnits(self.maxvalueraw)

    def rawToUnits(self, raw, noise = 0.0, units=None):
        """Convert the sensor units into default units."""
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
        """Returns the .visible of the sensor."""
        return self.visible
    def setVisible(self, value):
        """Sets the .visible attribute, and hides/shows window."""
        self.visible = value
        if self.window:
            if value:
                self.window.wm_deiconify()
            else:
                self.window.withdraw()
        return "Ok"
    def getActive(self):
        """Returns the value of .active."""
        return self.active
    def setActive(self, value):
        """Sets the .active property."""
        self.active = value
        return "Ok"
    def startDevice(self):
        """Starts the device (sets the .state)."""
        self.state = "started"
        return self
    def stopDevice(self):
        """Stops the device (sets the .state)."""
        self.state = "stopped"
        return "Ok"
    def destroy(self):
        """Hides the window."""
        if self.window:
            self.window.destroy()
    def getDeviceData(self):
        """Returns the device data, whatever it might be."""
        return {}
    def getDeviceState(self):
        """Returns the .state."""
        return self.state
    def updateDevice(self):
        """Method called to update the device properties."""
        pass
    # gui methods
    def addWidgets(self, window):
        """Method to addWidgets to the device window."""
        self._rangeData = 0
        try:
            len(self)
            self._rangeData = 1
        except: pass
        if self._rangeData:
            for i in range(min(self.count, 24)):
                window.addData(str(i), "[%d]:" % i, self[i].value)
        else:
            for d in self.__dict__:
                if d[0] != "_":
                    window.addData(d, d, self.__dict__[d])
                
    def updateWindow(self):
        """Method to update the device window."""
        if self.visible:
            if self._rangeData:
                for i in range(min(self.count, 24)):
                    self.window.updateWidget(str(i), "%.2f" % self[i].value)
            else:
                for d in self.__dict__:
                    if d[0] != "_":
                        self.window.updateWidget(d, self.__dict__[d])
                
    def makeWindow(self):
        """Method to make and show the device window."""
        if self.window:
            self.window.deiconify()
            self.visible = 1
        else:
            self.window = DeviceWindow(self, self.title)
