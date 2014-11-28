# Prints out the calibration values for the accelerometer
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
xs = []
ys = []
zs = []
try:
    while len(xs) < 1000:
        records = stream.readFromStream()
        if records and len(records[0]) == 10:
            xs.append(int(records[0][6]))
            ys.append(int(records[0][7]))
            zs.append(int(records[0][8]))
            print "\r{}".format(len(xs)),
finally:
    print "Mins: {}, {}, {}".format(min(xs), min(ys), min(zs))
    print "Maxs: {}, {}, {}".format(max(xs), max(ys), max(zs))
