
from ..RenderStage import RenderStage


class AmbientStage(RenderStage):

    """ This stage computes the ambient term """

    required_inputs = ["mainCam", "mainRender", "DefaultEnvmap",
                       "cameraPosition", "PrefilteredBRDF"]
    required_pipes = ["ShadedScene", "GBuffer"]

    def __init__(self, pipeline):
        RenderStage.__init__(self, "AmbientStage", pipeline)

    def get_produced_pipes(self):
        return {"ShadedScene": self._target['color']}

    def create(self):
        self._target = self._create_target("AmbientStage")
        self._target.add_color_texture(bits=16)
        self._target.prepare_offscreen_buffer()

    def set_shaders(self):
        self._target.set_shader(
            self._load_shader("Stages/AmbientStage.frag"))

    def resize(self):
        RenderStage.resize(self)
        self.debug("Resizing pass")

    def cleanup(self):
        RenderStage.cleanup(self)
        self.debug("Cleanup pass")
