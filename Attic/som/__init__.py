
import RandomArray, random, math, sys

class som:

    def __init__(self, rows, cols, size):
        self.rows = rows
        self.cols = cols
        self.vectorLen = size
        self.weight = RandomArray.random((rows, cols, size))
        self.input = []
        self.loadOrder = []
        self.step = 0
        self.maxStep = 1000.0

    def setInputs(self, inputs):
        self.input = inputs
        self.loadOrder = range(len(self.input)) # not random
        # will randomize later, if need be

    def euclidian(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def distance(self, v1, v2):
        dist = 0.0
        for i in range(len(v1)):
            d = v1[i] - v2[i]
            dist += (d ** 2)
        return dist

    def winner(self, pattern):
        diff = self.distance(self.weight[0][0], pattern)
        x = 0; y = 0
        for r in range(0, len(self.weight)):
            for c in range(0, len(self.weight[r])):
                d = self.distance(self.weight[r][c], pattern)
                if d < diff:
                    diff = d
                    x = c
                    y = r
        return (x, y, diff)

    def radius(self):
        return (1.0 - (self.step * 1.0) / self.maxStep) * min(self.rows, self.cols, 5)

    def testMap(self, pos, x, y): # pattern p, winner at (x, y)
        for r in range(self.rows):
            for c in range(self.cols):
                dist = self.euclidian(x, y, c, r)
                scale = self.gaussian(dist)
                print "%+.2f " % scale,
            print ""
        print ""
        #print "--More-- ",
        #sys.stdin.readline()

    def gaussian(self, dist):
        if dist == 0:
            scale = .9
        elif dist == 1:
            scale = -.1
        elif dist < self.radius() / 2.0:
            scale = .1
        else:
            scale = 0.0
        return scale

    def gaussian1(self, dist):
        if dist == 0:
            scale = .9
        elif dist < self.radius() * 1/5.0: 
            scale = .9
        elif dist < self.radius() * 2/5.0:
            scale = -.1
        elif dist < self.radius() * 3/5.0:
            scale = .3
        elif dist < self.radius() * 4/5.0:
            scale = .2
        elif dist < self.radius():
            scale = .1
        else:
            scale = 0.0
        return scale
    
    def scale(self):
        return (1.0 - (self.step * 1.0) / self.maxStep) 

    def updateMap(self, pos, x, y): # pattern p, winner at (x, y)
        error = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                scale = self.scale()
                # self.gaussian( self.euclidian(x, y, c, r))
                # if (scale != 0.0):
                if self.euclidian(x, y, c, r) <= 1.0:
                    for i in range( self.vectorLen):
                        e = (self.input[pos][i] - self.weight[r][c][i])
                        error += abs(e)
                        self.weight[r][c][i] += scale * e
                        # (scale * self.radius()) * e
                        if self.weight[r][c][i] < 0.00001: # to protect random array values from
                            self.weight[r][c][i] = 0.0     # getting too small
        return error
                    
    def randomizeOrder(self):
        flag = [0] * len(self.input)
        self.loadOrder = [0] * len(self.input)
        for i in range(len(self.input)):
            pos = int(random.random() * len(self.input))
            while (flag[pos] == 1):
                pos = int(random.random() * len(self.input))
            flag[pos] = 1
            self.loadOrder[pos] = i

    def train(self):
        self.step = 0
        image, x1, y1 = s.readPBM('stephbot2.pbm')
        for t in range(self.maxStep):
            print "Epoch #", t
            error = 0.0
            self.testMap(0, 0, 0)
            self.randomizeOrder()
            for p in self.loadOrder:
                x, y, d = self.winner(self.input[p])
                #print "Winner for input #", p, "is weight at (", x, y, ") (diff was", d,  ")"
                error += self.updateMap(p, x, y)
                #self.testMap(p, x, y)
            self.step += 1
            print "Error =", error
            s.writePBM("som-%d.pbm" % self.step, image, x1, y1)


    def test(self):
        self.loadOrder = range(len(self.input))
        for p in self.loadOrder:
            x, y, d = self.winner(self.input[p])
            print "Input[%d] =" % p, self.input[p],"(%d, %d)" % (x, y)

    def readPBM(self, filename):
        retval = []
        pbm = open(filename, 'r')
        file = pbm.read()
        data = map(lambda line: line.split(), file.splitlines())
        x, y = map(int, data[3])
        data = data[5:]
        for line in data:
            colorLine = map(lambda n: int(n)/255.0, line)
            for i in range(0, len(colorLine), 3):
                r = colorLine[i]
                g = colorLine[i+1]
                b = colorLine[i+2]
                retval.append( (r, g, b))
        print "Loaded ", len(retval), "patterns..."
        return retval, x, y

    def writePBM(self, filename, vector, x1, y1):
        pbm = open(filename, 'w')
        file = pbm.write("P3\n")
        file = pbm.write("# pyro.som\n")
        file = pbm.write("# D.S. Blank\n")
        file = pbm.write("%d %d\n" % (x1, y1))
        file = pbm.write("255\n")
        for p in range(len(vector)):
            x, y, d = self.winner(vector[p])
            pbm.write("%d %d 0\n" % ((x + 1.0)/self.cols * 256, \
                                     (y + 1.0)/self.rows * 256))

if __name__ == '__main__':
    import Numeric
    def sampleData(cnt, size):
        data = Numeric.ones((cnt, size), 'f')
        val = 1.0 / cnt
        for j in range(cnt):
            for i in range(size):
                data[j][i] = val
            val += 1.0 / cnt
        return data

    #samp = sampleData(100, 3)
    s = som(10, 10, 3) # rows, cols; length of high-dimensional input
    #s.setInputs( RandomArray.random((6, 5))) # number of inputs, length of high-dim input
    samp, x, y = s.readPBM('stephbot-partial.pbm')
    s.setInputs( samp ) 
    s.maxStep = 100.0
    s.train()
    #s.test()
