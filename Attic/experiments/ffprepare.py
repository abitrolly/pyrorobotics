import pyro.brain.psom as psom

dataPoints = 5000
measure = 10
inputfile = open("ffinputs.dat", "w")
targetfile = open("fftargets.dat", "w")

camera = open("camera.dat", "r")
sonar = open("sonar.dat", "r")
motors = open("motors.dat", "r")

# to get rid of vector length
sonar.readline()
camera.readline()

somSonar  = psom.psom(file = "sonar-200passes-20x15.cod")
somCamera = psom.psom(file = "camera-200passes-20x15.cod")

def saveListToFile(ls,file):
    for i in range(len(ls)):
        file.write("%.8f"%ls[i]+" ")
    file.write("\n")

def makeVector(pos, len):
   retval = [0.0] * len
   retval[pos] = 1.0
   return retval

motorVector = [0] * measure
sensoryVector = [0] * measure
for i in xrange(dataPoints / measure):
    for m in range(measure):
        sonarData  = map( float, sonar.readline().split() )
        cameraData = map( float, camera.readline().split() )
        modelSonar  = somSonar.map(psom.vector( sonarData ))
        modelCamera = somCamera.map(psom.vector(cameraData ))
        motorVector[m]  = map( float, motors.readline().split() )
        sensoryVector[m] = makeVector(modelSonar.point.x, 20) + \
                           makeVector(modelSonar.point.y, 15) + \
                           makeVector(modelCamera.point.x, 20) + \
                           makeVector(modelCamera.point.y, 15)
    goalVector = sensoryVector[measure - 1][35:]
    for m in range(measure - 1):
        saveListToFile(sensoryVector[m] + goalVector, inputfile)
        exaggeratedTrans = (5 * (motorVector[m][0] - .5) + .5)
        saveListToFile([exaggeratedTrans, motorVector[m][1] ], targetfile)
        assert( 0.0 <= exaggeratedTrans <= 1.0)
    saveListToFile(sensoryVector[measure - 1] + goalVector, inputfile)
    saveListToFile([0, 0], targetfile)
