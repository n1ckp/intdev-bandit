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
while True:
	records = stream.readFromStream()
	if records:
		print records
