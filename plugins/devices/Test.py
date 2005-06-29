# A Simple Device

from pyrobot.robot.device import Device

class Test(Device):

    def setup(self):
        self.type = "test"
        self.specialvalue = 42

    def makeWindow(self):
        self.visible = 1
        print "[[[[ made window! ]]]]"

    def updateWindow(self):
        print "update window!" # when visible, few times a second

    def updateDevice(self):
        print "------------- update device!" # 10 times a second!

def INIT(robot):
    return {"test": Test()}
