import Tkinter, os, random
import Image, ImageTk, ImageDraw, ImageFont 

class GUI(Tkinter.Toplevel):
    """
    A simple world from Russell and Norvig's AIMA. This works
    in tandom with SymbolicServer.
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
        # sensors: Stench, Breeze, Glitter, Bump, Scream
        self.goldFilename = os.environ["PYRO"] + "/images/gold.gif" 
        self.wumpusFilename = os.environ["PYRO"] + "/images/wumpus.gif" 
        self.pitFilename = os.environ["PYRO"] + "/images/pit.gif"
        self.agentFilename = os.environ["PYRO"] + "/images/agent.gif" 
        # --------------------------------------------------------
        self.goldImage = Image.open(self.goldFilename)
        self.goldImage = self.goldImage.resize( (100, 25), Image.BILINEAR )
        self.wumpusImage = Image.open(self.wumpusFilename)
        self.wumpusImage = self.wumpusImage.resize( (100, 100), Image.BILINEAR )
        self.pitImage = Image.open(self.pitFilename)
        self.pitImage = self.pitImage.resize( (100, 100), Image.BILINEAR )
        self.agentImage = Image.open(self.agentFilename)
        self.agentImage = self.agentImage.resize( (100, 100), Image.BILINEAR )
        # --------------------------------------------------------
        self.goldImageTk = ImageTk.PhotoImage(self.goldImage)
        self.wumpusImageTk = ImageTk.PhotoImage(self.wumpusImage)
        self.pitImageTk = ImageTk.PhotoImage(self.pitImage)
        self.agentImageTk = ImageTk.PhotoImage(self.agentImage)
        # --------------------------------------------------------
        self.initWorld()
        self.checkMovement()
        self.redraw()

    def initWorld(self):
        self.direction = "Right"
        self.location = (0, 0)
        self.dead = 0
        self.score = 0
        self.arrow = 1
        self.wumpusDead = 0
        self.bump = 0
        self.stench = 0
        self.breeze = 0
        self.gold = 0
        self.scream = 0
        self.world = [['' for y in range(4)] for x in range(4)]
        # ''  = nothing
        # 'W' = wumpus
        # 'G' = gold
        # 'P' = pit
        # 'A' = agent
        for x in range(1, 4):
            for y in range(1, 4):
                if random.random() < .20:
                    self.world[x][y] = 'P'
        self.world[ random.randint(1, 3) ][ random.randint(1, 3)] += 'G'
        self.world[ random.randint(1, 3) ][ random.randint(1, 3)] += 'W'

    def add(self, loc, dir):
        x = 0
        if loc[0] + dir[0] >= 0 and loc[0] + dir[0] < 4:
            x = loc[0] + dir[0]
        else:
            x = loc[0]
            self.bump = 1
        if loc[1] + dir[1] >= 0 and loc[1] + dir[1] < 4:
            y = loc[1] + dir[1]
        else:
            y = loc[1]
            self.bump = 1
        self.location = (x, y)

    def checkMovement(self):
        if ('W' in self.world[self.location[0]][self.location[1]] and not self.wumpusDead) or \
               'P' in self.world[self.location[0]][self.location[1]]:
            self.dead = 1
            self.score -= 1000
            return "you died a miserable death!"
        self.stench = self.nearby(self.location, 'W')
        self.breeze = self.nearby(self.location, 'P')
        self.gold = self.nearby(self.location, 'G')
        # bump computed when you move
        # scream computed when you shoot
        return "ok"

    def nearby(self, loc, ch):
        for x,y in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            xpos, ypos = loc[0] + x, loc[1] + y
            if ypos >= 0 and ypos < 4 and xpos >= 0 and xpos < 4:
                if ch in self.world[xpos][ypos]:
                    return 1
        return 0

    def inLine(self, loc, change):
        xpos, ypos = self.sum(loc , change)
        while ypos >= 0 and ypos < 4 and xpos >= 0 and xpos < 4:
            if 'W' in self.world[xpos][ypos]:
                self.wumpusDead = 1
                self.scream = 1
                self.world[xpos][ypos] = self.world[xpos][ypos].replace('W', '')
            xpos, ypos = self.sum((xpos,ypos), change)

    def sum(self, a, b):
        return a[0] + b[0], a[1] + b[1]
    
    def process(self, request):
        # moves: 'Forward', 'Left', 'Right', 'Grab', 'Shoot'
        dirs = {'Up':0, 'Right':1, 'Down':2, 'Left':3}
        pos  = {0:'Up', 1:'Right', 2:'Down', 3:'Left'}
        retval = "error"
        if request == 'Location':
            retval = "(%d,%d)" % (self.location[0] + 1, self.location[1] + 1)
        elif request == 'Direction':
            retval = self.direction
        elif request == 'Arrow':
            retval = "%d" % self.arrow
        elif request == 'score':
            retval = "%d" % self.score
        elif request == 'reset':
            self.initWorld()
            retval = "ok"
        elif request == 'end' or request == 'exit':
            retval = "ok"
            self.done = 1
        elif request == 'quit':
            retval = "ok"
            self.done = 1
            self.quit = 1
        elif request == 'percept':
            retval = "(%s, %s, %s, %s, %s)" % ({1:"Stench", 0:"None"}[self.stench],
                                               {1:"Breeze", 0:"None"}[self.breeze],
                                               {1:"Glitter", 0:"None"}[self.gold],
                                               {1:"Bump", 0:"None"}[self.bump],
                                               {1:"Scream", 0:"None"}[self.scream])
        elif self.dead:
            retval = "you died a miserable death!"
        elif request == 'Left': # ------------------------below here, you are alive!
            self.bump = 0
            self.scream = 0
            self.score -= 1
            self.direction = pos[(dirs[self.direction] - 1) % 4]
            retval = self.checkMovement()
        elif request == 'Shoot':
            # shoot arrow
            self.scream = 0
            if self.arrow:
                self.arrow = 0
                self.score -= 10
                if self.direction == 'Up':
                    self.inLine( self.location, (0, 1) )
                elif self.direction == 'Right':
                    self.inLine( self.location, (1, 0) )
                elif self.direction == 'Left':
                    self.inLine( self.location, (-1, 0) )
                elif self.direction == 'Down':
                    self.inLine( self.location, (0, -1) )
                retval = 'ok'
        elif request == 'Grab':
            if 'G' in self.world[self.location[0]][self.location[1]]:
                self.score += 1000
                self.world[self.location[0]][self.location[1]] = self.world[self.location[0]][self.location[1]].replace('G','')
                retval = "you win"
        elif request == 'Right':
            self.bump = 0
            self.scream = 0
            self.score -= 1
            self.direction = pos[(dirs[self.direction] + 1) % 4]
            retval = self.checkMovement()
        elif request == 'Forward':
            self.bump = 0
            self.scream = 0
            self.score -= 1
            if self.direction == 'Up':
                self.add( self.location, (0, 1) )
            elif self.direction == 'Right':
                self.add( self.location, (1, 0) )
            elif self.direction == 'Left':
                self.add( self.location, (-1, 0) )
            elif self.direction == 'Down':
                self.add( self.location, (0, -1) )
            retval = self.checkMovement()
        else:   # unknown command; returns "error"
            pass
        self.redraw()
        return retval

    def redraw(self):
        self.canvas.delete('all')
        for x in range(4):
            for y in range(4):
                posx = x * 100
                posy = 300 - y * 100
                if self.location[0] == x and self.location[1] == y:
                    self.canvas.create_image(posx, posy, image = self.agentImageTk, anchor=Tkinter.NW)
                if 'P' in self.world[x][y]:
                    self.canvas.create_image(posx, posy, image = self.pitImageTk, anchor=Tkinter.NW)
                if 'W' in self.world[x][y]:
                    self.canvas.create_image(posx, posy, image = self.wumpusImageTk, anchor=Tkinter.NW)
                if 'G' in self.world[x][y]:
                    self.canvas.create_image(posx, posy + 75, image = self.goldImageTk, anchor=Tkinter.NW)
        self.canvas.create_line(  2,   2,   2, 400, width = 2, fill = "black")
        self.canvas.create_line(100,   0, 100, 400, width = 2, fill = "black")
        self.canvas.create_line(200,   0, 200, 400, width = 2, fill = "black")
        self.canvas.create_line(300,   0, 300, 400, width = 2, fill = "black")
        self.canvas.create_line(400,   0, 400, 400, width = 2, fill = "black")
        # ------------------------------------------------------------------------
        self.canvas.create_line(  2,   2, 400,   2, width = 2, fill = "black")
        self.canvas.create_line(  0, 100, 400, 100, width = 2, fill = "black")
        self.canvas.create_line(  0, 200, 400, 200, width = 2, fill = "black")
        self.canvas.create_line(  0, 300, 400, 300, width = 2, fill = "black")
        self.canvas.create_line(  0, 400, 400, 400, width = 2, fill = "black")
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 400, 400)
