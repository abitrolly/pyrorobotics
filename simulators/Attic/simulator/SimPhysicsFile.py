"""
This is the Physical Model - will move things according to physical laws
It will take an array of objects (in a world) and a delta_time
then it will move them.
"""

from SimArtBasicFile import *
from pyro.gui import console
import math

class SimPhysics:
	"""
	Physics SImulator Class
	"""
	def __init__(self):
		pass
		
	def process(self, arts, delta_time):
		"""
		This function takes:
			arts:		 SimArtBasic array
			delta_time:  double - time to simulate
		This funciton has to move all the objects (update their X,Y)
		and then detect any collisions and fix them.
		"""
		console.log(console.INFO, "Phyisics Simulator - run")
		#Here's a very very very simple physics engine:
		#no collision detection for now
		for x in arts:
			#increase speed
			x.speed = x.speed + x.accl * delta_time
			#if (x.speed > x.max_speed):
			#	x.speed = x.max_speed
			#rotate - convert to radiant
			x.rotation_speed = x.rotation_speed + x.rotation_accl * delta_time
			#if (x.rotation_speed > x.max_rot_speed):
			#	x.rotation_speed = x.max_rot_speed
			
			#rotate
			x.angle = x.angle + x.rotation_speed * delta_time
			
			if (self.detectCollision(arts, x)):
				#if collided - then take the move back & modify speed
				x.angle = x.angle - x.rotation_speed * delta_time
				if (x.type != SimArtType['Move']):
					#unless it's a continuously moving object, stop it
					x.rotation_speed = 0

			#move
			x.location = [math.cos(x.angle)*x.speed*delta_time + x.location[0],\
						math.sin(x.angle)*x.speed*delta_time + x.location[1],\
						0*x.speed*delta_time + x.location[2]]

			if (self.detectCollision(arts, x)):
				#if collided - then take the move back & modify speed
				x.location = [x.location[0] - math.cos(x.angle)*x.speed*delta_time,\
						x.location[1] - math.sin(x.angle)*x.speed*delta_time,\
						x.location[2] - 0*x.speed*delta_time]				
				if (x.type != SimArtType['Move']):
					#unless it's a continuously moving object, stop it
					x.speed = 0
				#if it's a robot - then signal stall
				if (x.type == SimArtType['Robot']):
					x.stall = 1
			else:
				#if it's a robot - then signal stall
				if (x.type == SimArtType['Robot']):
					x.stall = 0
				
	def detectCollision(self, arts, obj):
		"""
		just return true if collision happened or not
		"""
		for x in arts:
			if (x == obj):
				continue
			if (obj.intersectArt(x)):
				return 1
		return 0
		
		