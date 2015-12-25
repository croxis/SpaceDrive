
from functools import partial

from panda3d.core import Vec3, Vec2, RenderState, TransformState
from direct.gui.DirectFrame import DirectFrame
from direct.interval.IntervalGlobal import Parallel, Sequence

from .BetterOnscreenImage import BetterOnscreenImage
from .BufferViewer import BufferViewer
from .PipeViewer import PipeViewer
from .BetterOnscreenText import BetterOnscreenText
from .BetterLabeledCheckbox import BetterLabeledCheckbox
from .CheckboxCollection import CheckboxCollection
from .FastText import FastText
from .ErrorMessageDisplay import ErrorMessageDisplay
from .ExposureWidget import ExposureWidget

from ..Util.DebugObject import DebugObject
from ..Globals import Globals
from ..BaseManager import BaseManager

class OnscreenDebugger(BaseManager):

    """ This class manages the onscreen gui """

    def __init__(self, pipeline):
        BaseManager.__init__(self)
        self.debug("Creating debugger")
        self._pipeline = pipeline

        self._fullscreen_node = Globals.base.pixel2d.attach_new_node(
            "PipelineDebugger")
        self._create_components()
        self._init_keybindings()
        self._init_notify()

    def _create_components(self):
        """ Creates the gui components """

        # When using small resolutions, scale the GUI so its still useable,
        # otherwise the sub-windows are bigger than the main window
        scale_factor = min(1.0, Globals.base.win.get_x_size() / 1800.0)
        self._fullscreen_node.set_scale(scale_factor)

        # Component values
        self._debugger_width = 460

        # Create states
        self._debugger_visible = False

        # Create intervals
        self._debugger_interval = None

        # Create the actual GUI
        self._create_debugger()
        self._create_topbar()
        self._create_stats()
        self._buffer_viewer = BufferViewer(self._pipeline, self._fullscreen_node)
        self._pipe_viewer = PipeViewer(self._pipeline, self._fullscreen_node)

        self._exposure_node = self._fullscreen_node.attach_new_node("ExposureWidget")
        self._exposure_node.set_pos(Globals.base.win.get_x_size() - 200, 1, -Globals.base.win.get_y_size() + 120)
        self._exposure_widget = ExposureWidget(self._pipeline, self._exposure_node)

    def _init_notify(self):
        """ Inits the notify stream which gets all output from panda and parses
        it """
        self._error_msg_handler = ErrorMessageDisplay()

    def do_update(self):
        """ Updates the gui """
        self._update_stats()
        self._error_msg_handler.update()

    def get_error_msg_handler(self):
        """ Returns the error message handler """
        return self._error_msg_handler

    def _create_topbar(self):
        """ Creates the topbar """
        self._pipeline_logo = BetterOnscreenImage(
            image="Data/GUI/OnscreenDebugger/PipelineLogo.png", x=30, y=30,
            parent=self._fullscreen_node)
        self._pipeline_logo_text = BetterOnscreenImage(
            image="Data/GUI/OnscreenDebugger/PipelineLogoText.png", x=124,
            y=55, parent=self._fullscreen_node)
        self._topbar = DirectFrame(parent=self._fullscreen_node,
                                   frameSize=(5000, 0, 0, -22),
                                   pos=(0, 0, 0),
                                   frameColor=(0.058, 0.058, 0.058, 1))
        # Hide the logo text in the beginning
        self._pipeline_logo_text.set_pos(150, -150)
        self._topbar.hide()

    def _create_stats(self):
        """ Creates the stats overlay """

        self._overlay_node = Globals.base.aspect2d.attach_new_node("Overlay")
        self._overlay_node.set_pos(Globals.base.getAspectRatio() - 0.07, 1, 1.0 - 0.07)

        self._debug_lines = []

        for i in range(2):
            self._debug_lines.append(FastText(
                pos=Vec2(0, -i * 0.05), parent=self._overlay_node, pixel_size=18,
                align="right"))

    def _update_stats(self):
        """ Updates the stats overlay """

        clock = Globals.clock
        self._debug_lines[0].set_text("{:3.0f} fps  |  {:3.1f} ms  |  {:3.1f} ms max".format(
            clock.get_average_frame_rate(),
            1000.0 / max(0.001, clock.get_average_frame_rate()),
            clock.get_max_frame_duration() * 1000.0))

        text = "{:4d} render states  |  {:4d} transform states"
        text += "  |  {:4d} commands  |  {:6d} lights"
        self._debug_lines[1].set_text(text.format(
            RenderState.get_num_states(), TransformState.get_num_states(),
            self._pipeline.get_light_mgr().get_cmd_queue().get_num_queued_commands(),
            self._pipeline.get_light_mgr().get_num_lights()))

        for line in self._debug_lines:
            line.update()

    def _create_debugger(self):
        """ Creates the debugger contents """

        debugger_opacity = 1.0

        self._debugger_node = self._fullscreen_node.attach_new_node("DebuggerNode")
        self._debugger_node.set_x(-self._debugger_width)
        self._debugger_bg = DirectFrame(
            parent=self._debugger_node, frameSize=(self._debugger_width, 0, -127, -2000),
            pos=(0, 0, 0), frameColor=(0.09, 0.09, 0.09, debugger_opacity))
        self._debugger_bg_bottom = DirectFrame(
            parent=self._fullscreen_node, frameSize=(self._debugger_width, 0, 0, -1),
            pos=(0, 0, 1), frameColor=(0.09, 0.09, 0.09, 1*debugger_opacity))
        self._debugger_divider = DirectFrame(
            parent=self._debugger_node, frameSize=(self._debugger_width, 0, 0, -3),
            pos=(0, 0, -125), frameColor=(0.09, 0.09, 0.09, 1*debugger_opacity))

        self._create_debugger_content()

        self._hint_reloading = BetterOnscreenImage(
            image="Data/GUI/OnscreenDebugger/ShaderReloadHint.png",
            x=80, y=Globals.base.win.get_y_size() - 100,
            parent=Globals.base.pixel2d)
        self.set_reload_hint_visible(False)

    def set_reload_hint_visible(self, flag):
        """ Sets whether the shader reload hint is visible """
        if flag:
            self._hint_reloading.show()
        else:
            self._hint_reloading.hide()

    def _create_debugger_content(self):
        """ Internal method to create the content of the debugger """

        debugger_content = self._debugger_node.attach_new_node("DebuggerContent")
        debugger_content.set_z(-190)
        debugger_content.set_x(40)
        heading_color = Vec3(0.7, 0.7, 0.24) * 1.2
        BetterOnscreenText(
            parent=debugger_content, text="Render Mode:".upper(), x=0, y=0, size=20,
            color=heading_color)

        render_modes = [
            ("Default", ""),
            ("Diffuse", "DIFFUSE"),
            ("Roughness", "ROUGHNESS"),
            ("Specular", "SPECULAR"),
            ("Normal", "NORMAL"),
            ("Metallic", "METALLIC"),
            ("Translucency", "TRANSLUCENCY"),
            # ("Velocity", "VELOCITY")
            # "Lighting",
            # "Scattering",
            # "GI-Diffuse",
            # "GI-Specular",
            ("PSSM Splits", "PSSM_SPLITS"),
            ("Ambient Occlusion", "OCCLUSION"),
            # "PSSM-Splits",
            # "Shadowing",
            # "Bloom"
        ]

        row_width = 200
        collection = CheckboxCollection()

        for idx, (mode, mode_id) in enumerate(render_modes):
            offs_y = (idx // 2) * 37 + 40
            offs_x = (idx % 2) * row_width
            box = BetterLabeledCheckbox(
                parent=debugger_content, x=offs_x, y=offs_y, text=mode.upper(),
                text_color=Vec3(0.9), radio=True, chb_checked=(mode == "Default"),
                chb_callback=partial(self._set_render_mode, mode_id),
                text_size=16, expand_width=160)
            collection.add(box.get_checkbox())

    def _set_render_mode(self, mode_id, value):
        """ Callback which gets called when a render mode got selected """
        if not value:
            return

        # Clear old defines
        self._pipeline.get_stage_mgr().remove_define_if(lambda name: name.startswith("_RM__"))

        if mode_id == "":
            self._pipeline.get_stage_mgr().define("ANY_DEBUG_MODE", 0)
        else:
            self._pipeline.get_stage_mgr().define("ANY_DEBUG_MODE", 1)
            self._pipeline.get_stage_mgr().define("_RM__" + mode_id, 1)

        # Reload all shaders
        self._pipeline.reload_shaders()

    def _init_keybindings(self):
        """ Inits the debugger keybindings """
        Globals.base.accept("g", self._toggle_debugger)
        Globals.base.accept("v", self._buffer_viewer.toggle)
        Globals.base.accept("c", self._pipe_viewer.toggle)
        Globals.base.accept("f5", self._toggle_gui_visible)

    def _toggle_gui_visible(self):
        """ Shows / Hides the gui """
        if not Globals.base.pixel2d.is_hidden():
            Globals.base.pixel2d.hide()
            Globals.base.aspect2d.hide()
            Globals.base.render2d.hide()
        else:
            Globals.base.pixel2d.show()
            Globals.base.aspect2d.show()
            Globals.base.render2d.show()
        
    def _toggle_debugger(self):
        """ Internal method to hide or show the debugger """
        if self._debugger_interval is not None:
            self._debugger_interval.finish()

        if self._debugger_visible:
            # Hide Debugger
            self._debugger_interval = Sequence(
                Parallel(
                    self._debugger_node.posInterval(
                        0.12, Vec3(-self._debugger_width, 0, 0),
                        Vec3(0, 0, 0), blendType="easeInOut"),
                    self._pipeline_logo_text.pos_interval(
                        0.16,
                        self._pipeline_logo_text.get_initial_pos() + Vec3(0, 0, 150),
                        self._pipeline_logo_text.get_initial_pos, blendType="easeInOut"),
                    self._pipeline_logo.hpr_interval(
                        0.12, Vec3(0, 0, 0), Vec3(0, 0, 90), blendType="easeInOut"),
                    self._debugger_bg_bottom.scaleInterval(
                        0.12, Vec3(1, 1, 1), Vec3(1, 1, 126), blendType="easeInOut")
                ))
        else:
            # Show debugger
            self._debugger_interval = Sequence(
                Parallel(
                    self._pipeline_logo.hpr_interval(
                        0.12, Vec3(0, 0, 90), Vec3(0, 0, 0), blendType="easeInOut"),
                    self._pipeline_logo_text.pos_interval(
                        0.12, self._pipeline_logo_text.get_initial_pos(),
                        self._pipeline_logo_text.get_initial_pos() + Vec3(0, 0, 150),
                        blendType="easeInOut"),
                    self._debugger_node.posInterval(
                        0.12, Vec3(0, 0, 0), Vec3(-self._debugger_width, 0),
                        blendType="easeInOut"),
                    self._debugger_bg_bottom.scaleInterval(
                        0.12, Vec3(1, 1, 126), Vec3(1, 1, 1), blendType="easeInOut")
                ))
        self._debugger_interval.start()
        self._debugger_visible = not self._debugger_visible
