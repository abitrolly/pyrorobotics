import socket, pickle
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
		self.devData["location"] = None
		self.devData["direction"] = None
		self.notSetables.extend( ["direction", "location"] )
		self.addr = (host, port)
		# Create socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			self.socket.settimeout(1)
		except:
			print "WARN: entering deadlock zone; upgrade to Python 2.3 to avoid"
		self.socket.connect( self.addr )

	def localize(self, x = 0, y = 0, th = 0):
		pass
		
	def update(self):
		self.devData["location"] = self.move("location")
		self.devData["direction"] = self.move("direction")
		self._update()

	def getItem(self, item):
		return self.move(item)

	def move(self, message, other = None):
		exp = None
		if other != None: return # rotate,translate command ignored
		if (self.socket.sendto(message, self.addr)):
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
		self.socket.close()

def INIT():
	robot = TCPRobot("localhost", 60000)
	return robot

