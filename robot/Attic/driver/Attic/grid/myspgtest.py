import spg
import math

width  = 40
height = 40
g = spg.new_SpacePerceptionGrid(width, height)

def drawgrid():
   for y in range(0, height):
      for x in range(0, width):
         if spg.SpacePerceptionGrid_get(g, x, y) > 0:
            print '',int(spg.SpacePerceptionGrid_get(g, x, y)),
         elif spg.SpacePerceptionGrid_get(g,x,y) < 0:
            print int(spg.SpacePerceptionGrid_get(g,x,y)),
         else:
            print "  ",
      print ""

#spg.SpacePerceptionGrid_updateGridRow(g,10,3,10,5.0);
spg.SpacePerceptionGrid_update(g, 0, 0, 20, 23, 20 * 3.1415 / 180.0,1,1)
spg.SpacePerceptionGrid_update(g, 0, 20, 20, 0, 10 * 3.1415 / 180.0,1,1)
spg.SpacePerceptionGrid_update(g, 0, 10, 20, 10, 5 * 3.1415 / 180.0,1,1)

spg.SpacePerceptionGrid_update(g, 0, 0, 10, 30, math.pi / 18)
drawgrid()

print ""
	 
for i in range(0, height):
   for j in range(0, width):
      print spg.SpacePerceptionGrid_get(g, i, j),
   print ""



