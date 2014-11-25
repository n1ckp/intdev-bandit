import math

class Calibration():
    # General
    gSign = [1, 1, 1]
    aSign = [-1, -1, -1]
    mSign = [1, 1, 1]

    # Accelerometer
    # 3.9 mg/digit
    # 1 g = 256
    gravity = 256

    # Gyro
    gGainX = 0.07
    gGainY = 0.07
    gGainZ = 0.07

    @staticmethod
    def scaleGyro(data):
        return data["x"]*radians(gGainX), data["y"]*radians(gGainY), data["z"]*radians(gGainZ)

    # Magnetometer (Constants need calibrating from real device)
    mMinX = -421
    mMinY = -639
    mMinZ = -238

    mMaxX = 424
    mMaxY = 295
    mMaxZ = 472

    kpRollPitch = 0.02
    kiRollPitch = 0.00002
    kpYaw = 1.2
    kiYaw = 0.00002