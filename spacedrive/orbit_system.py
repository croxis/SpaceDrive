# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sandbox

from math import sin, cos, radians, degrees, sqrt, atan2
from panda3d.core import LPoint3d, NodePath, PointLight, Vec4
import yaml

from .import celestial_components as cel_comp
from .import render_components as render_comps
from .import surface_mesh
from .import universals

from direct.directnotify.DirectNotify import DirectNotify

log = DirectNotify().newCategory("SpaceDrive OrbitSystem")


def calculate_soi(semimajor_axis, mass_body, mass_parent):
    """Calculates the sphere of influence of a body for patch conic
    approximation."""
    return semimajor_axis * (mass_body / mass_parent) ** (2 / 5.0)


class SolarSystem(sandbox.EntitySystem):
    """Create and manages solar system graph and their celestial bodies."""
    is2d = False

    def init(self, is2d=False):
        self.is2d = is2d

    def create_from_yaml_file(self, filename, is2d=False):
        with open(filename) as f:
            data = f.read()
        if data:
            solarDB = yaml.load(data)
            for system_name, db in solarDB.iteritems():
                self.create_solar_system(name=system_name, db)
        else:
            log.warning("No yaml file with that name")

    def create_solar_system(self, name='Sol', database={}, is2d=False):
        log.info("Generating solarsystem: " + name)
        entity = sandbox.create_entity()
        component = cel_comp.SolarSystemComponent()
        entity.add_component(component)
        for bodyName, bodyDB in database[name].items():
            self.generate_node(bodyName, bodyDB, component)

    def generate_node(self, name, database, parent_component):
        log.debug("Setting up body: " + name)
        body_entity = sandbox.create_entity()
        celestial_component = cel_comp.CelestialComponent(
            kind=database['type'])
        components = [celestial_component]
        if database['type'] == 'star':
            star_component = cel_comp.StarComponent(
                database['absolute magnitude'], database['spectral'])
            components.append(star_component)
        if database['type'] != 'barycenter':
            celestial_component.mass = database['mass']
            celestial_component.radius = database['radius']
            celestial_component.rotation = database['rotation']
            if parent_component:
                celestial_component.soi = calculate_soi(
                    celestial_component.orbit['a'],
                    celestial_component.mass,
                    parent_component.mass)
        if 'orbit' in database:
            celestial_component.orbit = database['orbit']
            celestial_component.period = database['period']
            # component.truePos = self.get2DBodyPosition(component, universals.day)
            # if name == "Earth":
            # #universals.spawn = component.truePos + LPoint3d(0, 6671000, 0)
            # universals.spawn = component.truePos + LPoint3d(6671000, 0, 0)
        if isinstance(parent_component, cel_comp.SolarSystemComponent):
            celestial_component.node_path.reparent_to(parent_component.root_node)
        else:
            celestial_component.node_path.reparent_to(parent_component.node_path)

        if universals.run_client:
            render_component = render_comps.CelestialRenderComponent()
            components.append(render_component)
            render_component.mesh = surface_mesh.make_planet(name=name, scale=celestial_component.radius)
            render_component.mesh.reparent_to(sandbox.base.render)
            sandbox.send('make pickable', [render_component.mesh])
            if database['type'] == 'star':
                render_component.light = render_component.mesh.attach_new_node(
                    PointLight("sunPointLight")
                )
                render_component.light.node().set_color(Vec4(1, 1, 1, 1))
                sandbox.base.render.set_light(render_component.light)
            elif database['type'] == 'solid' or database['type'] == 'moon':
                render_component.mesh.set_textures(database['texture'],
                                                   night_path=database['night'],
                                                   gloss_path=database['Spec'])
                render_component.mesh.set_ambient(1, 1, 1, 1)
                render_component.mesh.set_diffuse(1, 1, 1, 1)
                render_component.mesh.set_specular(1, 1, 1, 1)
                render_component.mesh.set_shininess(100)

        for component in components:
            body_entity.add_component(component)

        if 'bodies' in database:
            for body_name, body_database in database['bodies'].items():
                self.generate_node(body_name, body_database, celestial_component)


