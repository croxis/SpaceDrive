"""

RenderPipeline

Copyright (c) 2014-2015 tobspr <tobias.springer1@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
 	 	    	 	
"""
from __future__ import division

from .. import *

from panda3d.core import PTAInt, Vec4


class SMAAStage(RenderStage):

    """ This stage does the actual SMAA """

    required_pipes = ["ShadedScene", "GBuffer"]
    required_inputs = []

    def __init__(self, pipeline):
        RenderStage.__init__(self, "SMAAStage", pipeline)
        self._area_tex = None
        self._search_tex = None
        self._reprojection = True
        self._jitter_index = PTAInt.empty_array(1)

    def set_use_reprojection(self, reproject):
        self._reprojection = reproject

    def set_area_tex(self, tex):
        self._area_tex = tex

    def set_search_tex(self, tex):
        self._search_tex = tex

    def set_jitter_index(self, idx):
        self._jitter_index[0] = idx

        self._neighbor_targets[0].set_active(idx == 0)
        self._neighbor_targets[1].set_active(idx == 1)

        self._resolve_target.set_shader_input("CurrentTex", self._neighbor_targets[idx]["color"])
        self._resolve_target.set_shader_input("LastTex", self._neighbor_targets[1-idx]["color"])

    def get_produced_pipes(self):

        if self._reprojection:
            out_target = self._resolve_target["color"]
        else:
            out_target = self._neighbor_targets[0]["color"]
        return {
            "ShadedScene": out_target
        }

    def create(self):

        # Scene conversion
        self._srgb_target = self._create_target("SMAA:TemporarySRGB")
        self._srgb_target.add_color_texture(bits=8)
        self._srgb_target.add_aux_texture(bits=8)
        self._srgb_target.prepare_offscreen_buffer()
        self._srgb_target.set_clear_color(color=Vec4(0))

        # Edge detection
        self._edge_target = self._create_target("SMAA:EdgeDetection")
        self._edge_target.add_color_texture(bits=16)
        self._edge_target.prepare_offscreen_buffer()
        self._edge_target.set_clear_color(color=Vec4(0))


        self._edge_target.set_shader_input("SRGBSource", self._srgb_target["color"])
        self._edge_target.set_shader_input("PredicationSource", self._srgb_target["aux0"])

        # Weight blending
        self._blend_target = self._create_target("SMAA:BlendWeights")
        self._blend_target.add_color_texture(bits=16)
        self._blend_target.prepare_offscreen_buffer()
        self._blend_target.set_clear_color(color=Vec4(0))

        self._blend_target.set_shader_input("EdgeTex", self._edge_target["color"])
        self._blend_target.set_shader_input("AreaTex", self._area_tex)
        self._blend_target.set_shader_input("SearchTex", self._search_tex)
        self._blend_target.set_shader_input("JitterIndex", self._jitter_index)


        # Neighbor blending
        self._neighbor_targets = []
        for i in range(2 if self._reprojection else 1):

            target = self._create_target("SMAA:Neighbor-" + str(i))
            target.add_color_texture(bits=16)
            target.prepare_offscreen_buffer()
            target.set_shader_input("BlendTex", self._blend_target["color"])
            target.set_shader_input("SRGBSource", self._srgb_target["color"])
            self._neighbor_targets.append(target)

        # Resolving
        if self._reprojection:
            self._resolve_target = self._create_target("SMAA:Resolve")
            self._resolve_target.add_color_texture(bits=16)
            self._resolve_target.prepare_offscreen_buffer()
            self._resolve_target.set_shader_input("JitterIndex", self._jitter_index)

    def set_shaders(self):
        self._srgb_target.set_shader(self.load_plugin_shader("TemporarySRGB.frag.glsl"))
        self._edge_target.set_shader(self.load_plugin_shader("EdgeDetection.frag.glsl"))
        self._blend_target.set_shader(self.load_plugin_shader("BlendingWeights.frag.glsl"))
        for target in self._neighbor_targets:
            target.set_shader(self.load_plugin_shader("NeighborhoodBlending.frag.glsl"))

        if self._reprojection:
            self._resolve_target.set_shader(self.load_plugin_shader("Resolve.frag.glsl"))

    def resize(self):
        RenderStage.resize(self)
        self.debug("Resizing pass")

    def cleanup(self):
        RenderStage.cleanup(self)
        self.debug("Cleanup pass")
