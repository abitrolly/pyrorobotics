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


