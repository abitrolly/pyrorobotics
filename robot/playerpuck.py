from pyro.robot.playerbase import PlayerBase
from pyro.robot.driver.player import player

# Extension of PlayerBase for a full robot

class PlayerPuck(PlayerBase):
    # constructor takes name, port
    
    def _draw(self, options, renderer): # overloaded from robot
        pass

    def connect(self):
        self.dev = player('localhost', port=self.port)
        print "Device: ", self.dev
