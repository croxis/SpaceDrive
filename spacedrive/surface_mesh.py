from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexData
from panda3d.core import GeomVertexFormat, GeomVertexWriter
from panda3d.core import Material, NodePath, Shader, Texture, TextureStage
from panda3d.core import VBase4, Vec3


def myNormalize(myVec):
    myVec.normalize()
    return myVec

format = GeomVertexFormat.getV3n3c4t2()
vdata = GeomVertexData('quadFace', format, Geom.UHDynamic)
vertex = GeomVertexWriter(vdata, 'vertex')
normal = GeomVertexWriter(vdata, 'normal')
color = GeomVertexWriter(vdata, 'color')
texcoord = GeomVertexWriter(vdata, 'texcoord')


def create_mesh(parentnp, debug=False, invert=False):
    '''This creates a simple 17x17 grid mesh for the sides of our cube.
    The ultimate goal is to use a LOD system, probably based on quadtrees.
    If debug is true then we get a color gradiant on our vertexes.'''
    x = -1.0
    y = -1.0
    vertex_count = 0
    u = 0.0
    v = 0.0

    WIDTH_STEP = 2/16.0

    while y <= 1.0:
        while x <= 1.0:
            vertex.addData3f(x, y, 0)
            if invert:
                normal.addData3f(myNormalize((Vec3(2*x+1, 2*y+1, 2*0-1))))
            else:
                normal.addData3f(myNormalize((Vec3(2*x-1, 2*y-1, 2*0-1))))
            if debug:
                color.addData4f(1.0, u, v, 1.0)
            texcoord.addData2f(u, v)
            vertex_count += 1
            x += WIDTH_STEP
            u += WIDTH_STEP/2.0
        x = -1.0
        u = 0
        y += WIDTH_STEP
        v += WIDTH_STEP/2.0

    #print vertex_count
    triangles = []

    for y in range(0, 16):
        for x in range(0, 16):
            v = 17 * y + x
            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v)
            tri.addVertex(v+1)
            tri.addVertex(v+17)
            tri.closePrimitive()
            triangles.append(tri)

            tri = GeomTriangles(Geom.UHDynamic)
            tri.addVertex(v+1)
            tri.addVertex(v+18)
            tri.addVertex(v+17)
            
            tri.closePrimitive()
            triangles.append(tri)

    mesh = Geom(vdata)
    for t in triangles:
        mesh.addPrimitive(t)
    mnode = GeomNode('quadface')
    mnode.addGeom(mesh)
    nodePath = parentnp.attachNewNode(mnode)
    return nodePath


class Body(object):
    '''Generic class for cellestial bodies with NodePath like interfaces'''
    def __init__(self, name, scale=1, debug=False):
        '''Debug will generate colored pixles for fun time. self.init()
        is called for specific body type inits'''
        self.node_path = NodePath(name)
        self.sides = []
        for i in range(0, 6):
            m = create_mesh(self.node_path, debug, invert=True)
            m.set_scale(scale)
            self.sides.append(m)

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader'''
        self.sides[0].set_hpr(90, 90, 0)
        self.sides[1].set_hpr(-90, 90, 0)
        self.sides[2].set_hpr(0, 0, 0)
        self.sides[3].set_hpr(0, 180, 0)
        self.sides[4].set_hpr(0, 90, 0)
        self.sides[5].set_hpr(180, 90, 0)
        self.init()

    def init(self):
        raise NotImplementedError()

    def set_pos(self, *args):
        self.node_path.set_pos(args)

    def set_hpr(self, *args, **kwargs):
        self.node_path.set_hpr(*args, **kwargs)

    def get_scale(self):
        return self.node_path.get_scale()

    def set_scale(self, *args):
        self.node_path.set_scale(args)

    def reparent_to(self, *args):
        self.node_path.reparent_to(args)

    def set_shader_input(self, *args, **kwargs):
        self.node_path.set_shader_input(*args, **kwargs)


class Atmosphere(Body):
    '''planet is a parent nodepath that the 6 side mesh nodepaths will parent to.
    planet can be moved, scale, and rotated with no problems'''
    def init(self):
        '''Debug will generate colored pixles for fun time'''
        shaders = Shader.load(Shader.SLGLSL, 'planet_atmosphere_vert.glsl', 'planet_atmosphere_frag.glsl')
        self.node_path.setShader(shaders)
        self.set_scale(1.025)


class Surface(Body):
    '''planet is a parent nodepath that the 6 side mesh nodepaths will parent to.
    planet can be moved, scale, and rotated with no problems'''
    def init(self):
        shaders = Shader.load(Shader.SLGLSL, 'planet_surface_vert.glsl', 'planet_surface_frag.glsl')
        self.node_path.setShader(shaders)
        tex = Texture()

        # create sane material defaults
        self.material = Material()
        self.material.set_ambient(VBase4(0.0, 0.0, 0.0, 0.0))
        self.material.set_diffuse(VBase4(0.0, 0.0, 0.0, 0.0))
        self.material.set_emission(VBase4(0.0, 0.0, 0.0, 0.0))
        self.material.set_shininess(0)
        self.material.set_specular(VBase4(0.0, 0.0, 0.0, 0.0))
        for m in self.sides:
            m.set_material(self.material)
            '''m.set_shader_input('colorTexture', tex)
            m.set_shader_input('nightTesture', tex)
            m.set_shader_input('glossTexture', tex)'''

    def set_texture(self, texture_path):
        '''Textures the surface. texture_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The orientation
        is a little different than what is described in the panda manual.

        North pole is z-up'''
        for i in range(0, 6):
            self.sides[i].setShaderInput('colorTexture',
                loader.loadTexture(texture_path.replace('#', str(i))))

    def set_textures(self, texture_path='', night_path='', gloss_path=''):
        '''MultiTextures the surface. t_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The orientation
        is a little different than what is described in the panda manual.

        North pole is z-up'''
        for i in range(0, 6):
            texture = loader.loadTexture(texture_path.replace('#', str(i)))
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setAnisotropicDegree(4)
            self.sides[i].set_shader_input('colorTexture', texture)
            if night_path:
                self.sides[i].set_shader_input('nightTesture',
                    loader.loadTexture(night_path.replace('#', str(i))))
            if gloss_path:
                self.sides[i].set_shader_input('glossTexture',
                    loader.loadTexture(gloss_path.replace('#', str(i))))

    def set_ambient(self, r, g, b, a):
        self.material.set_ambient(VBase4(float(r), float(g), float(b), float(a)))

    def set_diffuse(self, r, g, b, a):
        self.material.set_diffuse(VBase4(float(r), float(g), float(b), float(a)))

    def set_specular(self, r, g, b, a):
        self.material.set_specular(VBase4(float(r), float(g), float(b), float(a)))

    def set_shininess(self, n):
        self.material.set_shininess(n)



def make_star(name='star', scale=1, debug=False):
    return make_planet(name, scale, debug)


def make_planet(name='planet', scale=1, debug=False):
    return Surface(name, scale, debug)


def make_atmosphere(name='atmosphere'):
    return Atmosphere(name)
