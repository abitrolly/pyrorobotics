# A Simple Device

from pyrobot.robot.device import Device
from threading import Thread, Event

class TestDevice(Device, Thread):
    def setup(self):
        self.type = "test"
        self.visible = 1
        self.specialvalue = 42
        self._stopevent = Event()
        self._sleepperiod = 0.01
        Thread.__init__(self, name="TestThread")
        self.threadCount = 0
        self.updateCount = 0
        self.start()
        
    def run(self):
        while not self._stopevent.isSet():
            self.threadCount += 1
            self._stopevent.wait(self._sleepperiod)

    def join(self,timeout=None):
        self._stopevent.set()
        Thread.join(self, timeout)

    def makeWindow(self):
        print "[[[[ made window! ]]]]"

    def updateWindow(self):
        print "Thread updates:", self.threadCount, "Manual updates:", self.updateCount

    def updateDevice(self):
        self.updateCount += 1

def INIT(robot):
    return {"test": TestDevice()}
