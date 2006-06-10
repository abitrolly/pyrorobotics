"""
Replicating ALife Nolfi 2006.
"""

from pyrobot.simulators.pysim import *
from pyrobot.geometry import distance
import time, random, math

# In pixels, (width, height), (offset x, offset y), scale:
sim = TkSimulator((441,434), (22,420), 40.357554, run=0)  
# x1, y1, x2, y2 in meters:
sim.addBox(0, 0, 10, 10)
# (x, y) meters, brightness usually 1 (1 meter radius):
sim.addLight(2, 2, 1)
sim.addLight(7, 7, 1)
# port, name, x, y, th, bounding Xs, bounding Ys, color
# (optional TK color name):
sim.addRobot(60000, TkPioneer("RedPioneer",
                              1, 1, -0.86,
                              ((.225, .225, -.225, -.225),
                               (.15, -.15, -.15, .15)),
                            "red"))
sim.addRobot(60001, TkPioneer("BluePioneer",
                             8, 8, -0.86,
                             ((.225, .225, -.225, -.225),
                              (.15, -.15, -.15, .15)),
                            "blue"))
sim.addRobot(60002, TkPioneer("GreenPioneer",
                              5, 1, -0.86,
                              ((.225, .225, -.225, -.225),
                               (.15, -.15, -.15, .15)),
                            "green"))
sim.addRobot(60003, TkPioneer("YellowPioneer",
                             8, 1, -0.86,
                             ((.225, .225, -.225, -.225),
                              (.15, -.15, -.15, .15)),
                            "yellow"))
# add some sensors:
for robot in sim.robots:
    robot.addDevice(PioneerFrontSonars())
    robot.addDevice(PioneerFrontLightSensors())

# client side:
from pyrobot.robot.symbolic import Simbot
from pyrobot.engine import Engine
clients = [Simbot(sim, ["localhost", 60000], 0),
           Simbot(sim, ["localhost", 60001], 1),
           Simbot(sim, ["localhost", 60002], 2),
           Simbot(sim, ["localhost", 60003], 3)]

engines = [Engine(), Engine(), Engine(), Engine()]

for n in range(4):
    engines[n].robot = clients[n]
    engines[n].loadBrain("NNBrain")

if 0:
    steps = 500
    start = time.time()
    for i in range(steps):
        for client in clients:
            client.update()
        for engine in engines:
            engine.brain.step()
        sim.step(run=0)
    stop = time.time()
    print "Average steps per second:", float(steps)/ (stop - start)

def myquit():
    for e in engines:
        e.shutdown()
import sys
sys.exitfunc = myquit

sim.redraw()

from pyrobot.geometry import Polar
def quadSound(myLoc, q, lastS, location):
    """
    Computes the sound heard for quad[q].
      |0|
    |3| |1|
      |2|
    myLoc:    (x, y, t) of current robot; t where 0 is up
    q:        which quad?
    lastS:    last sound made by robots
    location: (x, y, t) of robots; t where 0 is up
    """
    angleRange = [(0, 1), (0, 1), (0, 1), (0, 1)] # FIX: need angles of quads
    closest = (10000, 0) # dist, freq
    for n in range(len(location)):
        loc = location[n]
        if loc != myLoc:
            # distance between robots:
            dist = distance(myLoc[0], myLoc[1], loc[0], loc[1])
            # global angle from one robot to another:
            angle = Polar(loc[0] - myLoc[0], loc[1] - myLoc[1], bIsPolar=0) # 0 to right (geometry)
            # FIX: compute angle from myLoc[2]
            if angleRange[0] < angle < angleRange[1]: # if in right quad
                if dist < closest[0]: # if shorter than previous
                    closest = dist, lastS[n] # new closest
    return closest[1]

from pyrobot.brain.ga import *
import operator
g = engines[0].brain.net.arrayify()
class NNGA(GA):
    def fitnessFunction(self, genePos):
        for n in range(len(engines)):
            engine = engines[n]
            engine.brain.net.unArrayify(self.pop.individuals[genePos].genotype)
            # fix to make sure they don't overlap
            x, y, t = 1 + random.random() * 7, 1 + random.random() * 7, random.random() * math.pi
            engine.robot.simulation[0].setPose(n, x, y, t)
        fitness = [0.0] * 4
        seconds = 10 # how much simulated real time to run?
        s = [0] * 4
        lastS = [0] * 4
        location = [(0, 0, 0) for v in range(4)]
        for i in range(seconds * (1000/sim.timeslice)): # simulated seconds (10/sec)
            # move the robots
            for n in range(4): # number of robots
                engine = engines[n]
                engine.robot.update()
                # compute quad for this robot
                quad = [0] * 4
                myLoc = engine.robot.simulation[0].getPose(n)
                for q in range(4):
                    quad[q] = quadSound(myLoc, q, lastS, location)
                # compute output for each robot
                oTrans, oRotate, s[n] = engine.brain.propagate(quad)
                location[n] = engine.robot.simulation[0].getPose(n)
                # then move it
                engine.brain.step(oTrans, oRotate)
                lastS = [v for v in s]
            sim.step(run=0)
            sim.update_idletasks()
            closeTo = [0, 0] # how many robots are close to which lights?
            for n in range(len(engines)):
                engine = engines[n]
                # only allow two per feeding area
                reading = max(engine.robot.light[0].values())
                if reading >= 1.0:
                    # get global coords
                    x, y, t = engine.robot.simulation[0].getPose(n)
                    # which light?
                    dists = [distance(light.x, light.y, x, y) for light in sim.lights]
                    if dists[0] < dists[1]:
                        closeTo[0] += 1
                    else:
                        closeTo[1] += 1
            for n in range(len(engines)):
                for total in closeTo:
                    if total <= 2:
                        fitness[n] += .25 * total
                    else:
                        fitness[n] -= 1.0
        fit = reduce(operator.add, fitness)
        fit = max(0.01, fit)
        print "Fitness %d: %.5f" % (genePos, fit)
        return fit
    def isDone(self):
        return 0
ga = NNGA(Population(3, Gene, size=len(g), verbose=1,
                     min=-1, max=1, maxStep = 1,
                     elitePercent = .2),
          mutationRate=0.05, crossoverRate=0.6,
          maxGeneration=2, verbose=1)
ga.evolve()

