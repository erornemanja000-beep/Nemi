"""Kafa skrol-sajt, poglavlje 2 · POUR, foto-studio verzija (23.10.2026).

Stakleni bokal (kao Hario server) sa staklenim V60 i papirnim filterom (pravi konus 60°, krep tekstura,
šav). Od G65 odozgo, preko šava sa GRIND-om, u filter pada mlevena kafa (iste čestice kao u grind.py, iz
istog emitera i u istom trenutku; poslednje mrvice padnu oko G110). Kovano/brušeno gooseneck kuvalo
(bliže kameri, odsečeno desnom ivicom kadra) se od G100 do G112 primakne i nagne oko drške (12° -> 32°),
od G112 tanak mlaz vode (staklena cev po balističkoj putanji) pada u filter (stiže za ~10 kadrova); nivo
u filteru raste, papir vlaži odozdo, od G130 kaplje kafa (Volume Absorption), od G136 teče tanak mlaz i
nivo u bokalu raste, kondenzacija se pojavi na staklu; od G166 se kuvalo vraća, rep mlaza pada, počinje
drawdown. Na pultu leže 4 zrna. Para NIJE u renderu (pravi snimak preko CSS-a).

Zajednički svet (kamera rig K, sat G, mlaz mlevene kafe, karta za transmisiju, svetlo) je u grind.py i
ovde se uvozi. Kamera je ista kao u GRIND-u, tačno 1 S niže. Kadar scene = G + grind.G_OFF; fajlovi se
zovu po lokalnom broju sekvence: kadar_0001.png = G65 ... kadar_0128.png = G192.

Skupe proceduralne mape (kovane fasete kuvala, krep papira) peku se jednom u EXR (cache/, otisak koda u
imenu; promena koda = novo pečenje). HDRI „Lebombo“ (Greg Zaal, Poly Haven, CC0 1.0,
https://polyhaven.com/a/lebombo) dolazi iz common.world_hdri; ostalo je proceduralno.

Pokretanje iz korena repoa:
  unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \\
    -P scripts/blender/kafa/pour.py -- --out <folder> [--kadrovi 84,150,192 | sve] [--res 1200] \\
    [--uzorci 64] [--poster] [--fstop 5] [--bez-zamucenja] [--ponovo-peci]

--kadrovi su globalni G (65-192). Izlaz: kadar_LLLL.png (L = G - 64, RGBA 1200 x 1200), anchors.json
(sidra u S: ivica_v60, pult_y = zadnja ivica pulta, baza_y, kafa_y od G177), po želji poster.png (= G150).
Vreme (23.10.2026, 1200 px, 64 uzorka): ~340-390 CPU-s po kadru (~1,5 min na 4 slobodna jezgra); prvo
pečenje mapa ~80 s (posle iz keša).
"""
import argparse
import math
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import common as C  # noqa: E402
import grind as GR  # noqa: E402  (zajednički svet GRIND/POUR)

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Euler, Matrix, Vector  # noqa: E402

CACHE = GR.CACHE
TAN30 = math.tan(math.radians(30))
sf = GR.sf

# ---------------------------------------------------------------------------- mere (m), pult z=0
SERVER_PROFIL = [  # spoljna kontura bokala (r, z), od centra dna nagore (Hario server ~600 ml)
    (0.000, 0.000), (0.028, 0.000), (0.038, 0.0016), (0.0445, 0.0055), (0.0485, 0.0121),
    (0.0505, 0.0220), (0.0512, 0.0352), (0.0508, 0.0484), (0.0490, 0.0638), (0.0462, 0.0792),
    (0.0430, 0.0935), (0.0405, 0.1056), (0.0392, 0.1144), (0.0392, 0.1210), (0.0405, 0.1265),
    (0.0420, 0.1298),
]
SERVER_DEBLJINA = 0.0022
PLOCA_Z = (0.1303, 0.1353)      # donja i gornja strana staklene ploče drippera
KONUS_R0 = 0.0085               # unutrašnji poluprečnik konusa na dnu (otvor)
KONUS_Z1 = 0.2153               # gornja ivica konusa (ivica V60 ~0,217: 0,47 S od vrha POUR kadra)
RIM_R = 0.0612                  # spoljni poluprečnik usne V60
FILTER_VRH = 0.1244             # vrh papirnog konusa (viri kroz otvor)
FILTER_IZNAD = 0.018            # koliko papir viri iznad ivice V60
BOKAL_NIVO = ((132, 0.0030), (176, 0.0345), (192, 0.0420))   # nivo kafe u bokalu (G, z)

KUVALO_NAGIB = (12.0, 32.0)     # mirno / sipanje (stepeni)
KUVALO_ZAOKRET = -32.0          # telo kuvala ide napred-desno (bliže kameri), izliv nazad-levo
VRH_Z = 0.262                   # vrh izliva pri sipanju (storyboard ~0,26)
SLETANJE_Z = 0.186              # mlaz vode se gasi u filteru (ispod linije pogleda preko ivice)
MLAZ_BRZINA = 0.42              # m/s na izlazu iz izliva
MLAZ_R0 = 0.00185
DRSKA = Vector((0.095, 0.0, 0.120))   # tačka okreta (hvat na dršci), lokalno u kuvalu
PULT_ZADNJA = 0.070             # zadnja ivica pulta (y): senka samo na pultu, iza je zid sekcije
KUVALO_SKLONJENO = (0.050, 0.010)   # u mirovanju je kuvalo toliko desno/gore (x, z): izliv dalje od mlaza mlevene kafe


def r_konus(z):
    """Unutrašnji poluprečnik staklenog konusa (V60 ima 60° ugao, pola je 30°)."""
    return KONUS_R0 + (z - PLOCA_Z[1]) * TAN30


def r_filter(z):
    return max(z - FILTER_VRH, 0.0) * TAN30


def interp(keys, g):
    """Deo-po-deo smoothstep između (G, vrednost) ključeva."""
    if g <= keys[0][0]:
        return keys[0][1]
    for (g0, v0), (g1, v1) in zip(keys, keys[1:]):
        if g <= g1:
            return v0 + (v1 - v0) * GR.smoothstep(g0, g1, g)
    return keys[-1][1]


def filter_level(g):
    """Površina u filteru: suva kupa do G116, raste uz sipanje, drawdown od G166."""
    return interp([(65, 0.150), (110, 0.160), (118, 0.163), (160, 0.197), (166, 0.199), (192, 0.180)], g)


def carafe_level(g):
    return interp([(130, 0.0), *BOKAL_NIVO], g) if g >= 130 else 0.0


