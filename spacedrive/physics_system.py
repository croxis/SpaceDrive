from panda3d.core import NodePath, Point3, Vec3

import sandbox

import celestial_components as cel_comps
import physics_components as phys_comps
import universals

from direct.directnotify.DirectNotify import DirectNotify
log = DirectNotify().newCategory("SpaceDrive-Physics")


def get_physics():
    return sandbox.getSystem(PhysicsSystem)
'''notes:
76543.21 for a float cm precision
100,000 positive, and negative, so world size is 200,000 meters, or 200km'''


class FloatingPhysicsSystem(sandbox.EntitySystem):
    """Floating bullet worlds. Inspired by KSP and CCP physics system.

    Each ship is centered in a 100kmx100kmx100km bullet world.
    Bullet world origin has a soi relative pos. Ship true pos calculated from
    world origin true + relative position in world + soi position.

    If the ship enters a distance threshold in bullet world (say 25km) the
    heliocentric physics data is stored, old bullet world destroyed, new one
    created that matches current physics. Bullet worlds do not hpr, only pos.

    If the grid touches a ship in another grid, destroy and make a
    200x200x200km grid to hold all ships on grid. Grid position and velocity is
    average of all ships on new grid."""


class PhysicsSystem(sandbox.EntitySystem):
    """System that interacts with the Bullet physics world.
    Meshes are made in standard SI (meters, newtons, kg)."""
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
        soi = False
        previousR = 0
        for body in celestial_bodies:
            body_component = body.getComponent(cel_comps.CelestialComponent)
            distance = (body_component.true_pos
                - physcomp.get_true_pos()).length()
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
        vector = celestial_component.truePos - physcomp.get_true_pos()
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
