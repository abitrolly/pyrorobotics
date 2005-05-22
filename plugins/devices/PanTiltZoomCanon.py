""" This device signals the robot to load its PTZ """

from pyrobot.robot.aria import AriaPTZDevice

def INIT(robot):
    ptz = AriaPTZDevice(robot.dev, "canon")
    return {"ptz": ptz}
