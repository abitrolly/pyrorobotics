from pyro.system import share
import grabImage
share.grabImage = grabImage
from pyro.camera import Camera, CBuffer
import re, time
import PIL

class FakeCamera(Camera):
   """
   A fake camera.  This will emulate a camera, but instead of
   accessing the hardware, it will load a series of images from file.
   ONLY ONE OF THESE CAN EXIST AT A TIME!
   """
   def __init__(self, pattern = "vision/snaps/som-?.ppm",
                start = 0, limit = 19, char = "?",
                interval = 1.0):
      """
      pattern is a filename with indicators on where to put digits for the
      sequence.  Absolute or relative filenames can be used.

      For example, 'image???-.ppm' would start at 'image000.ppm'
      and continue up to limit.
      
      char is the character that should be replaced in the pattern.

      interval = how often do I get new image

      As an example, to load som-0.ppm through som-19.ppm, we could call
      FakeCamera('vision/snaps/som-?.ppm', 0, 19)
      """
      self.pattern = pattern
      self.limit = limit
      self.interval = interval
      self.lastUpdate = 0
      #create a matchdata object that we will store
      self.match = re.search(re.escape(char) + "+", pattern)
      #create a format string that we can use to replace the
      #replace characters
      self.fstring = "%%0%dd" % len(self.match.group())
      self.start = start
      self.current = start
      currname = self.pattern[:self.match.start()] + \
                 self.fstring % self.current + \
                 self.pattern[self.match.end():]
      self.width, self.height, self.depth, self.cbuf = share.grabImage.grab_image(currname)
      if self.depth == 8:
         self.color = 0
      else:
         self.color = 1
         
      Camera.__init__(self, self.width, self.height, self.depth,
                      "Fake Camera View")
      self.data = CBuffer(self.cbuf)
      self.rgb = (0, 1, 2) # offsets to RGB
      self.format = "RGB"
      
   def _update(self):
      if self.lockCamera == 0 and self.limit > 0:
         if (self.current < self.limit):
            currentTime = time.time()
            if currentTime - self.lastUpdate > self.interval:
               currname = self.pattern[:self.match.start()] + \
                          self.fstring % self.current + \
                          self.pattern[self.match.end():]
               share.grabImage.refresh_image(currname)
               self.current += 1
               self.lastUpdate = currentTime
         else:
            self.current = self.start 

   def __del__(self):
      share.grabImage.free_image()



