"""
A Pure Python 3D Robot Simulator in Tkinter

(c) 2005, PyroRobotics.org. Licensed under the GNU GPL.
"""
import Tkinter, time, math, random
from pyrobot.geometry.matrix import *
from pyrobot.simulators.pysim import *

## FIX: translateZ doesn't work? or maybe perspective is off?

class Tk3DSimulator(TkSimulator):
    def __init__(self, dimensions, offsets, scale, root = None, run = 1):
        TkSimulator.__init__(self, dimensions, offsets, scale, root, run)
        self.scale3D = 5.0/2.0 # FIX?
        self.centerx = self._width/2
        self.centery = self._height/2
        self.rotateMatrixWorld = translate(-self.centerx + self.offset_x,
                                           -self.centery, 0) * rotateYDeg(15) * rotateZDeg(15) * rotateXDeg(-60)
    def click_b2_up(self, event):
        self.click_stop = event.x, event.y
        if self.click_stop == self.click_start:
            # center on this position:
            center = self.canvas.winfo_width()/2, self.canvas.winfo_height()/2
            x_diff = self.click_stop[0] - center[0]
            y_diff = self.click_stop[1] - center[1]
        else: # move this much
            x_diff = self.click_start[0] - self.click_stop[0]
            y_diff = self.click_start[1] - self.click_stop[1]
        self.offset_x -= x_diff
        self.offset_y -= y_diff
        self.rotateMatrixWorld *= translate(-x_diff, y_diff, 0) 
        self.redraw()

    def drawLine(self, x0, y0, x1, y1, color, tag):
        return self.drawLine3D(x0, y0, 0, x1, y1, 0, fill = color, tag = tag)

    def drawLine3D(self, x0, y0, z0, x1, y1, z1, **args):
        VertsIn = [0, 0]
        VertsIn[0] = (self.matrix *
                      #translate(-__Robot->getActualX(),
                      #          -__Robot->getActualY(),0) *
                      Vertex3D(x0, y0, z0 ))
        VertsIn[1] = (self.matrix *
                      #Matrix::Translate(-__Robot->getActualX(),
                      #                  -__Robot->getActualY(),0) *
                      Vertex3D(x1, y1, z1 ))
        #ClipFace(VertsIn,2,VertsOut,lVertCount);
        #if (!lVertCount):
        #    break;
        ##################### VertsOut only beyond this point
        addPerspective(VertsIn[0], self.scale3D);
        addPerspective(VertsIn[1], self.scale3D);
        retval = self.canvas.create_line(self.centerx + VertsIn[0].data[0],
                                        self.centery - VertsIn[0].data[1],
                                        self.centerx + VertsIn[1].data[0],
                                        self.centery - VertsIn[1].data[1],
                                        **args)
        return retval

    def drawBox3D(self, x0, y0, z0, x1, y1, z1, **args):
        VertsIn = [0, 0]
        VertsIn[0] = (self.matrix *
                      #translate(-__Robot->getActualX(),
                      #          -__Robot->getActualY(),0) *
                      Vertex3D(x0, y0, z0 ))
        VertsIn[1] = (self.matrix *
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
        retval = self.canvas.create_line(self.centerx + VertsIn[0].data[0],
                                        self.centery - VertsIn[0].data[1],
                                        self.centerx + VertsIn[1].data[0],
                                        self.centery - VertsIn[1].data[1],
                                        **args)
        return retval

    def getPoint3D(self, x, y, z):
        VertsIn = (self.matrix *
                   #translate(-__Robot->getActualX(),
                   #          -__Robot->getActualY(),0) *
                   Vertex3D(x, y, z ))
        #ClipFace(VertsIn,2,VertsOut,lVertCount);
        #if (!lVertCount):
        #    break;
        ##################### VertsOut only beyond this point
        addPerspective(VertsIn, self.scale3D);
        return self.centerx + VertsIn.data[0], self.centery - VertsIn.data[1]

    def drawPolygon(self, points, color="", outline="black", tag = None, **args):
        xy = map(lambda pt: self.getPoint3D(pt[0],pt[1],0), points)
        return self.drawPolygon3D(xy, tag=tag, fill=color, outline=outline, **args)
    def drawPolygon3D(self, points, **args):
        return self.canvas.create_polygon(points, **args)
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
        self.matrix = matrix
        
        for segment in self.world:
            (x1, y1), (x2, y2) = segment.start, segment.end
            id = self.drawLine3D(x1, y1, 0, x2, y2, 0, tag="line")
            segment.id = id

        for shape in self.shapes:
            if shape[0] == "box":
                name, ulx, uly, lrx, lry, color = shape
                # wall 3:
                points = []
                points.append(self.getPoint3D(lrx, lry, 0))
                points.append(self.getPoint3D(lrx, uly, 0))
                points.append(self.getPoint3D(lrx, uly, 1))
                points.append(self.getPoint3D(lrx, lry, 1))
                self.drawPolygon3D(points, tag="line", fill=color, outline="black")
                # wall 4:
                points = []
                points.append(self.getPoint3D(lrx, lry, 0))
                points.append(self.getPoint3D(ulx, lry, 0))
                points.append(self.getPoint3D(ulx, lry, 1))
                points.append(self.getPoint3D(lrx, lry, 1))
                self.drawPolygon3D(points, tag="line", fill=color, outline="black")
                # wall 2:
                points = []
                points.append(self.getPoint3D(ulx, uly, 0))
                points.append(self.getPoint3D(lrx, uly, 0))
                points.append(self.getPoint3D(lrx, uly, 1))
                points.append(self.getPoint3D(ulx, uly, 1))
                self.drawPolygon3D(points, tag="line", fill=color, outline="black")
                # wall 1:
                points = []
                points.append(self.getPoint3D(ulx, uly, 0))
                points.append(self.getPoint3D(ulx, lry, 0))
                points.append(self.getPoint3D(ulx, lry, 1))
                points.append(self.getPoint3D(ulx, uly, 1))
                self.drawPolygon3D(points, tag="line", fill=color, outline="black")
                # top:
                if 0:
                    points = []
                    points.append(self.getPoint3D(ulx, uly, 1))
                    points.append(self.getPoint3D(ulx, lry, 1))
                    points.append(self.getPoint3D(lrx, lry, 1))
                    points.append(self.getPoint3D(lrx, uly, 1))
                    self.drawPolygon3D(points, tag="line", fill=color, outline="black")


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
        for robot in self.robots:
            robot._last_pose = (-1, -1, -1)
    

if __name__ == "__main__":
    sim = Tk3DSimulator((446,491),(21,451),80.517190)
    sim.addBox(0, 0, 5, 5)
    sim.addBox(0, 4, 1, 5, "blue", wallcolor="blue")
    sim.addBox(2.5, 0, 2.6, 2.5, "green", wallcolor="green")
    sim.addBox(2.5, 2.5, 3.9, 2.6, "green", wallcolor="green")
    sim.mainloop()

