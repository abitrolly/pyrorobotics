
from pyro.robot.sensor import *

class AriaRangeSensor(RangeSensor):
    """ For general Aria-sensors """
    def __init__(self):
        RangeSensor.__init__(self)
    def getType(self):
        return "range"

class AriaLaserRangeSensor(AriaRangeSensor):
    """ A Laser sensor for the Aria-class robots """
    def __init__(self):
        AriaRangeSensor.__init__(self)
    def getCount(self):
        return 180
    def getMaxValue(self):
        return 15.0
    def update(self):
        pass # handled by robot

class AriaSonar(AriaRangeSensor):
    """ A Sonar sensor for the Aria-class robots """

    
if __name__ == "__main__":
    s = AriaLaserRangeSensor()
    s.setRobotDiameter(10)
    s.setMaxValue(25)
    s.check()
