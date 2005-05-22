# Defines KheperaRobot, a subclass of robot

from pyrobot.robot.khepera import *

def INIT():
    return KheperaRobot(simulator = 1) 
