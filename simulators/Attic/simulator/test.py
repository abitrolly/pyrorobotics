

from __init__ import *

def test_():

	for x in range(1,4):
		print "x=", x
	
	sw = SimWorld()
	
	sw.addArt(SimArtBasic([0,0,0],[1,0,0]))	#at 0,0,0, looking forward
	
	for x in range(1,4):
		print "x=", x
		sw.listArts()
		sw.takeTimeStep()
		
		
	sw.listArts()
	
	print '\nDone\n'
	
test_()
