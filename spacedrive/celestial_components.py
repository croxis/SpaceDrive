from panda3d.core import LPoint3d, NodePath


class SolarSystemComponent:
    def __init__(self, name='Solar System', root_node=NodePath()):
        self.name = name
        self.root_node = root_node


'''Types of bodies:
    solid: Planet, asteroid
    star: Star
    moon: moon (due to orbit information)'''

TYPES = {'moon': 0, 'solid': 1, 'star': 2, 'barycenter': 3}


class CelestialComponent(object):
    def __init__(self, parent_entity, node_path=NodePath(), true_pos=LPoint3d(0, 0, 0),
                 mass=0, soi=0, kind='', orbit=None):
        if not orbit:
            orbit = {}
        self.node_path = node_path
        self.parent_entity = parent_entity
        self.true_pos = true_pos
        self.mass = mass
        self.soi = soi
        self.kind = kind
        self.orbit = orbit
        self.radius = 1
        self.rotation = 0


class StarComponent(object):
    def __init__(self, absolute_magnitude=1, spectral_type=''):
        self.absolute_magnitude = absolute_magnitude
        self.spectral_type = spectral_type
