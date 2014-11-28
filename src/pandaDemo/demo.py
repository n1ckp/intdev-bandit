# All coordinates are Z up
import random
import sys, os
sys.path.append(os.path.abspath("../"))

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CharacterJoint, LineSegs

import numpy as np

import Leg, rotationMagic
from utils.streamUtils.StreamRead import StreamRead

class MayaDemo(ShowBase):
    R_LEG_JOINTS = ["joint6", "joint7", "joint8"]
    L_LEG_JOINTS = ["joint10", "joint11", "joint12"]

    def __init__(self):
        ShowBase.__init__(self)

        self.bandit = Actor("banditRiggedNoHat.egg")
        self.bandit.makeSubpart("r_leg", self.R_LEG_JOINTS)
        self.bandit.makeSubpart("l_leg", self.L_LEG_JOINTS)

        headJoint = self.bandit.exposeJoint(None, "modelRoot", "joint5")
        hat = loader.loadModel("{}_hat.egg".format(random.randint(0, 7)))
        hat.setPos(0, 0, -0.08)
        hat.setHpr(-90, 0, 0)
        hat.setScale(0.35)
        hat.reparentTo(headJoint)

        self.bandit.reparentTo(render)

        r_hip_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[0])
        r_hip_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[0])
        r_knee_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[1])
        r_knee_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[1])
        r_ankle_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[2])
        r_ankle_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[2])
        distances = np.array([r_hip_ro.getDistance(r_knee_ro), r_knee_ro.getDistance(r_ankle_ro)])
        self.r_leg = Leg.Leg(r_hip_ro, r_hip_wo, r_knee_ro, r_knee_wo, r_ankle_ro, r_ankle_wo, distances)

        l_hip = self.bandit.controlJoint(None, "modelRoot", self.L_LEG_JOINTS[0])
        l_knee = self.bandit.controlJoint(None, "modelRoot", self.L_LEG_JOINTS[1])
        l_ankle = self.bandit.exposeJoint(None, "modelRoot", self.L_LEG_JOINTS[2])
        distances = np.array([l_hip.getDistance(l_knee), l_knee.getDistance(l_ankle)])
        #self.l_leg = Leg.Leg(l_hip, l_knee, l_ankle, distances)

        self.accept("arrow_up", self.r_leg.moveAnkle, [(0, 0, 0.1)])
        self.accept("arrow_down", self.r_leg.moveAnkle, [(0, 0, -0.1)])

        self.accept("arrow_left", self.r_leg.rotateAnkle, [(0, 0, 10)])
        self.accept("arrow_right", self.r_leg.rotateAnkle, [(0, 0, -10)])

        # Draws debug skeleton
        self.bandit.setBin('background', 1)
        self.walkJointHierarchy(self.bandit, self.bandit.getPartBundle('modelRoot'))

        self.stream = StreamRead("/dev/input/smartshoes")
        self.last_t = globalClock.getFrameTime()
        taskMgr.add(self.getDeviceData, 'Stream reader')

    def getDeviceData(self, task):
        records = self.stream.readFromStream()
        if records and len(records[0]) == 9:
            # TODO: Get a dt from the reciever
            # This timing code isn't strictly true
            time = globalClock.getFrameTime()
            dt = time - self.last_t
            self.last_t = time
            records = map(float, records[0])
            angular_velocity, acceleration, magnetic_field = [records[x:x+3] for x in range(0, 9, 3)]
            rotationMagic.rotationMagic(self.r_leg.ankle_rotation, dt, angular_velocity, acceleration, magnetic_field)
            self.r_leg.updateAnkleRotation()
        return task.again

    def walkJointHierarchy(self, actor, part, parentNode = None, indent = ""):
        if isinstance(part, CharacterJoint):
            np = actor.exposeJoint(None, 'modelRoot', part.getName())

            if parentNode and parentNode.getName() != "root":
                lines = LineSegs()
                lines.setThickness(3.0)
                lines.setColor(random.random(), random.random(), random.random())
                lines.moveTo(0, 0, 0)
                lines.drawTo(np.getPos(parentNode))
                lnp = parentNode.attachNewNode(lines.create())
                lnp.setBin("fixed", 40)
                lnp.setDepthWrite(False)
                lnp.setDepthTest(False)

            parentNode = np

        for child in part.getChildren():
            self.walkJointHierarchy(actor, child, parentNode, indent + "  ")

if __name__ == "__main__":
    app = MayaDemo()
    app.run()
