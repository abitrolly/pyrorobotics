from pyro.system.log import Log
from pyro.brain.conx import *
# Create the network  
n = Network()  
n.addThreeLayers(140,45,2)  
# Set learning parameters  
n.setEpsilon(0.1)  
n.setMomentum(0.9)  
n.setTolerance(0.1)
# if weights exists:
#n.initialize()
#n.loadWeightsFromFile("ff.wts")
# set inputs and targets (from collected data set)  
n.loadInputsFromFile('ffinputs.dat')
n.loadTargetsFromFile('fftargets.dat')
log = Log()
best = 0  
for i in xrange(0,10000,1):  
   tssError, totalCorrect, totalCount = n.sweep()    
   correctpercent = (totalCorrect*0.1) / (totalCount*0.1)  
   log.writeln( "Epoch # "+ str(i)+ " TSS ERROR: "+ str(tssError)+ 
                " Correct: "+ str(totalCorrect)+ " Total Count: "+ 
                str(totalCount)+ " %correct = "+ str(correctpercent))  
   if best < correctpercent:  
      n.saveWeightsToFile("ff.wts")  
      best = correctpercent  
print "done"  

