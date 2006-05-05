from pyrobot.brain.behaviors import State, FSMBrain
import random

class MaintainHeight(State):
    def onActivate(self):
        pass

    def update(self):
        pass

class Done(State):
    def onActivate(self):
        pass

    def update(self):
        pass

class HoverBullseye(State):
    def onActivate(self): # method called when activated or gotoed
        pass
    
    def update(self):
        # not seeing red for a bit,
        if random.random() < .1:
            self.goto('Done')
        else:
            self.goto('FindBullseye')
        # else keep centered on red

class FindBullseye(State):
    def onActivate(self):
        # remove filters on downward facing robot
        #self.robot.camera[]
        # add red, and blobify
        pass

    def update(self):
        # if you see bullseye
        self.goto('HoverBullseye')
        # else, search for it

class StartMaze(State):
    def onActivate(self):
        pass

    def update(self):
        self.goto('FindFiducial')

class FindFiducial(State):
    def onActivate(self):
        pass

    def update(self):
        self.goto('OrientFiducial')

class OrientFiducial(State):
    def onActivate(self):
        self.counter = 0

    def update(self):
        if self.counter > 100:
            self.goto('FindBullseye')
        self.counter += 1

def INIT(engine): # passes in engine, if you need it
    brain = FSMBrain("Blimpy", engine)
    # add a few states:
    brain.add(StartMaze(1))
    brain.add(MaintainHeight(1))
    brain.add(Done())
    brain.add(FindFiducial())
    brain.add(OrientFiducial())
    brain.add(HoverBullseye())
    brain.add(FindBullseye())
    return brain
