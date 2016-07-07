# https://bitbucket.org/soos/panda-procedural/src/2f2aa630e424c7872f0e06c0c4394d7997f655ff/procedural.py?at=master
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from panda3d.core import Geom, GeomNode, GeomPoints, GeomVertexData
from panda3d.core import GeomVertexFormat, GeomTriangles, GeomVertexWriter
from panda3d.core import NodePath, Quat, VBase3, Vec3
import math
from math import *


def empty(prefix, points=False):
    path = NodePath(prefix + '_path')
    node = GeomNode(prefix + '_node')
    path.attachNewNode(node)

    gvd = GeomVertexData('gvd', GeomVertexFormat.getV3n3t2(), Geom.UHStatic)
    geom = Geom(gvd)
    gvw = GeomVertexWriter(gvd, b'vertex')
    gnw = GeomVertexWriter(gvd, b'normal')
    gtw = GeomVertexWriter(gvd, b'texcoord')
    node.addGeom(geom)
    if points:
        prim = GeomPoints(Geom.UHStatic)
    else:
        prim = GeomTriangles(Geom.UHStatic)
    return (gvw, gnw, gtw, prim, geom, path)


def IcoSphere(radius=1, subdivisions=1):
    (gvw, gnw, gtw, prim, geom, path) = empty('ico')

    verts = []

    phi = .5 * (1. + sqrt(5.))
    invnorm = 1 / sqrt(phi * phi + 1)

    verts.append(Vec3(-1, phi, 0) * invnorm)  # 0
    verts.append(Vec3(1, phi, 0) * invnorm)  # 1
    verts.append(Vec3(0, 1, -phi) * invnorm)  # 2
    verts.append(Vec3(0, 1, phi) * invnorm)  # 3
    verts.append(Vec3(-phi, 0, -1) * invnorm)  # 4
    verts.append(Vec3(-phi, 0, 1) * invnorm)  # 5
    verts.append(Vec3(phi, 0, -1) * invnorm)  # 6
    verts.append(Vec3(phi, 0, 1) * invnorm)  # 7
    verts.append(Vec3(0, -1, -phi) * invnorm)  # 8
    verts.append(Vec3(0, -1, phi) * invnorm)  # 9
    verts.append(Vec3(-1, -phi, 0) * invnorm)  # 10
    verts.append(Vec3(1, -phi, 0) * invnorm)  # 11

    faces = [
        0, 1, 2,
        0, 3, 1,
        0, 4, 5,
        1, 7, 6,
        1, 6, 2,
        1, 3, 7,
        0, 2, 4,
        0, 5, 3,
        2, 6, 8,
        2, 8, 4,
        3, 5, 9,
        3, 9, 7,
        11, 6, 7,
        10, 5, 4,
        10, 4, 8,
        10, 9, 5,
        11, 8, 6,
        11, 7, 9,
        10, 8, 11,
        10, 11, 9
    ]

    size = 60

    # Step 2 : tessellate
    for subdivision in range(0, subdivisions):
        size *= 4;
        newFaces = []
        for i in range(0, int(size / 12)):
            i1 = faces[i * 3]
            i2 = faces[i * 3 + 1]
            i3 = faces[i * 3 + 2]
            i12 = len(verts)
            i23 = i12 + 1
            i13 = i12 + 2
            v1 = verts[i1]
            v2 = verts[i2]
            v3 = verts[i3]
            # make 1 vertice at the center of each edge and project it onto the sphere
            vt = v1 + v2
            vt.normalize()
            verts.append(vt)
            vt = v2 + v3
            vt.normalize()
            verts.append(vt)
            vt = v1 + v3
            vt.normalize()
            verts.append(vt)
            # now recreate indices
            newFaces.append(i1)
            newFaces.append(i12)
            newFaces.append(i13)
            newFaces.append(i2)
            newFaces.append(i23)
            newFaces.append(i12)
            newFaces.append(i3)
            newFaces.append(i13)
            newFaces.append(i23)
            newFaces.append(i12)
            newFaces.append(i23)
            newFaces.append(i13)
        faces = newFaces

    for i in range(0, len(verts)):
        gvw.addData3f(VBase3(verts[i]))
        gnw.addData3f(*verts[i])
        #Calculate texture coords
        x, y, z = verts[i]
        b = 1.0 / (2.0 * phi) / 0.587785243988
        u = -((math.atan2(x, y)) / math.pi) / 2.0 + 0.5
        v = (z / b) / 2.0 + 0.5
        gtw.add_data2f(*[u, v])
    for i in range(0, int(len(faces) / 3)):
        prim.addVertices(faces[i * 3], faces[i * 3 + 1], faces[i * 3 + 2])

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path

