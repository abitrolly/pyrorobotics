import Image, ImageChops, ImageDraw, ImageFont
import sys, os, colorsys, math
import random

class Trace:
    """
    Trace provides a general way of displaying a path on an image.
    """

    def __init__(self,
                 worldImageFilename = "",
                 pathDataFilename = ""):
        self.worldImageFilename = worldImageFilename
        self.pathDataFilename = pathDataFilename
        if os.environ.has_key('PYRO'):
            path = os.environ['PYRO']
        else:
            raise "UnknownEnvVar", "PYRO"
        self.fontFilename = path + "/tools/pilfonts/courR12.pil"
        self.symbols = 0        # activates/deactivates symbol mode
        self.color = 1          # activates/deactivates color
        self.lineWidth = 16     # the length of lines in non-symbol mode
        # the resolution given for the bitmap in the world file
        self.resolution = 0.01
        self.interval = 1       # frequency datapoints should be displayed
        self.symbolList = ['o','A','B','C','D','E','F','G','H','I','J','K','L','M',
                           'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                           '!','@','/','\\','#','$','%','&','-','+',
                           '=','<', '>', '?', '{' ,'}','(', ')']
        self.robotPathData = self.readDataFile()

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

    def drawSymbol(self, drawObj, loc, angle, index, maxIndex):
        pointList = []
        if self.symbols:
            drawObj.text(loc, self.symbolList[index % maxIndex],
                         font = ImageFont.load(self.fontFilename),
                         fill = self.indexToColor(index, maxIndex))
        else:
            drawObj.line([(loc[0] + (self.lineWidth/2)*math.sin(angle),
                           loc[1] + (self.lineWidth/2)*math.cos(angle)),
                          (loc[0] - (self.lineWidth/2)*math.sin(angle),
                           loc[1] - (self.lineWidth/2)*math.cos(angle))],
                         fill = self.indexToColor(index, maxIndex))

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

    def output(self, outFile = "default.ppm"):
        image = Image.open(self.worldImageFilename)
        if not self.color:
            image = ImageChops.invert(image)
        image = image.convert("RGB")
        self.convertXPositionData(image, self.robotPathData[0])
        drawObj = ImageDraw.Draw(image)
        iteration = 0
        for x, y, angle, model in self.robotPathData[0]:
            if iteration % self.interval == 0:
                self.drawSymbol(drawObj, (x,y), angle, int(model), self.robotPathData[1])
            iteration += 1
        image.save(outFile)    

if __name__ == "__main__":
    testTrace = Trace("/home/dblank/pyro/experiments/tutorial.gif","poses.dat")
    testTrace.output()
