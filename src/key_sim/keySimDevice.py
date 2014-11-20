#!/usr/bin/env python
import uinput
import uinput_inputmap

class keySimDevice:
    def __init__(self):
        # Private character mapping
        self.inputmap = uinput_inputmap.INPUT_MAP

        # Emulator device
        self.device = uinput.Device(
                self.inputmap.values() +
                [
                uinput.KEY_LEFTSHIFT,
                uinput.REL_X,
                uinput.REL_Y,
                ])

    def __keypress(self, char):
        charcode = self.inputmap.get(char.lower())
        if char.isupper():
            self.device.emit_combo([self.inputmap.get("shift"), charcode])
        else:
            self.device.emit_click(charcode)

    # Simulates all keypresses for characters in a given message
    def typeMessage(self, message):
        for char in message:
            self.__keypress(char)
        # End with return
        self.__keypress("\n")

    # Simulates combination keypress (e.g. alt-tab)
    def typeCombo(self, input1, input2):
        self.device.emit_combo([self.inputmap.get(input1.lower()),
                                self.inputmap.get(input2.lower())])

    # Simulates mouse movement
    def moveMouse(self,x,y):
        # Move mouse left/right
        self.device.emit(uinput.REL_X, x)
        # Move mouse up/down
        self.device.emit(uinput.REL_Y, y)
