from pyro.brain.conx import *

def xor(a,b):
    if a and b: return 0
    if not a and not b: return 0
    return 1

def sequentialXorSweeps(n, limit):
    step = 1
    totalErr1 = 0
    totalErr2 = 0
    totalErr3 = 0
    current = int(random.random()*2)
    while step <= limit:
        n.setInputs([[current]])
        next = int(random.random()*2)
        n.setOutputs([[next]])
        (tssError, totalCorrect, totalCount) = n.sweep()
        err1 = tssError
        n.setInputs([[next]])
        result = xor(current,next)
        n.setOutputs([[result]])
        (tssError, totalCorrect, totalCount) = n.sweep()
        err2 = tssError
        n.setInputs([[result]])
        current = int(random.random()*2)
        n.setOutputs([[current]])
        (tssError, totalCorrect, totalCount) = n.sweep()
        err3 = tssError
        if step % n.reportRate == 0:
            print "Epoch: #%6d" % step
        totalErr1 = totalErr1 + err1
        totalErr2 = totalErr2 + err2
        totalErr3 = totalErr3 + err3
        step = step + 1
    print "Only the second error value is predicatable and should be lower"
    print "Total errors  : %.4f %.4f %.4f" % (totalErr1, totalErr2, totalErr3)
    print "Average errors: %.4f %.4f %.4f" \
          % (totalErr1/step, totalErr2/step, totalErr3/step)

    
if __name__ == '__main__':
    print "Sequential XOR modeled after Elman's experiment ..........."
    print "The network will see a random 1 or 0, followed by another"
    print "random 1 or 0, followed by their XOR value.  Therefore only"
    print "the second output is predictable."
    n = SRN()
    n.addSRNLayers(1,2,1)
    n.setEpsilon(0.25)
    n.setMomentum(0.7)
    n.setBatch(0)
    n.setQuickProp(0)
    n.setReportRate(1000)
    sequentialXorSweeps(n, 30000)
    print "Training complete.  Test error again....................."
    n.setLearning(0)
    sequentialXorSweeps(n,1000)