def kettle_tilt(g):
    return interp([(100, KUVALO_NAGIB[0]), (112, KUVALO_NAGIB[1]), (166, KUVALO_NAGIB[1]),
                   (178, KUVALO_NAGIB[0])], g)


# ---------------------------------------------------------------------------- pomoćne funkcije

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


def arc_v(prof):
    """UV v za lathe: dužina luka profila, normalizovana na 0..1."""
    d = [0.0]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        d.append(d[-1] + math.hypot(r1 - r0, z1 - z0))
    return [x / d[-1] for x in d]


def offset_profil(pts, d):
    """Pomera (r, z) profil za d ka unutra (za šupljinu u koju ide tečnost)."""
    out = []
    for i, (r, z) in enumerate(pts):
        a = Vector(pts[max(i - 1, 0)])
        b = Vector(pts[min(i + 1, len(pts) - 1)])
        t = (b - a).normalized()
        p = Vector((r, z)) + Vector((-t.y, t.x)) * d
        out.append((max(p.x, 0.0) if i else 0.0, p.y))
    return out


def weld(obj, dist=1e-6):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def tube(name, pts, radii, segs=12, caps=True, mat=None, attr=None):
    """Cev duž polilinije (paralelni transport okvira); attr = vrednost po tački (npr. vreme duž mlaza)."""
    bm = bmesh.new()
    lay = bm.verts.layers.float.new('s') if attr is not None else None
    n = len(pts)
    rings, normal = [], None
    angles = [2 * math.pi * k / segs for k in range(segs)]
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        normal = t.orthogonal().normalized() if normal is None else (normal - t * normal.dot(t)).normalized()
        b = t.cross(normal)
        r = radii[i]
        ring = []
        for a in angles:
            v = bm.verts.new(pts[i] + r * (math.cos(a) * normal + math.sin(a) * b))
            if lay is not None:
                v[lay] = attr[i]
            ring.append(v)
        rings.append(ring)
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
    obj = C.link(bpy.data.objects.new(name, mesh))
    C.smooth(obj)
    if mat:
        C.assign(obj, mat)
    return obj


