"""
SimClientRobot	-	Simulated Client Robot Class
this class is a basis for all other robot clients.
It inherits from SimClient. It creates a robot on initialization.
It will take the following:
	- Shape
	- Sensors
	- Motor
	
It will do all the communication with the Server.
This class will get attached to a Robot class
any derivative should also provide its own version of
	

functiosn to override:
	init_robot_parts()
	
"""

from pyro.gui import console
from pyro.system.ClientServer import *
#from SimClientFile import *
from SimArtBasicFile import *
from SimRobotPartsFile import *
from pyro import geometry
import math

class SimClientRobot(Client):
	"""
	All Robot Simulators should extend this class
	It communicates with the server to:
		- Create the Robot
		- Move the Robot
		- Control the Robot
		- Control some aspects of simulation, like time
		
	TODO: fix the Client-Server direct response expectation!
	"""
	def __init__(self, host="localhost", port=PYROPORT):
		" here will inialize "
		Client.__init__(self, host, port)
		
		self.type = "ClientRobot"
		self.name = "Default"
		self.id = -1 #not initialized yet
		
		#location information
		self.location = geometry.Point()#[0,0,0]
		self.angle = 0	#radian angle		
		self.stall = 0
		
		#build the robot up - should override this function
		self.init_robot_parts()
		
	def connect(self):
		" here we connect and create robot at server "
		#connect
		Client.connect(self)
		#create robot instance in the server - no override
		self.init_robot_server()
	
	def init_robot_parts(self):
		"here we build up the robot - should override this function"		
		#def values are just for testing, derived robots should override this
		self.shape = SASCircle(1,8)
		self.sonars = []
		#add 6 sensors
		addCircularSonars(self,1,4)#robot, radius,number of sonars
		self.sonars.append(SimBumper([0,1,0], math.pi/2))	#front bumper
		self.sonars.append(SimBumper([0,-1,0],-math.pi/2))#back bumper
		self.motor = SimMotor()	#default Motor
		
	def init_robot_server(self):
		"will create a robot instance in the server - don't override"
		#Create the Robot
		self.send(Message("Robot","Create"))
		#not sure if it's best to wait right here for the reponse!
		msg = self.receive()
		if (msg.body == "OK Create"):
			self.id = msg.args['id']#success
			console.log(console.INFO,'Server created robot successfully')
		else:# (msg.body == "Error"):
			console.log(console.ERROR,"Can't create robot")
			#raise 'ClientError', "Server protocol not compatible - can't create robot"
			return#just to be sure!
		
		#now send the Shape
 		self.send(Message("Robot","Components",\
 			{'id':self.id, 'shape':self.shape, \
 			'sonars':self.sonars, 'motor':self.motor}))
		#not sure if it's best to wait right here for the reponse!
		msg = self.receive()
		if (msg.body == "Error"):
			console.log(console.ERROR,"Can't send components")
#			raise 'ClientError', "Server protocol not compatible - can't send components"
			return#just to be sure!		
		else:#success
			console.log(console.INFO,'Components of robot sent successfully to server')
	
	def move_direct(self, location, angle):
		"this function will pick up the robot and move it somewhere else"
		#send move request
		#locatin and angle are the CHANGE in POSITION
		#and not the absolute locationand position
 		self.send(Message("Robot","Move",\
 			{'id':self.id, 'location':location, 'angle':angle}))
 		#wait for response 		
 		msg = self.receive()
 		if (msg.body != "OK Move"):#all fine
			#raise 'ClientError', "Server protocols not compatible - can't move robot"
			console.log(console.ERROR,"Can't move robot [" + msg.body + "]")
			return#just to be sure!
		console.log(console.INFO,'Move successful')
		self.location = geometry.add(self.location, location)	#update new location
		self.angle += angle			#update new angle
		
	def move(self, speed, rot_speed):
		" regular move: should set the desired speed and angle"
 		self.send(Message("Robot","Command",\
 			{'id':self.id, 'speed':speed, 'rot_speed':rot_speed}))
 		#wait for response 		
 		msg = self.receive()
 		if (msg.body != "OK Command"):#all fine
			#raise 'ClientError', "Server protocols not compatible - can't move robot"
			console.log(console.ERROR,"Can't send commands to robot [" + msg.body + "]")
			return#just to be sure!
		console.log(console.INFO,'Command successful')
		
	def run_server(self, steps):
		" force world to simulate steps numnber of cycles"
 		self.send(Message("Robot","Time",\
 			{'steps':steps}))
 		#wait for response 		
 		msg = self.receive()
 		if (msg.body != "OK Time"):#all fine
			#raise 'ClientError', "Server protocols not compatible - can't move robot"
			console.log(console.ERROR,"Can't send time request to robot [" + msg.body + "]")
			return#just to be sure!
		console.log(console.INFO,'Time successful')
				
	def updateSenses(self):
		" force Sonar readings "
		pass
		#get location/and other stuff from server
		#self.location = geometry.add(self.location, geometry.multiply(self.speed, self.orient))
		#update new location
		#self.angle += angle			
		#update new angle
		
		
if (__name__ == '__main__'):#only in testing file
	import sys
	import string
	rb = SimClientRobot()
	rb.connect()
	quit = 0
	quit2 = 0
	while (quit2==0):
		try:
			while (quit==0):
				line = sys.stdin.readline()
				words = string.split(line)
				if (words[0] == 'time'):
					if (len(words) != 2):
						print 'time steps'
						continue
					steps = float(words[1])
					rb.run_server(steps)
				if (words[0] == 'command'):
					if (len(words) != 3):
						print 'command speed(-1,1) rot_speed(-1,1)'
						continue
					sp = float(words[1])
					rsp = float(words[2])
					rb.move(sp, rsp)
				if (words[0] == 'move'):
					if (len(words) != 4):
						print 'move x y angle'
						continue
					x = float(words[1])
					y = float(words[2])
					a = float(words[3])
					rb.move_direct([x,y,0],a)
				elif (words[0] == 'quit'):
					quit = 1
					break
			print 'done'
			quit2 = 1
		except:
			print "Some error happened:[",sys.exc_info()[0],']'
			print 'continue to run'
		
		
