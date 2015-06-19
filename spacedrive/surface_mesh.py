# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import os

from panda3d.core import Geom, GeomNode, GeomTriangles, GeomVertexArrayFormat
from panda3d.core import GeomVertexData, GeomVertexFormat, GeomVertexWriter
from panda3d.core import CardMaker, InternalName
from panda3d.core import Material, NodePath, PerlinNoise3, PNMImage, Point3
from panda3d.core import Texture, TextureStage
from panda3d.core import VBase4, Vec3

import sandbox

from .renderpipeline.Code.BetterShader import BetterShader
from .utils import convertToPatches


#you cant normalize in-place so this is a helper function
def normalize(vec):
    vec.normalize()
    return vec


# Build array for new format.
array = GeomVertexArrayFormat()
array.addColumn(InternalName.make(b'vertex'), 3, Geom.NTFloat32, Geom.CPoint)
array.addColumn(InternalName.make(b'texcoord'), 2, Geom.NTFloat32, Geom.CTexcoord)
array.addColumn(InternalName.make(b'normal'), 3, Geom.NTFloat32, Geom.CVector)
array.addColumn(InternalName.make(b'binormal'), 3, Geom.NTFloat32, Geom.CVector)
array.addColumn(InternalName.make(b'tangent'), 3, Geom.NTFloat32, Geom.CVector)

# Create and register format.
format = GeomVertexFormat()
format.addArray(array)
format = GeomVertexFormat.registerFormat(format)


def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


def vector_copy(v):
    """Utility function to coerce a list or tuple into Vec3 format"""
    return Vec3(v[0], v[1], v[2])


def point_copy(p):
    """Utility function to coerce a list or tuple into Point3 format"""
    return Point3(p[0], p[1], p[2])


