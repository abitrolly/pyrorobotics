import pyro.robot.saphira as saphira

class PioneerSimulated(saphira.SaphiraRobot):
	def __init__(self):
		saphira.SaphiraRobot.__init__(self, "PioneerSimulated", 1)

def INIT():
	return PioneerSimulated()



