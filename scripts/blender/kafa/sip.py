"""SIP: keramička šolja (stoneware sa curećom glazurom), kafa sa kremom, po želji tanka para.

Fotorealistična verzija (dokaz 23.10.2026 uz dijagnozu recenzenta, druga runda istog dana). Šolja ulazi
odozgo, okreće se ~28° i smiruje se; poslednjih ~12 % kadrova miruje (kraj skrola). Metri, pod z=0,
centar (0,0), kamera spreda 14° odozgo, lens 85, f/8, kvadrat.

Svetlo je zajednički foto-studio iz common.py (C.photo_studio_lights): tamna okolina (HDRI 0,15), key
prozor 0,6x0,9 m levo-gore-napred iza prozorskog okvira, dve uske trake pozadi, crna zastava desno i niska
blenda levo-napred koja se vidi samo u odsjaju (na boku šolje pri niskoj kameri daje odsjaj prozora); toplo
sunce kroz isti okvir pada SAMO na zid (light linking). Ekspozicija 0, AgX Medium High Contrast.

Glazura i glina su proceduralne (mat_stoneware), ali se za render jednom ispeku u teksture po UV mapi
(albedo, hrapavost/maska, visine za bump i displacement; EXR half u scripts/blender/kafa/cache/, ime nosi
otisak koda materijala, pa promena koda sama traži novo pečenje). --no-bake renderuje direktno proceduralno
(sporije, za razvoj izgleda).

  HDRI „Lebombo" (autor Greg Zaal, Poly Haven), 2k OpenEXR, jedini preuzeti materijal (odobrio direktor)
  stranica:  https://polyhaven.com/a/lebombo
  fajl:      https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/2k/lebombo_2k.exr
  md5:       15daa3dc91907106756355aa0d2a3517 (3,7 MB, ispod 5 MB, pa nije u .gitignore)
  licenca:   CC0 1.0, https://polyhaven.com/license („Our assets are all licensed as CC0"), provereno 23.10.2026
  preuzimanje (pre Blendera; Blender radi bez mreže):
    curl -sS --fail -o scripts/blender/assets/lebombo_2k.exr \
      https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/2k/lebombo_2k.exr

Pokretanje iz korena repoa (uslovi iz .claude/agents/blender-umetnik.md):
    unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \
      -P scripts/blender/kafa/sip.py -- --out <folder> [--frames 1,32,64] [--end 64] [--res 1200] \
      [--samples 64] [--backdrop] [--fstop 8] [--elev 14] [--reflector 0.9] [--poster] [--steam] \
      [--no-bake] [--rebake]

--backdrop: sto i zid boje SIP sekcije (RGB, za probu i poređenje); bez njega providna pozadina sa
senkom na shadow catcher-u (RGBA za sajt). Zrno filma se ne peče u render (ide preko CSS-a);
--grain/--vignette postoje samo za probu. Bez --frames renderuje sve kadrove 1..end.
--poster dodaje poster.png (smiren poslednji kadar). Para je podrazumevano isključena (biće pravi snimak).
"""
import argparse
import math
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

CACHE = pathlib.Path(__file__).resolve().parent / 'cache'     # ispečene mape (u .gitignore, > 5 MB)

# ---------------------------------------------------------------- mere šolje (m)
RIM_Z = 0.0980          # vrh oboda
GLAZE_Z = 0.0560        # srednja linija do koje glazura pokriva telo
COFFEE_Z = 0.0895       # nivo kafe (8,5 mm ispod oboda)
HANDLE_ANGLE = 12.0     # krajnji ugao drške (° oko Z; 0 = drška desno, + = ka nazad)
WALL_Y = 0.20           # zid iza šolje (samo uz --backdrop)

# boje SIP sekcije iz studio/kafa-skrol/dizajn/tokens.css
SIP_BG = '#6E3A27'      # --pp-espresso, pozadina (zid)
SIP_FLOOR = '#7C4532'   # --color-floor, sto ispod šolje

# tekstura šolje: širina = obim (4096 / 306 mm = 13,4 teksela/mm; šolja je ~460 px na 1200 px, pa je to
# ~2,8 teksela po pikselu, dovoljno i za 1600 px), po profilu 14 teksela/mm; dno i unutrašnjost ispod kafe
# se ne vide, pa dobijaju 8 % gustine; drška je traka iznad (u duž drške, v oko preseka)
TEX_W = 4096
TEX_DENSITY = 14000.0   # teksela po metru duž profila
HIDDEN_DENSITY = 0.08
HANDLE_ROWS = 480       # obim preseka drške ~34 mm x 14 teksela/mm
TEX_GAP = 32            # razmak između ostrva (bake margin je 16)


# ---------------------------------------------------------------- pomoćne funkcije


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
def mug_profile_parts():
    """Profil šolje (r, z) po delovima: donja strana, stopa i spoljni zid, obod, unutrašnji zid do dna.

    Tragovi kola i debljina glazure nisu u profilu nego u displacement-u materijala."""
    under = [(0.0005, 0.0030), (0.0120, 0.0031), (0.0235, 0.0030), (0.0262, 0.0024), (0.0275, 0.0011)]
    outer = catmull([(0.0283, 0.0003), (0.0295, 0.0), (0.0309, 0.0004), (0.0317, 0.0030), (0.0334, 0.0058),
                     (0.0380, 0.0097), (0.0427, 0.0163), (0.0462, 0.0252), (0.0481, 0.0362), (0.0487, 0.0480),
                     (0.0485, 0.0610), (0.0480, 0.0750), (0.0474, 0.0870), (0.0470, 0.0955)], steps=7)
    cx, cz, rr = 0.0445, 0.0955, 0.0025       # zaobljen obod
    rim = [(cx + rr * math.cos(a), cz + rr * math.sin(a)) for a in [math.pi * i / 12 for i in range(1, 12)]]
    inner = catmull([(0.0420, 0.0955), (0.0421, 0.0870), (0.0424, 0.0750), (0.0430, 0.0600), (0.0434, 0.0470),
                     (0.0430, 0.0360), (0.0412, 0.0260), (0.0380, 0.0180), (0.0325, 0.0125), (0.0250, 0.0095),
                     (0.0150, 0.0086), (0.0005, 0.0085)], steps=6)
    return under, outer, rim, inner


