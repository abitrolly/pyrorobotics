import Gnuplot

class FakeFile:
    def __init__(self):
        pass
    def readline(self):
        return ""
    def close(self):
        pass

class PCAPlot:
    def __init__(self, eigenfile, namefile = None, debug = 0,
                 dimensions = 2, title = None, datatitle = None):
        self.gp = Gnuplot.Gnuplot(debug = debug)
        self.dimensions = dimensions
        # read in eigenvalues, names
        efp = open(eigenfile, "r")
        if namefile:
            nfp = open(namefile, "r")
        else:
            nfp = FakeFile()
        eline = efp.readline()
        nline = nfp.readline()
        dataset = []
        while eline:
            eline = eline.strip()
            label = nline.strip()
            data = eline.split(" ")
            if dimensions == 2:
                if label:
                    self.gp('set label "%s" at %f,%f' %
                            (label, float(data[0]), float(data[1])))
                dataset.append( (float(data[0]), float(data[1])))
            elif dimensions == 3:
                if label:
                    self.gp('set label "%s" at %f,%f,%f' %
                            (label, float(data[0]),
                             float(data[1]), float(data[2])))
                dataset.append( (float(data[0]), float(data[1]),
                                 float(data[2])))
            else:
                raise "DimensionError", \
                      "cannot handle dimensions of %d" % dimensions
            eline = efp.readline()
            nline = nfp.readline()
        efp.close()
        nfp.close()
        self.data = Gnuplot.Data(dataset)
        self.gp('set data style points')
        self.gp.title(title)
        self.data.set_option(title = datatitle)

    def plot(self):
        if self.dimensions == 2:
            self.gp.plot(self.data)
        elif self.dimensions == 3:
            self.gp.splot(self.data)
        else:
            raise "DimensionError", \
                  "cannot handle dimensions of %d" % dimensions

    def replot(self):
        self.gp.replot()

    def hardcopy(self, output):
        self.gp.hardcopy(output)

if __name__ == '__main__':
    pca = PCAPlot("data.pca", "names", title = "Sample PCA Plot")
    pca.plot()
    raw_input()
    pca.data.set_option(title = "Data name")
    pca.replot()
    pca.hardcopy("/tmp/output.ps")
    raw_input()
