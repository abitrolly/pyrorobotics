import Image, ImageChops, ImageDraw, ImageFont
import sys, os, colorsys, math
import random
import Tkinter, ImageTk
#from pyro.vision import *

class Trace:
    """
    Trace provides a general way of displaying a path on an image.
    """

    def __init__(self,
                 worldImageFilename = "",
                 pathDataFilename = ""):
        self.worldImageFilename = worldImageFilename
        self.pathDataFilename = pathDataFilename
        self.app = 0
        if os.environ.has_key('PYRO'):
            path = os.environ['PYRO']
        else:
            raise "UnknownEnvVar", "PYRO"
        self.fontFilename = path + "/tools/pilfonts/courR12.pil"
        self.symbols = 0        # activates/deactivates symbol mode
        self.color = 1          # activates/deactivates color
        self.lineWidth = 30     # the length of lines in non-symbol mode
        # the resolution given for the bitmap in the world file
        self.resolution = 0.01
        self.interval = 1       # frequency datapoints should be displayed
        self.symbolList = ['o','A','B','C','D','E','F','G','H','I','J','K','L','M',
                           'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                           '!','@','/','\\','#','$','%','&','-','+',
                           '=','<', '>', '?', '{' ,'}','(', ')']
        self.robotPathData = self.readDataFile()
        im = Image.open(self.worldImageFilename)
        if not self.color:
            self.image = ImageChops.invert(im)
        self.image = im.convert("RGB")
        self.convertXPositionData(self.image, self.robotPathData[0])
        self.drawObj = ImageDraw.Draw(self.image)

    def readDataFile(self):
        dataFile = open(self.pathDataFilename, "r")
        dataList = []
        maxIndex = 1
        for lines in dataFile:
            # FIX: adding [0] to next line because it expects modelvector
            dataList += [[float(x) for x in lines.split()] + [0]]
            dataList[-1][0] = dataList[-1][0]/self.resolution
            dataList[-1][1] = dataList[-1][1]/self.resolution
            dataList[-1][2] = (dataList[-1][2] + 90.0) * math.pi/180.0
            if dataList[-1][3] > maxIndex:
                maxIndex = dataList[-1][3] + 1
        return (dataList, maxIndex)

    def drawSymbol(self, loc, angle, index, maxIndex):
        pointList = []
        if self.symbols:
            self.drawObj.text(loc, self.symbolList[index % maxIndex],
                         font = ImageFont.load(self.fontFilename),
                         fill = self.indexToColor(index, maxIndex))
        else:
            self.drawObj.line([(loc[0], loc[1]),
                          (loc[0] + self.lineWidth * math.sin(angle),
                           loc[1] + self.lineWidth * math.cos(angle))],
                         fill = self.indexToColor(index, maxIndex))
            self.drawObj.ellipse( (loc[0] - 2, loc[1] - 2, loc[0] + 2, loc[1] + 2),
                             fill = (0, 0, 0))

    def makeWindow(self):
        if self.app != 0:
            self.window.wm_state('normal')
        else:
            self.app = Tkinter.Tk()
            self.app.wm_state('withdrawn')
            self.window = Tkinter.Toplevel()
            self.window.wm_title("Trace View")
            self.im = self.getImage()
            self.image = ImageTk.PhotoImage(self.im)
            self.label = Tkinter.Label(self.window, image=self.image, bd=0)
            self.label.pack({'fill':'both', 'expand':1, 'side': 'left'})
            self.window.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.hideWindow)
            self.visible = 1
        while self.window.tk.dooneevent(2): pass

    def hideWindow(self):
        self.visible = 0
        self.window.wm_state('withdrawn')
      
    def updateWindow(self):
        image = ImageTk.PhotoImage(self.im)
        self.label.configure(image = image)
        while self.window.tk.dooneevent(2): pass

    def getImage(self):
        return self.image

    def indexToColor(self, index, maxIndex):
        if self.color:
            retColor = colorsys.hsv_to_rgb(float(index)/(maxIndex+1), 1.0, 1.0)
        else:
            retColor = (0,0,0)
        return (int(retColor[0]*255), int(retColor[1]*255), int(retColor[2]*255))

    def convertXPositionData(self, image, data):
        imWidth = image.size[1]
        for ls in data:
            ls[1] = imWidth - ls[1]

    def addLine(self, data):
        x, y, angle, model = data
        model = 1
        self.drawSymbol((x,y), angle, int(model), data[1])
        self.updateWindow()

    def output(self, outFile = "default.ppm"):
        iteration = 0
        for x, y, angle, model in self.robotPathData[0]:
            if iteration % self.interval == 0:
                self.drawSymbol((x,y), angle, int(model), self.robotPathData[1])
            iteration += 1
        self.image.save(outFile)    

    def run(self):
        for data in self.robotPathData[0]:
            self.addLine(data)

if __name__ == "__main__":
    import sys
    testTrace = Trace(sys.argv[1],sys.argv[2])
    #testTrace = Trace("/home/dblank/pyro/experiments/colorful.gif","ffgoalposes.dat")
    testTrace.output()
    #testTrace.makeWindow()
    #testTrace.run()
    #testTrace.app.mainloop()
