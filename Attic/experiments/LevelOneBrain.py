from pyro.brain import Brain
from pyro.brain.conx import *
import time
import random
import os

# change the directories before you run!
currentDirectory = '/local/stober/dill/'
currentExperiment = 'LevelOne/'
currentBrain = '~/pyro/experiments/LevelOneBrain.py'

def saveListToFile(ls, file): 
    """Nice format for lists."""
    for i in range(len(ls)): 
        file.write(str(ls[i]) + " ") 
    file.write("\n")
    file.flush()

def dzip(keys, values):
    """Create a dictionary out of a key list and value list."""
    d = {}
    for v in zip(keys, values):
        d[v[0]] = v[1]
    return d

class LevelOneBrain(Brain):
    """
    A brain to implement the level one architecture discussed summer
    2003. Some aspects yet to be implemented at this level include an
    sort of feature extraction device, including some form of level
    one governor for the prediction level network. Also, vision needs
    to be included.
    """
    def setup(self, **args):
        # sensors we hope to process
        self.modality = dzip(args['modality'], args['sizes'])

        # file IO        
        self.path = currentDirectory + currentExperiment
        if(os.path.isfile(self.path + "exp.lock")):
            raise "Lock error!"
        else:
            try:
                os.mkdir(self.path)
            except:
                pass
            lock = open(self.path + "exp.lock", "w")
            lock.write("This file locks the experiment directory to" + \
                       "prevent overwriting experimental data.")
            lock.close()
            # archive brain for future reference
            os.system("cp " + currentBrain + " " + self.path + "archive.py")
            self.netInfo = open(self.path + 'nn.dat', 'w')
            self.file = {}
            
        # initialize all the modalities here
        self.initModality()

        # network
        self.initNetwork()

        # brain params
        self.sleepTime = 0.1
        self.stopTime = 1000
        self.motors = [0.0, 0.0]

        # dump inputs and targets for SRN here
        self.previous = {}

        # intialize first inputs
        self.initPrevious()
        
    def scaleSensors(self, val):
        """From Robots (or anything) to [0, 1]"""
        return (val / self.maxValue)     

    def scaleMotors(self, val):
        return (val + 1) / 2

    def initPrevious(self):
        # hack
        motorSize = self.modality['motor']
        del self.modality['motor']

        # initialize the dict of previous values
        for key in self.modality:
            self.previous[key] = self.getModality(key)

        # hack
        self.modality['motor'] = motorSize
        
    def initModality(self):
        """ Overwrite this function as necessary for particular modalities. """
        for item in self.modality.items():
            if item[0] == 'bumper':
                self.getRobot().startService('bumper')
                self.file['bumper'] = open(self.path + 'bumper.dat', 'w')
            elif item[0] == 'sonar':
                self.getRobot().set('range', 'units', 'ROBOTS')
                self.sensorCount = self.getRobot().get('range', 'count')
                self.maxValue = self.getRobot().get('range', 'maxvalue')
                self.file['bumper'] = open(self.path + 'sonar.dat', 'w')
            elif item[0] == 'motor':
                self.file['motor'] = open(self.path + 'motor.dat', 'w')
            else:
                raise "Unkown modality"

    def getModality(self, name, motors = 1):
        """ Overwrite this function as necessary for particular modalities. """
        if name == 'motor':
            return map(self.scaleMotors, self.motors)
        elif name == 'bumper':
            if motors:
                return list(self.getRobot().getService('bumper').getServiceData())\
                       + map(self.scaleMotors, self.motors)
            else:
                return list(self.getRobot().getService('bumper').getServiceData())
        elif name == 'sonar':
            if motors:
                return map(self.scaleSensors, \
                           self.getRobot().get('sonar', 'value', 'all')) + \
                           map(self.scaleMotors, self.motors)
            else:
                return map(self.scaleSensors, \
                           self.getRobot().get('sonar', 'value', 'all'))
        else:
            raise "Unkown modality"

    def getRawModality(self, name):
        if name == 'motor':
            return self.motors
        elif name == 'bumper':
            return self.getRobot().getService('bumper').getServiceData()
        elif name == 'sonar':
            return self.getRobot.get('sonar', 'value', 'all')

    def recordModalities(self):
        """ Record modalities to files. """
        for key in self.modalities:
            saveListToFile(self.getRawModality(key), self.file[key])
                      
    def networkStep(self):
        """ Do a single step of the networks. """
        # hack
        motorSize = self.modality['motor']
        del self.modality['motor']

        prediction = {}

        # step through modal networks
        for key in self.modality.keys():
            net = self.network[key]
            prediction[key + 'Input'] = \
                           net.getLayer('hidden').getActivationsList()
            self.network[key].step(input = self.previous[key], \
                                   output = self.getModality(key, 0))
            prediction[key + 'Output'] = \
                           net.getLayer('hidden').getActivationsList()
        self.previous[key] = self.getModality(key)

        # step through prediction level network
        apply(self.network['prediction'].step, [], prediction)
        
        # hack
        self.modality['motor'] = motorSize
        
    def initNetwork(self):
        """
        Tries to create Level One as multiple networks.
        """
        self.network = {}

        # hack
        motorSize = self.modality['motor']
        del self.modality['motor']
        
        # create modal networks
        for item in self.modality.items():
            self.network[item[0]] = Network()
            self.network[item[0]].addThreeLayers(item[1] + motorSize, \
                                                 max(item[1]/2, 2), item[1])
        # create prediction network
        self.network['prediction'] = SRN()
        totalInputSize = 0
        for item in self.modality.items():
            totalInputSize += max(item[1]/2, 2)
            self.network['prediction'].add(Layer(item[0] + 'Input', \
                                                 max(item[1]/2, 2)))
        self.network['prediction'].addContext(Layer('context',  \
                                                    totalInputSize / 2))
        self.network['prediction'].add(Layer('hidden', totalInputSize / 2))
        for item in self.modality.items():
            self.network['prediction'].add(Layer(item[0] + 'Output', \
                                                 max(item[1]/2, 2)))

        #connect layers of prediction network
        for item in self.modality.items():
            self.network['prediction'].connect(item[0] + 'Input', 'hidden')
        self.network['prediction'].connect('context','hidden')
        for item in self.modality.items():
            self.network['prediction'].connect('hidden', item[0] + 'Output')

        # initialize and verify
        for value in self.network.values():
            value.initialize()
            value.verifyArchitecture()

        # hack
        self.modality['motor'] = motorSize
            
    def controller(self):
        return random.random()*2-1, random.random()*2-1

    def step(self):
        # record how long a single step takes
        startTime = time.time()

        # choose controller
        self.motors = self.controller()

        # move robot
        self.getRobot().move(self.motors[0], self.motors[1])

        # train the network
        self.networkStep()

        # make sure step takes a constant amount of time?
        stepTime = time.time() - startTime
        if self.sleepTime - stepTime > 0:
            time.sleep(self.sleepTime - stepTime)
        

def INIT(engine):
    return LevelOneBrain('LevelOneBrain', engine, \
                         modality = ('sonar', 'bumper', 'motor'), \
                         sizes = (16, 1, 2))

if __name__ == '__main__':
    os.system('pyro -s Stage -w simple.world -r Player2 &')
