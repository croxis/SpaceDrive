
import math
from panda3d.core import TransparencyAttrib, Texture, Vec2, ComputeNode

from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import DirectFrame


from LightManager import LightManager
from RenderTarget import RenderTarget
from RenderTargetType import RenderTargetType
from DebugObject import DebugObject
from BetterShader import BetterShader


class RenderingPipeline(DebugObject):

    def __init__(self, showbase):
        DebugObject.__init__(self, "RenderingPipeline")
        self.showbase = showbase
        self.lightManager = LightManager()
        self.size = self._getSize()
        self.precomputeSize = Vec2(0)
        self.camera = base.cam
        self.cullBounds = None
        self.patchSize = Vec2(32, 32)

        self._setup()

    def _setup(self):
        self.debug("Setting up render pipeline")

        # First, we need no transparency
        render.setAttrib(
            TransparencyAttrib.make(TransparencyAttrib.MNone), 100)

        # Now create deferred render buffers
        self._makeDeferredTargets()

        # Setup compute shader for lighting
        self._createLightingPipeline()

        # for debugging attach texture to shader
        self.deferredTarget.setShader(BetterShader.load(
            "Shader/DefaultPostProcess.vertex", "Shader/TextureDisplay.fragment"))
        # self.deferredTarget.setShaderInput("sampler", self.lightBoundsComputeBuff.getColorTexture())
        # self.deferredTarget.setShaderInput("sampler", self.lightPerTileStorage)
        self.deferredTarget.setShaderInput("sampler", self.lightingComputeContainer.getColorTexture())
        # self.deferredTarget.setShaderInput("sampler", self.lightManager.getAtlasTex())

        # self.deferredTarget.setShaderInput("screenSize", self.precomputeSize)

        # add update task
        self._attachUpdateTask()

        # DirectFrame(frameColor=(1, 1, 1, 0.2), frameSize=(-0.28, 0.28, -0.27, 0.4), pos=(base.getAspectRatio() - 0.35, 0.0, 0.49))

        # self.atlasDisplayImage =  OnscreenImage(image = self.lightManager.getAtlasTex(), pos = (base.getAspectRatio() - 0.35, 0, 0.5), scale=(0.25,0,0.25))



    # Creates all the render targets
    def _makeDeferredTargets(self):
        self.debug("Creating deferred targets")
        self.deferredTarget = RenderTarget("DeferredTarget")
        self.deferredTarget.addRenderTexture(RenderTargetType.Color)
        self.deferredTarget.addRenderTexture(RenderTargetType.Depth)
        self.deferredTarget.addRenderTexture(RenderTargetType.Aux0)
        self.deferredTarget.addRenderTexture(RenderTargetType.Aux1)
        self.deferredTarget.setAuxBits(16)
        self.deferredTarget.setColorBits(16)
        self.deferredTarget.setDepthBits(32)
        # self.deferredTarget.setSize(400, 240) # check for overdraw
        self.deferredTarget.prepareSceneRender()

    # Creates the storage to store the list of visible lights per tile
    def _makeLightPerTileStorage(self):

        storageSizeX = int(self.precomputeSize.x * 8)
        storageSizeY = int(self.precomputeSize.y * 8)

        self.debug(
            "Creating per tile storage of size", storageSizeX, "x", storageSizeY)

        self.lightPerTileStorage = Texture("LightsPerTile")
        self.lightPerTileStorage.setup2dTexture(
            storageSizeX, storageSizeY, Texture.TFloat, Texture.F_r16)
        self.lightPerTileStorage.setMinfilter(Texture.FTNearest)
        self.lightPerTileStorage.setMagfilter(Texture.FTNearest)

    # Inits the lighting pipeline
    def _createLightingPipeline(self):
        self.debug("Creating lighting pipeline ..")

        # size has to be a multiple of the compute unit size
        # but still has to cover the whole screen
        sizeX = int(math.ceil(self.size.x / self.patchSize.x))
        sizeY = int(math.ceil(self.size.y / self.patchSize.y))

        self.precomputeSize = Vec2(sizeX, sizeY)

        self.debug("Batch size =", sizeX, "x", sizeY,
                   "Actual Buffer size=", int(sizeX * self.patchSize.x), "x", int(sizeY * self.patchSize.y))

        self._makeLightPerTileStorage()

 

        # Create a buffer which computes which light affects which tile
        self._makeLightBoundsComputationBuffer(sizeX, sizeY)

        # Create a buffer which applies the lighting
        self._makeLightingComputeBuffer()

        # Register for light manager
        self.lightManager.setLightingComputators(
            [self.lightBoundsComputeBuff, self.lightingComputeContainer])


        # Ensure the images have the correct filter mode
        for bmode in [RenderTargetType.Color]:
            tex = self.lightBoundsComputeBuff.getTexture(bmode)
            tex.setMinfilter(Texture.FTNearest)
            tex.setMagfilter(Texture.FTNearest)

        self._loadFallbackCubemap()

        # Create storage for the bounds computation

        # Set inputs
        self.lightBoundsComputeBuff.setShaderInput(
            "destination", self.lightPerTileStorage)
        self.lightBoundsComputeBuff.setShaderInput(
            "depth", self.deferredTarget.getDepthTexture())

        self.lightingComputeContainer.setShaderInput(
            "data0", self.deferredTarget.getColorTexture())
        self.lightingComputeContainer.setShaderInput(
            "data1", self.deferredTarget.getAuxTexture(0))
        self.lightingComputeContainer.setShaderInput(
            "data2", self.deferredTarget.getAuxTexture(1))

        self.lightingComputeContainer.setShaderInput("shadowAtlas", self.lightManager.getAtlasTex())

    def _loadFallbackCubemap(self):
        cubemap = loader.loadCubeMap("Cubemap/#.png")
        cubemap.setMinfilter(Texture.FTLinearMipmapLinear)
        cubemap.setMagfilter(Texture.FTLinearMipmapLinear)
        cubemap.setFormat(Texture.F_srgb_alpha)
        self.lightingComputeContainer.setShaderInput(
            "fallbackCubemap", cubemap)

    def _makeLightBoundsComputationBuffer(self, w, h):
        self.debug("Creating light precomputation buffer of size", w, "x", h)
        self.lightBoundsComputeBuff = RenderTarget("ComputeLightTileBounds")
        self.lightBoundsComputeBuff.setSize(w, h)
        self.lightBoundsComputeBuff.addRenderTexture(RenderTargetType.Color)
        self.lightBoundsComputeBuff.setColorBits(16)
        self.lightBoundsComputeBuff.prepareOffscreenBuffer()

        self.lightBoundsComputeBuff.setShaderInput("mainCam", base.cam)
        self.lightBoundsComputeBuff.setShaderInput("mainRender", base.render)

        self._setPositionComputationShader()


    def _makeLightingComputeBuffer(self):
        self.lightingComputeContainer = RenderTarget("ComputeLighting")
        # self.lightingComputeContainer.setSize()
        self.lightingComputeContainer.addRenderTexture(RenderTargetType.Color)
        self.lightingComputeContainer.setColorBits(16)
        self.lightingComputeContainer.prepareOffscreenBuffer()

        self.lightingComputeContainer.setShaderInput(
            "lightsPerTile", self.lightPerTileStorage)

        self.lightingComputeContainer.setShaderInput("cameraPosition", base.cam.getPos(render))


    def _setLightingShader(self):
        lightShader = BetterShader.load(
            "Shader/DefaultPostProcess.vertex", "Shader/ApplyLighting.fragment")
        self.lightingComputeContainer.setShader(lightShader)

    def _setPositionComputationShader(self):
        pcShader = BetterShader.load(
            "Shader/DefaultPostProcess.vertex", "Shader/PrecomputeLights.fragment")
        self.lightBoundsComputeBuff.setShader(pcShader)

    def _getSize(self):
        return Vec2(
            int(self.showbase.win.getXSize()),
            int(self.showbase.win.getYSize()))

    def debugReloadShader(self):
        self.lightManager.debugReloadShader()
        self._setPositionComputationShader()
        self._setLightingShader()

    def _attachUpdateTask(self):
        self.showbase.addTask(self._update, "UpdateRenderingPipeline",sort=-10000)

    def _computeCameraBounds(self):
        # compute camera bounds in render space
        cameraBounds = self.camera.node().getLens().makeBounds()
        cameraBounds.xform(self.camera.getMat(render))
        return cameraBounds

    def _update(self, task):

        self.cullBounds = self._computeCameraBounds()

        self.lightManager.setCullBounds(self.cullBounds)
        self.lightManager.update()

        self.lightingComputeContainer.setShaderInput("cameraPosition", base.cam.getPos(render))

        return task.cont

    def getLightManager(self):
        return self.lightManager

    def getDefaultObjectShader(self):
        shader = BetterShader.load(
            "Shader/DefaultObjectShader.vertex", "Shader/DefaultObjectShader.fragment")
        return shader
