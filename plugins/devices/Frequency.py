import ossaudiodev, struct, math, FFT, Numeric, time
from pyrobot.robot.device import Device

class FrequencyDevice(Device):
    def __init__(self, dev = "/dev/dsp"):
        Device.__init__(self, "frequency")
        self.deviceName = dev
        self.status = "closed"
        self.number_of_channels= 1
        self.sample_rate= 8000
        self.sample_width= 1
        self.format = ossaudiodev.AFMT_U8
        self.minFreq = 20
        self.maxFreq = 3500
        self.debug = 0
        if self.debug:
            self.setFile("770.txt")

    def initialize(self, mode):
        self.dev = ossaudiodev.open(self.deviceName, mode)
        self.dev.setparameters(self.format,
                              self.number_of_channels,
                              self.sample_rate)
        self.status = mode
        
    def playTone(self, freq, seconds):
        """ freq example: 550 = middle C """
        if self.status != "w":
            self.initialize("w")
        sample = [128] * int(self.sample_rate * seconds)
        if type(freq) == type(1):
            freq = [freq]
        freqPortion = 127.0 / len(freq)
        for f in freq:
            for n in range(len(sample)):
                sample[n] += int(freqPortion * math.sin(n * 2 * math.pi * f/self.sample_rate))
        self.dev.write("".join(map(chr,sample)))
        self.dev.flush()

    def read(self, seconds):
        if self.status != "r":
            self.initialize("r")
        buffer = self.dev.read(int(self.sample_rate * seconds))
        size = len(buffer)
        return struct.unpack(str(size) + "B", buffer)

    def setFile(self, filename):
        self.debug = 1
        self.filename = filename
        self.fp = open(self.filename, "r")

    def readFile(self, seconds):
        data = None
        try:
            data = eval(self.fp.readline())
        except:
            self.fp = open(self.filename, "r")
            try:
                data = eval(self.fp.readline())
            except:
                print "Failed reading file '%s'" % self.filename
        time.sleep(seconds)
        return data[:int(seconds * self.sample_rate)]

    def getFreq(self, seconds):
        # change to read from the buffer, rather than block
        if self.debug:
            data = self.readFile(1)
        else:
            data = self.read(seconds)
        transform = FFT.real_fft(data).real
        minFreqPos = self.minFreq
        maxFreqPos = self.maxFreq
        freq = Numeric.argmax(transform[1+minFreqPos:maxFreqPos])
        value = transform[1+minFreqPos:maxFreqPos][freq]
        domFreq = (freq + self.minFreq) / seconds
        if self.debug and abs(value) > 8000 and self.minFreq < domFreq < self.maxFreq:
            print "Frequence:", domFreq, "Value:", value, "Volume:", transform[0]
        return (domFreq, value, transform[0])

    def close(self):
        if self.status != "closed":
            self.dev.close()
            self.status = "closed"

if __name__ == "__main__":
    sd = FrequencyDevice("/dev/dsp")
    sd.playTone(770, 1)
    sd.playTone(852, 1)
    for col in [697, 770, 852, 941]:
        for row in [1209, 1336, 1477, 1633]:
            sd.playTone((row, col), 1)
    #sd.setFile("697.txt")
    while 1:
        print sd.getFreq(1)
        
## DTMF Tones

##                  1209 Hz 1336 Hz 1477 Hz 1633 Hz

##                           ABC     DEF
##    697 Hz          1       2       3       A

##                   GHI     JKL     MNO
##    770 Hz          4       5       6       B

##                   PRS     TUV     WXY
##    852 Hz          7       8       9       C

##                           oper
##    941 Hz          *       0       #       D


def INIT(robot):
    return {"frequency": FrequencyDevice("/dev/dsp")}
