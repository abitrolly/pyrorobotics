import Tkinter, os, random, pickle
import Image, ImageTk, ImageDraw, ImageFont 
from Numeric import resize
from string import atof, atoi
import itertools

class GUI(Tkinter.Toplevel):
    """
    A simple world from Russell and Norvig's AIMA. This works
    with SymbolicSimulator.
    """
    def __init__(self, root, width, height):
        Tkinter.Toplevel.__init__(self, root)

        self.inaccessible = [(-1,-1),\
                             ( 4, 2),( 5, 2),( 6, 2),( 4, 3),( 5, 3),( 6, 3),\
                             ( 9, 2),(10, 2),(11, 2),( 9, 3),(10, 3),(11, 3),( 9, 4),(10, 4),(11, 4),\
                             (13, 1),(14, 1),(13, 2),(14, 2),(13, 3),(14, 3),(13, 4),(14, 4),\
                             (3,6),(4,6),(5,6),(3,7),(4,7),(5,7),(3,8),(4,8),(5,8),(3,9),(4,9),(5,9),\
                             (7,6),(8,6),     (7,7),(8,7),     (7,8),(8,8),    \
                             (6,9),(7,9),(8,9),     (6,10),(7,10),(8,10),(9,10),(10,10),(6,11),(7,11),\
                             (8,11),(9,11),(10,11),(6,12),(7,12),(8,12),(9,12),(6,13),(7,13),(8,13),\
                             (11,6),(12,6),(13,6),(11,7),(12,7),(13,7),(11,8),(12,8),(13,8),\
                             (0,11),(1,11),(2,11),(0,12),(1,12),(2,12),(0,13),(1,13),(2,13),(0,14),(1,14),(2,14)];
    
	self.path_color        = "#5ee563"
	self.visited_color     = "#c5c5c5"
        self.current_pos_color = "#00AF32"
	self.inaccessible_color= "black"
	self.gridline_color    = "black"
	self.background_color  = "white"

        self.path    = []
        self.visited = []
	self.pits    = []
	self.goal    = []

	self.goal_id = -1
	self.pit_ids = []

        # how many states ?
        self.num_squares_x = 15
        self.num_squares_y = 15

        self.utility     = resize( 0.0,(self.num_squares_x,self.num_squares_y)); 
        self.reward      = resize( 0.0,(self.num_squares_x,self.num_squares_y)); 
        self.squares     = resize(   0,(self.num_squares_x,self.num_squares_y)); 
        self.frequencies = resize(   0,(self.num_squares_x,self.num_squares_y));

        # various object members
        self.done    = 0
        self.quit    = 0
        self.moves   = 0
        self.root    = root
        self.width   = width
        self.height  = height
        self.complete = 0
        self.alpha = 0.2
        self.count = 1


        # various tk objects
        self.title("SymbolicSimulator: RLWorld")
        self.canvas = Tkinter.Canvas(self,width=self.width,height=self.height,bg="white")
        self.canvas.pack()
        self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.destroy)

        # set height and width of images
        self.square_height = self.width  / self.num_squares_x;
        self.square_width  = self.height / self.num_squares_y;

        # goal image
        goldFilename = os.environ["PYROBOT"] + "/images/rlgoal.gif" 
        goldImage = Image.open(goldFilename)
        goldImage = goldImage.resize( [self.square_height-2, self.square_width-2] )
        self.goldImageTk = ImageTk.PhotoImage(goldImage)

        # pit image
        pitFilename = os.environ["PYROBOT"] + "/images/rlpit.gif" 
        pitImage = Image.open(pitFilename)
        pitImage = pitImage.resize( [self.square_height-2, self.square_width-2] )
        self.pitImageTk = ImageTk.PhotoImage(pitImage, height=self.square_height, width=self.square_width)

	for i in range(0, self.num_squares_x):
	  for j in range(0, self.num_squares_y):
            self.squares[i][j] = self.canvas.create_rectangle( i*self.square_width, j*self.square_height,
                            	        (i+1)*self.square_width - 1, (j+1)*self.square_height - 1,
                                	fill= self.background_color, tag = "square-%d-%d" % (i,j));

        # initialize the world
        self.initWorld()
        self.resetStates()
        self.resetUtils()
        
        # used by simulator
        self.properties = ["location", "obstacles", "goal", "home", \
                           "final", "visited", "complete", "alpha", \
                           "pits", "count", "path"]

        self.movements = ["up", "right", "down", "left", "td"]
        self.ports = [60000]

        # start things off
        self.redraw()
        self.drawInaccessible()

    def resetUtils(self):
