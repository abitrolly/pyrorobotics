""" This device signals the robot to load its PTZ """

from pyro.robot.aria import AriaPTZService

def INIT(robot):
    ptz = AriaPTZService(robot.dev, "sony")
    return {"ptz": ptz}
