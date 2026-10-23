"""SIP: keramička šolja (stoneware sa curećom glazurom), kafa sa kremom, po želji tanka para.

Fotorealistična verzija (dokaz koncepta 23.10.2026, uz dijagnozu recenzenta). Šolja ulazi odozgo,
okreće se ~28° i smiruje se; poslednjih ~12 kadrova miruje (kraj skrola). Metri, pod z=0, centar (0,0),
kamera spreda 24° odozgo, lens 85, f/8, kvadrat.

Svetlo „foto-studio" (photo_studio_lights, predlog za common.py): tamna okolina (HDRI 0,1), jedan key
prozor 0,6x0,9 m na 1,3 m levo-gore-napred iza prozorskog okvira (krst se ogleda u glazuri), dve uske
trake 0,12x1,0 m pozadi za ivice, crna zastava desno; toplo popodnevno sunce kroz isti okvir pada
SAMO na zid (light linking) i crta kosu senku okvira kao u videu. Ekspozicija 0, AgX Medium High Contrast.

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
      -P scripts/blender/kafa/sip.py -- --out <folder> [--frames 1,45,90] [--end 90] [--res 1200] \
      [--samples 160] [--backdrop] [--fstop 8] [--exposure 0] [--poster] [--steam] [--grain 0]

--backdrop: sto i zid boje SIP sekcije (RGB, za probu i poređenje); bez njega providna pozadina sa
senkom na shadow catcher-u (RGBA za sajt). Zrno filma se ne peče u render (ide preko CSS-a);
--grain/--vignette postoje samo za probu. Bez --frames renderuje sve kadrove 1..end.
--poster dodaje poster.png (smiren poslednji kadar).
"""
import argparse
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ASSETS = pathlib.Path(__file__).resolve().parents[1] / 'assets'
HDRI = ASSETS / 'lebombo_2k.exr'

# ---------------------------------------------------------------- mere šolje (m)
RIM_Z = 0.0980          # vrh oboda
GLAZE_Z = 0.0560        # srednja linija do koje glazura pokriva telo
COFFEE_Z = 0.0895       # nivo kafe (8,5 mm ispod oboda)
HANDLE_ANGLE = 12.0     # krajnji ugao drške (° oko Z; 0 = drška desno, + = ka nazad)
WALL_Y = 0.34           # zid iza šolje (samo uz --backdrop)

# boje SIP sekcije iz studio/kafa-skrol/dizajn/tokens.css
SIP_BG = '#6E3A27'      # --pp-espresso, pozadina (zid)
SIP_FLOOR = '#7C4532'   # --color-floor, sto ispod šolje

# svetlo (azimut od +X, -90 = ka kameri, + = ka nazad; visina iznad horizonta, u stepenima)
KEY_AZ, KEY_EL, KEY_DIST = -140.0, 35.0, 1.30     # key prozor levo-gore-napred
KEY_SIZE = (0.60, 0.90)
STRIP_AZ, STRIP_DIST = (146.0, 34.0), 0.45         # uske trake pozadi levo i pozadi desno
FLAG_AZ, FLAG_DIST = -30.0, 0.42                   # crna zastava desno napred
SUN_SPOT = (-0.16, WALL_Y, 0.20)                   # tačka na zidu kroz koju sunce gađa sredinu prozora
HDRI_WINDOW_AZ = -42.0  # azimut prozora u neokrenutom HDRI-ju (izmereno iz EXR-a)


