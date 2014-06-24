from panda3d.core import NodePath, Point3, Vec3

import sandbox

import celestial_components as cel_comps
import physics_components as phys_comps
import universals

from direct.directnotify.DirectNotify import DirectNotify
log = DirectNotify().newCategory("SpaceDrive Physics")

def getPhysics():
    return sandbox.getSystem(PhysicsSystem)


class PhysicsSystem(sandbox.EntitySystem):
    """System that interacts with the Bullet physics world.
    Meshes are made in standard SI (meters, newtons).
    Internally we autoscale down to km. A factor of 1000.
    IE 1 blender unit = 1 m. 1 panda unit = 1 km.
    Configuration files units are km, metric ton, kilonewtons"""
    #TODO: Scale config to standard SI and programmaticly adjust to
    # km metric ton and kilonewtons
    def init(self):
        #self.accept("addSpaceship", self.addSpaceship)
        self.accept('setThrottle', self.setThrottle)
        self.counter = 0

    def begin(self):
        """Nab a copy of the solar system coordinates. No because of threading"""


    def process(self, entity):
        physcomp = entity.getComponent(phys_comps.BulletPhysicsComponent)
        if not physcomp.node.is_active():
            physcomp.node.setActive(True)
        celestial_bodies = sandbox.getEntitiesByComponentType(cel_comps.CelestialComponent)
        # Probably very expensive. Will need optimization later
        # We assume a single star solar system. Will need to update the
        # sol system structure for multiple star solar systems
        soi = False
        previousR = 0
        for body in celestial_bodies:
            body_component = body.getComponent(cel_comps.CelestialComponent)
            distance = (body_component.truePos
                - physcomp.getTruePos()).length()
            if distance < body_component.soi:
                if not soi:
                    previousR = distance
                    soi = True
                    physcomp.currentSOI = body.id
                elif distance < previousR:
                    physcomp.currentSOI = body.id
        if not soi:
            #shipPhysics.currentSOI = universals.defaultSOIid
            log.warning("No SOI for " + str(entity))

        celestial_component = sandbox.entities[physcomp.currentSOI].getComponent(
            cel_comps.CelestialComponent)
        vector = celestial_component.truePos - physcomp.getTruePos()
        distance = vector.length() * 1000
        gravityForce = Vec3(0, 0, 0)
        if distance:
            gravity = universals.G * celestial_component.mass * physcomp.node.getMass() / distance ** 2
            #print "Gravity", universals.G, celestial.mass, shipPhysics.node.getMass(), distance, gravity
            gravityForce = vector * -gravity

        thrust = universals.solarSystemRoot.getRelativeVector(shipPhysics.nodePath,
            (0, shipPhysics.currentThrust, 0))

        #force = (gravityForce + thrust) / 1000.0
        #print gravityForce, thrust / 1000.0
        #force = thrust / 1000.0
        force = thrust
        shipPhysics.node.applyCentralForce(force)
        shipPhysics.node.applyTorque(Vec3(0, 0, -shipPhysics.currentTorque))
        #shipPhysics.node.applyTorque(Vec3(0, 0, -1.3e+7))
        #print "beat", shipPhysics.nodePath.getHpr(), shipPhysics.node.getAngularVelocity()
        #print "Physics", shipPhysics.nodePath.getHpr(), shipPhysics.currentTorque, shipPhysics.node.getAngularVelocity()
        #print "Physics", shipPhysics.nodePath.getPos(), shipPhysics.node.getLinier
        #self.world.setDebugNode(shipPhysics.debugNode)

    def end(self):
        dt = globalClock.getDt()
        for zonex in worlds:
            for zoney in worlds[zonex]:
                worlds[zonex][zoney][0].doPhysics(dt)
        #self.world.doPhysics(dt, 10, 1.0 / 180.0)

    def setThrottle(self, shipid, data):
        if abs(data.normal) > 100 or abs(data.heading) > 100:
            print "Invalid"
            return
        ship = sandbox.entities[shipid]
        shipPhysics = ship.getComponent(shipComponents.BulletPhysicsComponent)
        shipThrust = ship.getComponent(shipComponents.ThrustComponent)
        shipPhysics.currentThrust = shipThrust.forward / (100.0 * 4) * data.normal
        # Divide thrust by 400 as max thrust should be when engineering overloads
        # Power to engines. Current max overload is 400%
        # TODO: Revisit caulculation when enginerring power is added
        # Power curve should be deminishing returns, bell curve function
        power = 1.0
        shipPhysics.currentTorque = shipThrust.heading * power * data.heading / 100.0
        #shipPhysics.currentTorque = 1.3e+7
        #shipPhysics.currentTorque = shipThrust.heading / (100.0 * 4) * data.heading
        #print "SetPhysics", shipPhysics.nodePath.getHpr(), shipPhysics.currentTorque, shipPhysics.node.getAngularVelocity()
        #print shipPhysics.nodePath.getPos(), shipPhysics.node.getLinearVelocity()
