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
    # Init context 
    n.getLayer('context').copyActivations([.5] * n.getLayer('context').size)
    while step <= limit:
        #n.setInputs([[current]])
        n.getLayer('input').copyActivations( [current] )
        next = int(random.random()*2)
        #n.setOutputs([[next]])
        n.getLayer('output').copyTarget( [next] )
        (tssError, totalCorrect, totalCount) = n.step()
        err1 = tssError
        #n.setInputs([[next]])
        n.getLayer('input').copyActivations( [next] )
        result = xor(current,next)
        #n.setOutputs([[result]])
        n.getLayer('output').copyTarget( [result] )
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        (tssError, totalCorrect, totalCount) = n.step()
        err2 = tssError
        #n.setInputs([[result]])
        n.getLayer('input').copyActivations( [result] )
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        current = int(random.random()*2)
        #n.setOutputs([[current]])
        n.getLayer('output').copyTarget( [current] )
        (tssError, totalCorrect, totalCount) = n.step()
        # for next step
        n.getLayer('context').copyActivations(n.getLayer('hidden').activation)
        err3 = tssError
        totalErr1 = totalErr1 + err1
        totalErr2 = totalErr2 + err2
        totalErr3 = totalErr3 + err3
        if step % n.reportRate == 0:
            print "Epoch: #%6d Errors = %.3f %.3f %.3f Avg = %.3f %.3f %.3f" \
                  % (step, err1, err2, err3, totalErr1 / step, \
                     totalErr2 / step, totalErr3 / step)
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
    n.setEpsilon(0.7)
    n.setMomentum(0.1)
    n.setBatch(0)
    n.setQuickProp(0)
    n.setReportRate(1000)
    sequentialXorSweeps(n, 30000)
    print "Training complete.  Test error again....................."
    n.setLearning(0)
    sequentialXorSweeps(n,1000)
