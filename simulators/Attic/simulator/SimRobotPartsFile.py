"""
Robot Parts File:
	SimSonar is class containing description of Sonars
	It should also include a Noise Module
	
	SimBumper is a subclass of Sonar (since Bumpers are very accurate - close
distance sonars

	SimMotor - description of Robot Motors - still to be thought about		

"""

import random
import math
from pyro import geometry

class SimSonar:
	""" Sonar Descriopion class
	"""
	
	def __init__(self, location=[0,0,0], angle=0, max_length=1.0, arc= 5 * math.pi/180):	#1 meter
		self.max_length = max_length
		self.length = max_length
		self.location = location
		self.angle = angle
		#angle points in the middle of the sonar arc
		self.arc = arc	#how wide is the sonar reading?
		#arc starts 1/2 before the anlge and finishes 1/2 after
		self.flag = 0	#0 if no new data, 1 if yes, 2 if new no hit (max)
		self.type = 'range'
		self.color = 'yellow'
				
		#the noise model for now will be value + rnd(1,0)*noise
		self.noise = 0.0
		
	def setReading(self, value):
		"""
		The world calls this function to set the sonar reading
		Sonar then adds its own noise to it
		note: value can have world-noise added to it originally
		"""
		if (geometry.toleq(value,self.max_length)):#equal to each other
			self.flag = 2
		else:
			self.flag = 1
		self.length = self.makeNoise(value) #should add noise later
		
	def getReading(self):
		" just a getter function "
		return self.length
	
	def getReadingXYZ(self, robot):
		" will return the point of hit - using the robot position "
		return robot.translate(reading_point(), 1)#1 for noshape
	
	def getFlag(self):
		a = self.flag
		self.flag = 0
		return a
	
	def makeNoise(self, value):
		"""for now, noise model is:
		value = value + rnd(1,0)*nosie
		"""
		return value + self.noise * random.random()
		
	def max_point(self):
		"simply will return point at tip of sonar length"
		return geometry.add(self.location,\
						geometry.pol2car(self.angle, self.max_length))
	
	def reading_point(self):
		"simply will return point at reading length of sonar length"
		return geometry.add(self.location,\
						geometry.pol2car(self.angle, self.getReading()))
		
class SimBumper(SimSonar):
	""" Bumper Description Class
		Bumpers are just accurate sonars with very small distance
	"""
	
	def __init__(self, location=[0,0,0],angle=0,bumper_length = .05):#.1 meter
		SimSonar.__init__(self,location,angle,bumper_length)
		self.threshold = bumper_length/2 #the value at which we consider push
		self.length = 1.0	#Not Pushed
		self.color = 'orange'
		
	def setReading(self,value):
		"function called by world"
		if (value < self.threshold): self.length = 0.0	#Pushed
		else: self.length = 1.0	#not pushed			

class SimMotor:
	"""
	This class is the SimBot Motor Model
	This class will determine the (basic) Acceleration in which the Robot
	will usse realtive to the Desired_Speed
	Accl should not go above accl_max (or below -accl_max)
	for now:
	Accl = alpha (is fixed) = .2 m/s*s
	
	OLD:
	Accl = (DesSpeed-CurSpeed) * alpha
	alpha is the "slowing factor" between 0 and 1
	"""	
	def __init__(self, max_accl=.3, max_rot_accl=1):
		" alpha - speed accl, beta - rotation accl"
		self.max_accl = max_accl	#m/s*s
		self.max_rot_accl = max_rot_accl	#1 Radian/s*s
		
	def getAccl(self, desired_speed, current_speed):
		"""
		It will calculate accl from des_speed and cur_speed
		should be called every time cycle to change acceleration
		"""
	
		#fixed acceleration
		accl = (desired_speed - current_speed)
		if (accl > self.max_accl): accl = self.max_accl
		if (accl < -self.max_accl): accl = - self.max_accl
		return accl
		
	def getRotAccl(self, desired_speed, current_speed):
		"""
		It will calculate accl from des_speed and cur_speed
		should be called every time cycle to change acceleration
		"""
	
		#fixed acceleratino
		rot_accl = (desired_speed - current_speed)
		if (rot_accl > self.max_rot_accl): rot_accl = self.max_rot_accl
		if (rot_accl < -self.max_rot_accl): rot_accl = - self.max_rot_accl
		return rot_accl
		
#some useful functions
def addCircularSonars(robot, radius, num_sonars):
	"""
	Will add num_sonars number of sonars around the robot with a distance
	of radius from the center of the robot
	"""
	for x in range(0,num_sonars):
		theta =  x*(math.pi*2.0/num_sonars)
		location = [radius *math.cos(theta), radius*math.sin(theta),0]
		robot.sonars.append(SimSonar(location, theta))
	