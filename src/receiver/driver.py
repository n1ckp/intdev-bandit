#!/usr/bin/python3

import bluetooth

DEBUG = True
RFDUINO_ADDR = "B8:8D:12:3A:87:53"

def dbgPrint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def canFindRFduino(expectedAddr):
    dbgPrint("Finding RFduino")
    name = bluetooth.lookup_name(expectedAddr)
    if name:
        return True

    dbgPrint("Trying fallback discovery!")

    devices = bluetooth.discover_devices(lookup_names=True)
    dbgPrint("Found {} devices:".format(len(devices)))
    if DEBUG:
        for addr, name in devices:
            print("{}: {}".format(name, addr))

    if next(filter((lambda x: x[0] == expectedAddr), devices), None):
        return True

    return False

if __name__ == "__main__":
    if DEBUG:
        if canFindRFduino(RFDUINO_ADDR):
            print("Found RFduino!")
        else:
            print("Cannot find RFduino!")