########################################################################

Vec3_ZERO = Vec3(0, 0, 0)


def getRotationTo(src, dest, fallbackAxis=Vec3_ZERO):
    # Quaternion q;
    # Vector3 v0 = *this;
    # Vector3 v1 = dest;
    # v0.normalise();
    # v1.normalise();
    q = Quat()
    v0 = Vec3(src)
    v1 = Vec3(dest)
    v0.normalize()
    v1.normalize()

    # Real d = v0.dotProduct(v1);
    d = v0.dot(v1)

    # if (d >= 1.0f)
    # {
    # return Quaternion::IDENTITY;
    # }
    if d >= 1.0:
        return Quat(1, 0, 0, 0)

    # if (d < (1e-6f - 1.0f))
    if d < (1.0e-6 - 1.0):
        # if (fallbackAxis != Vector3::ZERO)
        # {
        # // rotate 180 degrees about the fallback axis
        # q.FromAngleAxis(Radian(Math::PI), fallbackAxis);
        # }
        if fallbackAxis != Vec3_ZERO:
            q.setFromAxisAngleRad(pi, fallbackAxis)
        # else
        # {
        # // Generate an axis
        # Vector3 axis = Vector3::UNIT_X.crossProduct(*this);
        # if (axis.isZeroLength()) // pick another if colinear
        # axis = Vector3::UNIT_Y.crossProduct(*this);
        # axis.normalise();
        # q.FromAngleAxis(Radian(Math::PI), axis);
        # }
        else:
            axis = Vec3(1, 0, 0).cross(src)
            if axis.almostEqual(Vec3.zero()):
                axis = Vec3(0, 1, 0).cross(src)
            axis.normalize()
            q.setFromAxisAngleRad(pi, axis)
        # else
        # {
        # Real s = Math::Sqrt( (1+d)*2 );
        # Real invs = 1 / s;

        # Vector3 c = v0.crossProduct(v1);

        # q.x = c.x * invs;
        # q.y = c.y * invs;
        # q.z = c.z * invs;
        # q.w = s * 0.5f;
        # q.normalise();
    # }
    else:
        s = sqrt((1 + d) * 2)
        invs = 1 / s
        c = v0.cross(v1)
        q.setI(c.x * invs)
        q.setJ(c.y * invs)
        q.setK(c.z * invs)
        q.setR(s * .5)
        q.normalize()
    return q


def computeQuaternion(direction):
    # Quaternion quat = Vector3::UNIT_Z.getRotationTo(direction);
    quat = getRotationTo(Vec3(0, 0, 1), direction)
    projectedY = Vec3(0, 1, 0) - direction * Vec3(0, 1, 0).dot(direction)
    tY = quat.xform(Vec3(0, 1, 0))
    quat2 = getRotationTo(tY, projectedY)
    q = quat2 * quat
    return q


########################################################################

def TorusKnot(mRadius=1., mSectionRadius=.2, mP=2, mQ=3, mNumSegSection=64,
              mNumSegCircle=64):
    (gvw, prim, geom, path) = empty('tk')

    offset = 0

    for i in range(0, mNumSegCircle * mP + 1):
        phi = pi * 2 * i / mNumSegCircle
        x0 = mRadius * (2 + cos(mQ * phi / mP)) * cos(phi) / 3.
        y0 = mRadius * sin(mQ * phi / mP) / 3.
        z0 = mRadius * (2 + cos(mQ * phi / mP)) * sin(phi) / 3.

        phi1 = pi * 2 * (i + 1) / mNumSegCircle
        x1 = mRadius * (2 + cos(mQ * phi1 / mP)) * cos(phi1) / 3.
        y1 = mRadius * sin(mQ * phi1 / mP) / 3.
        z1 = mRadius * (2 + cos(mQ * phi1 / mP)) * sin(phi1) / 3.

        v0 = Vec3(x0, y0, z0)
        v1 = Vec3(x1, y1, z1)
        direction = v1 - v0
        direction.normalize()

        q = computeQuaternion(direction)

        for j in range(0, mNumSegSection + 1):
            alpha = pi * 2 * j / mNumSegSection
            vp = q.xform(Vec3(cos(alpha), sin(alpha), 0)) * mSectionRadius
            gvw.addData3f(v0 + vp)

            if i != mNumSegCircle * mP:
                prim.addVertices(offset + mNumSegSection + 1,
                                 offset + mNumSegSection, offset)
                prim.addVertices(offset + mNumSegSection + 1, offset,
                                 offset + 1)
            offset += 1

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path


