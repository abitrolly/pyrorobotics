import pyro.robot.armor as armor

class ArmorSimulated(armor.ArmorSimulated):
   def __init__(self):
      armor.ArmorSimulated.__init__(self, "ArmorSimulated", 1)

def INIT():
   return ArmorSimulated()