def mug_profile():
    """Profil šolje (r, z): donja strana -> stopa -> spoljni zid -> obod -> unutrašnji zid -> dno."""
    return [p for part in mug_profile_parts() for p in part]


def mug_atlas():
    """UV raspored teksture šolje: v za svaku tačku profila, (prvi red, broj redova) drške, visina teksture.

    v raste sa dužinom luka profila; skriveni delovi (donja strana, unutrašnjost ispod kafe) su sabijeni."""
    under, outer, rim, inner = mug_profile_parts()
    prof = under + outer + rim + inner
    n_under, n_inner = len(under), len(under) + len(outer) + len(rim)
    rows = [0.0]
    for j in range(len(prof) - 1):
        hidden = j < n_under or (j >= n_inner and min(prof[j][1], prof[j + 1][1]) < COFFEE_Z - 0.003)
        rows.append(rows[-1] + (HIDDEN_DENSITY if hidden else 1.0) * math.dist(prof[j], prof[j + 1]) * TEX_DENSITY)
    h0 = math.ceil(rows[-1]) + TEX_GAP
    height = (h0 + HANDLE_ROWS + TEX_GAP + 31) // 32 * 32
    return [r / height for r in rows], (h0, HANDLE_ROWS), height


def handle_mesh():
    """Pljosnata izvučena drška (presek 1:1,6), postepeno proširena ka spojevima sa telom; vraća mesh."""
    pts = [(0.0425, 0.0868, 1.80), (0.0505, 0.0896, 1.30), (0.0620, 0.0905, 1.06), (0.0735, 0.0858, 1.0),
           (0.0805, 0.0735, 0.98), (0.0808, 0.0590, 0.95), (0.0748, 0.0470, 0.93), (0.0650, 0.0396, 0.96),
           (0.0545, 0.0368, 1.18), (0.0440, 0.0360, 1.80)]
    cu = bpy.data.curves.new('Handle', 'CURVE')
    cu.dimensions = '3D'
    cu.resolution_u = 16
    cu.bevel_depth = 0.0043
    cu.bevel_resolution = 6
    cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(len(pts) - 1)
    for bp, (x, z, rad) in zip(sp.bezier_points, pts):
        bp.co = (x, 0, z)
        bp.radius = rad
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
    ob = C.link(bpy.data.objects.new('HandleCurve', cu))
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    me.transform(Matrix.Diagonal((1.0, 1.6, 1.0, 1.0)))    # 8,6 mm u ravni drške, 13,8 mm poprečno
    return me


def build_mug(rig):
    """Telo i drška u jednom mesh-u sa UV mapom za pečenje (telo po profilu, drška u traci iznad), pa wobble
    i subdivision za displacement. Spoj drške je zaobljen geometrijom (drška se širi ka telu)."""
    v, (h0, rows), height = mug_atlas()
    body = C.lathe('Mug', mug_profile(), segments=160, uv=v)
    body.parent = rig
    n_body = len(body.data.polygons)
    hme = handle_mesh()
    huv = hme.uv_layers[0].data                          # krivulja: u duž drške, v oko preseka
    bm = bmesh.new()
    bm.from_mesh(body.data)
    uv_layer = bm.loops.layers.uv['UVMap']
    vs = [bm.verts.new(vt.co) for vt in hme.vertices]
    for p in hme.polygons:
        try:
            f = bm.faces.new([vs[i] for i in p.vertices])
        except ValueError:
            continue
        for loop, li in zip(f.loops, p.loop_indices):
            u, w = huv[li].uv
            loop[uv_layer].uv = (u, (h0 + w * rows) / height)
    bm.to_mesh(body.data)
    bm.free()
    bpy.data.meshes.remove(hme)
    me = body.data
    for p in me.polygons:
        p.use_smooth = True
    # inner: lice okrenuto ka osi = unutrašnjost šolje (uvek glazirano); handle: drška (bez tragova kola)
    inner = me.attributes.new('inner', 'FLOAT', 'FACE')
    hnd = me.attributes.new('handle', 'FLOAT', 'FACE')
    for p in me.polygons:
        c, n = p.center, p.normal
        is_body = p.index < n_body
        inner.data[p.index].value = 1.0 if is_body and (n.x * c.x + n.y * c.y) < 0 and c.z > 0.006 else 0.0
        hnd.data[p.index].value = 0.0 if is_body else 1.0
    # ručno rađena šolja nije savršeno okrugla
    tex = bpy.data.textures.new('MugWobble', 'CLOUDS')
    tex.noise_scale = 0.035
    d = body.modifiers.new('Wobble', 'DISPLACE')
    d.texture, d.texture_coords, d.strength, d.mid_level = tex, 'LOCAL', 0.0012, 0.5
    s = body.modifiers.new('Subsurf', 'SUBSURF')
    s.levels = s.render_levels = 2                       # isti mesh za pečenje i render
    return body


def build_coffee(rig):
    zc = COFFEE_Z
    prof = [(0.0432, zc + 0.0014), (0.0425, zc + 0.0006), (0.0412, zc + 0.0001), (0.0390, zc), (0.0200, zc),
            (0.0003, zc)]
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


