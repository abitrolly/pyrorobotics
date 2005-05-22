import pyrobot.robot.driver as driver
import pyrobot.gui.console as console
import string
import array
import math

class KheperaSenseDriver(driver.Driver):

    def isStall(self, sc):
        return 0

    def getX(self, sc):
        return 0
    
    def getY(self, sc):
        return 0
    
    def getZ(self, sc):
        return 0
    
    def getTh(self, sc):
        return 0
    
    def getThr(self, sc):
        return 0
    
    def getIRXCoord(self, sc, pos):
        return 0

    def getIRRange(self, sc, pos):
        return 0

    def getIRFlag(self, sc, pos):
        return 0

    def getIRYCoord(self, sc, pos):
        return 0
    
    def sonar_x(self, sc, pos):
        return 0
    
    def sonar_y(self, sc, pos):
        return 0
    
    def sonar_th(self, sc, pos):
        return 0
    
    def __init__(self, machine):
        driver.Driver.__init__(self)

        self.senses['robot'] = {}
        
	# robot senses (all are functions):
        self.senses['robot']['stall'] = self.isStall
        self.senses['robot']['x'] = self.getX
        self.senses['robot']['y'] = self.getY
        self.senses['robot']['z'] = self.getZ
        self.senses['robot']['th'] = self.getTh # in degrees
        self.senses['robot']['thr'] = self.getThr # in radians
	self.senses['robot']['type'] = lambda self: 'khepera'

	self.senses['robot']['name'] = lambda self: 'khepera-1'

	self.senses['ir'] = {}
	self.senses['ir']['count'] = lambda self: 8

	# location of sensors' hits:
	self.senses['ir']['x'] = self.getIRXCoord
	self.senses['ir']['y'] = self.getIRYCoord
	self.senses['ir']['z'] = lambda self, pos: 0.25
	self.senses['ir']['value'] = self.getIRRange
	self.senses['ir']['flag'] = self.getIRFlag

	# location of origin of sensors:
        self.senses['ir']['ox'] = self.sonar_x
	self.senses['ir']['oy'] = self.sonar_y
	self.senses['ir']['oz'] = lambda self, pos: 0.25 # meters
	self.senses['ir']['th'] = self.sonar_th
        # in radians:
        self.senses['ir']['arc'] = lambda self, pos, \
                                      x = (5 * math.pi / 180) : x
	self.senses['ir']['type'] = lambda self: 'range'
        
        console.log(console.INFO,'khepera sense drivers loaded')

class KheperaControlDriver(driver.Driver):
    
    def move(self, sc, trans, rotate):
        pass
    
    def translate(self, sc, value):
        pass
    
    def rotate(self, sc, value):
        pass
    
    def localize(self):
        pass
    
    def __init__(self, machine):
        driver.Driver.__init__(self)
        self.controls['move'] = self.move
        self.controls['translate'] = self.translate
        self.controls['rotate'] = self.rotate
        # self.controls['update'] = self.update # Higher up!
        self.controls['localize'] = self.localize

        console.log(console.INFO,'khepera control drivers loaded')

