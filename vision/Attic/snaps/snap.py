
import os, time

x = 0
while (x < 100):
	os.system("./snapshot %d" % x)
	x = x + 1
	#time.sleep(1)
	print "\a"