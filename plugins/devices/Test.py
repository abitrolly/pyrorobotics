# A Simple Device

from pyrobot.robot.device import Device

class Test(Device):

    def seeData(self, *args):
        return args

    def setup(self):
        self.devData['specialvalue'] = 42
        self.subDataFunc['subdata'] = self.seeData

    def makeWindow(self):
        self.devData[".visible"] = 1
        print "[[[[ made window! ]]]]"

    def updateWindow(self):
        print "update window!" # when visible

    def updateDevice(self):
        #print "------------- update device!" 10 times a second!
        pass

def INIT(robot):
    return {"test": Test()}
