from pyrobot.robot.symbolic import TCPRobot
from pyrobot.system.share import ask

def INIT():
	retval = ask("Please enter the Simulator Connection Data",
		     (("Port", "60000"),
		      ("Host", "localhost")))
	if retval["ok"]:
		return TCPRobot(retval["Host"], int(retval["Port"]))
	else:
		raise "Cancelled!"

