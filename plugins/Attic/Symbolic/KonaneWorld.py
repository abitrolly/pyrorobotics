import Tkinter, os, random, pickle
import Image, ImageTk, ImageDraw, ImageFont 

class GUI(Tkinter.Toplevel):
    """
    Konane: Hawaiian Checkers
    """
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)
        self.done = 0
        self.quit = 0
        self.root = root
        self.width = width
        self.height = height
        self.visible = 1
        self.title("SymbolicSimulator: WumpusWorld")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height,bg="white")
        self.canvas.pack()
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)
        self.initWorld()
        self.count = 0
        self.tag = "data-%d" % self.count
        self.updateables = []
        self.notSetables = ["world"]
        self.movements = ["remove", "move"]
        self.ports = [60000, 60001]
        self.redraw()

    def initWorld(self):
        self.world = [['' for y in range(8)] for x in range(8)]
        for x in range(0, 8):
            for y in range(0, 8):
                if x % 2 == y % 2:
                    self.world[x][y] = 'O'
                else:
                    self.world[x][y] = 'X'

    def process(self, request):
        retval = "error"
        if 'remove' in request:
            request = request.replace(")", "")
            remove, pos = request.split("(")
            x,y = map(int, pos.split(","))
            self.world[x-1][y-1] = ''
            retval = "ok"
            self.redraw()
        elif 'connectionNum' in request:
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request == 'world':
            retval = self.world
        elif request == 'reset':
            self.initWorld()
            retval = "ok"
            self.redraw()
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == 'updateables':
            retval = self.updateables
        elif request == 'notsetables':
            retval = self.notSetables
        elif request == 'movements':
            retval = self.movements
        else:   # unknown command; returns "error"
            pass
        return pickle.dumps(retval)

    def redraw(self):
        oldtag = self.tag
        self.count = int(not self.count)
        self.tag = "data-%d" % self.count
        for x in range(8):
            for y in range(8):
                posx = x * (self.width / 8) + self.width/8/2
                posy = self.height - (self.height/8/2) - y * (self.height / 8)
                self.canvas.create_text(posx, posy, text = self.world[x][y], fill = "red", tag = self.tag, font = ("times", 31))
        # ------------------------------------------------------------------------        
        self.canvas.create_line(  2,   2,   2, self.height, width = 2, fill = "black", tag = self.tag)
        self.canvas.create_line(  2,   2, self.width,   2, width = 2, fill = "black", tag = self.tag)
        for i in range(1,  8 + 1):
            self.canvas.create_line(i * self.width/8,   0, i * self.width/8, self.height, width = 2, fill = "black", tag = self.tag)
        for i in range(1,  8 + 1):
            self.canvas.create_line(  0, i * self.height/8, self.width, i * self.height/8, width = 2, fill = "black", tag = self.tag)
        # ------------------------------------------------------------------------        
        self.canvas.delete(oldtag)
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 600, 600)