class OrbitSystem(sandbox.EntitySystem):
    """Positions and moves celestial bodies in orbit."""
    is2d = False

    def init(self, is2d=False):
        self.is2d = is2d

    def getBodyPosition(self, entity, time):
        """Returns celestial position relative to the parent"""
        # Convert to radians
        M = radians(eval(entity.orbit['M'])(time))
        w = radians(eval(entity.orbit['w'])(time))
        i = radians(eval(entity.orbit['i'])(time))
        N = radians(eval(entity.orbit['N'])(time))
        a = entity.orbit['a']
        e = eval(entity.orbit['e'])(time)
        # Compute eccentric anomaly
        E = M + e * sin(M) * (1.0 + e * cos(M))
        if degrees(E) > 0.05:
            E = self.computeE(E, M, e)
        # http://stjarnhimlen.se/comp/tutorial.html
        # Compute distance and true anomaly
        xv = a * (cos(E) - e)
        yv = a * (sqrt(1.0 - e * e) * sin(E))
        v = atan2(yv, xv)
        r = sqrt(xv * xv + yv * yv)
        xh = r * (cos(N) * cos(v + w) - sin(N) * sin(v + w) * cos(i))
        yh = r * (sin(N) * cos(v + w) + cos(N) * sin(v + w) * cos(i))
        zh = r * (sin(v + w) * sin(i))
        position = LPoint3d(xh, yh, zh)
        # If we are not a moon then our orbits are done in au.
        # Our units in panda are km, so we convert to km
        if entity.kind != cel_comp.TYPES['moon']:
            position = position * 149598000
        return position

    def get2DBodyPosition(self, component, time):
        """Returns celestial position relative to the parent"""
        # Convert to radians
        M = radians(eval(component.orbit['M'])(time))
        w = radians(eval(component.orbit['w'])(time))
        i = radians(eval(component.orbit['i'])(time))
        N = radians(eval(component.orbit['N'])(time))
        a = component.orbit['a']
        e = eval(component.orbit['e'])(time)
        # Compute eccentric anomaly
        E = M + e * sin(M) * (1.0 + e * cos(M))
        if degrees(E) > 0.05:
            E = self.computeE(E, M, e)
        # Compute distance and true anomaly
        xv = a * (cos(E) - e)
        yv = a * (sqrt(1.0 - e * e) * sin(E))
        v = atan2(yv, xv)
        r = sqrt(xv * xv + yv * yv)
        xh = r * (cos(N) * cos(v + w) - sin(N) * sin(v + w) * cos(i))
        yh = r * (sin(N) * cos(v + w) + cos(N) * sin(v + w) * cos(i))
        position = LPoint3d(xh, yh, 0)
        # If we are not a moon then our orbits are done in au.
        # We need to convert to km
        if component.kind != cel_comp.TYPES['moon']:
            position = position * 149598000
        return position

    def computeE(self, E0, M, e):
        '''Iterative function for a higher accuracy of E'''
        E1 = E0 - (E0 - e * sin(E0) - M) / (1 - e * cos(E0))
        if abs(abs(degrees(E1)) - abs(degrees(E0))) > 0.001:
            E1 = self.computeE(E1, M, e)
        return E1

    def addParentPos(self, displacement, childComponent):
        for component in sandbox.getComponents(cel_comp.CelestialComponent):
            if component.nodePath == childComponent.nodePath.getParent():
                if component.nodePath in self.solarsystemroots.values():
                    pass
                else:
                    displacement += self.addParentPos(displacement, component)
                    displacement += component.truePos
        return displacement

    def process(self, entity):
        '''Gets the xyz position of the body, relative to its parent, on the given day before/after the date of element. Units will be in AU'''
        # Static bodies for now
        # universals.day += globalClock.getDt() / 86400 * universals.TIMEFACTOR
        component = entity.getComponent(cel_comp.CelestialComponent)
        if component.orbit:
            # print component.nodePath, self.get2DBodyPosition(component.nodePath, universals.day)
            #component.nodePath.setPos(self.get2DBodyPosition(component, universals.day))
            if self.is2d:
                component.truePos = self.get2DBodyPosition(component,
                                                           universals.day)
            else:
                component.truePos = self.getBodyPosition(component,
                                                         universals.day)
            #NOTE: truePos is only get position relative to the parent body. We need
            # to convert this to heliocentric
            # This only computes to the position of the parent body
            # We want to put moons into heliocentric coords as well
            # Iterate through parents and add their positions
            component.truePos += self.addParentPos(LPoint3d(0, 0, 0),
                                                   component)
            #print component.nodePath, component.truePos