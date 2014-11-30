from itertools import izip
import time

from panda3d.core import LQuaternion, Vec3
from scipy import signal

from rotationMagic import RotationCorrector

class PosRotEstimator():
    def __init__(self, init_pos, init_rot=None):
        self.last_t = time.time()
        self.last_vel = Vec3()

        self.high_filter_cut_off = 0.001
        self.low_filter_cut_off = 5

        self.rotation = RotationCorrector(init_rot)
        self.init_position = init_pos
        self.position = init_pos

    def fixAccelToEarth(self, accel, orientation=None):
        if orientation is None:
            orientation = self.rotation.rotation
        # Rotate body accelerations to Earth orientation
        # TODO: Is this the best way of determining Earth orientation?
        acc = orientation * LQuaternion(0, accel) * orientation.conjugate()
        acc *= 9.81 # m/s/s
        return Vec3(acc[1], acc[2], acc[3] - 9.81)

    def estimate(self, timestamp, gyro, accel, magnetic_field):
        dt = timestamp - self.last_t
        self.last_t = timestamp

        gyro = Vec3(*gyro)
        accel = Vec3(*accel)

        b, a = signal.butter(1, (2*self.high_filter_cut_off)/(10/dt), 'high')
        w, h = signal.freqs(b, a, [accel.length()])
        accel_mag_filtered = abs(h[0])

        b, a = signal.butter(1, (2*self.low_filter_cut_off)/(10/dt), 'low')
        w, h = signal.freqs(b, a, [accel_mag_filtered])
        accel_mag_filtered = abs(h[0])

        orientation = self.rotation.rotationMagic(timestamp, gyro, accel, magnetic_field)

        acc = self.fixAccelToEarth(accel)

        # If is stationary
        # TODO: Combine this with pressure sensor data
        if accel_mag_filtered < 0.05:
            velocity = Vec3()
        else:
            velocity = self.last_vel + acc * dt

        self.last_vel = velocity

        # Cannot account for integral drift here because we aren't postprocessing
        # TODO: But we can when at a stationary position

        self.position = self.position + velocity * dt
        return (self.position, orientation)

    def estimateMany(self, timestamps, gyros, accels, magnetic_fields):
        gyros = [Vec3(*gyro) for gyro in gyros]
        accels = [Vec3(*accel) for accel in accels]
        magnetic_fields = [Vec3(*magnetic_field) for magnetic_field in magnetic_fields]

        # TODO: Make RotationCorrector not depend on this
        # (or merge it into this class)
        self.rotation.last_t = timestamps[0]
        # TODO: Rough estimate! :S
        dt = 1.0/256.0

        b, a = signal.butter(1, (2 * self.high_filter_cut_off) / (1/dt), 'high')
        w, h = signal.freqs(b, a, [accel.length() for accel in accels[1:]])
        accel_mag_filtereds = map(abs, h)

        b, a = signal.butter(1, (2 * self.low_filter_cut_off) / (1/dt), 'low')
        w, h = signal.freqs(b, a, accel_mag_filtereds)
        accel_mag_filtereds = map(abs, h)

        orientations = [self.rotation.rotationMagic(timestamp, gyro, accel, magnetic_field) for timestamp, gyro, accel, magnetic_field in izip(timestamps, gyros, accels, magnetic_fields)]

        accs = [self.fixAccelToEarth(accel, orientation) for accel, orientation in izip(accels, orientations)]
        # FIXME: Why does using timestamps not work? Our dt is fairly consistent though so we could hard code it?
        #dts = [t-last_t for last_t, t in izip(timestamps[:-1], timestamps[1:])]
        dts = [dt] * (len(timestamps) - 1)

        stationaries = [accel_mag_filtered < 0.05 for accel_mag_filtered in accel_mag_filtereds]

        velocities = []
        last_vel = Vec3()
        for stationary, acc, dt in izip(stationaries, accs, dts):
            if stationary:
                velocities.append(Vec3())
            else:
                velocities.append(last_vel + acc * dt)
            last_vel = velocities[-1]

        def findNextEnd(iterator):
            index, _ = next(i for i, ij in iterator if ij[1]-ij[0] == 1)
            return index

        def findNextStart(iterator):
            index, _ = next(i for i, ij in iterator if ij[1]-ij[0] == -1)
            return index

        try:
            stationary_iter = enumerate(izip(stationaries[:-1], stationaries[1:]))
            stationary_start = 0
            while True:
                stationary_end = findNextEnd(stationary_iter)
                num_samples = stationary_end - stationary_start
                drift_rate = velocities(stationary_end-1) / num_samples
                for i, j in enumerate(xrange(stationary_start, stationary_end)):
                    velocities[j] = velocities[j] - (i * drift_rate)
                stationary_start = findNextStart(stationary_iter)
        except StopIteration:
            pass

        positions = [self.init_position]
        for velocity, dt in izip(velocities, dts):
            positions.append(positions[-1] + velocity * dt)

        return izip(dts, positions, orientations)
