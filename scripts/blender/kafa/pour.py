"""Kafa skrol-sajt, poglavlje 2 · POUR.

Stakleni bokal (kao Hario server) sa V60 dripperom od providnog stakla i belim papirnim filterom.
Gooseneck kuvalo od tamnijeg brušenog inoxa gore desno sipa tanak mlaz u centar filtera, para se diže,
kafa curi iz drippera i nivo u bokalu raste. Pored bokala su dva zrna na podu.

Dogovor scena: metri, pod na z=0, centar drippera tačno na x=0, y=0 (tu upadaju zrna iz GRIND),
kamera spreda (-Y) ~10° odozgo, 85 mm, kadar 1:1, providna pozadina.

Pokretanje iz korena repoa:
  unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \\
    -P scripts/blender/kafa/pour.py -- --out <folder> [--kadrovi 120] [--render proba|sve|1,60,120] \\
    [--res 1600] [--uzorci 64] [--poster 90] [--para ravni|volumen]
"""
import argparse
import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

TRAJANJE = 4.0          # sekundi "fizičkog" vremena za celu sekvencu (ne zavisi od broja kadrova)
TAN30 = math.tan(math.radians(30))

# ---------------------------------------------------------------------------- mere (m)
SERVER_PROFIL = [  # spoljna kontura bokala (r, z), od centra dna nagore
    (0.000, 0.000), (0.028, 0.000), (0.038, 0.0015), (0.0445, 0.005), (0.0485, 0.011),
    (0.0505, 0.020), (0.0512, 0.032), (0.0508, 0.044), (0.0490, 0.058), (0.0462, 0.072),
    (0.0430, 0.085), (0.0405, 0.096), (0.0392, 0.104), (0.0392, 0.110), (0.0405, 0.115),
    (0.0420, 0.118),
]
SERVER_DEBLJINA = 0.0022
PLOCA_Z = (0.1185, 0.1235)      # donja i gornja strana staklene ploče drippera
KONUS_R0 = 0.0085               # unutrašnji poluprečnik konusa na dnu (otvor)
KONUS_Z1 = 0.2035               # gornja ivica konusa
FILTER_RAZMAK = 0.0022          # papir je toliko odmaknut od stakla (rebra su između)
FILTER_VRH = 0.1126             # vrh papirnog konusa (viri kroz otvor, kao pravi V60 filter)
NIVO_DRIPPER = 0.188            # površina kafe u filteru
NIVO_BOKAL = (0.010, 0.043)     # nivo kafe u bokalu na prvom i poslednjem kadru

KUVALO_NAGIB = 31.0             # stepeni, izliv nadole ka -X
KUVALO_ZAOKRET = 8.0            # stepeni oko Z, da se izliv malo okrene ka kameri
MLAZ_PAD = 0.09                 # visina vrha izliva iznad površine kafe u filteru
MLAZ_BRZINA = 0.45              # m/s na izlazu iz izliva
MLAZ_R0 = 0.0019


def r_konus(z):
    """Unutrašnji poluprečnik staklenog konusa (V60 ima 60° ugao, pola je 30°)."""
    return KONUS_R0 + (z - PLOCA_Z[1]) * TAN30


def r_filter(z):
    return (z - FILTER_VRH) * TAN30


# ---------------------------------------------------------------------------- pomoćne funkcije
# (predlog za common.py: catmull, tube, weld, shadow_light, animate, node helperi)

def catmull(pts, n=6):
    """Glatka kriva kroz tačke (Catmull-Rom), radi i za 2D i za 3D."""
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i > 0 else 2 * P[i] - P[i + 1]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else 2 * P[i + 1] - P[i]
        for k in range(n):
            s = k / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * s * s * s))
    out.append(P[-1].copy())
    return out


def profil(pts, n=4):
    return [(v.x, v.y) for v in catmull(pts, n)]


def offset_profil(pts, d):
    """Pomera (r, z) profil za d ka unutra (za šupljinu u koju ide tečnost)."""
    out = []
    for i, (r, z) in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)])
        b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized()
        n_in = Vector((-t.y, t.x))
        p = Vector((r, z)) + n_in * d
        out.append((max(p.x, 0.0) if i else 0.0, p.y))
    return out


def link_obj(obj):
    bpy.context.collection.objects.link(obj)
    return obj


