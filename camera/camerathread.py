# Camera class

import thread
import threading
import time
import pyro.gui.console
import os
#from pyro.gui.drawable import Drawable

#PYTHON ERROR: should be subclass of Drawable, but that stores its
#data in "self.data", and that is where thread gets its hash value
#name.

class Camera(threading.Thread): #, Drawable):

    def __init__(self, name = 'camera', robot = 0):
        threading.Thread.__init__(self)
        #Drawable.__init__(self, name)
        self.name = name
        self.robot = robot
	self.thread = 0
        self.condition = threading.Condition()
        self.needToStop = 1
        self.needToQuit = 0
        self.needToStep = 0
        self.start()

    def _draw(self, options, renderer):
        pass

    def getRobot(self):
        return self.robot
    
    def run(self):
        while self.needToQuit is not 1 and self.isAlive():
            count = 0
            while self.isAlive() and self.condition.acquire(0) == 0:
                count += 1
                if count > 20:
                    return
            
            if self.needToQuit:
                self.condition.release()
                return
            elif self.needToStep > 0:
                self.needToStep -= 1 #protectedvariable
                self.needToStop = 1 #will be picked up next pass
            elif self.needToStop:
                self.condition.wait(.25) # FIX: .5?
                self.condition.release()
                continue #check for quit before we step
            
            self.step()
            self.condition.release()

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
            gui.console.log(gui.console.WARN,"Camera thread is not alive but request to run was made.");
        self.needToStop = 0
        if callback != 0:
            callback()
		
    def step(self):
        print "Capturing image..."
        os.system("bttvgrab -G /dev/video0 -f camera.ppm -o pgm -N NTSC -Q -l 1 -S 1 -d q -W 32 -w 48")
