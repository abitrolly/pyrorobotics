import operator, string

def inner(a, b):
    return float(reduce(operator.add, [x * y for (x, y) in zip(a, b)]))
def fmt(list): return string.join([str(v) for v in list])

class Art:
    def __init__(self):
        self.labeled_units = []

    def train(self, labels, inputs, vigilance):
        for (label, input) in zip(labels, inputs):
            self.train1(label, input, vigilance)

    def train1(self, label, input, vigilance):
        dimension = len(input)
        tagged_units = []
        for labeled_unit in self.labeled_units:
            unit = labeled_unit[1]
            comparison = inner(unit, input)/inner(unit, unit)
            tagged_units.append([comparison, labeled_unit])
        tagged_units.sort()
        tagged_units.reverse()
        lensq = inner(input, input)
        for (comparison, labeled_unit) in tagged_units:
            unit = labeled_unit[1]
            if comparison <= lensq/dimension: break
            if inner(unit, input)/lensq >= vigilance:
                print "\naccept", labeled_unit[0], fmt(labeled_unit[1])
                print "   for", label, fmt(input)
                new_weights = [x * y for (x, y) in zip(unit, input)]
                labeled_unit[1] = new_weights
                labeled_unit[0] += label
                print "\nbecome", labeled_unit[0], fmt(labeled_unit[1])
                return
        print "\nadd", label, fmt(input)
        self.labeled_units.append( [label, input])
                
    def test(self, labels, inputs):
        print "total category vectors:", len(self.labeled_units)
        for (label, input) in zip(labels, inputs):
            result = self.test1(label, input)
            print "\nmatch", label, fmt(input)
            print "to", result[0], fmt(result[1])

    def test1(self, label, input):
        bestUnit = None
        bestValue = -1
        for u in self.labeled_units:
            unit = u[1]
            comparison = inner(unit, input)/inner(unit, unit)
            #print 'comparison is', comparison
            if comparison >= bestValue:
                bestUnit = u
                bestValue = comparison
        return bestUnit


if __name__ == "__main__":
    vigilance = .5
    f = open("letters.50.in")
    labels = []
    inputs = []
    for line in f.readlines():
        line = line.split()
        labels.append(line[0])
        inputs.append([int(v) for v in line[1:]])
    f.close()
    network = Art()
    network.train(labels[:26], inputs[:26], vigilance)
    network.test(labels[26:], inputs[26:])
