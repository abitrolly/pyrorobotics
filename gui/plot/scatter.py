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
                 title = None, width = 150, height = 150):
        self.win = Tk()
        if title == None:
            self.win.wm_title("scatter@%s:"%os.getenv('HOSTNAME'))
        else:
            self.win.wm_title(title)
        self.canvas = Canvas(self.win,width=width,height=height)
        self.canvas.pack()
        # border 
        self.canvas.create_line(30, 30, 30, 130, width = 1, fill='black')
        self.canvas.create_line(30, 30, 130, 30, width = 1, fill='black')
        self.canvas.create_line(30, 130, 130, 130, width = 1, fill='black')
        self.canvas.create_line(130, 30, 130, 130, width = 1, fill='black')
        # markers
        self.canvas.create_line(25, 30, 35, 30, width = 2, fill='black')
        self.canvas.create_line(25, 80, 35, 80, width = 2, fill='black')
        self.canvas.create_line(25, 130, 35, 130, width = 2, fill='black')
        self.canvas.create_line(30, 25, 30, 35, width = 2, fill='black')
        self.canvas.create_line(80, 25, 80, 35, width = 2, fill='black')
        self.canvas.create_line(130, 25, 130, 35, width = 2, fill='black')
        # text
        self.canvas.create_text(10, 30, text='0.0', fill='black')
        self.canvas.create_text(10, 80, text='0.5', fill='black')
        self.canvas.create_text(10, 130, text='1.0', fill='black')
        self.canvas.create_text(30, 10, text='0.0', fill='black')
        self.canvas.create_text(80, 10, text='0.5', fill='black')
        self.canvas.create_text(130, 10, text='1.0', fill='black')
        # ----------------------------------------------------------
        self.hist = [0] * history
        self.history = history
        self.count = 0
        self.offset = 30
        self.firstEver = 1
        self.last = 0

    def setTitle(self, title):
        self.win.wm_title(title)
        
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
            self.last.pointId = self.canvas.create_oval(int(x1 * 100.0) - 2 + self.offset,
                                                        int(y1 * 100.0) - 2 + self.offset,
                                                        int(x1 * 100.0) + 2 + self.offset,
                                                        int(y1 * 100.0) + 2 + self.offset,
                                                        width = 0,
                                                        tag = 'object',
                                                        fill = 'coral')

        if self.firstEver:
            self.firstEver = 0
            lid = -1
        else:
            lid = self.canvas.create_line(int(self.last.x * 100.0) +self.offset,
                                          int(self.last.y * 100.0) +self.offset,
                                          int(x * 100.0) + self.offset,
                                          int(y * 100.0)+ self.offset,
                                          width = 1,
                                          tag = 'object',
                                          fill = 'tan')
        pid = self.canvas.create_oval(int(x * 100.0) - 3 + self.offset,
                                      int(y * 100.0) - 3 + self.offset,
                                      int(x * 100.0) + 3 + self.offset,
                                      int(y * 100.0) + 3 + self.offset,
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
