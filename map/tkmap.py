from pyro.map import Map
import Tkinter
import pyro.gui.widgets.TKwidgets as TKwidgets
import pyro.system as system
import pyro.gui.console as console

class TkMap(Map, Tkinter.Tk):
    """ Map with Tkinter GUI functions """

    def __init__(self, cols, rows, value,
                 width, height,
                 widthMM, heightMM, title, menu = None, keybindings = []):
        """ TkMap extends Map and Tkinter """
        Map.__init__(self, cols, rows, widthMM, heightMM)
        Tkinter.Tk.__init__(self)
        self.title(title)
        if menu == None:
            menu = [('File',[['Exit',self.destroy]])]
        keybindings.append( ("<Configure>", self.changeSize))
        self.menuButtons = {}
        self.debug = 0
        self.application = 0
        self.width = width
        self.height = height
        self.colScale = self.width / self.cols
        self.rowScale = self.height / self.rows
        self.addMenu(menu)
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height)
        self.canvas.pack()
        self.addKeyBindings(keybindings)
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self.update_idletasks()
        self.canvas.focus_set()

    def addKeyBindings(self, keybindings):
        """ Bind keys and mice events to the canvas """
        for keyname, func in keybindings:
            self.canvas.bind(keyname, func)

    def addMenu(self, menu):
        """ Create a menu """
        self.mBar = Tkinter.Frame(self,relief=Tkinter.RAISED,borderwidth=2)
        self.mBar.pack(fill=Tkinter.X)
        for entry in menu:
            self.mBar.tk_menuBar(self.makeMenu(self.mBar, entry[0],entry[1]))

    def makeMenu(self, bar, name, commands):
        """ Assumes self.menuButtons exists """
        menu = Tkinter.Menubutton(bar,text=name,underline=0)
        self.menuButtons[name] = menu
        menu.pack(side=Tkinter.LEFT,padx="2m")
        menu.filemenu = Tkinter.Menu(menu)
        for cmd in commands:
            menu.filemenu.add_command(label=cmd[0],command=cmd[1])
        menu['menu'] = menu.filemenu
        return menu

    def changeSize(self, event = 0):
        self.width = self.winfo_width() - 2
        self.height = self.winfo_height() - 30
        self.canvas.configure(width = self.width, height = self.height)
        self.colScale = self.width / self.cols
        self.rowScale = self.height / self.rows
        self.redraw()

    def setGrid(self, grid):
        Map.setGrid(self, grid)
        self.changeSize()

    def destroy(self):
        self.withdraw()
        self.update_idletasks()
        if self.application:
            Tkinter.Tk.destroy(self)

    def redraw(self):
        print "warn: Need to overload redraw() from TkMap class"
        print "colScale: %f, rowScale: %f" % (self.colScale, self.rowScale)

    def fileloaddialog(self, filetype, skel, startdir = ''):
        from string import replace
        import pyro
        from os import getcwd, getenv, chdir
        retval = ""
        cwd = getcwd()
        if startdir == '':
            chdir(pyro.pyrodir() + "/plugins/" + filetype)
        else:
            chdir(startdir)
        d = TKwidgets.LoadFileDialog(self, "Load " + filetype, skel)
        if d.Show() == 1:
            doc = d.GetFileName()
            d.DialogCleanup()
            retval = doc
        else:
            d.DialogCleanup()
        chdir(cwd)
        return retval

    def loadMap(self):
        f = self.fileloaddialog("maps","*.py")
        if f != '':
            self.loadMapFile(f)

    def loadMapFile(self, file):
        import os
        if file[-3:] != '.py':
            file = file + '.py'
        if system.file_exists(file):
            grid = system.loadINIT(file)
        elif system.file_exists(os.getenv('PYRO') + \
                                '/plugins/maps/' + file): 
            grid = system.loadINIT(os.getenv('PYRO') + \
                                   '/plugins/plots/' + file)
        else:
            raise 'Map file not found: ' + file
        self.setGrid(grid)

    def saveMap(self):
        pass

if __name__ == '__main__':
    print "Testing TkMap()..."
    map = TkMap(8, 10, .5, 200, 200, 500, 1000, "Sample Map")
    map.display()
    map.reset()
    map.display()
    print "Setting Grid location..."
    map.setGridLocation(400, 900, 1.0, "A")
    map.validateGrid()
    print "Setting Grid to new size..."
    map.setGrid( [[0, 0, 0],
                  [0, 1, 0],
                  [0, 0, 0],
                  [1, 0, 0]] )
    map.validateGrid()
    map.display()
    print "All done!"
    map.application = 1
    map.mainloop()