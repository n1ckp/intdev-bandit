class DSP():
    def __init__(self, numSignals):
        self.numSignals = numSignals
        self.tMinus1 = [0] * numSignals
        self.tMinus2 = [0] * numSignals

    # Really basic LPF. Upgrade to numpy for more advanced. butterworth etc.
    def lowPass(self, *data):
        if len(data) != self.numSignals:
            print "The LPF needs to have all the signals you stated"

        result = [0] * self.numSignals

        for i in xrange(len(data)):
            result[i] = 0.5 * data[i] + 0.3 * self.tMinus1[i] + 0.2 * self.tMinus2[i]

        self.tMinus2 = self.tMinus1
        self.tMinus1 = list(data)

        return tuple(result)