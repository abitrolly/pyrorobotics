import Gnuplot

class TreePlot:
    def __init__(self, filename):
        self.gp = Gnuplot.Gnuplot()
        fp = open(filename, "r")
        line = fp.readline()
        while line:
            line = line.strip()
            if line.find('"') >= 0:
                data = line.split(" ")
                label = line[line.find('"')+2:-1]
                self.gp('set label "%s" at %f,%f' %
                        (label, float(data[0]), float(data[1])))
            line = fp.readline()
        fp.close()
        self.file = Gnuplot.File(filename)
        self.gp('set data style lines')
        self.file.set_option(title = None)

    def plot(self):
        self.gp.plot(self.file)

    def replot(self):
        self.gp.replot()

if __name__ == '__main__':
    tree = TreePlot("data.tree")
    tree.plot()
    raw_input()
