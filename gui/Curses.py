from pyro.gui import *
import curses
#import curses.wrapper

class Curses(gui):
    
    def init(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(1)
        begin_x = 20 ; begin_y = 7
        height = 5 ; width = 40
        self.win = curses.newwin(height, width, begin_y, begin_x)
          
    def run(self):
      done = 0
      while done is not 1:
         self.stdscr.addstr( "Pyro > ")
         self.stdscr.refresh()
         curses.echo()            # Enable echoing of characters
         retval = self.stdscr.getstr()
         curses.noecho()
         done = self.processCommand(retval)

    def cleanup(self):
        #curses.nobreak(); curses.keypad(0);
        curses.echo()
        curses.endwin()
