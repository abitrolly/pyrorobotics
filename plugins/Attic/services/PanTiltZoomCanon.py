""" This device signals the robot to load its PTZ """

from pyro.robot.aria import AriaPTZService

def INIT(robot):
    return {"ptz": AriaPTZService(robot.dev, "canon")}
