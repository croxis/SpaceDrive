from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from panda3d.core import Shader

import os, sys
sys.path.append('.')

from spacedrive.renderpipeline.Code.RenderingPipeline import RenderingPipeline
from panda3d.core import VirtualFileSystem, Vec3, loadPrcFile
from direct.showbase.ShowBase import ShowBase

loadPrcFile("configuration.prc")

base = ShowBase()

render_pipeline = RenderingPipeline(base)
render_pipeline.getMountManager().setBasePath('.')
render_pipeline.getMountManager().setWritePath("Temp/")
render_pipeline.loadSettings('pipeline.ini')
vfs = VirtualFileSystem.getGlobalPtr()
render_pipeline.create()

pos = 6371 + 20000
pos = 100

skybox = render_pipeline.getDefaultSkybox(scale=base.camLens.get_far()*0.8)
skybox.reparentTo(base.render)
print("Skybox scale:", base.camLens.get_far()*0.8)
skybox.reparent_to(base.render)

render_pipeline.scattering.adjustSetting("atmosphereOffset", Vec3(0, pos, 0))
render_pipeline.scattering.adjustSetting("atmosphereScale", Vec3(1))
#render_pipeline.scattering.adjustSetting("atmosphereScale", Vec3(1, 1, 20))

render_pipeline.onSceneInitialized()
base.run()

