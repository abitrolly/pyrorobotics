# a basic brain class


import thread
import threading
import time
import pyro.gui.console
#from pyro.gui.drawable import Drawable

#PYTHON ERROR: Brain should be subclass of Drawable, but that stores
#its data in "self.data", and that is where thread gets its hash value
#name.

class Brain(threading.Thread): #, Drawable):

    def __init__(self, name = 'brain', engine = 0):
        threading.Thread.__init__(self)
        self.lastRun = time.time() # seconds
        #Drawable.__init__(self, name)
        self.name = name
        self.engine = engine
        if engine:
            self.robot = engine.robot
	self.thread = 0
        self.condition = threading.Condition()
        self.needToStop = 1
        self.needToQuit = 0
        self.needToStep = 0
        if self.robot != 0:
            self.robot.localize()
        # user setup:
        self.setup()
        # start the thread:
        self.start()

    def __repr__(self):
        return "Brain name = '%s'" % self.name

    def _draw(self, options, renderer):
        pass

    def getRobot(self):
        return self.robot

    def getEngine(self):
        return self.engine

    def quit(self):
        self.needToStop = 0
        self.needToQuit = 1
        if self.engine and self.engine.gui:
            self.engine.gui.done = 1
    
    def run(self):
        while self.needToQuit is not 1 and self.isAlive():
            #print "Acquire ----------------------------"
            count = 0
            while self.isAlive() and self.condition.acquire(0) == 0:
                #print "r",
                count += 1
                if count > 20:
                    return
            
            if self.needToQuit:
                #print "release()"
                self.condition.release()
                #print "Return  ----------------------------"
                return
            elif self.needToStep > 0:
                self.needToStep -= 1 #protectedvariable
                self.needToStop = 1 #will be picked up next pass
            elif self.needToStop:
                #print "wait()"
                self.condition.wait(.25) # FIX: .5?
                #print "release()"
                self.condition.release()
                continue #check for quit before we step
            
            #print "step()"
            self.step()
            time.sleep(.1)
            self.lastRun = time.time() # seconds
            #print "release()"
            self.condition.release()
            #print "Return  ----------------------------"
            #print self.needToStep
        #print "End of run!"

    def pleaseQuit(self):
        #count = 0
        #while self.condition.acquire(0) == 0:
        #    print "q",
        #    count += 1
        #    if count > 20:
        #        return
        #self.condition.acquire()
        self.needToQuit = 1
        #self.condition.notify()
        #self.condition.release()
        
    def pleaseStep(self):
        count = 0
        while self.isAlive() and self.condition.acquire(0) == 0:
            #print "t",
            count += 1
            if count > 20:
                return
        #self.condition.acquire()
        self.needToStep += 1 #protected variable
        self.condition.notify()
        self.condition.release()
        self.pleaseRun()
        
    def pleaseStop(self):
        #count = 0
        #while self.condition.acquire(0) == 0:
        #    print "s",
        #    count += 1
        #    if count > 20:
        #        return
        #self.condition.acquire()
        self.needToStop = 1
        #self.condition.notify()
        #self.condition.release()
        
    def pleaseRun(self, callback = 0):
        if not self.isAlive():
            pyro.gui.console.log(pyro.gui.console.WARNING,"Brain thread is not alive but request to run was made.");
        #count = 0
        #while self.condition.acquire(0) == 0:
        #    print "R",
        #    count += 1
        #    if count > 20:
        #        return
        #self.condition.acquire()
        self.needToStop = 0
        #self.condition.notify()
        #self.condition.release()
        if callback != 0:
            callback()
		
    def step(self):
        print "need to override pyro.brain.Brain.step()."

    def setup(self):
        """
        User init method
        """
        pass
