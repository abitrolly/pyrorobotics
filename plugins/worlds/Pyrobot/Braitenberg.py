from pyrobot.simulators.pysim import TkSimulator, TkPioneer, RangeSensor, LightSensor
from pyrobot.geometry import PIOVER180

def INIT():
    sim = TkSimulator(38, 550, 52.627022) # x offset, y offset, scale
    sim.addBox(0, 0, 10, 10)
    sim.addLight(5, 5, 1)
    sim.addRobot(60000, TkPioneer("RedPioneer", 1, 3, -1.5, ((.75, .75, -.75, -.75), (.5, -.5, -.5, .5))))
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
    lights = LightSensor(((.75,  .5, 0), (.75, -.5, 0))) # make sure outside of bb!
    lights.groups = {"front-all": (0, 1),
                    "all": (0, 1),
                    "front": (0, 1),
                    "front-left": (0, ),
                    "front-right": (1, ),
                    'left' : (0,), 
                    'right' : (1,), 
                    'left-front' : (0,), 
                    'right-front' : (1, ),
                    'left-back' : [],
                    'right-back' : [],
                    'back-right' : [],
                    'back-left' : [], 
                    'back' : [],
                    'back-all' : []}
    sim.robots[0].addDevice(lights)
    return sim