def weld(obj, dist=1e-6):
    """Spaja duple tačke (pol lathe-a na osi) i ispravlja normale."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def tube(name, pts, radii, segs=12, caps=True, mat=None):
    """Cev duž polilinije (paralelni transport okvira); radii je poluprečnik po tački."""
    bm = bmesh.new()
    n = len(pts)
    rings, normal = [], None
    angles = [2 * math.pi * k / segs for k in range(segs)]
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        normal = t.orthogonal().normalized() if normal is None else (normal - t * normal.dot(t)).normalized()
        b = t.cross(normal)
        r = radii[i]
        rings.append([bm.verts.new(pts[i] + r * (math.cos(a) * normal + math.sin(a) * b)) for a in angles])
    for i in range(n - 1):
        for k in range(segs):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % segs], rings[i + 1][(k + 1) % segs], rings[i + 1][k]))
    if caps:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = link_obj(bpy.data.objects.new(name, mesh))
    C.smooth(obj)
    if mat:
        C.assign(obj, mat)
    return obj


def mesh_obj(name, verts, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    return link_obj(bpy.data.objects.new(name, mesh))


def solidify(obj, thickness, offset=-1.0, subsurf=0):
    m = obj.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness, m.offset, m.use_even_offset = thickness, offset, True
    if subsurf:
        s = obj.modifiers.new('Subsurf', 'SUBSURF')
        s.levels = s.render_levels = subsurf
    return obj


def shadow_light(mat, amount=0.7):
    """Staklo baca svetliju senku: za zrake senke deo materijala je providan (umesto kaustike)."""
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    src = out.inputs['Surface'].links[0].from_socket
    lp = nt.nodes.new('ShaderNodeLightPath')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = amount
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs['Fac'])
    nt.links.new(src, mix.inputs[1])
    nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return mat


def bsdf_of(mat):
    return mat.node_tree.nodes['Principled BSDF']


class N:
    """Kratki pomoćnik za čvorove u kodu."""

    def __init__(self, nt):
        self.nt = nt

    def new(self, kind, **inputs):
        n = self.nt.nodes.new(kind)
        for k, v in inputs.items():
            self.set(n.inputs[k], v)
        return n

    def set(self, socket, v):
        if hasattr(v, 'is_linked') or hasattr(v, 'links'):
            self.nt.links.new(v, socket)
        else:
            socket.default_value = v

    def math(self, op, a, b=0.0, clamp=False):
        n = self.nt.nodes.new('ShaderNodeMath')
        n.operation = op
        n.use_clamp = clamp
        self.set(n.inputs[0], a)
        self.set(n.inputs[1], b)
        return n.outputs[0]

    def maprange(self, x, a, b, c=0.0, d=1.0, smooth=True):
        n = self.nt.nodes.new('ShaderNodeMapRange')
        n.interpolation_type = 'SMOOTHSTEP' if smooth else 'LINEAR'
        n.clamp = True
        self.set(n.inputs['Value'], x)
        n.inputs['From Min'].default_value, n.inputs['From Max'].default_value = a, b
        n.inputs['To Min'].default_value, n.inputs['To Max'].default_value = c, d
        return n.outputs['Result']

    def mix_color(self, fac, a, b):
        n = self.nt.nodes.new('ShaderNodeMix')
        n.data_type = 'RGBA'
        self.set(n.inputs['Factor'], fac)
        self.set(n.inputs['A'], a)
        self.set(n.inputs['B'], b)
        return n.outputs['Result']

    def link(self, a, b):
        self.nt.links.new(a, b)


def animate(n_frames, setter, target, path, index=-1):
    """Ključni kadar na svakom kadru: setter(t, sec) postavi vrednost, pa se upiše ključ."""
    for f in range(1, n_frames + 1):
        t = (f - 1) / max(1, n_frames - 1)
        setter(t, t * TRAJANJE)
        target.keyframe_insert(data_path=path, frame=f, index=index)


# ---------------------------------------------------------------------------- materijali

def materijali():
    m = {}
    m['glass'] = shadow_light(C.mat_glass('Glass'), 0.8)
    m['steel'] = C.mat_steel('KettleSteel', roughness=0.26)
    bsdf_of(m['steel']).inputs['Base Color'].default_value = (0.50, 0.485, 0.47, 1)   # tamniji inox
    m['black'] = C.mat_plastic('KettleBlack', color=(0.018, 0.017, 0.016), roughness=0.42)
    m['coffee'] = C.mat_coffee_liquid('Coffee')
    m['coffee_thin'] = C.mat_coffee_liquid('CoffeeThin', color=(0.32, 0.13, 0.045))     # tanak mlaz je ćilibaran
    m['water'] = C.mat_water('Water')
    m['bean'] = C.mat_bean('Bean')
    m['filter'] = mat_filter()
    m['bed'] = mat_bed()
    m['top'] = mat_coffee_top()
    m['steam'] = []
    return m


def mat_filter():
    """Papir: suv i beo iznad kafe, mokar i taman ispod (kao u videu: donji deo drippera je taman)."""
    mat = C.mat_paper('Filter')
    b = bsdf_of(mat)
    nt = N(mat.node_tree)
    tc = nt.new('ShaderNodeTexCoord')
    sep = nt.new('ShaderNodeSeparateXYZ')
    nt.link(tc.outputs['Object'], sep.inputs[0])
    noise = nt.new('ShaderNodeTexNoise', Scale=90.0, Detail=3.0)
    nt.link(tc.outputs['Object'], noise.inputs['Vector'])
    zz = nt.math('ADD', sep.outputs['Z'], nt.math('MULTIPLY', nt.math('SUBTRACT', noise.outputs['Fac'], 0.5), 0.006))
    wet = nt.maprange(zz, NIVO_DRIPPER + 0.006, NIVO_DRIPPER + 0.0015, 0.0, 1.0)
    col = nt.mix_color(wet, (0.93, 0.91, 0.86, 1), (0.10, 0.048, 0.022, 1))
    nt.link(col, b.inputs['Base Color'])
    nt.link(nt.maprange(wet, 0, 1, 0.85, 0.35, smooth=False), b.inputs['Roughness'])
    return mat


def mat_bed():
    """Površina kafe u filteru: pena sa mehurićima i talasići oko mesta gde pada mlaz."""
    mat, b = C._principled('CoffeeBed', **{'Roughness': 0.22, 'Coat Weight': 0.4, 'Coat Roughness': 0.08})
    nt = N(mat.node_tree)
    tc = nt.new('ShaderNodeTexCoord')
    noise = nt.new('ShaderNodeTexNoise', Scale=260.0, Detail=4.0)
    nt.link(tc.outputs['Object'], noise.inputs['Vector'])
    col = nt.mix_color(nt.maprange(noise.outputs['Fac'], 0.35, 0.7), (0.07, 0.03, 0.012, 1), (0.30, 0.16, 0.07, 1))
    nt.link(col, b.inputs['Base Color'])
    vor = nt.new('ShaderNodeTexVoronoi', Scale=700.0)
    nt.link(tc.outputs['Object'], vor.inputs['Vector'])
    flat = nt.new('ShaderNodeVectorMath', Vector=(0, 0, 0))
    flat.operation = 'MULTIPLY'
    nt.link(tc.outputs['Object'], flat.inputs[0])
    flat.inputs[1].default_value = (1, 1, 0)
    wave = nt.new('ShaderNodeTexWave', Scale=70.0, Distortion=0.0, Detail=0.0)
    wave.wave_type = 'RINGS'
    nt.link(flat.outputs['Vector'], wave.inputs['Vector'])
    dist = nt.new('ShaderNodeVectorMath')
    dist.operation = 'LENGTH'
    nt.link(flat.outputs['Vector'], dist.inputs[0])
    fade = nt.maprange(dist.outputs['Value'], 0.004, 0.03, 1.0, 0.0)
    h = nt.math('ADD', nt.math('MULTIPLY', wave.outputs['Fac'], fade), nt.math('MULTIPLY', vor.outputs['Distance'], 0.5))
    bump = nt.new('ShaderNodeBump', Strength=0.35, Distance=0.0004)
    nt.link(h, bump.inputs['Height'])
    nt.link(bump.outputs['Normal'], b.inputs['Normal'])
    mat['wave'] = wave.name
    return mat


def mat_coffee_top():
    """Gornja površina kafe u bokalu: tamno ogledalo sa prstenom pene uz staklo."""
    mat, b = C._principled('CoffeeTop', **{'Roughness': 0.06, 'IOR': 1.34})
    nt = N(mat.node_tree)
    tc = nt.new('ShaderNodeTexCoord')
    flat = nt.new('ShaderNodeVectorMath')
    flat.operation = 'MULTIPLY'
    nt.link(tc.outputs['Object'], flat.inputs[0])
    flat.inputs[1].default_value = (1, 1, 0)
    dist = nt.new('ShaderNodeVectorMath')
    dist.operation = 'LENGTH'
    nt.link(flat.outputs['Vector'], dist.inputs[0])
    radius = nt.new('ShaderNodeValue')
    radius.name = 'Radius'
    radius.outputs[0].default_value = 0.045
    edge = nt.math('SUBTRACT', radius.outputs[0], dist.outputs['Value'])     # udaljenost od stakla
    vor = nt.new('ShaderNodeTexVoronoi', Scale=900.0)
    nt.link(tc.outputs['Object'], vor.inputs['Vector'])
    ring = nt.math('MULTIPLY', nt.maprange(edge, 0.0065, 0.0012), nt.maprange(vor.outputs['Distance'], 0.15, 0.55, 0.55, 1.0))
    col = nt.mix_color(ring, (0.03, 0.012, 0.005, 1), (0.34, 0.19, 0.085, 1))
    nt.link(col, b.inputs['Base Color'])
    nt.link(nt.maprange(ring, 0, 1, 0.06, 0.45, smooth=False), b.inputs['Roughness'])
    return mat


# ---------------------------------------------------------------------------- modeli

def bokal(m):
    prof = profil(SERVER_PROFIL, 4)
    srv = C.lathe('Server', prof, segments=128)
    # izliv (kljun) na -X strani: gornja ivica se izvlači napolje i malo nagore
    for v in srv.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        d = math.pi - abs(th)
        w = math.exp(-(d / 0.30) ** 2) * min(1.0, max(0.0, (z - 0.096) / 0.022)) ** 1.6
        if w > 1e-4:
            r = math.hypot(x, y) + 0.010 * w
            v.co = (r * math.cos(th), r * math.sin(th), z + 0.0025 * w)
    weld(srv)
    C.assign(srv, m['glass'])
    solidify(srv, SERVER_DEBLJINA, -1.0, subsurf=1)
    # drška desno
    pts = catmull([(0.034, 0, 0.106), (0.052, 0, 0.1085), (0.071, 0, 0.104), (0.080, 0, 0.088),
                   (0.080, 0, 0.064), (0.071, 0, 0.046), (0.054, 0, 0.037), (0.045, 0, 0.036)], 8)
    tube('ServerHandle', pts, [0.0045] * len(pts), segs=14, mat=m['glass'])
    return srv


def tecnost_bokal(m, n_frames):
    """Kafa u bokalu: šupljina bokala presečena kockom čija visina prati nivo (Boolean, egzaktno)."""
    outer = [p for p in profil(SERVER_PROFIL, 4) if p[1] <= 0.095]
    inner = offset_profil(outer, SERVER_DEBLJINA + 0.0003)
    cav = inner + [(0.0, inner[-1][1])]
    liq = weld(C.lathe('CoffeeLiquid', cav, segments=128))
    liq.data.materials.append(m['coffee'])
    liq.data.materials.append(m['top'])
    cut = mesh_obj('LevelCutter', [(-.1, -.1, -.2), (.1, -.1, -.2), (.1, .1, -.2), (-.1, .1, -.2),
                                   (-.1, -.1, 0), (.1, -.1, 0), (.1, .1, 0), (-.1, .1, 0)],
                   [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    cut.data.materials.append(m['top'])
    cut.hide_render = True
    cut.display_type = 'WIRE'
    b = liq.modifiers.new('Level', 'BOOLEAN')
    b.operation, b.solver, b.object = 'INTERSECT', 'EXACT', cut
    b.material_mode = 'TRANSFER'

    def r_in(h):
        for (r0, z0), (r1, z1) in zip(inner, inner[1:]):
            if z0 <= h <= z1 and z1 > z0:
                return r0 + (r1 - r0) * (h - z0) / (z1 - z0)
        return inner[-1][0]

    def level(t):
        return NIVO_BOKAL[0] + (NIVO_BOKAL[1] - NIVO_BOKAL[0]) * (0.25 * t + 0.75 * t * t * (3 - 2 * t))

    animate(n_frames, lambda t, s: setattr(cut.location, 'z', level(t)), cut, 'location', 2)
    rad = m['top'].node_tree.nodes['Radius'].outputs[0]
    animate(n_frames, lambda t, s: setattr(rad, 'default_value', r_in(level(t))), rad, 'default_value')
    return level


def dripper(m):
    z0, z1 = PLOCA_Z
    # staklena ploča (prsten) koja leži na bokalu
    plate = [(KONUS_R0, z0), (0.050, z0), (0.0532, z0 + 0.0009), (0.0542, (z0 + z1) / 2),
             (0.0532, z1 - 0.0009), (0.050, z1), (KONUS_R0 + 0.002, z1), (KONUS_R0, z0)]
    p = weld(C.lathe('DripperPlate', plate, segments=128))
    C.assign(p, m['glass'])
    # nožica koja ulazi u grlo bokala
    foot = C.lathe('DripperFoot', [(0.0345, 0.106), (0.0345, z0)], segments=96)
    C.assign(foot, m['glass'])
    solidify(foot, 0.0018, 1.0)
    # konus sa zaobljenom ivicom
    cone_pts = [(r_konus(z), z) for z in [z1 + i * (KONUS_Z1 - z1) / 10 for i in range(11)]]
    cone_pts += [(0.0562, 0.2055), (0.0588, 0.2066), (0.0612, 0.2060)]
    cone = C.lathe('DripperCone', profil(cone_pts, 3), segments=128)
    C.assign(cone, m['glass'])
    solidify(cone, 0.0025, 1.0, subsurf=1)
    # spiralna rebra iznutra (između stakla i papira)
    for k in range(12):
        th0 = 2 * math.pi * k / 12
        pts, rad = [], []
        for i in range(40):
            u = i / 39
            z = 0.131 + u * 0.067
            th = th0 + 0.85 * u
            r = r_konus(z) - 0.0007
            pts.append(Vector((r * math.cos(th), r * math.sin(th), z)))
            rad.append(0.00085 * min(1.0, 4 * u, 4 * (1 - u)) + 0.0002)
        tube(f'Rib{k:02d}', pts, rad, segs=8, mat=m['glass'])
    # drška desno
    hp = catmull([(0.048, 0, 0.199), (0.064, 0, 0.2015), (0.078, 0, 0.197), (0.0855, 0, 0.185),
                  (0.086, 0, 0.170), (0.079, 0, 0.157), (0.064, 0, 0.150), (0.045, 0, 0.148),
                  (0.024, 0, 0.150)], 8)
    tube('DripperHandle', hp, [0.0037] * len(hp), segs=14, mat=m['glass'])


def filter_papir(m):
    """V60 filter: konus uz staklo, iznad ivice se širi i gužva."""
    pts = [(0.0004, FILTER_VRH + 0.0007)]
    pts += [(r_filter(z), z) for z in [FILTER_VRH + 0.002 + i * (KONUS_Z1 - FILTER_VRH - 0.002) / 24 for i in range(25)]]
    pts += [(0.0541, 0.2075), (0.0566, 0.2125), (0.0601, 0.2185), (0.0634, 0.2245), (0.0652, 0.2285)]
    prof = profil(pts, 2)
    f = C.lathe('Filter', prof, segments=160)
    top = prof[-1][1]
    for v in f.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        s = min(1.0, max(0.0, (z - 0.201) / (top - 0.201)))
        if s <= 0:
            continue
        fold = 0.55 * math.sin(5 * th + 1.3) + 0.35 * math.sin(9 * th + 0.4) + 0.25 * math.sin(16 * th + 2.0)
        crum = 0.5 * math.sin(7 * th + 0.7) + 0.5 * math.sin(13 * th + 2.6) + 0.3 * math.sin(23 * th)
        r = math.hypot(x, y) * (1 + 0.045 * fold * s * s)
        v.co = (r * math.cos(th), r * math.sin(th), z + 0.0035 * crum * s ** 3)
    weld(f)
    C.assign(f, m['filter'])
    solidify(f, 0.00035, 1.0)
    # površina kafe u filteru (blago udubljena u sredini, gde pada mlaz)
    rb = r_filter(NIVO_DRIPPER) - 0.0003
    bed_prof = [(rb, NIVO_DRIPPER + 0.0007), (0.03, NIVO_DRIPPER), (0.012, NIVO_DRIPPER - 0.0008),
                (0.0, NIVO_DRIPPER - 0.0016)]
    bed = weld(C.lathe('CoffeeBed', profil(bed_prof, 4), segments=128))
    C.assign(bed, m['bed'])
    return bed


def kuvalo(m):
    """Gooseneck kuvalo u lokalnim koordinatama (uspravno, izliv ka -X). Vraća rig, vrh i pravac izliva."""
    rig = link_obj(bpy.data.objects.new('KettleRig', None))
    body_prof = profil([
        (0.000, 0.003), (0.050, 0.003), (0.060, 0.005), (0.0645, 0.009), (0.0660, 0.016),
        (0.0660, 0.026), (0.0650, 0.045), (0.0628, 0.065), (0.0595, 0.085), (0.0552, 0.103),
        (0.0500, 0.118), (0.0440, 0.129), (0.0380, 0.135), (0.0340, 0.137)], 6)
    body = C.lathe('KettleBody', body_prof, segments=192)

    def dimple(th, z):
        lo, hi, row_h, nn = 0.020, 0.126, 0.024, 16
        if z <= lo or z >= hi:
            return 0.0
        u = (z - lo) / row_h
        row = math.floor(u)
        a = 0.5 + 0.5 * math.cos(nn * (th + (row % 2) * math.pi / nn))
        return a ** 1.5 * math.sin(math.pi * (u - row)) * min(1.0, (z - lo) / 0.008, (hi - z) / 0.008)

    for v in body.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        r = math.hypot(x, y) * (1 - 0.017 * dimple(th, z))
        v.co = (r * math.cos(th), r * math.sin(th), z)
    weld(body)
    body.data.materials.append(m['steel'])
    body.data.materials.append(m['black'])
    for poly in body.data.polygons:
        if poly.center.z < 0.0115:
            poly.material_index = 1
    sub = body.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    lid = weld(C.lathe('KettleLid', profil([(0.0335, 0.1368), (0.0328, 0.1400), (0.0285, 0.1445),
                                            (0.020, 0.1475), (0.010, 0.1490), (0.0, 0.1493)], 4), 128))
    C.assign(lid, m['steel'])
    solidify(lid, 0.0012, -1.0)
    knob = weld(C.lathe('KettleKnob', profil([(0.0, 0.1480), (0.0095, 0.1480), (0.0105, 0.1500), (0.0108, 0.1560),
                                              (0.0100, 0.1610), (0.0075, 0.1635), (0.0, 0.1645)], 3), 64))
    C.assign(knob, m['black'])
    # izliv: tanka labudova šija
    sp = [(-0.040, 0, 0.018), (-0.068, 0, 0.030), (-0.088, 0, 0.050), (-0.104, 0, 0.075), (-0.117, 0, 0.098),
          (-0.128, 0, 0.115), (-0.138, 0, 0.125), (-0.148, 0, 0.129), (-0.157, 0, 0.127), (-0.164, 0, 0.122)]
    spts = catmull(sp, 10)
    srad = [0.0033 + 0.0058 * (1 - i / (len(spts) - 1)) ** 2.2 for i in range(len(spts))]
    spout = tube('KettleSpout', spts, srad, segs=20, mat=m['steel'])
    tip, tip_dir = spts[-1], (spts[-1] - spts[-3]).normalized()
    # otvor izliva: mali taman disk na vrhu
    hole = tube('SpoutHole', [tip - tip_dir * 0.0004, tip + tip_dir * 0.0002], [0.0022, 0.0022], segs=16,
                mat=m['black'])
    # drška pozadi (+X)
    hp = catmull([(0.036, 0, 0.132), (0.058, 0, 0.142), (0.084, 0, 0.140), (0.102, 0, 0.125), (0.107, 0, 0.095),
                  (0.100, 0, 0.062), (0.082, 0, 0.038), (0.058, 0, 0.026)], 8)
    handle = tube('KettleHandle', hp, [0.0058] * len(hp), segs=16, mat=m['black'])
    for o in (body, lid, knob, spout, hole, handle):
        o.parent = rig
    return rig, tip, tip_dir


def mlaz_putanja(tip_w, d):
    """Balistička putanja vode iz izliva; vraća tačke i poluprečnike (mlaz se tanji kako ubrzava)."""
    g = Vector((0, 0, -9.81))
    v0 = d * MLAZ_BRZINA
    a, b, c = 0.5 * g.z, v0.z, tip_w.z - (NIVO_DRIPPER - 0.004)
    t_end = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    pts, rad = [], []
    n = 220
    t0 = -0.004 / MLAZ_BRZINA
    for i in range(n):
        t = t0 + (t_end - t0) * (i / (n - 1)) ** 0.85
        tt = max(t, 0.0)
        p = tip_w + v0 * t + 0.5 * g * tt * tt
        speed = (v0 + g * tt).length
        pts.append(p)
        rad.append(MLAZ_R0 * math.sqrt(MLAZ_BRZINA / speed))
    return pts, rad


def postavi_kuvalo(rig, tip_local, dir_local):
    """Kuvalo visi na pivotu u vrhu izliva; pivot se pomera tako da mlaz padne tačno u x=0, y=0."""
    rot = Euler((0, -math.radians(KUVALO_NAGIB), math.radians(KUVALO_ZAOKRET)), 'XYZ')
    d = rot.to_matrix() @ dir_local
    tip_z = NIVO_DRIPPER + MLAZ_PAD
    g = -9.81
    v0 = d * MLAZ_BRZINA
    a, b, c = 0.5 * g, v0.z, MLAZ_PAD
    t_land = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    tip_w = Vector((-v0.x * t_land, -v0.y * t_land, tip_z))
    pivot = link_obj(bpy.data.objects.new('KettlePivot', None))
    pivot.location = tip_w
    pivot.rotation_euler = rot
    rig.parent = pivot
    rig.location = -tip_local
    return pivot, tip_w, d


def displace(obj, name, tex_scale, strength, coord_obj, direction='NORMAL'):
    tex = bpy.data.textures.new(name, 'CLOUDS')
    tex.noise_scale = tex_scale
    tex.noise_depth = 2
    mod = obj.modifiers.new(name, 'DISPLACE')
    mod.texture, mod.texture_coords, mod.texture_coords_object = tex, 'OBJECT', coord_obj
    mod.direction, mod.strength, mod.mid_level = direction, strength, 0.5
    return mod


def mlaz_vode(m, tip_w, d, n_frames):
    pts, rad = mlaz_putanja(tip_w, d)
    s = tube('WaterStream', pts, rad, segs=12, caps=True, mat=m['water'])
    flow = link_obj(bpy.data.objects.new('WaterFlow', None))
    sway = link_obj(bpy.data.objects.new('WaterSway', None))
    displace(s, 'WaterRipple', 0.0045, 0.00055, flow)
    displace(s, 'WaterSwayX', 0.035, 0.0011, sway, 'X')
    animate(n_frames, lambda t, sec: setattr(flow.location, 'z', 0.32 * sec), flow, 'location', 2)
    animate(n_frames, lambda t, sec: setattr(sway.location, 'z', 0.05 * sec), sway, 'location', 2)
    return s


def mlaz_kafe(m, level, n_frames):
    """Tanak mlaz kafe iz vrha filtera u bokal; dužina prati nivo u bokalu."""
    top = FILTER_VRH + 0.0015
    pts = [Vector((0, 0, -i / 160)) for i in range(161)]
    rad = [0.00125 * (1 - 0.3 * (i / 160) ** 0.7) for i in range(161)]
    s = tube('CoffeeStream', pts, rad, segs=10, mat=m['coffee_thin'])
    s.location = (0, 0, top)
    flow = link_obj(bpy.data.objects.new('CoffeeFlow', None))
    displace(s, 'CoffeeRipple', 0.004, 0.0005, flow)
    animate(n_frames, lambda t, sec: setattr(s.scale, 'z', top - level(t) + 0.002), s, 'scale', 2)
    animate(n_frames, lambda t, sec: setattr(flow.location, 'z', 0.2 * sec), flow, 'location', 2)
    return s


def para_ravni(m, n_frames):
    """Para kao 3 providne ravni sa šumom (brže od volumena na CPU-u)."""
    planes = []
    specs = [  # x, y, rotZ, širina, visina, drift, providnost, seme
        (0.000, -0.004, 0, 0.24, 0.27, 0.050, 0.55, 0.0),
        (-0.010, 0.016, 22, 0.22, 0.23, 0.075, 0.40, 3.7),
        (0.012, -0.022, -16, 0.20, 0.20, 0.030, 0.35, 7.1),
    ]
    for i, (x, y, rz, w, h, drift, alpha, seed) in enumerate(specs):
        mat = mat_steam(f'Steam{i}', h, drift, alpha, seed, n_frames)
        p = mesh_obj(f'Steam{i}', [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)], [(0, 1, 2, 3)])
        p.location = (x, y, NIVO_DRIPPER + 0.004)
        p.rotation_euler = (0, 0, math.radians(rz))
        C.assign(p, mat)
        p.visible_shadow = p.visible_diffuse = p.visible_glossy = False
        p.visible_transmission = p.visible_volume_scatter = False
        planes.append(p)
    return planes


def mat_steam(name, h, drift, alpha, seed, n_frames):
    mat, b = C._principled(name, **{'Base Color': (0.95, 0.93, 0.90, 1), 'Roughness': 1.0,
                                    'Emission Color': (0.95, 0.93, 0.9, 1), 'Emission Strength': 0.35})
    nt = N(mat.node_tree)
    tc = nt.new('ShaderNodeTexCoord')
    sep = nt.new('ShaderNodeSeparateXYZ')
    nt.link(tc.outputs['Object'], sep.inputs[0])
    zrel = nt.math('DIVIDE', sep.outputs['Z'], h)
    # stub pare se njiše i odnosi ulevo kako se diže
    cz = nt.new('ShaderNodeCombineXYZ')
    nt.link(sep.outputs['Z'], cz.inputs['Z'])
    wob = nt.new('ShaderNodeTexNoise', Scale=7.0, Detail=1.0)
    wob.noise_dimensions = '4D'
    nt.link(cz.outputs[0], wob.inputs['Vector'])
    center = nt.math('ADD', nt.math('MULTIPLY', nt.math('POWER', zrel, 1.6), -drift),
                     nt.math('MULTIPLY', nt.math('MULTIPLY', nt.math('SUBTRACT', wob.outputs['Fac'], 0.5), 0.09), zrel))
    width = nt.math('ADD', 0.010, nt.math('MULTIPLY', zrel, 0.05))
    q = nt.math('DIVIDE', nt.math('SUBTRACT', sep.outputs['X'], center), width)
    hmask = nt.math('EXPONENT', nt.math('MULTIPLY', nt.math('MULTIPLY', q, q), -1.0))
    vmask = nt.math('MULTIPLY', nt.maprange(zrel, 0.0, 0.18), nt.maprange(zrel, 0.40, 1.0, 1.0, 0.0))
    # pramenovi: 4D šum koji putuje nagore
    mp = nt.new('ShaderNodeMapping')
    nt.link(tc.outputs['Object'], mp.inputs['Vector'])
    mp.inputs['Scale'].default_value = (1.0, 1.0, 0.5)
    det = nt.new('ShaderNodeTexNoise', Scale=24.0, Detail=5.0, Roughness=0.6, Distortion=0.9)
    det.noise_dimensions = '4D'
    nt.link(mp.outputs['Vector'], det.inputs['Vector'])
    wisps = nt.maprange(det.outputs['Fac'], 0.42, 0.74)
    dens = nt.math('MULTIPLY', nt.math('MULTIPLY', hmask, vmask), nt.math('MULTIPLY', wisps, alpha))
    nt.link(dens, b.inputs['Alpha'])
    loc = mp.inputs['Location']
    animate(n_frames, lambda t, s: setattr(loc, 'default_value', (0, 0, -0.06 * s)), loc, 'default_value')
    for node in (wob, det):
        w_in = node.inputs['W']
        animate(n_frames, lambda t, s, w_in=w_in: setattr(w_in, 'default_value', seed + 0.35 * s), w_in, 'default_value')
    return mat


def zrno(m, name, loc, rot_z, flip=False):
    """Prženo zrno: spljošten elipsoid sa zakrivljenim urezom na ravnoj strani."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        X, Y, Z = x * 0.0056, y * 0.0041, z * 0.0028
        if z > 0:
            Z *= 0.55
            s = Y - 0.0009 * math.sin(x * 2.6)
            Z -= 0.0011 * math.exp(-(s / 0.00065) ** 2) * (1 - x * x) * min(1.0, z * 3)
        v.co = (X, Y, Z)
    bm.to_mesh(mesh)
    bm.free()
    o = link_obj(bpy.data.objects.new(name, mesh))
    C.smooth(o, subdiv=1)
    C.assign(o, m['bean'])
    o.location = (loc[0], loc[1], 0.0016 if flip else 0.0027)
    o.rotation_euler = (math.pi if flip else 0.0, 0.0, math.radians(rot_z))
    return o


