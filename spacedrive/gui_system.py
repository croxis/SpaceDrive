__author__ = 'croxis'
from cefpython3 import cefpython
import sandbox

from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import CardMaker, PNMImage, Texture, TransparencyAttrib
log = DirectNotify().newCategory("SpaceDrive-GUISystem")


def load_page(path):
    with open(path) as f:
        system = sandbox.get_system(GUISystem)
        system.load_string(f.read())


class ClientHandler(object):
    """A client handler is required for the browser to do built in callbacks
    back into the application."""
    def OnPaint(self, browser, paintElementType, dirtyRects, buffer, width, height):
        image = self.texture.modifyRamImage()
        if paintElementType == cefpython.PET_POPUP:
            log.debug("width=%s, height=%s" % (width, height))
        elif paintElementType == cefpython.PET_VIEW:
            image.set_data(buffer.GetString(mode="rgba", origin="bottom-left"))
        else:
            raise Exception("Unknown paintElementType: %s" % paintElementType)

    def GetViewRect(self, browser, rect):
        rect.append(0)
        rect.append(0)
        rect.append(self.texture.getXSize())
        rect.append(self.texture.getYSize())
        return True

    def GetScreenPoint(self, browser, viewX, viewY, screenCoordinates):
        print("GetScreenPoint()", browser, viewX, viewY, screenCoordinates)
        return False

    def OnLoadEnd(self, browser, frame, httpStatusCode):
        print("Load end", browser, frame, httpStatusCode)

    def OnLoadError(self, browser, frame, errorCode, errorText, failedURL):
        print("load error", browser, frame, errorCode, errorText, failedURL)


class GUISystem(sandbox.EntitySystem):
    """Manager for in game gui. This does not use entities or components for
    now. We just leverage Sandbox's infrastructure.

    If we plan on having additional browser windows in game we will need
    to redesign this architecture so gui is a subsystem."""
    browser = None
    image = None
    node_path = None
    texture = None
    handler = None

    def init(self):
        print("running")
        settings = {
        "log_severity": cefpython.LOGSEVERITY_INFO, # LOGSEVERITY_VERBOSE
        #"log_severity": cefpython.LOGSEVERITY_VERBOSE, # LOGSEVERITY_VERBOSE
        #"log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
        cefpython.GetModuleDirectory(), "subprocess")
        }
        print("Settings:", settings)
        cefpython.g_debug = True
        cefpython.Initialize(settings)
        # Set up the texture for the off screen browser to render to.
        cardMaker = CardMaker("browser2d")
        #cardMaker.setFrame(-0.75, 0.75, -0.75, 0.75)
        cardMaker.setFrameFullscreenQuad()
        node = cardMaker.generate()
        #For UI attach to render2d
        self.node_path = sandbox.base.render2d.attachNewNode(node)
        self.node_path.setTransparency(TransparencyAttrib.MAlpha)
        #self.node_path.setTexture(self.texture)
        window_handle = sandbox.base.win.getWindowHandle().getIntHandle()
        window_info = cefpython.WindowInfo()
        # You can pass 0 to parentWindowHandle, but then some things like
        # context menus and plugins may not display correctly.
        window_info.SetAsOffscreen(window_handle)
        #windowInfo.SetAsOffscreen(0)
        window_info.SetTransparentPainting(True)
        browser_settings = {}
        # Using non about:blank in constructor results in error before render
        # handler callback is set.
        # Either set it before/during construction, or set it after then call
        # LoadURL after it is set.
        self.browser = cefpython.CreateBrowserSync(
            window_info, browser_settings,
            navigateUrl="about:blank")
        self.browser.SendFocusEvent(True)
        self.handler = ClientHandler()
        self.browser.SetClientHandler(self.handler)
        self.set_browser_size()
        self.browser.SetClientCallback("OnLoadEnd", self.on_load_end)
        #self.browser.WasResized()

        self.accept("window-event", self.set_browser_size)
        self.accept("mouse1", self.on_mouse_down)
        self.accept("mouse1-up", self.on_mouse_up)

    def begin(self):
         cefpython.MessageLoopWork()

    def on_load_end(self, *args, **kwargs):
        print("load end", args, kwargs)# Example of one kind of call back

    def set_browser_size(self, window=None):
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
        self.handler.texture = self.texture
        self.handler.image = self.handler.texture.modifyRamImage()
        self.browser.WasResized()

    def load_string(self, html):
        """Load a web page from a string."""
        self.browser.GetMainFrame().LoadString(html, "http://fake")
        self.browser.GetMainFrame().ExecuteJavascript('window.location="http://google.com/"')
        self.browser.GetMainFrame().LoadUrl('http://google.com')

    def on_mouse_down(self):
        '''This logic is set up for an ui where the mouse will be interacting with
        both ui elements and in world elements, such as an rts, tbs, or simulation
        game. This requires checking if the pixel the mouse clicked on is ui or
        not.

        We do this by checking the alpha level of the ui texture. If there is
        no alpha we hand off to the other parts of the mouse ui logic. If there
        is alpha the mouse click is passed to the browser instead.

        It is advised to create another mouse click event that is fired when
        alpha = 0 and have the additional logic listen for that. Otherwise
        anything listening to mouse1 and mouse1-up will fire reguardless of
        the position of the mouse.'''

        if sandbox.base.win.has_pointer(0):
            x = int(sandbox.base.win.get_pointer(0).get_x())
            y = int(sandbox.base.win.get_pointer(0).get_y())
            '''# This is probably a more memory efficent, but does not work
            peek = handler.texture.peek()
            color = VBase4(1, 0, 1, 0)
            peek.lookup(color, int(x), int(y))
            print color, x, y'''
            # So this way instead!
            image = PNMImage()
            self.texture.store(image)
            if image.get_alpha(x, y):
                self.browser.SendMouseClickEvent(x, y, cefpython.MOUSEBUTTON_LEFT,
                    mouseUp=False, clickCount=1)
            else:
                print("Screen picking logic here!")
                #click_object()
            image.clear()

    def on_mouse_up(self):
        '''You may wish to pass all mouse-up events to both the browser
        and the game logic, depending on your needs.'''
        if sandbox.base.win.has_pointer(0):
            x = int(sandbox.base.win.get_pointer(0).get_x())
            y = int(sandbox.base.win.get_pointer(0).get_y())
            '''# This is probably a more memory efficent, but does not work
            peek = handler.texture.peek()
            color = VBase4(1, 0, 1, 0)
            peek.lookup(color, int(x), int(y))
            print color, x, y'''

            image = PNMImage()
            self.texture.store(image)
            if image.get_alpha(x, y):
                self.browser.SendMouseClickEvent(x, y, cefpython.MOUSEBUTTON_LEFT,
                    mouseUp=True, clickCount=1)
            else:
                print("Screen picking logic here!")
            image.clear()