########################################################################

def Torus(mNumSegSection=64, mNumSegCircle=64, mRadius=1.0,
          mSectionRadius=0.2):
    (gvw, prim, geom, path) = empty('t')

    deltaSection = (pi * 2 / mNumSegSection)
    deltaCircle = (pi * 2 / mNumSegCircle)

    offset = 0

    for i in range(0, mNumSegCircle + 1):
        for j in range(0, mNumSegSection + 1):
            v0 = Vec3(mRadius + mSectionRadius * cos(j * deltaSection),
                      mSectionRadius * sin(j * deltaSection), 0.0)
            q = Quat()
            q.setFromAxisAngleRad(i * deltaCircle, Vec3(0, 1, 0))
            v = q.xform(v0)

            gvw.addData3f(v)

            if i != mNumSegCircle:
                prim.addVertices(offset + mNumSegSection + 1, offset,
                                 offset + mNumSegSection)
                prim.addVertices(offset + mNumSegSection + 1, offset + 1,
                                 offset)
            offset += 1

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path


########################################################################

#  1  1  1 (0)   -1  1 -1 (1)    1 -1 -1 (2)
# -1  1 -1 (1)   -1 -1  1 (3)    1 -1 -1 (2)
#  1  1  1 (0)    1 -1 -1 (2)   -1 -1  1 (3)
#  1  1  1 (0)   -1 -1  1 (3)   -1  1 -1 (1)

def Tetrahedron():
    (gvw, prim, geom, path) = empty('tetra')

    verts = [(1., 1., 1.), (-1., 1., -1.), (1., -1., -1.), (-1., -1., 1.)]
    faces = [(0, 1, 2), (1, 3, 2), (0, 2, 3), (0, 3, 1)]

    for i in range(0, len(verts)):
        gvw.addData3f(VBase3(verts[i][0], verts[i][1], verts[i][2]))
    for i in range(0, len(faces)):
        prim.addVertices(faces[i][0], faces[i][1], faces[i][2])

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path


########################################################################

# -a  0  a (0)   -a  0 -a (1)    0  b  0 (2)
# -a  0 -a (1)    a  0 -a (3)    0  b  0 (2)
#  a  0 -a (3)    a  0  a (4)    0  b  0 (2)
#  a  0  a (4)   -a  0  a (0)    0  b  0 (2)
#  a  0 -a (3)   -a  0 -a (1)    0 -b  0 (5)
# -a  0 -a (1)   -a  0  a (0)    0 -b  0 (5)
#  a  0  a (4)    a  0 -a (3)    0 -b  0 (5)
# -a  0  a (0)    a  0  a (4)    0 -b  0 (5)

def Octahedron():
    (gvw, prim, geom, path) = empty('octa')

    a = 1. / (2. * sqrt(2.))
    b = 1. / 2.

    verts = [(-a, 0., a), (-a, 0., -a), (0., b, 0.), (a, 0., -a), (a, 0., a),
             (0., -b, 0.)]
    faces = [(0, 1, 2), (1, 3, 2), (3, 4, 2), (4, 0, 2), (3, 1, 5), (1, 0, 5),
             (4, 3, 5), (0, 4, 5)]

    for i in range(0, len(verts)):
        gvw.addData3f(VBase3(verts[i][0], verts[i][1], verts[i][2]))
    for i in range(0, len(faces)):
        prim.addVertices(faces[i][0], faces[i][1], faces[i][2])

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path


########################################################################

# Hexahedron (cube)
# -1 -1 -1    1 -1 -1    1 -1  1   -1 -1  1
# -1 -1 -1   -1 -1  1   -1  1  1   -1  1 -1
# -1 -1  1    1 -1  1    1  1  1   -1  1  1
# -1  1 -1   -1  1  1    1  1  1    1  1 -1
#  1 -1 -1    1  1 -1    1  1  1    1 -1  1
# -1 -1 -1   -1  1 -1    1  1 -1    1 -1 -1

# Divide each vertex by 2

########################################################################

