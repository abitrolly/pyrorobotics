import Image, ImageChops, ImageDraw, ImageFont
import sys, os, colorsys, math
import random
import Tkinter, ImageTk
import string
#from pyro.vision import *

class ColorSet:
    def __init__(self):
        self.colors = [ 0, 90, 215, 190, 138, 172, 24, 116, 233]
        self.colorCount = 0
    def next(self):
        retval = self.colors[self.colorCount]
        self.colorCount = (self.colorCount + 1) % len(self.colors)
        return retval

class SymbolSet:
    def __init__(self):
        self.symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        self.symbolCount = 0
    def next(self):
        retval = self.symbols[self.symbolCount]
        self.symbolCount = (self.symbolCount + 1) % len(self.symbols)
        return retval

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
        self.fontFilename = path + "/tools/pilfonts/courR08.pil"
        self.symbols = 1        # activates/deactivates symbol mode
        self.color = 1          # activates/deactivates color
        self.lineWidth = 10     # the length of lines in non-symbol mode
        # the resolution given for the bitmap in the world file
        self.resolution = 0.01
        self.interval = 2       # frequency datapoints should be displayed
        self.robotPathData = self.readDataFile()
        im = Image.open(self.worldImageFilename)
        if not self.color:
            self.image = ImageChops.invert(im)
        self.image = im.convert("RGB")
        self.convertXPositionData(self.image, self.robotPathData)
        self.drawObj = ImageDraw.Draw(self.image)
        self.textDict = {}
        self.symbolDict = {}
        self.autoSymbol = 0
        self.symbolSet = SymbolSet()
        self.colorSet = ColorSet()

    def readDataFile(self):
        dataFile = open(self.pathDataFilename, "r")
        dataList = []
        for line in dataFile:
            elements = line.split()
            if len(elements) < 3:
                raise ValueError, "line contains less than 3 elements:" + line
            elif len(elements) == 3:
                dataList += [[float(x) for x in elements] + [" "]]
            else:
                dataList += [[float(x) for x in elements[:3]] + [string.join(elements[3:])]]
            dataList[-1][0] = dataList[-1][0]/self.resolution
            dataList[-1][1] = dataList[-1][1]/self.resolution
            dataList[-1][2] = (dataList[-1][2] + 90.0) * math.pi/180.0
        return dataList

    def getColor(self, label):
        if label in self.textDict:
            return self.textDict[label]
        else:
            self.textDict[label] = self.colorSet.next()
            return self.textDict[label]

    def getSymbol(self, label):
        if label in self.symbolDict:
            return self.symbolDict[label]
        else:
            self.symbolDict[label] = self.symbolSet.next()
            return self.symbolDict[label]

    def drawSymbol(self, loc, angle, label):
        pointList = []
        if self.autoSymbol:
            label = self.getSymbol(label)
        colorNum = self.getColor(label)
        if self.symbols:
            self.drawObj.text(loc, label, font = ImageFont.load(self.fontFilename),
                              fill = self.indexToColor(colorNum) )
        else:
            self.drawObj.line([(loc[0], loc[1]),
                          (loc[0] + self.lineWidth * math.sin(angle),
                           loc[1] + self.lineWidth * math.cos(angle))],
                         fill = self.indexToColor(colorNum))
            self.drawObj.ellipse( (loc[0] - 2, loc[1] - 2, loc[0] + 2, loc[1] + 2),
                             fill = (0, 0, 0))

    def makeWindow(self):
        if self.app != 0:
            self.window.deiconify()
        else:
            self.app = Tkinter.Tk()
            self.app.withdraw()
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
        self.window.withdraw()
      
    def updateWindow(self):
        image = ImageTk.PhotoImage(self.im)
        self.label.configure(image = image)
        while self.window.tk.dooneevent(2): pass

    def getImage(self):
        return self.image

    def indexToColor(self, index):
        maxIndex = 256
        if self.color:
            retColor = colorsys.hsv_to_rgb(float(index)/maxIndex, 1.0, 1.0)
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
        for x, y, angle, label in self.robotPathData:
            if iteration % self.interval == 0:
                self.drawSymbol((x,y), angle, label)
            iteration += 1
        self.image.save(outFile)

    def run(self):
        for data in self.robotPathData[0]:
            self.addLine(data)

if __name__ == "__main__":
    import sys
    testTrace = Trace(sys.argv[1],sys.argv[2])
    #testTrace = Trace("/home/dblank/pyro/experiments/colorful.gif","ffgoalposes.dat")
    testTrace.output(sys.argv[3])
    #testTrace.makeWindow()
    #testTrace.run()
    #testTrace.app.mainloop()
