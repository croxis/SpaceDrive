# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sandbox

from math import sin, cos, radians, degrees, sqrt, atan2
from panda3d.core import LPoint3d, Vec3
import yaml

from .import celestial_components as cel_comp
from .import render_components as render_comps
from .import surface_mesh
from .import universals
from .utils import blackbody

from .renderpipeline import DirectionalLight
from .renderpipeline import Scattering

from direct.directnotify.DirectNotify import DirectNotify

log = DirectNotify().newCategory("SpaceDrive-OrbitSystem")
log.setSeverity(3)

is2d = False


class OrbitSystem(sandbox.EntitySystem):
    """Positions and moves celestial bodies in orbit."""
    def add_parent_pos(self, displacement, child_component):
        parent_node_path = child_component.node_path.get_parent()
        parent_entity = parent_node_path.get_python_tag('entity')
        if parent_entity:
            parent_component = parent_entity.get_component(cel_comp.CelestialComponent)
            if parent_component:
                displacement += self.add_parent_pos(displacement, parent_component)
                displacement += parent_component.true_pos
        return displacement

    def process(self, entity):
        """Gets the xyz position of the body, relative to its parent, on the
        given day before/after the date of element. Units will be in AU."""
        # Static bodies for now
        # Also clock should not be here. Put in another system.
        # universals.day += globalClock.getDt() / 86400 * universals.TIMEFACTOR
        component = entity.get_component(cel_comp.CelestialComponent)
        if component.orbit:
            # print component.nodePath, self.get2DBodyPosition(component.nodePath, universals.day)
            # component.nodePath.setPos(self.get2DBodyPosition(component, universals.day))
            component.true_pos = calc_body_pos(component, universals.day)
            # NOTE: truePos is only get position relative to the parent body. We need
            # to convert this to heliocentric
            # This only computes to the position of the parent body
            # We want to put moons into heliocentric coords as well
            # Iterate through parents and add their positions
            #TODO: Do we really need to do this? If not this should be moved
            #to the end step function to prevent celestial motion jitters
            #as we have no guarantee of order
            component.true_pos += self.add_parent_pos(LPoint3d(0, 0, 0),
                                                      component)


def create_from_yaml_file(self, filename):
    with open(filename) as f:
        data = f.read()
    if data:
        solardb = yaml.load(data)
        for system_name, db in solardb.iteritems():
            create_solar_system(name=system_name, database=db)
    else:
        log.warning("No yaml file with that name")


def create_solar_system(name='Sol', database={}):
    log.info("Generating solarsystem: " + name)
    entity = sandbox.create_entity()
    component = cel_comp.SolarSystemComponent(name)
    entity.add_component(component)
    for bodyName, bodyDB in database[name].items():
        generate_node(bodyName, bodyDB, component)


