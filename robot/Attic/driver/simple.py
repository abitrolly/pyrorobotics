import pyro.robot.driver as driver
import pyro.gui.console as console


class SimpleSenseDriver(driver.Driver):
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.senses['robot'] = {}
        
	# robot senses (all are functions):
        self.senses['robot']['stall'] = lambda self: 0
        self.senses['robot']['x'] = lambda self: 0
        self.senses['robot']['y'] = lambda self: 0
        self.senses['robot']['z'] = lambda self: 0
        self.senses['robot']['th'] = lambda self: 0
	self.senses['robot']['type'] = lambda self: 'simple'

	self.senses['robot']['name'] = lambda self: 'simple-1'

	self.senses['sonar'] = {}
	self.senses['sonar']['count'] = lambda self: 0

	# location of sensors' hits:
	self.senses['sonar']['x'] = lambda self, pos: 0
	self.senses['sonar']['y'] = lambda self, pos: 0
	self.senses['sonar']['z'] = lambda self, pos: 0
	self.senses['sonar']['range'] = lambda self, pos: 0 
	self.senses['sonar']['flag'] = lambda self, pos: 0 

	# location of sensors:
        self.senses['sonar']['ox'] = lambda self, pos: 0
	self.senses['sonar']['oy'] = lambda self, pos: 0
	self.senses['sonar']['oz'] = lambda self, pos: 0
	self.senses['sonar']['th'] = lambda self, pos: 0
        self.senses['sonar']['arc'] = lambda self, pos: 0
        
	self.senses['sonar']['type'] = lambda self: 'range'
        
        console.log(console.INFO,'simple sense driver loaded')

class SimpleControlDriver(driver.Driver):
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.controls['move'] = lambda self, val1, val2: 0 
        self.controls['translate'] = lambda self, pos: 0 
        self.controls['rotate'] = lambda self, pos: 0 
        self.controls['update'] = lambda self: 0 
        console.log(console.INFO,'simple control driver loaded')


