#
# simsim.py
# the simple simulator. One simple robot. No noise. No nonsence.
#
#
#

import thread

from pyro.robot.driver import *

class SimSim(driver.Driver):
   """
   Simple Simulator
   Provides two senses, a range sense and a bump sence.
   """
   def __init__(self):
      """
      constructor. duh.
      """
      driver.Driver(self)
      
      self.stop = 0
      self.location = [0.0,0.0]  
      self.direction = [0.0,1.0] #normalized

      #build our storage for readings
      radius = .002
      sonarGeometry,sonarReadings = [],[]
      bumpGeometry,bumpReadings = [],
      for x in xrange(0,24):
         t = 2*3.14*float(x)/24
         x,y,z,i,j,k = radius*sin(t),radius*cos(t),0,sin(t),cos(t),0
         sonarGeometry.append(([x,y,z],normalize([i,j,k])))
         sonarReadings.append(0)
         bumpGeometry.append(([x,y,z],normalize([i,j,k])))
         bumpReadings.append(0)
      
      self.senses['sonar'] = RangeSensor(sonarGeometry,sonarReading)
      self.senses['bump']  = RangeSensor(bumpGeometry,bumpReading)

      self.controls['rotation velocity'] = Control(0)
      self.controls['forward velocity']  = Control(0)

      #build our virtual world
      self.objects = []
      self.objects.append(Plane(( 1.0, 0.0),(-1.0, 0.0),2.0))
      self.objects.append(Plane(( 0.0, 1.0),( 0.0,-1.0),2.0))
      self.objects.append(Plane((-1.0, 0.0),( 1.0, 0.0),2.0))
      self.objects.append(Plane(( 0.0,-1.0),( 0.0, 1.0),2.0))

      self.objects.append(Cube((.5,.5),.1))
      self.objects.append(Cube((-.5,-.9),.06))

      #start the world
      thread.start_new_thread(self.simulator,())

   def simulator(self):
      """
      this is a thread that actually performs the simulation.
      """
      while 1:
         if self.stop == 1:
            break
         dt = t - currentTime
         t = currentTime
         self.updateRobot(dt)
         self.senses['sonar'].update()
         self.senses['bump'].update()
   
   def shutdown(self):
      """
      do cleanup. stop thread. stuff.
      """
      self.stop = 1

   def updateRobot(self,dt):
      """
      this updates the position of the robot.
      """
      rotdist = dt*self.controls['rotational velocity'].getValue()
      fordist = dt*self.controls['forward velocity'].getValue()

      self.direction[0] = #rotate shit here 
      self.direction[1] = #rotate shit here
      
      for x in range(0,2):
         self.location[x] += fordist*self.direction[x]
         


