""" All sensors should derive from here. """

class Sensor:
    """
    Base class for all sensors.
    """
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
        self.rawUnits = units
    def getRawUnits(self):
        return self.rawUnits
    def setUnits(self, units):
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
        pass
    def getX(self):
        pass
    def getY(self):
        pass
    def getZ(self):
        return 0.0
    def update(self):
        pass
    def draw(self, renderer = None, options = {}):
        pass
        
    
class RangeSensor(Sensor):
    """
    Base class for all range sensors.
    """
    def __init__(self):
        Sensor.__init__(self)

    def getCount(self):
        pass
    def getMaxValue(self):
        pass
    def getUnits(self):
        pass
    def getData(self):
        pass
    def getDataByPos(self, pos):
        pass
    
    def getXHitByPos(self, pos):
        pass
    def getYHitByPos(self, pos):
        pass
    def getZHitByPos(self, pos):
        pass
    
    def getXOrigByPos(self, pos):
        pass
    def getYOrigByPos(self, pos):
        pass
    def getZOrigByPos(self, pos):
        pass

    def getThetaByPos(self, pos):
        pass
    def getArcByPos(self, pos):
        pass

if __name__ == '__main__':

    s = Sensor()
    s.setRobotDiameter(34)
    s.setMaxValue(50)
    for rawunits in ("METERS", "MM", "CM"):
        s.setRawUnits(rawunits)
        for units in ("METERS", "MM", "CM", "ROBOTS", "SCALED"):
            s.setUnits(units)
            print "raw", rawunits, "units", units
            print 12, rawunits, "is", s.rawToUnits(12), units
            print 12, rawunits, "is", s.rawToUnits(12, "METERS"), "METERS"
            print 12, rawunits, "is", s.rawToUnits(12, "CM"), "CM"
            print 12, rawunits, "is", s.rawToUnits(12, "MM"), "MM"
            print 12, rawunits, "is", s.rawToUnits(12, "ROBOTS"), "ROBOTS"
            print 12, rawunits, "is", s.rawToUnits(12, "SCALED"), "SCALED"
            print 12, "MM", "is", s.mmToUnits(12, "METERS"), "METERS"
            print 12, "MM", "is", s.mmToUnits(12, "CM"), "CM"
            print 12, "MM", "is", s.mmToUnits(12, "MM"), "MM"
            print 12, "MM", "is", s.mmToUnits(12, "ROBOTS"), "ROBOTS"
            print 12, "MM", "is", s.mmToUnits(12, "SCALED"), "SCALED"
            print "==========================================="
