# Defines SaphiraRobot, a subclass of robot

from pyro.robot.saphira import *

class Pioneer2AT(SaphiraRobot):
    def __init__(self): 
        SaphiraRobot.__init__(self, "Pioneer2AT", 0)
        # 0 makes it a real robot

def INIT():
    return Pioneer2AT()
