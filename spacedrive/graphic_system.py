from __future__ import absolute_import
#from __future__ import division#Must wait
from __future__ import print_function
from __future__ import unicode_literals

from panda3d.core import Point3, Point3D, Vec3

import sandbox

from .celestial_components import CelestialComponent, StarComponent
from .render_components import CelestialRenderComponent


__author__ = 'croxis'


class GraphicsSystem(sandbox.EntitySystem):
    camera_entity = 0  # Entity camera is attached to for relative positioning
    current_pos = Point3D(0)
    sun_pos = Point3D(0)

    def begin(self):
        self.far_clip_plane = sandbox.base.camLens.get_far()
        self.scale_start_distance = self.far_clip_plane/2.0
        #entity = sandbox.entities[self.camera_entity]
        #entity.get_component()
        #self.current_pos = component.get_true_pos()
        # Get normalized sun direction. Expand to multiple suns later
        component = sandbox.get_components(StarComponent)[0]
        entity = sandbox.get_entity(component)
        celestial_component = entity.get_component(CelestialComponent)
        self.sun_pos = celestial_component.true_pos

    def process(self, entity):
        if entity.has_component(CelestialRenderComponent):
            render_component = entity.get_component(CelestialRenderComponent)
            celestial_component = entity.get_component(CelestialComponent)
            relative_pos = Point3D(celestial_component.true_pos - self.current_pos)
            debug = Point3D(relative_pos)
            debug.normalize()
            scale_factor = 1
            radius = celestial_component.radius
            if relative_pos.length() > self.scale_start_distance:
                #scale_factor = (1 / (0.5**self.scale_start_distance)) * (0.5)**difference.length()
                #scale_factor = (self.scale_start_distance / difference.length())
                #scale_factor = (1 / (0.999999**self.scale_start_distance)) * (0.999999)**difference.length()
                scale_factor = 1/1000.0
                relative_pos *= scale_factor
                radius *= scale_factor
                # Scale again if we are too far
                if relative_pos.length() > self.scale_start_distance:
                    scale_factor = 1*(0.9999999)**((relative_pos.length() - self.scale_start_distance))
                    relative_pos *= scale_factor
                    radius *= scale_factor
            screen_pos = Point3(relative_pos.get_x(), relative_pos.get_y(), relative_pos.get_z())
            render_component.mesh.set_pos(screen_pos)
            render_component.mesh.set_scale(radius)
            if render_component.light:
                #vector = self.current_pos - self.sun_pos
                vector = self.sun_pos - self.current_pos
                vector.normalize()
                vector *= self.scale_start_distance
                sun_vector = Vec3(vector.get_x(), vector.get_y(), vector.get_z())
                #render_component.light.setDirection(sun_vector)

            if render_component.atmosphere:
                offset = Vec3(screen_pos.get_x(), screen_pos.get_y(), screen_pos.get_z())
                render_component.atmosphere.adjustSetting("atmosphereOffset", offset)
                #sandbox.render_pipeline.lightingComputeContainer.setShaderInput('sunIntensity', 0.5)
                vector = self.sun_pos - celestial_component.true_pos
                vector.normalize()
                sun_vector = Vec3(vector.get_x(), vector.get_y(), vector.get_z())
                #print(sun_vector)
                #sandbox.render_pipeline.lightingComputeContainer.setShaderInput('sunVector', sun_vector)
                #render_component.atmosphere.adjustSetting("atmosphereScale", Vec3(1.3))
                #render_component.atmosphere.adjustSetting("atmosphereScale", Vec3(1/10.0))

        """if entity.has_component(solarSystem.PlanetRender):
            difference = self.getPos() - Globals.position
        if difference.length() < 10000:
            self.mesh.setPos(difference)
            self.mesh.setScale(self.radius)
            #if self.atmo:
            #    self.atmo.setScale(self.radius + 60)
        else:
            bodyPosition = difference/(difference.length()/10000) + difference/100000
            self.mesh.setPos(bodyPosition)
            scale = difference.length()/(10000 ) + difference.length()/100000
            self.mesh.setScale(self.radius/scale)
            #if self.atmo:
            #    self.atmo.setScale((self.radius+60)/scale)
        try:
            lightv = starlights[0].getPos()
            lightdir = lightv / lightv.length()
            self.atmo.setShaderInput("v3LightPos", lightdir[0], lightdir[1], lightdir[2])
        except:
            print "ummm"
        cameraPos = base.camera.getPos() - self.mesh.getPos()
        self.atmo.setShaderInput("v3CameraPos", cameraPos.getX(),
            cameraPos.getY(), cameraPos.getZ())
        cameraHeight = (base.camera.getPos()-self.mesh.getPos()).length()
        self.atmo.setShaderInput("fCameraHeight", cameraHeight)
        self.atmo.setShaderInput("fCameraHeight2", cameraHeight*cameraHeight)"""
