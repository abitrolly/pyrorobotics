#
# SimArtBasic Class - Simulator Atrifact (Object)
#	
#		SimArtShape: Shape description
#		Plain: a regular plain thast contains vecs & color
#		The vecs in the lpain represent POINTS (vectors from origin to the points)
#			and NOT vectors from previous point.
#		SASSquar (SAS: SimArtShape) ready-to-use square
#		SASCircle: ready-to-use circle
#		SASBox (2d)

import pyro.geometry
import pyro.gui.console
import math
import pickle

class Plain:
	"""
	Simple Plain Class
	"""
	def __init__(self):
		self.vecs = []	# Vectors that will draw the plain
		self.color = 0	# Some color for the plain
		
	def addVector(self,x,y,z=0):
		"""
		Create a Vector & add it
		"""
		self.vecs.append([x,y,z]);	
	
class SimArtShape:
	"""
	Artifact Shape - One plain for now - 2D
	"""
	def __init__(self):
		self.shape = Plain()	#The Shape - relative to the origin
		self.origin = [0,0,0]	#The Origin
		
	def centerShape(self):
		"""
		will center object to average of its x's & y's
		"""
		ave = [0,0,0] #x,y,z
		num = 0
		for vec in self.shape.vecs:
			num += 1
			for i in range(0,3):
				ave[i] += vec[i]
		if num !=0:
			for i in range(0,3):
				ave[i] /= num
			origin = ave	
	
	def toString(self):
		return "Shape"
			
		
class SASSquare(SimArtShape):
	"""Square - SimArtShape"""
	def __init__(self, side = 10, origin = [0,0,0]):
		"""side: side length, origin[x,y,z] origin point"""
		self.shape = Plain()
		self.origin = origin     #So Cube starts at 0,0,0
		self.side = side
		self.shape.vecs=[]				# clear list
		self.shape.addVector(side/2,side/2)			#upper-right
		self.shape.addVector(side/2,-side/2)		#lower-right
		self.shape.addVector(-side/2,-side/2)		#lower-left
		self.shape.addVector(-side/2,side/2)		#upper-left
	
	def toString(self):
		return "Square(" + str(self.side) + ")"

class SASBox(SimArtShape):
	"""Box - SimArtShape"""
	def __init__(self, sides = [10,10,10], origin = [0,0,0]):
		"""sides: [x,y,z] lengths of sides, origin[x,y,z] origin point"""
		self.shape = Plain()
		self.origin = origin     #So Cube starts at 0,0,0
		self.sides = sides
		self.shape.vecs=[]				# clear list
		self.shape.addVector(sides[0]/2,sides[1]/2)			#upper-right
		self.shape.addVector(sides[0]/2,-sides[1]/2)		#lower-right
		self.shape.addVector(-sides[0]/2,-sides[1]/2)		#lower-left
		self.shape.addVector(-sides[0]/2,sides[1]/2)		#upper-left
		
	def toString(self):
		return "Box(" + str(self.sides) + ")"		

class SASCircle(SimArtShape):
	"""Circle - SimArtSHape"""
	def __init__(self, radius = 10, segments = 8, origin = [0,0,0]):
		"""radius: raius, origin=[x,y,z]: origin, segments """
		self.shape = Plain()
		self.origin = origin     #So Cube starts at 0,0,0
		self.radius = radius
		self.segments = segments
		self.shape.vecs=[]				# clear list
		theta = math.pi*2/segments		
		for i in range(0,segments):
			self.shape.addVector(radius * math.cos(theta*i)\
								,radius * math.sin(theta*i))		#add a segment
	def toString(self):
		return "Circle(" + str(self.radius) + "," + str(self.segments) + ")"

