"""SIP: keramička šolja (stoneware sa curećom glazurom), kafa sa malo kreme i tanka para.

Šolja ulazi odozgo, okreće se ~28° i smiruje se; poslednjih ~12 kadrova miruje (kraj skrola).
Dogovor scena: metri, pod z=0, centar (0,0), kamera spreda ~10° odozgo, lens 85, kvadrat,
providna pozadina, C.shadow_catcher(), C.studio_lights().

Pokretanje iz korena repoa (uslovi iz .claude/agents/blender-umetnik.md):
    unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \
      -P scripts/blender/kafa/sip.py -- --out <folder> [--frames 1,45,90] [--end 90] [--res 800] \
      [--samples 32] [--spin 28] [--drop 0.045] [--poster] [--no-steam]

Bez --frames renderuje sve kadrove 1..end. --poster dodaje poster.png (smiren poslednji kadar).
"""
import argparse
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

import bpy  # noqa: E402

# ---------------------------------------------------------------- mere šolje (m)
RIM_Z = 0.0980          # vrh oboda
GLAZE_Z = 0.0560        # srednja linija do koje glazura pokriva telo
COFFEE_Z = 0.0895       # nivo kafe (8,5 mm ispod oboda, vidi se pod uglom od 10°)
HANDLE_ANGLE = -8.0     # krajnji ugao drške (° oko Z; 0 = drška desno, + = ka nazad)


