from pyro.brain import Brain

class TrackBall(Brain):

    def setup(self):
        self.cam = self.robot.getDevice( self.robot.hasA("camera") )
        self.ptz = self.robot.getDevice( self.robot.hasA("ptz") )
        self.ptz.setPose(0, 0, 0)
        print "Brain: make sure you set a Blobify Filter before running."

    def step(self):
        results = self.robot.get("robot/camera/filterResults")
        if len(results) > 1: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > 25:
                    centerX, centerY = (x1 + x2)/2, (y1 + y2)/2
                    pose = self.ptz.pose # p,t,z,r
                    print "center:", (centerX, centerY)
                    # ---------------------------------
                    diff = (centerX - (self.cam.width/2))
                    if abs(diff) < (.05 * self.cam.width):
                        pass
                    elif diff < 0:
                        # negative is right, positive is left
                        self.ptz.pan( pose[0] + .05) 
                    else:
                        self.ptz.pan( pose[0] - .05) 
                    # ---------------------------------
                    diff = (centerY - self.cam.height/2) 
                    if abs(diff) < .05 * self.cam.height:
                        pass
                    elif diff < 0: # down
                        self.ptz.tilt( pose[1] + .05) # positive is left
                    else:
                        self.ptz.tilt( pose[1] - .05) # negative is right
                    
                else:
                    self.ptz.center() #print "searching..."
                
            else:
                self.ptz.center() #print "searching..."
        else:
            print "Brain: I added a Blobify Filter for you!"
            self.cam.addFilter("match",220,27,46,)
            self.cam.addFilter("match",143,24,28,)
            self.cam.addFilter("blobify",0,255,255,0,1,1,1,)

def INIT(engine):
    assert(engine.robot.hasA("ptz") != 0 and
           engine.robot.hasA("camera") != 0)
    return TrackBall("Tracker", engine)
      
