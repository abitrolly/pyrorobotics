#Desc: device definition for Sparko ( a Pioneer robot with sonars,bumpers,gripper and camera)
#Author : Ioana Butoi
#Date: 28 May 2003

#define 16 sonars
define sparko_sonar sonar
(
  scount 16
  spose[0] [ 0.115 0.130 90]
  spose[1] [ 0.155 0.115 50 ]
  spose[2] [ 0.190 0.080 30 ]
  spose[3] [ 0.210 0.025 10 ]
  spose[4] [ 0.210 -0.025 -10 ]
  spose[5] [ 0.190 -0.080 -30 ]
  spose[6] [ 0.155 -0.115 -50 ]
  spose[7] [ 0.115 -0.130 -90 ]
  spose[8] [ -0.115 -0.130 -90 ]
  spose[9] [ -0.155 -0.115 -130 ]
  spose[10] [ -0.190 -0.080 -150 ]
  spose[11] [ -0.210 -0.025 -170 ]
  spose[12] [ -0.210 0.025 170 ]
  spose[13] [ -0.190 0.080 150 ]
  spose[14] [ -0.155 0.115 130 ]
  spose[15] [ -0.115 0.130 90 ]
)

#define 5 straight bumpers on the rear edge of the robot
define sparko_bumpers bumper
(
  bcount 5
  bpose[0] [ -0.25  0.22  128  0.105 0.0 ]
  bpose[1] [ -0.32  0.12  161  0.105 0.0 ]
  bpose[2] [ -0.34  0.00  180  0.105 0.0 ]
  bpose[3] [ -0.32 -0.12  199  0.105 0.0 ]
  bpose[4] [ -0.25 -0.22  232  0.105 0.0 ]
)

# the pioneer's center of rotation is offset from its
# center of area
define sparko position
(  	
  size [.440 .330]
  offset [-0.04 0.0]
  sparko_sonar()
  sparko_bumpers()
  gripper( pose [0.2 0 0] consume "false")
  ptz( pose [0.1 0 0 ] blobfinder() )
  power()
)
