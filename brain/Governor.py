import pyro.brain.ravq

class Governor:

    def initialize(self, ravqSettings, mask, bufferSize):
        # ravq
        self.ravq = pyro.brain.ravq.RAVQ(ravqSettings)
        self.ravq.setHistory(0)
        self.ravq.setAddModels(1)
        self.ravq.setMask(mask)

        # buffer 
        self.buffer = []
        self.bufferSize = bufferSize
        self.bufferIndex = 0

    def process(self, vector):
        self.ravq.input(vector)
        if self.ravq.getNewWinner(): 
            if len(self.buffer) >= self.bufferSize:
                self.buffer = self.buffer[1:] + [vector]
            else:
                self.buffer.append(vector)
        if len(self.buffer) > 0: 
            array = self.buffer[self.bufferIndex]
            self.bufferIndex = (self.bufferIndex + 1) % len(self.buffer)
            return array
        else:
            return vector

    def query(self):
        return str(self.ravq)
    
    def save(self, filename):
        self.ravq.saveRAVQToFile(filename)

    def load(self, filename):
        self.ravq.loadRAVQFromFile(filename)
        
