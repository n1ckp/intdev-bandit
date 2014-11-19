import sys, subprocess, string

class BleConn():
    def __init__(self, sourceMac, destMac):
        if type(sourceMac) != str or type(destMac) != str:
            print "MAC address needs to be a string"
            sys.exit()

        self.sourceMac = sourceMac
        self.destMac = destMac

    # read a RAW characteristic from a given UUID
    def readRawUUID(self, uuid):
        if type(uuid) != int:
            print "UUID needs to be an integer"
            sys.exit()

        proc = subprocess.Popen(["gatttool", "-t", self.sourceMac, "-b", self.destMac, "--char-read", "--uuid=" + str(uuid)], stdout = subprocess.PIPE)

        return proc.communicate()[0]

    # read a RAW characteristic from a given Handle
    def readRawHandle(self, handle):
        if type(handle) != str:
            print "handle needs to be a string representation of hex address"
            sys.exit()

        proc = subprocess.Popen(["gatttool", "-t", self.sourceMac, "-b", self.destMac, "--char-read", "--handle=" + handle], stdout = subprocess.PIPE)

        return proc.communicate()[0]

    # extract the value from a characteristic of given UUID
    def readValueFromUUID(self, uuid):
        raw = self.readRawUUID(uuid).strip()

        try:
            value = raw[string.rindex(raw, "value:") + 7:]
        except(ValueError):
            print "Error reading value from UUID: " + str(uuid)
            print "[ERROR] " + raw
            sys.exit()

        return value

        # extract the value from a characteristic of given UUID
    def readValueFromHandle(self, handle):
        raw = self.readRawHandle(handle).strip()

        try:
            value = raw[string.rindex(raw, "Characteristic value/descriptor:") + 33:]
        except(ValueError):
            print "Error reading value from Handle: " + handle
            print "[ERROR] " + raw
            sys.exit()

        return value