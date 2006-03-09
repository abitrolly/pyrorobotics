"""
A Pure Python 3D Robot Simulator in Tkinter

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""
import Tkinter, time, math, random
from pyrobot.geometry.matrix import *
from pyrobot.simulators.pysim import TkSimulator

## FIX: translateZ doesn't work

class Tk3DSimulator(TkSimulator):
    def __init__(self, dimensions, offsets, scale, root = None, run = 1):
        TkSimulator.__init__(self, dimensions, offsets, scale, root, run)
        if (self._width/2 > self._height/2):
            self.scale3D = self._width/2
        else:
            self.scale3D = self._height/2
        self.centerx = self._width/2
        self.centery = self._height/2
        self.rotateMatrixWorld = translate(-self.centerx + self.offset_x, -self.centery + self.offset_y, 0) # * rotate(0, 0, 85)
    def click_b2_up(self, event):
        self.click_stop = event.x, event.y
        if self.click_stop == self.click_start:
            # center on this position:
            center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= (self.click_stop[0] - center[0])
            self.offset_y -= (self.click_stop[1] - center[1])
        else: # move this much
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
            self.offset_x -= x_diff
            self.offset_y -= y_diff
        self.rotateMatrixWorld *= translate(-x_diff, y_diff, 0) 
        self.redraw()

    def drawLine(self, matrix, x0, y0, z0, x1, y1, z1, **args):
        print "drawLine:", x0, y0, z0, x1, y1, z1
        VertsIn = [0, 0]
        VertsIn[0] = (matrix *
                      #translate(-__Robot->getActualX(),
                      #          -__Robot->getActualY(),0) *
                      Vertex3D(x0, y0, z0 ))
        VertsIn[1] = (matrix *
                      #Matrix::Translate(-__Robot->getActualX(),
                      #                  -__Robot->getActualY(),0) *
                      Vertex3D(x1, y1, z1 ))
        #ClipFace(VertsIn,2,VertsOut,lVertCount);
        #if (!lVertCount):
        #    break;
        ##################### VertsOut only beyond this point
        addPerspective(VertsIn[0], self.scale3D);
        addPerspective(VertsIn[1], self.scale3D);
        retval = sim.canvas.create_line(self.centerx + VertsIn[0].data[0],
                                        self.centery - VertsIn[0].data[1],
                                        self.centerx + VertsIn[1].data[0],
                                        self.centery - VertsIn[1].data[1],
                                        **args)
        return retval

    def drawBox(self, matrix, x0, y0, z0, x1, y1, z1, **args):
        print "drawBox:", x0, y0, z0, x1, y1, z1
        VertsIn = [0, 0]
        VertsIn[0] = (matrix *
                      #translate(-__Robot->getActualX(),
                      #          -__Robot->getActualY(),0) *
                      Vertex3D(x0, y0, z0 ))
        VertsIn[1] = (matrix *
                      #Matrix::Translate(-__Robot->getActualX(),
                      #                  -__Robot->getActualY(),0) *
                      Vertex3D(x1, y1, z1 ))
        #ClipFace(VertsIn,2,VertsOut,lVertCount);
        #if (!lVertCount):
        #    break;
        ##################### VertsOut only beyond this point
        addPerspective(VertsIn[0], self.scale3D);
        addPerspective(VertsIn[1], self.scale3D);
        if "outline" in args:
            del args["outline"]
        retval = sim.canvas.create_line(self.centerx + VertsIn[0].data[0],
                                        self.centery - VertsIn[0].data[1],
                                        self.centerx + VertsIn[1].data[0],
                                        self.centery - VertsIn[1].data[1],
                                        **args)
        return retval

    def getPoint(self, matrix, x, y, z):
        VertsIn = (matrix *
                   #translate(-__Robot->getActualX(),
                   #          -__Robot->getActualY(),0) *
                   Vertex3D(x, y, z ))
        #ClipFace(VertsIn,2,VertsOut,lVertCount);
        #if (!lVertCount):
        #    break;
        ##################### VertsOut only beyond this point
        addPerspective(VertsIn, self.scale3D);
        return self.centerx + VertsIn.data[0], self.centery - VertsIn.data[1]

    def drawPoly(self, points, **args):
        retval = sim.canvas.create_polygon(points, **args)
        return retval
    def rotateWorld(self, x, y, z):
        self.rotateMatrixWorld *= rotate(x, y, z)
        self.redraw()
    def translateWorld(self, x, y, z):
        self.rotateMatrixWorld *= translate(x, y, z)
        self.redraw()

    def redraw(self):
        self.canvas.delete('all')
        matrix = (
            ## get the robot away from the screen
            #translate(0,0,0) *
            ## do the screen rotate
            self.rotateMatrixWorld *
            ## This will point 0 angle of world, up
            #rotateXRad(math.pi/2) *
            ## tip down a bit:
            #rotateYDeg(45) *
            ## scale it
            scale(self.scale,self.scale,self.scale)
            )
        # rotate the world around robot's dir:
        #matrix = (
        #    ## get the robot away from the screen
        #    Matrix::Translate(0,0,-75.0) *
        #    ## do the screen rotate
        #    rotateMatrixRobot *
        #    ## this will let the robot rotate the world
        #    RotateZRad(-__Robot->getActualRadth()) *
        #    ## scale it
        #    Matrix::Scale(30,30,30)
        #    )        
        
        for shape in self.shapes:
            if shape[0] == "box":
                name, ulx, uly, lrx, lry, color = shape
                points = []
                points.append(self.getPoint(matrix, ulx, uly, 0))
                points.append(self.getPoint(matrix, ulx, lry, 0))
                points.append(self.getPoint(matrix, ulx, lry, -1))
                points.append(self.getPoint(matrix, ulx, uly, -1))
                self.drawPoly(points, tag="line", fill=color, outline="black")

        for segment in self.world:
            (x1, y1), (x2, y2) = segment.start, segment.end
            id = self.drawLine(matrix, x1, y1, 0, x2, y2, 0, tag="line")
            segment.id = id

##         for light in self.lights:
##             if light.type != "fixed": continue 
##             x, y, brightness, color = light.x, light.y, light.brightness, light.color
##             self.canvas.create_oval(self.scale_x(x - brightness), self.scale_y(y - brightness),
##                                     self.scale_x(x + brightness), self.scale_y(y + brightness),
##                                     tag="line", fill=color, outline="orange")
##         i = 0
##         for path in self.trail:
##             if self.robots[i].subscribed and self.robots[i].display["trail"] == 1:
##                 if path[self.trailStart] != None:
##                     lastX, lastY, lastA = path[self.trailStart]
##                     lastX, lastY = self.scale_x(lastX), self.scale_y(lastY)
##                     color = self.robots[i].color
##                     for p in range(self.trailStart, self.trailStart + self.maxTrailSize):
##                         xya = path[p % self.maxTrailSize]
##                         if xya == None: break
##                         x, y = self.scale_x(xya[0]), self.scale_y(xya[1])
##                         self.canvas.create_line(lastX, lastY, x, y, fill=color)
##                         lastX, lastY = x, y
##             i += 1
##         for robot in self.robots:
##             robot._last_pose = (-1, -1, -1)
    

if __name__ == "__main__":
    sim = Tk3DSimulator((446,491),(21,451),80.517190)
    sim.addBox(0, 0, 5, 5)
    sim.addBox(0, 4, 1, 5, "blue", wallcolor="blue")
    sim.addBox(2.5, 0, 2.6, 2.5, "green", wallcolor="green")
    sim.addBox(2.5, 2.5, 3.9, 2.6, "green", wallcolor="green")
    sim.mainloop()

