#This is designed for the B21R robot (sonar, 2 cameras, bumpers, laser)

from pyro.robot.player import PlayerRobot

def INIT():
    robot = PlayerRobot("B21R",6665)
    robot.set('robot','type','B21R')
    robot.dev.start('ptz')
    robot.dev.start('laser')
    return robot 

