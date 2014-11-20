#!/usr/bin/env python
#
## This tests the uinput library using keyboard inputs.
## The uinput library must be installed, by running within the python-uinput-master directory:
## python setup.py build
## python setup.py install
##
## The terminal window must be focused, and needs root access to run this file

import thread
import time
import sys

from keySimDevice import keySimDevice

# Make our keyboard emulator device
device = keySimDevice()

try:
    # Windows
    from msvcrt import getch
except ImportError:
    # Linux
    def getch():
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

char = None

def keypress():
    global char
    while True:
        char = getch()
        # Exits if ESC is pressed
        if char == chr(27).encode():
            thread.exit()
        elif char == 'a':
            device.moveMouse(-10,0)
        elif char == 'd':
            device.moveMouse(10,0)
        elif char == 'w':
            device.moveMouse(0,-10)
        elif char == 's':
            device.moveMouse(0,10)
        elif char == 'c':
            # Switches focus from terminal window
            device.typeCombo("alt","tab")
        else:
            device.typeMessage("Hello World")


thread.start_new_thread(keypress, ())

while True:
    if char is not None:
        # Break if escape is pressed
        if char == chr(27).encode():
            sys.exit()
        char = None
