# Defines SaphiraRobot, a subclass of robot for older Pioneer Robots

from pyro.robot.saphira import *
#from pyro.camera.BT848 import BT848Camera

class Pioneer2AT(SaphiraRobot):
    def __init__(self): 
        SaphiraRobot.__init__(self, "Pioneer2AT", 0)
        # 0 makes it a real robot
	#self.camera = BT848Camera(new_CameraMover())

def INIT():
    return Pioneer2AT()
