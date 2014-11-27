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
        self.mMinX = -2564.0
        self.mMinY = -2767.0
        self.mMinZ = -2378.0

        self.mMaxX = 3691
        self.mMaxY = 3319
        self.mMaxZ = 3935

    def process(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        return tuple(self.scaleGyro(gx, gy, gz) + self.scaleAccel(ax, ay, az) + self.scaleMag(mx, my, mz))

    def scaleGyro(self, gx, gy, gz):
        return [self.gSign[0]*gx*math.radians(self.gGainX),
                self.gSign[1]*gy*math.radians(self.gGainY),
                self.gSign[2]*gz*math.radians(self.gGainZ)]

    def scaleAccel(self, ax, ay, az):
        return [self.aSign[0]*(ax >> 4),
                self.aSign[1]*(ay >> 4),
                self.aSign[2]*(az >> 4)]

    def scaleMag(self, mx, my, mz):
        return [(self.mSign[0]*(mx - self.mMinX)) / (self.mMaxX - self.mMinX) - self.mSign[0]*0.5,
                (self.mSign[1]*(my - self.mMinY)) / (self.mMaxY - self.mMinY) - self.mSign[1]*0.5,
                (self.mSign[2]*(mz - self.mMinZ)) / (self.mMaxZ - self.mMinZ) - self.mSign[2]*0.5]
