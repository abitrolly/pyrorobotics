# Defines B21RRobot, a subclass of robot

from pyro.robot import *
import pyro.gui.console as console
import pyro.robot.driver.b21r.lowlevel as lowlevel
import string
import array
import math
import termios
from time import sleep

PIOVER180 = pi / 180.0
DEG90RADS = 0.5 * pi
COSDEG90RADS = math.cos(DEG90RADS) / 1000.0
SINDEG90RADS = math.sin(DEG90RADS) / 1000.0

class B21RRobot(Robot):
    def __init__(self, name = None, simulator = 0): # 0 makes it real
        Robot.__init__(self, name, "b21r") # robot constructor
        self.inform("Loading B21R robot interface...")
        self.dev = lowlevel.b21r()
        self.stallHistoryPos = 0
        self.stallHistorySize = 5
        self.stallHistory = [0] * self.stallHistorySize
        self.sensorSet = {'all': range(180),
                          'front' : range(45, 135), 
                          'front-left' : range(115, 165), 
                          'front-right' :range (15,65),
                          'front-all' : range(45, 135),
                          'left' : range(135,180),
                          'right' : range(0,45), 
                          'back-left' : (), 
                          'back-right' : (), 
                          'back-all' : (), 
                          'back' : ()} 
        self.senseData = {}
        self.lastTranslate = 0
        self.lastRotate = 0
        self.currSpeed = [0, 0]

	# robot senses (all are functions):
        self.senses['robot'] = {}
        self.senses['robot']['simulator'] = lambda self, x = simulator: x
        self.senses['robot']['stall'] = self.isStall
        self.senses['robot']['x'] = self.getX
        self.senses['robot']['y'] = self.getY
        self.senses['robot']['z'] = self.getZ
        self.senses['robot']['radius'] = lambda self: .6 # in UNITS
        self.senses['robot']['th'] = self.getTh # in degrees
        self.senses['robot']['thr'] = self.getThr # in radians
	self.senses['robot']['type'] = lambda self: 'b21r'
        self.senses['robot']['units'] = lambda self: 'METERS'

	self.senses['robot']['name'] = lambda self, x = name: x

	self.senses['sonar'] = {}
	self.senses['sonar']['count'] = lambda self: 16
	self.senses['sonar']['type'] = lambda self: 'range'

	# location of sensors' hits:
	self.senses['sonar']['x'] = self.getSonarXCoord
	self.senses['sonar']['y'] = self.getSonarYCoord
	self.senses['sonar']['z'] = lambda self, pos: 0.03
	self.senses['sonar']['value'] = self.getSonarRange
        self.senses['sonar']['all'] = self.getSonarRangeAll
        self.senses['sonar']['maxvalue'] = self.getSonarMaxRange
	self.senses['sonar']['flag'] = self.getSonarFlag
        self.senses['sonar']['units'] = lambda self: "ROBOTS"

	# location of origin of sensors:
        self.senses['sonar']['ox'] = self.sonar_ox
	self.senses['sonar']['oy'] = self.sonar_oy
	self.senses['sonar']['oz'] = lambda self, pos: 0.03 # meters
	self.senses['sonar']['th'] = self.sonar_th
        # in radians:
        self.senses['sonar']['arc'] = lambda self, pos, \
                                      x = (15 * math.pi / 180) : x

	self.senses['laser'] = {}
	self.senses['laser']['count'] = lambda self: 180
	self.senses['laser']['type'] = lambda self: 'range'
        self.senses['laser']['maxvalue'] = self.getLaserMaxRange
        self.senses['laser']['units'] = lambda self: "ROBOTS"
        self.senses['laser']['all'] =   self.getLaserRangeAll

        # location of sensors' hits:
        self.senses['laser']['x'] = self.getLaserXCoord
	self.senses['laser']['y'] = self.getLaserYCoord
	self.senses['laser']['z'] = lambda self, pos: 0.03
	self.senses['laser']['value'] = self.getLaserRange
	self.senses['laser']['flag'] = self.getLaserFlag

	# location of origin of sensors:
        self.senses['laser']['ox'] = self.laser_ox
	self.senses['laser']['oy'] = self.laser_oy
	self.senses['laser']['oz'] = lambda self, pos: 0.03 # meters
	self.senses['laser']['th'] = self.laser_th
        # in radians:
        self.senses['laser']['arc'] = lambda self, pos : 1

        self.senses['self'] = self.senses['robot']
        self.senses['range'] = self.senses['laser']

        console.log(console.INFO,'b21r sense drivers loaded')

        self.controls['move'] = self._moveDev
        self.controls['accelerate'] = self.accelerate
        self.controls['translate'] = self.translate
        self.controls['rotate'] = self.rotate
        self.controls['update'] = self.update 
        self.controls['localize'] = self.localize

	self.translateFactor = 1.0
	self.rotateFactor = 1.0

        console.log(console.INFO,'b21r control drivers loaded')
        self.SanityCheck()
        self.x = 0.0
        self.y = 0.0
        self.thr = 0.0
        self.th = 0.0
	self.update() 
        self.inform("Done loading robot.")

    def getLaserXCoord(self, dev, pos):
	pass
    def getLaserYCoord(self, dev, pos):
	pass
    def getLaserFlag(self, dev):
	pass
    def laser_ox(self, pos):
	pass
    def laser_oy(self, pos):
	pass

    def getSonarXCoord(self, dev, pos):
        # convert to x,y relative to robot
        dist = self.rawToUnits(dev, self.senseData['sonar'][pos], 'sonar', 'METERS')
        angle = (-self.sonar_thd(dev, pos)  - 90.0) / 180.0 * math.pi
        return dist * math.cos(angle)

    def getSonarYCoord(self, dev, pos):
        # convert to x,y relative to robot
        dist = self.rawToUnits(dev, self.senseData['sonar'][pos], 'sonar', 'METERS')
        angle = (-self.sonar_thd(dev, pos) - 90.0) / 180.0 * math.pi
        return dist * math.sin(angle)
    
    def sonar_ox(self, dev, pos):
        # in mm
        if pos == 0:
            retval = 10.0
        elif pos == 1:
            retval = 20.0
        elif pos == 2:
            retval = 30.0
        elif pos == 3:
            retval = 30.0 
        elif pos == 4:
            retval = 20.0
        elif pos == 5:
            retval = 10.0
        elif pos == 6:
            retval = -30.0
        elif pos == 7:
            retval = -30.0
        return retval

    def sonar_oy(self, dev, pos):
        # in mm
        if pos == 0:
            retval = 30.0
        elif pos == 1:
            retval = 20.0
        elif pos == 2:
            retval = 10.0
        elif pos == 3:
            retval = -10.0 
        elif pos == 4:
            retval = -20.0
        elif pos == 5:
            retval = -30.0
        elif pos == 6:
            retval = -10.0
        elif pos == 7:
            retval = 10.0
        return retval

    def laser_thd(self, dev, pos):
	""" B21R has 0 degree to far right """
	return pos - 90.0

    def sonar_th(self, dev, pos):
	pass

    def sonar_thd(self, dev, pos):
        if pos == 0:
            return 90.0
        elif pos == 1:
            return 45.0
        elif pos == 2:
            return 0.0
        elif pos == 3:
            return 0.0 
        elif pos == 4:
            return -45.0
        elif pos == 5:
            return -90.0
        elif pos == 6:
            return 180.0
        elif pos == 7:
            return 180.0

    def getOptions(self): # overload 
        pass

    def connect(self):
        pass

    def disconnect(self):
        self.stop()

    def update(self):
	self.dev.UpdateReadings()
	self.x = self.dev.getX() / 1000.0
	self.y = self.dev.getY() / 1000.0
	self.th = self.dev.getTh()
	self.thr = self.dev.getThr()
	self.senseData["laser"] = self.dev.getLaser()
	self.senseData["sonar"] = self.dev.getSonarHigh()
	self.senseData["lowsonar"] = self.dev.getSonarLow()
        self.stallHistoryPos = (self.stallHistoryPos + 1) % self.stallHistorySize
	self._update()

    def isStall(self, dev = 0):
        stalls = float(reduce(lambda x, y: x + y, self.stallHistory))
        # if greater than % of last history is stall, then stall
        return (stalls / self.stallHistorySize) > 0.5

    def getX(self, dev = 0):
        return self.mmToUnits(self.x, self.senses['robot']['units'](dev))
    
    def getY(self, dev = 0):
	return self.mmToUnits(self.y, self.senses['robot']['units'](dev))
    
    def getZ(self, dev = 0):
        return 0
    
    def getTh(self, dev = 0):
        return self.th

    def getThr(self, dev = 0):
        return self.thr

    def getSonarMaxRange(self, dev):
        return self.rawToUnits(dev, 2.999, 'sonar')

    def getSonarRange(self, dev, pos):
        return self.rawToUnits(dev, self.senseData['sonar'][pos], 'sonar')

    def getLaserRange(self, dev, pos):
        return self.rawToUnits(dev, self.senseData['laser'][pos], 'laser')

    def getLaserMaxRange(self, dev):
        return self.mmToUnits(15.0 * 1000, 'ROBOTS')

    def mmToUnits(self, mm, units):
        if units == 'MM':
            return mm
        elif units == 'CM':
            return mm / 100.0
        elif units == 'METERS':
            return mm / 1000.0
        elif units == 'ROBOTS':
            return mm / 6000.0
	else:
	    raise TypeError, "unknown type: '%s'" % units
        
    def rawToUnits(self, dev, raw, name, units = None):
        if units == None:
            units = self.senses[name]['units'](dev)
        if name == 'sonar':
            maxvalue = 2.999
            meters = raw
        elif name == 'laser':
	    maxvalue = 15.0
            meters = raw
        else:
            raise TypeError, "Type is invalid"
        if units == "ROBOTS":
            return meters / 0.6 # b21r is about 6000mm diameter
        elif units == "METERS":
            return meters
        elif units == "RAW":
            return raw 
        elif units == "CM":
            return meters / 100.0 # cm
        elif units == "MM":
            return meters / 1000.0 
        elif units == "SCALED":
            return meters / maxvalue
        else:
            raise TypeError, "Units are set to invalid type"

    def getSonarRangeAll(self, dev):
        vector = [0] * self.get('sonar', 'count')
        for i in range(self.get('sonar', 'count')):
            vector[i] = self.getSonarRange(dev, i)
        return vector

    def getLaserRangeAll(self, dev):
	vector = [0] * self.get('laser', 'count')
        for i in range(self.get('laser', 'count')):
            vector[i] = self.getLaserRange(dev, i)
        return vector

    def getSonarFlag(self, dev, pos):
        return 0

    def laser_th(self, dev, pos):
        return self.laser_thd(dev, pos) / 180.0 * math.pi

    def move(self, trans, rotate):
	self.moveDev(self.dev, trans, rotate)
    
    def moveDev(self, dev, trans, rotate):
	self.lastTranslate = trans
	self.lastRotate = rotate
        self.adjustSpeed()

    def adjustSpeed(self):
        self.dev.move(self.lastTranslate, self.lastRotate)
        
    def _move(self, trans, rotate):
	self._moveDev(self.dev, trans, rotate)

    def _moveDev(self, dev, trans, rotate):
	self.lastTranslate = trans
	self.lastRotate = rotate
	self.adjustSpeed()

    def translate(self, value):
        self.lastTranslate = value
        self.adjustSpeed()
    
    def rotate(self, value):
        self.lastRotate = value
        self.adjustSpeed()
    
    def localize(self, x = 0.0, y = 0.0, th = 0.0):
        self.x = x * 1000.0
        self.y = y * 1000.0
        self.th = th
        self.thr = self.th * PIOVER180
    
if __name__ == '__main__':
    robot = B21RRobot()
    robot.update()
