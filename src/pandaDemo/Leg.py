# Adapted from https://github.com/studywolf/blog/tree/master/InvKin
import sys
sys.path.append("../")

import math
import numpy as np
import scipy.optimize

from panda3d.core import LQuaternion, MeshDrawer, OmniBoundingVolume, Vec3, Vec4
from utils.rotationMagic import RotationCorrector
from utils.posRotEstimator import PosRotEstimator

class Leg:
    def __init__(self, hip_ro, hip_wo, knee_ro, knee_wo, ankle_ro, ankle_wo, L, q=[math.pi/4, math.pi/4], q0=np.array([math.pi/4, math.pi/4])):
        """Set up the basic parameters of the leg.
        All lists are in order [hip, knee].

        :param list q: the initial joint angles of the leg
        :param list q0: the default (resting state) joint configuration
        :param list L: the leg segment lengths
        """

        self.hip_ro = hip_ro
        self.hip_wo = hip_wo
        self.knee_ro = knee_ro
        self.knee_wo = knee_wo
        self.ankle_ro = ankle_ro
        self.ankle_wo = ankle_wo

        self.q = q
        self.q0 = q0
        self.L = L

        self.ankle_pos_rot = PosRotEstimator(self.ankle_ro.getPos(), self.ankle_ro.getHpr(render))

        """
        # Debug visuals
        self.sphere = loader.loadModel("sphere.egg")
        self.sphere.setPos(self.ankle_ro.getPos(render))
        self.sphere.setScale(0.1)
        self.sphere.reparentTo(render)

        self.drawer = MeshDrawer()
        self.drawer.setBudget(10)
        self.drawerNode = self.drawer.getRoot()
        #set Drawernode settings
        self.drawerNode.setDepthWrite(False)
        self.drawerNode.setTwoSided(True)
        self.drawerNode.setTransparency(True)
        #add drawerNode to render
        self.drawerNode.setLightOff()
        self.drawerNode.setShaderOff()
        self.drawerNode.node().setBounds(OmniBoundingVolume())
        self.drawerNode.node().setFinal(True)
        self.drawerNode.reparentTo(render)

        taskMgr.add(self.drawtask, "meshdrawer")
        """

    def inv_kin(self, xy):
        """This is just a quick write up to find the inverse kinematics
        for a 2-link leg, using the SciPy optimize package minimization function.

        Given an (x,y) position of the ankle, return a set of joint angles (q)
        using constraint based minimization,
        minimize the distance of each joint from it's default position (q0).

        :param list xy: a tuple of the desired xy position of the leg
        :returns list: the optimal [hip, knee] angle configuration
        """

        def distance_to_default(q, *args):
            """Objective function to minimize
            Calculates the euclidean distance through joint space to the default
            leg configuration. The weight list allows the penalty of each joint
            being away from the resting position to be scaled differently, such
            that the leg tries to stay closer to resting state more for higher
            weighted joints than those with a lower weight.

            :param list q: the list of current joint angles
            :returns scalar: euclidean distance to the default leg position
            """
            weight = [1, 1]
            return np.sqrt(np.sum([(qi - q0i)**2 * wi
                for qi,q0i,wi in zip(q, self.q0, weight)]))

        def x_constraint(q, xy):
            """Returns the corresponding hand xy coordinates for
            a given set of joint angle values [hip, knee],
            and the above defined leg segment lengths, L

            :param list q: the list of current joint angles
            :returns: the difference between current and desired x position
            """
            x = ( self.hip_ro.getX() + self.L[0]*np.cos(q[0]) - self.L[1]*np.cos(q[0]+q[1]) ) - xy[0]
            return x

        def y_constraint(q, xy):
            """Returns the corresponding hand xy coordinates for
            a given set of joint angle values [hip, knee],
            and the above defined leg segment lengths, L

            :param list q: the list of current joint angles
            :returns: the difference between current and desired y position
            """
            y = ( self.hip_ro.getZ() - self.L[0]*np.sin(q[0]) - self.L[1]*np.sin(q[0]+q[1]) ) - xy[1]
            return y

        return scipy.optimize.fmin_slsqp( func=distance_to_default,
            x0=self.q, eqcons=[x_constraint, y_constraint],
            args=(xy,), iprint=0)

    def drawtask(self, task):
        self.drawer.begin(base.cam, render)
        hippos = Vec3(self.hip_ro.getPos(render))
        kneepos = hippos + (self.L[0]*np.cos(self.q[0]), 0, -self.L[0]*np.sin(self.q[0]))
        anklepos = kneepos - (self.L[1]*np.cos(self.q[0]+self.q[1]), 0, self.L[1]*np.sin(self.q[0]+self.q[1]))
        self.drawer.segment(hippos, kneepos, Vec4(0,0,1,1), 0.01, Vec4(1.0,0.0,0.0,0.5))
        self.drawer.segment(kneepos, anklepos, Vec4(0,0,1,1), 0.01, Vec4(1.0,0.0,0.0,0.5))
        self.drawer.end()
        return task.cont

    def manuallyUpdateAnkle(self, pos, rot):
        self.ankle_wo.setPos(pos)
        #print pos
        self.ankle_wo.setHpr(rot.getHpr() + (0, 0, -90))

    def updateAnkle(self, timestamp, gyro, accel, magnetic_field):
        pos, rot = self.ankle_pos_rot.estimate(timestamp, gyro, accel, magnetic_field)
        self.manuallyUpdateAnkle(pos, rot)
