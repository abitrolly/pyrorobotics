from pyro.brain.psom import vis
import pyro.brain.psom as psom
from pyro.brain import Brain
#from pyro.brain.VisConx.VisRobotConx import *
from pyro.brain.conx import Network
from time import sleep

def makeVector(pos, len):
   retval = [0.0] * len
   retval[pos] = 1.0
   return retval

class ffBrain(Brain):

   def setup(self):
      #self.mode = "viewState"
      self.mode = "run"
      self.getRobot().noise = 0

      # start and goal poses
      self.startPose = [4.44, 2.24, 87]
      self.goalPose = [1.018, 3.75, -117] #1.018, 3.75, -118

      # Setup the robot/start services:
      self.getRobot().startService(["BlobCamera", "truth"])
      self.truth = self.getRobot().getService("truth")
      self.camera = self.getRobot().getService("BlobCamera")
      # The FF Network:
      #self.n = VisRobotNetwork()
      self.n = Network()
      self.n.addThreeLayers(105,15,2)
      self.n.initialize()
      self.n.loadWeightsFromFile("ff.wts")
      # The SOMs:
      self.somSonar  = vis.VisPsom(file = "sonar-200passes-20x15.cod")
      self.somCamera = vis.VisPsom(file = "camera-200passes-20x15.cod")
      # Set goal
      self.truth.setPose(self.goalPose[0], self.goalPose[1], self.goalPose[2])
      sleep(1)
      # next save SOM state of goal pose (camera and sonar):
      # force a robot/camera update for data:
      self.getRobot().update()
      self.camera.update()
      # get data:
      sonarData = self.scaleSonar(self.getRobot().get("range", "value", "all"))
      image = self.camera.getShrunkenImage(xscale = 0.125, mode="sample")
      cameraData = self.scaleList(image.data, 255.0)
      modelSonar  = self.somSonar.map(psom.vector( sonarData ))
      modelCamera = self.somCamera.map(psom.vector(cameraData ))
      self.goalVector = makeVector(modelCamera.point.x, 20) + \
                        makeVector(modelCamera.point.y, 15)
      self.goalList = [modelSonar.point.x, modelSonar.point.y, modelCamera.point.x, modelCamera.point.y]
      print "Goal:", self.goalList
      # Put robot in place to start:
      #self.truth.setPose(2.0, 1.25, 270)
      self.truth.setPose(self.startPose[0], self.startPose[1], self.startPose[2])
      sleep(1)
      self.getRobot().update()
      self.camera.update()
      self.out = open("path.dat", "w")
      print "Initialized"

   def destroy(self):
      self.somCamera.destroy()
      self.somSonar.destroy()
      self.n.destroy()
      self.out.close()

   def scaleSonar(self,ls):
      myl = []
      for val in ls:
         myl += [val/3.99]
      return myl

   def scaleList(self, ls, maxval): 
      for i in range(len(ls)): 
         ls[i] = ls[i] / float(maxval) 
      return ls

   def step(self):
      # 1. set current from camera, sonar data
      sonarData = self.scaleSonar(self.getRobot().get("range", "value", "all"))
      image = self.camera.getShrunkenImage(xscale = 0.125, mode="sample")
      cameraData = self.scaleList(image.data, 255.0)
      modelSonar  = self.somSonar.map(psom.vector( sonarData ))
      modelCamera = self.somCamera.map(psom.vector(cameraData ))
      currVector = makeVector(modelSonar.point.x, 20) + \
                   makeVector(modelSonar.point.y, 15) + \
                   makeVector(modelCamera.point.x, 20) + \
                   makeVector(modelCamera.point.y, 15)

      # 2. load inputs into network
      self.n["input"].copyActivations( currVector + self.goalVector )
      # 3. propagate
      self.n.propagate()
      # 4. move the robot based on output (unscale the ouputs first!)
      exaggeratedTrans, scaledRotate = self.n["output"].getActivations()
      scaledTrans = (((exaggeratedTrans - .5) / .5) * .1) + .5
      unscaledTrans = (scaledTrans * 2) - 1
      unscaledRotate = (scaledRotate * 2) - 1

      #sonarState = modelSonar.point.y * 20 + modelSonar.point.x
      #cameraState = modelCamera.point.y * 20 + modelCamera.point.x
      print "Current state = ", [modelSonar.point.x, modelSonar.point.y, modelCamera.point.x, modelCamera.point.y]
      print "Goal state = ", self.goalList

      if self.mode == "run":
         self.getRobot().move(unscaledTrans, unscaledRotate)
         self.out.write("%f %f %f\n" %  self.truth.getPose())


def INIT(engine):
   return ffBrain("FFBrain", engine)
