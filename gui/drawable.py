# Drawable class; subclassed by anything that wants to be able to be
# drawn.

from UserList import UserList

class Drawable(UserList):
   """
   This class encapsulates things that can be rendered. Drawables are
   lists of drawables. 
   """
   def __init__(self,name='top level',options={}):
      """
      Name is a globaly unique name for this drawable
      """
      UserList.__init__(self)
      self.drawableName = name
      self.options = options
      self.needToRedraw = 0

   def getOptions(self):
      """
      Returns a dictionary (indexed by drawable name) of dictionaries
      (indexed by option name) of possible option values. 
      """
      opts = {}
      for d in self: 
         opts[d.getName()]
      opts[self] = self.options
      return opts

   def getName(self):
      """
      Return the name of this Drawable
      """
      return self.drawableName

   def getDrawables(self):
      """
      Returns a list of self plus all children's drawables
      """
      list = []
      for d in self:
         #print d, "is a drawable of", self
         for x in d.getDrawables():
            list.append(x)
      #list.append(self)
      return list


   def draw(self,options,renderer):
      """
      Draw all children and then draw self
      """
      for d in self:
         #print "Calling draw for", d.drawableName
         d.draw(options,renderer)# [d.getName()],renderer)
      #print "Calling draw for self:", self.drawableName
      self._draw(options,renderer);
      self.needToRedraw = 0


   def _draw(self,options,renderer):
      """
      This is the function that children should implement. It should
      draw itself.
      """
      raise "Drawable._draw: is an abstract funtion"

