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
				try:
					# doesn't get "drop_ball" above
					currentlist.append( float(symbol) )
				except:
					currentlist.append( symbol )
	if len(stack) != 0:
		raise AttributeError, "missing ending paren"
	return currentlist[0]

class RobocupRobot(Robot):
	BUF = 1024
	def __init__(self, name = "TeamPyro", host = "localhost",
		     port = 6000, teamMode = 0):
		Robot.__init__(self)
		self.lastTranslate = 0
		self.lastRotate = 0
		self.updateNumber = 0L
		self.historyNumber = 0L
		self.teamMode = teamMode
		self.lastHistory = 0
		self.historySize = 100
		self.history = [0] * self.historySize
		self.devData["simulated"] = 1
		self.devData["name"] = name
		self.devData["host"] = host
		self.devData["port"] = port
		self.address = (self.devData["host"], self.devData["port"])
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.sendto("(init %s)" % self.devData["name"], self.address)
		self.devData["builtinDevices"] = ["truth"]
		self.startDevice("truth")
		self.set("/devices/truth0/pose", (-25, 0))
		if self.teamMode:
			self.makeTeam()
		
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
		self.lastHistory = self.historyNumber % self.historySize
		msg = self.getMsg()
		if len(msg):
			self.history[self.lastHistory] = msg
			self.historyNumber += 1
		self._update()
		self.keepGoing()
		self.updateNumber += 1

	def keepGoing(self):
		# only one per cycle!
		if self.lastTranslate and self.updateNumber % 2:
			self.translate(self.lastTranslate)
		elif self.lastRotate:
			self.rotate(self.lastRotate)
			
	def translate(self, translate_velocity):
		# robocup takes values between -100 and 100
		self.lastTranslate = translate_velocity
		val = translate_velocity * 100.0
		self.sendMsg("(dash %f)" % val)

	def rotate(self, rotate_velocity):
		# robocup takes degrees -180 180
		# but that is a lot of turning!
		# let's scale it back a bit
		# also, directions are backwards
		self.lastRotate = rotate_velocity
		val = -rotate_velocity * 20.0
		self.sendMsg("(turn %f)" % val)

	def move(self, translate_velocity, rotate_velocity):
		# only one per cycle!
		self.translate(translate_velocity)
		self.rotate(rotate_velocity)

	def makeTeam(self):
		self.teamMode = 1
		self.team = [0] * 11
		# main robot:
		self.team[0] = self.socket
		# goalie
		# TODO: make this be a (goalie)
		self.team[1] = socket(AF_INET, SOCK_DGRAM)
		self.team[1].sendto("(init %s)" % self.devData["name"],
				    self.address)
		self.team[1].sendto("(move 25 25)", self.address)
		# create the other team mates:
		for x in range(2, 11):
			self.team[x] = socket(AF_INET, SOCK_DGRAM)
			self.team[x].sendto("(init %s)" % self.devData["name"],
					    self.address)
			# put in random place
			self.team[x].sendto("(move 25 25)", self.address)

	def teamMsg(self, number, msg):
		self.team[number].sendto(msg, self.address)
