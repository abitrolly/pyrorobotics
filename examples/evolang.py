"""
evolang.py for exploring ideas from:
Emergence of Communication in Teams of Embodied and Situated
Agents, by Davide Marocco and Stefano Nolfi, ALife 2006.

Author: Doug Blank
        Bryn Mawr College
Date:   March 2008

For use with PyroRobotics.org
"""

############################################################
# First, let's build a simulated world:
############################################################

from pyrobot.simulators.pysim import *
from pyrobot.geometry import distance, Polar
from pyrobot.tools.sound import SoundDevice
from pyrobot.brain.ga import *
from pyrobot.robot.symbolic import Simbot
from pyrobot.engine import Engine
import sys, time, random, math

# Defaults:
SimulatorClass, PioneerClass = TkSimulator, TkPioneer
robotCount = 4
automaticRestart = False
playSound = False
playRobot = 0
sd = "/dev/dsp"
startEvolving = False
i = 1
while i < len(sys.argv):
    if sys.argv[i] == "-h":
        print "python evolang.py command line:"
        print 
        print "   -g 2d|3d|none  (graphics)"
        print "   -n N           (robot count)"
        print "   -a             (automatic restart)"
        print "   -e             (start evolving)"
        print "   -p /dev/dsp    (to play sounds)"
        print "   -r M           (which robot to play sound, 0-N)"
        print
        print " CONTROL+c to stop at next end of generation"
        print " CONTROL+c CONTROL+c to stop now"
        sys.exit()
    if sys.argv[i] == "-g":
        i += 1
        simType = sys.argv[i]
        if simType == "2d":
            SimulatorClass, PioneerClass = TkSimulator, TkPioneer
        elif simType == "none":
            SimulatorClass, PioneerClass = Simulator, Pioneer
        elif simType == "3d":
            from pyrobot.simulators.pysim3d import Tk3DSimulator
            SimulatorClass, PioneerClass = Tk3DSimulator, TkPioneer
        else:
            raise AttributeError("unknown graphics mode: '%s'" % simType)
    elif sys.argv[i] == "-n":
        i += 1
        robotCount = int(sys.argv[i])
    elif sys.argv[i] == "-a":
        automaticRestart = True
    elif sys.argv[i] == "-e":
        startEvolving = True
    elif sys.argv[i] == "-p":
        i += 1 
        sd = SoundDevice(sys.argv[i])
        playSound = True
    elif sys.argv[i] == "-r":
        i += 1
        playRobot = int(sys.argv[i])
    i += 1

# Define the world:
# In pixels, (width, height), (offset x, offset y), scale:
sim = SimulatorClass((441,434), (22,420), 40.357554, run=0)  
# Add a bounding box:
# x1, y1, x2, y2 in meters:
sim.addBox(0, 0, 10, 10)
# Add a couple of light sources:
# (x, y) meters, brightness usually 1 (1 meter radius):
sim.addLight(2, 2, 1)
sim.addLight(7, 7, 1)

# Robot colors; make sure you have enough for robotCount:
colors = ["red", "blue", "green", "purple", "pink", "orange", "white"]

for i in range(robotCount):
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    sim.addRobot(60000 + i, PioneerClass("Pioneer%d" % i,
                                         1, 1, -0.86,
                                         ((.225, .225, -.225, -.225),
                                          (.15, -.15, -.15, .15)),
                                         colors[i]))
    robot = sim.robots[-1] # last one
    robot.addDevice(PioneerFrontSonars())
    robot.addDevice(PioneerFrontLightSensors())

############################################################
# Now, make some connections to the sim robots
############################################################

# client side:
clients = [Simbot(sim, ["localhost", 60000 + n], n)  for n in range(robotCount)]
# server side:
engines = [Engine() for n in range(robotCount)]
for n in range(robotCount):
    engines[n].robot = clients[n]
    clients[n].light[0].noise = 0.0
    clients[n].sonar[0].noise = 0.0
    engines[n].loadBrain("NNBrain")
sim.redraw()

############################################################
# Define some functions for hearing support
############################################################

def quadNum(myangle, angle):
    """
    Given angle, return quad number
      |0|
    |3| |1|
      |2|
    """
    diff = angle - myangle
    if diff >= 0:
        if diff < math.pi/4:
            return 0
        elif diff < math.pi/4 + math.pi/2:
            return 3
        elif diff < math.pi:
            return 2
        else:
            return 1
    else:
        if diff > -math.pi/4:
            return 0
        elif diff > -math.pi/4 - math.pi/2:
            return 1
        elif diff > -math.pi:
            return 2
        else:
            return 3