# ---------------------------------------------------------------------------- scena

def svet(scene):
    """Okolina: dole tamno, horizont u terakoti sajta, gore krem (za odsjaje na inoxu i staklu)."""
    w = C.world(scene, strength=0.55)
    nt = N(w.node_tree)
    bg = w.node_tree.nodes['Background']
    tc = nt.new('ShaderNodeTexCoord')
    sep = nt.new('ShaderNodeSeparateXYZ')
    nt.link(tc.outputs['Generated'], sep.inputs[0])
    ramp = nt.new('ShaderNodeValToRGB')
    nt.link(nt.maprange(sep.outputs['Z'], -1.0, 1.0, 0.0, 1.0, smooth=False), ramp.inputs['Fac'])
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.30, (0.10, 0.06, 0.04, 1)
    els[1].position, els[1].color = 0.62, (0.92, 0.88, 0.80, 1)
    e = els.new(0.50)
    e.color = (0.30, 0.11, 0.05, 1)
    nt.link(ramp.outputs['Color'], bg.inputs['Color'])


def parse():
    p = argparse.ArgumentParser(prog='pour.py')
    p.add_argument('--out', required=True, help='folder za kadar_0001.png ...')
    p.add_argument('--kadrovi', type=int, default=120)
    p.add_argument('--render', default='proba', help="'proba' (prvi, srednji, poslednji), 'sve' ili '1,60,120'")
    p.add_argument('--res', type=int, default=800)
    p.add_argument('--uzorci', type=int, default=32)
    p.add_argument('--poster', type=int, default=0, help='kadar koji se snima i kao poster.png (0 = ne)')
    p.add_argument('--para', choices=['ravni'], default='ravni')
    p.add_argument('--kamera-daljina', type=float, default=1.15)
    return p.parse_args(C.args())


