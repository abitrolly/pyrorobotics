# a basic brain class

import thread
import threading
import time
import pyro.gui.console

class Brain(threading.Thread): 

    def __init__(self, name = 'brain', engine = 0, **kwargs):
        threading.Thread.__init__(self)
        self.lastRun = time.time() # seconds
        self.name = name
        self.engine = engine
        if engine is not 0:
            self.robot = engine.robot
	self.thread = 0
        self.condition = threading.Condition()
        self.needToStop = 1
        self.needToQuit = 0
        self.needToStep = 0
        self.pauseTime = 0.1 # time to sleep() in main loop. 0.1 means brain step() runs at max 10/sec
        if self.robot != 0:
            self.robot.localize()
        # user setup:
        self.setup(**kwargs)
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
        self.couldBeMoving = 0
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
                if self.couldBeMoving:
                    self.couldBeMoving = 0
                    self.robot.move(0, 0)
                continue #check for quit before we step
            
            #print "step()"
            self.robot.update()
            self.step()
            self.couldBeMoving = 1
            time.sleep(self.pauseTime)
            self.lastRun = time.time() # seconds
            #print "release()"
            self.condition.release()
            #print "Return  ----------------------------"
            #print self.needToStep
        #print "End of run!"
            
    def pleaseQuit(self):
        self.needToQuit = 1
        
    def pleaseStep(self):
        count = 0
        while self.isAlive() and self.condition.acquire(0) == 0:
            count += 1
            if count > 20:
                return
        self.needToStep += 1 #protected variable
        self.condition.notify()
        self.condition.release()
        self.pleaseRun()
        
    def pleaseStop(self):
        self.needToStop = 1
        
    def pleaseRun(self, callback = 0):
        if not self.isAlive():
            pyro.gui.console.log(pyro.gui.console.WARNING,"Brain thread is not alive but request to run was made.");
        self.needToStop = 0
        if callback != 0:
            callback()
		
    def step(self):
        print "need to override pyro.brain.Brain.step()."

    def setup(self, **kwargs):
        """
        User init method
        """
        pass

    def makeWindow(self):
        import Tkinter
        self.window = Tkinter.Toplevel()
        self.window.wm_title("Brain View")
        self.canvas = Tkinter.Canvas(self.window,width=550,height=300)
        self.canvas.pack()

    def redraw(self):
        self.canvas.create_text(100,130, tags='pie',fill='black', text = "This Brain needs a redraw method!")

    def destroy(self):
        """
        Method to override of you create objects.
        """
        pass
