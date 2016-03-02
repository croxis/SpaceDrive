"""

RenderTarget

Copyright (c) 2015 tobspr <tobias.springer1@gmail.com>

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

from panda3d.core import GraphicsOutput, CardMaker, OmniBoundingVolume, Texture
from panda3d.core import AuxBitplaneAttrib, NodePath, OrthographicLens, Geom
from panda3d.core import Camera, Vec4, TransparencyAttrib, StencilAttrib
from panda3d.core import ColorWriteAttrib, DepthWriteAttrib, GeomVertexData
from panda3d.core import WindowProperties, FrameBufferProperties, GraphicsPipe
from panda3d.core import GeomVertexFormat, GeomNode, GeomVertexWriter
from panda3d.core import GeomTriangles, SamplerState, LVecBase2i, DepthTestAttrib
from panda3d.core import ShaderInput

try:
    from panda3d.core import PostProcessRegion
except ImportError:
    # Handled already by the render pipeline
    pass

from rplibs.six.moves import range
from rplibs.six import iterkeys, itervalues, iteritems

from rpcore.render_target import RenderTarget
from rpcore.gui.buffer_viewer import BufferViewer
from rpcore.globals import Globals
from rpcore.rpobject import RPObject

class setter(object):
    """ Setter only property """
    def __init__(self, func):
        self.__func = func
        self.__doc__ = func.__doc__

    def __set__(self, name, value):
        return self.__func(name, value)

class RenderTarget2(RPObject):

    """ Second version of the RenderTarget, IN DEVELOPMENT! The pipeline is
    slowly updated to use this version of the render target, when the process
    is done this will replace the first version. """

    _NUM_BUFFERS_ALLOCATED = 0

    def __init__(self, name="target"):
        RPObject.__init__(self, name)
        self._targets = {}
        self._color_bits = (0, 0, 0, 0)
        self._aux_bits = 8
        self._aux_count = 0
        self._depth_bits = 0
        self._size = LVecBase2i(-1, -1)
        self._source_window = Globals.base.win
        self._source_region = None
        self._active = False
        self._internal_buffer = None

        # Public attributes
        self.engine = Globals.base.graphicsEngine
        self.support_transparency = False
        self.use_oversized_triangle = True
        self.create_default_region = True

        # Disable all global clears, since they are not required
        for region in Globals.base.win.get_display_regions():
            region.disable_clears()

    #
    # METHODS TO SETUP
    #

    def add_color_attachment(self, bits=8, alpha=False):
        """ Adds a new color attachment with the given amount of bits, bits can
        be either a single int or a tuple determining the bits. If bits is a
        single int, alpha determines whether alpha bits are requested """
        self._targets["color"] = Texture(self.debug_name + "_color")
        if isinstance(bits, (list, tuple)):
            self._color_bits = (bits[0], bits[1], bits[2], bits[3] if len(bits) == 4 else 0)
        else:
            self._color_bits = ((bits, bits, bits, (bits if alpha else 0)))

    def add_depth_attachment(self, bits=32):
        """ Adds a depth attachment wit the given amount of bits """
        self._targets["depth"] = Texture(self.debug_name + "_depth")
        self._depth_bits = 32

    def add_aux_attachment(self, bits=8):
        """ Adds a new aux attachment with the given amount of bits. The amount
        of bits passed overrides all previous bits set, since all aux textures
        have to have the same amount of bits. """
        self._aux_bits = bits
        self._aux_count += 1

    def add_aux_attachments(self, bits=8, count=1):
        """ Adds n new aux attachments, with the given amount of bits. All
        previously set aux bits are overriden, since all aux textures have to
        have the same amount of bits """
        self._aux_bits = bits
        self._aux_count += count

    @setter
    def size(self, *args):
        """ Sets the render target size. This can be either a single integer,
        in which case it applies to both dimensions. Negative integers cause
        the render target to be proportional to the screen size, i.e. a value
        of -4 produces a quarter resolution target, a value of -2 a half
        resolution target, and a value of -1 a full resolution target
        (the default). """
        self._size = LVecBase2i(*args)

    #
    # METHODS TO QUERY AFTER SETUP
    #

    @property
    def active(self):
        """ Returns whether the target is currently active """
        return self._active

    @active.setter
    def active(self, flag):
        """ Sets whether the target is active, this just propagates the active
        flag to all display regions """
        if self._active is not flag:
            for region in self._internal_buffer.get_display_regions():
                region.set_active(flag)
            self._active = flag

    @property
    def color_tex(self):
        """ Returns the color attachment if present """
        return self._targets["color"]

    @property
    def depth_tex(self):
        """ Returns the depth attachment if present """
        return self._targets["depth"]

    @property
    def aux_tex(self):
        """ Returns a list of aux textures, can be used like target.aux_tex[2],
        notice the indices start at zero, so the first target has the index 0. """
        return [self._targets[i] for i in sorted(iterkeys(self._targets)) if i.startswith("aux_")]

    def set_shader_input(self, *args):
        """ Sets a shader input available to the target """
        if self.create_default_region:
            self._source_region.set_shader_input(ShaderInput(*args))

    @setter
    def shader(self, shader_obj):
        """ Sets a shader on the target """
        if not shader_obj:
            self.warn("shader must not be None!")
            return
        self._source_region.set_shader(shader_obj)

    @property
    def internal_buffer(self):
        """ Returns a handle to the internal GraphicsBuffer object """
        return self._internal_buffer

    @property
    def targets(self):
        """ Returns the dictionary of attachments, whereas the key is the name
        of the attachment and the value is the Texture handle of the attachment """
        return self._targets

    @property
    def region(self):
        """ Returns the internally used PostProcessRegion """
        return self._source_region

    def prepare_render(self, camera_np):
        """ Prepares to render a scene """
        self.create_default_region = False
        self._create_buffer()
        self._source_region = self._internal_buffer.get_display_region(0)

        if camera_np:
            initial_state = NodePath("rtis")
            initial_state.set_state(camera_np.node().get_initial_state())

            if self._aux_count:
                initial_state.set_attrib(AuxBitplaneAttrib.make(self._aux_bits), 20)
            initial_state.set_attrib(TransparencyAttrib.make(TransparencyAttrib.M_none), 20)

            if self._color_bits.count(0) == 4:
                initial_state.set_attrib(ColorWriteAttrib.make(ColorWriteAttrib.C_off), 20)

            # Disable existing regions of the camera
            for region in camera_np.node().get_display_regions():
                region.set_active(False)

            # Remove the existing display region of the camera
            for region in self._source_window.get_display_regions():
                if region.get_camera() == camera_np:
                    self._source_window.remove_display_region(region)

            camera_np.node().set_initial_state(initial_state.get_state())
            self._source_region.set_camera(camera_np)

        self._internal_buffer.disable_clears()
        self._source_region.disable_clears()
        self._source_region.set_active(True)
        self._source_region.set_sort(20)

        # Reenable depth-clear, usually desireable
        self._source_region.set_clear_depth_active(True)
        self._source_region.set_clear_depth(1.0)
        self._active = True

    def prepare_buffer(self):
        """ Prepares the target to render to an offscreen buffer """
        self._create_buffer()
        self._active = True

    def present_on_screen(self):
        """ Prepares the target to render on the main window, to present the
        final rendered image """
        self._source_region = PostProcessRegion.make(self._source_window)
        self._source_region.set_sort(5)

    def cleanup(self):
        """ Deletes this buffer, restoring the previous state """
        self._internal_buffer.clear_render_textures()
        self.engine.remove_window(self._internal_buffer)
        self._active = False

        for target in itervalues(self._targets):
            target.release_all()

    def set_clear_color(self, *args):
        """ Sets the  clear color """
        self._internal_buffer.set_clear_color_active(True)
        self._internal_buffer.set_clear_color(Vec4(*args))

    #
    # INTERNAL METHODS
    #


    def _create_buffer(self):
        """ Internal method to create the buffer object """
        win = self._source_window

        if self._size.x < 0:
            self._size.x = (win.get_x_size() - self._size.x - 1) // (-self._size.x)

        if self._size.y < 0:
            self._size.y = (win.get_y_size() - self._size.y - 1) // (-self._size.y)

        if not self._create():
            self.error("Failed to create buffer!")
            return False

        if self.create_default_region:
            self._source_region = PostProcessRegion.make(self._internal_buffer)

    def _setup_textures(self):
        """ Preparse all bound textures """
        for i in range(self._aux_count):
            self._targets["aux_{}".format(i)] = Texture(
                self.debug_name + "_aux{}".format(i))
        for name, tex in iteritems(self._targets):
            tex.set_wrap_u(SamplerState.WM_clamp)
            tex.set_wrap_v(SamplerState.WM_clamp)
            tex.set_anisotropic_degree(0)
            tex.set_x_size(self._size.x)
            tex.set_y_size(self._size.y)
            tex.set_minfilter(SamplerState.FT_linear)
            tex.set_magfilter(SamplerState.FT_linear)

    def _make_properties(self):
        """ Creates the window and buffer properties """
        window_props = WindowProperties.size(self._size.x, self._size.y)
        buffer_props = FrameBufferProperties()

        if self._color_bits == (16, 16, 16, 0):
            # Optional: Always use R11G11B10
            # buffer_props.set_rgba_bits(11, 11, 10, 0)
            buffer_props.set_rgba_bits(16, 16, 16, 0)
        elif self._color_bits == (8, 8, 8, 0):
            buffer_props.set_rgba_bits(11, 11, 10, 0)
        else:
            buffer_props.set_rgba_bits(*self._color_bits)

        buffer_props.set_accum_bits(0)
        buffer_props.set_stencil_bits(0)
        buffer_props.set_back_buffers(0)
        buffer_props.set_coverage_samples(0)
        buffer_props.set_depth_bits(self._depth_bits)
        buffer_props.set_float_depth(True)
        buffer_props.set_float_color(max(self._color_bits) > 8)
        buffer_props.set_force_hardware(True)
        buffer_props.set_multisamples(0)
        buffer_props.set_srgb_color(False)
        buffer_props.set_stereo(False)
        buffer_props.set_stencil_bits(0)

        if self._aux_bits == 8:
            buffer_props.set_aux_rgba(self._aux_count)
        elif self._aux_bits == 16:
            buffer_props.set_aux_hrgba(self._aux_count)
        elif self._aux_bits == 32:
            buffer_props.set_aux_float(self._aux_count)
        else:
            self.error("Invalid aux bits")

        return window_props, buffer_props

    def _create(self):
        """ Creates the internally used buffer """
        self._setup_textures()
        window_props, buffer_props = self._make_properties()

        self._internal_buffer = self.engine.make_output(
            self._source_window.get_pipe(), self.debug_name, 1,
            buffer_props, window_props, GraphicsPipe.BF_refuse_window,
            self._source_window.get_gsg(), self._source_window)

        if not self._internal_buffer:
            self.error("Failed to create buffer")
            return

        if self._depth_bits:
            self._internal_buffer.add_render_texture(
                self.depth_tex, GraphicsOutput.RTM_bind_or_copy,
                GraphicsOutput.RTP_depth)

        if self._color_bits.count(0) != 4:
            self._internal_buffer.add_render_texture(
                self.color_tex, GraphicsOutput.RTM_bind_or_copy,
                GraphicsOutput.RTP_color)

        aux_prefix = {
            8: "RTP_aux_rgba_{}",
            16: "RTP_aux_hrgba_{}",
            32: "RTP_aux_float_{}",
        }[self._aux_bits]

        for i in range(self._aux_count):
            target_mode = getattr(GraphicsOutput, aux_prefix.format(i))
            self._internal_buffer.add_render_texture(
                self.aux_tex[i], GraphicsOutput.RTM_bind_or_copy, target_mode)

        sort = -300 + RenderTarget._NUM_BUFFERS_ALLOCATED * 10
        RenderTarget._NUM_BUFFERS_ALLOCATED += 1
        self._internal_buffer.set_sort(sort)
        self._internal_buffer.disable_clears()
        self._internal_buffer.get_display_region(0).disable_clears()
        self._internal_buffer.get_overlay_display_region().disable_clears()
        self._internal_buffer.get_overlay_display_region().set_active(False)

        BufferViewer.register_entry(self)
        return True
