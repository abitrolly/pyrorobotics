# -------------------------------------------------------
# Scatter Plotter
# -------------------------------------------------------

from OpenGL.Tk import *
import os

class Line:
    def __init__(self, x, y, lineId, pointId):
        self.x = x
        self.y = y
        self.lineId = lineId
        self.pointId = pointId

class Scatter: # Plot
    def __init__(self, history = 100, xLabel = 'X', yLabel = 'Y',
                 title = None, width = 200, height = 200):
        self.win = Tk()
        if title == None:
            self.win.wm_title("scatter@%s:"%os.getenv('HOSTNAME'))
        else:
            self.win.wm_title(title)
        self.canvas = Canvas(self.win,width=width,height=height)
        self.canvas.pack()
        self.xBorder = 30
        self.yBorder = 30
        self.plotWidth = width - 2 * self.xBorder # / max value
        self.plotHeight = height - 2 * self.yBorder # / max value
        # title
        self.canvas.create_text(self.xBorder, 10,
                                text=title, fill='black')
        # border 
        self.canvas.create_line(self.xBorder, self.yBorder,
                                self.xBorder, height - self.yBorder,
                                width = 1, fill='black')
        self.canvas.create_line(self.xBorder, self.yBorder,
                                width - self.xBorder, self.yBorder,
                                width = 1, fill='black')
        self.canvas.create_line(self.xBorder, height - self.yBorder,
                                width - self.xBorder, width - self.yBorder,
                                width = 1, fill='black')
        self.canvas.create_line(width - self.xBorder, self.yBorder,
                                width - self.xBorder, width - self.yBorder,
                                width = 1, fill='black')
        # markers
        self.canvas.create_line(self.xBorder - 5, self.yBorder,
                                self.xBorder + 5, self.yBorder,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder - 5, self.yBorder + self.plotHeight / 2,
                                self.xBorder + 5, self.yBorder + self.plotHeight / 2,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder - 5, height - self.yBorder,
                                self.xBorder + 5, height - self.yBorder,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder, height - self.yBorder - 5,
                                self.xBorder, height - self.yBorder + 5,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder + self.plotWidth / 2, height - self.yBorder - 5,
                                self.xBorder + self.plotWidth / 2, height - self.yBorder + 5,
                                width = 2, fill='black')
        self.canvas.create_line(width - self.xBorder, height - self.yBorder - 5,
                                width - self.xBorder, height - self.yBorder + 5,
                                width = 2, fill='black')
        # text
        self.canvas.create_text(self.xBorder, height - 10,
                                text='0.0', fill='black')
        self.canvas.create_text(self.xBorder + self.plotWidth / 2, height - 10,
                                text='0.5', fill='black')
        self.canvas.create_text(width - self.xBorder, height - 10,
                                text='1.0', fill='black')
        self.canvas.create_text(10, self.yBorder, text='1.0', fill='black')
        self.canvas.create_text(10, self.yBorder + self.plotHeight / 2,
                                text='0.5', fill='black')
        self.canvas.create_text(10, height - self.yBorder,
                                text='0.0', fill='black')
        # ----------------------------------------------------------
        self.hist = [0] * history
        self.history = history
        self.count = 0
        self.offset = 30
        self.firstEver = 1
        self.last = 0

    def setTitle(self, title):
        self.win.wm_title(title)

    def _x(self, val):
        return int(val * self.plotWidth) + self.xBorder

    def _y(self, val):
        return int(self.plotHeight - val * self.plotHeight + self.yBorder)

    def addPoint(self, x, y):
        if self.count >= self.history:
            self.count = 0
        # if there is an old one here, delete it
        if type(self.hist[self.count]) != type(1):
            self.canvas.delete( self.hist[self.count].lineId )
            self.canvas.delete( self.hist[self.count].pointId )
        if type(self.last) != type(1):
            self.canvas.delete( self.last.pointId)
            x1 = self.last.x
            y1 = self.last.y
            self.last.pointId = self.canvas.create_oval(self._x(x1) - 2,
                                                        self._y(y1) - 2,
                                                        self._x(x1) + 2,
                                                        self._y(y1) + 2,
                                                        width = 0,
                                                        tag = 'object',
                                                        fill = 'coral')

        if self.firstEver:
            self.firstEver = 0
            lid = -1
        else:
            lid = self.canvas.create_line(self._x(self.last.x),
                                          self._y(self.last.y),
                                          self._x(x),
                                          self._y(y),
                                          width = 1,
                                          tag = 'object',
                                          fill = 'tan')
        pid = self.canvas.create_oval(self._x(x) - 3,
                                      self._y(y) - 3,
                                      self._x(x) + 3,
                                      self._y(y) + 3,
                                      width = 0,
                                      tag = 'object',
                                      fill = 'red')
        self.hist[self.count] = Line(x, y, lid, pid)
        self.last = self.hist[self.count]
        self.count += 1

if __name__ == '__main__':
    sp = Scatter()
    for y in range(100):
        for x in range(10):
            sp.addPoint(x/10.0, x/10.0)
    sp.win.mainloop()
