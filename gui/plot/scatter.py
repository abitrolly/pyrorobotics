# -------------------------------------------------------
# Scatter Plotter
# -------------------------------------------------------

from Tkinter import *
import os

class Line:
    def __init__(self, x, y, lineId, pointId):
        self.x = x
        self.y = y
        self.lineId = lineId
        self.pointId = pointId

class Scatter: # Plot
    def __init__(self, history = [100,], xLabel = 'X', yLabel = 'Y',
                 title = None, legend = [None, ], width = 275, height = 200,
                 linecount = 1, xStart = 0.0, xEnd = 1.0, yStart = 0.0, yEnd = 1.0):
        self.color = ['blue', 'red', 'green', 'yellow', 'orange', \
                      'black', 'azure', 'beige', 'brown', 'coral', \
                      'gold', 'ivory', 'moccasin', 'navy', 'salmon', \
                      'tan', 'ivory']
        self.win = Toplevel()
        if title == None:
            self.win.wm_title("scatter@%s:"%os.getenv('HOSTNAME'))
        else:
            self.win.wm_title(title)
        self.width = width
        self.height = height
        self.title = title
        self.xBorder = 30
        self.yBorder = 30
        self.plotHeight = self.height - 2 * self.yBorder # / max value
        self.plotWidth =  self.plotHeight # / max value
        self.xStart = xStart
        self.xEnd = xEnd
        self.yStart = yStart
        self.yEnd = yEnd
        self.linecount = linecount
        self.legend = legend
        # ----------------------------------------------------------
        self.lineCount = self.linecount
        self.hist = [0] * self.linecount # actual hist of line
        self.history = history[:] # history counts for each line
        self.firstEver = [0] * self.linecount
        self.last = [0] * self.linecount
        self.count = [0] * self.linecount
        for i in range(self.linecount):
            self.hist[i] = [0] * history[i]
            self.firstEver[i] = 1
            self.last[i] = 0
            self.count[i] = 0

        # width - 2 * self.xBorder # / max value
        # background
        self.canvas = Canvas(self.win, width=width, height=height)
        self.canvas.bind("<Configure>", self.changeSize)
        self.canvas.pack({'fill':'both', 'expand':1, 'side': 'left'})
        self.init_graphics()
        
    def init_graphics(self):
        self.canvas.delete('graph')
        self.canvas.delete('object')
        self.canvas.create_rectangle(self.xBorder, self.yBorder,
                                     self.xBorder + self.plotWidth,
                                     self.height - self.yBorder,
                                     tag = 'graph',
                                     width = 1, fill='white')
        # title
        self.canvas.create_text(self.width / 2.0, 13,
                                tag = 'graph',
                                text=self.title, fill='black')
        # legend
        for i in range(self.linecount):
            self.canvas.create_rectangle(self.xBorder + self.plotWidth + 5,
                                         self.yBorder + i * 20,
                                         self.xBorder + self.plotWidth + 5 + 15,
                                         self.yBorder + i * 20 + 15,
                                         tag = 'graph',
                                         width = 1, fill=self.color[i])
            self.canvas.create_text(self.xBorder + self.plotWidth + 5 + 20,
                                    self.yBorder + i * 20 + 8,
                                    text=self.legend[i], fill='black',
                                    tag = 'graph',
                                    anchor='w')
        # text
        tick = 0.0 
        xtick_label = self.xStart
        while tick <= 1.0: 
            self.canvas.create_text(self.xBorder + self.plotWidth * tick, self.height - 10,
                                    tag = 'graph',
                                    text=xtick_label, fill='black')
            self.canvas.create_line(self.xBorder + self.plotWidth * tick,
                                    self.height - self.yBorder - 5,
                                    self.xBorder + self.plotWidth * tick,
                                    self.height - self.yBorder + 5,
                                    tag = 'graph',
                                    width = 2, fill='black')
            tick += 1.0 / 4.0
            xtick_label += (self.xEnd - self.xStart) / 4.0
        tick = 1.0
        ytick_label = self.yStart
        while tick >= 0.0:
            self.canvas.create_text(10, self.yBorder + self.plotHeight * tick,
                                    tag = 'graph',
                                    text=ytick_label, fill='black')
            self.canvas.create_line(self.xBorder - 5,
                                    self.yBorder + self.plotHeight * tick,
                                    self.xBorder + 5,
                                    self.yBorder + self.plotHeight * tick,
                                    tag = 'graph',
                                    width = 2, fill='black')
            tick -= 1.0 / 4.0
            ytick_label += (self.yEnd - self.yStart) / 4.0
        #self.canvas.lower('graph')
            
    def changeSize(self, event):
        self.width = self.win.winfo_width() 
        self.height = self.win.winfo_height() 
        self.plotHeight = self.height - (2 * self.yBorder) # / max value
        self.plotWidth =  self.plotHeight # / max value
        self.init_graphics()
            
    def setTitle(self, title):
        self.win.wm_title(title)

    def _x(self, val):
        val = (val - self.xStart) / (self.xEnd - self.xStart)
        return int(val * self.plotWidth) + self.xBorder

    def _y(self, val):
        val = (val - self.yStart) / (self.yEnd - self.yStart)
        return int(self.plotHeight - val * self.plotHeight + self.yBorder)

    def addPoint(self, x, y, line = 0):
        if self.count[line] >= self.history[line]:
            self.count[line] = 0
        # if there is an old one here, delete it
        if type(self.hist[line][self.count[line]]) != type(1):
            self.canvas.delete( self.hist[line][self.count[line]].lineId )
            self.canvas.delete( self.hist[line][self.count[line]].pointId )
        if type(self.last[line]) != type(1):
            last_x = self._x(self.last[line].x)
            last_y = self._y(self.last[line].y)
            self.canvas.delete( self.last[line].pointId)
            try:
                self.last[line].pointId = self.canvas.create_oval(last_x - 2,
                                                                  last_y - 2,
                                                                  last_x + 2,
                                                                  last_y + 2,
                                                                  width = 0,
                                                                  tag = 'object',
                                                                  fill = 'coral')
            except:
                pass
        try:
            my_x = self._x(x)
            my_y = self._y(y)
            if self.firstEver[line]:
                self.firstEver[line] = 0
                lid = -1
            else:
                last_x = self._x(self.last[line].x)
                last_y = self._y(self.last[line].y)
                lid = self.canvas.create_line(last_x,
                                              last_y,
                                              my_x,
                                              my_y,
                                              width = 1,
                                              tag = 'object',
                                              fill = 'tan')
            pid = self.canvas.create_oval(my_x - 3,
                                          my_y - 3,
                                          my_x + 3,
                                          my_y + 3,
                                          width = 0,
                                          tag = 'object',
                                          fill = self.color[line])
            self.hist[line][self.count[line]] = Line(x, y, lid, pid)
            self.last[line] = self.hist[line][self.count[line]]
            self.count[line] += 1
        except:
            pass

    def update(self):
        while self.win.tk.dooneevent(2): pass


if __name__ == '__main__':
    sp = Scatter()
    from random import random
    for y in range(100):
        for x in range(10):
            sp.addPoint(random(), random())
            sp.update()
    sp.win.mainloop()
