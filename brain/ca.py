# Cellular Automata Class
# D.S. Blank

from random import random

class Matrix:

    def randomize(self, bias = .5):
        for i in range(self.size):
            self.data[0][i] = random() < bias
            
    def randomize(self, bias = .5):
        for i in range(self.size):
            self.data[0][i] = random() < bias

    def display(self, rows = -1):
        if rows == -1:
            for i in range(self.height):
                self.displayRow(i)
                if i + 1 < self.height and self.data[i] == self.data[i + 1]:
                    return
        else:
            self.displayRow(rows)
            

    def displayRow(self, row = 0):
        s = ''
        cnt = 0.0
        print "%3d" % row,
        for i in range(self.size):
            if self.data[row][i]:
                s += 'X'
            else:
                s += '.'
            if self.data[row][i]:
                cnt += 1
        print s, "%.2f" % (cnt / self.size)



class Rules(Matrix):
    
    def __init__(self, window = 3, values = 2):
        self.window = window
        self.values = values
        self.size = (self.values ** (self.window * 2 + 1))
        self.height = 1
        self.data = [0]
        self.data[0] = [0] * self.size

    def apply(self, lat, c):
        for i in range(lat.size):
            lat.data[c+1][i] = self.data[0][lat.bits2rule(c, i - self.window, i + self.window)]
            if c + 1 < self.height and self.data[c] == self.data[c + 1]:
                return


    def init(self, str):
        if (len(str) != self.size):
            raise "ImproperLength", str
        if str[0] == '0' or str[0] == '1': # repr of 0 and 1
            for i in range(len(str)):
                self.data[0][i] = (str[i] == '1')
        elif str[0] == '.' or str[0] == 'X': # repr of . and X
            for i in range(len(str)):
                self.data[0][i] = (str[i] == 'X')
        else:
            raise "UnknownRepresentation", str

class Lattice(Matrix):

    def __init__(self, size = 149, height = 150):
        self.size = size
        self.height = height
        self.data = [0] * self.height
        for h in range(self.height):
            self.data[h] = [0] * self.size

    def bit(self, row, pos):
        if pos < 0:
            return self.data[row][self.size + pos]
        if pos >= self.size:
            return self.data[row][pos % self.size]
        else:
            return self.data[row][pos]

    def bits2rule(self, row, start, stop):
        sum = 0
        cnt = 0
        for i in range(stop, start - 1, -1):
            sum += self.bit(row, i) * 2 ** cnt
            cnt += 1
        return sum

if __name__ == '__main__':

    data = Lattice()
    data.randomize(.1)
    print "A 10% Lattice:"
    data.display()
    data.randomize(.5)
    print "A 50% Lattice:"
    data.display()
    data.randomize(.9)
    print "A 90% Lattice:"
    data.display()
    
    rules = Rules()
    rules.randomize()
    print "A 50% Random Rule set:"
    rules.display()
    
    data.randomize(.05)
    for c in range( data.height - 1):
        rules.apply(data, c)
    print "A 50% Rule applied to a 10% Lattice:"
    data.display()
        
    rules.init("00000000010111110000000001011111000000000101111100000000010111110000000001011111111111110101111100000000010111111111111101011111")
    print "GKL Rule set:"
    rules.display()
    
    data.randomize(.3)
    for c in range( data.height - 1):
        rules.apply(data, c)
    print "GKL Rule applied to a 30% Lattice:"
    data.display()
    
    data.randomize(.7)
    for c in range( data.height - 1):
        rules.apply(data, c)
    print "GKL Rule applied to a 70% Lattice:"
    data.display()
    
