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
      if filename == None:
         year,month,day,hour,minute,second,one,two,three=time.localtime()
         filename='log-'+str(month)+'-'+str(day)+'('+str(hour)+":"+str(minute)+':'+str(second)+')'
      self.file = open(filename,'w')
      self.writeln("Log opened: %s/%s/%s at %s:%s:%s" %
                   (str(month), str(day), str(year), str(hour),
                    str(minute), str(second)))
      if name:
         self.writeln('Experiment name:\n' + "   " + name)
      if robot:
         self.writeln('Robot:\n' + "   " + robot.get('robot','type'))
      if brain:
         self.writeln('Brain:\n' + "   " + brain.name)

   def write(self, msg):
      """ Write a string to the log """
      self.file.write(msg)

   def writeln(self, msg):
      """ Write a line (with newline) to the log """
      self.file.write(msg + "\n")

   def close(self):
      """ Close the log """
      year,month,day,hour,minute,second,one,two,three=time.localtime()
      self.writeln("Log closed: %s/%s/%s at %s:%s:%s" %
                   (str(month), str(day), str(year), str(hour),
                   str(minute), str(second)))
      self.file.close()
   
if __name__ == '__main__':
   log = Log()
   log.write("testing...")
   log.write("testing...")
   log.writeln("tested!")
   log.close()
