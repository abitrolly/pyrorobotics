
from pyro.robot.sensor import *

class AriaRangeSensor(RangeSensor):
    """ For general Aria-sensors """

class AriaLaser(AriaRangeSensor):
    """ A Laser sensor for the Aria-class robots """

    def getType(self):
        return "range"
    def getCount(self):
        return 180
    def getMaxvalue(self):
        return self.mmToUnits(15.0 * 1000, 'ROBOTS')

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



class AriaSonar(AriaRangeSensor):
    """ A Sonar sensor for the Aria-class robots """

    
