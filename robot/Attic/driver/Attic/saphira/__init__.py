#
#
# - doug -
# 

import pyro.robot.driver as driver
import pyro.gui.console as console
from pyro.robot.driver.saphira.lowlevel import *
import math

class SaphiraSenseDriver(driver.Driver):
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.robot = machine
        self.senses['robot'] = {}
        
	# robot senses (all are functions):
        self.senses['robot']['stall'] = Saphira_IsStall
        self.senses['robot']['x'] = Saphira_getX
        self.senses['robot']['y'] = Saphira_getY
        self.senses['robot']['z'] = Saphira_getZ
        self.senses['robot']['th'] = Saphira_getTh # in degrees
        self.senses['robot']['thr'] = Saphira_getThr # in radians
        self.senses['robot']['type'] = lambda self, x = Saphira_getType(machine.dev): x
	self.senses['robot']['name'] = lambda self: 'pioneer-1'
	self.senses['sonar'] = {}
	self.senses['sonar']['count'] = \
		lambda self, x = Saphira_getSonarCount(machine.dev) : x

	# location of sensors' hits:
	self.senses['sonar']['x'] = Saphira_getSonarXCoord
	self.senses['sonar']['y'] = Saphira_getSonarYCoord
	self.senses['sonar']['z'] = lambda self, pos: 0.25
	self.senses['sonar']['value'] = self.getSonarRange
        self.senses['sonar']['all'] = self.getSonarAll
        self.senses['sonar']['maxvalue'] = self.getSonarMaxRange
	self.senses['sonar']['flag'] = Saphira_getSonarFlag

	# location of origin of sensors:
        self.senses['sonar']['ox'] = Saphira_sonar_x
	self.senses['sonar']['oy'] = Saphira_sonar_y
	self.senses['sonar']['oz'] = lambda self, pos: 0.25 # meters
	self.senses['sonar']['th'] = Saphira_sonar_th # radians
        # in radians:
        self.senses['sonar']['arc'] = lambda self, pos, \
                                      x = (5 * math.pi / 180) : x
	self.senses['sonar']['type'] = lambda self: 'range'
        self.senses['sonar']['units'] = lambda self: "ROBOTS"

        # Make a copy, for default values
        self.senses['range'] = self.senses['sonar']
        console.log(console.INFO,'saphira sense drivers loaded')

    def getSonarRange(self, dev, pos):
        return self.rawToUnits(dev, Saphira_getSonarRange(dev, pos), 'sonar')

    def getSonarMaxRange(self, dev):
        return self.rawToUnits(dev, 2.99, 'sonar')

    def rawToUnits(self, dev, raw, name):
        if name == 'sonar':
            val = min(max(raw, 0.0), 2.99)
        else:
            raise 'InvalidType', "Type is invalid"
        if self.senses[name]['units'](dev) == "ROBOTS":
            return val / 0.75 # Pioneer is about .5 meters diameter
        elif self.senses[name]['units'](dev) == "MM":
            return val * 1000.0
        elif self.senses[name]['units'](dev) == "CM":
            return (val) * 100.0 # cm
        elif self.senses[name]['units'](dev) == "METERS" or \
             self.senses[name]['units'](dev) == "RAW":
            return (val) 
        elif self.senses[name]['units'](dev) == "SCALED":
            return val / 2.99
        else:
            raise 'InvalidType', "Units are set to invalid type"

    def getSonarAll(self, dev):
        vector = [0] * Saphira_getSonarCount(dev)
        for i in range(Saphira_getSonarCount(dev)):
            vector[i] = self.getSonarRange(dev, i)
        return vector

class SaphiraControlDriver(driver.Driver):
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.controls['move'] = Saphira_Move
        self.controls['move_now'] = Saphira_Move
        #self.controls['accelerate'] = Saphira_Accelerate
        self.controls['translate'] = Saphira_Translate
        self.controls['rotate'] = Saphira_Rotate
        self.controls['update'] = Saphira_UpdateReadings
        self.controls['localize'] = Saphira_Localize
        console.log(console.INFO,'saphira control drivers loaded')


