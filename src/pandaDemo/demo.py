# All coordinates are Z up
import random
import os, sys, time
sys.path.append(os.path.abspath("../"))

from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CharacterJoint, LineSegs

import numpy as np

import Leg
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

        """
        r_hip_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[0])
        r_hip_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[0])
        r_knee_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[1])
        r_knee_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[1])
        r_ankle_ro = self.bandit.exposeJoint(None, "modelRoot", self.R_LEG_JOINTS[2])
        r_ankle_wo = self.bandit.controlJoint(None, "modelRoot", self.R_LEG_JOINTS[2])
        distances = np.array([r_hip_ro.getDistance(r_knee_ro), r_knee_ro.getDistance(r_ankle_ro)])
        self.r_leg = Leg.Leg(r_hip_ro, r_hip_wo, r_knee_ro, r_knee_wo, r_ankle_ro, r_ankle_wo, distances)
        """

        l_hip_ro = self.bandit.exposeJoint(None, "modelRoot", self.L_LEG_JOINTS[0])
        l_hip_wo = self.bandit.controlJoint(None, "modelRoot", self.L_LEG_JOINTS[0])
        l_knee_ro = self.bandit.exposeJoint(None, "modelRoot", self.L_LEG_JOINTS[1])
        l_knee_wo = self.bandit.controlJoint(None, "modelRoot", self.L_LEG_JOINTS[1])
        l_ankle_ro = self.bandit.exposeJoint(None, "modelRoot", self.L_LEG_JOINTS[2])
        l_ankle_wo = self.bandit.controlJoint(None, "modelRoot", self.L_LEG_JOINTS[2])
        distances = np.array([l_hip_ro.getDistance(l_knee_ro), l_knee_ro.getDistance(l_ankle_ro)])
        self.l_leg = Leg.Leg(l_hip_ro, l_hip_wo, l_knee_ro, l_knee_wo, l_ankle_ro, l_ankle_wo, distances)

        # Draws debug skeleton
        self.bandit.setBin('background', 1)
        self.walkJointHierarchy(self.bandit, self.bandit.getPartBundle('modelRoot'))

        self.stream = StreamRead("/dev/input/smartshoes")
        self.last_t = time.time()
        if True:
            self.cap_file = open("capture.csv", "w")
            taskMgr.add(self.getDeviceData, 'Stream reader')
        else:
            self.cap_file = open("capture.csv", "r")
            all_records = self.cap_file.readlines()
            all_records = [self.interpretRecordLine(line[:-1].split(',')) for line in all_records]
            all_records = zip(*all_records)
            self.record_iter = self.l_leg.ankle_pos_rot.estimateMany(*all_records)
            self.setNextTask(self.l_leg)

    @staticmethod
    def interpretRecordLine(records):
        records = map(float, records)
        angular_velocity, acceleration, magnetic_field = [records[x:x+3] for x in range(0, 9, 3)]

        # Switch axis orientations
        angular_velocity[2], angular_velocity[0] = angular_velocity[0], angular_velocity[2]
        acceleration[2], acceleration[0] = acceleration[0], acceleration[2]
        magnetic_field[2], magnetic_field[0] = magnetic_field[0], magnetic_field[2]

        return (records[17], angular_velocity, acceleration, magnetic_field)

    def getDeviceData(self, task):
        records = self.stream.readFromStream()
        if records and len(records[0]) == 18:
            self.cap_file.write(','.join(records[0]) + "\n")
            records = self.interpretRecordLine(records[0])
            self.l_leg.updateAnkle(*records)
        return task.again

    def useCapturedDeviceData(self, leg, pos, rot):
        self.l_leg.manuallyUpdateAnkle(pos, rot)
        self.setNextTask(leg)

    def setNextTask(self, leg):
        try:
            dt, position, orientation = next(self.record_iter)
            taskMgr.doMethodLater(dt, self.useCapturedDeviceData, 'File reader', extraArgs=[leg, position, orientation])
        except StopIteration:
            pass

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
