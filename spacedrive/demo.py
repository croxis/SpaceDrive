from direct.directnotify.DirectNotify import DirectNotify
from panda3d.core import loadPrcFileData

loadPrcFileData("", "notify-level-demos debug")
log = DirectNotify().newCategory("demos")

import spacedrive
spacedrive.init()