#        self.utility = resize(array(0.0),(self.num_squares_x,self.num_squares_y)); 
 	for i in range(0, self.num_squares_x):
          for j in range(0, self.num_squares_y):
             self.utility[i][j] = 0.0       

        for e in self.inaccessible:
            self.utility[e] = -1.0
        for e in self.pits:
            self.utility[e] = -1.0
        e = self.goal
        self.utility[e] = 1.0

        # used for Temporal Differencing
#        self.reward = resize(array(-5.0),(self.num_squares_x,self.num_squares_y))
 	for i in range(0, self.num_squares_x):
          for j in range(0, self.num_squares_y):
             self.reward[i][j] = 0.0       

        self.reward[self.goal] = 100
        for e in self.pits:
            self.reward[e] = -50
            
    def resetStates(self):
        # various states
        self.home = (0, 0)
        self.location = (0, 0)
       
        num_pits = random.randrange(5) + 1

#        self.pits = []
        del self.pits[0:]

        for i in range(num_pits):
            self.pits.append( (random.randrange(self.num_squares_x), random.randrange(self.num_squares_y)) )
            
        self.goal = []

        while self.goal == [] or self.goal in self.inaccessible or self.goal in self.pits:
            self.goal = (random.randrange(self.num_squares_x), random.randrange(self.num_squares_y))


        self.final_states = [self.goal] + self.pits

        

    def initWorld(self):
        self.completed = 0
        self.location = (0, 0)

        del self.path[0:]
        del self.visited[0:]
#        self.path    = []
#        self.visited = []


    def change_Alpha( new_val ):
        self.alpha = new_val
        
    def running_average( self, util, reward, freq ):
        return ((util * (freq - 1) + reward) / freq)
   
    def Temporal_Difference( self, U, p, frequencies ):
        final_state = self.final_states

        # we want to traverse in reverse!
        p.reverse();
        next_state = p[0]
        # start from end, go until start
        for curr_state in p:
            # update the frequencies of all states in the path
            frequencies[curr_state] = frequencies[curr_state] + 1
            
            if( curr_state in self.final_states ):
                rew = self.reward[curr_state] - (len(p) * 0) # 2)
                U[curr_state] = round( self.running_average( U[curr_state],
                                                            self.reward[curr_state],
                                                            frequencies[curr_state] ), 10) ;
            else:
                temp = U[next_state]-U[curr_state];
                U[curr_state] = round(U[curr_state] + self.alpha*(self.reward[curr_state] + temp), 10);
                
            # since we're iterating backwards
            next_state = curr_state;


