""" This service loads a Global Perceptual View """

from pyro.map.gps import GPS
from pyro.robot.service import Service
import pyro.system.share as share

class GPSService(GPS, Service):
    def __init__(self, robot, lps, *args, **kwargs):
        self.robot = robot
        self.lps = lps
        Service.__init__(self, "GPS Service", 1) # visible = 1
        GPS.__init__(self, *args, **kwargs)
    
    def makeWindow(self):
        pass

    def updateWindow(self):
        self.redraw()

    def getServiceData(self):
        return self.grid

    def getServiceState(self):
        return self.state

    def updateService(self):
        self.updateFromLPS(self.lps, self.robot)

def INIT(robot):
    if "GlobalPerceptualView" in robot.getServices():
        print "Service is already running: GlobalPerceptualView"
        return {}
    if "LocalPerceptualView" in robot.getServices():
        print "Service is already running: LocalPerceptualView"
    else:
        robot.startService("LocalPerceptualView")
    lps = robot.getService("LocalPerceptualView")
    units = robot.get('range', 'units')
    robot.set('range', 'units', 'MM')
    rangeMaxMM = robot.get('range', 'maxvalue')
    sizeMM = rangeMaxMM * 3 + robot.get('self', 'radius')
    # Reset our unit of measure
    robot.set('range', 'units', units)
    gps = GPSService(robot, lps, share.gui, maxrange=rangeMaxMM, cols=500, rows=500,
                     heightMM = sizeMM * 10, widthMM = sizeMM * 10)
    return {"GlobalPerceptualView": gps}
