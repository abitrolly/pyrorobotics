#This is designed for the B21R robot (sonar, 2 cameras, bumpers, laser)

from pyro.robot.player import PlayerRobot

class B21RSimulated(PlayerRobot):

    def __init__(self, name, port):
        PlayerRobot.__init__(self, name, port)
        self.set('robot','type','B21R')
        self.dev.start('ptz')
        self.dev.start('laser')
        self.laserNoise = 0.01
        
        self.senses['laser'] = {}
        self.laserGeometry = self.dev.get_laser_geometry()
        # ((0, 0, 0), (154, 154))
        self.senses['laser']['count'] = lambda dev: 180
        self.senses['laser']['type'] = lambda self: 'range'
        self.senses['laser']['maxvalue'] = self.getLaserMaxRange
        self.senses['laser']['units'] = lambda self: "ROBOTS"
        self.senses['laser']['all'] =   self.getLaserRangeAll
        
        # location of sensors' hits:
        self.senses['laser']['x'] = self.getLaserXCoord
        self.senses['laser']['y'] = self.getLaserYCoord
        self.senses['laser']['z'] = lambda self, pos: 0.03
        self.senses['laser']['value'] = self.getLaserRange
        self.senses['laser']['flag'] = self.getLaserFlag
        
        # location of origin of sensors:
        self.senses['laser']['ox'] = self.laser_ox
        self.senses['laser']['oy'] = self.laser_oy
        self.senses['laser']['oz'] = lambda self, pos: 0.03 # meters
        self.senses['laser']['th'] = self.laser_th
        # in radians:
        self.senses['laser']['arc'] = lambda self, pos : 1
        
        self.senses['range'] = self.senses['laser']

    def getLaserMaxRange(self, dev):
        return 8.0
    def getLaserRangeAll(self, dev):
        return [self.getLaserRange(self.dev, x) for x in range(180)]
    def getLaserXCoord(self, dev):
        pass
    def getLaserYCoord(self, dev):
        pass
    def getLaserRange(self, dev, pos):
        return self.rawToUnits(dev, self.dev.laser[0][1][pos],
                               'laser',
                               self.laserNoise)
        
    def getLaserFlag(self, dev, pos):
        pass
    def laser_ox(self, dev, pos):
        pass
    def laser_oy(self, dev, pos):
        pass
    def laser_th(self, dev, pos):
        pass
        

def INIT():
    return B21RSimulated("B21R",6665)

