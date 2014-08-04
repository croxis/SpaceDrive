__author__ = 'croxis'

from panda3d.core import Texture


def prepare_srgb(node_path):
    for tex in node_path.findAllTextures():

        baseFormat = tex.getFormat()

        if baseFormat == Texture.FRgb:
            tex.setFormat(Texture.FSrgb)
        elif baseFormat == Texture.FRgba:
            tex.setFormat(Texture.FSrgbAlpha)
        else:
            print "Unkown texture format:", baseFormat
            print "\tTexture:", tex

        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        tex.setAnisotropicDegree(16)

    # for stage in np.findAllTextureStages():
    # print stage, stage.getMode()