# Icosahedron
#  0  b -a    b  a  0   -b  a  0
#  0  b  a   -b  a  0    b  a  0
#  0  b  a    0 -b  a   -a  0  b
#  0  b  a    a  0  b    0 -b  a
#  0  b -a    0 -b -a    a  0 -b
#  0  b -a   -a  0 -b    0 -b -a
#  0 -b  a    b -a  0   -b -a  0
#  0 -b -a   -b -a  0    b -a  0
# -b  a  0   -a  0  b   -a  0 -b
# -b -a  0   -a  0 -b   -a  0  b
#  b  a  0    a  0 -b    a  0  b
#  b -a  0    a  0  b    a  0 -b
#  0  b  a   -a  0  b   -b  a  0
#  0  b  a    b  a  0    a  0  b
#  0  b -a   -b  a  0   -a  0 -b
#  0  b -a    a  0 -b    b  a  0
#  0 -b -a   -a  0 -b   -b -a  0
#  0 -b -a    b -a  0    a  0 -b
#  0 -b  a   -b -a  0   -a  0  b
#  0 -b  a    a  0  b    b -a  0

# a = 1 / 2
# b = 1 / (2 * phi)
# phi = (1 + sqrt(5)) / 2

# v1       0  b -a
# v2       b  a  0
# v3      -b  a  0
# v4       0  b  a
# v5       0 -b  a
# v6      -a  0  b
# v7       0 -b -a
# v8       a  0 -b
# v9       a  0  b
# v10     -a  0 -b
# v11      b -a  0
# v12     -b -a  0

# f1       v1    v2    v3
# f2       v4    v3    v2
# f3       v4    v5    v6
# f4       v4    v9    v5
# f5       v1    v7    v8
# f6       v1    v10   v7
# f7       v5    v11   v12
# f8       v7    v12   v11
# f9       v3    v6    v10
# f10      v12   v10   v6
# f11      v2    v8    v9
# f12      v11   v9    v8
# f13      v4    v6    v3
# f14      v4    v2    v9
# f15      v1    v3    v10
# f16      v1    v8    v2
# f17      v7    v10   v12
# f18      v7    v11   v8
# f19      v5    v12   v6
# f20      v5    v9    v11

########################################################################

# Dodecahedron

#  c  0  1 (0)   -c  0  1 (1)   -b  b  b (12)    0  1  c (5)    b  b  b (16)
# -c  0  1 (1)    c  0  1 (0)    b -b  b (13)    0 -1  c (7)   -b -b  b (18)
#  c  0 -1 (2)   -c  0 -1 (3)   -b -b -b (14)    0 -1 -c (6)    b -b -b (19)
# -c  0 -1 (3)    c  0 -1 (2)    b  b -b (15)    0  1 -c (4)   -b  b -b (17)
#  0  1 -c (4)    0  1  c (5)    b  b  b (16)    1  c  0 (8)    b  b -b (15)
#  0  1  c (5)    0  1 -c (4)   -b  b -b (17)   -1  c  0 (10)  -b  b  b (12)
#  0 -1 -c (6)    0 -1  c (7)   -b -b  b (18)   -1 -c  0 (11)  -b -b -b (14)
#  0 -1  c (7)    0 -1 -c (6)    b -b -b (19)    1 -c  0 (9)    b -b  b (13)
#  1  c  0 (8)    1 -c  0 (9)    b -b  b (13)    c  0  1 (0)    b  b  b (16)
#  1 -c  0 (9)    1  c  0 (8)    b  b -b (15)    c  0 -1 (2)    b -b -b (19)
# -1  c  0 (10)  -1 -c  0 (11)  -b -b -b (14)   -c  0 -1 (3)   -b  b -b (17)
# -1 -c  0 (11)  -1  c  0 (10)  -b  b  b (12)   -c  0  1 (1)   -b -b  b (18)

# b = 1 / phi 
# c = 2 - phi

# Divide each coordinate by 2

