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
        self.senses['robot'] = {}
        
	# robot senses (all are functions):
        self.senses['robot']['stall'] = Saphira_IsStall
        self.senses['robot']['x'] = Saphira_getX
        self.senses['robot']['y'] = Saphira_getY
        self.senses['robot']['z'] = Saphira_getZ
        self.senses['robot']['th'] = Saphira_getTh # in degrees
        self.senses['robot']['thr'] = Saphira_getThr # in radians
	self.senses['robot']['type'] = lambda self: 'saphira'

	self.senses['robot']['name'] = lambda self: 'saphira-1'

	self.senses['sonar'] = {}
	self.senses['sonar']['count'] = \
		lambda self, x = Saphira_getSonarCount(machine.dev) : x

	# location of sensors' hits:
	self.senses['sonar']['x'] = Saphira_getSonarXCoord
	self.senses['sonar']['y'] = Saphira_getSonarYCoord
	self.senses['sonar']['z'] = lambda self, pos: 0.25
	self.senses['sonar']['value'] = Saphira_getSonarRange
        self.senses['range'] = {}
        self.senses['range']['all'] = self.getSonarAll
        self.senses['range']['count'] = \
		lambda self, x = Saphira_getSonarCount(machine.dev) : x
        self.senses['range']['maxvalue'] = lambda self: 2.99
	self.senses['sonar']['flag'] = Saphira_getSonarFlag

	# location of origin of sensors:
        self.senses['sonar']['ox'] = Saphira_sonar_x
	self.senses['sonar']['oy'] = Saphira_sonar_y
	self.senses['sonar']['oz'] = lambda self, pos: 0.25 # meters
	self.senses['sonar']['th'] = Saphira_sonar_th
        # in radians:
        self.senses['sonar']['arc'] = lambda self, pos, \
                                      x = (5 * math.pi / 180) : x
	self.senses['sonar']['type'] = lambda self: 'range'
        
        console.log(console.INFO,'saphira sense drivers loaded')

    def mToSenseUnits(self, val):
        if self.senseUnits == ROBOTS:
            return val / 0.5 # Pioneer is about .5 meters diameter
        elif self.senseUnits == MM:
            return val / 1000.0
        elif self.senseUnits == CM:
            return (val) / 100.0 # cm
        elif self.senseUnits == METERS:
            return (val) 
        elif self.senseUnits == SCALED:
            print "WARNING: Pioneer senseUnits is SCALED?"
            # FIX: should we have maxvalue? Force [0,1]?
            return val / 0.5

    def getSonarAll(self, dev):
        vector = [0] * Saphira_getSonarCount(dev)
        for i in range(Saphira_getSonarCount(dev)):
            vector[i] = Saphira_getSonarRange(dev, i)
        return vector


class SaphiraControlDriver(driver.Driver):
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.controls['move'] = Saphira_Move
        #self.controls['accelerate'] = Saphira_Accelerate
        self.controls['translate'] = Saphira_Translate
        self.controls['rotate'] = Saphira_Rotate
        self.controls['update'] = Saphira_UpdateReadings
        self.controls['localize'] = Saphira_Localize
        console.log(console.INFO,'saphira control drivers loaded')


