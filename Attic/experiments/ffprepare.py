import pyro.brain.psom as psom

dataPoints = 5000
measureSize = 10  # must be even
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
   #for i in range(len):
   #    retval[i] = min(max(1 - abs(i - pos)/float(len/2 - 1), 0.0), 1.0)
   retval[pos] = 1.0
   return retval

def fillSecondHalf(sensoryVectors, motorVectors):
    mid = len(sensoryVectors) / 2
    for i in range(mid, len(sensoryVectors)):
        sonarData  = map(float, sonar.readline().split())
        cameraData = map(float, camera.readline().split())
        modelSonar  = somSonar.map(psom.vector(sonarData))
        modelCamera = somCamera.map(psom.vector(cameraData))
        sensoryVectors[i] = makeVector(modelSonar.point.x, 20) + \
                            makeVector(modelSonar.point.y, 15) + \
                            makeVector(modelCamera.point.x, 20) + \
                            makeVector(modelCamera.point.y, 15)

        motorData = map(float, motors.readline().split())
        motorVectors[i] = motorData

def shiftToFirstHalf(sensoryVectors, motorVectors):
    mid = len(sensoryVectors) / 2
    for i in range(mid):
        sensoryVectors[i] = sensoryVectors[i + mid]
        motorVectors[i] = motorVectors[i + mid]

def generateTrainingData(sensoryVectors, motorVectors):
    size = len(sensoryVectors)
    goalVector = sensoryVectors[size - 1][:] # change to [35:] to be just camera
    for i in range(size - 1):
        sensoryVector = sensoryVectors[i]
        saveListToFile(sensoryVector + goalVector, inputfile)
        translate = motorVectors[i][0]
        rotate = motorVectors[i][1]
        exaggeratedTrans = (5 * (translate - .5) + .5)
        motorVector = [exaggeratedTrans, rotate]
        saveListToFile(motorVector, targetfile)
        assert(0.0 <= exaggeratedTrans <= 1.0)
    saveListToFile(sensoryVectors[size - 1] + goalVector, inputfile)
    saveListToFile([0, 0], targetfile)

sensoryVectors = [0] * measureSize
motorVectors = [0] * measureSize
numMeasures = dataPoints / measureSize

fillSecondHalf(sensoryVectors, motorVectors)
for i in range(2 * numMeasures - 1):
    shiftToFirstHalf(sensoryVectors, motorVectors)
    fillSecondHalf(sensoryVectors, motorVectors)
    generateTrainingData(sensoryVectors, motorVectors)
