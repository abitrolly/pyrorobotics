""" All sensors should derive from here. """

import types

class Sensor:
    """
    Base class for all sensors.
    """
    RAWUNITS = ["MM", "CM", "METERS"]
    UNITS = ["SCALED", "ROBOTS"] + RAWUNITS
    def __init__(self):
        self.units = "ROBOTS"
        self.data = []
        self.namedGroups = {}
        self.robotDiameter = 0.0
        self.maxValue = 0.0 # in raw units
        self.rawUnits = "METERS"
    def setRobotDiameter(self, diam): # in rawUnits
        self.robotDiameter = diam
    def getRobotDiameter(self):       # in rawUnits
        return self.robotDiameter
    def setMaxValue(self, value): # in rawUnits
        self.maxValue = value
    def getMaxValue(self):       # in rawUnits
        return self.maxValue
    def setRawUnits(self, units):
        if units not in Sensor.RAWUNITS:
            raise ValueError
        self.rawUnits = units
    def getRawUnits(self):
        return self.rawUnits
    def setUnits(self, units):
        if units not in Sensor.UNITS:
            raise ValueError
        self.units = units # reporting units
    def getUnits(self):
        return self.units
    def mmToUnits(self, value, units = None):
        if units == None:
            units = self.units
        if units == 'MM':
            return value
        elif units == 'CM':
            return value / 10.0
        elif units == "METERS":
            return value / 1000.0
        elif units == "ROBOTS":
            return value / self.rawToUnits(self.getRobotDiameter(), "MM")
        elif units == "SCALED":
            return value / self.rawToUnits(self.getMaxValue(), "MM")
        else:
            raise TypeError, "'%s' is not a valid unit type" % units
    def metersToUnits(self, value, units = None):
        return self.mmToUnits(value * 1000.0, units)
    def rawToUnits(self, raw, units = None):
        if self.rawUnits == units:
            return float(raw)
        elif self.rawUnits == "METERS":
            return self.metersToUnits(raw, units)
        elif self.rawUnits == "CM":
            return self.mmToUnits(raw/10.0, units)
        elif self.rawUnits == "MM":
            return self.mmToUnits(raw, units)
        else:
            raise TypeError, "'%s' is not a valid unit type" % self.rawUnits
    # --------------------------------------------------
    def getType(self):
        raise NotImplementedError
    def getX(self):
        return 0.0
    def getY(self):
        return 0.0
    def getZ(self):
        return 0.0
    def update(self):
        raise NotImplementedError
    def draw(self, renderer = None, options = {}):
        pass
    def check(self):
        # call those things that can raise and exception:
        self.getType()
        self.update()
    
class RangeSensor(Sensor):
    """
    Base class for all range sensors.
    """
    def __init__(self):
        Sensor.__init__(self)
        self.rangeData = []
    def getCount(self):
        raise NotImplementedError
    def getData(self):
        raise NotImplementedError
    def getDataByPos(self, pos):
        raise NotImplementedError
    def getXHitByPos(self, pos):
        raise NotImplementedError
    def getYHitByPos(self, pos):
        raise NotImplementedError
    def getZHitByPos(self, pos):
        raise NotImplementedError
    def getXOrigByPos(self, pos):
        raise NotImplementedError
    def getYOrigByPos(self, pos):
        raise NotImplementedError
    def getZOrigByPos(self, pos):
        raise NotImplementedError
    def getThetaByPos(self, pos):
        raise NotImplementedError
    def getArcByPos(self, pos):
        raise NotImplementedError

    def check(self):
        Sensor.check(self)
        self.getCount()
        self.getMaxValue()
        self.getUnits()
        self.getData()
        self.getDataByPos(0)
        self.getXHitByPos(0)
        self.getYHitByPos(0)
        self.getZHitByPos(0)
        self.getXOrigByPos(0)
        self.getYOrigByPos(0)
        self.getZOrigByPos(0)
        self.getThetaByPos(0)
        self.getArcByPos(0)


if __name__ == '__main__':

    s = Sensor()
    s.setRobotDiameter(10)
    s.setMaxValue(25)
    print "Robot diameter is", s.robotDiameter
    print "MaxValue is", s.maxValue
    for rawunits in ("METERS", "MM", "CM"):
        s.setRawUnits(rawunits)
        for units in ("METERS", "MM", "CM", "ROBOTS", "SCALED"):
            s.setUnits(units)
            val = 5
            print "raw = ", rawunits, "units = ", units
            print val, rawunits, "is", s.rawToUnits(val), units
            print val, rawunits, "is", s.rawToUnits(val, "METERS"), "METERS"
            print val, rawunits, "is", s.rawToUnits(val, "CM"), "CM"
            print val, rawunits, "is", s.rawToUnits(val, "MM"), "MM"
            print val, rawunits, "is", s.rawToUnits(val, "ROBOTS"), "ROBOTS"
            print val, rawunits, "is", s.rawToUnits(val, "SCALED"), "SCALED"
            print val, "MM", "is", s.mmToUnits(val, "METERS"), "METERS"
            print val, "MM", "is", s.mmToUnits(val, "CM"), "CM"
            print val, "MM", "is", s.mmToUnits(val, "MM"), "MM"
            print val, "MM", "is", s.mmToUnits(val, "ROBOTS"), "ROBOTS"
            print val, "MM", "is", s.mmToUnits(val, "SCALED"), "SCALED"
            print "==========================================="
    #s.check()
