
from panda3d.core import Texture, ShaderAttrib, NodePath, Shader
from Globals import Globals

class TextureCleaner:

    """ This class is a simple interface to completely clear a
    texture to a given color. It internally uses compute shaders """

    @classmethod
    def _createClearShader(self):
        """ Internal method to create the compute shader which will
        clear the texture """

        shader = """
        #version 430

        layout (local_size_x = 16, local_size_y = 16) in;

        uniform int layers;
        uniform writeonly image2D destination;
        uniform vec4 clearColor;
        
        void main() {
            ivec2 coord = ivec2(gl_GlobalInvocationID.xy);
            imageStore(destination, coord, clearColor);
        }
        """
        return Shader.makeCompute(Shader.SLGLSL, shader)

    @classmethod
    def clearTexture(self, tex, clearColor):
        """ Clears a texture object """
        if tex.getZSize() > 1:
            print "TextureCleaner: 3D Textures not supported (yet!)"
            return
        else:
            w, h, d = tex.getXSize(), tex.getYSize(), tex.getZSize()
            dispatchW = (w + 15) / 16
            dispatchH = (h + 15) / 16
            shader = self._createClearShader()
            dummy = NodePath("dummy")
            dummy.setShader(shader)
            dummy.setShaderInput("layers", d)
            dummy.setShaderInput("destination", tex)
            dummy.setShaderInput("clearColor", clearColor)
            sattr = dummy.get_attrib(ShaderAttrib)

            # Dispatch the compute shader, right now!
            Globals.base.graphicsEngine.dispatch_compute(
                (dispatchW, dispatchH, 1), sattr, Globals.base.win.get_gsg())
