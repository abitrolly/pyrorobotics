#
# SimWindow: a class to visualize SimWorld
#
#
#

from SimWorldFile import *
from pyro.gui import console
from threading import *
import Tkinter

class SimWindow(Thread):
	"""
	a class to visualize SinWorld
	"""
	def __init__(self, sw, server = None): #sw is SimWorld
		console.log(console.INFO,'Creating SimWindow')
		Thread.__init__(self,name='SimWindow')
		self.server = server
		self.world = sw
		self.root = None
		self.cwidth = 500
		self.cheight = 500
		self.centerx = self.cwidth/2
		self.centery = self.cheight/2
		self.canvas = None
		self.xscale = 10	#each meter equals 10 pixels - in x axis
		self.yscale = 10	#each meter equals 10 pixels - in y axis
		self.meter_space = 5	#for grid - every 5 meters
		
		self.alive = 1	#yes, alive
		self.art_ids = {}
		self.show()
		self.grid(1)
		self.axis(1)
		self.update()
		#self.start()#caling original Thread.staret() here
		#self.run()
	
	def axis(self, onoff = 1):	#yes for grids
		"""this function will add axis to the window
		pass 1 for on, 0 for off"""
		if (onoff==1):
			self.art_ids['x_axis'] = self.canvas.create_line\
				(0,self.centery,self.cwidth,self.centery,fill='red', width=2)
			self.art_ids['y_axis'] = self.canvas.create_line\
				(self.centerx,0,self.centerx,self.cheight,fill='red',width=2)
			self.canvas.pack()
		if (onoff==0):
			if self.art_ids.has_key('x_axis'):
				self.canvas.delete(self.art_ids['x_axis'])
			if self.art_ids.has_key('y_axis'):
				self.canvas.delete(self.art_ids['y_axis'])
	
	
	def grid(self, onoff = 1, meter_space = 5):	#yes for grids
		"""this function will add grids to the window
		pass 1 for on, 0 for off
		space = 5 meters per line
		"""
		
		if (self.meter_space != meter_space):
			self.grid(0, self.meter_space)   #take old lines off first
			self.meter_space = meter_space
			
		if (onoff == 1):
			#vertical lines
			space = meter_space * self.xscale
			lines = int((self.cwidth/2)/space)
			offset = ((self.cwidth/2)/space - lines) * space
			for x in range(0,lines*2):
				nm = "ver_line_" + str(x)
				pos = offset + x * space
				self.art_ids[nm] = self.canvas.create_line\
					(pos,0,pos,self.cheight,fill='red', width=1)
						
			#Horizontal lines
			space = meter_space * self.yscale
			lines = int((self.cheight/2)/space)
			offset = ((self.cheight/2)/space - lines) * space
			for x in range(0,lines*2):
				nm = "hor_line_" + str(x)
				pos = offset + x * space
				self.art_ids[nm] = self.canvas.create_line\
					(0,pos,self.cwidth,pos,fill='red', width=1)
		else:
			#vertical lines
			space = meter_space * self.xscale
			lines = int((self.cwidth/2)/space)
			for x in range(0,lines*2):
				nm = "ver_line_" + str(x)
				if self.art_ids.has_key(nm):
					self.canvas.delete(self.art_ids[nm])
						
			#Horizontal lines
			space = meter_space * self.yscale
			lines = int((self.cheight/2)/space)
			for x in range(0,lines*2):
				nm = "hor_line_" + str(x)
				if self.art_ids.has_key(nm):
					self.canvas.delete(self.art_ids[nm])		
	
	def scale(self,value):
		"""change both xscale and yscale"""
		self.xscale = value
		self.yscale = value
		self.update()
	
	def kill(self):
		self.alive = 0
		self.root.destroy()
		console.log(console.INFO,'Window killed')
	
	def show(self):
		"""will show the window for the first time"""
		self.root = Tkinter.Tk()
		self.canvas = Tkinter.Canvas(self.root,\
									width=self.cwidth,\
									height=self.cheight)
		
		# create a menu
		self.menu = Tkinter.Menu(self.root)
		self.root.config(menu=self.menu)
		self.menu_file = Tkinter.Menu(self.menu)
		self.menu.add_cascade(label="File", menu=self.menu_file)
		self.menu_file.add_command(label="Open...", command=self.menu_file_open)
		self.menu_file.add_separator()		
		self.menu_file.add_command(label="Quit", command=self.menu_file_quit)
		
		console.log(console.INFO,'SimWindow brought up')
	
	def run(self):
		"""show the window & update if world changes time"""
		console.log(console.INFO,'Running Window')
		while self.alive==1:
		    self.update()
		    self.canvas.after(10)	#sleep
	
		
	def add_art(self, x): #x is SimArtBasic
		"""add an artifact to the window and assign it an id"""
		xy2 = []
		for line in x.shape.shape.vecs:
			#xy2 += [self.centerx+line[0], self.centery-line[1]]
			tline = x.translate(line)
			xy2.append(self.centerx + tline[0]*self.xscale) 			
			xy2.append(self.centery - tline[1]*self.yscale)
		self.art_ids[x.id] = self.canvas.create_polygon\
		(xy2,outline=x.color,fill=x.color)
		self.canvas.pack()
		if (x.type == SimArtType['Robot']):
			self.add_sonars(x)
	
	def add_sonars(self, rb):
		for i in range(0,len(rb.sonars)):
			x = rb.sonars[i]
			nm = str(rb.id) + "_" + str(i)
			tfrom = rb.translate(x.location, 1)#1 for noshape translation			
			tto = rb.translate(x.reading_point(), 1)
			xy = tfrom[0], tfrom[1], tto[0], tto[1]
			self.art_ids[nm + "a"] = \
				self.canvas.create_arc(xy, start=0,\
				 extent=180*x.arc/(2*math.pi), fill=x.color)
			self.art_ids[nm + "b"] = \
				self.canvas.create_arc(xy, start=0,\
				 extent=-180*x.arc/(2*math.pi), fill=x.color)
		self.canvas.pack()
				
	def update_sonars(self, rb):
		#console.log(console.INFO,"drawing sonars")
		for i in range(0,len(rb.sonars)):
			x = rb.sonars[i]
			nm = str(rb.id) + "_" + str(i)
			tfrom = rb.translate(x.location, 1)#1 for noshape translation			
			tto = rb.translate(x.reading_point(), 1)
			xy = tfrom[0], tfrom[1], tto[0], tto[1]
			self.canvas.itemconfigure(self.art_ids[nm + "a"], start=0,\
				 extent=180*x.arc/(2*math.pi), fill=x.color)
			self.canvas.itemconfigure(self.art_ids[nm + "b"], start=0,\
				 extent=-180*x.arc/(2*math.pi), fill=x.color)
				
		
	def update_art(self, x): #x isSimArtBasic
		"""Update an artifact in the window""" 		
		xy2 = []
		index = 0
		xystring = ""
		for line in x.shape.shape.vecs:
			tr_line = x.translate(line)
			xy2.append(self.centerx+\
				tr_line[0]*self.xscale)
			xy2.append(self.centery-\
				tr_line[1]*self.yscale)
			#if (index != 0): xystring += ","
			#xystring += str(self.centerx+line[0]) + "," + self.centery-line[1]
			index += 1
		
		#self.canvas.coords(self.art_ids[x.id], xy2)
		#self.canvas.coords(self.art_ids[x.id], eval(xystring))
		#eval("self.canvas.coords(self.art_ids[x.id]," + xystring + ")")
		#update coordinates of points of object x in window
		apply(self.canvas.coords, [self.art_ids[x.id]]+xy2)
		if (x.type == SimArtType['Robot']):
			self.update_sonars(x)
				
	def update(self):
		"""Update window"""
		for x in self.world.arts:
			if (self.art_ids.has_key(x.id)):	#Object not in window
				self.update_art(x)
			else:
				self.add_art(x)
		self.canvas.update()
	

	#menus
	def menu_file_quit(self):
		" will call quit from server "
		if (self.server != None):
			self.server.quit()
		
	
	def menu_file_open(self):
		pass
		
if (__name__ == '__main__'):
	import sys
	
	def test_():
	
		sw = SimWorld()
		
		sw.addArt(SimArtSquare(1,[10,10,0],0))	#at 0,0,0, looking forward
		sw.arts[0].color = "red"
		sw.addArt(SimArtBox([1,1,1],[10,10,0],0))	#at 0,0,0, looking forward
		sw.arts[1].color = "green"
		sw.addArt(SimArtCircle(1,8,[-10,-10,0],0))	#at 0,0,0, looking forward
		sw.arts[2].color = "pink"
		sw.addArt(SimRobot())	#at 0,0,0, looking forward
		sw.arts[3].color = "orange"
		
		for x in range(1,4):
			sw.listArts()
			sw.takeTimeStep()
					
		sw.listArts()
		
		wind = SimWindow(sw)
		wind.update()
		
		sw.arts[3].setDesired(1,0)
		
		for x in range(1, 10):
			print 'timestep:', x
			print sw.arts[3].toString()
			sw.takeTimeStep()
			wind.update()
		
		print '**********\n** Done **\n**********'
		print 'press enter to finish'
		sys.stdin.readline()
		
		
	test_()
