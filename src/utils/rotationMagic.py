import time

from panda3d.core import LMatrix4, LQuaternion, Vec3

class RotationCorrector():
    def __init__(self, init_rotation=None):
        if init_rotation is None:
            self.rotation = LQuaternion()
        else:
            self.rotation = LQuaternion(1, *init_rotation)
        self.last_t = time.time()

    def getHpr(self):
        return self.rotation.getHpr()

    def setHpr(self, *args, **kwargs):
        self.rotation.setHpr(*args, **kwargs)

    @staticmethod
    def rotationFromCompass(acceleration, magnetic_field):
        down = -acceleration
        east = down.cross(magnetic_field)
        north = east.cross(down)

        east.normalize()
        north.normalize()
        down.normalize()

        r = LMatrix4()
        r.setRow(0, north)
        r.setRow(1, east)
        r.setRow(2, down)
        return r

    @staticmethod
    def rotate(rotation, w, dt):
        rotation *= LQuaternion(1, w*dt/2)
        rotation.normalize()

    def rotationMagic(self, timestamp, angular_velocity, acceleration, magnetic_field):
        dt = timestamp - self.last_t
        self.last_t = timestamp

        angular_velocity = Vec3(*angular_velocity)
        acceleration = Vec3(*acceleration)
        magnetic_field = Vec3(*magnetic_field)
        correction = (0, 0, 0)

        if abs(acceleration.length() - 1) <= 0.3:
            correction_strength = 1
            rotationCompass = self.rotationFromCompass(acceleration, magnetic_field)
            rotationMatrix = LMatrix4()
            self.rotation.extractToMatrix(rotationMatrix)

            correction = rotationCompass.getRow3(0).cross(rotationMatrix.getRow3(0))
            correction += rotationCompass.getRow3(1).cross(rotationMatrix.getRow3(1))
            correction += rotationCompass.getRow3(2).cross(rotationMatrix.getRow3(2))
            correction *= correction_strength

        self.rotate(self.rotation, angular_velocity + correction, dt)
        return self.rotation
