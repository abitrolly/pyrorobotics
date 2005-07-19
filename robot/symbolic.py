import socket, pickle
from pyrobot.robot import Robot
from pyrobot.robot.device import Device, SensorValue

class SimDevice(Device):
	def __init__(self, name, index, robot, geometry, groups):
		Device.__init__(self, name)
		self.geometry = geometry
		self.groups = groups
		self.startDevice()
		self._dev = robot
		self.index = index
		self.maxvalueraw = geometry[2]
		self.rawunits = "M"
		self.units = "ROBOTS"
		self.radius = robot.radius
	def __len__(self):
		return len(self.geometry[0])
	def getSensorValue(self, pos):
		try:
			v = self._dev.__dict__["%s_%d" % (self.type, self.index)][pos]
		except:
			v = 0.0
		return SensorValue(self, v, pos,
				   (self.geometry[0][pos][0], # x in meters
				    self.geometry[0][pos][1], # y
				    0.03,                    # z
				    self.geometry[0][pos][2], # arc rads
				    self.geometry[1]),        # arc rads
				   )
class TCPRobot(Robot):
	"""
	A simple TCP-based socket robot for talking to PyrobotSimulator.
	"""
	BUFSIZE = 1024
	def __init__(self, host, port):
		Robot.__init__(self)
		# Set the socket parameters
		self.host = host
		self.port = port
		self.addr = (host, port)
		self.type = "Pyrobot"
		self.radius = 1.50
		# Create socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			self.socket.settimeout(1)
		except:
			print "WARN: entering deadlock zone; upgrade to Python 2.3 to avoid"
		self.socket.connect( self.addr )
		self.connectionNum = self.getItem("connectionNum:%d" % self.port)
		self.properties = self.getItem("properties")
		self.builtinDevices = self.getItem("builtinDevices")
		self.supportedFeatures = self.getItem("supportedFeatures")
		self.id   = self.connectionNum
		for dev in self.builtinDevices:
			d = self.startDevice(dev)
			if dev in ["sonar", "laser"]:
				self.range = d

	def localize(self, x = 0, y = 0, th = 0):
		pass

	def update(self):
		for i in self.properties:
			self.__dict__[i] = self.getItem(i)
		self.updateDevices()
		
	def getItem(self, item):
		return self.move(item)

	def eat(self, amt):
		return self.move("e_%f" % (amt))

	def play(self, item):
		return self.move(item)

	def tell(self, item):
		return self.move(item)

	def ask(self, item):
		return self.move(item)

	def moveDir(self, dir):
		if dir == 'L':
			self.move("left")
		elif dir == 'R':
			self.move("right")
		elif dir == 'F':
			self.move("forward")
		elif dir == 'B':
			self.move("back")

	def startDeviceBuiltin(self, name, index = 0):
		self.properties.append("%s_%d" % (name, index))
		self.move("s_%s_%d" % (name, index))
		geometry = self.move("g_%s_%d" % (name, index))
		groups = self.move("r_%s_%d" % (name, index))
		return {name: SimDevice(name, index, self, geometry, groups)}

	def translate(self, value):
		self.move("t_%f" % value)

	def rotate(self, value):
		self.move("o_%f" % value)

	def move(self, message, other = None):
		if type(message) in [type(1), type(1.)] and type(other) in [type(1), type(1.)]:
			message = "m_%.2f_%.2f" % (message, other)
			other = None
		exp = None
		if self.socket == 0: return "not connected"
		if other != None: return # rotate,translate command ignored
		if message == "quit" or message == "exit" or message == "end":
			if self.connectionNum == 0: # the main one, let's close up!
				self.socket.sendto(message, self.addr)
			self.socket.close()
			self.socket = 0
			return "ok"
		else:
			self.socket.sendto(message, self.addr)
			try:
				retval, addr = self.socket.recvfrom(self.BUFSIZE)
			except:
				retval = ""
			retval = retval.strip()
			try:
				exp = pickle.loads( retval )
			except:
				exp = retval
		return exp

	def disconnect(self):
		# Close socket
		self.getItem("quit")

