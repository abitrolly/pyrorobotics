from pyro.brain.psom import vis
import pyro.brain.psom as psom

inputfile = open("ffinputs.dat", "w")
targetfile = open("fftargets.dat", "w")

camera = open("camera.dat", "r")
sonar = open("sonar.dat", "r")
motors = open("motors.dat", "r")

# to get rid of vector length
sonar.readline()
camera.readline()

somSonar  = vis.VisPsom(file = "sonar-20passes-20x15.cod")
somCamera = vis.VisPsom(file = "camera-20passes-20x15.cod")

def saveListToFile(ls,file):
    for i in range(len(ls)):
        file.write("%.8f"%ls[i]+" ")
    file.write("\n")

def makeVector(pos, len):
   retval = [0.0] * len
   retval[pos] = 1.0
   return retval
   
sonarData  = map( float, sonar.readline().split() )
cameraData = map( float, camera.readline().split() )
modelSonar  = somSonar.map(psom.vector( sonarData ))
modelCamera = somCamera.map(psom.vector(cameraData ))

goalVector = makeVector(modelSonar.point.x, 20) + \
             makeVector(modelSonar.point.y, 15) + \
             makeVector(modelCamera.point.x, 20) + \
             makeVector(modelCamera.point.y, 15)

for i in xrange(4999):
   currVector = goalVector[:]
   currMotor  = map( float, motors.readline().split() )

   sonarData  = map( float, sonar.readline().split() )
   cameraData = map( float, camera.readline().split() )
   modelSonar  = somSonar.map(psom.vector( sonarData ))
   modelCamera = somCamera.map(psom.vector(cameraData ))
   
   goalVector = makeVector(modelSonar.point.x, 20) + \
                makeVector(modelSonar.point.y, 15) + \
                makeVector(modelCamera.point.x, 20) + \
                makeVector(modelCamera.point.y, 15)

   saveListToFile(currVector + goalVector, inputfile)
   exaggeratedTrans = (5 * (currMotor[0] - .5) + .5)
   saveListToFile([exaggeratedTrans, currMotor[1] ], targetfile)
   assert( 0.0 <= translate <= 1.0)

