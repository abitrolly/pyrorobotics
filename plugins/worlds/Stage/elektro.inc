#Desc: device definition for Elektro( B21R)
#Author : Ioana Butoi
#Date: 28 May 2003

# the pioneer's center of rotation is offset from its
# center of area
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


define pioneer position
(  	
  size [.550 .550]
  offset [-0.04 0.0]
  sparko_sonar()
  ptz( pose [0.1 0 0 ] blobfinder()  )
  laser( pose [0 0 0])
  power()
)
