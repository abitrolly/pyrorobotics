import socket
from pyro.robot import Robot

class TCPRobot(Robot):
	"""
	A simple TCP-based socket robot for talking to SymbolicSimulator.
	"""
	BUFSIZE = 1024
	def __init__(self, host, port):
		Robot.__init__(self)
		# Set the socket parameters
		self.devData["host"] = host
		self.devData["port"] = port
		self.devData["Location"] = None
		self.devData["Status"] = None
		self.notSetables.extend( ["Status", "Location"] )
		self.addr = (host, port)
		# Create socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.socket.settimeout(1)
		self.socket.connect( self.addr )

	def localize(self, x = 0, y = 0, th = 0):
		pass
		
	def update(self):
		self.devData["Location"] = self.move("Location")
		self.devData["Status"] = self.move("Status")
		self._update()

	def getItem(self, item):
		return self.move(item)

	def move(self, message, other = None):
		if other != None: return # rotate,translate command ignored
		if (self.socket.sendto(message, self.addr)):
			try:
				retval, addr = self.socket.recvfrom(self.BUFSIZE)
			except:
				retval = ""
			retval = retval.strip()
		return retval

	def disconnect(self):
		# Close socket
		self.socket.close()

def INIT():
	robot = TCPRobot("localhost", 6000)
	return robot