class myGeom(object):
    def __init__(self, center=[0.0, 0.0, 0.0], scale=1.0, smooth=True, tangents=True, verts=None, polys=None, mats=None, norms=None, uvs=None, mapping="box", fit_uvs=False):
        """
        Variable mapping should be a string defining the UV mapping type to use.
        Options are:
        'planar' = Planar mapping along forward axis
        'box' = Box mapping
        'sphere' = Sphere mapping along vertical axis, with split poles
        'cylinder' = Cylinder mapping, no caps
        'cylinder_cap' or 'cylinder_caps' = Cylinder mapping with caps
        'global' = Global mapping, in which all objects mapped with this type will share the same UV space
        'tile' or 'poly' = Per-poly, tiled mapping, with each poly maximized to fill the entire 0-1 UV range
        The object will not be mapped if texcoords are provided in the uvs list.

        Instantiate the class providing at least verts and polys, in the format shown below.
        Without both verts and polys submitted, class will default to creating an example box geometry.
        This class was intended to be compatible with e.g. a simple obj file reader, which would pass
        the vertices, polygons, normals, and materials from the obj.

        If smooth is True and norms is None, vertex normals will be smoothed across polygons.
        If tangents is True, tangents and bitangents will be calculated.
        """
        self.example = False
        self.smooth = smooth
        self.use_tangents = tangents
        self.mapping = mapping
        self.fit_uvs = fit_uvs

        if verts:
            #self.verts = verts
            self.verts = [[0.0, 0.0, 0.0] for i in verts]
            for vi in range(len(verts)):
                for i in range(3):
                    self.verts[vi][i] = (verts[vi][i] + center[i]) * scale
            if polys:
                self.polys = polys
            else:
                self.example = True
        else:
            self.example = True

        if self.example:
            self.box = [center[0]-scale,center[0]+scale, center[1]-scale, center[1]+scale, center[2]-scale, center[2]+scale]
            # box format is [minX,maxX,minY,maxY,minZ,maxZ]
            self.verts = [ [self.box[0],self.box[2],self.box[4]], [self.box[0],self.box[3],self.box[4]],
                           [self.box[0],self.box[3],self.box[5]], [self.box[0],self.box[2],self.box[5]],
                           [self.box[1],self.box[2],self.box[4]],[self.box[1],self.box[3],self.box[4]],
                           [self.box[1],self.box[3],self.box[5]],[self.box[1],self.box[2],self.box[5]] ]
            self.polys = [[3,2,1,0],[4,5,6,7],[5,4,0,1],[6,5,1,2],[7,6,2,3],[4,7,3,0]]
            self.mats = ["right", "left", "bottom", "back", "top", "front"]

        if norms:
            self.vnorms = norms
        else:
            self.vnorms = None

        if uvs:
            self.uvs = uvs
            self.uvMapper = None
        else:
            self.uvs = None
            self.uvMapper = myUVMapper()

        if mats:
            self.mats = mats
        else:
            if not self.example:
                self.mats = ["Preview" for i in self.polys]

        if not self.smooth:
            self.split_verts()

        self.colors = []
        for name in self.mats:
            if not name in self.colors:
                self.colors.append(name)

        self.textureStages = None

    def split_verts(self):
        """Split all the polygons, for hard edges."""
        verts = [[j for j in i] for i in self.verts]
        self.verts = []
        polys = [[j for j in i] for i in self.polys]
        self.polys = [[] for i in polys]
        for poly_index in range(len(polys)):
            poly = polys[poly_index]
            for vi in poly:
                self.verts.append([i for i in verts[vi]])
                self.polys[poly_index].append(len(self.verts)-1)
        if (self.vnorms != None) and (len(self.vnorms) != len(self.verts)):
            self.vnorms = None # Clear the normals list if lengths no longer match

    def build(self):
        # http://www.panda3d.org/forums/viewtopic.php?t=11528
        """Create the geometry from the submitted arrays"""
        verts = self.verts
        polys = self.polys
        self.geomnode = GeomNode('geometry')
        self.color_lookup = []
        if not self.vnorms:
            self.getNormals()
        if not self.uvs:
            self.getUVMapping()
        if self.use_tangents:
            self.getTangents()

        # Build array for new format.
        array = GeomVertexArrayFormat()
        array.addColumn(InternalName.make(b'vertex'), 3, Geom.NTFloat32, Geom.CPoint)
        array.addColumn(InternalName.make(b'texcoord'), 2, Geom.NTFloat32, Geom.CTexcoord)
        array.addColumn(InternalName.make(b'normal'), 3, Geom.NTFloat32, Geom.CVector)
        if self.use_tangents:
            array.addColumn(InternalName.make(b'binormal'), 3, Geom.NTFloat32, Geom.CVector)
            array.addColumn(InternalName.make(b'tangent'), 3, Geom.NTFloat32, Geom.CVector)

        # Create and register format.
        format = GeomVertexFormat()
        format.addArray(array)
        format = GeomVertexFormat.registerFormat(format)

        geoms = []
        for i in range(len(self.colors)):
            vdata = GeomVertexData('ngon', format, Geom.UHStatic)
            geom = Geom(vdata)
            tri = GeomTriangles(Geom.UHStatic)
            vertex = GeomVertexWriter(vdata, b'vertex')
            normal = GeomVertexWriter(vdata, b'normal')
            texcoord = GeomVertexWriter(vdata, b'texcoord')
            geoms.append({'geom':geom,
                          'tri':tri,
                          'vertex':vertex,
                          'texcoord':texcoord,
                          'normal':normal,
                          'index':0,
                          'vdata':vdata,
                          'color':i})
            if self.use_tangents:
                tangent = GeomVertexWriter(vdata, b'tangent')
                binormal = GeomVertexWriter(vdata, b'binormal')
                geoms[i]['tangent'] = tangent
                geoms[i]['binormal'] = binormal

        for poly_index in range(len(polys)):
            color_index = self.colors.index(self.mats[poly_index])
            vertcount = geoms[color_index]['index']

            p = polys[poly_index]
            poly = [verts[i] for i in p]
            uvs = self.uvs[poly_index]
            norm = [self.vnorms[i] for i in p]
            if self.use_tangents:
                binorm = [self.binorms[i] for i in p]
                tan = [self.tans[i] for i in p]
            reindexed = [] # New vertex indices per-poly

            for v in poly:
                geoms[color_index]['vertex'].addData3f(v[0], v[1], v[2])
                reindexed.append(vertcount)
                vertcount += 1
            geoms[color_index]['index'] = vertcount
            for i in range(len(poly)):
                geoms[color_index]['normal'].addData3f(Vec3(norm[i][0], norm[i][1], norm[i][2]))
                if self.use_tangents:
                    geoms[color_index]['binormal'].addData3f(Vec3(binorm[i][0], binorm[i][1], binorm[i][2]))
                    geoms[color_index]['tangent'].addData3f(Vec3(tan[i][0], tan[i][1], tan[i][2]))
            for tvert in uvs:
                geoms[color_index]['texcoord'].addData2f(tvert[0], tvert[1])

            triangulated = self.getFanning(reindexed) # Use new vertex indices
            for tri_index in range(len(triangulated)):
                t = triangulated[tri_index]
                tri = geoms[color_index]['tri']
                tri.addVertices(t[0], t[1], t[2])

        for color_index in range(len(self.colors)):
            geom = geoms[color_index]['geom']
            tri = geoms[color_index]['tri']
            tri.closePrimitive()
            geom.addPrimitive(tri)
            self.geomnode.addGeom(geom)
            self.color_lookup.append(color_index)
        #self.setMats()

    '''def setMats(self): # This shows how to set up multi-texturing on a procedural geometry.
        """Set the texture and normal maps"""
        color_attribs = []
        self.textureStages = []
        for i in range(len(self.colors)):
            name = self.colors[i]
            tex = Texture("%s_tex" %(name))
            texAttrib = TextureAttrib.make()
            ts_tex = TextureStage("%s_tex"%(name))
            ts_tex.setMode(TextureStage.MModulate)
            texAttrib = texAttrib.addOnStage(ts_tex, tex)
            bump = Texture("%s_bump" %(name))
            ts_bump = TextureStage("%s_bump"%(name))
            ts_bump.setMode(TextureStage.MNormal)
            texAttrib = texAttrib.addOnStage(ts_bump, bump)
            color_attribs.append(texAttrib)
            self.textureStages.append(myTextureStage("%s_tex"%(name), ts_tex, tex, TextureStage.MModulate, matname=name))
            self.textureStages.append(myTextureStage("%s_bump"%(name),ts_bump, bump, TextureStage.MNormal, matname=name))
        for index in range(self.geomnode.getNumGeoms()):
            color = self.color_lookup[index]
            texAttrib = color_attribs[color]
            newRenderState = self.geomnode.getGeomState(index).addAttrib(texAttrib,1)
            self.geomnode.setGeomState(index, newRenderState)'''

    def getUVMapping(self):
        """Get the UV mapping from the myUVMapper class instance"""
        if self.mapping == "box":
            self.uvMapper.box_map(self.verts, self.polys, inbounds=0)
        elif self.mapping == "planar":
            self.uvMapper.planar_map(self.verts, self.polys, axis=1)
        elif self.mapping == "sphere":
            self.uvMapper.sphere_map(self.verts, self.polys, axis=2, split_poles=1, fix_overlap=1)
        elif self.mapping == "cylinder":
            self.uvMapper.cylinder_map(self.verts, self.polys, axis=2, fix_overlap=1)
        elif self.mapping == "cylinder_caps" or self.mapping == "cylinder_cap":
            self.uvMapper.cylinder_map_caps(self.verts, self.polys, axis=1, fix_overlap=1)
        elif self.mapping == "global":
            self.uvMapper.global_map(self.verts, self.polys)
        elif self.mapping == "tile" or self.mapping== "poly":
            self.uvMapper.tile_map(self.verts, self.polys)
        if self.fit_uvs:
            self.uvMapper.fitUVs()
        self.uvs = self.uvMapper.uvs

    def normalize(self, myVec):
        """Convenience function, from Panda Procedural Cube example."""
        myVec.normalize()
        return myVec

    def getNorms(self, v1, v2, v3):
        """Get the poly normal for a tri/poly/Ngon"""
        e1 = self.normalize(v1 - v2)
        e2 = self.normalize(v3 - v2)
        norm = self.normalize(e2.cross(e1))
        return norm

    def getFanning(self, poly):
        """Split Ngon into tris, using simple fanning method"""
        triangulated = []
        for index in range(1,len(poly)-1): # Number of tris per poly will be number of verts in poly, minus 2
            triangulated.append([poly[0], poly[index], poly[index+1]])
        return triangulated

    def getTangents(self):
        """
        Calculate tangents and bitangents (binormals).
        Requires both normals and texcoords up front.
        We need a set of orthonormal vectors for the normal, but
        these need to be properly aligned with the uvs for each poly.
        """
        # http://gamedev.stackexchange.com/questions/68612/how-to-compute-tangent-and-bitangent-vectors
        verts = self.verts
        polys = self.polys
        uvs = self.uvs
        norms = self.vnorms
        tan1 = [Vec3(0,0,0) for i in verts]
        tan2 = [Vec3(0,0,0) for i in verts]
        self.tans = [None for i in verts]
        self.binorms = [None for i in verts]
        epsilon = 1.19209290e-010
        for poly_index in range(len(polys)):
            p = polys[poly_index]
            i1 = p[0]
            i2 = p[1]
            i3 = p[2]

            v1 = verts[i1]
            v2 = verts[i2]
            v3 = verts[i3]

            #print uvs[poly_index]
            w1 = uvs[poly_index][0]
            w2 = uvs[poly_index][1]
            w3 = uvs[poly_index][2]

            x1 = v2[0] - v1[0]
            x2 = v3[0] - v1[0]
            y1 = v2[1] - v1[1]
            y2 = v3[1] - v1[1]
            z1 = v2[2] - v1[2]
            z2 = v3[2] - v1[2]

            s1 = w2[0] - w1[0]
            s2 = w3[0] - w1[0]
            t1 = w2[1] - w1[1]
            t2 = w3[1] - w1[1]

            d = (s1 * t2 - s2 * t1)
            if abs(d) < epsilon: # Float division error protection.
                d = epsilon
            r = 1.0 / d
            sdir = Vec3((t2 * x1 - t1 * x2) * r, (t2 * y1 - t1 * y2) * r, (t2 * z1 - t1 * z2) * r)
            tdir = Vec3((s1 * x2 - s2 * x1) * r, (s1 * y2 - s2 * y1) * r, (s1 * z2 - s2 * z1) * r)

            tan1[i1] += sdir
            tan1[i2] += sdir
            tan1[i3] += sdir

            tan2[i1] += tdir
            tan2[i2] += tdir
            tan2[i3] += tdir

        for a in range(len(verts)):
            n = norms[a]
            t = tan1[a]
            # Gram-Schmidt orthogonalize
            self.tans[a] = self.normalize((t - n * n.dot(t)))
            # Calculate handedness
            ncross = n.cross(t)
            t2 = Vec3(tan2[a][0], tan2[a][1], tan2[a][2])
            if ncross.dot(t2) < 0.0: # If pointing in opposite directions
                self.tans[a] *= -1.0 # Flip it
            self.binorms[a] = self.normalize(self.tans[a].cross(n))

    def getNormals(self):
        """
        Gathers all the face normals, then the vertex normals from those.
        """
        self.pnorms = [None for i in range(len(self.polys))]
        polys = self.polys
        for poly_index in range(len(polys)):
            p = polys[poly_index]
            face = [self.verts[i] for i in p]
            vecs = []
            for v in face:
                vecs.append(Vec3(v[0], v[1], v[2]))
            self.pnorms[poly_index] = self.getNorms(vecs[0], vecs[1], vecs[2])
        self.getVertpolys()
        self.vnorms = self.getVertexNormals(self.pnorms)

    def getVertpolys(self):
        """
        self.vpolys is a convenience array to assist with sorting.
        vpolys = polygons of vertices
        Whereas self.polys lists verts of polys, this lists polys of verts.
        Used here to sort polygon normals into vertex normals.
        """
        polys = self.polys
        self.vpolys = [[] for i in range(len(self.verts))]
        for pvi in range(len(polys)):
            for v in polys[pvi]:
                if not pvi in self.vpolys[v]:
                    self.vpolys[v].append(pvi)

    def getVertexNormals(self, norms):
        """
        norms is poly normals, binormals, or tangents
        vpolys is polygons of vertices, from myMesh instance
        Get the vertex normals from poly normals
        """
        vpolys = self.vpolys
        vnorms = [[0.0,0.0,0.0] for i in vpolys]
        for vi in range(len(vpolys)):
            polys = vpolys[vi]
            nx = 0; ny = 0; nz = 0
            l = len(polys)
            if l == 0: # In some unusual geometries, there may be vertices with no polygon associations - we try to skip these.  1/26/08
                #print "Stray vertex: %s, %s" %(vi,l)
                continue # If we don't skip these, we get a divide by zero crash error due to a bad mesh.
            for p in polys:
                nx += norms[p][0]
                ny += norms[p][1]
                nz += norms[p][2]
            n = Vec3(nx/l,ny/l,nz/l)
            n = self.normalize(n)    # Shouldn't need to do this, but it can't hurt
            vnorms[vi] = n
        return vnorms


