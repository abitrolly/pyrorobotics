# Uses KheperaRobot, a subclass of robot, for the Hemisson

#import termios
from pyrobot.robot.khepera import *

def INIT():
    # For serial connected Hemisson:
    return KheperaRobot(port = "/dev/ttyUB0",
                        rate = 115200,
                        subtype = "Hemisson")
