""" This device signals the robot to load its PTZ """

from pyro.robot.aria import AriaPTZService

def INIT(robot):
    ptz = AriaPTZService(robot.dev, "canon")
    # init has to be done separate, because the constructor
    # is called before robot connection (to supply "supports")
    # so, we need to init now, after connection to robot is made:
    ptz.init()
    return {"ptz": ptz }
