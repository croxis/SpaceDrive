__author__ = 'croxis'
from cefpython3 import cefpython
import sandbox

from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import CardMaker, Texture, TransparencyAttrib
log = DirectNotify().newCategory("SpaceDrive-GUISystem")



class GUISystem(sandbox.EntitySystem):
    """Manager for in game gui. This does not use entities or components for
    now. We just leverage Sandbox's infrastructure.

    If we plan on having additional browser windows in game we will need
    to redesign this architecture so gui is a subsystem."""
    browser = None
    image = None
    node_path = None
    texture = None

    def init(self):
        settings = {
        "log_severity": cefpython.LOGSEVERITY_INFO, # LOGSEVERITY_VERBOSE
        #"log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
        cefpython.GetModuleDirectory(), "subprocess")
        }
        cefpython.g_debug = True
        cefpython.Initialize(settings)

        # Set up the texture for the off screen browser to render to.
        cardMaker = CardMaker("browser2d")
        cardMaker.setFrameFullscreenQuad()
        node = cardMaker.generate()
        #For UI attach to render2d
        node_path = sandbox.base.render2d.attachNewNode(node)
        node_path.setTransparency(TransparencyAttrib.MAlpha)
        window_handle = sandbox.base.win.getWindowHandle().getIntHandle()
        window_info = cefpython.WindowInfo()
        #You can pass 0 to parentWindowHandle, but then some things like context menus and plugins may not display correctly.
        window_info.SetAsOffscreen(window_handle)
        #windowInfo.SetAsOffscreen(0)
        window_info.SetTransparentPainting(True)
        browser_settings = {}
        # Using non about:blank in constructor results in error before render handler callback is set.
        # Either set it before/during construction, or set it after then call LoadURL after it is set.
        self.browser = cefpython.CreateBrowserSync(
            window_info, browser_settings,)
        #    navigateUrl="http://www.panda3d.org")
        self.browser.SendFocusEvent(True)
        self.browser.SetClientHandler(self)
        self.set_browser_size()
        sandbox.base.accept("window-event", self.set_browser_size)

    def set_browser_size(self):
        """Set the off screen browser to the same resolution of the panda window.

        Best I can find is creating a new texture on resize.
        """
        self.texture = Texture()
        self.texture.setCompression(Texture.CMOff)
        self.texture.setComponentType(Texture.TUnsignedByte)
        self.texture.setFormat(Texture.FRgba4)
        self.texture.setXSize(sandbox.base.win.getXSize())
        self.texture.setYSize(sandbox.base.win.getYSize())
        self.node_path.setTexture(self.texture)
        self.image = self.texture.modifyRamImage()
        self.browser.WasResized()

    # The following are built in callbacks.
    def OnPaint(self, browser, paintElementType, dirtyRects, buffer, width, height):
        if paintElementType == cefpython.PET_POPUP:
            log.debug("width=%s, height=%s" % (width, height))
        elif paintElementType == cefpython.PET_VIEW:
            self.image.set_data(buffer.GetString(mode="rgba", origin="bottom-left"))
        else:
            raise Exception("Unknown paintElementType: %s" % paintElementType)

    def GetViewRect(self, browser, rect):
        width = self.texture.getXSize()
        height = self.texture.getYSize()
        rect.append(0)
        rect.append(0)
        rect.append(width)
        rect.append(height)
        return True