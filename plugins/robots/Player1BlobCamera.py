from pyro.robot.player import PlayerRobot
from pyro.camera.blob import BlobCamera

# This should work for real and simulated Aria-based robots

def INIT():
	robot = PlayerRobot("Player1", 6665)
	robot.camera = BlobCamera(robot)
	robot.camera.makeWindow()
	return robot


