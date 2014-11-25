#Allows for relative import
import sys, os, argparse
sys.path.append(os.path.abspath("../"))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation

from utils.streamUtils.StreamRead import StreamRead


parser = argparse.ArgumentParser(description = "Demo stream reading application - reads data from smart shoes stream and print to terminal")
parser.add_argument("-s", action = "store", default = "/dev/input/smartshoes", type = str, dest = "streamFile", help = "The Name of the stream to write to (default: /dev/input/smartshoes)")
inputArgs = parser.parse_args()

#open stream reader
stream = StreamRead(inputArgs.streamFile)

class SubplotAnimation(animation.TimedAnimation):
    def __init__(self):
        fig = plt.figure()
        self.axes = []
        self.lines = []
        for i in xrange(0, 9):
            axis = fig.add_subplot(3, 3, i+1)
            axis.set_ylim(-1, 1)
            axis.set_xlim(0, 50)
            axis.grid()
            self.axes.append(axis)

            line = Line2D([], [])
            self.lines.append(line)
            axis.add_line(line)

        self.xdata = range(0, 50)
        self.ydatas = []
        for i in xrange(0, 9):
            self.ydatas.append([0] * 50)

        animation.TimedAnimation.__init__(self, fig, interval=50, blit=True)

    def _draw_frame(self, framedata):
        records = stream.readFromStream()
        if not records or len(records[0]) < 9:
            return

        values = map(int, records[0])
        t = framedata
        for i in xrange(0, 9):
            self.ydatas[i].pop(0)
            self.ydatas[i].append(values[i])
            self.lines[i].set_data(self.xdata, self.ydatas[i])

        if t >= 5:
            for i in xrange(0, 9, 3):
                ymin, ymax = self.axes[i].get_ylim()

                if max(values[i:i+3]) >= ymax or min(values[i:i+3]) <= ymin:
                    minimum = min(ymin + [min(values[i:i+3])])
                    maximum = max(ymax + [max(values[i:i+3])])
                    for j in xrange(i, i+3):
                        self.axes[j].set_ylim(minimum, maximum)
                        self.axes[j].figure.canvas.draw()

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(1000))

ani = SubplotAnimation()
plt.show()