class myUVMapper(object):
    def __init__(self):
        self.uvs = []
        self.epsilon = 1.19209290e-07

    def getAxis(self, xdir):
        """Get the major axis along which a vector points"""
        absz = [abs(i) for i in xdir]
        index = absz.index(max(absz))
        sign = self.getSign(xdir[index])
        axis = [0,0,0]
        axis[index] = 1 * sign
        return axis

    def getSign(self, num):
        if abs(num) == num:
            return 1
        return -1

    def getBounds(self, verts):
        """
        create bounding boxes
        """
        # box format is [minX,maxX,minY,maxY,minZ,maxZ]
        minX = 1000000.0; maxX = -1000000.0
        minY = 1000000.0; maxY = -1000000.0
        minZ = 1000000.0; maxZ = -1000000.0
        for i in range(len(verts)):
            tx = verts[i][0]
            ty = verts[i][1]
            tz = verts[i][2]
            if tx < minX: minX = tx
            if tx > maxX: maxX = tx
            if ty < minY: minY = ty
            if ty > maxY: maxY = ty
            if tz < minZ: minZ = tz
            if tz > maxZ: maxZ = tz
        return [minX,maxX,minY,maxY,minZ,maxZ]

    def box_center(self, box):
        """
        find the center of the box
        To use results as a cylinder: use box_center x,z with vertex y
        Game gems: can also do (min + max)/2 for each axis.
        """
        minX,maxX,minY,maxY,minZ,maxZ = box
        cx = (abs(minX-maxX)/2)+minX
        cy = (abs(minY-maxY)/2)+minY
        cz = (abs(minZ-maxZ)/2)+minZ
        return [cx,cy,cz]

    def normalize(self, myVec):
        myVec.normalize()
        return myVec

    def getUVBounds(self, uvs, single=False):
        """
        create bounding boxes
        """
        # box format is [minX,maxX,minY,maxY]
        minX = 1000000.0; maxX = -1000000.0
        minY = 1000000.0; maxY = -1000000.0
        if single:
            uvs = [uvs]
        for uvset in uvs:
            for i in range(len(uvset)):
                tx = uvset[i][0]
                ty = uvset[i][1]
                if tx < minX: minX = tx
                if tx > maxX: maxX = tx
                if ty < minY: minY = ty
                if ty > maxY: maxY = ty
        return [minX,maxX,minY,maxY]

    def fitUVs(self):
        bounds = self.getUVBounds(self.uvs)
        udist = bounds[0]
        vdist = bounds[2]
        for poly in self.uvs:
            for uv in poly:
                uv[0] -= udist
                uv[1] -= vdist
        bounds = self.getUVBounds(self.uvs)
        for poly in self.uvs:
            for uv in poly:
                uv[0] = uv[0]/bounds[1]
                uv[1] = uv[1]/bounds[3]

    def fitUVSingle(self,poly):
        bounds = self.getUVBounds(poly,single=1)
        udist = bounds[0]
        vdist = bounds[2]
        for uv in poly:
            uv[0] -= udist
            uv[1] -= vdist
        bounds = self.getUVBounds(poly,single=1)
        for uv in poly:
            uv[0] = uv[0]/bounds[1]
            uv[1] = uv[1]/bounds[3]

    def tile_map(self,verts,polys):
        self.box_map(verts,polys)
        for poly in self.uvs:
            self.fitUVSingle(poly)


    def planar_map(self, verts, polys, axis=1):
        """Create a planar map if there are no UVs.  Uses Panda Y (forward) axis by default."""
        bbox = self.getBounds(verts)
        if axis == 0:
            minx = bbox[2]
            maxx = bbox[3]
            miny = bbox[4]
            maxy = bbox[5]
            index1 = 1
            index2 = 2
        elif axis == 1:
            minx = bbox[0]
            maxx = bbox[1]
            miny = bbox[4]
            maxy = bbox[5]
            index1 = 0
            index2 = 2
        elif axis == 2:
            minx = bbox[0]
            maxx = bbox[1]
            miny = bbox[2]
            maxy = bbox[3]
            index1 = 0
            index2 = 1
        sizex = max(maxx - minx, 1)
        sizey = max(maxy - miny, 1)
        self.uvs = [[] for i in range(len(polys))]
        for poly_index in range(len(polys)):
            poly = polys[poly_index]
            for vi in poly:
                vert = verts[vi]
                u = (vert[index1] - minx)/sizex
                v = (vert[index2] - miny)/sizey
                self.uvs[poly_index].append([u,v])

    def box_map(self,verts,polys,inbounds=0):
        """
        Apply box-mapped UVs.
        Adapted from UV-mapping plugin for AC3D.
        http://www.inivis.com/supercoldmilk/ac3dplug/uvmap.html
        """
        bounds = self.getBounds(verts)
        nx,mx,ny,my,nz,mz = bounds
        szx = max(mx - nx,1)
        szy = max(my - ny,1)
        szz = max(mz - nz,1)
        self.uvs = []
        for pi in range(len(polys)):
            psets = polys[pi]
            edge1 = point_copy(verts[psets[1]]) - point_copy(verts[psets[0]])
            edge2 = point_copy(verts[psets[0]]) - point_copy(verts[psets[len(psets)-1]])
            norm = edge1.cross(edge2)
            norm = self.normalize(norm)
            axis = self.getAxis(norm)
            uvs = []
            for vi in psets:
                vert = verts[vi]
                if axis[0]:
                    u = (vert[2] - nz)/szz
                    v = (vert[1] - ny)/szy
                    u = -u
                    if norm[0] > 0.0:
                        u = -u
                elif axis[1]:
                    u = (vert[0] - nx)/szx
                    v = (vert[2] - nz)/szz
                    u = -u
                    v = -v
                    if norm[1] < 0.0:
                        u = -u
                else:
                    u = (vert[0] - nx)/szx
                    v = (vert[1] - ny)/szy
                    u = -u
                    if norm[2] < 0.0:
                        u = -u
                if inbounds:
                    u *= 0.5
                    v *= 0.5
                    u += 0.5
                    v += 0.5
                uvs.append([u,v])
            self.uvs.append(uvs)

    def cylinder_map(self,verts,polys,axis=2,fix_overlap=0):
        """
        Adapted from UV-mapping plugin for AC3D.
        http://www.inivis.com/supercoldmilk/ac3dplug/uvmap.html
        Create a cylindrical map if there are no UVs.
        Does not split poles/handle caps/split seams.
        """
        bounds = self.getBounds(verts)
        nx,mx,ny,my,nz,mz = bounds
        center = self.box_center(bounds)
        if axis == 0:
            north = [1.0,0.0,0.0]
            equator = [0.0,0.0,1.0]
            selheight = mx - nx
        elif axis == 2:
            north = [0.0,0.0,1.0]
            equator = [0.0,1.0,0.0]
            selheight = mz - nz
        else:
            north = [0.0,1.0,0.0]
            equator = [0.0,0.0,1.0]
            selheight = my - ny
        north = point_copy(north)
        equator = point_copy(equator)
        northequatorx = north.cross(equator)
        self.uvs = []

        for pi in range(len(polys)):
            psets = polys[pi]
            uvs = []
            for vi in psets:
                vert = point_copy(verts[vi])
                vcenter = point_copy(center)
                vcenter[axis] = vert[axis]
                vray = vert - vcenter
                vray = self.normalize(vray)
                phi = math.acos(north.dot(vray))
                if ((vray[axis] == 1.0) or (vray[axis] == -1.0)):
                    u = 0.5
                else:
                    u = math.acos(max(min(equator.dot(vray)/max(math.sin(phi),self.epsilon),1.0),-1.0)) / (2.0*math.pi + 0.5)
                    #if northequatorx.dot(vray) < 0.0: u = -u
                if axis == 0:
                    v = (vert[0] - nx)/selheight
                elif axis == 2:
                    v = (vert[2] - nz)/selheight
                else:
                    v = (vert[1] - ny)/selheight
                uvs.append([(u+0.5),v]) #uvs.append([(u+0.5),v])
            self.uvs.append(uvs)
            if fix_overlap:
                self.FixUVWrap(pi)

    def cylinder_map_caps(self,verts,polys,axis=2,fix_overlap=0):
        """
        Adapted from UV-mapping plugin for AC3D.
        http://www.inivis.com/supercoldmilk/ac3dplug/uvmap.html
        Create a cylindrical map if there are no UVs.
        """
        bounds = self.getBounds(verts)
        nx,mx,ny,my,nz,mz = bounds
        szx = max(mx - nx,1)
        szy = max(my - ny,1)
        szz = max(mz - nz,1)
        center = self.box_center(bounds)
        if axis == 0:
            north = [1.0,0.0,0.0]
            equator = [0.0,0.0,1.0]
            selheight = mx - nx
        elif axis == 2:
            north = [0.0,0.0,1.0]
            equator = [0.0,1.0,0.0]
            selheight = mz - nz
        else:
            north = [0.0,1.0,0.0]
            equator = [0.0,0.0,1.0]
            selheight = my - ny
        north = point_copy(north)
        equator = point_copy(equator)
        northequatorx = north.cross(equator)
        self.uvs = []

        for pi in range(len(polys)):
            psets = polys[pi]
            uvs = []
            fixuvs = False
            edge1 = point_copy(verts[psets[1]]) - point_copy(verts[psets[0]])
            edge2 = point_copy(verts[psets[0]]) - point_copy(verts[psets[len(psets)-1]])
            norm = edge1.cross(edge2)
            norm = self.normalize(norm)
            plane = self.getAxis(norm)
            for vi in psets:
                vert = point_copy(verts[vi])
                if plane[0] and axis == 0:
                    u = (vert[2] - nz)/szz
                    v = (vert[1] - ny)/szy
                elif plane[1] and axis == 1:
                    u = (vert[0] - nx)/szx
                    v = (vert[2] - nz)/szz
                elif plane[2] and axis == 2:
                    u = (vert[0] - nx)/szx
                    v = (vert[1] - ny)/szy
                else:
                    fixuvs = True
                    vcenter = point_copy(center)
                    vcenter[axis] = vert[axis]
                    vray = vert - vcenter
                    vray = self.normalize(vray)
                    phi = math.acos(north.dot(vray))
                    if ((vray[axis] == 1.0) or (vray[axis] == -1.0)):
                        u = 0.5
                    else:
                        u = math.acos(max(min(equator.dot(vray)/max(math.sin(phi),self.epsilon),1.0),-1.0)) / (2.0*math.pi) + 0.5
                        #if northequatorx.dot(vray) > 0.0: u = 1.0 - u
                    if axis == 0:
                        v = (vert[0] - nx)/selheight
                    elif axis == 2:
                        u = 1.0 - u
                        v = (vert[2] - nz)/selheight
                    else:
                        v = (vert[1] - ny)/selheight
                uvs.append([u,v])
            self.uvs.append(uvs)
            if fix_overlap and fixuvs:
                self.FixUVWrap(pi)

    def sphere_map(self,verts,polys,axis=2,fix_overlap=0,split_poles=0):
        """
        Create a spherical map if there are no UVs.
        http://www.inivis.com/supercoldmilk/ac3dplug/uvmap.html
        Doesn't split texverts at edges.
        """
        if axis == 0:
            north = [1,0,0]
            equator = [0,0,1]
        if axis == 1:
            north = [0,0,1]
            equator = [0,1,0]
        if axis == 2:
            north = [0,1,0]
            equator = [0,0,1]
        north = vector_copy(north)
        equator = vector_copy(equator)
        northequatorx = north.cross(equator)
        bbox = self.getBounds(verts)
        center = point_copy(self.box_center(bbox))
        self.uvs = [[] for i in range(len(polys))]
        for poly_index in range(len(polys)):
            poly = polys[poly_index]
            for vi in poly:
                vert = point_copy(verts[vi])
                vray = vert - center
                vray = self.normalize(vray)
                phi = math.acos(north.dot(vray))
                v = 1.0 - (phi/math.pi)
                if axis == 0 and (vray[0] == 1.0 or vray[0] == -1.0):
                    u = 0.5
                elif axis == 2 and (vray[1] == 1.0 or vray[1] == -1.0):
                    u = 0.5
                elif axis == 1 and (vray[2] == 1.0 or vray[2] == -1.0):
                    u = 0.5
                else:
                    u = math.acos(max(min(equator.dot(vray)/max(math.sin(phi),self.epsilon),1.0),-1.0)) / (2.0*math.pi) + 0.5
                    #if northequatorx.dot(vray) > 0.0: u = 1.0 - u

                self.uvs[poly_index].append([u,v])
            if fix_overlap:
                self.FixUVWrap(poly_index)
        if split_poles:
            self.SpacePolarCoordinates(polys, verts, axis, self.box_center(bbox))

    def FixUVWrap(self, poly_index):
        #===============================================================
        # Courtesy Andy Colebourne, with edits to get min/max tu:
        # check for overlaps in spherical mapping
        flag = 0
        uvs = self.uvs
        poly = self.uvs[poly_index]
        for uv1 in poly:
            for uv2 in poly:
                if 0.5 <= math.fabs(uv1[0] - uv2[0]):
                    flag |= 1

        minu = 100.0; maxu = -100.0
        if flag == 1:

            for uvi in range(len(poly)):
                uv = poly[uvi]
                if uv[0] < 0.5:
                    self.uvs[poly_index][uvi][0] += 1.0
                    uv[0] += 1.0
                    #print poly_index, uvi
                minu = min(uv[0], minu)
                maxu = max(uv[0], maxu)
        #===============================================================
        # Pull texture coordinates back if over 1/2 of the horizontal bounds is past 1.0
        if 1.0 - minu < maxu - 1.0:
            for uvi in range(len(poly)):
                uv = poly[uvi]
                self.uvs[poly_index][uvi][0] -= 1.0

    def SpacePolarCoordinates(self, polys, verts, axis, vcenter):
        for poly_index in range(len(polys)):
            poly = polys[poly_index]
            uvs = self.uvs[poly_index]
            for uvi in range(len(poly)):
                v = verts[poly[uvi]]
                polar = False
                if axis == 0:
                    # X axis
                    if math.fabs(vcenter[1] - v[1]) < self.epsilon and math.fabs(vcenter[2] - v[2]) < self.epsilon:
                        polar = True
                elif axis == 1: # Y and Z need to be flipped for Panda compatability -- here, but not in sphere_map.
                    # Z axis
                    if math.fabs(vcenter[1] - v[1]) < self.epsilon and math.fabs(vcenter[0] - v[0]) < self.epsilon:
                        polar = True
                else:
                    # Y axis
                    if math.fabs(vcenter[0] - v[0]) < self.epsilon and math.fabs(vcenter[2] - v[2]) < self.epsilon:
                        polar = True
                if polar:
                    # Move the horizontal UV to the unweighted center
                    first = True
                    for uvi2 in range(len(poly)):
                        if uvi2 == uvi:
                            continue
                        uv = uvs[uvi2]
                        if first:
                            tumin = uv[0]
                            tumax = uv[0]
                            first = False
                        else:
                            tumin = min(tumin,uv[0])
                            tumax = max(tumax,uv[0])
                        # Ensure we read at least one entry (!first)
                        if not first:
                            self.uvs[poly_index][uvi][0] = tumin + ((tumax - tumin) * 0.5)


    def global_map(self, verts, polys, scale=1.0, offset=0.0, rotation=0.0):
        # Front UVs are flipped?
        """
        Adapted from UV-mapping plugin for AC3D.
        http://www.inivis.com/supercoldmilk/ac3dplug/uvmap.html
        """
        self.uvs = []
        scale = 1.0/scale
        rotating = math.fabs(rotation) > 0.00001
        if rotating:
            rotcos = math.cos( math.radians(rotation))
            rotsin = math.sin( math.radians(rotation))
        for pi in range(len(polys)):
            psets = polys[pi]
            edge1 = point_copy(verts[psets[1]]) - point_copy(verts[psets[0]])
            edge2 = point_copy(verts[psets[0]]) - point_copy(verts[psets[len(psets)-1]])
            norm = edge1.cross(edge2)
            norm = self.normalize(norm)
            normx = 1
            normy = 1
            axis = self.getAxis(norm)
            ptv = []
            uvs = []
            for vi in psets:
                vert = verts[vi]
                if axis[0]:
                    u = vert[2]
                    v = vert[1]
                    if norm[0] > 0.0:
                        u = -u
                elif axis[1]:
                    u = vert[0]
                    v = vert[2]
                    if norm[1] < 0.0:
                        v = -v
                else:
                    u = vert[0]
                    v = vert[1]
                    if norm[2] < 0.0:
                        u = -u
                if (u < 1.0) and (u > -1.0):
                    normx = 0
                if (v < 1.0) and (v > -1.0):
                    normy = 0
                if rotating:
                    tvx = u  # keep an uncorrupted copy
                    u = (u * rotcos) - (tverty * rotsin)
                    v = (tvx * rotsin) + (tverty * rotcos)
                u = (u * scale) + offset
                v = (v * scale) + offset
                ptv.append([u,v])
            if normx or normy:
                absx = 0.0
                u = ptv[0][0]
                if u > 1.0:
                    absx = math.floor(u)
                else:
                    absx = math.ceil(u)
                absy = 0.0
                v = ptv[0][1]
                if v > 1.0:
                    absy = math.floor(v)
                else:
                    absy = math.ceil(v)
                for uvi in range(1,len(ptv)):
                    u,v = ptv[uvi]
                    if normx:
                        if math.fabs(u) < math.fabs(absx):
                            if u > 1.0:
                                absx = math.floor(u)
                            else:
                                absx = math.ceil(u)
                    if normy:
                        if math.fabs(v) < math.fabs(absy):
                            if v > 1.0:
                                absy = math.floor(v)
                            else:
                                absy = math.ceil(v)
                for uvi in range(len(ptv)):
                    ptv[uvi][0] -= absx
                    ptv[uvi][1] -= absy
            for u,v in ptv:
                #uvs.append([-(u+0.5)*0.5,v*0.5])
                #uvs.append([-(u+0.5),v])
                uvs.append([u,v])
            self.uvs.append(uvs)


