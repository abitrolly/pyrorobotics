# Uses RobocupRobot, a subclass of robot

from pyro.robot.robocup import *

def INIT():
    # Make a team of 11 robots:
    list = [0] * 11
    for x in range(11):
        list[x] = RobocupRobot(name = "TeamB", goalie = (x == 0))
    # store the list on the first one
    list[0].team = list
    # put the goalie in the box
    list[0].set("devices/truth0/pose", (-50, 0))
    # return the first one
    return list[0]
