from pyro.brain import Brain 
import time 
 
# Searches for red pucks and tries to grab and consume them. 
# Quits after finding three. 
 
class FindBlobs(Brain):  
    def setup(self):
        self.robot.startService('blob') 
        self.robot.startService('gripper')
        self.gripper = self.robot.getService("gripper")
        self.pucksFound = 0 
 
    def consumePuck(self): 
        gripper = self.gripper
        robot = self.robot
        if gripper.isClosed():
            gripper.store() 
            self.pucksFound += 1 
            print "pucks found:", self.pucksFound 
            time.sleep(1) 
            gripper.open() 
            time.sleep(1) 
        elif gripper.getBreakBeamState(): 
            robot.move(0, 0) 
            gripper.close() 
        else: 
            robot.move(0.05, 0) 
 
    def seekColor(self, channel): 
        minRange = 0.9 
        robot = self.robot
        gripper = self.gripper
        if gripper.getBreakBeamState() or gripper.isClosed(): 
            self.consumePuck() 
        elif self.collisionImminent('front-all', minRange): 
            translate, rotate = self.avoid(minRange) 
            robot.move(translate, rotate) 
        else: 
            result = self.getClosestBlob(channel) 
            if result == 'None': 
                leftSide = min(robot.get('/robot/range/front-left/value'))
                rightSide = min(robot.get('robot/range/front-right/value')
                if leftSide < rightSide: 
                    robot.move(0.1, -0.5) 
                else: 
                    robot.move(0.1, 0.5) 
            else: 
                turnDirection = result[0] 
                range = result[1] 
                if turnDirection > 0: 
                    robot.move(0.1, 0.15) 
                elif turnDirection < 0: 
                    robot.move(0.1, -0.15) 
                else: 
                    robot.move(0.2, 0) 
 
    # Returns 1 when the minimum sonar value from the given location group is 
    # less than the minRange. 
    def collisionImminent(self, location, minRange): 
        if min(self.robot.get('/robot/range',location,'value')) < minRange: 
            return 1 
        return 0 
 
    # Returns translate and rotate values for avoiding obstacles. 
    def avoid(self, minRange): 
        if self.collisionImminent('front', minRange): 
            return 0, -0.3 
        elif self.collisionImminent('front-left', minRange): 
            return 0, -0.3  
        elif self.collisionImminent('front-right', minRange): 
            return 0, 0.3 
        else: 
            return 0.2, 0 
 
    # Returns a list of all blobs on the given color channel. 
    def getBlobChannel(self, channel): 
        index = 0 
        data = self.robot.getServiceData('blob')
        if channel == 'red': 
            index = 0 
        elif channel == 'green': 
            index = 1 
        elif channel == 'blue': 
            index = 2 
        else: 
            print "unrecognized color channel"
        # 0 - dimension of area
        # 1 - blob data in terms of area
        range = data[1][index] 
        return range 
 
    # Returns a list of the two key features of the blob information for the 
    # closest blob on the given channel. 
    # The blob information consists of a list of nine features: 
    # Index 2: is an integer between 0 and 160 which represents the x position 
    # of the blob's centeroid.  A value of 0 indicates that the blob is at the 
    # farthest left location, a value of 80 indicates that the blob is centered, 
    # and a value of 160 indicates that the blob is at the farthest right location. 
    # Index 8: is an integer representing the range to the blob.  When using a 
    # pioneer robot with a gripper, if the blob is centered, then a range of 380 
    # indicates that it is within the grasp of the gripper. 
    def getClosestBlob(self, channel): 
        all = self.getBlobChannel(channel) 
        if len(all) == 0: 
            return 'None' 
        else: 
            if all[0][2] < 75: 
                turnDirection = 1 
            elif all[0][2] > 85: 
                turnDirection = -1 
            else: 
                turnDirection = 0 
            return turnDirection, all[0][8] 
  
    def step(self): 
        if (self.pucksFound > 2): 
            print "Quitting after finding 3 pucks" 
            self.quit() 
        else: 
            self.seekColor('red') 
  
def INIT(engine):  
   return FindBlobs('FindBlobs', engine)
