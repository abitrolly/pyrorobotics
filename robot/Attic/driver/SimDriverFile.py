"""
This file conatins the automatic drivers, taht will take
a SimClientRobot as input,m and then analyse it into sensors and controls
"""

import pyro.robot.driver as driver
import pyro.gui.console as console


class SimSenseDriver(driver.Driver):
	def __init__(self, machine, simrobot):
		" machine: nothing, simrobot: SimClientRobot instance "
		driver.Driver.__init__(self)
		self.senses['robot'] = {}
		self.simrobot = simrobot
		
		# robot senses (all are functions):		
		self.senses['robot']['stall'] = lambda self: self.stall
		self.senses['robot']['x'] = lambda self: self.location[0]
		self.senses['robot']['y'] = lambda self: self.location[1]
		self.senses['robot']['z'] = lambda self: self.location[2]
		self.senses['robot']['th'] = lambda self: self.getAngle()
		self.senses['robot']['type'] = lambda self: self.type
		self.senses['robot']['name'] = lambda self: self.name

		#sonars
		self.senses['sonar'] = {}
		self.senses['sonar']['count'] = lambda self: len(self.simrobot.sonars)
		
		# location of sensors:
		self.senses['sonar']['ox'] = lambda self, index: self.sonars[index].location[0]
		self.senses['sonar']['oy'] = lambda self, index: self.sonars[index].location[1]
		self.senses['sonar']['oz'] = lambda self, index: self.sonars[index].location[2]
		self.senses['sonar']['th'] = lambda self, index: self.sonars[index].getAngle()*(180/3.14)
		self.senses['sonar']['thr'] = lambda self, index: self.sonars[index].getAngle()
		self.senses['sonar']['arc'] = lambda self, index: self.sonars[index].arc
		
		
		# location of sensors' hits:
		self.senses['sonar']['x'] = lambda self, index: self.sonars[index].getReadingXYZ()[0]
		self.senses['sonar']['y'] = lambda self, index: self.sonars[index].getReadingXYZ()[1]
		self.senses['sonar']['z'] = lambda self, index: self.sonars[index].getReadingXYZ()[2]
		self.senses['sonar']['range'] = lambda self, index: self.sonars[index].getReading()
		#0 if no new data, 1 if new data, 2 if new no hit
		self.senses['sonar']['flag'] = lambda self, index: self.sonars[index].getFlag()
		
		self.senses['sonar']['type'] = lambda self: self.sonars[index].type

		console.log(console.INFO,'SimClientRobot['+self.simrobot.type+':'+self.simrobot.name+'] sense driver loaded')


class SimControlDriver(driver.Driver):
	def __init__(self, machine, simrobot):
		self.simrobot = simrobot
		driver.Driver.__init__(self)
		self.controls['move'] = lambda self, velo, rot_velo: self.move(velo,rot_velo)
		self.controls['translate'] = lambda self, velo: self.move(velo,0)
		self.controls['rotate'] = lambda self, rot_velo: self.move(0,rot_velo)
		self.controls['update'] = lambda self: self.updateSenses()
		console.log(console.INFO,'SimClientRobot['+self.simrobot.type+':'+self.simrobot.name+'] control driver loaded')


