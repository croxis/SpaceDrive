import sandbox

from math import sin, cos, radians, degrees, sqrt, atan2
from panda3d.core import LPoint3d, NodePath
import yaml

import celestial_components as cel_comp
import render_components as render_comps
import surface_mesh
import universals

from direct.directnotify.DirectNotify import DirectNotify
log = DirectNotify().newCategory("SpaceDrive OrbitSystem")


class OrbitSystem(sandbox.EntitySystem):
    """Generates celestial bodies and moves them in orbit"""
    is2d = False
    solarsystemroots = {'center': NodePath("systemcenter")} #{'name': NodePath}
    #TODO: Further enhance to allow multiple star systems
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
        #Static bodies for now
        #universals.day += globalClock.getDt() / 86400 * universals.TIMEFACTOR
        component = entity.getComponent(cel_comp.CelestialComponent)
        if component.orbit:
            #print component.nodePath, self.get2DBodyPosition(component.nodePath, universals.day)
            #component.nodePath.setPos(self.get2DBodyPosition(component, universals.day))
            if self.is2d:
                component.truePos = self.get2DBodyPosition(component, universals.day)
            else:
                component.truePos = self.getBodyPosition(component, universals.day)
            #NOTE: truePos is only get position relative to the parent body. We need
            # to convert this to heliocentric
            # This only computes to the position of the parent body
            # We want to put moons into heliocentric coords as well
            # Iterate through parents and add their positions
            component.truePos += self.addParentPos(LPoint3d(0, 0, 0), component)
            #print component.nodePath, component.truePos

    def init(self, name='Sol', filename='solarsystem.yaml', is2d=False):
        self.is2d = is2d
        log.debug("Loading Solar System Bodies")
        stream = file(filename, "r")
        self.bodies = []
        solarDB = yaml.load(stream)
        stream.close()
        #self.sphere = shapeGenerator.Sphere(1, 128)
        #self.solarSystemRoot = NodePath(name)
        for bodyName, bodyDB in solarDB[name].items():
            self.generateNode(bodyName, bodyDB, self.solarsystemroots['center'])

    def generateNode(self, name, DB, parentNode):
        log.debug("Setting up " + name)
        bodyEntity = sandbox.createEntity()
        component = cel_comp.CelestialComponent()
        if DB['type'] == 'solid':
            body = cel_comp.Body(name)
        elif DB['type'] == 'moon':
            body = cel_comp.Body(name)
            body.kind = "moon"
        elif DB['type'] == 'star':
            body = cel_comp.Star(name)
            body.absoluteM = DB['absolute magnitude']
            body.spectral = DB['spectral']
        elif DB['type'] == 'barycenter':
            body = cel_comp.BaryCenter(name)

        component.kind = cel_comp.TYPES[DB['type']]

        if DB['type'] != "barycenter":
            component.mass = DB['mass']
            body.radius = DB['radius']
            body.rotation = DB['rotation']

        if 'orbit' in DB:
            component.orbit = DB['orbit']
            body.period = DB['period']
            #body.setPos(self.get2DBodyPosition(component, universals.day))
            component.truePos = self.get2DBodyPosition(component, universals.day)
            if name == "Earth":
                #universals.spawn = component.truePos + LPoint3d(0, 6671, 0)
                universals.spawn = component.truePos + LPoint3d(6671, 0, 0)

        if parentNode == universals.solarSystemRoot:
            universals.defaultSOIid = bodyEntity.id
            component.soi = 0
        elif DB['type'] != 'star' or DB['type'] != 'barycenter':
            component.soi = self.getSOI(component.mass, self.bodies[0].mass, component.orbit['a'])

        body.type = DB['type']
        body.reparentTo(parentNode)
        component.nodePath = body
        self.bodies.append(component)
        bodyEntity.addComponent(component)

        if universals.runClient and DB['type'] == 'star':
            component = render_comps.CelestialRenderComponent()
            component.mesh = surface_mesh.make_planet(name=name, scale=body.radius)
            component.mesh.reparentTo(sandbox.base.render)
            sandbox.send('makePickable', [component.mesh])
            #texture = sandbox.base.loader.loadTexture('planets/' + DB['texture'])
            #texture.setMinfilter(Texture.FTLinearMipmapLinear)
            #ts1 = TextureStage('textures1')
            #ts1.setMode(TextureStage.MGlow)
            #component.mesh.setTexture(ts1, texture)
            #component.mesh.setTexture(texture, 1)

            component.light = component.mesh.attachNewNode(PointLight("sunPointLight"))
            component.light.node().setColor(Vec4(1, 1, 1, 1))
            sandbox.base.render.setLight(component.light)
            bodyEntity.addComponent(component)

            '''#Shader test
            componentStar = graphicsComponents.StarRender()
            componentStar.noise_texture = Texture('noise')
            componentStar.noise_texture.setup2dTexture()
            img = PNMImage(1024, 1024)
            for y in range(1024):
                for x in range(1024):
                    img.setXel(x, y, componentStar.noise.noise(x, y))
                    #print componentStar.noise.noise(x, y)
            componentStar.noise_texture.load(img)
            #componentStar.noise_texture.write('test.png')
            #component.mesh.setTexture(componentStar.noise_texture, 1)

            texture = sandbox.base.loader.loadTexture('planets/' + DB['texture'])
            ts1 = TextureStage('textures1')
            ts1.setMode(TextureStage.MGlow)
            component.mesh.setTexture(ts1, componentStar.noise_texture)
            #component.mesh.setTexture(ts1, texture)

            component.mesh.setShaderInput('time', universals.get_day_in_seconds())
            shaders = Shader.load(Shader.SLGLSL, 'vortexVertex.glsl', 'starFrag.glsl')
            component.mesh.setShader(shaders)
            sandbox.send('makePickable', [component.mesh])'''


        if universals.runClient and (DB['type'] == 'solid' or DB['type'] == 'moon'):
            component = graphicsComponents.RenderComponent()
            #component.mesh = shapeGenerator.Sphere(body.radius, 128, name)
            #component.mesh = shapeGenerator.Sphere(body.radius, 64, name)
            component.mesh = surface_mesh.make_planet(name=name, scale=body.radius)
            #sandbox.send('makePickable', [component.mesh])
            sandbox.send('makePickable', [component.mesh.node_path])
            #component.mesh.setScale(body.radius)
            component.mesh.reparent_to(sandbox.base.render)
            # Doing world text
            text = TextNode('node name')
            text.setText(name)
            #textNodePath = component.mesh.attachNewNode(text)
            textNodePath = component.mesh.node_path.attachNewNode(text)
            textNodePath.setScale(0.07)

            component.mesh.set_textures(DB['texture'],
                night_path=DB['night'],
                gloss_path=DB['spec'])


            component.mesh.set_ambient(1, 1, 1, 1)
            component.mesh.set_diffuse(1, 1, 1, 1)
            component.mesh.set_specular(1, 1, 1, 1)
            component.mesh.set_shininess(100)

            '''if '#' in DB['texture']:
                component.mesh.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
                component.mesh.setTexProjector(TextureStage.getDefault(), sandbox.base.render, component.mesh)
                component.mesh.setTexScale(TextureStage.getDefault(), 1,  1, -1)
                component.mesh.setTexHpr(TextureStage.getDefault(), 90, -18, 90)
                #self.mesh.setHpr(0, 90, 0)
                texture = loader.loadCubeMap('planets/' + DB['texture'])
            else:
                texture = sandbox.base.loader.loadTexture('planets/' + DB['texture'])
            #texture.setMinfilter(Texture.FTLinearMipmapLinear)
            component.mesh.setTexture(texture, 1)'''
            '''if "atmosphere" in DB:
                component.atmosphere = shapeGenerator.Sphere(-1, 128)
                component.atmosphere.reparentTo(render)
                component.atmosphere.setScale(body.radius * 1.025)
                outerRadius = component.atmosphere.getScale().getX()
                scale = 1 / (outerRadius - component.body.getScale().getX())
                component.atmosphere.setShaderInput("fOuterRadius", outerRadius)
                component.atmosphere.setShaderInput("fInnerRadius", component.mesh.getScale().getX())
                component.atmosphere.setShaderInput("fOuterRadius2", outerRadius * outerRadius)
                component.atmosphere.setShaderInput("fInnerRadius2",
                    component.mesh.getScale().getX()
                    * component.mesh.getScale().getX())

                component.atmosphere.setShaderInput("fKr4PI",
                    0.000055 * 4 * 3.14159)
                component.atmosphere.setShaderInput("fKm4PI",
                    0.000015 * 4 * 3.14159)

                component.atmosphere.setShaderInput("fScale", scale)
                component.atmosphere.setShaderInput("fScaleDepth", 0.25)
                component.atmosphere.setShaderInput("fScaleOverScaleDepth", scale / 0.25)

                # Currently hard coded in shader
                component.atmosphere.setShaderInput("fSamples", 10.0)
                component.atmosphere.setShaderInput("nSamples", 10)
                # These do sunsets and sky colors
                # Brightness of sun
                ESun = 15
                # Reyleight Scattering (Main sky colors)
                component.atmosphere.setShaderInput("fKrESun", 0.000055 * ESun)
                # Mie Scattering -- Haze and sun halos
                component.atmosphere.setShaderInput("fKmESun", 0.000015 * ESun)
                # Color of sun
                component.atmosphere.setShaderInput("v3InvWavelength", 1.0 / math.pow(0.650, 4),
                                                  1.0 / math.pow(0.570, 4),
                                                  1.0 / math.pow(0.465, 4))
                #component.atmosphere.setShader(Shader.load("atmo.cg"))'''
            bodyEntity.addComponent(component)
        log.info(name + " set Up")
        if 'bodies' in DB:
            for bodyName, bodyDB in DB['bodies'].items():
                self.generateNode(bodyName, bodyDB, body)

    def getSOI(self, massPlanet, massSun, axis):
        '''Calculates the sphere of influence of a body for patch conic approximation'''
        return axis * (massPlanet / massSun) ** (2 / 5.0)

    """def getBodyComponents(self):
        '''Returns only planets and moons. Assumes single star starsystem'''
        bodies = []
        bodies += sandbox.getComponents(Body)
        return bodies

    def getBodyEntities(self):
        '''Returns only planets and moons. Assumes single star starsystem'''
        bodies = []
        bodies += sandbox.getEntitiesByComponentType(Body)
        return bodies"""