#def create_mesh(parentnp, debug=False, invert=False, width=32):
def create_mesh(debug=False, invert=False, width=32):
    """This creates a simple 17x17 grid mesh for the sides of our cube.
    The ultimate goal is to use a LOD system, probably based on quadtrees.
    If debug is true then we get a color gradient on our vertexes.

    From http://www.panda3d.org/forums/viewtopic.php?f=8&t=16930&p=98241"""

    # Vertex coord stepsize for given length in quads
    width_size = 2 / width
    # We are going to process verts in groups of 4
    step_size = width_size * 2
    verts = []
    polys = []
    vnorms = []
    for y in frange(-1, 1 + width_size, width_size):
        for x in frange(-1, 1 + width_size, width_size):
            verts.append([x, y, 1])

    for y in range(0, width):
        for x in range(0, width):
            v = (width + 1) * y + x
            polys.append([v, v+1, v+width+1])
            polys.append([v+1, v+width+2, v+width+1])


    geom = myGeom(verts=verts, polys=polys)
    geom.build()

    return geom.geomnode

mesh_node = create_mesh(debug=False, invert=False)


def create_side(parent_nodepath, debug=False, invert=False):
    mnode = GeomNode('quadface')
    mnode.add_geoms_from(mesh_node)
    return parent_nodepath.attach_new_node(mnode)


