import sandbox

from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import CardMaker, PNMImage, Texture, TransparencyAttrib

log = DirectNotify().newCategory("SpaceDrive-GUISystem")


def load_page(path, *callbacks):
    with open(path) as f:
        system = sandbox.get_system(GUISystem)
        if callbacks:
            system.load_string(f.read(), *callbacks)
        else:
            system.load_string(f.read())


def setup_screen(screen):
    """Generates a screen and callbacks from a screen object."""
    system = sandbox.get_system(GUISystem)
    system.setup_screen(screen)


class ClientHandler:
    #TODO: Implement LUI
    pass


class GUISystem(sandbox.EntitySystem):
    """Manager for in game gui. This does not use entities or components for
    now. We just leverage Sandbox's infrastructure.

    If we plan on having additional browser windows in game we will need
    to redesign this architecture so gui is a subsystem."""
    # TODO: Implement LUI
    browser = None
    node_path = None
    handler = None

    def init(self):
        pass

    def setup_screen(self, *args, **kwargs):
        pass