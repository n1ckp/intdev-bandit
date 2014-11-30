import math

class Calibration():
    def __init__(self):
        # General
        self.gSign = [1, -1, 1]
        self.aSign = [-1, -1, -1]
        self.mSign = [1, 1, 1]

        # Accelerometer
        # 3.9 mg/digit
        # 1 g = 256
        self.aScale = 0.000244

        # Gyro
        self.gGainX = math.radians(0.07)
        self.gGainY = math.radians(0.07)
        self.gGainZ = math.radians(0.07)
        self.gOffsetX = -0.055822625
        self.gOffsetY = -0.0302865
        self.gOffsetZ = -0.882037125

         # Magnetometer (Constants need calibrating from real device)
        self.mMinX = -2564.0
        self.mMinY = -2767.0
        self.mMinZ = -2378.0

        self.mMaxX = 3691.0
        self.mMaxY = 3319.0
        self.mMaxZ = 3935.0

    def process(self, gx, gy, gz, ax, ay, az, mx, my, mz):
        ax = int(ax)
        ay = int(ay)
        az = int(az)
        return tuple(self.scaleGyro(gx, gy, gz) + self.scaleAccel(ax, ay, az) + self.scaleMag(mx, my, mz))

    def scaleGyro(self, gx, gy, gz):
        return [self.gSign[0]*(gx-self.gOffsetX)*self.gGainX,
                self.gSign[1]*(gy-self.gOffsetY)*self.gGainY,
                self.gSign[2]*(gz-self.gOffsetZ)*self.gGainZ]

    def scaleAccel(self, ax, ay, az):
        return [self.aSign[0]*ax*self.aScale,
                self.aSign[1]*ay*self.aScale,
                self.aSign[2]*az*self.aScale]

    def scaleMag(self, mx, my, mz):
        return [(self.mSign[0]*(mx - self.mMinX)) / (self.mMaxX - self.mMinX) - self.mSign[0]*0.5,
                (self.mSign[1]*(my - self.mMinY)) / (self.mMaxY - self.mMinY) - self.mSign[1]*0.5,
                (self.mSign[2]*(mz - self.mMinZ)) / (self.mMaxZ - self.mMinZ) - self.mSign[2]*0.5]
