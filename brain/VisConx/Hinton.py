# -------------------------------------------------------
# Hinton Diagrams
# -------------------------------------------------------

import Tkinter

class HintonBlock(Tkinter.Canvas):
    PADDING=4
    def __init__(self, parent, size, value, maxAbs, areaScaling=1):
        Tkinter.Canvas.__init__(self, parent)
        self.config(width=size, height=size, highlightbackground="black")
        self.value = value
        self.maxAbs=maxAbs
        self.size =size
        self.areaScaling = areaScaling
        self.center = size//2
        self.rect = self.create_rectangle(0,0,0,0,outline="black")
        self.drawRectangle()

    def setScaling(self, areaScaling):
        self.areaScaling = areaScaling
        self.drawRectangle()
    
    def updateRectangle(self, value, maxAbs):
        self.value = value
        self.maxAbs=maxAbs
        self.drawRectangle()

    def drawRectangle(self):
        if self.areaScaling:
            offset = (self.size*(abs(self.value)/self.maxAbs)**.5)/2 - self.PADDING
        else:
            offset = self.size*(abs(self.value)/self.maxAbs)/2 - self.PADDING

        if self.value > 0:
            fillCol = "white"
            borderCol = "black"
        elif self.value < 0:
            fillCol = "black"
            borderCol = "black"
        else:
            fillCol="#d9d9d9"
            borderCol="#d9d9d9"
        self.coords(self.rect, self.center-offset, self.center-offset, self.center+offset+1, self.center+offset+1)
        self.itemconfig(self.rect, fill=fillCol, outline = borderCol)       
        
class MatrixHinton(Tkinter.Toplevel):
    OUTSIDE_COL="white"
    TOP_SPACE = 10
    def __init__(self, parent, title, weightMatrix, fromAxisLabel="", toAxisLabel="", blockSize=50):
        Tkinter.Toplevel.__init__(self, parent)
        self.title(title)
        self.config(bg="white")
        
        self.fromAxisLabel = fromAxisLabel
        self.toAxisLabel = toAxisLabel
        
        self.weightMatrix = weightMatrix
        self.maxAbs = self.findMax()
        self.rectMatrix = []

        #top spacer
        Tkinter.Frame(self, bg="white", highlightthickness=0, height=self.TOP_SPACE).grid(row=0, col=0, columnspan=len(self.weightMatrix))
                                                                                             
        # place "axis" labels
        if not toAxisLabel=="":
            Tkinter.Label(self, text="%s" % (toAxisLabel,), bg=self.OUTSIDE_COL).grid(row=1, col=0, \
                                                                                                      rowspan = len(self.weightMatrix[0]), sticky=Tkinter.NSEW)
        if not fromAxisLabel=="":
            Tkinter.Label(self, text="%s" % (fromAxisLabel,), bg=self.OUTSIDE_COL).grid(row = len(self.weightMatrix[0])+2,\
                                                                                                          col=2, columnspan=len(self.weightMatrix), sticky=Tkinter.NSEW)

        #create the specific data labels
        if len(weightMatrix[0]) > 1:
            for i in xrange(len(weightMatrix[0])):
                Tkinter.Label(self, text="%u" % (i,), bg=self.OUTSIDE_COL).grid(col=1, row=i+1, sticky=Tkinter.NSEW)
        for i in xrange(len(weightMatrix)):
            Tkinter.Label(self, text="%u" % (i,), bg=self.OUTSIDE_COL).grid(row = len(self.weightMatrix[0])+1, col = i+2, sticky=Tkinter.NSEW)

        #scaling selection buttons
        self.byArea=Tkinter.IntVar()
        self.byArea.set(1)        
        buttonFrame = Tkinter.Frame(self, bg=self.OUTSIDE_COL)
        Tkinter.Label(buttonFrame, bg=self.OUTSIDE_COL, text="Scale by:").grid(col=0,row=1, sticky=Tkinter.W)
        self.areaButton = Tkinter.Radiobutton(buttonFrame, text="Area", bg=self.OUTSIDE_COL, activebackground=self.OUTSIDE_COL, \
                                              highlightthickness=0, variable=self.byArea, value=1, command=self.updateScaling, state=Tkinter.ACTIVE)
        self.areaButton.grid(col=0,row=2, sticky=Tkinter.W)
        self.areaButton.invoke()
        sideButton = Tkinter.Radiobutton(buttonFrame, text="Side Length", bg=self.OUTSIDE_COL, activebackground=self.OUTSIDE_COL, \
                                         highlightthickness=0, variable=self.byArea, value=0,command=self.updateScaling)
        sideButton.grid(col=0,row=3, sticky=Tkinter.W)
        buttonFrame.grid(col=len(weightMatrix)+2, row=1, rowspan=len(weightMatrix), sticky=Tkinter.NSEW)
                         
        #draw rectangles
        for i in xrange(len(weightMatrix)):
            tempRectList = []
            for j in xrange(len(weightMatrix[i])):
                tempRectList += [HintonBlock(self, blockSize, self.weightMatrix[i][j], self.maxAbs, areaScaling=self.byArea)]
                tempRectList[-1].grid(col=i+2, row=j+1)
            self.rectMatrix += [tempRectList]
                
        self.update_idletasks()

    def updateWeights(self, weightMatrix):
        self.weightMatrix = weightMatrix
        self.maxAbs = self.findMax()
        for i in xrange(len(self.rectMatrix)):
            for j in xrange(len(self.rectMatrix[i])):
                self.rectMatrix[i][j].updateRectangle(self.weightMatrix[i][j], self.maxAbs)
        self.update_idletasks()

    def findMax(self):
        maxAbs = 0
        for row in self.weightMatrix:
            for weight in row:
                if abs(weight) > maxAbs:
                    maxAbs = abs(weight)

        if maxAbs == 0.0:
            return 1.0
        else:
            return maxAbs

    def updateScaling(self):
        for rows in self.rectMatrix:
            for items in rows:
                items.setScaling(self.byArea.get())
        self.update_idletasks()
        
if __name__ == '__main__':
    root = Tkinter.Tk()
    #diag = RowHinton(root, "Side Length Test", [0.0, .25, .5, .75, 1.0])
    #diag = RowHinton(root, "Area Test", [0.0,.1,.2, .25, .5, .75, 1.0], scaleArea=1)
    myDiag = MatrixHinton(root, "Matrix Hinton Test", [[5.0, 3.0, 2.0], [-2.0, -3.4, -6.0], [1.0, 4.0, -7.0]])
    myDiag = MatrixHinton(root, "Scaling Test", [[-9.88652774], [4.94260928]])
    root.mainloop()