def generate_node(name, database, parent_component):
    log.info("Setting up body: " + name)
    log.debug("Raw data: " + str(database))
    body_entity = sandbox.create_entity()
    celestial_component = cel_comp.CelestialComponent(name,
                                                      sandbox.get_entity(
                                                          parent_component),
                                                      kind=database['type'])
    components = [celestial_component]
    if database['type'] == 'star':
        star_component = cel_comp.StarComponent(
            database['absolute magnitude'], database['spectral'],
            temperature=database['temperature'])
        components.append(star_component)
    if 'orbit' in database:
        celestial_component.orbit = database['orbit']
        celestial_component.period = database['period']
        celestial_component.true_pos = calc_body_pos(celestial_component,
                                                     universals.day)
    if database['type'] != 'barycenter':
        celestial_component.mass = database['mass']
        celestial_component.radius = database['radius']
        celestial_component.rotation = database['rotation']
        if not isinstance(parent_component, cel_comp.SolarSystemComponent):
            celestial_component.soi = calculate_soi(
                celestial_component.orbit['a'],
                celestial_component.mass,
                parent_component.mass)

            # if name == "Earth":
            # #universals.spawn = component.truePos + LPoint3d(0, 6671000, 0)
            # universals.spawn = component.truePos + LPoint3d(6671000, 0, 0)
    if isinstance(parent_component, cel_comp.SolarSystemComponent):
        celestial_component.node_path.reparent_to(parent_component.root_node)
    else:
        celestial_component.node_path.reparent_to(parent_component.node_path)
    celestial_component.node_path.set_python_tag('entity', body_entity)


    #FIXME: Does not factor parent positions for nested objects.
    if celestial_component.orbit:
        true_pos = calc_body_pos(celestial_component, universals.day)
        celestial_component.true_pos = true_pos

    if universals.run_client:
        render_component = render_comps.CelestialRenderComponent()
        components.append(render_component)

        #For porting to new render system only
        if database['type'] != 'star':
            render_component.mesh = surface_mesh.make_planet(name=name)
            '''render_component.mesh = surface_mesh.make_planet(name=name,
                                                         scale=celestial_component.radius)'''
            if 'atmosphere' in database:
                render_component.atmosphere = Scattering()
                render_component.atmosphere.setSettings({
                    'radiusGround': database['radius']/1000 + 1.0,
                    'radiusAtmosphere': database['radius']/1000 + 150.0,
                })
                render_component.atmosphere.precompute()
                render_component.atmosphere.bindTo(sandbox.base.render_pipeline.lightingComputeContainer, "scatteringOptions")
                sandbox.base.render_pipeline.lightingComputeContainer.setShaderInput(
                    "transmittanceSampler", render_component.atmosphere.getTransmittanceResult())
                sandbox.base.render_pipeline.lightingComputeContainer.setShaderInput(
                    "inscatterSampler", render_component.atmosphere.getInscatterTexture())

        #sandbox.send('make pickable', [render_component.mesh])
        if database['type'] == 'star':
            color = blackbody.convert_K_to_RGB_float(database['temperature'])
            render_component.mesh = surface_mesh.make_star(name=name, color=color)
            #Debug prototype purposes only
            render_component.mesh.set_pos(0, 0, 0)
            #/Debug
            render_component.temperature = database['temperature']
            render_component.light = DirectionalLight()
            render_component.light.setAmbientColor(Vec3(0))
            render_component.light.setColor(Vec3(color))
            render_component.light.setDirection(render_component.mesh.get_pos())
            render_component.light.setShadowMapResolution(1024)
            render_component.light.setCastsShadows(True)
            sandbox.base.render_pipeline.addLight(render_component.light)

        elif database['type'] == 'solid' or database['type'] == 'moon':
            render_component.mesh.set_textures(database['textures'])
            #render_component.mesh.set_ambient(1, 1, 1, 1)
            #render_component.mesh.set_diffuse(1, 1, 1, 1)
            #render_component.mesh.set_specular(1, 1, 1, 1)
            #render_component.mesh.set_shininess(100)
        render_component.mesh.reparent_to(sandbox.base.render)

    for component in components:
        body_entity.add_component(component)

    if 'bodies' in database:
        for body_name, body_database in database['bodies'].items():
            generate_node(body_name, body_database, celestial_component)


def calculate_soi(semimajor_axis, mass_body, mass_parent):
    """Calculates the sphere of influence of a body for patch conic
    approximation."""
    return semimajor_axis * (mass_body / mass_parent) ** (2 / 5.0)


def calc_body_pos(component, time):
    """Returns celestial position relative to the parent."""
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
        E = compute_e(E, M, e)
    # http://stjarnhimlen.se/comp/tutorial.html
    # Compute distance and true anomaly
    xv = a * (cos(E) - e)
    yv = a * (sqrt(1.0 - e * e) * sin(E))
    v = atan2(yv, xv)
    r = sqrt(xv * xv + yv * yv)
    xh = r * (cos(N) * cos(v + w) - sin(N) * sin(v + w) * cos(i))
    yh = r * (sin(N) * cos(v + w) + cos(N) * sin(v + w) * cos(i))
    if is2d:
        zh = 0
    else:
        zh = r * (sin(v + w) * sin(i))
    '''The above assumes looking "down" on the solar system where x and y are
    the circle and z = 0 is on the heliocentric ecliptic. Panda3d uses the above.
    Opengl is y up and z depth so we switch the y and z coordinates below..'''
    #TODO: z+ is out of the screen so check if we need to flip the sign of zh
    '''xh = r * (cos(N) * cos(v + w) - sin(N) * sin(v + w) * cos(i))
    zh = r * (sin(N) * cos(v + w) + cos(N) * sin(v + w) * cos(i))
    if is2d:
        yh = 0
    else:
        yh = r * (sin(v + w) * sin(i))'''
    position = LPoint3d(xh, yh, zh)
    # If we are not a moon then our orbits are done in au.
    # Moons are done in km
    # Our units in panda are m, so we convert to m
    if component.kind != cel_comp.TYPES['moon']:
        position *= 149598000
    position *= 1000
    return position


def compute_e(E0, M, e):
    """Iterative function for a higher accuracy of E."""
    E1 = E0 - (E0 - e * sin(E0) - M) / (1 - e * cos(E0))
    if abs(abs(degrees(E1)) - abs(degrees(E0))) > 0.001:
        E1 = compute_e(E1, M, e)
    return E1