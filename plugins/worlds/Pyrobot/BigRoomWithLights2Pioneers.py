import os, sys
path = os.environ["PYROBOT"]
spare = ''
while spare == '':
   (path,spare) = os.path.split(path) # peel off pyrobot dir
sys.path.insert(0, path) # add PYROBOT to PYTHON and OS search path
os.environ["PATH"] += ":%s/plugins/simulators" % os.environ["PYROBOT"]
from pyrobot.simulators.pysim import TkSimulator, TkPioneer, RangeSensor, LightSensor
from pyrobot.geometry import PIOVER180

def INIT():
    sim = TkSimulator(30, 586, 13.7) # x offset, y offset, scale
    sim.addBox(0, 0, 40, 40)
    sim.addLight(5, 5, 1)
    sim.addLight(5, 30, 1)
    sim.addWall(0, 20, 10, 10)
    sim.addRobot(60000, TkPioneer("Red Pioneer", 15, 30, 0.0, ((.75, .75, -.75, -.75), (.5, -.5, -.5, .5))))
    sim.addRobot(60001, TkPioneer("Blue Pioneer", 30, 35, 1.5, ((.75, .75, -.75, -.75), (.5, -.5, -.5, .5)), color="blue"))
    sonar = RangeSensor("sonar", geometry = (( 0.20, 0.50, 90 * PIOVER180),
                                             ( 0.30, 0.40, 65 * PIOVER180),
                                             ( 0.40, 0.30, 40 * PIOVER180),
                                             ( 0.50, 0.20, 15 * PIOVER180),
                                             ( 0.50,-0.20,-15 * PIOVER180),
                                             ( 0.40,-0.30,-40 * PIOVER180),
                                             ( 0.30,-0.40,-65 * PIOVER180),
                                             ( 0.20,-0.50,-90 * PIOVER180)),
                        arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
    sonar.groups = {'all': range(8),
                    'front': (3, 4),
                    'front-left' : (1,2,3),
                    'front-right' : (4, 5, 6),
                    'front-all' : (1,2, 3, 4, 5, 6),
                    'left' : (0,), 
                    'right' : (7,), 
                    'left-front' : (0,), 
                    'right-front' : (7, ),
                    'left-back' : [],
                    'right-back' : [],
                    'back-right' : [],
                    'back-left' : [], 
                    'back' : [],
                    'back-all' : []}
    sim.robots[0].addDevice(sonar)
    sonar = RangeSensor("sonar", geometry = (( 0.20, 0.50, 90 * PIOVER180),
                                             ( 0.30, 0.40, 65 * PIOVER180),
                                             ( 0.40, 0.30, 40 * PIOVER180),
                                             ( 0.50, 0.20, 15 * PIOVER180),
                                             ( 0.50,-0.20,-15 * PIOVER180),
                                             ( 0.40,-0.30,-40 * PIOVER180),
                                             ( 0.30,-0.40,-65 * PIOVER180),
                                             ( 0.20,-0.50,-90 * PIOVER180)),
                        arc = 5 * PIOVER180, maxRange = 8.0, noise = 0.0)
    sonar.groups = {'all': range(8),
                    'front': (3, 4),
                    'front-left' : (1,2,3),
                    'front-right' : (4, 5, 6),
                    'front-all' : (1,2, 3, 4, 5, 6),
                    'left' : (0,), 
                    'right' : (7,), 
                    'left-front' : (0,), 
                    'right-front' : (7, ),
                    'left-back' : [],
                    'right-back' : [],
                    'back-right' : [],
                    'back-left' : [], 
                    'back' : [],
                    'back-all' : []}
    sim.robots[1].addDevice(sonar)
    sim.robots[0].addDevice(LightSensor(((.75,  .5, 0), (.75, -.5, 0)))) # make sure outside of bb!
    sim.robots[1].addDevice(LightSensor(((.75,  .5, 0), (.75, -.5, 0)))) # make sure outside of bb!
    return sim
