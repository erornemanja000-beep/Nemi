"""GRIND (kafa skrol-sajt, poglavlje 1): inox mlin sa burr mehanizmom.

Zrna padaju odozgo (van kadra) u stakleni levak i pune ga (rigid body), a iz otvora napred dole
curi mlevena kafa (čestice) naniže, van kadra, ka dripperu iz scene POUR.

Pokretanje iz korena repoa (vidi .claude/agents/blender-umetnik.md):
  unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \
    -P scripts/blender/kafa/grind.py -- --out <folder> --kadrova 90 --kadrovi 1,45,90 --res 800 --uzorci 32

Dogovor svih scena: metri, pod z=0, kamera spreda (-Y) 10 stepeni odozgo, objektiv 85 mm, kadar 1:1,
providna pozadina, C.studio_lights(). Otvor mlina (odakle pada mlevena kafa) je tačno na x=0.
Mlin je okrenut za --rot stepeni oko vertikalne ose kroz otvor (pogled 3/4 kao u videu), pa je
telo pomereno ~2 cm udesno, a levak (i mlaz zrna odozgo) je na x~+0.017.

Fizika ide od negativnih kadrova (preroll), tako da je na kadru 1 levak već pun do pola, a mlazevi
teku. Kadrovi 1..N su kadrovi sekvence (kadar_0001.png ... kadar_00NN.png).
"""
import argparse
import math
import pathlib
import random
import sys
import time

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

# --------------------------------------------------------------------------------------------
# mere mlina (lokalno: centar tela na (0,0), pod z=0, prednja strana ka -Y)
W, D = 0.155, 0.180          # telo: širina (x), dubina (y)
RC = 0.016                   # radijus vertikalnih ivica tela
Z_TOP = 0.165                # gornja površina tela
Z_OVER = 0.048               # donja ivica gornjeg dela (nadstrešnica iznad otvora)
RECESS = 0.058               # koliko je postolje uvučeno napred (niša ispod otvora)
SPOUT = (0.012, -D / 2 + 0.024)   # osa otvora (lokalno x, y)
SPOUT_Z = 0.036              # donja ivica crnog prstena otvora
DIAL = (-0.026, 0.098)       # točkić za mlevenje na prednjoj strani (x, z)
HOP_Z0, HOP_TOP = 0.192, 0.319    # stakleni levak
RIM_R = 0.0825               # unutrašnji radijus crnog prstena na vrhu (otvor za zrna)

BEAN = (0.014, 0.0102, 0.0043, 0.0029)   # zrno: dužina, širina, ispupčena i ravna polu-debljina


def parse():
    p = argparse.ArgumentParser(prog='grind.py')
    p.add_argument('--out', default='/tmp/nemi-blender/grind', help='folder za kadar_NNNN.png')
    p.add_argument('--kadrova', type=int, default=90, help='broj kadrova sekvence')
    p.add_argument('--kadrovi', default='sve', help='"sve" ili lista, npr. 1,45,90')
    p.add_argument('--res', type=int, default=1600, help='stranica kvadratnog kadra u px')
    p.add_argument('--uzorci', type=int, default=64)
    p.add_argument('--izlaz', choices=['mleveno', 'zrna'], default='mleveno',
                   help='šta curi iz otvora: mlevena kafa ili cela zrna')
    p.add_argument('--rot', type=float, default=-25.0, help='okret mlina oko otvora (stepeni)')
    p.add_argument('--usporenje', type=float, default=0.4, help='brzina fizike (1 = stvarno vreme)')
    p.add_argument('--preroll', type=int, default=65, help='kadrova fizike pre kadra 1')
    p.add_argument('--pocetna', type=int, default=600, help='zrna u levku na kadru 1')
    p.add_argument('--tok', type=float, default=4.0, help='zrna po kadru u mlazu odozgo')
    p.add_argument('--mleveno', type=int, default=150, help='čestica mlevene kafe po kadru')
    p.add_argument('--seed', type=int, default=7)
    p.add_argument('--poster', type=int, default=0, help='kadar koji se snima i kao poster.png')
    p.add_argument('--bez-rendera', action='store_true', help='samo napravi scenu i bake, ispiši stanje')
    return p.parse_args(C.args())


