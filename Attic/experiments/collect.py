from pyro.brain import Brain
import random
from time import sleep

def saveListToFile(ls,file):
    for i in range(len(ls)):
        file.write("%.8f"%ls[i]+" ")
    file.write("\n")

class Collect(Brain):
    """
    This program collects sonar, images and motor data using avoid obstacle
    behavior
    Names of the files need to be set
    """

    def setup(self):
        self.noise = 0
        self.getRobot().startService(["BlobCamera", "truth"])
        self.camera = self.getRobot().getService("BlobCamera")
        self.truth = self.getRobot().getService("truth")
        self.sonar = open("sonar.dat","w")
        self.vision = open("camera.dat","w")
        self.motors = open("motors.dat", "w")
        self.pose = open("poses.dat", "w")
        self.vision.write("900\n")
        self.sonar.write("16\n")
        self.currStep = 1
        self.wasStalled = 0
        self.direction = 1
        self.blockedFront = 0
        self.truth.setPose(0.850, 0.800, 65.400)

    def avoidObstacles(self):
        """
        Determines next action, but doesn't execute it.
        Returns the translate and rotate values.
        
        When front is blocked, it picks to turn away from the
        direction with the minimum reading and maintains that
        turn until front is clear.
        """
        d = 0.7
        ds = 0.3
        turn = random.random()
        minFront = self.getRobot().get('range','value','front','min')[1]
        minLeft  = self.getRobot().get('range','value','front-left','min')[1]
        minRight = self.getRobot().get('range','value','front-right','min')[1]
        sideLeft = self.getRobot().get('range','value',0)
        sideRight = self.getRobot().get('range','value',7)
        if self.getRobot().get('robot','stall'):
            if not self.wasStalled:
                print 'Stalled; Now backing up.'
                self.wasStalled = 1
                if (random.random() < 0.5):
                    return [-.3,-.3] 
                else:
                    return [-.3,.3]
            else:
                self.wasStalled = 0
        else:
            self.wasStalled = 0       
        if minFront < d:
            if not self.blockedFront:
                if minRight < minLeft:
                    self.direction = 1
                else:   
                    self.direction = -1
            self.blockedFront = 1
            return [0, self.direction * turn]
        elif minLeft < d:
            if self.blockedFront:
                return [0, self.direction * turn]
            else:
                return [0,-turn] 
        elif minRight < d:
            if self.blockedFront:
                return [0, self.direction * turn]
            else:
                return [0,turn] 
        else:
            if sideLeft < ds:
                return [0,-turn]
            elif sideRight < ds:
                return [0,turn]
            else:
                self.blockedFront = 0
                return [.2,0]
    
    def scaleSonar(self,ls):
        myl = []
        for val in ls:
            myl += [val/3.99]
        return myl
    
    def scaleMotor(self,ls):
        myl = []
        for val in ls:
            myl += [(val+1.0)/2.0]
        return myl

    def scaleList(self, ls, maxval): 
        for i in range(len(ls)): 
            ls[i] = ls[i] / float(maxval) 
        return ls

    def step(self):
        if self.currStep <= 5000 :
            pose = self.truth.getPose()
            image = self.camera.getShrunkenImage(xscale = 0.125, mode="sample")
            saveListToFile(pose, self.pose)
            saveListToFile(self.scaleSonar(self.getRobot().get("range",
                                                               "value",
                                                               "all")),
                           self.sonar)
            saveListToFile(self.scaleList(image.data, 255.0), self.vision)
            motVals = self.avoidObstacles()
            saveListToFile( self.scaleMotor( motVals ), self.motors)
            self.getRobot().move(motVals[0],motVals[1])
            sleep(.7)
            self.getRobot().stop()
            print "Step #", self.currStep
            self.motors.flush()
            self.currStep += 1
        else:
            self.quit()

def INIT(engine):
    return Collect("Collect",engine)
        
