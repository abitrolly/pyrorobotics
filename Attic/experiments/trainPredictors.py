from pyro.brain.conx import *
import sys
import time

input = {}
target = {}
file = {}
network = {}
dimension = {}

def runEpoch():
    while 1:
        for name in modality:
            target[name] = map(float, file[name].readline().split())
            # if end of file, re-open files
            if target[name]:
                openFiles()
                return
            if name != 'wheel':
                inputs = input[name]+input['wheel']
                targets = target[name]
                error, correct, total = \
                       network[name].step(input=inputs, output=targets)
                print count, name, error, correct, total
        for name in modality:
            input[name] = target[name]

def openFiles():
    for name in modality:
        file[name] = open(name + ".dat", "r")
        dimension[name] = int(file[name].readline())
    for name in modality:
        input[name] = map(float, file[name].readline().split())

if __name__=='__main__':
    modality = sys.argv[1:]
    openFiles()
    for name in modality:
        if name == 'wheel':
            continue
        network[name] = Network()
        inputSize = dimension[name]+dimension['wheel']
        hiddenSize = max(inputSize/2, 2)
        print name, dimension[name], inputSize, hiddenSize
        network[name].addThreeLayers(inputSize, hiddenSize, dimension[name])
    runEpoch()
    # save all the weights
    for name in modality:
        if name != 'wheel':
            network[name].saveWeightsToFile(name + ".wts")
        

                             
        
    
