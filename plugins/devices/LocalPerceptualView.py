""" This service loads a Local Perceptual View """

from pyro.map.lps import LPS
from pyro.robot.service import Service
import pyro.system.share as share

class LPSService(LPS, Service):
    def __init__(self, robot, *args, **kwargs):
        self.robot = robot
        Service.__init__(self, "LPS Service", 1) # visible = 1
        LPS.__init__(self, *args, **kwargs)
    
    def makeWindow(self):
        pass

    def updateWindow(self):
        self.redraw()

    def getServiceData(self):
        return self.grid

    def getServiceState(self):
        return self.state

    def updateService(self):
        self.reset()
        self.sensorHits(self.robot, 'range')

def INIT(robot):
    if "LocalPerceptualView" in robot.getServices():
        print "Service is already running: LocalPerceptualView"
        return {}
    units = robot.get('range', 'units')
    robot.set('range', 'units', 'MM')
    rangeMaxMM = robot.get('range', 'maxvalue')
    sizeMM = rangeMaxMM * 3 + robot.get('self', 'radius')
    # Reset our unit of measure
    robot.set('range', 'units', units)
    lps = LPSService(robot, share.gui, 20, 20, widthMM = sizeMM, heightMM = sizeMM)
    return {"view": lps}
