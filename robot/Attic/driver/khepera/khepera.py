import SerialConnection
import termios

sc = SerialConnection.SerialConnection("/dev/ttyS1", termios.B38400)
sc.writeline("N\n")
print sc.readline(1)
