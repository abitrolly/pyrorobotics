from pyro.brain.conx import *
import sys
import time

if __name__=='__main__':
    modality = sys.argv[1:]
    file = {}
    network = {}
    dimension = {}
    for name in modality:
        file[name] = open(name + ".dat", "r")
        dimension[name] = int(file[name].readline())
    for name in modality:
        if name == 'wheel':
            continue
        network[name] = Network()
        inputSize = dimension[name]+dimension['wheel']
        hiddenSize = max(inputSize/2, 2)
        print name, dimension[name], inputSize, hiddenSize
        network[name].addThreeLayers(inputSize, hiddenSize, dimension[name])
    input = {}
    target = {}
    for name in modality:
        input[name] = map(float, file[name].readline().split())
    for count in range(500-1):
        for name in modality:
            target[name] = map(float, file[name].readline().split())
            if name != 'wheel':
                inputs = input[name]+input['wheel']
                targets = target[name]
                #print name, "inputs:", inputs
                #print name, "targets:", targets
                error, correct, total = \
                       network[name].step(input=inputs, output=targets)
                print count, name, error, correct, total
        for name in modality:
            input[name] = target[name]
    for name in modality:
        if name != 'wheel':
            network[name].saveWeightsToFile(name + ".wts")
        

                             
        
    
