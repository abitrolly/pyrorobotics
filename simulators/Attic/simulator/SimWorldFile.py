#
# Simulator World
#	This class will handle Objects/Their motion/Their state/etc...
#	It does NOT include: communication/Object features/interaction
#	It's 2D only - for now
#		- Muhammad Arrabi
# art is a SimArtBasic (Artifact)
# arts is the list of Artifacts

from SimArtBasicFile import *
from SimPhysicsFile import *
from SimRobotPartsFile import *
from SimRobotFile import *
from pyro.gui import console
from pyro import geometry
import random

class SimWorld:
	"""
	The Simulator World Class
	"""
	def __init__(self):
		console.log(console.INFO,'Creating the World')
		self.arts = []		#SimArt objects
		self.time = 0.0		#starts at time 0
		self.delta_time = 1.0 #ms - that means each step is a 1ms
		self.physics_model = SimPhysics()
		
	def listArts(self):
		"""
		Print a list of artifacts to console
		"""
		i=0
		print "time=", self.time	#print time
		for x in self.arts:				#print Artifacts
			i = i+1
			print 'Art ', i, ':', x.toString()
		
		
	def addArt(self, art):
		"""
		Add Artifact to the World by its Shape
		agrs: art - SimArtBasic class - or child
		return: art.id - int, artifact ID
		"""
		console.log(console.INFO,'Adding Artifact to the world')
		art.id = len(self.arts)
		self.arts.append(art)				#append to the list
		return art.id
		
	
	def setSonarReading(self, sonars, holder = SimArtBasic()):
		"""
		This function will take SimSonar array
		and fix their reading - using some noise module
		Note: the noise model is part of the SimSonar class
		"""
		value = 10 #get sonar value from world
		#add world noise (rain, etc.)
		#the sonar will add its own noise also
		#sonars[0].getReading(value)
		
		for x in sonars:
			a = holder.translate(x.location, 1)#1 for noshape
			b = holder.translate(x.max_point(),1)
			(inter, d) = self.intersectWithAll(a, b, holder)
			if (inter):
				length = geometry.distance(a, d)
				length = self.addSonarNoise(length)
			else:
				length = x.max_length
				length = self.addSonarNoise(length)
			x.setReading(length)
	
	def addSonarNoise(self, length):
		"""
		for now, no noise added from world
		"""
		self.sonar_noise = 0
		return length + self.sonar_noise * random.random()
			

	def intersectWithAll(self, a, b, holder):
		"""this function will intersect the line a-b with
		all objects in world except the holder, and return
		the closest intersection point to a.
		return (intersect?, intersection_point)"""
		inter_res = 0
		res = [0,0,0]
		for x in self.arts:
			if (x == holder):
				continue
			(inter, d) = x.intersectLine(a, b)
			if (inter):
				if (inter_res==0 or geometry.distance(a,d)\
					 < geometry.distance(a,res)):
					res = d
					inter_res = 1
		return (inter_res, res)	
		
	
	def takeTimeStep(self):
		"""
		Take a time step in the World & update it
		"""
		self.time += self.delta_time			#increment time
		for x in self.arts:	#update artifacts
			x.takeTimeStep()
			#When this functino is called in the Robot
			#It gets to change desired-speed/acceleration/
			#and to read sonars. To read sonars, call GetSonarReading
		
		#update any sonar readings
		for x in self.arts:	#update artifacts
			if (x.type == SimArtType['Robot']):
				self.setSonarReading(x.sonars, x)
		
		#This is the physics part
		self.physics_model.process(self.arts,self.delta_time)
		
#testing code:
#I put it in the SimWindow file
if (__name__ == '__main__'):
	import sys
	from SimWindowFile import *
	
	def test_():
	
		print dir(base.simulator)
		
		sw = SimWorld()
		
		sw.addArt(SimArtSquare(1,[10,10,0],0))	#at 0,0,0, looking forward
		sw.arts[0].color = "red"
		sw.addArt(SimArtBox([1,1,1],[10,10,0],0))	#at 0,0,0, looking forward
		sw.arts[1].color = "green"
		sw.addArt(SimArtCircle(1,8,[-10,-10,0],0))	#at 0,0,0, looking forward
		sw.arts[2].color = "pink"
		sw.addArt(SimRobot())	#at 0,0,0, looking forward
		sw.arts[3].color = "orange"
		
		for x in range(1,4):
			sw.listArts()
			sw.takeTimeStep()
					
		sw.listArts()
		
		wind = SimWindow(sw)
		wind.update()
		
		sw.arts[3].setDesired(1,0)
		
		for x in range(1, 10):
			print 'timestep:', x
			print sw.arts[3].toString()
			sw.takeTimeStep()
			wind.update()
		
		print '**********\n** Done **\n**********'
		print 'press enter to finish'
		sys.stdin.readline()
		
		
	test_()
