# Uses KheperaRobot, a subclass of robot, for the Hemisson

import termios
from pyro.robot.khepera import *

def INIT():
    return KheperaRobot(port = "/dev/ttyUB0",
                        rate = termios.B115200)