def srgb(hex_color):
    """'#RRGGBB' -> linearni RGB (Blender radi u linearnom prostoru)."""
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


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

    def mixv(self, fac, a, b):
        n = self.new('ShaderNodeMix', data_type='VECTOR', clamp_factor=True)
        self.put(fac, n.inputs[0])
        self.put(a, n.inputs[4])
        self.put(b, n.inputs[5])
        return n.outputs[1]

    def noise(self, vec, scale, detail=2.0, rough=0.5, distortion=0.0, w=None, kind='FBM'):
        n = self.new('ShaderNodeTexNoise', noise_dimensions='4D' if w is not None else '3D', noise_type=kind)
        self.put(vec, n.inputs['Vector'])
        if w is not None:
            self.put(w, n.inputs['W'])
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        n.inputs['Roughness'].default_value = rough
        n.inputs['Distortion'].default_value = distortion
        return n.outputs[0]

    def voronoi(self, vec, scale, feature='F1', randomness=1.0):
        n = self.new('ShaderNodeTexVoronoi', feature=feature)
        self.put(vec, n.inputs['Vector'])
        n.inputs['Scale'].default_value = scale
        n.inputs['Randomness'].default_value = randomness
        return n.outputs['Distance'], n.outputs.get('Color')   # DISTANCE_TO_EDGE nema Color


def new_material(name):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:  # u 5.x materijal uvek ima čvorove (use_nodes je zastareo)
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


def direction(az_deg, el_deg):
    a, e = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def ray_visibility(ob, camera=True, diffuse=True, glossy=True, transmission=True, scatter=True, shadow=True):
    ob.visible_camera, ob.visible_diffuse, ob.visible_glossy = camera, diffuse, glossy
    ob.visible_transmission, ob.visible_volume_scatter, ob.visible_shadow = transmission, scatter, shadow


# ---------------------------------------------------------------- modeli
def mug_profile():
    """Profil šolje (r, z): donja strana -> stopa -> spoljni zid -> obod -> unutrašnji zid -> dno.

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
    return under + outer + rim + inner


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
    ob = link(bpy.data.objects.new('HandleCurve', cu))
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    me.transform(Matrix.Diagonal((1.0, 1.6, 1.0, 1.0)))    # 8,6 mm u ravni drške, 13,8 mm poprečno
    return me


def build_mug(rig):
    """Telo i drška u jednom mesh-u (da Bevel shader zaobli spoj), pa wobble i subdivision za displacement."""
    body = C.lathe('Mug', mug_profile(), segments=160)
    body.parent = rig
    n_body = len(body.data.polygons)
    hme = handle_mesh()
    bm = bmesh.new()
    bm.from_mesh(body.data)
    vs = [bm.verts.new(v.co) for v in hme.vertices]
    for p in hme.polygons:
        try:
            bm.faces.new([vs[i] for i in p.vertices])
        except ValueError:
            pass
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
    s.levels, s.render_levels = 1, 2
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
    C.assign(floor, mat_surface('Floor', SIP_FLOOR, rough=(0.42, 0.62), spec=0.45, bump=0.000035))
    if not backdrop:
        floor.is_shadow_catcher = True
        return floor, None
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, WALL_Y, 0.75))
    wall = bpy.context.active_object
    wall.name = 'Wall'
    wall.scale = (3.0, 1.5, 1.0)
    wall.rotation_euler = (math.radians(90), 0, 0)      # normala ka kameri (-Y)
    C.assign(wall, mat_surface('Wall', SIP_BG, rough=(0.80, 0.92), spec=0.3, bump=0.00006, scale=1.0))
    return floor, wall


def area_light(name, loc, aim, size, power, kelvin, shape='RECTANGLE'):
    d = bpy.data.lights.new(name, 'AREA')
    d.shape, d.size, d.size_y = shape, size[0], size[1]
    d.energy = power
    d.use_temperature, d.temperature = True, kelvin
    ob = link(bpy.data.objects.new(name, d))
    ob.location = loc
    ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    ob.visible_camera = False
    return ob


def flag(name, loc, aim, size):
    """Crna zastava (molton): upija svetlo, u glazuri daje tamnu površinu = kontrast odsjaja."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1.0)
    ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    ray_visibility(ob, camera=False)
    m, _, b, _ = new_material(name)
    b.inputs['Base Color'].default_value = (0.004, 0.004, 0.004, 1)
    b.inputs['Roughness'].default_value = 1.0
    b.inputs['Specular IOR Level'].default_value = 0.0
    C.assign(ob, m)
    return ob