def quadTest(robot = 0):
    location = [0] * robotCount
    for n in range(robotCount):
        location[n] = engines[0].robot.simulation[0].getPose(n)
    myLoc = location[robot]
    return quadSound(myLoc, range(robotCount), location)

def quadSound(myLoc, lastS, location):
    """
    Computes the sound heard for all quads.
    myLoc:    (x, y, t) of current robot; t where 0 is up
    lastS:    last sound made by robots
    location: (x, y, t) of robots; t where 0 is up
    """
    closest = [(10000,0.5), (10000,0.5), (10000,0.5), (10000,0.5)] # dist, freq
    for n in range(len(location)):
        loc = location[n]
        if loc != myLoc:
            # distance between robots:
            dist = distance(myLoc[0], myLoc[1], loc[0], loc[1])
            # global angle from one robot to another:
            # 0 to right, neg down (geometry-style)
            angle = Polar(loc[0] - myLoc[0], loc[1] - myLoc[1], bIsPolar=0) 
            angle = angle.t # get theta
            if angle < 0:
                angle = math.pi + (math.pi + angle) # 0 to 2pi
            angle = (angle - math.pi/2) % (math.pi * 2)
            q = quadNum(myLoc[2], angle) 
            #print n, myLoc[2], angle, q
            if dist < closest[q][0]: # if shorter than previous
                closest[q] = dist, lastS[n] # new closest
    return [((v[1] - .5) * 2.0) for v in closest] # return the sounds

############################################################
# Now, let's define the GA:
############################################################

class NNGA(GA):

    def __init__(self, *args, **kwargs):
        self.pre_init = 1
        GA.__init__(self, *args, **kwargs)
        self.pre_init = 0
        self.done = 0
        self.randomizePositions()

    def loadWeights(self, genePos):
        for n in range(len(engines)):
            engine = engines[n]
            engine.brain.net.unArrayify(self.pop.individuals[genePos].genotype)

    def randomizePositions(self):
        positions = [(2, 2), (7, 7)] # position of lights
        for n in range(len(engines)):
            engine = engines[n]
            # Put each robot in a random location:
            x, y, t = (1 + random.random() * 7, 
                       1 + random.random() * 7, 
                       random.random() * math.pi * 2)
            minDistance = min([distance(x, y, x2, y2) for (x2,y2) in positions])
            # make sure they are far enough apart:
            while minDistance < 1:
                x, y, t = (1 + random.random() * 7, 
                           1 + random.random() * 7, 
                           random.random() * math.pi * 2)
                minDistance = min([distance(x, y, x2, y2) for (x2,y2) in positions])
            positions.append( (x,y) )
            engine.robot.simulation[0].setPose(n, x, y, t)
        sim.redraw()

    def fitnessFunction(self, genePos, randomize=1):
        if self.pre_init: # initial generation fitness
            return 1.0
        if genePos >= 0: # -1 is test of last one
            self.loadWeights(genePos)
            if randomize:
                self.randomizePositions()
        sim.resetPaths()
        sim.redraw()
        s = [0] * robotCount # each robot's sound
        lastS = [0] * robotCount # previous sound
        location = [(0, 0, 0) for v in range(robotCount)] 
        fitness = 0.01
        for i in range(self.seconds * (1000/sim.timeslice)): # (10 per sec)
            # ------------------------------------------------
            # First, get the locations:
            # ------------------------------------------------
            for n in range(robotCount): # number of robots
                location[n] = engines[0].robot.simulation[0].getPose(n)
            # ------------------------------------------------
            # Next, compute the move for each robot
            # ------------------------------------------------
            for n in range(robotCount): # number of robots
                engine = engines[n]
                engine.robot.update()
                # compute quad for this robot
                myLoc = location[n]
                quad = quadSound(myLoc, lastS, location)
                # print n, quad
                # compute output for each robot
                oTrans, oRotate, s[n] = engine.brain.propagate(quad)
                # then set the move velocities:
                engine.brain.step(oTrans, oRotate)
                sim.robots[n].say("%.2f Heard: [%s]" % 
                                  (s[n], 
                                   ",".join(map(lambda v: "%.2f" % v, quad))))
            # ------------------------------------------------
            # Save the sounds
            # ------------------------------------------------
            for n in range(robotCount): # number of robots
                lastS = [v for v in s]
            # ------------------------------------------------
            # Make the move:
            # ------------------------------------------------
            sim.step(run=0)
            # update tasks in GUI:
            if isinstance(sim, TkSimulator):
                while sim.tk.dooneevent(2): pass
            # Stop the robots from moving on other steps:
            for n in range(robotCount): # number of robots
                engine = engines[n]
                engine.robot.stop()
            # play a sound, need to have a sound thread running
            if playSound:
                sd.playTone(int(round(engines[playRobot].brain.net["output"].activation[-1], 1) * 2000) + 500, .1) # 500 - 2500
            # ------------------------------------------------
            # Compute fitness
            # ------------------------------------------------
            closeTo = [0, 0] # number of lights
            # how many robots are close to which lights?
            for n in range(len(engines)):
                engine = engines[n]
                # get global coords
                x, y, t = engine.robot.simulation[0].getPose(n)
                # which light?
                dists = [distance(light.x, light.y, x, y) for light in sim.lights]
                if min(dists) <= 1.0:
                    if dists[0] < dists[1]:
                        closeTo[0] += 1
                    else:
                        closeTo[1] += 1
            # ------------------------------------------------
            # Finally, compute the fitness
            # ------------------------------------------------
            for total in closeTo:
                fitness += .25 * total
                # only allow N per feeding area
                if total > 2:
                    fitness -= 1.0 * (total - 2)
                fitness = max(0.01, fitness)
            #print "   ", closeTo, fitness,
            #raw_input(" press [ENTER]")
        print "Fitness %d: %.5f" % (genePos, fitness)
        return fitness
    def setup(self, **args):
        if args.has_key('seconds'):
            self.seconds = args['seconds']
        else:
            # default value
            self.seconds = 20 # how much simulated seconds to run
    def isDone(self):
        if self.generation % 10 == 0:
            self.saveGenesToFile("gen-%05d.pop" % self.generation)
        return self.done