# ---------------------------------------------------------------- pomoćne funkcije (predlog za common.py)
class Nodes:
    """Kratak zapis za čvorove: ulazi mogu biti broj, torka ili izlaz drugog čvora."""

    def __init__(self, tree):
        self.nt = tree

    def new(self, kind, **props):
        n = self.nt.nodes.new(kind)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def put(self, src, dst):
        if src is None:
            return
        if isinstance(src, bpy.types.NodeSocket):
            self.nt.links.new(src, dst)
        else:
            dst.default_value = src

    def math(self, op, a, b=0.0, c=0.0, clamp=False):
        n = self.new('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.put(a, n.inputs[0])
        self.put(b, n.inputs[1])
        self.put(c, n.inputs[2])
        return n.outputs[0]

    def add(self, a, b):
        return self.math('ADD', a, b)

    def sub(self, a, b):
        return self.math('SUBTRACT', a, b)

    def mul(self, a, b):
        return self.math('MULTIPLY', a, b)

    def vmath(self, op, a, b=None, scale=None):
        n = self.new('ShaderNodeVectorMath', operation=op)
        self.put(a, n.inputs[0])
        self.put(b, n.inputs[1])
        if scale is not None:
            self.put(scale, n.inputs[3])
        return n.outputs['Value'] if op in ('LENGTH', 'DOT_PRODUCT', 'DISTANCE') else n.outputs['Vector']

    def xyz(self, x=0.0, y=0.0, z=0.0):
        n = self.new('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            self.put(v, n.inputs[i])
        return n.outputs[0]

    def sep(self, vec):
        n = self.new('ShaderNodeSeparateXYZ')
        self.put(vec, n.inputs[0])
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def ramp(self, x, lo, hi, a=0.0, b=1.0, mode='SMOOTHSTEP'):
        """Map Range: x od lo do hi -> od a do b, sa smoothstep prelazom i odsecanjem."""
        n = self.new('ShaderNodeMapRange', interpolation_type=mode, clamp=True)
        for i, v in enumerate((x, lo, hi, a, b)):
            self.put(v, n.inputs[i])
        return n.outputs[0]

    def mix(self, fac, a, b):
        """Mešanje boja (torke od 3 ili 4 broja ili izlazi)."""
        n = self.new('ShaderNodeMix', data_type='RGBA', clamp_factor=True)
        self.put(fac, n.inputs[0])
        self.put(a if not isinstance(a, tuple) or len(a) == 4 else (*a, 1.0), n.inputs[6])
        self.put(b if not isinstance(b, tuple) or len(b) == 4 else (*b, 1.0), n.inputs[7])
        return n.outputs[2]

    def mixf(self, fac, a, b):
        n = self.new('ShaderNodeMix', data_type='FLOAT', clamp_factor=True)
        self.put(fac, n.inputs[0])
        self.put(a, n.inputs[2])
        self.put(b, n.inputs[3])
        return n.outputs[0]

    def noise(self, vec, scale, detail=2.0, rough=0.5, distortion=0.0, w=None, kind='FBM'):
        n = self.new('ShaderNodeTexNoise', noise_dimensions='4D' if w is not None else '3D', noise_type=kind)
        self.put(vec, n.inputs['Vector'])
        if w is not None:
            self.put(w, n.inputs['W'])
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        n.inputs['Distortion'].default_value = distortion
        return n.outputs['Fac']

    def voronoi(self, vec, scale, feature='F1', randomness=1.0):
        n = self.new('ShaderNodeTexVoronoi', feature=feature)
        self.put(vec, n.inputs['Vector'])
        n.inputs['Scale'].default_value = scale
        n.inputs['Randomness'].default_value = randomness
        return n.outputs['Distance'], n.outputs['Color']


def new_material(name):
    m = bpy.data.materials.new(name)
    if hasattr(m, 'use_nodes') and not m.use_nodes:  # u 5.x je uvek uključeno
        m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes['Principled BSDF'], Nodes(nt)


def catmull(points, steps=8):
    """Glatka kriva kroz tačke (Catmull-Rom); vraća gustu listu (r, z)."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(steps):
            t = s / steps
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in (0, 1)))
    out.append(points[-1])
    return out


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out_cubic(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=0.9):
    """Blago prebaci cilj pa se vrati: „smiruje se"."""
    t = min(max(t, 0.0), 1.0) - 1
    return t * t * ((s + 1) * t + s) + 1


# ---------------------------------------------------------------- modeli
def mug_profile():
    """Profil šolje (r, z): donja strana -> stopa -> spoljni zid -> obod -> unutrašnji zid -> dno."""
    under = [(0.0005, 0.0030), (0.0120, 0.0030), (0.0250, 0.0030), (0.0272, 0.0020)]
    outer = catmull([(0.0282, 0.0010), (0.0296, 0.0), (0.0311, 0.0010), (0.0317, 0.0042), (0.0334, 0.0060),
                     (0.0378, 0.0095), (0.0425, 0.0160), (0.0462, 0.0250), (0.0482, 0.0360), (0.0487, 0.0470),
                     (0.0482, 0.0600), (0.0476, 0.0750), (0.0472, 0.0870), (0.0470, 0.0955)], steps=7)
    # tragovi točka (okretanje na grnčarskom kolu) u donjem delu, vidljivi i na silueti
    rippled = []
    for r, z in outer:
        env = smoothstep(0.010, 0.018, z) * (1 - smoothstep(0.046, 0.060, z))
        rippled.append((r + 0.00011 * env * math.sin(2 * math.pi * z / 0.0066 + 0.7), z))
    cx, cz, rr = 0.0445, 0.0955, 0.0025       # zaobljen obod
    rim = [(cx + rr * math.cos(a), cz + rr * math.sin(a)) for a in [math.pi * i / 12 for i in range(1, 12)]]
    inner = catmull([(0.0420, 0.0955), (0.0421, 0.0870), (0.0424, 0.0750), (0.0430, 0.0600), (0.0434, 0.0470),
                     (0.0430, 0.0360), (0.0412, 0.0260), (0.0380, 0.0180), (0.0325, 0.0125), (0.0250, 0.0095),
                     (0.0150, 0.0086), (0.0005, 0.0085)], steps=6)
    return under + rippled + rim + inner


def build_body(rig):
    body = C.lathe('MugBody', mug_profile(), segments=192)
    body.parent = rig
    me = body.data
    # lice okrenuto ka osi = unutrašnjost šolje -> uvek glazirano (atribut koji čita shader)
    attr = me.attributes.new('inner', 'FLOAT', 'FACE')
    for p in me.polygons:
        c, n = p.center, p.normal
        attr.data[p.index].value = 1.0 if (n.x * c.x + n.y * c.y) < 0 and c.z > 0.006 else 0.0
    # ručno rađena šolja nije savršeno okrugla
    tex = bpy.data.textures.new('MugWobble', 'CLOUDS')
    tex.noise_scale = 0.035
    d = body.modifiers.new('Wobble', 'DISPLACE')
    d.texture, d.texture_coords, d.strength, d.mid_level = tex, 'LOCAL', 0.0012, 0.5
    return body


def build_handle(rig):
    """Debela drška: kriva sa okruglim presekom, deblja gore, proširena na spojevima."""
    pts = [(0.0435, 0.0862, 1.50), (0.0540, 0.0898, 1.15), (0.0665, 0.0900, 1.04), (0.0765, 0.0840, 1.0),
           (0.0815, 0.0710, 0.98), (0.0805, 0.0570, 0.95), (0.0740, 0.0460, 0.93), (0.0640, 0.0390, 0.96),
           (0.0540, 0.0365, 1.12), (0.0455, 0.0365, 1.45)]
    cu = bpy.data.curves.new('Handle', 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 16
    cu.bevel_depth = 0.0050
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, (x, z, rad) in zip(sp.bezier_points, pts):
        bp.co = (x, 0, z)
        bp.radius = rad
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.use_smooth = True
    ob = bpy.data.objects.new('Handle', cu)
    bpy.context.collection.objects.link(ob)
    ob.parent = rig
    ob.scale = (1.0, 1.25, 1.0)   # presek ovalan: širi poprečno, kao izvučena drška
    return ob


def build_coffee(rig):
    zc = COFFEE_Z
    prof = [(0.0430, zc + 0.0012), (0.0418, zc + 0.0003), (0.0400, zc), (0.0200, zc), (0.0003, zc)]
    ob = C.lathe('Coffee', prof, segments=128)
    ob.parent = rig
    return ob


def build_steam(rig):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, RIM_Z + 0.062))
    ob = bpy.context.active_object
    ob.name = 'Steam'
    ob.scale = (0.10, 0.10, 0.125)
    ob.parent = rig
    return ob


# ---------------------------------------------------------------- materijali
def mat_stoneware(body, seed=7):
    """Tamnobraon zrnasta glina (mat) + krem-siva sjajna glazura koja curi u kapima."""
    m, nt, bsdf, N = new_material('Stoneware')
    rnd = random.Random(seed)

    tc = N.new('ShaderNodeTexCoord', object=body)
    P = tc.outputs['Object']
    x, y, z = N.sep(P)
    flat = N.xyz(x, y, 0.0)
    r = N.vmath('LENGTH', flat)
    u = N.vmath('NORMALIZE', flat)          # pravac oko ose: šare se ponavljaju bez šava

    # --- ivica glazure: talasasta linija + kapi (rastojanje u metrima, < 0 = glazura)
    w1 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=1.3), (3.1, 7.7, 1.9)), 1.0, detail=3, rough=0.55)
    w2 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=4.0), (8.2, 1.3, 4.4)), 1.0, detail=1)
    z0 = N.add(N.math('MULTIPLY_ADD', N.sub(w1, 0.5), 0.0260, GLAZE_Z), N.mul(N.sub(w2, 0.5), 0.0080))
    d = N.sub(z0, z)

    # kapi: široki jezici (glazura se slegla) i uže kapi sa zadebljanim vrhom, raspoređeni nepravilno
    drips, angles = [], []
    while len(drips) < 9:
        a = rnd.uniform(0, 2 * math.pi)
        if any(abs(math.atan2(math.sin(a - b), math.cos(a - b))) < 0.34 for b in angles):
            continue
        angles.append(a)
        if len(drips) < 3:
            drips.append((a, rnd.uniform(0.0030, 0.0070), rnd.uniform(0.0065, 0.0120), 1.0))
        else:
            drips.append((a, rnd.uniform(0.0050, 0.0160), rnd.uniform(0.0030, 0.0052), rnd.uniform(1.05, 1.22)))
    for a, length, wid, bead_k in drips:
        top = GLAZE_Z + 0.004
        bot = GLAZE_Z - length
        h = N.mul(r, N.vmath('LENGTH', N.vmath('SUBTRACT', u, (math.cos(a), math.sin(a), 0.0))))
        zc = N.math('MAXIMUM', N.math('MINIMUM', z, top), bot)
        # kap se sužava naniže (vrat), a na kraju se skuplja u kapljicu
        taper = N.math('MULTIPLY_ADD', N.sub(zc, bot), 0.55 * wid / (top - bot), 0.72 * wid)
        neck = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(z, zc), 0.0)), taper)
        bead = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(z, bot + wid * 0.30), 0.0)), wid * bead_k * 0.9)
        d = N.math('SMOOTH_MIN', d, N.math('MINIMUM', neck, bead), 0.0060)
    d = N.math('MULTIPLY_ADD', N.sub(N.noise(P, 240.0, detail=2), 0.5), 0.0018, d)   # neravna ivica
    d = N.math('MULTIPLY_ADD', N.sub(N.noise(P, 800.0, detail=1), 0.5), 0.0007, d)
    d = N.math('MAXIMUM', d, N.sub(r, 0.0525))                 # drška ostaje gola osim spoja
    inner = N.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='inner').outputs['Fac']
    d = N.sub(d, N.mul(inner, 0.02))                            # unutrašnjost je sva glazirana
    nd = N.math('MULTIPLY', d, -1.0)                            # dubina u glazuri od ivice

    mask = N.ramp(d, -0.00018, 0.00018, 1.0, 0.0)
    edge_in = N.ramp(nd, 0.0, 0.0012, 1.0, 0.0)
    halo = N.mul(N.ramp(d, 0.0, 0.0013, 1.0, 0.0), N.ramp(N.noise(P, 160.0), 0.35, 0.65, 0.35, 1.0))

    # --- glina: čokoladno-braon, zrnasta (zrnca hvataju svetlo), sitan svetli šamot
    pebble, _ = N.voronoi(P, 850.0, randomness=0.9)
    peb_top = N.ramp(pebble, 0.55, 0.05)                        # 1 na vrhu zrnca
    grain = N.noise(P, 2600.0, detail=1)
    clay_var = N.noise(P, 90.0, detail=4)
    clay = N.mix(clay_var, (0.020, 0.0115, 0.0075), (0.038, 0.023, 0.015))
    clay = N.mix(N.mul(peb_top, 0.55), clay, (0.068, 0.045, 0.032))
    grog_d, _ = N.voronoi(P, 520.0)
    clay = N.mix(N.mul(N.ramp(grog_d, 0.10, 0.04), 0.8), clay, (0.12, 0.085, 0.062))
    clay = N.mix(N.mul(halo, 0.6), clay, (0.085, 0.036, 0.016))             # rđasti oreol oko glazure

    # --- glazura: krem-siva sa toplim tonom; oblaci, tačke gvožđa, reljef gline kroz tanku glazuru
    gv = N.noise(P, 55.0, detail=5, rough=0.62)
    glaze = N.mix(N.ramp(gv, 0.30, 0.72), (0.165, 0.128, 0.085), (0.395, 0.328, 0.240))
    cloud = N.ramp(N.noise(P, 30.0, detail=4, distortion=0.5), 0.48, 0.72)
    glaze = N.mix(N.mul(cloud, 0.65), glaze, (0.20, 0.120, 0.070))              # smeđi oblaci
    top_tone = N.ramp(z, GLAZE_Z + 0.010, RIM_Z - 0.002)                      # ka obodu glazura je tanja
    glaze = N.mix(N.mul(top_tone, 0.5), glaze, (0.21, 0.140, 0.088))
    glaze = N.mix(N.mul(peb_top, 0.60), glaze, (0.14, 0.088, 0.052))          # zrnca gline probijaju
    spot_d, _ = N.voronoi(P, 210.0)
    spots = N.mul(N.ramp(spot_d, 0.26, 0.10), N.ramp(N.noise(P, 45.0, detail=2), 0.40, 0.58))
    glaze = N.mix(N.mul(spots, 0.9), glaze, (0.085, 0.040, 0.020))            # tačke gvožđa
    fleck_d, _ = N.voronoi(P, 900.0)
    glaze = N.mix(N.mul(N.ramp(fleck_d, 0.18, 0.05), 0.8), glaze, (0.12, 0.065, 0.034))
    glaze = N.mix(N.mul(edge_in, 0.5), glaze, (0.21, 0.115, 0.060))           # tanka ivica -> karamel
    rim_brk = N.mul(N.ramp(z, RIM_Z - 0.0045, RIM_Z - 0.0008), N.ramp(N.noise(P, 300.0), 0.3, 0.6, 0.55, 1.0))
    glaze = N.mix(rim_brk, glaze, (0.15, 0.072, 0.034))                       # obod: glazura puca u smeđe

    N.put(N.mix(mask, clay, glaze), bsdf.inputs['Base Color'])
    N.put(N.mixf(mask, N.math('MULTIPLY_ADD', grain, 0.10, 0.80), N.math('MULTIPLY_ADD', gv, 0.18, 0.20)),
          bsdf.inputs['Roughness'])
    N.put(N.mixf(mask, 0.18, 0.5), bsdf.inputs['Specular IOR Level'])
    N.put(N.mixf(mask, 0.15, 0.35), bsdf.inputs['Coat Weight'])          # glina ima blag satenski sjaj
    N.put(N.mixf(mask, 0.38, 0.10), bsdf.inputs['Coat Roughness'])

    # --- reljef (u metrima): zrnca gline (i kroz glazuru), tragovi kola, zadebljana ivica glazure
    ring = N.math('SINE', N.math('MULTIPLY_ADD', z, 2 * math.pi / 0.0066,
                                 N.mul(N.noise(P, 40.0), 2.5)))
    peb_h = N.mul(N.sub(1.0, pebble), 0.00016)
    clay_h = N.add(peb_h, N.mul(ring, 0.00003))
    lip = N.mul(N.ramp(nd, 0.0, 0.0010), N.ramp(nd, 0.0010, 0.0032, 1.0, 0.55))
    pin, _ = N.voronoi(P, 1800.0)
    glaze_h = N.add(N.add(N.mul(lip, 0.00075), N.mul(peb_h, 0.60)), N.mul(N.ramp(pin, 0.12, 0.0), -0.000025))
    height = N.mixf(mask, clay_h, glaze_h)
    bump = N.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 1.0
    bump.inputs['Distance'].default_value = 1.0
    N.put(height, bump.inputs['Height'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    gbump = N.new('ShaderNodeBump')
    gbump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(lip, 0.00075), gbump.inputs['Height'])
    N.put(gbump.outputs['Normal'], bsdf.inputs['Coat Normal'])
    return m


def mat_coffee(coffee):
    """Tamna kafa, sjajna površina, tanak prsten kreme uz zid i par mrlja."""
    m, nt, bsdf, N = new_material('CoffeeSip')
    tc = N.new('ShaderNodeTexCoord', object=coffee)
    P = tc.outputs['Object']
    x, y, _ = N.sep(P)
    rr = N.vmath('LENGTH', N.xyz(x, y, 0.0))
    swirl = N.noise(P, 120.0, detail=3, distortion=1.2)
    crema = N.add(N.mul(N.ramp(rr, 0.0335, 0.0392), N.ramp(swirl, 0.35, 0.6, 0.55, 1.0)),
                  N.mul(N.ramp(swirl, 0.60, 0.72), 0.55))
    col = N.mix(crema, (0.016, 0.0065, 0.0028), N.mix(swirl, (0.20, 0.090, 0.038), (0.32, 0.16, 0.07)))
    N.put(col, bsdf.inputs['Base Color'])
    N.put(N.mixf(crema, 0.10, 0.35), bsdf.inputs['Roughness'])
    bsdf.inputs['Specular IOR Level'].default_value = 0.18   # tamna kafa, bez ogledala neba pod oštrim uglom
    bub, _ = N.voronoi(P, 2200.0)
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(N.mul(bub, crema), 0.00004), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_steam(steam, glow=0.6):
    """Tanki pramenovi pare: listovi šuma koji se dižu i šire, gusti samo iznad sredine šolje."""
    m = bpy.data.materials.new('Steam')
    if hasattr(m, 'use_nodes') and not m.use_nodes:
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial':
            nt.nodes.remove(n)
    out = nt.nodes['Material Output']
    N = Nodes(nt)
    clock = N.new('ShaderNodeValue', label='SteamTime')
    amount = N.new('ShaderNodeValue', label='SteamAmount')
    t, amt = clock.outputs[0], amount.outputs[0]

    tc = N.new('ShaderNodeTexCoord', object=steam)
    x, y, z = N.sep(tc.outputs['Object'])           # kocka: -0.5..0.5, skalirana na 10x10x12.5 cm
    zm = N.mul(N.add(z, 0.5), 0.125)                # visina iznad oboda u metrima
    xm, ym = N.mul(x, 0.10), N.mul(y, 0.10)
    sway = N.mul(N.math('SINE', N.math('MULTIPLY_ADD', zm, 55.0, N.mul(t, 1.7))), N.mul(zm, 0.12))
    q = N.xyz(N.add(xm, sway), ym, N.sub(N.mul(zm, 0.42), N.mul(t, 0.012)))
    f = N.noise(q, 55.0, detail=2, rough=0.5, distortion=0.35, w=N.mul(t, 0.35))
    sheet = N.math('POWER', N.sub(1.0, N.math('ABSOLUTE', N.math('MULTIPLY_ADD', f, 2.0, -1.0))), 4.0)
    patch = N.ramp(N.noise(q, 16.0, detail=1, w=N.add(N.mul(t, 0.2), 3.0)), 0.42, 0.64)
    rr = N.vmath('LENGTH', N.xyz(N.add(xm, sway), ym, 0.0))
    wide = N.math('MULTIPLY_ADD', zm, 0.22, 0.012)
    radial = N.ramp(rr, N.mul(wide, 0.35), wide, 1.0, 0.0)
    vert = N.mul(N.ramp(zm, 0.0, 0.010), N.ramp(zm, 0.030, 0.105, 1.0, 0.0))
    dens = N.mul(N.mul(N.mul(sheet, patch), N.mul(radial, vert)), N.mul(amt, 30.0))

    # jeftin trik bez šuma: para samo upija (daje alfa) i svetli belo srazmerno gustini,
    # pa je rezultat isto što i providna bela koprena; nema rasejanja, nema zrnaca
    vol = N.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1)
    vol.inputs['Absorption Color'].default_value = (0.0, 0.0, 0.0, 1)
    vol.inputs['Emission Color'].default_value = (1.0, 0.97, 0.94, 1)
    N.put(dens, vol.inputs['Density'])
    N.put(N.mul(dens, glow), vol.inputs['Emission Strength'])
    nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m, clock, amount


