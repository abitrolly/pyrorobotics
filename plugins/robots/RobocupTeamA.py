# Uses RobocupRobot, a subclass of robot

from pyro.robot.robocup import *

def INIT():
    return RobocupRobot(name = "TeamA", teamMode = 1)