class Experiment:
    def __init__(self, seconds, popsize, maxgen):
        g = engines[0].brain.net.arrayify()
        self.ga = NNGA(Population(popsize, Gene, size=len(g), verbose=1,
                                  imin=-1, imax=1, min=-50, max=50, maxStep = 1,
                                  elitePercent = .20),
                       mutationRate=0.02, crossoverRate=0.6,
                       maxGeneration=maxgen, verbose=1, seconds=seconds)
    def evolve(self, cont=0):
        self.ga.done = 0
        self.ga.evolve(cont)
    def stop(self):
        for n in range(robotCount):
            engines[n].robot.stop()
    def saveBest(self, filename):
        net = engines[0].brain.net
        net.unArrayify(self.ga.pop.bestMember.genotype)
        net.saveWeightsToFile(filename)
    def loadGenotypes(self, filename):
        engines[0].brain.net.loadWeightsFromFile(filename)
        genotype = engines[0].brain.net.arrayify()
        for p in self.ga.pop:
            for n in range(len(genotype)):
                p.genotype[n] = genotype[n]
    def loadWeights(self, filename):
        for n in range(robotCount):
            engines[n].brain.net.loadWeightsFromFile(filename)
    def test(self, seconds):
        self.ga.seconds = seconds
        return self.ga.fitnessFunction(-1) # -1 testing

def testSpeed(steps=100):
    start = time.time()
    for i in range(steps):
        for client in clients:
            client.update()
        for engine in engines:
            engine.brain.step(1,1)
        sim.step(run=0)
        if isinstance(sim, TkSimulator):
            while sim.tk.dooneevent(2): pass
    stop = time.time()
    print "Average steps per second:", float(steps)/ (stop - start)
    print "%.2f x realtime" % (((float(steps)/ (stop - start)) / 10.0))

# ------------------------------------------------
# Hack to shutdown engine threads, but keep robot:
# ------------------------------------------------
for e in engines:
    temp = e.robot
    e.pleaseStop()
    e.shutdown()
    e.robot = temp

# ----------------------------------
# Code to handle control+c: once to 
# exit at end of generation; twice to 
# abort right now.
# ----------------------------------
def suspend(*args):
    if not e.ga.done: # first time
        print "# ------------------------------------------"
        print "# Setting GA to stop at end of generation..."
        print "# ------------------------------------------"
        e.ga.done = 1
    else:
        print "# ------------------------------------------"
        print "# Stopping..."
        print "# ------------------------------------------"
        raise KeyboardInterrupt
import signal
signal.signal(signal.SIGINT,suspend)

e = Experiment(seconds=20, popsize=50, maxgen=100)
if automaticRestart:
    import glob
    maxI = None
    flist = glob.glob("./gen-*.pop")
    if len(flist) > 0:
        filename = flist[-1]
        e.ga.loadGenesFromFile(filename)
        e.ga.generation = int(filename[6:11])
if startEvolving:
    e.evolve(cont=1)

#e.evolve()
#e.loadWeights("nolfi-100.wts")
#e.loadGenotypes("nolfi-100.wts")
#e.evolve()
#e.saveBest("nolfi-200.wts")
#e.ga.saveGenesToFile("nolfi-20-20-100.pop")

