import Tkinter

class GUI(Tkinter.Toplevel):
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)
        self.done = 0
        self.quit = 0
        self.root = root
        self.width = width
        self.height = height
        self.title("SymbolicServer")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height)
        self.canvas.pack()
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)
        self.world = {"A": ("Dirty",), "B": ("Clean",)}
        self.location = "A"
        self.redraw()

    def process(self, request):
        retval = "error"
        if request == 'move':
            if self.location == 'A':
                self.location = 'B'
            else:
                self.location = 'A'
            retval = "ok"
        elif request == 'location':
            retval = self.location
        elif request == 'status':
            retval = self.world[self.location]
        elif request == 'end':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        else:
            # unknown command
            pass
        self.redraw()
        return retval

    def redraw(self):
        self.canvas.delete('all')
        #if self.location == 'A':
        #else:

    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 400, 200)
