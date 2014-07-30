from panda3d.core import PerlinNoise2


class CelestialRenderComponent(object):
    body = None
    atmosphere = None
    light = None
    noise = PerlinNoise2(64, 64)
    noise_texture = None
    mesh = None
    temperature = 0
