from socket import *
from pyro.robot import Robot
from pyro.robot.device import Device

#class IRSensor(Device):
#	def __init__(self, dev, type = "ir"):

def car_cdr(lisp):
	car = ""
	for x in range(1, len(lisp)):
		if lisp[x] == ")":
			return car, "(" + lisp[len(car)+1:]
		elif lisp[x] == " ":
			return car, "(" + lisp[len(car)+2:]
		else:
			car += lisp[x]

def lisp2list(lisp):
	if lisp[0] == "(":
		car,cdr = car_cdr(lisp)

class RobocupRobot(Robot):
	BUF = 1024
	def __init__(self, name, host = "localhost", port = 6000):
		Robot.__init__(self)
		self.devData["simulated"] = 1
		self.devData["name"] = name
		self.devData["host"] = host
		self.devData["port"] = port
		self.address = (self.host, self.port)
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
		if 
			self.sendMsg('N') 
			self.sendMsg('O') 
			self.sendMsg('H') 
			self.sendMsg('E') 
			self.sendMsg('K') 
