#
# SimArtBasic Class - Simulator Atrifact (Object)
#	
#		SimArtBasic: basic atrifact
#		SimArtSquare: basic square (box) object
#		SimArtCircle: basic circle object
#		SimArtBox: basic box object

from pyro.gui import console
from pyro import geometry
from SimArtShapeFile import *
import math
		
#SimArtBasic Movement Types
SimArtType = {}
SimArtType['Static']	= 0		#Static Objects
SimArtType['Move']		= 1		#Moving Objects
SimArtType['Active']	= 2		#Interactive objects (M&M machine)
SimArtType['Robot']		= 3		#Robot

class SimArtBasic:
	"""
	The Simulator Artifact
	"""
	def __init__(self, loc=[0,0,0], angle = 0):
		"""
		Creates a SimArt - Static Square in Def
		"""
		angle = angle + 5.	#a little test to make sure it's number
		angle = angle - 5.
		if not 'title' in dir(self):
			self.title = "SimArtBasic"
		console.log(console.INFO,'Creating Artifact [' + self.title + ']')
		
		#Management
		self.id = 0		#Assign ID
		self.type = SimArtType['Static']	#Assign Type
		
		#Shape
		self.shape = SASSquare(10)	#Create a new shape		
		self.color = "red"		#In the future - Color should go with Shape
				
		#Location Variables (of the real world)
		self.location = loc		#x,y,z
		self.angle = angle		#0 to 2*Math.pi 0 is in X direction
		
		#Physics Simulation Variables
		self.rotation_speed = 0	#radians per second
		self.rotation_accl = 0	#radians per second square		
		self.speed = 0	#meters per second
		self.accl = 0	#meters per second square
		self.mass = 0	#if =0 then ignore mass in this object
		
	def toString(self):
		""" Print some info about the Atrifact
		"""	
		return "id(" + str(self.id) + ") loc: " +\
				 geometry.PrintPoint(self.location) +\
				"," + str(self.angle) + " " + self.shape.toString()
	
	def takeTimeStep(self):
		""" Update the object according to the control model"""
		#No movement for Static Objects!
		#do nothing for now
		pass
		
	def translate(self, vec, noshape = 0):#vec points from center to some point
		if (noshape):
			return geometry.add(geometry.rotate(vec, self.angle),\
									 self.location)
		else:
			return geometry.add(self.shape.origin,\
							geometry.add(geometry.rotate(vec, self.angle),\
									 self.location))
	
	def intersectLine(self, a, b):
		"""intersect line a-b with this object
		return (intersect?, intersection_point) that is closest
		to a"""
		inter_res = 0
		res = [0,0,0]
		v = self.shape.shape.vecs
		for i in range(0, len(v)-1):
			va = self.translate(v[i])
			vb = self.translate(v[i+1])			
			(inter, d) = geometry.intersectSegSeg(va, vb, a, b)
			if (len(d)==2):
				d.append(0.0)
			if (inter):
				if (inter_res==0 or geometry.distance(a,d)\
					 < geometry.distance(a,res)):
					res = d
					inter_res = 1
		return (inter_res, res)

	def intersectArt(self, art):
		"""intersect artifact with this object
		return if they intersect or not"""
		v = self.shape.shape.vecs
		for i in range(0, len(v)-1):
			(inter, d) = art.intersectLine(v[i], v[i+1])
			if (inter):
				return inter
		return 0
		
		

class SimArtSquare(SimArtBasic):
	""" SimArtBasic - Square """
	def __init__(self, side=1, loc=[0,0,0], angle=0):
		self.title = "Square"
		SimArtBasic.__init__(self, loc, angle)
		self.type = SimArtType['Static']
		self.shape = SASSquare(side)

class SimArtCircle(SimArtBasic):
	""" SimArtBasic - Circle """
	def __init__(self, radius=1, segments=8, loc=[0,0,0], angle=0):
		self.title = "Circle"
		SimArtBasic.__init__(self, loc, angle)
		self.type = SimArtType['Static']
		self.shape = SASCircle(radius, segments)

class SimArtBox(SimArtBasic):
	""" SimArtBasic - Box """
	def __init__(self, sides=[1,1,1], loc=[0,0,0], angle=0):
		self.title = "Box"
		SimArtBasic.__init__(self, loc, angle)
		self.type = SimArtType['Static']
		self.shape = SASBox(sides)

