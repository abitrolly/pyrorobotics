#
#
#	SimRobot:
#		child of SimArtBasic - this class has the description of a general
#		robot. It will have Sonars, Motors, Bumpers, Shape
#		To make SimRobot after Elektro or Magellan, derive this class
#		and fix the desired Motors/Sonars/Laser/...
#

from SimArtBasicFile import *
from SimRobotPartsFile import *
import math

class SimRobot(SimArtBasic):
	"""
	This is a SimulatedRobot class
	As far the SimWorld is concerned, this is a regular object
	The server feeds it orders evey turn
	the robot performs these
	"""
	def __init__(self):
		self.title = "SimRobot"		#name - for debugging mainly
			#maybe use it for meanigful purposes later
		SimArtBasic.__init__(self,[0,0,0],0)	#call parent init
		self.type = SimArtType['Robot']	#not sure if this will ever be useful!
		#maybe for visualization in the future
		self.shape = SASCircle(1,8)	#Standard robots are circles
		
		self.sonars = []	#Sonars are ALL INPUT Devices the robot has
		#inluding Sonars/Bumpers/Lasers - exception is the Video Camera
		
		#by default, add these sensors
		addCircularSonars(self, 1,4)#robot, radius,number of sonars
		self.sonars.append(SimBumper([0,1,0],math.pi/2))	#front bumper
		self.sonars.append(SimBumper([0,-1,0],-math.pi/2))#back bumper
		self.stall = 0	#1 for true, 0 for false
		
		self.motor = SimMotor()	#default Motor
		
		self.desired_speed = 0.
		self.desired_rot_speed = 0.	#relative - not absolute
		
		self.max_speed = .5 #m/s - robot speed
		self.max_rot_speed = .2 #m/s - robot rotation speed
	
	def setDesired(self,speed, rotation_speed):
		"""
		This function will be called by the Server whenevr it gets a message
		from the client
		Should NOT be called by client
		"""
		if (speed > 1 or speed < -1):
			console.log(console.WARNING, "Desired Speed should be -1 to 1, it's:" + str(speed))
		if (rotation_speed > 1 or rotation_speed < -1):
			console.log(console.WARNING, "Desired Rot_Speed should be -1 to 1, it's:" + str(rotation_speed))
		self.desired_speed = speed * self.max_speed
		self.desired_rot_speed = rotation_speed	* self.max_rot_speed#relative (not absolute)
		
	def takeTimeStep(self):
		"""
		update speed/accl for robot
		Will be called once by the World
		Should NOT be called by client
		"""
		self.accl = self.motor.getAccl(self.desired_speed, self.speed)
		self.rotation_accl = self.motor.getRotAccl(self.desired_rot_speed, self.rotation_speed)
#		console.log(console.INFO, self.toString())
#		self.rotation_speed = \
#			self.motor.getRotationSpeed(self.desired_rotation)
		"""
		updating the sonars will be the worlds' job
		it has to update their values every time cycle
		"""
	
	def toString(self):
		""" Print some info about the Robot
		"""	
		return "id(" + str(self.id) + ") loc: " + geometry.PrintPoint(self.location) +\
				" " + self.shape.toString() +\
				"\nSpeed=" + str(self.speed) + " accl=" + str(self.accl) +\
				" rotation_speed=" + str(self.rotation_speed) +\
				"\nDesired speed=" + str(self.desired_speed) +\
				"desired rotation=" + str(self.desired_rot_speed)
			