# ---------------------------------------------------------------- scena
def build(args):
    scene = C.reset()
    C.render_settings(scene, width=args.res, height=args.res, samples=args.samples, transparent=True)
    scene.frame_start, scene.frame_end = 1, args.end
    scene.cycles.volume_step_rate = 2.0
    scene.view_settings.exposure = args.exposure   # common.studio_lights je jako za tamnu keramiku
    C.world(scene, color=(0.36, 0.20, 0.12), strength=0.5)   # smeđa okolina kao sekcija SIP: odsjaj u glazuri
    C.studio_lights()
    C.shadow_catcher()

    rig = bpy.data.objects.new('MugRig', None)
    scene.collection.objects.link(rig)
    body = build_body(rig)
    handle = build_handle(rig)
    coffee = build_coffee(rig)
    stone = mat_stoneware(body)
    C.assign(body, stone)
    handle.data.materials.append(stone)
    C.assign(coffee, mat_coffee(coffee))

    clock = amount = None
    if not args.no_steam:
        steam = build_steam(rig)
        sm, clock, amount = mat_steam(steam, glow=0.6 * 2 ** -args.exposure)   # sjaj ne zavisi od ekspozicije
        C.assign(steam, sm)
        steam.visible_shadow = False

    # kamera: spreda, 10° odozgo, lens 85; okvir ~26 cm, šolja malo ispod sredine (para ima mesta)
    elev, dist, target = math.radians(10.0), 0.56, (0.0, 0.0, 0.077)
    C.camera((0.0, -dist * math.cos(elev), target[2] + dist * math.sin(elev)), target, lens=85)

    # animacija: kadar po kadar (ključ na svakom kadru, pa vrsta interpolacije ne igra ulogu)
    n = args.end
    for f in range(1, n + 1):
        p = (f - 1) / max(n - 1, 1)
        rig.location = (0.0, 0.0, args.drop * (1 - ease_out_cubic(p / 0.70)))
        rig.rotation_euler = (0.0, 0.0, math.radians(HANDLE_ANGLE + args.spin * (1 - ease_out_back(p / 0.86))))
        rig.keyframe_insert('location', frame=f)
        rig.keyframe_insert('rotation_euler', frame=f)
        if clock is not None:
            clock.outputs[0].default_value = f / 30.0
            clock.outputs[0].keyframe_insert('default_value', frame=f)
            amount.outputs[0].default_value = 0.35 + 0.65 * smoothstep(0.15, 0.75, p)
            amount.outputs[0].keyframe_insert('default_value', frame=f)
    return scene


def main():
    ap = argparse.ArgumentParser(prog='sip.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='', help='npr. 1,45,90; prazno = svi kadrovi')
    ap.add_argument('--end', type=int, default=90)
    ap.add_argument('--res', type=int, default=1600)
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--spin', type=float, default=28.0)
    ap.add_argument('--drop', type=float, default=0.045)
    ap.add_argument('--exposure', type=float, default=-1.9)
    ap.add_argument('--poster', action='store_true')
    ap.add_argument('--no-steam', dest='no_steam', action='store_true')
    args = ap.parse_args(C.args())

    scene = build(args)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    frames = [int(f) for f in args.frames.split(',') if f.strip()] or list(range(1, args.end + 1))
    C.render_frames(scene, str(out), frames)
    if args.poster:
        scene.frame_set(args.end)
        scene.render.filepath = str(out / 'poster.png')
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
