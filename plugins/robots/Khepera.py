# Defines KheperaRobot, a subclass of robot

from pyro.robot.khepera import *

def INIT():
    return KheperaRobot(port = "/dev/ttyUB0") # 1 makes it simulated
