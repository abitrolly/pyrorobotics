# Aibo robot

from pyro.robot.aibo import AiboRobot
from pyro.system.share import ask

def INIT():
    # replace "aibo" with your dog's IP or DNS name
    dict = ask("What Aibo do you want to connect onto?",
               [("AIBO name or IP", "")])
    return AiboRobot(dict["AIBO name or IP"]) 