#        return U;

    # checks the current motion, if it is valid the location will be changed, otherwise no change
    def add(self, loc, dir):
        x = 0

        if (loc[0] + dir[0],loc[1] + dir[1]) in self.inaccessible:
            x = loc[0]
            y = loc[1]

        else:
            if loc[0] + dir[0] >= 0 and loc[0] + dir[0] < self.num_squares_x:
                x = loc[0] + dir[0]
            else:
                x = loc[0]
            if loc[1] + dir[1] >= 0 and loc[1] + dir[1] < self.num_squares_y:
                y = loc[1] + dir[1]
            else:
                y = loc[1]
            
        self.location = (x, y)

    # check if we are at the goal state
    def checkMovement(self):        
        xloc = self.location[0]
        yloc = self.location[1]

        if ( (xloc,yloc) in self.final_states ):
            return "Success!"

        return "ok0"

    # removes all elements in path after el
    def removeAfter(self, el,path):
        if len(path) <= 1:
            return path

        path.reverse()
        path = list(itertools.dropwhile(lambda n: not el == n, path))[1:]
        path.reverse()

        return path

    # returns a list of all elements in l1 that are not in l2
    def getDifferences(self, l1, l2):
        dl = []
        for e in l1:
            if not(e in l2):
                dl.append(e)
        return dl

    # adds a new location to the current path, and removes new loops in the process
    def addToPath( self, el ):
        path = self.path

        # removes loops -- they're not significant
        if len(path) == 0:
            pass
        elif path[len(path)-1] == el:
            return

        if el in path:
            path = self.removeAfter( el, path )
            # self.erasePath( self.getDifferences( self.path, path ) )
            self.redrawVisited()
        path.append(el)


        if el in self.final_states:
            self.complete = 1
        else:
            self.complete = 0

        if( not( el in self.visited ) ):
            self.visited.append( el )
        self.path = path

    # process incoming requests
    def process(self, request, sockname ):
        if request != 'location' and 'location' in request:
            request = 'location'
        elif request != 'moves' and 'moves' in request:
            request = 'moves'
        # moves: 'up', 'right', 'down', 'left'
        retval = "error"

        if request.count('connectionNum'):
            connectionNum, port = request.split(":")
            retval = self.ports.index( int(port) )
        elif request[0:6] == "alpha=" :
            self.alpha = atof(request[6:10])
            retval = self.alpha
        elif request[0:7] == "utility" :
            temp= (atoi(request[7:9]), atoi(request[9:11]))
            retval = self.utility[temp]
        elif request == 'location':
            self.addToPath(self.location)
            retval = self.location[0], self.location[1]
        elif request == 'complete':
            retval = self.complete
        elif request == 'count':
            retval = self.count
        elif request == 'path':
            retval = self.path
        elif request == 'alpha':
            retval = self.alpha
        elif request == 'final':
            retval = self.final_states
        elif request == 'obstacles':
            retval = self.inaccessible

        elif request == 'visited':
            retval = self.visited

        elif request == 'incAlpha':
            self.alpha += .1
            retval = (self.alpha)
        elif request == 'td':
            self.addToPath(self.location)

            self.Temporal_Difference(self.utility, self.path, self.frequencies)
            self.initWorld()
            self.redrawUtilities()
            self.count = self.count + 1
            retval = "okTD"
        elif request == 'goal':
            retval = (self.goal)
        elif request == 'pits':
            retval = (self.pits)
        elif request == 'home':
            retval = (self.home)
        elif request == 'reset':
            print "RESET!!"
            self.initWorld()
            self.resetStates()
            self.resetUtils()
            retval = "reset complete"
            self.redraw()
            self.drawInaccessible()
        elif request == 'end' or request == 'exit':
            retval = "exiting"
            self.done = 1
        elif request == 'quit':
            retval = "quitting"
            self.done = 1
            self.quit = 1
        elif request == 'properties':
            retval = self.properties
        elif request == 'movements':
            retval = self.movements
        elif request == 'up':
            self.addToPath(self.location)
            self.moves += 1
            self.add( self.location, (0, -1) )
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'right':
            self.addToPath(self.location)
            self.moves += 1
            self.add( self.location, (1, 0) )
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'left':
            self.addToPath(self.location)
            self.moves += 1
            self.add( self.location, (-1, 0) )
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'down':
            self.addToPath(self.location)
            self.moves += 1
            self.add( self.location, (0, 1) )
            retval = self.checkMovement()
            self.redrawPath()
        elif request == 'supportedFeatures':
            retval = []
        elif request == 'builtinDevices':
            retval = []
        elif request == 'start':
            self.complete = 0
            self.initWorld()
            retval = self.location
            self.redrawPath()
        else:   # unknown command; returns "error"
            pass

        return pickle.dumps(retval)

    def redrawPath(self):
        for (x,y) in self.path:
           self.canvas.itemconfig( self.squares[x][y], fill=self.path_color )
        self.redrawLocation()

    def redrawVisited(self):
        for (x,y) in self.visited:
           self.canvas.itemconfig( self.squares[x][y], fill = self.visited_color )
        self.redrawLocation()

    def redrawLocation(self):
        self.canvas.itemconfig( self.squares[self.location], fill = self.current_pos_color )

    def erasePath(self, p):
        for (x,y) in p:
            strcolor = self.getUtilRGB( self.utility[x][y] )
            self.canvas.itemconfig( self.squares[x][y], fill = strcolor )
        self.redrawLocation()

    def drawGoal(self):
        (x,y) = self.goal
	if self.goal_id > -1:
          self.canvas.delete( self.goal_id )

        self.goal_id = self.canvas.create_image( x*self.square_width+1, y*self.square_height+1,
                                  image = self.goldImageTk, anchor=Tkinter.NW, tag="goal")

    def drawPits(self):
	while len( self.pit_ids ) > 0:
          self.canvas.delete( self.pit_ids.pop() );

        for (x,y) in self.pits:
          if not (x,y) in self.inaccessible:
            self.pit_ids.append( self.canvas.create_image( x*self.square_width+1, y*self.square_height+1,
                                 image = self.pitImageTk, anchor=Tkinter.NW, tag="pit") )

    def drawInaccessible(self):
        for (x,y) in self.inaccessible:
            self.canvas.itemconfig( self.squares[x][y], fill = self.inaccessible_color )

    # returns an RGB string for a given utility value
    def getUtilRGB(self, util):
        if util < 0:
            neg = 1
            util *= -1
        else:
            neg = 0

        # make values (v) range from 0-255
        v = int(util * 5.12)


        if v > 512:
            r = v - 512;
        else:
            r = 0;
        if v > 256:
            g = v - 256;
        else:
            g = 0
        b = v;
            
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255

        if r < 0:
            r = 0
        if g < 0:
            g = 0
        if b < 0:
            b = 0

        r = 255 - r
        g = 255 - g
        b = 255 - b

        if neg:
            tmp = b
            b = r
            r = tmp

        strr = hex(r)[2:]
        while len(strr) < 2:
            strr = "0" + strr;
        strg = hex(g)[2:]
        while len(strg) < 2:
            strg = "0" + strg;
        strb = hex(b)[2:]
        while len(strb) < 2:
            strb = "0" + strb;

        return( "#" + strr + strg + strb )

    def redrawUtilities(self):
        for x in range(self.num_squares_x):
            for y in range(self.num_squares_y ):
                if not (x, y) in self.inaccessible : 
                    strv = self.getUtilRGB(self.utility[x][y])
                    self.canvas.itemconfig( self.squares[x][y], fill = strv )

    def createGridlines(self):
        # grid-lines
        for x in range(self.num_squares_x):
            self.canvas.create_line(  0, x*self.square_height, self.width, x*self.square_height,
                                      width = 2, fill = gridline_color, tag = "gridline")
            self.canvas.create_line(  x*self.square_height, 0, x*self.square_height, self.height,
                                      width = 2, fill = gridline_color, tag = "gridline")
    

    def redraw(self):
	self.drawGoal()
	self.drawPits()

        self.redrawUtilities()
        self.redrawVisited()
        self.redrawPath()
        self.redrawLocation()

            
    # ------------------------------------------------------------------------        
        
    def destroy(self):
        self.done = 1 # stop processing requests, if handing
        self.quit = 1 # stop accept/bind toplevel
        self.root.quit() # kill the gui

def INIT():
    root = Tkinter.Tk()
    root.withdraw()
    return GUI(root, 240, 240) #375, 375)
