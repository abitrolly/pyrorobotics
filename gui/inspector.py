
import Tkinter
import types
import pyro.system.share as share

class Inspector(Tkinter.Tk):

    def __init__(self, root = None):
        Tkinter.Tk.__init__(self)
        # first the obj window:
        leftFrame = Tkinter.Frame(self)
        leftFrame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 
                        'fill' :'both'})
        frame = Tkinter.Frame(leftFrame)
        frame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 
                    'fill' :'both'})
        frame['relief'] = 'raised'
        frame['bd']	 = '2'
        filesFrame = Tkinter.Frame(frame)
        filesFrame['relief'] = 'flat'
        filesFrame['bd']	 = '2'
        filesFrame.pack({'side':'top', 'expand':'yes', 'fill':'y'})
        label = Tkinter.Label(filesFrame)
        label['text'] = 'Objects:'
        label.pack({'side':'top', 'expand':'no', 'anchor':'w',
                    'fill':'none'})
        scrollBar = Tkinter.Scrollbar(filesFrame, {'orient':'vertical'})
        scrollBar.pack({'expand':'no', 'side':'right', 'fill':'y'})
        self.dirLb = Tkinter.Listbox(filesFrame, {'yscroll':scrollBar.set})
        self.dirLb.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
                         'fill' :'both'})
        self.dirLb.bind('<Button-1>', self.selectItem)
        scrollBar['command'] = self.dirLb.yview

        # methods:
        frame = Tkinter.Frame(leftFrame)
        frame.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
                    'fill' :'both'})
        frame['relief'] = 'raised'
        frame['bd']	 = '2'
        filesFrame = Tkinter.Frame(frame)
        filesFrame['relief'] = 'flat'
        filesFrame['bd']	 = '2'
        filesFrame.pack({'side':'top', 'expand':'yes', 'fill':'x'})
        # Methods:
        label = Tkinter.Label(filesFrame)
        label['text'] = 'Methods:'
        label.pack({'side':'top', 'expand':'no', 'anchor':'w',
                    'fill':'none'})
        scrollBar = Tkinter.Scrollbar(filesFrame, {'orient':'vertical'})
        scrollBar.pack({'expand':'yes', 'side':'right', 'fill':'y'})
        self.methods = Tkinter.Listbox(filesFrame, {'yscroll':scrollBar.set})
        self.methods.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
                           'fill' :'both'})
        # variables:
        frame = Tkinter.Frame(leftFrame)
        frame.pack({'expand':'yes', 'side' :'bottom', 'pady' :'1', 
                    'fill' :'both'})
        frame['relief'] = 'raised'
        frame['bd']	 = '2'
        filesFrame = Tkinter.Frame(frame)
        filesFrame['relief'] = 'flat'
        filesFrame['bd']	 = '2'
        filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
        # Variables:
        label = Tkinter.Label(filesFrame)
        label['text'] = 'Variables:'
        label.pack({'side':'top', 'expand':'no', 'anchor':'w',
                    'fill':'none'})
        scrollBar = Tkinter.Scrollbar(filesFrame, {'orient':'vertical'})
        scrollBar.pack({'expand':'yes', 'side':'right', 'fill':'y'})
        self.variables = Tkinter.Listbox(filesFrame, {'yscroll':scrollBar.set})
        self.variables.pack({'expand':'yes', 'side' :'bottom', 'pady' :'1', 
                             'fill' :'both'})        

        # help text:
        frame = Tkinter.Frame(self)
        frame.pack({'expand':'yes', 'side' :'right', 'pady' :'1', 
                    'fill' :'both'})
        frame['relief'] = 'raised'
        frame['bd']	 = '2'
        filesFrame = Tkinter.Frame(frame)
        filesFrame['relief'] = 'flat'
        filesFrame['bd']	 = '2'
        filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
        label = Tkinter.Label(filesFrame)
        label['text'] = 'Help:'
        label.pack({'side':'top', 'expand':'yes', 'anchor':'w',
                    'fill':'none'})
        # help:
        scrollBar = Tkinter.Scrollbar(filesFrame, {'orient':'vertical'})
        scrollBar.pack({'expand':'no', 'side':'right', 'fill':'y'})
        self.helptext = Tkinter.Text(filesFrame, {'yscroll':scrollBar.set, "width": 70})
        self.helptext.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
                            'fill' :'both'})        

        self.methods.bind('<Button-1>', self.methodItem)
        self.variables.bind('<Button-1>', self.variableItem)

        if root == None:
            root = dir()
        for thing_s in root:
            self.dirLb.insert('end', thing_s)

    def showHelp(self, thing_s):
        self.helptext.delete(1.0, 'end')
        exec "thing = %s" % thing_s
        if thing.__doc__:
            self.helptext.insert('end', thing.__doc__)
        else:
            self.helptext.insert('end', "")

    def loadItems(self, thing_s):
        self.methods.delete(0, self.methods.size())
        self.variables.delete(0, self.variables.size())
        self.helptext.delete(1.0, 'end')
        exec "thing = %s" % thing_s
        if thing.__doc__:
            self.helptext.insert('end', thing.__doc__)
        else:
            self.helptext.insert('end', "")
        for subthing_s in dir(thing):
            if subthing_s[0] == '_': continue
            exec "subthing = %s.%s" % (thing_s, subthing_s)
            if type(subthing) == types.MethodType:
                self.methods.insert('end', subthing_s)
            else:
                self.variables.insert('end', subthing_s)

    def selectItem(self, event):
        lb = event.widget
        self.currentObject = lb.get(lb.nearest(event.y))
        self.loadItems(self.currentObject)

    def methodItem(self, event):
        lb = event.widget
        self.showHelp(self.currentObject + "." + lb.get(lb.nearest(event.y)))

    def variableItem(self, event):
        lb = event.widget
        self.showHelp(self.currentObject + "." + lb.get(lb.nearest(event.y)))

if __name__ == '__main__':
    class Testing:
        """ This is the class Testing"""
        var1 = 56
        def __init__(self):
            pass
        def methd1(self):
            """method 1 test"""
            pass
    testing = Testing()
    ins = Inspector(('testing', ))
    ins.mainloop()
