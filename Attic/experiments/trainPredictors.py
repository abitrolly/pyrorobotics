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
                pred[name + 'Input'] = network[name].getLayer('hidden').getActivations()
                error, correct, total = \
                       network[name].step(input=inputs, output=targets)
                pred[name + 'Output'] = network[name].getLayer('hidden').getActivations()
                terror[name] += error
                #print name, error, correct, total
        apply(netPredict.step, [], pred)
        for name in modality:
            input[name] = target[name]
            if not name == 'wheel':
                pred[name + 'Input'] = pred[name + 'Output']
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
        #network[name] = VisRobotNetwork()
        network[name] = Network()
        inputSize = dimension[name]+dimension['wheel']
        hiddenSize = max(inputSize/2, 2)
        hiddenSizes[name] = hiddenSize
        print "Building network:", name, inputSize, hiddenSize, dimension[name]
        network[name].addThreeLayers(inputSize, hiddenSize, dimension[name])
    # here is the prediction network that sits on top of the modal networks
    print "Building goal directed network:"
    
    #netPredict = SRN()
    totalInputSize = 0
    for item in hiddenSizes.items():
        totalInputSize += item[1]
        netPredict.add(Layer(item[0] + 'Input', item[1]))
    netPredict.addContext(Layer('context', totalInputSize / 2), 'hidden')
    netPredict.add(Layer('hidden', totalInputSize / 2))
    for item in hiddenSizes.items():
        netPredict.add(Layer(item[0] + 'Output', item[1]))
    for key in hiddenSizes.keys():
        netPredict.connect(key + 'Input', 'hidden')
    netPredict.connect('context','hidden')
    for key in hiddenSizes.keys():
        netPredict.connect('hidden', key + 'Output')
    #netPredict.display()
        
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
pred = {}
netPredict = VisRobotSRN()
file = {}
network = {}
dimension = {}
done = {}
hiddenSizes = {}
runNetworks()