class Body(object):
    """Generic class for normalized cube celestial bodies with NodePath like
    interfaces."""

    def __init__(self, name, scale=1, debug=False):
        """Debug will generate colored pixels for fun time. self.init()
        is called for specific body type inits."""
        self.name = name
        self.node_path = NodePath(name)
        self.sides = []
        for i in range(0, 6):
            m = create_side(self.node_path, debug, invert=True)
            m.set_scale(scale)
            self.sides.append(m)

        '''The side meshes are rotated here. They are moved to their correct
        position in the shader.'''
        self.sides[0].set_hpr(90, 90, 0)
        self.sides[1].set_hpr(-90, 90, 0)
        self.sides[2].set_hpr(0, 0, 0)
        self.sides[3].set_hpr(0, 180, 0)
        self.sides[4].set_hpr(0, 90, 0)
        self.sides[5].set_hpr(180, 90, 0)
        base.accept('h', self.node_path.hide)
        base.accept('j', self.node_path.show)
        self.init()

    def get_name(self):
        return self.name

    def init(self):
        raise NotImplementedError()

    def get_pos(self):
        return self.node_path.get_pos()

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


class Surface(Body):
    """Planet is a parent nodepath that the 6 side mesh nodepaths will parent
    to. Planet can be moved, scale, and rotated with no problems"""

    def init(self):
        # create sane material defaults
        self.material = Material()
        self.material.set_diffuse(VBase4(1.0, 1.0, 1.0, 1.0))
        #self.material.set_ambient(VBase4(1.0, 1.0, 1.0, 1.0))
        self.material.set_emission(VBase4(0.0, 0.0, 0.0, 1.0))
        self.material.set_shininess(1)
        self.material.set_specular(VBase4(0.5, 0.0, 0.0, 1.0))

        #tex = Texture()
        for m in self.sides:
            m.set_material(self.material)
            '''m.set_shader_input('colorTexture', tex)
            m.set_shader_input('nightTesture', tex)
            m.set_shader_input('glossTexture', tex)'''
        self.load_shaders()

    def load_shaders(self):
        shaders = BetterShader.load('Shader/Planet/surface_vertex.glsl',
                                    'Shader/Planet/surface_fragment.glsl',
                                    '',
                                    "Shader/DefaultObjectShader/tesscontrol.glsl",
                                    "Shader/DefaultObjectShader/tesseval.glsl")
        convertToPatches(self.node_path)
        for m in self.sides:
            m.set_shader(shaders)

    def set_texture(self, texture_path):
        """Textures the surface. texture_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The orientation
        is a little different than what is described in the panda manual.

        North pole is z-up."""
        for i in range(0, 6):
            self.sides[i].setShaderInput('colorTexture',
                                         loader.loadTexture(
                                             texture_path.replace('#',
                                                                  str(i))))

    def set_textures(self, texture_paths={}):
        """MultiTextures the surface. t_path is a string in the same format as
        loader.loadCubeMap('texture_#.png') for a multifile cubemap. The
        orientation is a little different than what is described in the panda
        manual.

        North pole is z-up."""
        for i in range(0, 6):
            diffuse = sandbox.base.loader.loadTexture(texture_paths['diffuse'].replace('#',
                                                                           str(i)))
            diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
            diffuse.setAnisotropicDegree(4)
            self.sides[i].set_texture(diffuse)
            normal = sandbox.base.loader.loadTexture('Data/Textures/EmptyNormalTexture.png')
            normalts = TextureStage('normalts')
            self.sides[i].set_texture(normalts, normal)
            if 'specular' in texture_paths:
                specular = sandbox.base.loader.loadTexture(texture_paths['specular'].replace('#',
                                                                           str(i)))
            else:
                specular = sandbox.base.loader.loadTexture('Data/Textures/EmptySpecularTexture.png')
            spects = TextureStage('spects')
            self.sides[i].set_texture(spects, specular)
            roughness = sandbox.base.loader.loadTexture('Data/Textures/EmptyRoughnessTexture.png')
            roughts= TextureStage('roughts')
            self.sides[i].set_texture(roughts, roughness)
            '''if 'night' in texture_paths:
                self.sides[i].set_shader_input('nightTexture',
                                               sandbox.base.loader.loadTexture(
                                                   texture_paths['night'].replace('#',
                                                                      str(i))))'''
            '''self.sides[i].set_shader_input('colorTexture', texture)
            if night_path:
                self.sides[i].set_shader_input('nightTesture',
                                               loader.loadTexture(
                                                   night_path.replace('#',
                                                                      str(i))))
            if gloss_path:
                self.sides[i].set_shader_input('glossTexture',
                                               loader.loadTexture(
                                                   gloss_path.replace('#',
                                                                      str(i))))'''
        self.load_shaders()

    def set_ambient(self, r, g, b, a):
        self.material.set_ambient(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_diffuse(self, r, g, b, a):
        self.material.set_diffuse(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_specular(self, r, g, b, a):
        self.material.set_specular(
            VBase4(float(r), float(g), float(b), float(a)))

    def set_shininess(self, n):
        self.material.set_shininess(n)


def make_star(name='star', scale=1, color=Vec3(1), texture_size=64, debug=False):
    card_maker = CardMaker(name)
    card_maker.set_frame(-1, 1, -1, 1)
    node_path = NodePath(name)
    node = card_maker.generate()
    final_node_path = node_path.attach_new_node(node)
    final_node_path.set_billboard_point_eye()
    path = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(path, 'spacedrive', 'Shader', 'Star')
    shaders = BetterShader.load(os.path.join(path, 'vertex.glsl'),
                                os.path.join(path, 'fragment.glsl'))
    final_node_path.set_shader_input('cameraSpherePos', 1, 1, 1)
    final_node_path.set_shader_input('sphereRadius', 1.0)
    final_node_path.set_shader_input('myCamera', base.camera)
    final_node_path.set_shader(shaders)
    final_node_path.set_shader_input('blackbody', color)
    material = Material()
    material.set_emission(VBase4(color, 1.0))
    final_node_path.set_material(material)
    xn = PerlinNoise3(0.5, 0.5, 0.5)
    #yn = PerlinNoise3(0.5, 0.5, 0.5)
    texture = Texture('star')
    texture.setup_3d_texture()
    for z in range(texture_size):
        p = PNMImage(texture_size, texture_size)
        for y in range(texture_size):
            for x in range(texture_size):
                p.set_gray(x, y, abs(xn.noise(x, y, z)))
        texture.load(p, z, 0)
    diffuse = texture
    diffuse.setMinfilter(Texture.FTLinearMipmapLinear)
    diffuse.setAnisotropicDegree(4)
    final_node_path.set_texture(diffuse)
    normal = sandbox.base.loader.loadTexture('Data/Textures/EmptyNormalTexture.png')
    normalts = TextureStage('normalts')
    final_node_path.set_texture(normalts, normal)
    specular = sandbox.base.loader.loadTexture('Data/Textures/EmptySpecularTexture.png')
    spects = TextureStage('spects')
    final_node_path.set_texture(spects, specular)
    roughness = sandbox.base.loader.loadTexture('Data/Textures/EmptyRoughnessTexture.png')
    roughts= TextureStage('roughts')
    final_node_path.set_texture(roughts, roughness)
    return final_node_path


def make_planet(name='planet', scale=1, debug=False):
    return Surface(name, scale, debug)
