from socket import *
from pyro.robot import Robot
from pyro.robot.device import Device

class TruthDevice(Device):
	def __init__(self, dev, type = "truth"):
		Device.__init__(self, type)
		self.dev = dev
		self.devData["pose"] = (0, 0)
	def postSet(self, item):
		if item == "pose":
			self.dev.sendMsg("(move %f %f)" % (self.devData["pose"][0], self.devData["pose"][1] ))
			

def lex(str):
	retval = []
	currentword = ""
	for ch in str:
		if ch == "(":
			if currentword:
				retval.append(currentword)
			retval.append("(")
			currentword = ""
		elif ch == ")":
			if currentword:
				retval.append(currentword)
			retval.append(")")
			currentword = ""
		elif ch == " ":
			if currentword:
				retval.append(currentword)
			currentword = ""
		elif ord(ch) == 0:
			pass
		else:
			currentword += ch
	if currentword:
		retval.append(currentword)
	return retval

def parse(str):
	lexed = lex(str)
	stack = []
	currentlist = []
	for symbol in lexed:
		if symbol == "(":
			stack.append( currentlist )
			currentlist = []
		elif symbol == ")":
			if len(stack) == 0:
				raise AttributeError, "too many closing parens"
			currentlist, temp = stack.pop(), currentlist
			currentlist.append( temp )
		else:
			if symbol.isalpha():
				currentlist.append( symbol )
			elif symbol.isdigit():
				currentlist.append( int(symbol) )
			else:
				currentlist.append( float(symbol) )
	if len(stack) != 0:
		raise AttributeError, "missing ending paren"
	return currentlist[0]

class RobocupRobot(Robot):
	BUF = 1024
	def __init__(self, name = "Pyro1", host = "localhost", port = 6000):
		Robot.__init__(self)
		self.devData["simulated"] = 1
		self.devData["name"] = name
		self.devData["host"] = host
		self.devData["port"] = port
		self.address = (self.devData["host"], self.devData["port"])
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.sendto("(init %s)" % self.devData["name"], self.address)
		self.devData["builtinDevices"] = ["truth"]
		self.startDevice("truth")
		self.sendMsg("(move 26 26)")
		
	def startDeviceBuiltin(self, item):
		if item == "truth":
			return {"truth": TruthDevice(self, "truth")}
		else:
			raise AttributeError, "robocup robot does not support device '%s'" % item
		
	def sendMsg(self, msg):
		self.socket.sendto(msg, self.address)

	def getMsg(self):
		data, addr = self.socket.recvfrom(self.BUF)
		return parse(data)

	def disconnect(self):
		self.stop()
		self.socket.close()

	def update(self):
		self._update()
			
	def translate(self, translate_velocity):
		# robocup takes values between -100 and 100
		val = translate_velocity * 100.0
		self.sendMsg("(dash %f)" % val)

	def rotate(self, rotate_velocity):
		# robocup takes degrees -180 180
		val = rotate_velocity * 180.0
		self.sendMsg("(turn %f)" % val)

	def move(self, translate_velocity, rotate_velocity):
		# only one per cycle!
		if translate_velocity != 0.0:
			val = translate_velocity * 100.0
			self.sendMsg("(dash %f)" % val)
		if rotate_velocity != 0.0:
			val = rotate_velocity * 180.0
			self.sendMsg("(turn %f)" % val)
