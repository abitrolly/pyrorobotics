
# Desc: Device definitions for handy beacons
# Author: Richard Vaughan
# Date: 29 October 2002
# CVS: $Id$

# vision beacons - bright round circles
# that show up nicely in the blobfinder

define visionbeacon box
(
  shape "circle"
  color "orange" 
  size [0.2 0.2]
)


# laser beacons - laser-bright flat targets. any non-zero ID will cause
# this these objects to show up in the laserbeacondevice

define laserbeacon box
(
  fiducial_id 1
  size [ 0.05 0.3 ]
  laser_return "bright"
  color "LightBlue"
)

