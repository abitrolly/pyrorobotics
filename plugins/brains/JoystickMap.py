from pyro.brain import *
from pyro.tools.joystick import Joystick
import pyro.system.share as share
from pyro.map.lps import LPS
from pyro.map.gps import GPS

class Map(Brain):
   def setup(self):
       # We want our map to measure in MM, so we first store our current unit of measure
       units = self.get('/robot/range/units')
       # We then reset our measurements to MMs
       self.robot.set('/robot/range/units', 'MM')
       # Calculate the maximum range of our sensors
       rangeMaxMM = self.get('/robot/range/maxvalue')
       sizeMM = rangeMaxMM * 3 + self.robot.get('/robot/radius')
       # Reset our unit of measure
       self.robot.set('robot/range/units', units)
       # Now, we create our Local Perceptiual Space window - this will hold our local map
       #   Our map will be 20px by 20px and will represent an height and width of sizeMM (total sensor range)
       self.lps = LPS( 20, 20, widthMM = sizeMM, heightMM = sizeMM)
       # Then create our Global Perceptual Space window - this will hold our global map
       #    This map will be 500px by 500px and will represent an area ten times the size of our maximum range
       self.gps = GPS(cols=500, rows=500, heightMM = sizeMM * 10, widthMM = sizeMM * 10)
       self.joystick = Joystick()
       
   def step(self):
       robot = self.robot
       # First we clear out all our old LPS data
       self.lps.reset()
       # Next we update our LPS with current 'range' sensor readings
       self.lps.sensorHits(robot, 'range')
       # Now redraw our LPS window - the LPS redraw can be improve performance
       self.lps.redraw()
       # Then update our GPS with the new information in the LPS
       self.gps.updateFromLPS(self.lps, robot)
       # Finally, we redraw the GPS window
       self.gps.redraw()
       self.robot.move(self.joystick.translate, self.joystick.rotate)
       
   def destroy(self):
       # Make sure we close down cleanly
       self.lps.destroy()
       self.gps.destroy()
       self.joystick.destroy()
       
def INIT(engine):
    return Map("Mapping Brain", engine)


