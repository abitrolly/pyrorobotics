# A log class

import time

class Log:
   """
   A log class to do automatically what needs to be done for each
   experiment.
   """
   def __init__(self,filename = None, name = None, robot = None, brain = None):
      """
      Pass in robot and brain so that we can query them (and maybe make
      copies and query them on occation).
      """
      timestamp = self.timestamp()
      if filename == None:
         filename= timestamp + '.log'
      self.filename = filename
      self.file = open(filename,'w')
      self.writeln("Log opened: " + timestamp)
      if name:
         self.writeln('Experiment name: ' + name)
      if robot:
         self.writeln('Robot: ' + robot.get('robot','type'))
      if brain:
         self.writeln('Brain: ' + brain.name)

   def timestamp(self):
      year,month,day,hour,minute,second,one,two,three=time.localtime()
      return '%4d-%02d-%02d:%02d:%02d:%02d' % (year, month, day, hour, minute, second)

   def write(self, msg):
      """ Write a string to the log """
      self.file.write(msg)

   def writeln(self, msg):
      """ Write a line (with newline) to the log """
      self.file.write(msg + "\n")

   def close(self):
      """ Close the log """
      year,month,day,hour,minute,second,one,two,three=time.localtime()
      self.writeln("Log closed: " + self.timestamp())
      self.file.close()
   
if __name__ == '__main__':
   log = Log()
   log.write("testing...")
   log.write("testing...")
   log.writeln("tested!")
   log.close()
