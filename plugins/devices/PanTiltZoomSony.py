""" This device signals the robot to load its PTZ """

from pyro.robot.aria import AriaPTZDevice

def INIT(robot):
    ptz = AriaPTZDevice(robot.dev, "sony")
    return {"ptz": ptz}
