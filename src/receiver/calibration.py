import math

class Calibration():
    def __init__(self):
        # General
        self.gSign = [1, 1, 1]
        self.aSign = [-1, -1, -1]
        self.mSign = [1, 1, 1]

        # Accelerometer
        # 3.9 mg/digit
        # 1 g = 256
        self.gravity = 256

        # Gyro
        self.gGainX = 0.07
        self.gGainY = 0.07
        self.gGainZ = 0.07

         # Magnetometer (Constants need calibrating from real device)
        self.mMinX = -421
        self.mMinY = -639
        self.mMinZ = -238

        self.mMaxX = 424
        self.mMaxY = 295
        self.mMaxZ = 472

        self.kpRollPitch = 0.02
        self.kiRollPitch = 0.00002
        self.kpYaw = 1.2
        self.kiYaw = 0.00002

        self.dirCosine = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.updateVals = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.tempVals = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        self.gyroVec = [0] * 3
        self.accelVec = [0] * 3

        self.pitch = 0
        self.roll = 0
        self.yaw = 0

        # integration timer
        self.DT = 0.02

    def process(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        self.valsUpdate(gx, gy, gz, ax, ay, az)

        return self.calcEulerAngles()

    def valsUpdate(self, gx, gy, gz, ax, ay, az):
        self.gyroVec = self.scaleGyro({"x" : gx, "y" : gy, "z" : gz})
        self.accelVec = self.scaleAccel({"x" : ax, "y" : ay, "z" : az})

        self.updateVals[0][1] = -self.DT * self.gyroVec[2]
        self.updateVals[0][2] = self.DT * self.gyroVec[1]
        self.updateVals[1][0] = self.DT * self.gyroVec[2]

        self.updateVals[1][2] = -self.DT * self.gyroVec[0]
        self.updateVals[2][0] = -self.DT * self.gyroVec[1]
        self.updateVals[2][1] = self.DT * self.gyroVec[0]

    def scaleAccel(self, data):
        return [self.aSign[0]*(data["x"] >> 4),
                self.aSign[1]*(data["y"] >> 4),
                self.aSign[2]*(data["z"] >> 4)]

    def scaleGyro(self, data):
        return [self.gSign[0]*data["x"]*radians(self.gGainX),
                self.gSign[1]*data["y"]*radians(self.gGainY),
                self.gSign[2]*data["z"]*radians(self.gGainZ)]

    def calcEulerAngles(self):
        pitch = -asin(self.dirCosine[2][0])
        roll = atan2(self.dirCosine[2][1], self.dirCosine[2][2])
        yaw = atan2(self.dirCosine[1][0], self.dirCosine[0][0])
        return pitch, roll, yaw