def mesh_obj(name, verts, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    return C.link(bpy.data.objects.new(name, mesh))


def solidify(obj, thickness, offset=-1.0, subsurf=0):
    m = obj.modifiers.new('Solidify', 'SOLIDIFY')
    m.thickness, m.offset, m.use_even_offset = thickness, offset, True
    if subsurf:
        s = obj.modifiers.new('Subsurf', 'SUBSURF')
        s.levels = s.render_levels = subsurf
    return obj


def displace(obj, name, tex_scale, strength, coord_obj, direction='NORMAL'):
    tex = bpy.data.textures.new(name, 'CLOUDS')
    tex.noise_scale = tex_scale
    tex.noise_depth = 2
    mod = obj.modifiers.new(name, 'DISPLACE')
    mod.texture, mod.texture_coords, mod.texture_coords_object = tex, 'OBJECT', coord_obj
    mod.direction, mod.strength, mod.mid_level = direction, strength, 0.5
    return mod


def value_node(N, label, value=0.0):
    n = N.new('ShaderNodeValue', label=label)
    n.outputs[0].default_value = value
    return n.outputs[0]


def no_deform_blur(ob):
    """Sporo promenljiva geometrija (Boolean nivo): bez deformacionog motion blur-a (štedi vreme)."""
    if hasattr(ob, 'cycles'):
        ob.cycles.use_deform_motion = False


# ---------------------------------------------------------------------------- materijali

def mat_glass_drops(level_fn):
    """Unutrašnja strana bokala: kapljice kondenzacije iznad kafe (kao u videu)."""
    m = GR.mat_glass('StakloKapi', tint=(0.97, 0.98, 0.975), shadow=0.85, smudge=0.03)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    N = C.Nodes(nt)
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    _, _, z = N.sep(P)
    d, c = N.voronoi(P, 420.0, randomness=1.0)
    cr, cg, _ = N.split(c)
    size = N.math('MULTIPLY_ADD', cr, 0.32, 0.12)
    dome = N.math('SUBTRACT', 1.0, N.math('DIVIDE', d, size), clamp=True)
    keep = N.ramp(cg, 0.40, 0.46)
    band = N.mul(N.ramp(z, 0.050, 0.068), N.ramp(z, 0.112, 0.124, 1.0, 0.0))
    fog = value_node(N, 'Kondenzacija', 0.0)            # 0 dok je bokal hladan, 1 kad se napuni vrelom kafom
    h = N.mul(N.mul(N.mul(N.math('SQRT', dome), keep), band), fog)
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(h, 0.0005), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_coffee_liquid(name, foam=False, density=900.0):
    """Kafa: providna površina (IOR 1,34) + Volume Absorption (tamna u sredini, ćilibarna gde je tanka).
    foam=True: na vrhu tanak prsten pene uz staklo; nivo i poluprečnik su Value čvorovi 'Nivo' i
    'Poluprecnik' (ključevi po kadru). Vraća (materijal, nivo, poluprečnik) (utičnice ili None)."""
    m, nt, b, N = C.new_material(name)
    b.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['IOR'].default_value = 1.34
    b.inputs['Roughness'].default_value = 0.03
    out = nt.nodes['Material Output']
    surf = b.outputs['BSDF']
    level = radius = None
    if foam:
        level = value_node(N, 'Nivo', 0.0)
        radius = value_node(N, 'Poluprecnik', 0.045)
        tc = N.new('ShaderNodeTexCoord')
        P = tc.outputs['Object']
        x, y, z = N.sep(P)
        r = N.vmath('LENGTH', N.xyz(x, y, 0.0))
        top = N.ramp(N.sub(z, level), -0.0006, -0.0002)
        edge = N.sub(radius, r)
        vor, _ = N.voronoi(P, 900.0)
        ring = N.mul(N.mul(top, N.ramp(edge, 0.0035, 0.0008)), N.ramp(vor, 0.10, 0.45, 0.45, 0.9))
        pb = N.new('ShaderNodeBsdfPrincipled')
        pb.inputs['Base Color'].default_value = (0.15, 0.080, 0.036, 1.0)
        pb.inputs['Roughness'].default_value = 0.45
        mix = N.new('ShaderNodeMixShader')
        N.put(ring, mix.inputs['Fac'])
        nt.links.new(surf, mix.inputs[1])
        nt.links.new(pb.outputs['BSDF'], mix.inputs[2])
        surf = mix.outputs['Shader']
    nt.links.new(surf, out.inputs['Surface'])
    va = N.new('ShaderNodeVolumeAbsorption')
    va.inputs['Color'].default_value = (0.80, 0.50, 0.12, 1.0)
    va.inputs['Density'].default_value = density
    nt.links.new(va.outputs[0], out.inputs['Volume'])
    return m, level, radius


def mat_water(name='Voda'):
    """Mlaz vode: čisto staklo IOR 1,333; vidljiv samo između s_start i s_end (glava i rep mlaza)."""
    m, nt, b, N = C.new_material(name)
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['IOR'].default_value = 1.333
    b.inputs['Roughness'].default_value = 0.0
    b.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    s = N.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='s').outputs['Fac']
    s0 = value_node(N, 'MlazPocetak', 0.0)
    s1 = value_node(N, 'MlazKraj', 0.0)
    vis = N.mul(N.math('GREATER_THAN', s, s0), N.math('LESS_THAN', s, s1))
    tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader')
    N.put(vis, mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(b.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    return m, s0, s1


def mat_filter_src(obj):
    """Proceduralni papir za pečenje: krep (fine talasaste bore), meki nabori, 3 pregiba od savijanja."""
    m, nt, b, N = C.new_material('FilterIzvor')
    tc = N.new('ShaderNodeTexCoord', object=obj)
    P = tc.outputs['Object']
    x, y, z = N.sep(P)
    th = N.math('ARCTAN2', y, x)
    crepe = N.noise(N.vmath('MULTIPLY', P, (140.0, 140.0, 1100.0)), 1.0, detail=3, rough=0.55, distortion=0.6)
    soft = N.noise(P, 38.0, detail=3)
    h = N.add(N.mul(crepe, 0.000035), N.mul(soft, 0.00030))
    for a0 in (0.6, 2.7, 4.4):
        da = N.math('ABSOLUTE', N.math('SINE', N.mul(N.sub(th, a0), 0.5)))   # ~ugaono rastojanje / 2
        h = N.sub(h, N.mul(N.math('EXPONENT', N.mul(N.mul(da, da), -9000.0)), 0.00025))
    fib = N.noise(P, 900.0, detail=2)
    alb = N.mix(N.ramp(fib, 0.3, 0.7), (0.74, 0.72, 0.68), (0.82, 0.80, 0.76))
    N.put(alb, b.inputs['Base Color'])
    maps = {'albedo': alb, 'height': N.math('MULTIPLY_ADD', h, 1000.0, 1.0)}
    return m, maps


def mat_filter_baked(imgs):
    """Papir iz ispečenih mapa + vlaženje odozdo (Value 'VlagaZ'): mokar papir je tamnosmeđ (kafa iza)."""
    m, nt, b, N = C.new_material('Filter')
    wet_z = value_node(N, 'VlagaZ', 0.0)
    alb, _ = N.image(imgs['albedo'])
    h, _ = N.image(imgs['height'])
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    _, _, z = N.sep(P)
    zz = N.add(z, N.mul(N.sub(N.noise(P, 70.0, detail=3), 0.5), 0.006))
    wet = N.ramp(zz, N.add(wet_z, 0.002), N.sub(wet_z, 0.002), 0.0, 1.0)
    col = N.mix(wet, alb, (0.075, 0.038, 0.016))
    N.put(col, b.inputs['Base Color'])
    N.put(N.mixf(wet, 0.85, 0.42), b.inputs['Roughness'])
    b.inputs['Specular IOR Level'].default_value = 0.35
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 0.001
    N.put(h, bump.inputs['Height'])
    N.put(N.mixf(wet, 1.0, 0.5), bump.inputs['Strength'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    tl = N.new('ShaderNodeBsdfTranslucent')
    N.put(col, tl.inputs['Color'])
    N.put(bump.outputs['Normal'], tl.inputs['Normal'])
    mix = N.new('ShaderNodeMixShader')
    N.put(N.mixf(wet, 0.28, 0.05), mix.inputs['Fac'])
    nt.links.new(b.outputs['BSDF'], mix.inputs[1])
    nt.links.new(tl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    return m


def mat_kettle_src(obj):
    """Proceduralni kovani inox za pečenje: Voronoi udubljenja (uspravno izdužena, ~11 mm), sitni tragovi
    čekića, mrlje i otisci (hrapavost)."""
    m, nt, b, N = C.new_material('KuvaloIzvor')
    tc = N.new('ShaderNodeTexCoord', object=obj)
    P = tc.outputs['Object']
    d1, c1 = N.voronoi(N.vmath('MULTIPLY', P, (1.0, 1.0, 0.62)), 92.0, randomness=0.85)
    d2, _ = N.voronoi(P, 300.0, randomness=1.0)
    dent = N.add(N.mul(N.mul(d1, d1), -0.00020), N.mul(N.mul(d2, d2), -0.00003))
    cr, _, _ = N.split(c1)
    sm = N.ramp(N.noise(P, 14.0, detail=4, distortion=0.5), 0.55, 0.78)
    rough = N.add(N.add(N.math('MULTIPLY_ADD', cr, 0.06, 0.20), N.mul(sm, 0.10)),
                  N.mul(N.noise(N.vmath('MULTIPLY', P, (30.0, 30.0, 1800.0)), 1.0, detail=2), 0.05))
    maps = {'height': N.math('MULTIPLY_ADD', dent, 1000.0, 1.0), 'rough': rough}
    return m, maps


def mat_kettle_baked(imgs):
    m, nt, b, N = C.new_material('Kuvalo')
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Base Color'].default_value = (0.50, 0.49, 0.475, 1.0)
    h, _ = N.image(imgs['height'])
    r, _ = N.image(imgs['rough'])
    N.put(N.split(r)[0], b.inputs['Roughness'])
    b.inputs['Anisotropic'].default_value = 0.55
    tan = N.new('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    N.put(tan.outputs['Tangent'], b.inputs['Tangent'])
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 0.001
    N.put(N.split(h)[0], bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def baked_material(obj, src_fn, baked_fn, name, size, rebake, *extra):
    """Peče proceduralne mape objekta (po UV mapi) u cache/<name>_<otisak>_<kanal>.exr i vraća materijal iz
    tekstura; promena koda materijala ili geometrije = novo pečenje."""
    src, maps = src_fn(obj)
    C.assign(obj, src)
    key = C.source_key(src_fn, baked_fn, *extra, size, len(obj.data.vertices))
    paths = {k: CACHE / f'{name}_{key}_{k}.exr' for k in maps}
    if rebake or not all(p.exists() for p in paths.values()):
        for old in CACHE.glob(f'{name}_*.exr'):
            if key not in old.name:
                old.unlink()
        t0 = time.time()
        C.bake_maps(obj, src, maps, paths, size[0], size[1], samples=4)
        print(f'POUR pečenje {name}: {size[0]}x{size[1]}, {len(maps)} mape, {time.time() - t0:.0f} s', flush=True)
    m = baked_fn(C.load_maps(paths))
    C.assign(obj, m)
    bpy.data.materials.remove(src)
    return m


def mat_bed():
    """Površina u filteru: suva mlevena kafa -> bloom (tamni od sredine) -> tečna kafa sa penom.
    Value čvorovi 'Bloom' (poluprečnik mokrog kruga, m) i 'Mokro' (0..1) se ključaju po kadru."""
    m, nt, b, N = C.new_material('PovrsinaFiltera')
    bloom_r = value_node(N, 'Bloom', 0.0)
    wetness = value_node(N, 'Mokro', 0.0)
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    x, y, _ = N.sep(P)
    r = N.vmath('LENGTH', N.xyz(x, y, 0.0))
    grain = N.noise(P, 900.0, detail=2)
    dry = N.mix(N.ramp(grain, 0.3, 0.7), (0.085, 0.048, 0.026), (0.150, 0.088, 0.050))
    wet_m = N.mul(N.ramp(N.sub(r, bloom_r), 0.002, -0.002), 1.0)
    swirl = N.noise(P, 160.0, detail=4, distortion=1.2)
    foam = N.mix(N.ramp(swirl, 0.35, 0.70), (0.040, 0.020, 0.009), (0.19, 0.105, 0.048))
    bub, _ = N.voronoi(P, 1400.0)
    foam = N.mix(N.mul(N.ramp(bub, 0.28, 0.06), 0.5), foam, (0.26, 0.15, 0.07))
    col = N.mix(N.math('MAXIMUM', wet_m, wetness), dry, foam)
    N.put(col, b.inputs['Base Color'])
    N.put(N.mixf(N.math('MAXIMUM', wet_m, wetness), 0.92, 0.22), b.inputs['Roughness'])
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.add(N.mul(grain, 0.00008), N.mul(N.sub(0.3, bub), 0.00003)), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    return m


# ---------------------------------------------------------------------------- modeli

def bokal(glass, glass_drops):
    prof = profil(SERVER_PROFIL, 4)
    srv = C.lathe('Server', prof, segments=160)
    for v in srv.data.vertices:            # kljun na -X: gornja ivica se izvlači napolje
        x, y, z = v.co
        th = math.atan2(y, x)
        d = math.pi - abs(th)
        w = math.exp(-(d / 0.30) ** 2) * min(1.0, max(0.0, (z - 0.106) / 0.024)) ** 1.6
        if w > 1e-4:
            r = math.hypot(x, y) + 0.014 * w
            v.co = (r * math.cos(th), r * math.sin(th), z)
    weld(srv)
    C.assign(srv, glass)
    srv.data.materials.append(glass_drops)
    solidify(srv, SERVER_DEBLJINA, -1.0, subsurf=1)
    srv.modifiers['Solidify'].material_offset = 1
    pts = catmull([(0.034, 0, 0.1166), (0.052, 0, 0.1193), (0.071, 0, 0.1144), (0.080, 0, 0.0968),
                   (0.080, 0, 0.0704), (0.071, 0, 0.0506), (0.054, 0, 0.0407), (0.045, 0, 0.0396)], 8)
    h = tube('ServerHandle', pts, [0.0045] * len(pts), segs=16, mat=glass)
    return [srv, h]


def tecnost_bokal(mat_name):
    """Kafa u bokalu: šupljina bokala presečena kockom čija visina prati nivo (Boolean, egzaktno)."""
    outer = [p for p in profil(SERVER_PROFIL, 4) if p[1] <= 0.106]
    inner = offset_profil(outer, SERVER_DEBLJINA + 0.0003)
    liq = weld(C.lathe('KafaBokal', inner + [(0.0, inner[-1][1])], segments=128))
    cut = mesh_obj('NivoBokala', [(-.1, -.1, -.2), (.1, -.1, -.2), (.1, .1, -.2), (-.1, .1, -.2),
                                  (-.1, -.1, 0), (.1, -.1, 0), (.1, .1, 0), (-.1, .1, 0)],
                   [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    cut.hide_render = True
    cut.display_type = 'WIRE'
    bo = liq.modifiers.new('Nivo', 'BOOLEAN')
    bo.operation, bo.solver, bo.object = 'INTERSECT', 'EXACT', cut
    no_deform_blur(liq)

    def r_in(h):
        for (r0, z0), (r1, z1) in zip(inner, inner[1:]):
            if z0 <= h <= z1 and z1 > z0:
                return r0 + (r1 - r0) * (h - z0) / (z1 - z0)
        return inner[-1][0]
    return liq, cut, r_in


def dripper(glass):
    z0, z1 = PLOCA_Z
    objs = []
    plate = [(KONUS_R0, z0), (0.050, z0), (0.0532, z0 + 0.0009), (0.0542, (z0 + z1) / 2),
             (0.0532, z1 - 0.0009), (0.050, z1), (KONUS_R0 + 0.002, z1), (KONUS_R0, z0)]
    p = weld(C.lathe('DripperPlate', plate, segments=160))
    C.assign(p, glass)
    objs.append(p)
    foot = C.lathe('DripperFoot', [(0.0345, z0 - 0.0125), (0.0345, z0)], segments=96)
    C.assign(foot, glass)
    solidify(foot, 0.0018, 1.0)
    objs.append(foot)
    cone_pts = [(r_konus(z), z) for z in [z1 + i * (KONUS_Z1 - z1) / 10 for i in range(11)]]
    cone_pts += [(0.0562, KONUS_Z1 + 0.0020), (0.0588, KONUS_Z1 + 0.0031), (RIM_R, KONUS_Z1 + 0.0025)]
    cone = C.lathe('DripperCone', profil(cone_pts, 3), segments=160)
    C.assign(cone, glass)
    solidify(cone, 0.0025, 1.0, subsurf=1)
    objs.append(cone)
    for k in range(12):                    # spiralna rebra (svetle linije kao u videu)
        th0 = 2 * math.pi * k / 12
        pts, rad = [], []
        for i in range(40):
            u = i / 39
            z = z1 + 0.0075 + u * 0.067
            th = th0 + 0.85 * u
            r = r_konus(z) + 0.0029 - 0.0002
            pts.append(Vector((r * math.cos(th), r * math.sin(th), z)))
            rad.append(0.0009 * min(1.0, 4 * u, 4 * (1 - u)) + 0.0002)
        objs.append(tube(f'Rib{k:02d}', pts, rad, segs=8, mat=glass))
    dz = KONUS_Z1 - 0.2035
    hp = catmull([(0.048, 0, 0.199 + dz), (0.064, 0, 0.2015 + dz), (0.078, 0, 0.197 + dz), (0.0855, 0, 0.185 + dz),
                  (0.086, 0, 0.170 + dz), (0.079, 0, 0.157 + dz), (0.064, 0, 0.150 + dz), (0.045, 0, 0.148 + dz),
                  (0.024, 0, 0.150 + dz)], 8)
    objs.append(tube('DripperHandle', hp, [0.0037] * len(hp), segs=14, mat=glass))
    return objs


def filter_papir(rebake):
    """V60 filter: pravi konus 60° uz rebra (2,2 mm od stakla), iznad ivice nastavlja konus ~1,8 cm sa
    blago talasastim, isečenim rubom; preklopljen šav sa strane."""
    top = KONUS_Z1 + FILTER_IZNAD
    zs = [FILTER_VRH + 0.0008] + [FILTER_VRH + 0.002 + i * (top - FILTER_VRH - 0.002) / 40 for i in range(41)]
    prof = [(0.0004, FILTER_VRH)] + [(r_filter(z), z) for z in zs]
    f = C.lathe('Filter', prof, segments=192, uv=arc_v(prof))
    for v in f.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        s = min(1.0, max(0.0, (z - KONUS_Z1 + 0.002) / (top - KONUS_Z1 + 0.002)))
        if s <= 0:
            continue
        wob = 0.5 * math.sin(3 * th + 0.7) + 0.3 * math.sin(5 * th + 2.1) + 0.2 * math.sin(9 * th + 0.3)
        r = math.hypot(x, y) * (1 + 0.012 * wob * s * s)
        v.co = (r * math.cos(th), r * math.sin(th), z + 0.0010 * wob * s ** 2)
    weld(f)
    solidify(f, 0.00025, 1.0)
    m = baked_material(f, mat_filter_src, mat_filter_baked, 'filter', (4096, 1024), rebake, prof)
    th_s = math.radians(-118)                 # šav spreda levo
    seam_v, seam_f = [], []
    for i in range(13):
        z = FILTER_VRH + 0.006 + i * (top - 0.0010 - FILTER_VRH - 0.006) / 12
        r = r_filter(z) + 0.0003
        for dth in (0.0, 0.085):
            seam_v.append(((r) * math.cos(th_s + dth), (r) * math.sin(th_s + dth), z))
        if i:
            k = 2 * i
            seam_f.append((k - 2, k - 1, k + 1, k))
    seam = mesh_obj('FilterSav', seam_v, seam_f)
    C.smooth(seam)
    C.assign(seam, m)
    solidify(seam, 0.0003, 0.0)
    bed = weld(C.lathe('PovrsinaFiltera', [(1.0, 0.0006), (0.6, 0.0), (0.2, -0.0005), (0.0, -0.0007)], segments=128))
    return [f, seam], bed


def kuvalo(steel_pol, black):
    """Gooseneck kuvalo (uspravno, izliv ka -X). Telo ima kovane redove u geometriji + ispečene sitne
    tragove čekića; izliv je šupalj (bez crnog diska). Vraća rig, telo, vrh i pravac izliva, sve delove."""
    rig = C.link(bpy.data.objects.new('KuvaloRig', None))
    body_prof = profil([
        (0.000, 0.003), (0.050, 0.003), (0.061, 0.005), (0.0655, 0.010), (0.0665, 0.020),
        (0.0625, 0.045), (0.0580, 0.072), (0.0530, 0.098), (0.0480, 0.118), (0.0430, 0.129),
        (0.0375, 0.1345), (0.0340, 0.137)], 6)
    body = C.lathe('KuvaloTelo', body_prof, segments=192, uv=arc_v(body_prof))

    def dimple(th, z):
        lo, hi, row_h, nn = 0.022, 0.126, 0.026, 16
        if z <= lo or z >= hi:
            return 0.0
        u = (z - lo) / row_h
        row = math.floor(u)
        a = 0.5 + 0.5 * math.cos(nn * (th + (row % 2) * math.pi / nn))
        return a ** 1.5 * math.sin(math.pi * (u - row)) * min(1.0, (z - lo) / 0.008, (hi - z) / 0.008)

    for v in body.data.vertices:
        x, y, z = v.co
        th = math.atan2(y, x)
        r = math.hypot(x, y) * (1 - 0.010 * dimple(th, z))
        v.co = (r * math.cos(th), r * math.sin(th), z)
    weld(body)
    sub = body.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    lid = weld(C.lathe('KuvaloPoklopac', profil([(0.0335, 0.1368), (0.0328, 0.1400), (0.0285, 0.1445),
                                                 (0.020, 0.1475), (0.010, 0.1490), (0.0, 0.1493)], 4), 128))
    C.assign(lid, steel_pol)
    solidify(lid, 0.0012, -1.0)
    knob = weld(C.lathe('KuvaloDugme', profil([(0.0, 0.1480), (0.0095, 0.1480), (0.0105, 0.1500), (0.0108, 0.1560),
                                               (0.0100, 0.1610), (0.0075, 0.1635), (0.0, 0.1645)], 3), 64))
    C.assign(knob, black)
    base_ring = weld(C.lathe('KuvaloDno', [(0.0, 0.0), (0.050, 0.0), (0.0605, 0.0012), (0.0635, 0.0048),
                                            (0.0650, 0.0080), (0.0, 0.0080)], 128))
    C.assign(base_ring, black)
    sp = [(-0.040, 0, 0.018), (-0.068, 0, 0.030), (-0.088, 0, 0.050), (-0.104, 0, 0.075), (-0.117, 0, 0.098),
          (-0.128, 0, 0.115), (-0.138, 0, 0.125), (-0.148, 0, 0.129), (-0.157, 0, 0.127), (-0.164, 0, 0.122)]
    spts = catmull(sp, 10)
    srad = [0.0033 + 0.0058 * (1 - i / (len(spts) - 1)) ** 2.2 for i in range(len(spts))]
    spout = tube('KuvaloIzliv', spts, srad, segs=24, caps=False, mat=steel_pol)
    solidify(spout, 0.0007, -1.0)               # šupalj vrh sa ivicom, voda izlazi iznutra
    tip, tip_dir = spts[-1], (spts[-1] - spts[-3]).normalized()
    hp = catmull([(0.036, 0, 0.132), (0.058, 0, 0.142), (0.084, 0, 0.140), (0.102, 0, 0.125), (0.107, 0, 0.095),
                  (0.100, 0, 0.062), (0.082, 0, 0.038), (0.058, 0, 0.026)], 8)
    handle = tube('KuvaloDrska', hp, [0.0058] * len(hp), segs=16, mat=black)
    parts = [body, lid, knob, base_ring, spout, handle]
    for o in parts:
        o.parent = rig
    return rig, body, tip, tip_dir, parts


def mlaz_putanja(tip_w, d, z_end):
    """Balistička putanja vode iz izliva, tačke na jednakim vremenskim koracima (s = vreme 0..1)."""
    g = Vector((0, 0, -9.81))
    v0 = d * MLAZ_BRZINA
    a, b, c = 0.5 * g.z, v0.z, tip_w.z - z_end
    t_end = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    pts, rad, s = [], [], []
    n = 160
    t0 = -0.006 / MLAZ_BRZINA
    for i in range(n):
        u = i / (n - 1)
        t = t0 + (t_end - t0) * u
        tt = max(t, 0.0)
        pts.append(tip_w + v0 * t + 0.5 * g * tt * tt)
        speed = (v0 + g * tt).length
        rad.append(MLAZ_R0 * math.sqrt(MLAZ_BRZINA / speed))
        s.append(u)
    return pts, rad, s, t_end


def postavi_kuvalo(rig, tip_local, dir_local):
    """Kuvalo se naginje oko drške (ruka), kao pravo: pri nagibu za sipanje vrh izliva je na tip_w, odakle
    mlaz pada tačno u x=0, y=0 (sredina filtera); u mirovanju je izliv viši i desno."""
    rot = Euler((0, -math.radians(KUVALO_NAGIB[1]), math.radians(KUVALO_ZAOKRET)), 'XYZ')
    R = rot.to_matrix()
    d = R @ dir_local
    v0 = d * MLAZ_BRZINA
    a, b, c = -0.5 * 9.81, v0.z, VRH_Z - SLETANJE_Z
    t_land = (-b - math.sqrt(b * b - 4 * a * c)) / (2 * a)
    tip_w = Vector((-v0.x * t_land, -v0.y * t_land, VRH_Z))
    pivot = C.link(bpy.data.objects.new('KuvaloPivot', None))
    pivot.location = tip_w - R @ (Vector(tip_local) - DRSKA)
    pivot.rotation_euler = rot
    rig.parent = pivot
    rig.location = -DRSKA
    return pivot, tip_w, d


def kapi_i_mlaz_kafe(mat):
    """Kapanje iz V60: kapi (G130-G138), tanak mlaz (G138-G182), retke kapi posle. Sve po kadru G."""
    z_top = FILTER_VRH - 0.0006
    objs = []
    # tanak mlaz: jedinična cev od 0 do -1, skala po z = dužina; vrh i dno se animiraju
    pts = [Vector((0, 0, -i / 120)) for i in range(121)]
    rad = [1.0 - 0.25 * (i / 120) ** 0.7 for i in range(121)]
    st = tube('KafaMlaz', pts, rad, segs=12, mat=mat)
    flow = C.link(bpy.data.objects.new('KafaMlazTok', None))
    displace(st, 'KafaTalasici', 0.004, 0.30, flow)      # u jedinicama poluprečnika (cev je skalirana)
    no_deform_blur(st)
    objs.append(st)
    g_on, g_off = 136, 182
    dt = GR.SLOW / GR.FPS
    for g in range(GR.G_POUR[0], GR.G_POUR[1] + 1):
        lvl = carafe_level(g) + 0.0005
        full = z_top - lvl
        head = full * min(1.0, max(0.0, (0.5 * 9.81 * ((g - g_on) * dt) ** 2) / full)) if g >= g_on else 0.0
        tail = min(full, 0.5 * 9.81 * ((g - g_off) * dt) ** 2) if g >= g_off else 0.0
        r = 0.0013 * GR.smoothstep(136, 150, g) * (1 - 0.35 * GR.smoothstep(168, 182, g)) + 0.0006
        visible = head - tail > 0.0008
        st.location = (0.0, 0.0, z_top - tail)
        st.scale = (r, r, max(head - tail, 0.0005))
        st.hide_render = not visible
        st.keyframe_insert('location', frame=sf(g))
        st.keyframe_insert('scale', frame=sf(g))
        st.keyframe_insert('hide_render', frame=sf(g))
        flow.location = (0, 0, 0.25 * g * dt)
        flow.keyframe_insert('location', frame=sf(g))
    # kapi: pre mlaza i posle njega
    drops = [130, 133, 135.5] + [184.5, 188, 191]
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0)
    for v in bm.verts:
        v.co = (v.co.x * 0.0017, v.co.y * 0.0017, v.co.z * (0.0022 if v.co.z > 0 else 0.0017))
    me = bpy.data.meshes.new('Kap')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    for k, g0 in enumerate(drops):
        ob = C.link(bpy.data.objects.new(f'Kap{k}', me))
        for g in range(GR.G_POUR[0], GR.G_POUR[1] + 1):
            t = (g - g0) * dt
            z = z_top - 0.0015 - 0.5 * 9.81 * max(t, 0.0) ** 2
            hit = z < carafe_level(g) + 0.001
            ob.location = (0.0, 0.0, max(z, carafe_level(g)))
            ob.hide_render = t < 0 or hit
            ob.keyframe_insert('location', frame=sf(g))
            ob.keyframe_insert('hide_render', frame=sf(g))
        objs.append(ob)
    return objs


def zrna_na_pultu(render_meshes):
    """4 zrna na pultu desno od bokala (statična, kontaktna senka na shadow catcher-u)."""
    objs = []
    spots = [((0.074, -0.034), 35, False, 3), ((0.091, -0.018), -70, True, 7), ((0.112, -0.040), 12, False, 1),
             ((0.128, -0.022), 98, True, 10)]
    for i, ((x, y), rz, flip, shape) in enumerate(spots):
        ob = C.link(bpy.data.objects.new(f'ZrnoPult{i}', render_meshes[shape]))
        sh = GR.bean_shape(shape)
        ob.location = (x, y, sh['tb'] * 0.85 if not flip else sh['tt'] * 0.92)
        ob.rotation_euler = (math.pi if flip else 0.0, 0.0, math.radians(rz))
        objs.append(ob)
    return objs


# ---------------------------------------------------------------------------- scena

def parse():
    p = argparse.ArgumentParser(prog='pour.py')
    p.add_argument('--out', required=True, help='folder za kadar_LLLL.png (L = G - 64) i anchors.json')
    p.add_argument('--kadrovi', default='sve', help="'sve' ili lista globalnih G, npr. 84,150,192")
    p.add_argument('--res', type=int, default=1200)
    p.add_argument('--uzorci', type=int, default=64)
    p.add_argument('--adaptive', type=float, default=0.02)
    p.add_argument('--fstop', type=float, default=GR.FSTOP)
    p.add_argument('--key', type=float, default=70.0)
    p.add_argument('--strip', type=float, default=6.0)
    p.add_argument('--mleveno', type=int, default=600, help='čestica mlevene kafe po kadru (isto kao GRIND)')
    p.add_argument('--odsjaj', type=float, default=3.0, help='blenda levo-napred (samo odsjaj), W')
    p.add_argument('--poster', action='store_true', help='poster.png = G150')
    p.add_argument('--bez-zamucenja', dest='bez_zamucenja', action='store_true')
    p.add_argument('--ponovo-peci', dest='ponovo_peci', action='store_true', help='ponovo ispeci mape')
    p.add_argument('--bez-rendera', dest='bez_rendera', action='store_true')
    return p.parse_args(C.args())


def build(a):
    sc = C.reset()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    GR.render_setup(sc, a.res, a.res, a.uzorci, a.adaptive, motion_blur=not a.bez_zamucenja)
    sc.frame_start, sc.frame_end = sf(GR.G_POUR[0]), sf(GR.G_POUR[1])
    C.world_hdri(sc, 0.15)
    cam = GR.rig_camera(sc, 'pour', a.res, a.fstop)
    GR.transmission_card(sc, GR.BG_POUR, GR.LIGHT_TARGET - Vector((0, 0, GR.S)), glossy_bounces=1)

    glass = GR.mat_glass('Staklo', tint=(0.97, 0.98, 0.975), shadow=0.85, smudge=0.04)
    steel_pol = GR.mat_steel('KuvaloIzlivInox', rough=0.14, aniso=0.4, prints=False, smudge=0.8)
    black = GR.mat_plastic('KuvaloCrno', color=(0.014, 0.013, 0.012), rough=0.45)

    subjects = []
    liq, cut, r_in = tecnost_bokal('KafaBokal')
    coffee_mat, lvl_v, rad_v = mat_coffee_liquid('KafaBokal', foam=True)
    C.assign(liq, coffee_mat)
    C.assign(cut, coffee_mat)
    subjects.append(liq)
    drops_mat = mat_glass_drops(carafe_level)
    fog_v = next(n for n in drops_mat.node_tree.nodes if n.label == 'Kondenzacija').outputs[0]
    subjects += bokal(glass, drops_mat)
    subjects += dripper(glass)
    filt_objs, bed = filter_papir(a.ponovo_peci)
    fmat = filt_objs[0].data.materials[0]
    wet_v = next(n for n in fmat.node_tree.nodes if n.label == 'VlagaZ').outputs[0]
    subjects += filt_objs
    bed_mat = mat_bed()
    bloom_v = next(n for n in bed_mat.node_tree.nodes if n.label == 'Bloom').outputs[0]
    wetness_v = next(n for n in bed_mat.node_tree.nodes if n.label == 'Mokro').outputs[0]
    C.assign(bed, bed_mat)
    subjects.append(bed)

    rig, body, tip_l, dir_l, kparts = kuvalo(steel_pol, black)
    baked_material(body, mat_kettle_src, mat_kettle_baked, 'kuvalo', (2048, 1024), a.ponovo_peci, kuvalo)
    pivot, tip_w, d = postavi_kuvalo(rig, tip_l, dir_l)
    subjects += kparts
    pts, rad, s_attr, t_fall = mlaz_putanja(tip_w, d, SLETANJE_Z - 0.004)
    water_mat, s0, s1 = mat_water()
    stream = tube('MlazVode', pts, rad, segs=14, caps=True, mat=water_mat, attr=s_attr)
    flow = C.link(bpy.data.objects.new('MlazVodeTok', None))
    sway = C.link(bpy.data.objects.new('MlazVodeNjihanje', None))
    displace(stream, 'VodaTalasici', 0.0045, 0.00045, flow)
    displace(stream, 'VodaNjihanje', 0.035, 0.0009, sway, 'X')
    subjects.append(stream)

    drip_mat, _, _ = mat_coffee_liquid('KafaKapi', foam=False, density=900.0)
    subjects += kapi_i_mlaz_kafe(drip_mat)
    render_meshes, proxy_meshes, _ = GR.bean_meshes()
    for pm in proxy_meshes:
        bpy.data.meshes.remove(pm)
    beans = zrna_na_pultu(render_meshes)

    # senka samo na pultu: od prednje ivice kadra do zadnje ivice pulta (y = PULT_ZADNJA); iza je zid sekcije,
    # pa bi senka iza te linije visila po pozadini
    catcher = mesh_obj('Senka', [(-0.24, -0.30, 0.0), (0.26, -0.30, 0.0), (0.26, PULT_ZADNJA, 0.0),
                                 (-0.24, PULT_ZADNJA, 0.0)], [(0, 1, 2, 3)])
    catcher.name = 'Senka'
    catcher.is_shadow_catcher = True
    catcher.visible_transmission = False
    catcher.visible_glossy = False

    em, crumbs = GR.build_grounds(sc, a.mleveno, end_g=GR.G_POUR[1])
    # trake pozadi i blenda samo na staklo, inox i vodu (papir i zrna bi isprale u sivo)
    shiny = [o for o in subjects if o not in filt_objs and o is not bed]
    GR.lights(sc, 'pour', shiny, crumbs, key=a.key, strip=a.strip, refl=a.odsjaj, refl_subjects=kparts)
    # pult: nizak key baca dugu senku unazad, do zadnje ivice pulta (tu i u stvarnosti pada sa ivice). Svetla
    # sa light linking-om na shadow catcher-u ne koristiti: catcher tada zatamni ceo pult jednolično.

    # ---------------- animacija po kadru G
    dt = GR.SLOW / GR.FPS
    rest = pivot.rotation_euler.copy()
    rest_loc = pivot.location.copy()
    for g in range(GR.G_POUR[0], GR.G_POUR[1] + 1):
        f = sf(g)
        tilt = kettle_tilt(g) + 0.25 * math.sin(2 * math.pi * (g - 118) / 40.0) * GR.smoothstep(118, 126, g) \
            * (1 - GR.smoothstep(160, 166, g))
        pivot.rotation_euler = (rest.x, -math.radians(tilt), rest.z)
        pivot.keyframe_insert('rotation_euler', frame=f)
        away = 1.0 - GR.smoothstep(98, 112, g) + GR.smoothstep(166, 180, g)
        pivot.location = rest_loc + Vector((KUVALO_SKLONJENO[0], 0.0, KUVALO_SKLONJENO[1])) * away
        pivot.keyframe_insert('location', frame=f)
        # mlaz vode: glava izlazi G112 (kuvalo je nagnuto) i stiže do filtera za t_fall; rep kreće G166
        fall_frames = t_fall / dt
        s1.default_value = min(1.0, max(0.0, (g - 112) / fall_frames)) if g >= 112 else 0.0
        s0.default_value = min(1.0, max(0.0, (g - 166) / fall_frames)) if g >= 166 else 0.0
        s1.keyframe_insert('default_value', frame=f)
        s0.keyframe_insert('default_value', frame=f)
        stream.hide_render = not (112 <= g <= 166 + fall_frames + 1)
        stream.keyframe_insert('hide_render', frame=f)
        flow.location = (0, 0, 0.30 * g * dt)
        sway.location = (0, 0, 0.05 * g * dt)
        flow.keyframe_insert('location', frame=f)
        sway.keyframe_insert('location', frame=f)
        # površina u filteru, bloom i vlaga papira
        zf = filter_level(g)
        bed.location = (0, 0, zf)
        rr = r_filter(zf) - 0.0005
        bed.scale = (rr, rr, 1.0)
        bed.keyframe_insert('location', frame=f)
        bed.keyframe_insert('scale', frame=f)
        bloom_v.default_value = 0.06 * GR.smoothstep(116, 132, g)
        wetness_v.default_value = GR.smoothstep(126, 140, g)
        bloom_v.keyframe_insert('default_value', frame=f)
        wetness_v.keyframe_insert('default_value', frame=f)
        wz = max(filter_level(x) for x in range(65, g + 1)) + 0.004 if g >= 116 else FILTER_VRH - 0.01
        wet_v.default_value = wz
        wet_v.keyframe_insert('default_value', frame=f)
        # bokal
        lv = carafe_level(g)
        cut.location = (0, 0, lv if lv > 0.0005 else -0.5)
        cut.keyframe_insert('location', frame=f)
        lvl_v.default_value = lv
        lvl_v.keyframe_insert('default_value', frame=f)
        fog_v.default_value = GR.smoothstep(136, 170, g)
        fog_v.keyframe_insert('default_value', frame=f)
        rad_v.default_value = r_in(max(lv, 0.001))
        rad_v.keyframe_insert('default_value', frame=f)
    GR.bake_particles(sc)
    return sc, cam, r_in, tip_w


def main():
    a = parse()
    t0 = time.time()
    sc, cam, r_in, tip_w = build(a)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sc.frame_set(sf(150))
    rim_z = KONUS_Z1 + 0.0025
    cx, cy = GR.project(sc, cam, (0, 0, rim_z), 'pour')
    rx = GR.project(sc, cam, (RIM_R, 0, rim_z), 'pour')[0] - cx
    ry = GR.project(sc, cam, (0, -RIM_R, rim_z), 'pour')[1] - cy
    kafa = []
    for g in range(177, 193):
        lv = carafe_level(g)
        kafa.append(round(GR.project(sc, cam, (0, -r_in(lv), lv), 'pour')[1], 4))
    GR.write_anchors(out, {'id': 'pour', 'units': 'S od gornjeg levog ugla punog kadra (W 1, H 1)',
                           'full': {'W': 1, 'H': 1}, 'osa_x': round(GR.project(sc, cam, (0, 0, 0.2), 'pour')[0], 4),
                           'ivica_v60': {'x': round(cx, 4), 'y': round(cy, 4), 'rx': round(rx, 4), 'ry': round(ry, 4)},
                           'pult_y': round(GR.project(sc, cam, (0, PULT_ZADNJA, 0), 'pour')[1], 4),
                           'baza_y': round(GR.project(sc, cam, (0, -0.028, 0), 'pour')[1], 4),
                           'kafa_y': {'from': 177, 'values': kafa}, 'g_od': GR.G_POUR[0], 'g_do': GR.G_POUR[1],
                           'fajl': 'kadar_LLLL.png, L = G - 64', 'generator': 'scripts/blender/kafa/pour.py'})
    kb = [o for o in bpy.data.objects if o.name.startswith('Kuvalo') and o.type == 'MESH']
    print(f'POUR scena {time.time() - t0:.0f} s; vrh izliva {tuple(round(c, 4) for c in tip_w)}; '
          f'V60 ({cx:.3f}, {cy:.3f}) rx {rx:.3f} ry {ry:.3f}', flush=True)
    if a.bez_rendera:
        for g in (100, 150):
            sc.frame_set(sf(g))
            xs, ys = [], []
            for o in kb:
                for c in o.bound_box:
                    x, y = GR.project(sc, cam, o.matrix_world @ Vector(c), 'pour')
                    xs.append(x)
                    ys.append(y)
            print(f'POUR kuvalo G{g}: x {min(xs):.3f}..{max(xs):.3f}, y {min(ys):.3f}..{max(ys):.3f} S', flush=True)
        return
    for g in GR.frame_list(a.kadrovi, GR.G_POUR):
        t1, c1 = time.time(), time.process_time()
        sc.frame_set(sf(g))
        sc.render.filepath = str(out / f'kadar_{g - GR.G_POUR[0] + 1:04d}.png')
        bpy.ops.render.render(write_still=True)
        cpu = time.process_time() - c1
        print(f'POUR kadar G{g} (kadar_{g - GR.G_POUR[0] + 1:04d}): {time.time() - t1:.1f} s zidno, {cpu:.0f} CPU-s '
              f'(~{cpu / 4:.0f} s na 4 slobodna jezgra)', flush=True)
    if a.poster:
        p150 = out / f'kadar_{150 - GR.G_POUR[0] + 1:04d}.png'
        if not p150.exists():
            sc.frame_set(sf(150))
            sc.render.filepath = str(p150)
            bpy.ops.render.render(write_still=True)
        (out / 'poster.png').write_bytes(p150.read_bytes())


if __name__ == '__main__':
    main()
