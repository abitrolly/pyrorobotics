# A Simple Service

from pyro.robot.device import Device

def INIT(robot):
    return {"simple": Device()}
