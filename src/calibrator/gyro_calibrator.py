# Prints out the calibration values for the gyro
# This can be terminated early with Ctrl+C and still print out the values

#Allows for relative import
import sys, os, argparse
sys.path.append(os.path.abspath("../"))

from utils.streamUtils.StreamRead import StreamRead

parser = argparse.ArgumentParser(description = "Demo stream reading application - reads data from smart shoes stream and print to terminal")
parser.add_argument("-s", action = "store", default = "/dev/input/smartshoes", type = str, dest = "streamFile", help = "The Name of the stream to write to (default: /dev/input/smartshoes)")
inputArgs = parser.parse_args()

#open stream reader
stream = StreamRead(inputArgs.streamFile)

#continually poll stream
iterations = 0
x = 0.0
y = 0.0
z = 0.0
while iterations < 32:
    records = stream.readFromStream()
    if records and len(records[0]) == 10:
        x += float(records[0][3])
        y += float(records[0][4])
        z += float(records[0][5])
        iterations += 1

print "Offsets: {}, {}, {}".format(x/iterations, y/iterations, z/iterations)
