# simple robot:

from pyro.robot.driver.SimDriverFile import *
from pyro.robot import *
from pyro.simulator.SimClientRobotFile import *

class SimSimpleRobot(Robot):
	def __init__(self, simrobot = None):
		Robot.__init__(self, "PyroSim") # queries robot
		if (simrobot == None):
			self.simrobot = SimClientRobot()
		else:
			self.simrobot = simrobot
		self.dev = self.simrobot # device
		# this simrobot contains description of robot to
		# connect to server
		self.simrobot.connect()
		self.simrobot.run_server(-1)
		Robot.load_drivers(self) # queries robot
		self.inform("Done loading lobot.")

	def connect(self):
		self.simrobot.connect()
		pass

	def disconnect(self):
		# disconect server!
		pass
   
	def loadDrivers(self):
		self.drivers.append(SimSenseDriver(self, self.simrobot))
		self.drivers.append(SimControlDriver(self, self.simrobot))

def INIT():
	return SimSimpleRobot()
