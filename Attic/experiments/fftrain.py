from pyro.brain.conx import *
# Create the network  
n = Network()  
n.addThreeLayers(105,15,2)  
# Set learning parameters  
n.setEpsilon(0.1)  
n.setMomentum(0.9)  
n.setTolerance(0.1)  
# set inputs and targets (from collected data set)  
n.loadInputsFromFile('ffinputs.dat')
n.loadTargetsFromFile('fftargets.dat')

best = 0  
for i in xrange(0,1000,1):  
   tssError, totalCorrect, totalCount = n.sweep()    
   correctpercent = (totalCorrect*0.1) / (totalCount*0.1)  
   print ( "Epoch # "+ str(i)+ " TSS ERROR: "+ str(tssError)+ 
           " Correct: "+ str(totalCorrect)+ " Total Count: "+ 
           str(totalCount)+ " %correct = "+ str(correctpercent))  
   if best < correctpercent:  
      n.saveWeightsToFile("ff.wts")  
      best = correctpercent  
print "done"  

