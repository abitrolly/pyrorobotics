"""
A PyrobotSimulator world. A room with one obstacle and
a small inner room.

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import TkSimulator, TkPioneer, \
     PioneerFrontSonars, PioneerFrontLightSensors

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((600, 600), (50, 550), 100)  
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 5, 5)
    sim.addBox(0, 4, 1, 5, "blue")
    sim.addBox(2.5, 0, 2.6, 2.5, "green")
    sim.addBox(2.5, 2.5, 3.9, 2.6, "green")
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  .5, 2.5, 0.00,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175))))
    # add some sensors:
    sim.robots[0].addDevice(PioneerFrontSonars())
    return sim
