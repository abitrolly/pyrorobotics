from pyro.brain import Brain 
import random
import time

def saveListToFile(ls, file): 
    for i in range(len(ls)): 
        file.write(str(ls[i]) + " ") 
    file.write("\n")
    file.flush()

class Sample(Brain):
    """
    This class collects sample data.

    """
    def setup(self, **args):
        self.modality=args.get('modality')
        self.file = {}
        for name in self.modality:
            self.file[name] = open(name + ".dat", "w")
            if name == 'bumper':
                self.getRobot().startService('bumper')
            current = self.getValue(name, 0)
            self.file[name].write(str(len(current)) + '\n')
        self.count = 0
        
    def step(self):
        if self.count < 500:
            for name in self.modality:
                current = self.getValue(name)
                saveListToFile(current, self.file[name])
            self.count += 1
        else:
            self.getRobot().stop()
            self.pleaseStop()
            print "done collecting samples"

    def getValue(self, name, moveit = 1):
        if name == 'wheel':
            translate, rotate = random.random()*2-1, random.random()*2-1
            if moveit:
                self.getRobot().move(translate, rotate)
            time.sleep(0.25)
            return (translate+1)/2.0, (rotate+1)/2.0
        elif name == 'bumper':
            return self.getRobot().getService('bumper').getServiceData()
        else:
            values = self.getRobot().get(name,'value', 'all')
            maxValue = self.getRobot().get(name, 'maxvalue')
            return map(lambda v: v/maxValue, values)

def INIT(engine):
    return Sample('Sample', engine, modality = ('sonar','wheel','bumper'))

