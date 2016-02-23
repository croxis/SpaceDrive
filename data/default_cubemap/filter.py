"""

RenderPipeline

Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>

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

from __future__ import print_function, division

import os
from panda3d.core import *
from direct.showbase.ShowBase import ShowBase

class Application(ShowBase):
    def __init__(self):
        load_prc_file_data("", """
            textures-power-2 none
            window-type offscreen
            win-size 100 100
            gl-coordinate-system default
            notify-level-display error
            print-pipe-types #f
        """)

        ShowBase.__init__(self)

        if not os.path.isdir("filtered/"):
            os.makedirs("filtered/")

        cubemap = self.loader.loadCubeMap("#.jpg")
        mipmap, size = -1, cubemap.get_y_size() * 2

        cshader = Shader.load_compute(Shader.SL_GLSL, "filter.compute.glsl")

        while size > 1:
            size = size // 2
            mipmap += 1
            print("Filtering mipmap", mipmap)

            dest_cubemap = Texture("Dest")
            dest_cubemap.setup_cube_map(size, Texture.T_float, Texture.F_rgba16)
            node = NodePath("")

            for i in range(6):
                node.set_shader(cshader)
                node.set_shader_input("SourceTex", cubemap)
                node.set_shader_input("DestTex", dest_cubemap)
                node.set_shader_input("currentSize", size)
                node.set_shader_input("currentMip", mipmap)
                node.set_shader_input("currentFace", i)
                attr = node.get_attrib(ShaderAttrib)
                self.graphicsEngine.dispatch_compute(
                    ( (size + 15) // 16, (size+15) // 16, 1), attr, self.win.get_gsg())

            print(" Extracting data ..")

            self.graphicsEngine.extract_texture_data(dest_cubemap, self.win.get_gsg())

            print(" Writing data ..")
            dest_cubemap.write("filtered/{}-#.png".format(mipmap), 0, 0, True, False)

Application()