def main():
    a = parse()
    scene = C.reset()
    scene.frame_start, scene.frame_end = 1, a.kadrovi
    C.render_settings(scene, width=a.res, height=a.res, samples=a.uzorci, transparent=True, fps=30)
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.cycles.blur_glossy = 1.0
    scene.cycles.sample_clamp_indirect = 6.0
    svet(scene)
    C.studio_lights()
    C.shadow_catcher()

    m = materijali()
    bokal(m)
    level = tecnost_bokal(m, a.kadrovi)
    dripper(m)
    bed = filter_papir(m)
    rig, tip_l, dir_l = kuvalo(m)
    pivot, tip_w, d = postavi_kuvalo(rig, tip_l, dir_l)
    mlaz_vode(m, tip_w, d, a.kadrovi)
    mlaz_kafe(m, level, a.kadrovi)
    para_ravni(m, a.kadrovi)
    zrno(m, 'Bean1', (0.084, -0.030), 35)
    zrno(m, 'Bean2', (0.101, -0.012), -70, flip=True)

    # talasići u filteru putuju od centra
    wave = bed.data.materials[0].node_tree.nodes[m['bed']['wave']].inputs['Phase Offset']
    animate(a.kadrovi, lambda t, s: setattr(wave, 'default_value', -30.0 * s), wave, 'default_value')
    # kuvalo se jedva primetno njiše oko vrha izliva (mlaz ostaje na mestu)
    base = pivot.rotation_euler.copy()
    animate(a.kadrovi, lambda t, s: setattr(pivot, 'rotation_euler',
                                            (base.x, base.y + math.radians(0.8) * math.sin(2 * math.pi * t), base.z)),
            pivot, 'rotation_euler', 1)

    el = math.radians(10)
    target = Vector((0, 0, 0.215))
    cam = C.camera(target + a.kamera_daljina * Vector((0, -math.cos(el), math.sin(el))), target, lens=85)
    print(f'[pour] vrh izliva {tuple(round(c, 4) for c in tip_w)}, kamera {tuple(round(c, 4) for c in cam.location)}')

    if a.render == 'proba':
        frames = sorted({1, (a.kadrovi + 1) // 2, a.kadrovi})
    elif a.render == 'sve':
        frames = list(range(1, a.kadrovi + 1))
    else:
        frames = [int(x) for x in a.render.split(',') if x.strip()]
    out = str(pathlib.Path(a.out).resolve())
    for f in frames:
        t0 = time.time()
        C.render_frames(scene, out, [f])
        print(f'[pour] kadar {f}: {time.time() - t0:.1f} s')
    if a.poster:
        scene.frame_set(a.poster)
        scene.render.filepath = f'{out}/poster.png'
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f'[pour] poster (kadar {a.poster}): {time.time() - t0:.1f} s')


main()
