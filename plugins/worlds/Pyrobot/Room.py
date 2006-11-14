"""
A PyrobotSimulator world. A large room with a robot

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""

from pyrobot.simulators.pysim import *

def INIT():
    # (width, height), (offset x, offset y), scale:
    sim = TkSimulator((357,486), (38,397), 57.838547)
    # x1, y1, x2, y2 in meters:
    sim.addBox(0, 0, 5, 5)
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    # (optional TK color name):
    sim.addRobot(60000, TkPioneer("RedPioneer",
                                  2.48, 0.82, 6.28,
                                  ((.225, .225, -.225, -.225),
                                   (.175, -.175, -.175, .175)),
                                  "red"))
    # add some sensors:
    sim.robots[0].addDevice(Pioneer16Sonars())
    return sim
