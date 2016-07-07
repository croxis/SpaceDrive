# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
__author__ = 'croxis'

from panda3d.core import Vec3
from .renderpipeline.Code.MovementController import MovementController

class MainScreenMovementController(MovementController):
    """Camera location remains stationary. We move in space in other ways!"""
    def _update(self, task):
        """ Internal update method """

        # Update mouse first
        if self.showbase.mouseWatcherNode.hasMouse():
            x = self.showbase.mouseWatcherNode.getMouseX()
            y = self.showbase.mouseWatcherNode.getMouseY()
            self.currentMousePos = [x * 90 * self.mouseSensivity, y * 70 * self.mouseSensivity]

            if self.mouseEnabled:
                diffx = self.lastMousePos[0] - self.currentMousePos[0]
                diffy = self.lastMousePos[1] - self.currentMousePos[1]

                # no move on the beginning
                if self.lastMousePos[0] == 0 and self.lastMousePos[1] == 0:
                    diffx = 0
                    diffy = 0

                self.showbase.camera.setH(self.showbase.camera.getH() + diffx)
                self.showbase.camera.setP(self.showbase.camera.getP() - diffy)

            self.lastMousePos = self.currentMousePos[:]

        # Compute movement in render space
        movementDirection = (Vec3(self.movement[1], self.movement[0], 0)
                             * self.speed
                             * self.showbase.taskMgr.globalClock.getDt() * 100.0)

        # Transform by camera direction
        cameraQuaternion = self.showbase.camera.getQuat(self.showbase.render)
        translatedDirection = cameraQuaternion.xform(movementDirection)


        # zforce is independent of camera direction
        translatedDirection.addZ(
            self.movement[2] * self.showbase.taskMgr.globalClock.getDt() * 40.0 * self.speed)

        self.velocity += translatedDirection*0.15

        # apply new position
        self.showbase.camera.setPos(
            self.showbase.camera.getPos() + self.velocity)

        self.velocity *= self.smoothness  + 0.0

        # transform rotation (keyboard keys)
        rotationSpeed = self.keyboardHprSpeed * 100.0 * self.showbase.taskMgr.globalClock.getDt()
        self.showbase.camera.setHpr(self.showbase.camera.getHpr() + Vec3(self.hprMovement[0],self.hprMovement[1],0) * rotationSpeed )

        return task.cont