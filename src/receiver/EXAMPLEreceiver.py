import argparse, sys, struct, binascii

from bleconn import BleConn
from calibration import Calibration
from dsp import DSP

parser = argparse.ArgumentParser(description = "GATTTOOL wrapper for Bluetooth Low Energy Characteristic Reading from RFduino")
parser.add_argument("MAC", action = "store", type = str, help = "BLE device MAC address e.g. AB:CD:EF:12:34:56")
parser.add_argument("-D", action = "store_true", default = False, dest = "debug", help = "DEBUG mode - print Raw RX packets")
parser.add_argument("-S", action = "store", default = "random", type = str, dest = "sourceMac", help = "Source MAC address (default: random)")
parser.add_argument("-U", action = "store", default = None, type = int, dest = "uuid", help = "Characteristic UUID to read from (RFduino: 2221)")
parser.add_argument("-H", action = "store", default = None, type = int, dest = "handle", help = "Characteristic Handle to read from (RFduino: 0x000e)")
parser.add_argument("-C", action = "store_true", default = False, dest = "continuous", help = "Continuous read mode")
parser.add_argument("-R", action = "store_true", default = False, dest = "raw", help = "Raw (Uncalibrated) Sensor data output")
parser.add_argument("-LPF" action = "store_true", default = False, dest = "lpf", help = "Pass sensor values through a FIR Low Pass Filter")
parser.add_argument("-i", action = "store", default = "hci0", type = str, dest = "interface", help = "BLE interface (default: hci0)")
inputArgs = parser.parse_args()

if (not inputArgs.uuid and not inputArgs.handle) or (inputArgs.uuid and inputArgs.handle):
    print "Please specify either a UUID or Handle (not both) to read from"
    parser.print_help()
    sys.exit()

RFduinoConn = BleConn(inputArgs.sourceMac, inputArgs.MAC, inputArgs.interface)

def getValue():
    if inputArgs.uuid:
        return RFduinoConn.readValueFromUUID(inputArgs.uuid)
    else:
        return RFduinoConn.readValueFromHandle(inputArgs.handle)

def unpackFloat(hex):
    return struct.unpack("f", binascii.unhexlify(hex))[0]

def unpackInt(hex):
    return struct.unpack("h", binascii.unhexlify(hex))[0]

c = Calibration()
dsp = DSP(9)

value = getValue()
if inputArgs.debug:
    print value

while inputArgs.continuous:
    value = getValue()

    hexStr = "".join(value.split(" "))
    gx = unpackInt(hexStr[:4])
    gy = unpackInt(hexStr[4:8])
    gz = unpackInt(hexStr[8:12])
    ax = unpackInt(hexStr[12:16])
    ay = unpackInt(hexStr[16:20])
    az = unpackInt(hexStr[20:24])
    mx = unpackInt(hexStr[24:28])
    my = unpackInt(hexStr[28:32])
    mz = unpackInt(hexStr[32:36])

    if not inputArgs.raw:
        gx, gy, gz, ax, ay, az, mx, my, mz = c.process(gx, gy, gz, ax, ay, az, mx, my, mz)

    if inputArgs.lpf:
        gx, gy, gz, ax, ay, az, mx, my, mz = dsp.lowPass(gx, gy, gz, ax, ay, az, mx, my, mz)

    if inputArgs.debug:
        #print value
        print "gx: " + str(gx) + " gy: " + str(gy) + " gz: " + str(gz) + " ax: " + str(ax) + " ay: " + str(ay) + " az: " + str(az) + " mx: " + str(mx) + " my: " + str(my) + " mz: " + str(mz)