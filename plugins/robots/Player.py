from pyro.robot.player import PlayerRobot
from pyro.system.share import ask

# This should work for real and simulated Player-based robots

def INIT():
    retval = ask("Please enter the Player Data",
                 (("Port", "6665"),
                  ("Host", "localhost")))
    if retval["ok"]:
        return PlayerRobot("Player6665",
                           port = int(retval["Port"]),
                           hostname = retval["Host"])
    else:
        raise "Cancelled!"


