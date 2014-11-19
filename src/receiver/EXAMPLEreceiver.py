import argparse, sys

from bleconn import BleConn

parser = argparse.ArgumentParser(description = "GATTTOOL wrapper for Bluetooth Low Energy Characteristic Reading from RFduino")
parser.add_argument("MAC", action = "store", type = str, help = "BLE device MAC address e.g. AB:CD:EF:12:34:56")
parser.add_argument("-D", action = "store_true", default = False, dest = "debug", help = "DEBUG mode - print Raw RX packets")
parser.add_argument("-S", action = "store", default = "random", type = str, dest = "sourceMac", help = "Source MAC address (default: random)")
parser.add_argument("-U", action = "store", default = None, type = int, dest = "uuid", help = "Characteristic UUID to read from (RFduino: 2221)")
parser.add_argument("-H", action = "store", default = None, type = int, dest = "handle", help = "Characteristic Handle to read from (RFduino: 0x000e)")
parser.add_argument("-C", action = "store_true", default = False, dest = "continuous", help = "Continuous read mode")
inputArgs = parser.parse_args()

if (not inputArgs.uuid and not inputArgs.handle) or (inputArgs.uuid and inputArgs.handle):
    print "Please specify either a UUID or Handle (not both) to read from"
    parser.print_help()
    sys.exit()

RFduinoConn = BleConn(inputArgs.sourceMac, inputArgs.MAC)

def getValue():
    if inputArgs.uuid:
        return RFduinoConn.readValueFromUUID(inputArgs.uuid)
    else:
        return RFduinoConn.readValueFromHandle(inputArgs.handle)


value = getValue()
if inputArgs.debug:
    print value

while inputArgs.continuous:
    value = getValue()
    if inputArgs.debug:
        print value