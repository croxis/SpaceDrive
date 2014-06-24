# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

if sys.version > '3':
    long = int

import sandbox

from direct.directnotify.DirectNotify import DirectNotify

from panda3d.core import loadPrcFileData
from panda3d.core import VirtualFileSystem

from . import celestial_components
from . import physics_components

from . import orbit_system
from . import physics_system

from . import universals
log = DirectNotify().newCategory("SpaceDrive")

vfs = VirtualFileSystem.getGlobalPtr()


def init(
        run_server=False,
        run_client=False,
        local_only=False,
        log_filename=None,
        log_level=None,
        window_title='SpaceDrive'
):
    """Call first. This will set up the initial engine state"""
    loadPrcFileData("", "notify-level-SpaceDrive " + log_level)
    if log_level == 'debug':
        log.setSeverity(2)
    if log_level == 'info':
        log.setSeverity(3)
    if log_level == 'warning':
        log.setSeverity(4)
    log.info("Init SpaceDrive")
    universals.run_server = run_server
    universals.run_client = run_client
    if log_filename:
        mstream = MultiplexStream()
        mstream.addFile(logFilename)
        mstream.addStandardOutput()
        Notify.ptr().setOstreamPtr(mstream, False)

        # Also make Python output go to the same place.
        sw = StreamWriter(mstream, False)
        sys.stdout = sw
        sys.stderr = sw

        # Since we're writing to a log file, turn on timestamping.
        loadPrcFileData('', 'notify-timestamp 1')

    if not run_client:
        # Don't open a graphics window on the server.  (Open a window only
        # if we're running a normal client, not one of the server
        # processes.)
        loadPrcFileData('', 'window-type none\naudio-library-name null')
    else:
        loadPrcFileData('', 'frame-rate-meter-scale 0.035')
        loadPrcFileData('', 'frame-rate-meter-side-margin 0.1')
        loadPrcFileData('', 'show-frame-rate-meter 1')
        loadPrcFileData('', 'window-title ' + window_title)
        loadPrcFileData('', "sync-video 0")
        loadPrcFileData('', 'task-timer-verbose 1')
        loadPrcFileData('', 'pstats-tasks 1')
        loadPrcFileData('', 'want-pstats 1')
    log.info("Loading Sandbox")
    sandbox.init(log_level=log_level)
    sandbox.base.setSleep(0.001)
    sandbox.base.disableMouse()


def init_system(system, component=None):
    """

    :param system:
    :param component:
    """
    system = system(component)
    system.init()
    sandbox.add_system(system)


def init_graphics():
    '''Sets up multipass rendering. Rendering is done in this order:
    Skybox, Suns, Atmospheres, Celestial bodies, ships'''


def init_client_net(system, component=None, address='127.0.0.1', port='1999'):
    """Sets up and registers client network system."""


def init_server_net(system, component=None, address='127.0.0.1', port='1999'):
    system = system(component)
    system.init(address, port)
    sandbox.add_system(system)


def init_physics(system=physics_system.PhysicsSystem,
                 component=physics_components.BulletPhysicsComponent):
    init_system(system, component)


def init_orbits(system=orbit_system.OrbitSystem,
                component=celestial_components.CelestialComponent):
    init_system(system, component)


def run():
    sandbox.run()


if __name__ == '__main__':
    init(run_server=True, run_client=True, log_level='debug')
    print("Testing systems")
    run()
