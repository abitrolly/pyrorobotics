from pyro.robot.player import PlayerRobot

def INIT():
	robot = PlayerRobot("Player1", 6665)
	robot.startService("BlobCamera")
	robot.camera = robot.getService("BlobCamera")
	robot.camera.makeWindow()
	return robot


