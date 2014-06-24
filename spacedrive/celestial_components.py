from panda3d.core import LPoint3d, NodePath

'''Types of bodies:
    solid: Planet, asteroid
    star: Star
    moon: moon (due to orbit information)'''

TYPES = {'moon': 0, 'solid': 1, 'star': 2, 'barycenter': 3}


class BaryCenter(NodePath):
    '''This class is used to simulate the center of a multibody system.
    Mass is the sum of masses of the multibody system
    SOI is the sphere of influence of a body for patched conics
    In this case soi is the "virtual" sphere for the entire system'''


class Body(BaryCenter):
    period = 0
    radius = 1
    kind = "solid"


class Star(Body):
    kind = "star"
    absoluteM = 1
    spectralType = ""


class CelestialComponent(object):
    nodePath = None
    truePos = LPoint3d(0, 0, 0)
    mass = 0
    soi = 0
    kind = None
    orbit = {}