def photo_studio_lights(target, wall=None, key=110.0, strip=28.0, sun=2.2, flags=True):
    """Foto-studio (predlog za common.py): jedan key prozor levo-gore-napred iza prozorskog okvira,
    dve uske trake pozadi, crna zastava desno; uz zid i toplo sunce kroz isti okvir koje pada samo na zid.

    Fill skoro ne postoji (samo tamni HDRI), pa je odnos key:fill oko 5-8:1 i svetlo pada sleva udesno."""
    tgt = Vector(target)
    kdir = direction(KEY_AZ, KEY_EL)
    key_pos = tgt + KEY_DIST * kdir
    a = Vector((kdir.x, kdir.y, 0.0)).normalized()    # horizontalno, od šolje ka prozoru
    t = Vector((a.y, -a.x, 0.0))                      # horizontala u ravni prozora (t x a = +Z)
    win = key_pos - 0.06 * a                          # ravan okvira 6 cm ispred key svetla

    # okvir: zid oko otvora + 2x3 okna sa prečkama 3,5 cm; baca senku i vidi se u odsjaju, kameri nevidljiv
    W, H, bar, margin = KEY_SIZE[0] + 0.04, KEY_SIZE[1] + 0.04, 0.035, 0.55
    cols, rows = 2, 3
    rects = [(-W / 2 - margin, -H / 2 - margin, -W / 2, H / 2 + margin),       # levo
             (W / 2, -H / 2 - margin, W / 2 + margin, H / 2 + margin),         # desno
             (-W / 2, H / 2, W / 2, H / 2 + margin),                           # gore
             (-W / 2, -H / 2 - margin, W / 2, -H / 2)]                         # dole
    for i in range(1, cols):
        u = -W / 2 + W * i / cols
        rects.append((u - bar / 2, -H / 2, u + bar / 2, H / 2))
    for j in range(1, rows):
        v = -H / 2 + H * j / rows
        rects.append((-W / 2, v - bar / 2, W / 2, v + bar / 2))
    bm = bmesh.new()
    for u0, v0, u1, v1 in rects:
        bm.faces.new([bm.verts.new((u, 0.0, v)) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))])
    me = bpy.data.meshes.new('WindowFrame')
    bm.to_mesh(me)
    bm.free()
    frame = link(bpy.data.objects.new('WindowFrame', me))
    frame.matrix_world = Matrix(((t.x, a.x, 0.0, win.x), (t.y, a.y, 0.0, win.y),
                                 (0.0, 0.0, 1.0, win.z), (0.0, 0.0, 0.0, 1.0)))
    ray_visibility(frame, camera=False, diffuse=False, transmission=False, scatter=False)
    fm, _, fb, _ = new_material('WindowFrame')
    fb.inputs['Base Color'].default_value = (0.02, 0.018, 0.016, 1)
    fb.inputs['Roughness'].default_value = 0.9
    C.assign(frame, fm)

    # key: vertikalan prozor (kao pravi), 4300 K toplo popodne
    kd = bpy.data.lights.new('Key', 'AREA')
    kd.shape, kd.size, kd.size_y = 'RECTANGLE', KEY_SIZE[0], KEY_SIZE[1]
    kd.energy = key
    kd.use_temperature, kd.temperature = True, 4300
    ko = link(bpy.data.objects.new('Key', kd))
    ko.location = key_pos
    ko.rotation_euler = (-a).to_track_quat('-Z', 'Z').to_euler()
    ko.visible_camera = False
    lights = [ko]

    # trake pozadi: tanke svetle linije duž leve i desne ivice šolje
    for i, az in enumerate(STRIP_AZ):
        pos = tgt + STRIP_DIST * direction(az, 18.0) + Vector((0.0, 0.0, 0.10))
        lights.append(area_light(f'Strip{i}', pos, tgt + Vector((0.0, 0.0, 0.01)), (0.12, 1.0), strip, 5200))
    if flags:
        fpos = tgt + FLAG_DIST * direction(FLAG_AZ, 12.0)
        flag('FlagRight', fpos, tgt, (0.45, 0.70))

    if wall is not None:
        # sunce kroz isti okvir, samo na zid (light linking): kosa senka okvira kao u videu
        s = (win - Vector(SUN_SPOT)).normalized()
        sd = bpy.data.lights.new('Sun', 'SUN')
        sd.energy = sun
        sd.angle = math.radians(2.5)                  # mekša ivica senke nego pravo sunce (izmaglica)
        sd.use_temperature, sd.temperature = True, 3500
        so = link(bpy.data.objects.new('Sun', sd))
        so.rotation_euler = (-s).to_track_quat('-Z', 'Y').to_euler()
        rc = bpy.data.collections.new('SunReceivers')
        rc.objects.link(wall)
        so.light_linking.receiver_collection = rc
        lights.append(so)
    return lights


