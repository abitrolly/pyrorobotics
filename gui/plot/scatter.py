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
    def __init__(self, history = [100,], xLabel = 'X', yLabel = 'Y',
                 title = None, legend = [None, ], width = 275, height = 200,
                 linecount = 1):
        self.color = ['blue', 'red', 'green', 'yellow', 'orange', \
                      'black', 'azure', 'beige', 'brown', 'coral', \
                      'gold', 'ivory', 'moccasin', 'navy', 'salmon', \
                      'tan', 'ivory']
        self.win = Tk()
        if title == None:
            self.win.wm_title("scatter@%s:"%os.getenv('HOSTNAME'))
        else:
            self.win.wm_title(title)
        self.canvas = Canvas(self.win,width=width,height=height)
        self.canvas.pack()
        self.xBorder = 30
        self.yBorder = 30
        self.plotHeight = height - 2 * self.yBorder # / max value
        self.plotWidth =  self.plotHeight # / max value
        # width - 2 * self.xBorder # / max value
        # background
        self.canvas.create_rectangle(self.xBorder, self.yBorder,
                                     self.xBorder + self.plotWidth,
                                     height - self.yBorder,
                                     width = 1, fill='white')
        # title
        self.canvas.create_text(width / 2.0, 13,
                                text=title, fill='black')
        # legend
        for i in range(linecount):
            self.canvas.create_rectangle(self.xBorder + self.plotWidth + 5,
                                         self.yBorder + i * 20,
                                         self.xBorder + self.plotWidth + 5 + 15,
                                         self.yBorder + i * 20 + 15,
                                         width = 1, fill=self.color[i])
            self.canvas.create_text(self.xBorder + self.plotWidth + 5 + 20,
                                    self.yBorder + i * 20 + 8,
                                    text=legend[i], fill='black',
                                    anchor='w')

        # markers
        self.canvas.create_line(self.xBorder - 5, self.yBorder,
                                self.xBorder + 5, self.yBorder,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder - 5,
                                self.yBorder + self.plotHeight / 2,
                                self.xBorder + 5,
                                self.yBorder + self.plotHeight / 2,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder - 5, height - self.yBorder,
                                self.xBorder + 5, height - self.yBorder,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder, height - self.yBorder - 5,
                                self.xBorder, height - self.yBorder + 5,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder + self.plotWidth / 2,
                                height - self.yBorder - 5,
                                self.xBorder + self.plotWidth / 2,
                                height - self.yBorder + 5,
                                width = 2, fill='black')
        self.canvas.create_line(self.xBorder + self.plotWidth,
                                height - self.yBorder - 5,
                                self.xBorder + self.plotWidth,
                                height - self.yBorder + 5,
                                width = 2, fill='black')
        # text
        self.canvas.create_text(self.xBorder, height - 10,
                                text='0.0', fill='black')
        self.canvas.create_text(self.xBorder + self.plotWidth / 2, height - 10,
                                text='0.5', fill='black')
        self.canvas.create_text(self.xBorder + self.plotWidth, height - 10,
                                text='1.0', fill='black')
        self.canvas.create_text(10, self.yBorder, text='1.0', fill='black')
        self.canvas.create_text(10, self.yBorder + self.plotHeight / 2,
                                text='0.5', fill='black')
        self.canvas.create_text(10, height - self.yBorder,
                                text='0.0', fill='black')
        # ----------------------------------------------------------
        self.lineCount = linecount
        self.hist = [0] * linecount # actual hist of line
        self.history = history[:] # history counts for each line
        self.firstEver = [0] * linecount
        self.last = [0] * linecount
        self.count = [0] * linecount
        for i in range(linecount):
            self.hist[i] = [0] * history[i]
            self.firstEver[i] = 1
            self.last[i] = 0
            self.count[i] = 0
    def setTitle(self, title):
        self.win.wm_title(title)

    def _x(self, val):
        return int(val * self.plotWidth) + self.xBorder

    def _y(self, val):
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
            self.last[line].pointId = self.canvas.create_oval(last_x - 2,
                                                        last_y - 2,
                                                        last_x + 2,
                                                        last_y + 2,
                                                        width = 0,
                                                        tag = 'object',
                                                        fill = 'coral')
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

if __name__ == '__main__':
    sp = Scatter()
    for y in range(100):
        for x in range(10):
            sp.addPoint(x/10.0, x/10.0)
    sp.win.mainloop()