def build_set(backdrop):
    """Sto (i zid uz --backdrop). Bez pozadine sto je shadow catcher: ostaju samo senka i odsjaj."""
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0.6, 0))
    floor = bpy.context.active_object
    floor.name = 'Floor'
    C.assign(floor, C.mat_surface('Floor', SIP_FLOOR, rough=(0.55, 0.75), spec=0.25, bump=0.000035, gain=0.90,
                                  desat=0.35))
    if not backdrop:
        floor.is_shadow_catcher = True
        return floor, None
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, WALL_Y, 0.75))
    wall = bpy.context.active_object
    wall.name = 'Wall'
    wall.scale = (3.0, 1.5, 1.0)
    wall.rotation_euler = (math.radians(90), 0, 0)      # normala ka kameri (-Y)
    C.assign(wall, C.mat_surface('Wall', SIP_BG, rough=(0.80, 0.92), spec=0.3, bump=0.00006, desat=0.35))
    return floor, wall


# ---------------------------------------------------------------- materijali
# podešavanja izgleda glazure (ulaze u otisak keša, pa promena = novo pečenje)
LOOK = dict(
    red=0.92,          # crvena komponenta albeda glazure (-8 %: dokaz je bio previše roze)
    cloud=0.40,        # smeđi oblaci u glazuri (bilo 0,55)
    thin=0.50,         # pojas gde se glazura tanji iznad ivice (bilo 1,0 = do 0,75)
    edge=0.35,         # karamel na samoj ivici glazure (bilo 0,55)
    drip=0.45,         # kapljice i zadebljan rub svetliji, krem (bilo 0,10)
    peb_glaze=0.30,    # reljef zrnaca gline kroz glazuru (bilo 0,55)
    handle_bump=0.40,  # reljef gline na dršci (0,4x)
    spots=1.0,         # smeđe pege kao u referenci
    streak=0.35,       # smeđe pruge od oboda naniže (glazura se tanji i curi)
)