def world_hdri(scene, strength, rot_deg):
    w = bpy.data.worlds.new('World')
    scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    N = Nodes(nt)
    env = N.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(str(HDRI), check_existing=True)
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(rot_deg))
    N.put(tc.outputs['Generated'], mp.inputs['Vector'])
    N.put(mp.outputs['Vector'], env.inputs['Vector'])
    bg = nt.nodes['Background']
    N.put(env.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    return w


# ---------------------------------------------------------------- materijali
def mat_stoneware(body, seed=7):
    """Tamnobraon zrnasta glina (mat) + ovsena krem-siva glazura koja curi u kapima.

    Displacement (pravo pomeranje temena): tragovi kola u spirali, debljina glazure sa zadebljanom
    ivicom i kapljicama na kraju kapi. Bump: zrnca gline (i kroz glazuru), rupice, krakelir, ogrebotine."""
    m, nt, bsdf, N = new_material('Stoneware')
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
    w1 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=1.3), (3.1, 7.7, 1.9)), 1.0, detail=3, rough=0.55)
    w2 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=4.0), (8.2, 1.3, 4.4)), 1.0, detail=1)
    w3 = N.noise(N.vmath('ADD', N.vmath('SCALE', u, scale=8.0), (2.4, 5.1, 9.3)), 1.0, detail=2)   # 4-8 mm
    z0 = N.add(N.math('MULTIPLY_ADD', N.sub(w1, 0.5), 0.0260, GLAZE_Z), N.mul(N.sub(w2, 0.5), 0.0080))
    z0 = N.math('MULTIPLY_ADD', N.sub(w3, 0.5), 0.0050, z0)
    d = N.sub(z0, z)

    # kapi: široki jezici (glazura se slegla) i uže kapi sa zadebljanim vrhom, nejednaki razmaci;
    # neke stoje u paru (0,06-0,12 rad), pa se preko smooth-min spajaju u jednu široku kap
    drips, angles = [], []
    while len(drips) < 12:
        if angles and rnd.random() < 0.3:
            a = angles[-1] + rnd.choice((-1, 1)) * rnd.uniform(0.06, 0.12)
        else:
            a = rnd.uniform(0, 2 * math.pi)
            if any(abs(math.atan2(math.sin(a - b), math.cos(a - b))) < 0.22 for b in angles):
                continue
        angles.append(a)
        if len(drips) < 3:
            drips.append((a, rnd.uniform(0.0025, 0.0075), rnd.uniform(0.0060, 0.0130), 1.0))
        else:
            drips.append((a, rnd.uniform(0.0030, 0.0185), rnd.uniform(0.0026, 0.0058), rnd.uniform(1.0, 1.28)))
    beads = None
    for a, length, wid, bead_k in drips:
        top = GLAZE_Z + 0.004
        bot = GLAZE_Z - length
        h = N.mul(r, N.vmath('LENGTH', N.vmath('SUBTRACT', u, (math.cos(a), math.sin(a), 0.0))))
        zc = N.math('MAXIMUM', N.math('MINIMUM', z, top), bot)
        # kap se sužava naniže (vrat), a na kraju se skuplja u kapljicu
        taper = N.math('MULTIPLY_ADD', N.sub(zc, bot), 0.55 * wid / (top - bot), 0.72 * wid)
        neck = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(z, zc), 0.0)), taper)
        bead = N.sub(N.vmath('LENGTH', N.xyz(h, N.sub(z, bot + wid * 0.30), 0.0)), wid * bead_k * 0.9)
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
    phase = N.add(N.math('MULTIPLY_ADD', z, 2 * math.pi / 0.0074, theta), N.mul(N.noise(P, 22.0, detail=2), 3.2))
    ring = N.math('POWER', N.math('MULTIPLY_ADD', N.math('SINE', phase), 0.5, 0.5), 1.6)   # 0..1, oštriji grebeni
    ring_env = N.mul(N.ramp(z, 0.009, 0.017), N.mixf(N.ramp(z, 0.050, 0.064), 1.0, 0.35))
    ring_env = N.mul(N.mul(ring_env, N.sub(1.0, hnd)), N.mixf(inner, 1.0, 0.45))
    ring_h = N.mul(N.mul(ring, ring_env), 0.00034)

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
    clay = N.mix(clay_var, (0.021, 0.0135, 0.0100), (0.040, 0.027, 0.020))
    clay = N.mix(N.mul(peb_top, 0.55), clay, (0.072, 0.052, 0.040))
    grog_d, _ = N.voronoi(P, 520.0)
    clay = N.mix(N.mul(N.ramp(grog_d, 0.10, 0.04), 0.8), clay, (0.13, 0.095, 0.070))
    clay = N.mix(N.mul(ring, N.mul(ring_env, 0.35)), clay, (0.055, 0.038, 0.028))   # grebeni malo svetliji
    clay = N.mix(N.mul(halo, 0.6), clay, (0.085, 0.036, 0.016))             # rđasti oreol oko glazure

    # --- glazura: ovsena krem-siva sa zelenkastim tonom; oblaci, gvožđe, reljef gline kroz tanku glazuru
    gv = N.noise(P, 55.0, detail=5, rough=0.62)
    glaze = N.mix(N.ramp(gv, 0.30, 0.72), (0.175, 0.150, 0.108), (0.400, 0.365, 0.285))
    cloud = N.ramp(N.noise(P, 30.0, detail=4, distortion=0.5), 0.48, 0.72)
    glaze = N.mix(N.mul(cloud, 0.60), glaze, (0.20, 0.125, 0.075))              # smeđi oblaci
    top_tone = N.ramp(z, GLAZE_Z + 0.010, RIM_Z - 0.002)                      # ka obodu glazura je tanja
    glaze = N.mix(N.mul(top_tone, 0.45), glaze, (0.21, 0.140, 0.085))
    glaze = N.mix(N.mul(ring, N.mul(ring_env, 0.55)), glaze, (0.17, 0.105, 0.060))   # glazura puca na grebenima
    glaze = N.mix(N.mul(peb_top, 0.55), glaze, (0.15, 0.098, 0.060))          # zrnca gline probijaju
    glaze = N.mix(N.mul(N.sub(1.0, pool), 0.25), glaze, (0.24, 0.17, 0.11))    # tanje = toplije
    spot_d, _ = N.voronoi(P, 210.0)
    spots = N.mul(N.ramp(spot_d, 0.26, 0.10), N.ramp(N.noise(P, 45.0, detail=2), 0.40, 0.58))
    glaze = N.mix(N.mul(spots, 0.9), glaze, (0.085, 0.040, 0.020))            # tačke gvožđa
    fleck_d, _ = N.voronoi(P, 900.0)
    glaze = N.mix(N.mul(N.ramp(fleck_d, 0.18, 0.05), 0.8), glaze, (0.12, 0.065, 0.034))
    glaze = N.mix(N.mul(edge_in, 0.55), glaze, (0.21, 0.115, 0.060))          # tanka ivica -> karamel
    glaze = N.mix(N.mul(dome, 0.35), glaze, (0.46, 0.43, 0.35))               # debela kapljica -> svetlija
    rim_brk = N.mul(N.ramp(z, RIM_Z - 0.0060, RIM_Z - 0.0010), N.ramp(N.noise(P, 300.0), 0.3, 0.6, 0.55, 1.0))
    glaze = N.mix(rim_brk, glaze, (0.15, 0.072, 0.034))                       # obod: glazura puca u smeđe
    craze_d, _ = N.voronoi(N.vmath('MULTIPLY', P, (1.0, 1.0, 0.7)), 140.0, feature='DISTANCE_TO_EDGE')
    craze = N.mul(N.ramp(craze_d, 0.0, 0.03, 1.0, 0.0), N.ramp(N.noise(P, 20.0), 0.45, 0.6))
    glaze = N.mix(N.mul(craze, 0.30), glaze, (0.12, 0.075, 0.045))            # krakelir (fine pukotine)
    # mokar trag kafe iznad nivoa, unutra
    wet = N.mul(inner, N.ramp(z, COFFEE_Z + 0.0004, COFFEE_Z + 0.0022, 1.0, 0.0))
    glaze = N.mix(N.mul(wet, 0.6), glaze, (0.05, 0.025, 0.012))

    N.put(N.mix(mask, clay, glaze), bsdf.inputs['Base Color'])

    # --- hrapavost: glina mat sa zrncima koja se sjaje; glazura satenska + mrlje od prstiju i ogrebotine
    smudge = N.ramp(N.noise(P, 9.0, detail=3), 0.48, 0.70)
    scratch_d, _ = N.voronoi(N.vmath('MULTIPLY', P, (30.0, 30.0, 420.0)), 1.0, feature='DISTANCE_TO_EDGE')
    scratch = N.mul(N.ramp(scratch_d, 0.0, 0.02, 1.0, 0.0), N.ramp(N.noise(P, 14.0), 0.52, 0.62))
    g_rough = N.add(N.math('MULTIPLY_ADD', gv, 0.05, 0.08), N.add(N.mul(smudge, 0.05), N.mul(craze, 0.04)))
    c_rough = N.add(N.math('MULTIPLY_ADD', smudge, 0.03, 0.05), N.mul(scratch, 0.12))
    k_rough = N.math('MULTIPLY_ADD', N.sub(1.0, peb_top), 0.12, 0.70)
    N.put(N.mixf(mask, k_rough, N.mixf(wet, g_rough, 0.08)), bsdf.inputs['Roughness'])
    N.put(N.mixf(mask, 0.30, 0.5), bsdf.inputs['Specular IOR Level'])
    N.put(N.mixf(mask, 0.10, 0.40), bsdf.inputs['Coat Weight'])
    N.put(N.mixf(mask, 0.40, c_rough), bsdf.inputs['Coat Roughness'])
    # glazura je staklasta: malo svetla uđe i rasprši se (mekši prelaz senke na glazuri)
    N.put(N.mul(mask, 0.22), bsdf.inputs['Subsurface Weight'])
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.62, 0.38)
    bsdf.inputs['Subsurface Scale'].default_value = 0.0012

    # --- normala: Bevel zaobli spoj drške i ivice stope (bez oboda, tanak je), pa sitni reljef preko
    geo = N.new('ShaderNodeNewGeometry')
    bev = N.new('ShaderNodeBevel', samples=6)
    near_handle = N.math('MAXIMUM', hnd, N.mul(N.ramp(N.math('COSINE', theta), 0.90, 0.985), N.ramp(r, 0.040, 0.046)))
    N.put(N.math('MULTIPLY_ADD', near_handle, 0.0016, 0.0012), bev.inputs['Radius'])
    base_n = N.mixv(N.ramp(z, RIM_Z - 0.006, RIM_Z - 0.003), bev.outputs['Normal'], geo.outputs['Normal'])
    pin, _ = N.voronoi(P, 600.0)                                  # rupice ~0,4 mm (2 px na 1200 px)
    pinholes = N.mul(N.ramp(pin, 0.15, 0.05), N.ramp(N.noise(P, 60.0), 0.52, 0.66))
    peel = N.sub(N.noise(P, 420.0, detail=2), 0.5)                # „pomorandžina kora" glazure, ~2 mm
    peb_h = N.mul(N.sub(1.0, pebble), 0.00016)
    clay_h = N.add(peb_h, N.mul(N.sub(grain, 0.5), 0.00003))
    glaze_h = N.add(N.add(N.mul(peb_h, 0.55), N.mul(pinholes, -0.00010)), N.mul(craze, -0.000006))
    glaze_h = N.add(glaze_h, N.mul(peel, 0.00005))
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mixf(mask, clay_h, glaze_h), bump.inputs['Height'])
    N.put(base_n, bump.inputs['Normal'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    cbump = N.new('ShaderNodeBump')
    cbump.inputs['Distance'].default_value = 1.0
    N.put(N.add(N.add(N.mul(pinholes, -0.00010), N.mul(N.mul(scratch, mask), -0.000003)), N.mul(peel, 0.00005)),
          cbump.inputs['Height'])
    N.put(base_n, cbump.inputs['Normal'])
    N.put(cbump.outputs['Normal'], bsdf.inputs['Coat Normal'])
    return m


def mat_coffee(coffee):
    """Crna kafa sa ogledalskom površinom; krema: tanka svetlosmeđa pena uz zid, ostrvca i mehurići."""
    m, nt, bsdf, N = new_material('CoffeeSip')
    tc = N.new('ShaderNodeTexCoord', object=coffee)
    P = tc.outputs['Object']
    x, y, _ = N.sep(P)
    rr = N.vmath('LENGTH', N.xyz(x, y, 0.0))
    swirl = N.noise(P, 110.0, detail=4, distortion=1.4)
    patch = N.noise(P, 38.0, detail=3, distortion=0.8)
    crema = N.add(N.mul(N.ramp(rr, 0.0300, 0.0395), N.ramp(swirl, 0.36, 0.56, 0.45, 1.0)),
                  N.mul(N.ramp(patch, 0.56, 0.66), N.ramp(swirl, 0.40, 0.60, 0.3, 0.9)))
    crema = N.math('MINIMUM', crema, 1.0)
    bub, _ = N.voronoi(P, 1500.0)
    big, _ = N.voronoi(P, 420.0, randomness=0.8)
    big_m = N.mul(N.ramp(big, 0.22, 0.12), N.ramp(rr, 0.036, 0.041))           # krupniji mehurići uz zid
    foam = N.mix(N.ramp(swirl, 0.3, 0.7), (0.20, 0.095, 0.040), (0.42, 0.24, 0.11))
    foam = N.mix(N.mul(N.ramp(bub, 0.30, 0.05), 0.35), foam, (0.55, 0.36, 0.19))
    col = N.mix(crema, (0.010, 0.0045, 0.0020), foam)
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


def mat_surface(name, hex_color, rough=(0.5, 0.7), spec=0.4, bump=0.00004, scale=1.0):
    """Mat farbana ploča (sto, zid): boja iz dizajna, blaga mrljavost, sitna tekstura gleta."""
    m, nt, bsdf, N = new_material(name)
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    base = srgb(hex_color)
    lo = tuple(c * 0.90 for c in base)
    hi = tuple(min(c * 1.10, 1.0) for c in base)
    big = N.noise(P, 2.2 * scale, detail=4, rough=0.6)
    col = N.mix(N.ramp(big, 0.30, 0.70), lo, hi)
    fine = N.noise(P, 700.0 * scale, detail=3, rough=0.6)
    speck, _ = N.voronoi(P, 380.0 * scale)
    col = N.mix(N.mul(N.ramp(speck, 0.08, 0.02), 0.25), col, tuple(c * 0.75 for c in base))
    N.put(col, bsdf.inputs['Base Color'])
    N.put(N.mixf(N.ramp(N.noise(P, 6.0 * scale, detail=3), 0.35, 0.70), rough[0], rough[1]),
          bsdf.inputs['Roughness'])
    bsdf.inputs['Specular IOR Level'].default_value = spec
    b = N.new('ShaderNodeBump')
    b.inputs['Distance'].default_value = 1.0
    N.put(N.mul(N.add(fine, N.mul(N.noise(P, 90.0 * scale, detail=2), 0.5)), bump), b.inputs['Height'])
    N.put(b.outputs['Normal'], bsdf.inputs['Normal'])
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
    N = Nodes(ng)
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
    C.render_settings(scene, width=args.res, height=args.res, samples=args.samples, transparent=transparent)
    cy = scene.cycles
    cy.adaptive_threshold = 0.012
    cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    cy.denoising_prefilter = 'ACCURATE'
    cy.denoising_quality = 'HIGH'
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 8, 4, 4
    cy.caustics_reflective = cy.caustics_refractive = False
    cy.blur_glossy = 0.2
    cy.sample_clamp_indirect = 15.0
    cy.volume_step_rate = 2.0
    scene.frame_start, scene.frame_end = 1, args.end
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = args.exposure

    world_hdri(scene, args.hdri_strength, args.hdri_rot)
    floor, wall = build_set(args.backdrop)
    photo_studio_lights((0.0, 0.0, 0.055), wall, key=args.key, strip=args.strip, sun=args.sun,
                        flags=not args.no_flags)

    rig = bpy.data.objects.new('MugRig', None)
    scene.collection.objects.link(rig)
    body = build_mug(rig)
    coffee = build_coffee(rig)
    C.assign(body, mat_stoneware(body))
    C.assign(coffee, mat_coffee(coffee))

    clock = amount = None
    if args.steam:
        steam = build_steam(rig)
        sm, clock, amount = mat_steam(steam, glow=0.6 * 2 ** -args.exposure)
        C.assign(steam, sm)
        steam.visible_shadow = False

    # kamera: spreda, 24° odozgo, lens 85; fokus malo ispred ose šolje, f/8 (cela šolja oštra, zid mekan)
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


def main():
    ap = argparse.ArgumentParser(prog='sip.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--frames', default='', help='npr. 1,45,90; prazno = svi kadrovi')
    ap.add_argument('--end', type=int, default=90)
    ap.add_argument('--res', type=int, default=1200)
    ap.add_argument('--samples', type=int, default=160)
    ap.add_argument('--spin', type=float, default=28.0)
    ap.add_argument('--drop', type=float, default=0.045)
    ap.add_argument('--exposure', type=float, default=0.0)
    ap.add_argument('--backdrop', action='store_true', help='sto i zid umesto providne pozadine')
    ap.add_argument('--fstop', type=float, default=8.0)
    ap.add_argument('--elev', type=float, default=24.0, help='ugao kamere odozgo (°)')
    ap.add_argument('--dist', type=float, default=0.60)
    ap.add_argument('--frame-z', dest='frame_z', type=float, default=0.050)
    ap.add_argument('--key', type=float, default=110.0, help='key prozor (area 0,6x0,9 m), W')
    ap.add_argument('--strip', type=float, default=28.0, help='svaka od dve trake pozadi, W')
    ap.add_argument('--sun', type=float, default=2.2, help='sunce na zidu (gobo), W/m²')
    ap.add_argument('--no-flags', dest='no_flags', action='store_true')
    ap.add_argument('--hdri-strength', dest='hdri_strength', type=float, default=0.10)
    ap.add_argument('--hdri-rot', dest='hdri_rot', type=float, default=HDRI_WINDOW_AZ - KEY_AZ)
    ap.add_argument('--grain', type=float, default=0.0, help='samo za probu; na sajtu ide CSS')
    ap.add_argument('--vignette', type=float, default=0.0, help='samo za probu')
    ap.add_argument('--poster', action='store_true')
    ap.add_argument('--steam', action='store_true', help='para (volumen); podrazumevano isključena')
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
