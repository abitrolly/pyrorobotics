#
# Test Server (receive python command, execute, and then send back
#	This class will handle WSimWoprld Server communication
#
#	All communication between Client and Server are done through
#		Message objects. NO REGULAR TEXT EXCHANGE!
#
#	Protocol: Server will return a message for every message it gets!
#
"""
TO be done:
provide easy functiosn to interpret and control the server options
add the option to kill_server
add GUI to window to control the server
add interface functiosn to control world/window/server/atrifacts

"""

from SimWorldFile import *
from SimWindowFile import *
from pyro.system.ClientServer import *
from pyro import geometry

from pyro.gui import console
import time
import thread

import socket
import SocketServer

class SimReqHandler(ReqHandler):
	"""
	This class is created per connection
	It keeps getting stuff from the connection until it's closed
	"""
	
	def process_robot(self, data):
		"""this function will process any messages that deal with robots
		args: data - Message class
		return: msg - Message class
		"""
		msg = None
		#Creation
		if (data.body == "Create"):
			id = self.server.world.addArt(SimRobot())	#at 0,0,0 looking 0
			msg = Message("Robot","OK Create",{'id':id})
			console.log(console.INFO,'Robot created')

		#load robot components
		elif(data.body == "Components"):
			id = data.args['id']#the robot artifact ID in the world
			#{id, shape, sonars, motor}
			self.server.world.arts[id].shape = data.args['shape']
			self.server.world.arts[id].sonars = data.args['sonars']
			self.server.world.arts[id].motor = data.args['motor']			
			msg = Message("Robot","OK Components")
			console.log(console.INFO,'Robot components loaded')
		
		#Movement - Direct: left the robot and put it somewhere
		elif(data.body == "Move"):
			id = data.args['id']
			location = geometry.add(self.server.world.arts[id].location\
								,data.args['location'])
			angle = self.server.world.arts[id].angle + data.args['angle']
			
			self.server.world.arts[id].location = location
			self.server.world.arts[id].angle = angle
			console.log(console.INFO,'Robot OK move')
			msg = Message("Robot","OK Move")
		
		#Set Desired Movement
		elif(data.body == "Command"):
			id = data.args['id']
			speed = data.args['speed']
			rot_speed = data.args['rot_speed']
			
			self.server.world.arts[id].setDesired(speed, rot_speed)
			console.log(console.INFO,'Robot ok command')
			msg = Message("Robot","OK Command")
		
		#Set Desired Movement
		elif(data.body == "Time"):
			time_steps = data.args['steps']
			console.log(console.INFO,'Robot ok time:' + str(time_steps))			
			self.server.running = time_steps
			msg = Message("Robot","OK Time")
		
		#Error
		else:
			console.log(console.WARNING,'Unknown message args[0] from client['\
			 + data.body + ':' + data.type + ':' + str(data.args) + ']')
			msg = Message("Robot","Error",data.args)
					
		if (msg == None):
			msg = Message("Robot","Error",data.args)
			console.log(console.INFO,'data not processed in process_robot()')
		return msg
			

class SimServer(Server):
	def __init__(self, ip_port=("localhost",PYROPORT)):
		Server.__init__(self, ip_port, SimReqHandler)

	def init_world(self):
		"""
		this is the real init - as far as creating the world, window
		and stuff like that
		"""
		self.world = SimWorld()
		self.window = SimWindow(self.world, self)
		self.window.start()
		#launch the runner - which will keep the world running
		self.cycle_time = .1 #.5 secomds per cycle
		#print "Running init"
		self.running = 0	#0 is stop, -1 is continuous, 9 means run 9 times
		thread.start_new_thread(self.runner, ())
		
	def runner(self):
		console.log(console.INFO, "Server Runner is launched")
		while (self.alive==1):
			#console.log(console.INFO, "Server Runnerisalive run" +str(self.running))
 			if (self.running > 0):
				self.world.takeTimeStep()
				#self.window.update()
				#self.takeTimeStep()
				self.running -= 1
				time.sleep(self.cycle_time)
			elif (self.running == -1):
				self.world.takeTimeStep()
				#self.window.update()
				#self.takeTimeStep()
				time.sleep(self.cycle_time)
			else:
				#do nothing
				pass
		console.log(console.INFO, "Server Runner has quit")						
		
	def takeTimeStep(self):
		self.world.takeTimeStep()
		self.window.update()
	
	def quit(self):
		Server.quit(self)
		if (self.window != None):
			self.window.kill()
	
if (__name__=='__main__'):

	ss = SimServer()
	ss.serve()	#listen infinitely

