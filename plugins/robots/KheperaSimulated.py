# Defines KheperaRobot, a subclass of robot

from pyro.robot.khepera import *

def INIT():
    return KheperaRobot(simulator = 1) 