def Dodecahedron():
    (gvw, prim, geom, path) = empty('dodeca')

    phi = (1. + sqrt(5.)) / 2.
    b = 1. / phi
    c = 2. - phi

    verts = [
        (c, 0, 1),
        (-c, 0, 1),
        (c, 0, -1),
        (-c, 0, -1),
        (0, 1, -c),
        (0, 1, c),
        (0, -1, -c),
        (0, -1, c),
        (1, c, 0),
        (1, -c, 0),
        (-1, c, 0),
        (-1, -c, 0),
        (-b, b, b),
        (b, -b, b),
        (-b, -b, -b),
        (b, b, -b),
        (b, b, b),
        (-b, b, -b),
        (-b, -b, b),
        (b, -b, -b),
        (b, -b, b),
        (b, b, -b),
        (-b, -b, -b),
        (-b, b, b)]

    faces = [
        (16, 5, 12, 1, 0),
        (18, 7, 13, 0, 1),
        (19, 6, 14, 3, 2),
        (17, 4, 15, 2, 3),
        (4, 5, 16, 8, 15),
        (5, 4, 17, 10, 12),
        (6, 7, 18, 11, 14),
        (7, 6, 19, 9, 13),
        (16, 0, 13, 9, 8),
        (19, 2, 15, 8, 9),
        (17, 3, 14, 11, 10),
        (18, 1, 12, 10, 11)]

    for i in range(0, len(verts)):
        gvw.addData3f(VBase3(verts[i][0], verts[i][1], verts[i][2]))
    for i in range(0, len(faces)):
        prim.addVertices(faces[i][0], faces[i][1], faces[i][2])
        prim.addVertices(faces[i][0], faces[i][2], faces[i][4])
        prim.addVertices(faces[i][4], faces[i][2], faces[i][3])

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path


########################################################################

# Limpet Torus

# x = cos(u) / [sqrt(2) + sin(v)]
# y = sin(u) / [sqrt(2) + sin(v)]
# z = 1 / [sqrt(2) + cos(v)]

def LimpetTorus(u=32, v=64):
    (gvw, prim, geom, path) = empty('lt', True)

    du = 2. * pi / u
    dv = 8. / v
    ui = 0.
    offset = 0

    for i in range(0, u + 1):
        vi = -4.
        for j in range(0, v + 1):
            x = cos(ui) / (sqrt(2.) + sin(vi))
            y = sin(ui) / (sqrt(2.) + sin(vi))
            z = 1 / (sqrt(2.) + cos(vi))

            gvw.addData3f(VBase3(x, y, z))

            if i != u:
                #				prim.addVertices(offset + v + 1, offset, offset + v)
                #				prim.addVertices(offset + v + 1, offset + 1, offset)
                prim.addVertices(offset + v, offset, offset + v + 1)
                prim.addVertices(offset, offset + 1, offset + v + 1)
            offset += 1

            vi += dv
        ui += du

    prim.closePrimitive()
    geom.addPrimitive(prim)

    return path

########################################################################

# Dini's Surface or Twisted Pseudosphere

# x = a cos(u) sin(v)
# y = a sin(u) sin(v)
# z = a (cos(v) + log(tan(v/2))) + b u
# 0 <= u, 0 < v

# def TwistedPseudosphere():
# prefix = 'tp'
# path = NodePath(prefix + '_path')
# node = GeomNode(prefix + '_node')
# path.attachNewNode(node)

# gvd = GeomVertexData('gvd', GeomVertexFormat.getV3(), Geom.UHStatic)
# geom = Geom(gvd)
# gvw = GeomVertexWriter(gvd, 'vertex')
# node.addGeom(geom)
# prim = GeomLines(Geom.UHStatic)

# i = 0
# for u in range(0,628,5):
# for v in range(1,400,5):
# a = 1.
# b = 1.
# x = a * cos(u/100.)*sin(v/100.)
# y = a * sin(u/100.)*sin(v/100.)
# z = a * (cos(v/100.) + log(tan((v/2.)/100.))) + b * u

# gvw.addData3f(VBase3(x,y,z))
# gvw.addData3f(VBase3(x,y+.001,z))
# gvw.addData3f(VBase3(x,y,z+.001))
# prim.addVertices(i, i+1, i+2)
# i += 3

# prim.closePrimitive()
# geom.addPrimitive(prim)

# return path

########################################################################

# Elliptic Torus

# x = (c + cos(v)) cos(u)
# y = (c + cos(v)) sin(u)
# z = sin(v) + cos(v)

# -pi <= u,v <= pi 
# cool with c > 1

########################################################################

# UV Sphere

# x = cos(theta) cos(phi)
# y = cos(theta) sin(phi)
# z = sin(theta)

# where:
# -90 <= theta <= 90
# 0 <= phi <= 360

# every face is:
# (theta,phi)
# (theta+dtheta,phi)
# (theta+dtheta,phi+dphi)
# (theta,phi+dphi)
# where dtheta and dphi is deltas
