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
		self.addr = (host, port)
		# Create socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			self.socket.settimeout(1)
		except:
			print "WARN: entering deadlock zone; upgrade to Python 2.3 to avoid"
		self.socket.connect( self.addr )
		notsetables = self.getItem("notsetables")
		for item in notsetables:
			self.devData[item] = None
		self.notSetables.extend( notsetables )
		self.connectionNum = self.getItem("connectionNum:%d" % self.devData["port"])
		self.updateables = self.getItem("updateables")

	def localize(self, x = 0, y = 0, th = 0):
		pass
		
	def update(self):
		for item in self.updateables:
			self.devData[item] = self.move(item)
		self._update()

	def getItem(self, item):
		return self.move(item)

	def play(self, item):
		return self.move(item)

	def tell(self, item):
		return self.move(item)

	def ask(self, item):
		return self.move(item)

	def move(self, message, other = None):
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

