# A Simple Service

from pyro.robot.service import Service

class Test(Service):

    def makeWindow(self):
        self.visible = 1
        print "made window!"

    def updateWindow(self):
        print "update window!"

def INIT(robot):
    return {"test": Test()}
