from __future__ import absolute_import
from __future__ import division#Must wait
from __future__ import print_function
from __future__ import unicode_literals

from panda3d.core import Point3D, Vec3

import sandbox

from .celestial_components import CelestialComponent
from .render_components import CelestialRenderComponent


__author__ = 'croxis'


class GraphicsSystem(sandbox.EntitySystem):
    camera_entity = 0  # Entity camera is attached to for relative positioning
    current_pos = Point3D(0)

    def begin(self):
        self.far_clip_plane = sandbox.base.camLens.get_far()
        self.scale_start_distance = self.far_clip_plane/2.0
        #entity = sandbox.entities[self.camera_entity]
        #entity.get_component()
        #self.current_pos = component.get_true_pos()

    def process(self, entity):
        if entity.has_component(CelestialRenderComponent):
            render_component = entity.get_component(CelestialRenderComponent)
            celestial_component = entity.get_component(CelestialComponent)
            difference = celestial_component.true_pos - self.current_pos
            new_pos = Point3D(difference)
            scale_factor = 1
            if difference.length() < self.scale_start_distance:
                render_component.mesh.set_pos(difference.get_x(), difference.get_y(), difference.get_z())
                render_component.mesh.set_scale(celestial_component.radius)
            else:
                scale_factor = 1*(0.999999)**((difference.length() - self.scale_start_distance))
                new_pos *= scale_factor
                render_component.mesh.set_pos(new_pos.get_x(), new_pos.get_y(), new_pos.get_z())
                render_component.mesh.set_scale(scale_factor * celestial_component.radius)
            if render_component.atmosphere:
                offset = Vec3(new_pos.get_x()/1000, new_pos.get_y()/1000, new_pos.get_z()/1000)
                print("Atmosphere", offset, scale_factor * celestial_component.radius)
                render_component.atmosphere.setSettings({
                    "atmosphereOffset": offset,
                    "atmosphereScale": Vec3(scale_factor * celestial_component.radius)
                })

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