# --------------------------------------------------------------------------------------------
# geometrija (pomoćne funkcije; kandidati za common.py)

def mesh_object(name, bm, smooth=True, sharp_deg=None, collection=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = smooth
    if smooth and sharp_deg:
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.collection).objects.link(ob)
    return ob


def lathe2(name, profile, segments=96, closed=False, sharp_deg=40, smooth=True):
    """Telo okretanja oko Z; profile je lista (r, z). closed=True spaja poslednju tačku sa prvom
    (puni zid sa debljinom). Tačke na osi (r=0) se spajaju. Normale idu napolje ako profil ide
    suprotno od kazaljke na satu u ravni (r, z): gore spolja, unutra na vrhu, dole iznutra."""
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * ca, r * sa, z)) for r, z in profile])
    n = len(profile)
    for i in range(segments):
        A, B = rings[i], rings[(i + 1) % segments]
        for j in range(n if closed else n - 1):
            j2 = (j + 1) % n
            bm.faces.new((A[j], B[j], B[j2], A[j2]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    return mesh_object(name, bm, smooth=smooth, sharp_deg=sharp_deg)


def rounded_box(name, x0, x1, y0, y1, z0, z1, rc, rt=0.001, rb=0.001, seg_c=12, seg_e=5):
    """Kvadar sa zaobljenim vertikalnim ivicama (rc) i zaobljenim gornjim/donjim ivicama (rt, rb).
    Normale su izračunate tačno (custom normals), pa ravne strane nemaju lažne prelive."""
    cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    prof = []   # (uvlačenje, z, normala_r, normala_z)
    for k in range(seg_e + 1):
        a = math.pi / 2 * k / seg_e
        prof.append((rb * (1 - math.sin(a)), z0 + rb * (1 - math.cos(a)), math.sin(a), -math.cos(a)))
    for k in range(seg_e + 1):
        a = math.pi / 2 * k / seg_e
        prof.append((rt * (1 - math.cos(a)), z1 - rt + rt * math.sin(a), math.cos(a), math.sin(a)))
    corners = [(1, 1, 0.0), (-1, 1, 90.0), (-1, -1, 180.0), (1, -1, 270.0)]
    bm = bmesh.new()
    rings, normals = [], []
    for inset, z, nr, nz in prof:
        ring = []
        rr = max(rc - inset, 1e-5)
        for sx, sy, a0 in corners:
            ccx, ccy = cx + sx * (hx - rc), cy + sy * (hy - rc)
            for k in range(seg_c + 1):
                a = math.radians(a0 + 90.0 * k / seg_c)
                ca, sa = math.cos(a), math.sin(a)
                ring.append(bm.verts.new((ccx + rr * ca, ccy + rr * sa, z)))
                normals.append(Vector((ca * nr, sa * nr, nz)).normalized())
        rings.append(ring)
    m = len(rings[0])
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(m):
            i2 = (i + 1) % m
            bm.faces.new((A[i], A[i2], B[i2], B[i]))
    bm.faces.new(rings[-1])
    bm.faces.new(list(reversed(rings[0])))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    me.normals_split_custom_set_from_vertices(normals)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def bean_bm(rng, groove=True, u=40, v=20):
    """Zrno kafe: elipsoid, ispupčen gore (+Z), ravan dole sa urezom uzduž (blago S)."""
    L, Wb, Tt, Tb = BEAN
    sx = L / 2 * rng.uniform(0.93, 1.07)
    sy = Wb / 2 * rng.uniform(0.92, 1.06)
    tt, tb = Tt * rng.uniform(0.92, 1.08), Tb * rng.uniform(0.9, 1.1)
    bend = rng.uniform(-0.0012, 0.0012)
    s_amp = rng.uniform(0.0003, 0.0008)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    for vert in bm.verts:
        a, b, c = vert.co            # c: osa polova = dužina zrna
        X, Y = c * sx, a * sy
        if b >= 0:
            Z = b * tt
        else:
            Z = -tb * ((-b) ** 0.7)  # ravnija donja strana
            if groove:
                yc = s_amp * math.sin(math.pi * c)
                g = 0.0017 * math.exp(-((Y - yc) / 0.00105) ** 2) * max(0.0, 1 - c ** 4)
                Z += g * min(1.0, -b * 1.6)
        Z += bend * (c * c - 0.3)
        vert.co = (X, Y, Z)
    return bm


def chunk_bm(rng):
    """Komadić mlevene kafe: nepravilan, sa oštrim stranama."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    s = (rng.uniform(0.0008, 0.0012), rng.uniform(0.0007, 0.001), rng.uniform(0.0005, 0.0008))
    for vert in bm.verts:
        k = rng.uniform(0.65, 1.2)
        vert.co = (vert.co.x * s[0] * k, vert.co.y * s[1] * k, vert.co.z * s[2] * k)
    return bm


# --------------------------------------------------------------------------------------------
# materijali (na osnovu common.py)

def mat_brushed(name, roughness=0.26, color=(0.80, 0.79, 0.77), streaks=(25, 25, 2200), spun=False):
    """Brušeni inox. Horizontalno brušenje (tangenta oko Z) razvlači odsjaje uspravno, kao na
    mlinu u videu. spun=True: kružno brušenje oko lokalne Z ose (lice točkića)."""
    m = C.mat_steel(name, roughness)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Anisotropic'].default_value = 0.75 if spun else 0.6
    tan = nt.nodes.new('ShaderNodeTangent')
    tan.direction_type, tan.axis = 'RADIAL', 'Z'
    nt.links.new(tan.outputs['Tangent'], b.inputs['Tangent'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Detail'].default_value = 3.0
    if spun:
        sep = nt.nodes.new('ShaderNodeVectorMath')
        sep.operation = 'MULTIPLY'
        sep.inputs[1].default_value = (1, 1, 0)
        ln = nt.nodes.new('ShaderNodeVectorMath')
        ln.operation = 'LENGTH'
        mul = nt.nodes.new('ShaderNodeMath')
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = 3000.0
        nz.noise_dimensions = '1D'
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        nt.links.new(sep.outputs['Vector'], ln.inputs[0])
        nt.links.new(ln.outputs['Value'], mul.inputs[0])
        nt.links.new(mul.outputs['Value'], nz.inputs['W'])
    else:
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = streaks
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = roughness - 0.07
    mr.inputs['To Max'].default_value = roughness + 0.07
    nt.links.new(nz.outputs['Fac'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.04
    bump.inputs['Distance'].default_value = 0.0001
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_hopper_glass(name='HopperGlass'):
    """Staklo levka: za zrake senke je providno (Transparent), pa su zrna u levku osvetljena kao u
    videu, bez skupih kaustika."""
    m = C.mat_glass(name, tint=(0.93, 0.94, 0.94), roughness=0.03)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['IOR'].default_value = 1.5
    out = nt.nodes['Material Output']
    lp = nt.nodes.new('ShaderNodeLightPath')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (0.92, 0.92, 0.92, 1)
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mix.inputs['Fac'])
    nt.links.new(b.outputs['BSDF'], mix.inputs[1])
    nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m


def random_tint(m, lo=0.7, hi=1.25):
    """Svako zrno/komadić malo drugačije nijanse (Object Info > Random)."""
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    base = tuple(b.inputs['Base Color'].default_value)
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value, mr.inputs['To Max'].default_value = lo, hi
    hsv = nt.nodes.new('ShaderNodeHueSaturation')
    hsv.inputs['Color'].default_value = base
    nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], hsv.inputs['Value'])
    nt.links.new(hsv.outputs['Color'], b.inputs['Base Color'])
    return m


# --------------------------------------------------------------------------------------------
# mlin

def build_grinder(M):
    """Pravi sve delove mlina u lokalnim koordinatama i postavlja ih matricom M (okret + pomeraj).
    Vraća rečnik sa objektima koji trebaju fizici."""
    steel = mat_brushed('Inox')
    steel_pol = mat_brushed('InoxPolirani', roughness=0.16)
    steel_spun = mat_brushed('InoxTockic', roughness=0.2, spun=True)
    black = C.mat_plastic('CrnaPlastika', color=(0.018, 0.018, 0.018), roughness=0.32)
    mark = C.mat_plastic('Oznake', color=(0.05, 0.05, 0.05), roughness=0.5)
    glass = mat_hopper_glass()

    def place(ob, local=Matrix()):
        ob.matrix_world = M @ local
        return ob

    parts = {}
    # telo: gornji deo i uvučeno postolje (niša ispod otvora, kao na kadru iz videa)
    body = rounded_box('Telo', -W / 2, W / 2, -D / 2, D / 2, Z_OVER, Z_TOP, RC, rt=0.007, rb=0.004)
    C.assign(place(body), steel)
    base = rounded_box('Postolje', -W / 2 + 0.002, W / 2 - 0.002, -D / 2 + RECESS, D / 2 - 0.002,
                       0.0, Z_OVER + 0.004, RC - 0.002, rt=0.001, rb=0.003)
    C.assign(place(base), steel)
    parts['body'] = body

    # okrugli „vrat" (burr kućište) ispod levka, sa tankim žlebom po sredini
    collar = lathe2('Kuciste', [(0.0, Z_TOP - 0.0005), (0.049, Z_TOP - 0.0005), (0.0502, Z_TOP + 0.001),
                                (0.0502, 0.1765), (0.0488, 0.1772), (0.0488, 0.1782), (0.0502, 0.1789),
                                (0.0502, 0.1885), (0.0490, 0.1900), (0.0, 0.1900)], segments=128)
    C.assign(place(collar), steel_pol)
    parts['collar'] = collar
    gasket = lathe2('Zaptivka', [(0.0355, 0.1895), (0.0452, 0.1895), (0.0458, 0.1905), (0.0458, 0.1960),
                                 (0.0450, 0.1970), (0.0355, 0.1970)], segments=128, closed=True)
    C.assign(place(gasket), black)

    # stakleni levak (zid 3 mm) i crni prsten na vrhu
    hop = [(0.0400, HOP_Z0), (0.0400, 0.2040), (0.0425, 0.2085), (0.0870, 0.2560), (0.0885, 0.2620),
           (0.0890, HOP_TOP - 0.001), (0.0888, HOP_TOP), (0.0862, HOP_TOP), (0.0860, HOP_TOP - 0.001),
           (0.0855, 0.2625), (0.0842, 0.2575), (0.0397, 0.2098), (0.0370, 0.2050), (0.0370, HOP_Z0)]
    hopper = lathe2('Levak', hop, segments=160, closed=True, sharp_deg=50)
    C.assign(place(hopper), glass)
    ring = [(0.0895, 0.312), (0.0925, 0.312), (0.0935, 0.3132), (0.0935, 0.3268), (0.0925, 0.328),
            (RIM_R + 0.001, 0.328), (RIM_R, 0.3268), (RIM_R, 0.3205), (RIM_R + 0.001, HOP_TOP + 0.0005),
            (0.0895, HOP_TOP + 0.0005)]
    C.assign(place(lathe2('Poklopac', ring, segments=160, closed=True, sharp_deg=50)), black)

    # sudar za zrna: unutrašnjost levka (malo uža od stakla), dno u grlu i vrh prstena
    col = [(0.0, 0.2000), (0.0362, 0.2000), (0.0362, 0.2045), (0.0388, 0.2095), (0.0832, 0.2572),
           (0.0848, 0.2620), (0.0852, HOP_TOP - 0.001), (RIM_R - 0.0007, 0.3205), (RIM_R - 0.0007, 0.3285),
           (0.0940, 0.3285), (0.0942, 0.300)]
    collider = lathe2('LevakSudar', col, segments=64, smooth=False)
    place(collider)
    collider.hide_render = True
    collider.display_type = 'WIRE'
    parts['hopper_collider'] = collider

    # točkić za mlevenje: prsten sa podeocima + dugme sa kružno brušenim licem
    dx, dz = DIAL
    dial_m = Matrix.Translation((dx, -D / 2 + 0.0005, dz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    bezel = lathe2('TockicPrsten', [(0.0300, -0.001), (0.0350, -0.001), (0.0350, 0.0022), (0.0342, 0.0031),
                                    (0.0300, 0.0031)], segments=128, closed=True, sharp_deg=50)
    C.assign(place(bezel, dial_m), steel_pol)
    knob = lathe2('Tockic', [(0.0, 0.0), (0.0276, 0.0), (0.0276, 0.0026), (0.0290, 0.0040), (0.0290, 0.0250),
                             (0.0284, 0.0266), (0.0268, 0.0277), (0.0230, 0.0281), (0.0, 0.0276)],
                  segments=128, sharp_deg=50)
    C.assign(place(knob, dial_m), steel_spun)
    for k in range(7):          # podeoci po gornjem luku prstena
        a = math.radians(40 + k * 100 / 6)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.0020, 0.0006, 0.0005), verts=bm.verts)
        tick = mesh_object(f'Podeok{k}', bm, smooth=False)
        loc = Matrix.Translation((0.0323 * math.cos(a), 0.0323 * math.sin(a), 0.0030)) @ \
            Matrix.Rotation(a, 4, 'Z')
        C.assign(place(tick, dial_m @ loc), mark)
    bm = bmesh.new()             # oznaka na licu dugmeta
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.0055, 0.0009, 0.0006), verts=bm.verts)
    a = math.radians(120)
    ind = mesh_object('TockicOznaka', bm, smooth=False)
    C.assign(place(ind, dial_m @ Matrix.Translation((0.0215 * math.cos(a), 0.0215 * math.sin(a), 0.0280))
                   @ Matrix.Rotation(a, 4, 'Z')), mark)

    # nareckano dugme gore levo (tajmer) i jezičak-brava levka desno
    bm = bmesh.new()
    n, r0, h = 72, 0.0155, 0.0135
    rings = []
    for z, kn, rr in ((Z_TOP - 0.001, True, r0), (Z_TOP + h - 0.0018, True, r0), (Z_TOP + h, False, r0 - 0.0016)):
        ring = []
        for i in range(n):
            a = 2 * math.pi * i / n
            r = rr - (0.0007 if (kn and i % 2) else 0.0)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for j in range(2):
        for i in range(n):
            i2 = (i + 1) % n
            bm.faces.new((rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]))
    bm.faces.new(rings[-1])
    knurl = mesh_object('DugmeGore', bm, sharp_deg=35)
    C.assign(place(knurl, Matrix.Translation((-0.052, -0.045, 0.0))), steel_pol)
    tab = rounded_box('Jezicak', 0.030, 0.080, -0.013, -0.001, 0.1862, 0.1900, 0.0055, rt=0.0012, rb=0.0008,
                      seg_c=8, seg_e=3)
    C.assign(place(tab), steel_pol)

    # otvor za mlevenu kafu: crni prsten ispod nadstrešnice
    sx, sy = SPOUT
    spout = lathe2('Otvor', [(0.0, 0.0445), (0.0135, 0.0445), (0.0135, SPOUT_Z), (0.0185, SPOUT_Z),
                             (0.0190, SPOUT_Z + 0.0008), (0.0190, Z_OVER + 0.0005), (0.0, Z_OVER + 0.0005)],
                   segments=96, sharp_deg=50)
    C.assign(place(spout, Matrix.Translation((sx, sy, 0.0))), black)
    return parts


# --------------------------------------------------------------------------------------------
# fizika

def rb_add(objs, kind):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.rigidbody.objects_add(type=kind)


def make_beans(a, M, hop_xy, rng, phys_coll, bean_coll, bean_meshes, proxy_meshes, frame0):
    """Zrna na „pokretnoj traci" iznad kadra: svako zrno se spušta kao kinematičko telo i u svom
    kadru prelazi u dinamičko (nasleđuje brzinu trake), pa pada u levak."""
    fps, slow = 30, a.usporenje
    v0 = 0.8                                   # m/s pri puštanju (stvarno vreme)
    vq = v0 * slow / fps                       # m po kadru
    z_rel = 0.53                               # visina puštanja, iznad gornje ivice kadra
    fill_from, fill_len = frame0 + 2, 30
    stream_from = -18
    plan = []
    for i in range(a.pocetna):                 # punjenje pre kadra 1, šire i gušće
        plan.append((fill_from + fill_len * i / a.pocetna, 0.060))
    n_stream = int(a.tok * (a.kadrova - stream_from))
    for i in range(n_stream):                  # mlaz koji se vidi u kadru
        plan.append((stream_from + (a.kadrova - stream_from) * i / n_stream, 0.028))
    placed = []                                # (qz, x, y) u koordinatama trake
    beans = []
    for idx, (t_rel, radius) in enumerate(plan):
        for _ in range(200):
            rr = radius * math.sqrt(rng.random())
            ang = rng.uniform(0, 2 * math.pi)
            x, y = hop_xy[0] + rr * math.cos(ang), hop_xy[1] + rr * math.sin(ang)
            jz = rng.uniform(0.0, 0.012)
            qz = vq * t_rel + jz
            ok = all((x - px) ** 2 + (y - py) ** 2 + (qz - pz) ** 2 > 0.0148 ** 2
                     for pz, px, py in placed[-120:] if abs(qz - pz) < 0.0148)
            if ok:
                break
        placed.append((qz, x, y))
        rel = max(int(math.floor(t_rel)), frame0 + 2)
        var = idx % len(bean_meshes)
        proxy = bpy.data.objects.new(f'ZrnoF{idx:04d}', proxy_meshes[var])
        phys_coll.objects.link(proxy)
        proxy.hide_render = True
        proxy.display_type = 'BOUNDS'
        z_at_rel = z_rel + jz + vq * (t_rel - rel)
        rot0 = Vector((rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3)))
        w = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * (12 * slow / fps)
        drift = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0)) * (0.06 * slow / fps)
        proxy.location = (x - drift.x * (rel - frame0), y - drift.y * (rel - frame0),
                          z_at_rel + vq * (rel - frame0))
        proxy.rotation_euler = rot0
        proxy.keyframe_insert('location', frame=frame0)
        proxy.keyframe_insert('rotation_euler', frame=frame0)
        proxy.location = (x, y, z_at_rel)
        proxy.rotation_euler = rot0 + w * (rel - frame0)
        proxy.keyframe_insert('location', frame=rel)
        proxy.keyframe_insert('rotation_euler', frame=rel)
        render = bpy.data.objects.new(f'Zrno{idx:04d}', bean_meshes[var])
        bean_coll.objects.link(render)
        render.parent = proxy
        render.hide_render = True
        render.keyframe_insert('hide_render', frame=frame0)
        render.hide_render = False
        render.keyframe_insert('hide_render', frame=rel)
        beans.append((proxy, rel))
    rb_add([b for b, _ in beans], 'ACTIVE')
    for proxy, rel in beans:
        rb = proxy.rigid_body
        rb.collision_shape = 'CONVEX_HULL'
        rb.mass = 0.05
        rb.friction = 0.6
        rb.restitution = 0.12
        rb.use_margin = True
        rb.collision_margin = 0.0004
        rb.linear_damping = 0.05
        rb.angular_damping = 0.35
        rb.kinematic = True
        proxy.keyframe_insert('rigid_body.kinematic', frame=frame0)
        proxy.keyframe_insert('rigid_body.kinematic', frame=rel)
        rb.kinematic = False
        proxy.keyframe_insert('rigid_body.kinematic', frame=rel + 1)
    return [b for b, _ in beans]


def make_stream(a, M, frame0, rng):
    """Mlaz iz otvora: čestice (Newton) sa instancama komadića mlevene kafe ili celih zrna."""
    sx, sy = SPOUT
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=0.0062)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    em = mesh_object('MlazIzvor', bm, smooth=False)
    em.matrix_world = M @ Matrix.Translation((sx, sy, SPOUT_Z + 0.002))
    em.show_instancer_for_render = False
    em.hide_render = False
    coll = bpy.data.collections.new('MlazOblici')        # nije u sceni, samo za instance
    if a.izlaz == 'mleveno':
        mat = random_tint(C.mat_plastic('MlevenaKafa', color=(0.12, 0.066, 0.036), roughness=0.7), 0.6, 1.35)
        for k in range(6):
            ob = mesh_object(f'Komadic{k}', chunk_bm(rng), smooth=False, collection=coll)
            C.assign(ob, mat)
        rate, size, size_rand = a.mleveno, 1.0, 0.55
    else:
        mat = bpy.data.materials['Zrno']
        for k in range(4):
            ob = mesh_object(f'ZrnoMlaz{k}', bean_bm(rng), collection=coll)
            C.assign(ob, mat)
        rate, size, size_rand = 6, 1.0, 0.1
    ps = em.modifiers.new('Mlaz', 'PARTICLE_SYSTEM').particle_system
    ps.seed = a.seed
    st = ps.settings
    st.frame_start, st.frame_end = -24, a.kadrova + 1
    st.count = int(rate * (st.frame_end - st.frame_start))
    st.lifetime = 45
    st.emit_from = 'FACE'
    st.use_emit_random = True
    st.physics_type = 'NEWTON'
    st.normal_factor = 0.22
    st.factor_random = 0.035
    st.brownian_factor = 0.0
    st.time_tweak = a.usporenje * 25.0 / 30.0      # čestice računaju 1 kadar = 1/25 s
    st.render_type = 'COLLECTION'
    st.instance_collection = coll
    st.use_collection_pick_random = True
    st.particle_size = size
    st.size_random = size_rand
    st.use_rotations = True
    st.rotation_mode = 'NONE'
    st.rotation_factor_random = 1.0
    st.phase_factor_random = 2.0
    st.angular_velocity_mode = 'RAND'
    st.angular_velocity_factor = 25.0
    return em


# --------------------------------------------------------------------------------------------

def main():
    a = parse()
    t_start = time.time()
    rng = random.Random(a.seed)
    sc = C.reset()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    C.render_settings(sc, width=a.res, height=a.res, samples=a.uzorci, transparent=True, fps=30)
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    sc.cycles.seed = a.seed
    frame0 = 1 - a.preroll
    sc.frame_start, sc.frame_end = 1, a.kadrova

    # okret mlina oko otvora: otvor ostaje tačno na x=0
    th = math.radians(a.rot)
    sx, sy = SPOUT
    spout_x = sx * math.cos(th) - sy * math.sin(th)
    M = Matrix.Translation((-spout_x, 0.0, 0.0)) @ Matrix.Rotation(th, 4, 'Z')
    hop_xy = (M @ Vector((0, 0, 0))).xy

    C.world(sc)
    C.studio_lights()
    C.camera((0.0, -1.228 * math.cos(math.radians(10)), 0.20 + 1.228 * math.sin(math.radians(10))),
             (0.0, 0.0, 0.20), lens=85)

    parts = build_grinder(M)

    # senka: hvatač samo iza prednje ivice postolja, da mlaz slobodno pada ispod z=0 (preko ivice)
    catcher = C.shadow_catcher(size=1.0)
    catcher.scale = (3.0, 3.0, 1.0)
    catcher.matrix_world = M @ Matrix.Translation((0, -D / 2 + RECESS - 0.004 + 1.5, 0)) @ \
        Matrix.Diagonal((3.0, 3.0, 1.0, 1.0))

    # zrna
    bean_mat = random_tint(C.mat_bean('Zrno', color=(0.15, 0.075, 0.037)), 0.7, 1.3)
    bean_meshes, proxy_meshes = [], []
    for k in range(4):
        r1 = random.Random(a.seed * 100 + k)
        me = bpy.data.meshes.new(f'ZrnoOblik{k}')
        bm = bean_bm(r1)
        bm.to_mesh(me)
        bm.free()
        for poly in me.polygons:
            poly.use_smooth = True
        me.materials.append(bean_mat)
        bean_meshes.append(me)
        pm = bpy.data.meshes.new(f'ZrnoFizika{k}')
        bm = bean_bm(random.Random(a.seed * 100 + k), groove=False, u=10, v=6)
        bm.to_mesh(pm)
        bm.free()
        proxy_meshes.append(pm)
    phys_coll = bpy.data.collections.new('ZrnaFizika')
    bean_coll = bpy.data.collections.new('Zrna')
    sc.collection.children.link(phys_coll)
    sc.collection.children.link(bean_coll)

    bpy.ops.rigidbody.world_add()
    rbw = sc.rigidbody_world
    rbw.substeps_per_frame = 12
    rbw.solver_iterations = 25
    rbw.use_split_impulse = True
    rbw.time_scale = a.usporenje
    rbw.point_cache.frame_start = frame0
    rbw.point_cache.frame_end = a.kadrova
    rb_add([parts['hopper_collider']], 'PASSIVE')
    hc = parts['hopper_collider'].rigid_body
    hc.collision_shape, hc.mesh_source = 'MESH', 'BASE'
    hc.use_margin, hc.collision_margin, hc.friction, hc.restitution = True, 0.0006, 0.5, 0.1
    rb_add([parts['body'], parts['collar'], catcher], 'PASSIVE')
    parts['body'].rigid_body.collision_shape = 'BOX'
    parts['collar'].rigid_body.collision_shape = 'CYLINDER'
    catcher.rigid_body.collision_shape = 'BOX'

    beans = make_beans(a, M, hop_xy, rng, phys_coll, bean_coll, bean_meshes, proxy_meshes, frame0)
    make_stream(a, M, frame0, rng)
    print(f'GRIND: scena gotova za {time.time() - t_start:.1f} s, zrna {len(beans)}, '
          f'otvor x=0, levak x={hop_xy.x:.4f}')

    t = time.time()
    with bpy.context.temp_override(scene=sc):
        bpy.ops.ptcache.bake_all(bake=True)
    print(f'GRIND: bake {sc.frame_end - frame0 + 1} kadrova za {time.time() - t:.1f} s')

    # provera: koliko je zrna u levku, koliko je ispalo
    for f in sorted({1, a.kadrova // 2, a.kadrova}):
        sc.frame_set(f)
        inside = out = air = 0
        for p in beans:
            q = p.matrix_world.translation
            rho = math.hypot(q.x - hop_xy.x, q.y - hop_xy.y)
            if q.z > 0.45:
                air += 1
            elif 0.195 < q.z < 0.335 and rho < 0.095:
                inside += 1
            elif q.z <= 0.335:
                out += 1
        print(f'GRIND: kadar {f}: u levku {inside}, iznad/u vazduhu {air}, ispalo {out}')

    if a.bez_rendera:
        return
    out_dir = a.out.rstrip('/')
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    frames = list(range(1, a.kadrova + 1)) if a.kadrovi == 'sve' else [int(x) for x in a.kadrovi.split(',')]
    for f in frames:
        t = time.time()
        C.render_frames(sc, out_dir, [f])
        print(f'GRIND: kadar {f} renderovan za {time.time() - t:.1f} s')
    if a.poster:
        sc.frame_set(a.poster)
        sc.render.filepath = f'{out_dir}/poster.png'
        bpy.ops.render.render(write_still=True)


main()
