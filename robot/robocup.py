from socket import *
from pyro.robot import Robot
from pyro.robot.device import Device

#class IRSensor(Device):
#	def __init__(self, dev, type = "ir"):

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
	def __init__(self, name, host = "localhost", port = 6000):
		Robot.__init__(self)
		self.devData["simulated"] = 1
		self.devData["name"] = name
		self.devData["host"] = host
		self.devData["port"] = port
		self.address = (self.devData["host"], self.devData["port"])
		self.socket = socket(AF_INET, SOCK_DGRAM)
		self.socket.sendto("(init %s)" % self.devData["name"], self.address)

	def sendMsg(self, msg):
		self.socket.sendto(msg, addr)

	def getMsg(self):
		data, addr = self.socket.recvfrom(self.BUF)
		return data

	def disconnect(self):
		self.stop()
		self.socket.close()

	def update(self):
		self._update()
		data = self.getMsg()
		print data
		try:
			pdata = parse(data)
			print pdata
		except:
			print "error"
