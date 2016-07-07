class BulletPhysicsComponent(object):
    """Contains reference to bullet shape and node as well as SOI for
    planetary gravitational influence.

    zonex and zoney is the id of the bullet world. The true
    position is is worldx + nodePath.getX()"""
    bulletShape = None
    node = None
    nodePath = None
    debugNode = None
    debugNodePath = None
    currentThrust = 0
    currentTorque = 0
    currentSOI = None  # EntityID
    zonex = 0
    zoney = 0

    def get_true_pos(self, debug=False):
        '''Returns the "true" position of this object'''
        if debug:
            print(self.nodePath.getName(), self.zoney * physics.ZONESIZE, self.nodePath.getY(), self.zoney * physics.ZONESIZE + self.nodePath.getY())
        return LPoint3d(
            self.zonex * physics.ZONESIZE + self.nodePath.getX(),
            self.zoney * physics.ZONESIZE + self.nodePath.getY(),
            self.nodePath.getZ()
        )

    def setTruePos(self, truex, truey):
        '''Converts the true pos into the proper zone system'''
        physics.setZone(self, truex, truey)
