from pyro.brain.VisConx.VisRobotConx import *
import sys
import time

STOP_ERROR = {'bumper' : 32, 'sonar': 50}

def runEpoch():
    count = 1
    terror = {}
    for name in modality:
        terror[name] = 0.0
    while 1:
        #print "Pattern #", count
        for name in modality:
            target[name] = map(float, file[name].readline().split())
            # if end of file, re-open files
            if not target[name]:
                #print "Done!"
                openFiles()
                return terror
            if name != 'wheel' and not done[name]:
                inputs = input[name]+input['wheel']
                targets = target[name]
                error, correct, total = \
                       network[name].step(input=inputs, output=targets)
                terror[name] += error
                #print name, error, correct, total
        for name in modality:
            input[name] = target[name]
        count += 1

def openFiles():
    for name in modality:
        file[name] = open(name + ".dat", "r")
        dimension[name] = int(file[name].readline())
    for name in modality:
        input[name] = map(float, file[name].readline().split())


def runNetworks():
    for name in modality:
        done[name] = 0
    done["wheel"] = 1
    openFiles()
    for name in modality:
        if name == 'wheel':
            continue
        network[name] = VisRobotNetwork()
        inputSize = dimension[name]+dimension['wheel']
        hiddenSize = max(inputSize/2, 2)
        print "Building network:", name, inputSize, hiddenSize, dimension[name]
        network[name].addThreeLayers(inputSize, hiddenSize, dimension[name])

    epoch = 1
    while not reduce( lambda a,b: a and b, done.values() ):
        terror = runEpoch()
        for name in modality:
            if name != 'wheel':
                if terror[name] < STOP_ERROR[name]:
                    done[name] = 1
        print "#%d " % epoch,
        for name in modality:
            print "%s = %f " % (name, terror[name]),
        print
        epoch += 1
    # save all the weights
    for name in modality:
        if name != 'wheel':
            network[name].saveWeightsToFile(name + ".wts")
        
modality = sys.argv[1:]
print "Running with modalities:", modality
input = {}
target = {}
file = {}
network = {}
dimension = {}
done = {}
runNetworks()
