# Uses KheperaRobot, a subclass of robot, for the Hemisson

#import termios
from pyro.robot.khepera import *

def INIT():
    # For serial connected Hemisson:
    #return KheperaRobot(port = "/dev/ttyS0", # "/dev/ttyUB0",
    #                    rate = termios.B115200,
    #                    subtype = "Hemisson")
    return KheperaRobot(port = "/dev/ttyUB0",
                        rate = 115200, # 38400
                        subtype = "Hemisson")
