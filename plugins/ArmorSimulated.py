import pyro.robot.armor as armor

class ArmorSimulated(armor.ArmorRobot):
   def __init__(self):
      armor.ArmorRobot.__init__(self, "ArmorSimulated", 1)

def INIT():
   return ArmorSimulated()