def mat_stoneware(body, seed=7, look=None):
    """Tamnobraon zrnasta glina (mat) + ovsena sivo-zelena glazura sa smeđim pegama koja curi u kapima.

    Displacement (pravo pomeranje temena): tragovi kola u spirali, debljina glazure sa zadebljanom
    ivicom i kapljicama na kraju kapi. Bump: zrnca gline (i kroz glazuru), rupice, krakelir, ogrebotine.
    Vraća (materijal, mape za pečenje): albedo, rough = (hrapavost, hrapavost laka, maska glazure),
    height = (bump, bump laka, displacement) u mm + 1."""
    K = dict(LOOK, **(look or {}))
    m, nt, bsdf, N = C.new_material('Stoneware')
    m.displacement_method = 'DISPLACEMENT'
    out = nt.nodes['Material Output']
    rnd = random.Random(seed)

    tc = N.new('ShaderNodeTexCoord', object=body)
    P = tc.outputs['Object']
    x, y, z = N.sep(P)
    flat = N.xyz(x, y, 0.0)
    r = N.vmath('LENGTH', flat)
    u = N.vmath('NORMALIZE', flat)          # pravac oko ose: šare se ponavljaju bez šava
    theta = N.math('ARCTAN2', y, x)
    inner = N.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='inner').outputs['Fac']
    hnd = N.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='handle').outputs['Fac']

    # --- ivica glazure: talasasta linija + kapi (rastojanje u metrima, < 0 = glazura)
    w1 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=1.3), (3.1, 7.7, 1.9)), 1.0, detail=2, rough=0.45)
    w2 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=4.0), (8.2, 1.3, 4.4)), 1.0, detail=1)
    w3 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=8.0), (2.4, 5.1, 9.3)), 1.0, detail=2)   # 4-8 mm
    z0 = N.add(N.math('MULTIPLY_ADD', N.sub(w1, 0.5), 0.0140, GLAZE_Z), N.mul(N.sub(w2, 0.5), 0.0060))
    z0 = N.math('MULTIPLY_ADD', N.sub(w3, 0.5), 0.0065, z0)
    d = N.sub(z0, z)
    zr = N.add(N.sub(z, z0), GLAZE_Z)          # visina u odnosu na lokalnu liniju glazure (kapi kreću sa nje)

    # kapi: oko kruga (14 mesta, pomak ±6°, ~15% praznina), pa nejednaki razmaci; uz trećinu stoji
    # druga kap na 4-7°, pa se preko smooth-min spajaju u širu kap; jedan širok jezik gde se glazura slegla
    drips = []
    for i in range(14):
        a0 = 2 * math.pi * i / 14 + rnd.uniform(-0.10, 0.10)
        if rnd.random() < 0.15:
            continue
        if not drips:
            drips.append((a0, rnd.uniform(0.0025, 0.0060), rnd.uniform(0.0050, 0.0090), 1.0))
            continue
        drips.append((a0, rnd.uniform(0.0040, 0.0200), rnd.uniform(0.0030, 0.0062), rnd.uniform(0.95, 1.12)))
        if rnd.random() < 0.35:
            drips.append((a0 + rnd.choice((-1, 1)) * rnd.uniform(0.07, 0.12), rnd.uniform(0.0030, 0.0120),
                          rnd.uniform(0.0028, 0.0050), rnd.uniform(0.95, 1.10)))
    beads = None
    for a, length, wid, bead_k in drips:
        top = GLAZE_Z + 0.004
        bot = GLAZE_Z - length
        h = N.mul(r, N.vmath('LENGTH', N.vmath('SUBTRACT', u, (math.cos(a), math.sin(a), 0.0))))
        zc = N.math('MAXIMUM', N.math('MINIMUM', zr, top), bot)
        # kap se sužava naniže (vrat), a na kraju se skuplja u kapljicu
        taper = N.math('MULTIPLY_ADD', N.sub(zc, bot), 0.45 * wid / (top - bot), 0.85 * wid)
        neck = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(zr, zc), 0.0)), taper)
        bead = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(zr, bot + wid * 0.30), 0.0)), wid * bead_k * 0.9)
        beads = bead if beads is None else N.math('MINIMUM', beads, bead)
        d = N.math('SMOOTH_MIN', d, N.math('MINIMUM', neck, bead), 0.0060)
    d = N.math('MULTIPLY_ADD', N.sub(N.noise(P, 240.0, detail=2), 0.5), 0.0018, d)   # neravna ivica
    d = N.math('MULTIPLY_ADD', N.sub(N.noise(P, 800.0, detail=1), 0.5), 0.0007, d)
    d = N.math('MAXIMUM', d, N.mul(hnd, 0.01))                  # drška je gola glina (bez svetlog okovratnika)
    d = N.sub(d, N.mul(inner, 0.02))                            # unutrašnjost je sva glazirana
    nd = N.math('MULTIPLY', d, -1.0)                            # dubina u glazuri od ivice

    mask = N.ramp(d, -0.00018, 0.00018, 1.0, 0.0)
    edge_in = N.ramp(nd, 0.0, 0.0014, 1.0, 0.0)
    halo = N.mul(N.ramp(d, 0.0, 0.0013, 1.0, 0.0), N.ramp(N.noise(P, 160.0), 0.35, 0.65, 0.35, 1.0))

    # --- tragovi kola: spirala (faza raste sa uglom, pa nema šava), nepravilan korak, jače u donjem delu
    phase = N.add(N.math('MULTIPLY_ADD', z, 2 * math.pi / 0.0085, theta), N.mul(N.noise(P, 18.0, detail=3), 5.0))
    ring = N.math('POWER', N.math('MULTIPLY_ADD', N.math('SINE', phase), 0.5, 0.5), 1.3)   # 0..1
    ring = N.mul(ring, N.ramp(N.noise(P, 26.0, detail=2), 0.30, 0.65, 0.45, 1.0))          # negde jedva vidljivi
    ring_env = N.mul(N.ramp(z, 0.009, 0.017), N.mixf(N.ramp(z, 0.050, 0.064), 1.0, 0.35))
    ring_env = N.mul(N.mul(ring_env, N.sub(1.0, hnd)), N.mixf(inner, 1.0, 0.45))
    ring_h = N.mul(N.mul(ring, ring_env), 0.00028)

    # --- debljina glazure: tanka uz ivicu, zadebljan rub (površinski napon), kupole na kapljicama
    lip = N.mul(N.ramp(nd, 0.0, 0.0009), N.ramp(nd, 0.0009, 0.0034, 1.0, 0.50))
    dome = N.ramp(N.math('MULTIPLY', beads, -1.0), 0.0, 0.0030)
    pool = N.ramp(N.noise(P, 70.0, detail=2), 0.40, 0.70)       # glazura se negde nakupi
    glaze_t = N.mul(mask, N.add(N.add(N.mul(lip, 0.00042), N.mul(dome, 0.00040)),
                                N.math('MULTIPLY_ADD', pool, 0.00010, 0.00012)))
    lumpy = N.mul(N.sub(N.noise(P, 35.0, detail=2), 0.5), 0.00012)
    height = N.add(N.add(N.mul(ring_h, N.mixf(mask, 1.0, 0.55)), glaze_t), N.mul(lumpy, N.sub(1.0, hnd)))
    disp = N.new('ShaderNodeDisplacement', space='OBJECT')
    disp.inputs['Midlevel'].default_value = 0.0
    disp.inputs['Scale'].default_value = 1.0
    N.put(height, disp.inputs['Height'])
    N.put(disp.outputs['Displacement'], out.inputs['Displacement'])

    # --- glina: čokoladno-siva, zrnasta (zrnca hvataju svetlo), sitan svetli šamot
    pebble, _ = N.voronoi(P, 850.0, randomness=0.9)
    peb_top = N.ramp(pebble, 0.55, 0.05)                        # 1 na vrhu zrnca
    grain = N.noise(P, 2600.0, detail=1)
    clay_var = N.noise(P, 90.0, detail=4)
    clay = N.mix(clay_var, (0.0080, 0.0055, 0.0045), (0.0165, 0.0115, 0.0090))
    clay = N.mix(N.mul(peb_top, 0.55), clay, (0.040, 0.029, 0.024))
    grog_d, _ = N.voronoi(P, 520.0)
    clay = N.mix(N.mul(N.ramp(grog_d, 0.10, 0.04), 0.7), clay, (0.10, 0.075, 0.058))
    clay = N.mix(N.mul(ring, N.mul(ring_env, 0.30)), clay, (0.034, 0.024, 0.019))   # grebeni malo svetliji
    clay = N.mix(N.mul(halo, 0.6), clay, (0.085, 0.036, 0.016))             # rđasti oreol oko glazure

    # --- glazura: ovsena sivo-zelena; oblaci, gvožđe, reljef gline kroz tanku glazuru, krem kapljice
    gv = N.noise(P, 55.0, detail=5, rough=0.62)
    glaze = N.mix(N.ramp(gv, 0.36, 0.64), (0.092, 0.108, 0.096), (0.305, 0.395, 0.360))
    cloud = N.ramp(N.noise(P, 30.0, detail=4, distortion=0.5), 0.48, 0.72)
    glaze = N.mix(N.mul(cloud, K['cloud']), glaze, (0.14, 0.105, 0.075))         # smeđi oblaci
    top_tone = N.ramp(z, GLAZE_Z + 0.010, RIM_Z - 0.002)                      # ka obodu glazura je tanja
    glaze = N.mix(N.mul(top_tone, 0.15), glaze, (0.21, 0.140, 0.085))
    # smeđe pruge od oboda naniže (glazura se pri pečenju tanji i curi): šum izdužen po visini
    streak = N.ramp(N.noise(N.vmath('MULTIPLY', P, (1.0, 1.0, 0.12)), 70.0, detail=3), 0.50, 0.72)
    streak = N.mul(N.mul(streak, N.ramp(z, GLAZE_Z + 0.006, RIM_Z - 0.010)), N.sub(1.0, inner))
    glaze = N.mix(N.mul(streak, K['streak']), glaze, (0.15, 0.095, 0.055))
    glaze = N.mix(N.mul(ring, N.mul(ring_env, 0.35)), glaze, (0.17, 0.105, 0.060))   # glazura puca na grebenima
    glaze = N.mix(N.mul(peb_top, 0.25), glaze, (0.15, 0.098, 0.060))          # zrnca gline probijaju
    glaze = N.mix(N.mul(N.sub(1.0, pool), 0.15), glaze, (0.24, 0.17, 0.11))    # tanje = toplije
    # pege gvožđa kao u referenci: retke krupnije (1-2,5 mm), mekane mrlje (5-8 mm), sitne pegice
    spot_d, spot_c = N.voronoi(P, 150.0)
    sr, sg, _ = N.split(spot_c)
    spot_r = N.math('MULTIPLY_ADD', sg, 0.16, 0.08)                            # poluprečnik u ćelijama
    spots = N.mul(N.ramp(N.sub(spot_d, spot_r), 0.02, -0.03), N.ramp(sr, 0.35, 0.45))
    spots = N.mul(spots, N.ramp(N.noise(P, 40.0, detail=2), 0.25, 0.45, 0.55, 1.0))
    glaze = N.mix(N.mul(spots, 0.85 * K['spots']), glaze, (0.050, 0.026, 0.013))
    blot = N.mul(N.ramp(N.noise(P, 24.0, detail=3, distortion=0.6), 0.64, 0.76), N.sub(1.0, inner))
    glaze = N.mix(N.mul(blot, 0.45 * K['spots']), glaze, (0.085, 0.050, 0.028))   # mekane smeđe mrlje
    fleck_d, _ = N.voronoi(P, 650.0)
    glaze = N.mix(N.mul(N.ramp(fleck_d, 0.17, 0.05), N.ramp(N.noise(P, 30.0), 0.3, 0.6, 0.4, 0.9)), glaze,
                  (0.09, 0.050, 0.026))                                          # sitne pegice ~0,5 mm
    glaze = N.mix(N.mul(edge_in, K['edge']), glaze, (0.21, 0.115, 0.060))       # tanka ivica -> karamel
    thin = N.mul(N.ramp(nd, 0.0008, 0.0060, 1.0, 0.0), N.ramp(N.noise(P, 48.0, detail=3), 0.35, 0.62, 0.25, 0.75))
    glaze = N.mix(N.mul(N.mul(thin, K['thin']), N.sub(1.0, inner)), glaze, (0.13, 0.080, 0.046))   # tanji pojas
    cream = N.math('MAXIMUM', dome, N.mul(lip, 0.6))
    glaze = N.mix(N.mul(cream, K['drip']), glaze, (0.48, 0.47, 0.40))           # debela kapljica = krem
    rim_brk = N.mul(N.ramp(z, RIM_Z - 0.0085, RIM_Z - 0.0025), N.ramp(N.noise(P, 300.0), 0.25, 0.6, 0.6, 1.0))
    glaze = N.mix(N.mul(rim_brk, 0.92), glaze, (0.10, 0.050, 0.026))         # obod: glazura puca u smeđe
    craze_d, _ = N.voronoi(N.vmath('MULTIPLY', P, (1.0, 1.0, 0.7)), 140.0, feature='DISTANCE_TO_EDGE')
    craze = N.mul(N.ramp(craze_d, 0.0, 0.03, 1.0, 0.0), N.ramp(N.noise(P, 20.0), 0.45, 0.6))
    glaze = N.mix(N.mul(craze, 0.30), glaze, (0.12, 0.075, 0.045))            # krakelir (fine pukotine)
    # mokar trag kafe iznad nivoa, unutra
    wet = N.mul(inner, N.ramp(z, COFFEE_Z + 0.0004, COFFEE_Z + 0.0022, 1.0, 0.0))
    glaze = N.mix(N.mul(wet, 0.6), glaze, (0.05, 0.025, 0.012))
    glaze = N.tint(glaze, (K['red'], 1.0, 1.0))                                # manje crvene = ovsena, ne roze

    albedo = N.mix(mask, clay, glaze)
    N.put(albedo, bsdf.inputs['Base Color'])

    # --- hrapavost: glina mat sa zrncima koja se sjaje; glazura satenska + mrlje od prstiju i ogrebotine
    smudge = N.ramp(N.noise(P, 9.0, detail=3), 0.48, 0.70)
    scratch_d, _ = N.voronoi(N.vmath('MULTIPLY', P, (30.0, 30.0, 420.0)), 1.0, feature='DISTANCE_TO_EDGE')
    scratch = N.mul(N.ramp(scratch_d, 0.0, 0.02, 1.0, 0.0), N.ramp(N.noise(P, 14.0), 0.52, 0.62))
    g_rough = N.add(N.math('MULTIPLY_ADD', gv, 0.05, 0.08), N.add(N.mul(smudge, 0.05), N.mul(craze, 0.04)))
    c_rough = N.add(N.math('MULTIPLY_ADD', smudge, 0.03, 0.05), N.mul(scratch, 0.12))
    k_rough = N.math('MULTIPLY_ADD', N.sub(1.0, peb_top), 0.12, 0.70)
    rough = N.mixf(mask, k_rough, N.mixf(wet, g_rough, 0.08))
    coat_rough = N.mixf(mask, 0.40, c_rough)
    N.put(rough, bsdf.inputs['Roughness'])
    N.put(N.mixf(mask, 0.30, 0.5), bsdf.inputs['Specular IOR Level'])
    N.put(N.mixf(mask, 0.10, 0.25), bsdf.inputs['Coat Weight'])
    N.put(coat_rough, bsdf.inputs['Coat Roughness'])
    # bez subsurface-a: na 1,2 mm i težini 0,12 se nije videlo, a random walk je bio najskuplji deo kadra

    # --- normala: sitni reljef (Bevel shader je izbačen: 4 zraka po tački; spoj drške je zaobljen geometrijom)
    pin, _ = N.voronoi(P, 600.0)                                  # rupice ~0,4 mm (2 px na 1200 px)
    pinholes = N.mul(N.ramp(pin, 0.15, 0.05), N.ramp(N.noise(P, 60.0), 0.52, 0.66))
    peel = N.sub(N.noise(P, 420.0, detail=2), 0.5)                # „pomorandžina kora" glazure, ~2 mm
    peb_h = N.mul(N.sub(1.0, pebble), 0.00016)
    clay_h = N.add(peb_h, N.mul(N.sub(grain, 0.5), 0.00003))
    clay_h = N.mul(clay_h, N.mixf(hnd, 1.0, K['handle_bump']))   # drška je glađa (palac je ugladi)
    glaze_h = N.add(N.add(N.mul(peb_h, K['peb_glaze']), N.mul(pinholes, -0.00010)), N.mul(craze, -0.000006))
    glaze_h = N.add(glaze_h, N.mul(peel, 0.00005))
    bump_h = N.mixf(mask, clay_h, glaze_h)
    coat_h = N.add(N.add(N.mul(pinholes, -0.00010), N.mul(N.mul(scratch, mask), -0.000003)), N.mul(peel, 0.00005))
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(bump_h, bump.inputs['Height'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    cbump = N.new('ShaderNodeBump')
    cbump.inputs['Distance'].default_value = 1.0
    N.put(coat_h, cbump.inputs['Height'])
    N.put(cbump.outputs['Normal'], bsdf.inputs['Coat Normal'])

    mm = lambda v: N.math('MULTIPLY_ADD', v, 1000.0, 1.0)      # noqa: E731  (m -> mm + 1, za EXR half)
    maps = {'albedo': albedo,
            'rough': N.rgb(rough, coat_rough, mask),
            'height': N.rgb(mm(bump_h), mm(coat_h), mm(height))}
    return m, maps


def mat_stoneware_baked(imgs):
    """Isti materijal iz ispečenih mapa (load_maps): par tekstura umesto stotina čvorova po tački."""
    m, nt, bsdf, N = C.new_material('StonewareBaked')
    m.displacement_method = 'DISPLACEMENT'
    out = nt.nodes['Material Output']
    alb, _ = N.image(imgs['albedo'])
    rough, coat_rough, mask = N.split(N.image(imgs['rough'])[0])
    bump_h, coat_h, disp_h = N.split(N.image(imgs['height'])[0])
    N.put(alb, bsdf.inputs['Base Color'])
    N.put(rough, bsdf.inputs['Roughness'])
    N.put(coat_rough, bsdf.inputs['Coat Roughness'])
    N.put(N.mixf(mask, 0.30, 0.5), bsdf.inputs['Specular IOR Level'])
    N.put(N.mixf(mask, 0.10, 0.25), bsdf.inputs['Coat Weight'])
    for h, sock in ((bump_h, 'Normal'), (coat_h, 'Coat Normal')):
        b = N.new('ShaderNodeBump')
        b.inputs['Distance'].default_value = 0.001              # mape su u mm
        N.put(h, b.inputs['Height'])
        N.put(b.outputs['Normal'], bsdf.inputs[sock])
    disp = N.new('ShaderNodeDisplacement', space='OBJECT')
    disp.inputs['Midlevel'].default_value = 1.0
    disp.inputs['Scale'].default_value = 0.001
    N.put(disp_h, disp.inputs['Height'])
    N.put(disp.outputs['Displacement'], out.inputs['Displacement'])
    return m


def stoneware(body, bake=True, rebake=False, samples=4):
    """Materijal šolje: proceduralni (bake=False) ili iz keša ispečenih mapa (ispeče ih ako ih nema)."""
    src, maps = mat_stoneware(body)
    C.assign(body, src)
    if not bake:
        return src
    _, _, height = mug_atlas()
    key = C.source_key(mat_stoneware, mug_profile_parts, mug_atlas, handle_mesh, build_mug, LOOK,
                       (TEX_W, height, TEX_DENSITY, HIDDEN_DENSITY, HANDLE_ROWS, samples))
    paths = {k: CACHE / f'stoneware_{key}_{k}.exr' for k in maps}
    if rebake or not all(p.exists() for p in paths.values()):
        for old in CACHE.glob('stoneware_*.exr'):       # stari otisci se brišu
            if key not in old.name:
                old.unlink()
        t0 = time.time()
        C.bake_maps(body, src, maps, paths, TEX_W, height, samples=samples)
        print(f'SIP bake: {TEX_W}x{height}, {len(maps)} mape, {time.time() - t0:.0f} s -> {CACHE}')
    m = mat_stoneware_baked(C.load_maps(paths))
    C.assign(body, m)
    return m


def mat_coffee(coffee):
    """Crna kafa sa ogledalskom površinom; krema: tanka svetlosmeđa pena uz zid, ostrvca i mehurići."""
    m, nt, bsdf, N = C.new_material('CoffeeSip')
    tc = N.new('ShaderNodeTexCoord', object=coffee)
    P = tc.outputs['Object']
    x, y, _ = N.sep(P)
    rr = N.vmath('LENGTH', N.xyz(x, y, 0.0))
    swirl = N.noise(P, 110.0, detail=4, distortion=1.4)
    patch = N.noise(P, 38.0, detail=3, distortion=0.8)
    crema = N.add(N.mul(N.ramp(rr, 0.0396, 0.0422), N.ramp(swirl, 0.38, 0.58, 0.35, 1.0)),
                  N.mul(N.ramp(patch, 0.72, 0.78), N.ramp(swirl, 0.45, 0.62, 0.0, 0.5)))
    crema = N.math('MINIMUM', crema, 1.0)
    bub, _ = N.voronoi(P, 1500.0)
    big, _ = N.voronoi(P, 420.0, randomness=0.8)
    big_m = N.mul(N.ramp(big, 0.22, 0.12), N.ramp(rr, 0.036, 0.041))           # krupniji mehurići uz zid
    foam = N.mix(N.ramp(swirl, 0.3, 0.7), (0.11, 0.050, 0.022), (0.24, 0.125, 0.058))
    foam = N.mix(N.mul(N.ramp(bub, 0.30, 0.05), 0.35), foam, (0.32, 0.19, 0.095))
    col = N.mix(crema, (0.0045, 0.0020, 0.0009), foam)
    N.put(col, bsdf.inputs['Base Color'])
    N.put(N.mixf(crema, 0.03, 0.32), bsdf.inputs['Roughness'])
    bsdf.inputs['IOR'].default_value = 1.34
    N.put(N.mixf(crema, 0.5, 0.25), bsdf.inputs['Specular IOR Level'])
    ripple = N.noise(P, 18.0, detail=1)
    hgt = N.add(N.mul(N.mul(N.sub(0.35, bub), crema), 0.00006), N.mul(N.sub(0.22, big), N.mul(big_m, 0.0004)))
    hgt = N.add(hgt, N.mul(ripple, 0.00003))
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(hgt, bump.inputs['Height'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_steam(steam, glow=0.6):
    """Tanki pramenovi pare: listovi šuma koji se dižu i šire, gusti samo iznad sredine šolje."""
    m = bpy.data.materials.new('Steam')
    if m.node_tree is None:
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial':
            nt.nodes.remove(n)
    out = nt.nodes['Material Output']
    N = C.Nodes(nt)
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

    # jeftin trik bez šuma: para samo upija (daje alfa) i svetli belo srazmerno gustini
    vol = N.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1)
    vol.inputs['Absorption Color'].default_value = (0.0, 0.0, 0.0, 1)
    vol.inputs['Emission Color'].default_value = (1.0, 0.97, 0.94, 1)
    N.put(dens, vol.inputs['Density'])
    N.put(N.mul(dens, glow), vol.inputs['Emission Strength'])
    nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m, clock, amount


# ---------------------------------------------------------------- kompozitor
def compositor(scene, grain=0.05, vignette=0.0, dispersion=0.0):
    """Zrno filma (sitno, srazmerno svetlini), po želji vinjeta i blaga hromatska aberacija."""
    ng = bpy.data.node_groups.new('Foto', 'CompositorNodeTree')
    scene.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N = C.Nodes(ng)
    rl = N.new('CompositorNodeRLayers')
    rl.scene = scene
    img, alpha = rl.outputs['Image'], rl.outputs['Alpha']
    if dispersion > 0:
        ld = N.new('CompositorNodeLensdist')
        N.put(img, ld.inputs['Image'])
        if 'Dispersion' in ld.inputs:
            ld.inputs['Dispersion'].default_value = dispersion
        img = ld.outputs['Image']
    coords = N.new('CompositorNodeImageCoordinates')
    N.put(img, coords.inputs['Image'])
    pix = coords.outputs['Pixel']
    wn = N.new('ShaderNodeTexWhiteNoise', noise_dimensions='3D')
    N.put(pix, wn.inputs['Vector'])
    clump = N.noise(pix, 0.6, detail=0.0)                       # zrnca ~1,5 px, ne samo šum po pikselu
    g = N.math('MULTIPLY_ADD', N.sub(clump, 0.5), 2.2, N.sub(wn.outputs['Value'], 0.5))
    fac = N.math('MULTIPLY_ADD', g, grain, 1.0)
    if vignette > 0:
        info = N.new('CompositorNodeImageInfo')
        N.put(img, info.inputs['Image'])
        res = info.outputs['Resolution']
        half = N.vmath('SCALE', res, scale=0.5)
        q = N.vmath('DIVIDE', N.vmath('SUBTRACT', pix, half), half)
        dist = N.vmath('LENGTH', q)
        fac = N.mul(fac, N.ramp(dist, 0.55, 1.45, 1.0, 1.0 - vignette))
    cc = N.new('CompositorNodeCombineColor')
    for i in range(3):
        N.put(fac, cc.inputs[i])
    cc.inputs[3].default_value = 1.0
    mx = N.new('ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY', clamp_factor=True)
    mx.inputs[0].default_value = 1.0
    N.put(img, mx.inputs[6])
    N.put(cc.outputs[0], mx.inputs[7])
    sa = N.new('CompositorNodeSetAlpha')
    N.put(mx.outputs[2], sa.inputs['Image'])
    N.put(alpha, sa.inputs['Alpha'])
    if 'Type' in sa.inputs:
        sa.inputs['Type'].default_value = 'Replace Alpha'
    elif hasattr(sa, 'mode'):
        sa.mode = 'REPLACE_ALPHA'
    go = N.new('NodeGroupOutput')
    N.put(sa.outputs['Image'], go.inputs[0])
    scene.render.use_compositing = True
    return ng


# ---------------------------------------------------------------- scena
def build(args):
    scene = C.reset()
    transparent = not args.backdrop
    C.photo_render_settings(scene, width=args.res, height=args.res, samples=args.samples, transparent=transparent,
                            adaptive=args.adaptive, exposure=args.exposure)
    scene.cycles.volume_step_rate = 2.0
    scene.frame_start, scene.frame_end = 1, args.end

    C.world_hdri(scene, args.hdri_strength, args.hdri_rot)
    floor, wall = build_set(args.backdrop)

    rig = bpy.data.objects.new('MugRig', None)
    scene.collection.objects.link(rig)
    body = build_mug(rig)
    coffee = build_coffee(rig)
    stoneware(body, bake=not args.no_bake, rebake=args.rebake)
    C.assign(coffee, mat_coffee(coffee))
    C.photo_studio_lights((0.0, 0.0, 0.055), [body, coffee], wall, key=args.key, strip=args.strip, sun=args.sun,
                          bg=args.bg, reflector=args.reflector, flags=not args.no_flags,
                          sun_spot=tuple(float(v) for v in args.sun_spot.split(',')))

    clock = amount = None
    if args.steam:
        steam = build_steam(rig)
        sm, clock, amount = mat_steam(steam, glow=0.6 * 2 ** -args.exposure)
        C.assign(steam, sm)
        steam.visible_shadow = False

    # kamera: spreda, nisko (14°: na boku se vidi odsjaj blende), lens 85; fokus malo ispred ose šolje,
    # f/8 (cela šolja oštra, zid mekan)
    elev, dist = math.radians(args.elev), args.dist
    target = (0.010, 0.0, args.frame_z)
    cam = C.camera((target[0], -dist * math.cos(elev), target[2] + dist * math.sin(elev)), target, lens=85)
    focus = bpy.data.objects.new('Focus', None)
    scene.collection.objects.link(focus)
    focus.parent = rig
    focus.location = (0.0, -0.020, 0.060)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = focus
    cam.data.dof.aperture_fstop = args.fstop
    cam.data.dof.aperture_blades = 7
    cam.data.dof.aperture_rotation = math.radians(12)

    if args.grain > 0 or args.vignette > 0:     # samo za probu: na sajtu zrno i vinjeta idu preko CSS-a
        compositor(scene, grain=args.grain, vignette=args.vignette)
    else:
        scene.render.use_compositing = False

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


def parse_args(argv):
    ap = argparse.ArgumentParser(prog='sip.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='', help='npr. 1,32,64; prazno = svi kadrovi')
    ap.add_argument('--end', type=int, default=64, help='broj kadrova (storyboard: 64 desktop, telefon = neparni)')
    ap.add_argument('--res', type=int, default=1200)
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--adaptive', type=float, default=0.02, help='adaptive sampling threshold')
    ap.add_argument('--spin', type=float, default=28.0)
    ap.add_argument('--drop', type=float, default=0.045)
    ap.add_argument('--exposure', type=float, default=0.0)
    ap.add_argument('--backdrop', action='store_true', help='sto i zid umesto providne pozadine')
    ap.add_argument('--fstop', type=float, default=8.0)
    ap.add_argument('--elev', type=float, default=14.0, help='ugao kamere odozgo (°)')
    ap.add_argument('--dist', type=float, default=0.60)
    ap.add_argument('--frame-z', dest='frame_z', type=float, default=0.050)
    ap.add_argument('--key', type=float, default=70.0, help='key prozor (area 0,6x0,9 m), W')
    ap.add_argument('--strip', type=float, default=10.0, help='svaka od dve trake pozadi, W (svetle samo šolju)')
    ap.add_argument('--reflector', type=float, default=0.9,
                    help='niska blenda levo-napred, W (samo odsjaj na šolji; 0 = bez)')
    ap.add_argument('--sun', type=float, default=5.0, help='sunce na zidu (gobo), W/m²')
    ap.add_argument('--sun-spot', dest='sun_spot', default='{},{}'.format(*C.STUDIO['sun_spot']),
                    help='x,z tačke na zidu kroz koju sunce gađa sredinu prozora (pomera šaru okvira)')
    ap.add_argument('--bg', type=float, default=6.0, help='meko svetlo zida sleva, W')
    ap.add_argument('--no-flags', dest='no_flags', action='store_true')
    ap.add_argument('--hdri-strength', dest='hdri_strength', type=float, default=0.15)
    ap.add_argument('--hdri-rot', dest='hdri_rot', type=float,
                    default=C.HDRI_LEBOMBO_WINDOW_AZ - C.STUDIO['key_az'])
    ap.add_argument('--grain', type=float, default=0.0, help='samo za probu; na sajtu ide CSS')
    ap.add_argument('--vignette', type=float, default=0.0, help='samo za probu')
    ap.add_argument('--poster', action='store_true')
    ap.add_argument('--steam', action='store_true', help='para (volumen); podrazumevano isključena')
    ap.add_argument('--no-bake', dest='no_bake', action='store_true',
                    help='proceduralni materijal bez pečenja (sporije; za razvoj izgleda)')
    ap.add_argument('--rebake', action='store_true', help='ponovo ispeci mape šolje i ako postoje u kešu')
    return ap.parse_args(argv)


def main():
    args = parse_args(C.args())
    t0 = time.time()
    scene = build(args)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    frames = [int(f) for f in args.frames.split(',') if f.strip()] or list(range(1, args.end + 1))
    print(f'SIP scena: {time.time() - t0:.0f} s')
    for f in frames:
        t1 = time.time()
        C.render_frames(scene, str(out), [f])
        print(f'SIP kadar {f}: {time.time() - t1:.1f} s')
    if args.poster:
        scene.frame_set(args.end)
        scene.render.filepath = str(out / 'poster.png')
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
