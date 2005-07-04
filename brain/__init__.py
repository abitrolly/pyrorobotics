# a basic brain class

import threading, time, operator
import pyrobot.gui.console

def avg(list):
    sum = reduce(operator.add, list)
    return sum / float(len(list))

class Brain(threading.Thread):
    """
    This is the main thread for running a robot controler (ie, a brain).
    """
    def __init__(self, name = 'brain', engine = 0, **kwargs):
        threading.Thread.__init__(self)
        self.debug = 0
        self.stack = [] # used in brains with states (BehaviorBasedBrain and FSMBrain)
        self.stepCount = 0
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
        self.profilePerformance = 0
        self.profileCount = 0
        self.setup(**kwargs)
        # start the thread:
        self.start()

    # wrappers here to talk to default robot:
    def move(self, *args):
        return self.robot.move(*args)
    def translate(self, *args):
        return self.robot.translate(*args)
    def rotate(self, *args):
        return self.robot.rotate(*args)
    def stop(self):
        return self.robot.stop()
    def startDevice(self, *args, **keywords):
        return self.robot.startDevice(*args, **keywords)
    def removeDevice(self, *args, **keywords):
        return self.robot.removeDevice(*args, **keywords)
    def update(self):
        return self.robot.update()
    def motors(self, *args):
        return self.robot.motors(*args)
    def getDevice(self, *args):
        return self.robot.getDevice(*args)
    def hasA(self, *args):
        return self.robot.hasA(*args)
    def requires(self, *args):
        return self.robot.requires(*args)
    def _draw(self, options, renderer):
        pass
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
            self.stepCount += 1
            self.couldBeMoving = 1
            time.sleep(self.pauseTime)
            if self.profilePerformance == 2:
                self.profileCount += 1
                self.profileTotalTime += time.time() - self.lastRun
                if self.profileCount % 100 == 0:
                    print "Profile: brain running at %.3f steps/second" % (float(self.profileCount) / self.profileTotalTime)
                    self.profileTotalTime = 0.0
                    self.profileCount = 0
            if self.profilePerformance == 1:
                self.profileTotalTime = 0.0
                self.profilePerformance = 2
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
            pyrobot.gui.console.log(pyrobot.gui.console.WARNING,"Brain thread is not alive but request to run was made.");
        self.needToStop = 0
        if callback != 0:
            callback()
		
    def step(self):
        print "need to override pyrobot.brain.Brain.step()."

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

