from Tkinter import *

class Joystick:

   def __init__(self, robot):
      self.app = Tk()
      self.app.wm_state('withdrawn')
      self.win = Toplevel()
      self.win.wm_title('Joystick')

      self.robot = robot
      self.canvas = Canvas(self.win,
                           width = 360,
                           height = 220,
                           bg = 'white')

      self.canvas.bind("<ButtonRelease-1>", self.canvas_clicked_up)
      self.canvas.bind("<Button-1>", self.canvas_clicked_down)
      self.canvas.bind("<B1-Motion>", self.canvas_moved)
      self.canvas.pack(side=TOP)

      self.circle_dim = (150, 10, 350, 210)
      self.circle = self.canvas.create_oval(self.circle_dim, fill = 'white')
      self.canvas.create_oval(245, 105, 255, 115, fill='black')

      self.panicButton = Button(self.win, text="STOP!!", command=self.stop)
      self.win.pack(side = LEFT)
      self.app.mainloop()

   def canvas_clicked_up(self, event):
      self.robot.move(0, 0)

   def canvas_clicked_down(self, event):
      if self.in_circle(event.x, event.y):
         trans, rotate = self.calc_tr(event.x, event.y)
         self.robot.move(trans, rotate)

   def canvas_moved(self, event):
      if self.in_circle(event.x, event.y):
         trans, rotate = self.calc_tr(event.x, event.y)
         self.robot.move(trans, rotate)

   def stop(self, event):
      self.robot.move(0, 0)

   def in_circle(self, x, y):
      r2 = ((self.circle_dim[2] - self.circle_dim[0])/2)**2
           
      center = ((self.circle_dim[2] + self.circle_dim[0])/2,
                (self.circle_dim[3] + self.circle_dim[1])/2)
      #x in?
      dist2 = (center[0] - x)**2 + (center[1] - y)**2
      if (dist2 < r2):
         return True
      else:
         return False

   def calc_tr(self, x, y):
      #right is negative
      center = ((self.circle_dim[2] + self.circle_dim[0])/2,
                (self.circle_dim[3] + self.circle_dim[1])/2)
      rot = float(center[0] - x) / float(center[0] - self.circle_dim[0])
      trans = float(center[1] - y) / float(center[1] - self.circle_dim[1])
      return (trans, rot)
