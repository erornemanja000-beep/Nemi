"""Nemi Studio, reklama od 19 s: tačka-ideja koja odskače i gradi mali bečki svet (voxel), pa postaje tačka u logu NEMI.

Pokretanje (Blender 4.5 LTS, bez auto-run-a i bez mreže):
  blender -b --factory-startup -Y --offline-mode --python-exit-code 1 -P scena.py -- <mod> <izlaz> [opcije]
  mod: preview  -> mali kadrovi (640x360) za proveru tajminga
       final    -> PNG kadrovi; opcije: uzorci, prvi kadar, poslednji kadar, rezolucija (npr. 6 1 240 1600x900)
       stills   -> pojedinačni kadrovi; opcije su sekunde, npr. 2.0 5.5 9.0
Za EEVEE bez ekrana pokreni kroz xvfb-run.

Priča (sekunde):
  0.0–3.0   mrak, tačka pada i odskače           "Alles beginnt / mit einer Idee."
  3.0–8.0   svaki odskok gradi: ulica, zgrade, Riesenrad, kafić   "Wir geben ihr / Form."
  8.0–12.5  telefon u vazduhu: sajt, video, 3D okret               "Websites. / Videos. / 3D."
  12.5–15.4 sumrak, prozori se pale, ljudi dolaze                  "Damit Wien / dich sieht."
  15.4–19.0 tačka odlazi u nebo i postaje tačka u logu NEMI.
"""
import bpy
import math
import random
import sys
import zlib
from mathutils import Matrix, Vector

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
MODE = ARGS[0] if ARGS else 'preview'
OUT = ARGS[1] if len(ARGS) > 1 else '/tmp/nemi_out/'
FPS = 25
END_S = 19.0


def F(s):
    return int(round(s * FPS)) + 1


FONT_BLACK = '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf'
FONT_SEMI = '/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf'

# ------------------------------------------------------------------ osnova
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
COLL = sc.collection
PREF = bpy.context.preferences.edit


def seed_of(*a):
    return zlib.crc32(repr(a).encode()) % 100000


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def K(owner, attr, frame, value, interp='BEZIER', easing='AUTO'):
    """Ključni kadar; interpolacija važi za deo posle ovog ključa (BOUNCE/BACK/ELASTIC su ease-out)."""
    setattr(owner, attr, value)
    owner.keyframe_insert(attr, frame=frame)
    path = owner.path_from_id(attr)
    for fc in owner.id_data.animation_data.action.fcurves:
        if fc.data_path == path:
            for k in fc.keyframe_points:
                if abs(k.co.x - frame) < 0.01:
                    k.interpolation = interp
                    k.easing = easing


def KI(ob, attr, idx, frame, value, interp='BEZIER', easing='AUTO'):
    """Ključ za jednu komponentu vektora, sa izborom easing-a."""
    getattr(ob, attr)[idx] = value
    PREF.keyframe_new_interpolation_type = interp
    ob.keyframe_insert(attr, index=idx, frame=frame)
    fc = ob.animation_data.action.fcurves.find(attr, index=idx)
    for k in fc.keyframe_points:
        if abs(k.co.x - frame) < 0.01:
            k.interpolation = interp
            k.easing = easing


def show_at(ob, t, scale=(1, 1, 1)):
    """Objekat ne postoji (scale 0) do trenutka t."""
    K(ob, 'scale', 1, (0, 0, 0), 'CONSTANT')
    K(ob, 'scale', F(t), scale, 'CONSTANT')


def pop(ob, t, dur=0.45, interp='BACK', final=(1, 1, 1), start=(0, 0, 0)):
    K(ob, 'scale', 1, start, 'CONSTANT')
    K(ob, 'scale', F(t), start, interp)
    K(ob, 'scale', F(t + dur), final, 'BEZIER')


def link(ob):
    COLL.objects.link(ob)
    return ob


# ------------------------------------------------------------------ materijali
MAT = {}


def principled(name, color=(0.8, 0.8, 0.8), rough=0.6, metal=0.0, emit=None, strength=0.0, vcol=False, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    if vcol:
        a = nt.nodes.new('ShaderNodeAttribute')
        a.attribute_name = 'vcol'
        nt.links.new(a.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    MAT[name] = m
    return m


def emis(m):
    return m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']


principled('voxel', vcol=True, rough=0.72, spec=0.35)
principled('metal', vcol=True, rough=0.28, metal=1.0)
WARM = srgb('#FFB86B')
principled('shopglass', srgb('#2A2338'), rough=0.1, emit=WARM, strength=0.0)
principled('lamp', srgb('#FFE2A8'), rough=0.4, emit=srgb('#FFD38A'), strength=0.0)
principled('wheel_light', srgb('#FFD38A'), rough=0.4, emit=srgb('#FFC24B'), strength=0.0)
principled('text', srgb('#FFF8F0'), rough=0.35, emit=srgb('#FFF8F0'), strength=1.8)
principled('text_shadow', (0.0, 0.0, 0.0), rough=1.0, spec=0.0)
principled('text_coral', srgb('#FF5C7A'), rough=0.35, emit=srgb('#FF5C7A'), strength=2.2)
principled('text_amber', srgb('#FFC24B'), rough=0.35, emit=srgb('#FFC24B'), strength=1.6)
principled('neon', srgb('#FFF4E6'), rough=0.3, emit=srgb('#FFE9CF'), strength=0.0)
principled('dot', srgb('#FF5C7A'), rough=0.25, emit=srgb('#FF5C7A'), strength=7.0)
principled('phone_body', srgb('#16131F'), rough=0.22, metal=0.6)
principled('phone_rim', srgb('#FF5C7A'), rough=0.3, emit=srgb('#FF5C7A'), strength=2.5)
principled('screen', srgb('#141226'), rough=0.2, emit=srgb('#1D1940'), strength=1.0)
for nm, hx, st in [('ui_white', '#F6F3FF', 1.4), ('ui_violet', '#7C5CFF', 1.6), ('ui_coral', '#FF5C7A', 1.6),
                   ('ui_amber', '#FFC24B', 1.6), ('ui_teal', '#3DD9C5', 1.4), ('ui_dim', '#3A3560', 1.0)]:
    principled(nm, srgb(hx), rough=0.3, emit=srgb(hx), strength=st)

# ------------------------------------------------------------------ voxel graditelj
PAL = {}


def pal(key, hexc, mat='voxel'):
    PAL[key] = (srgb(hexc), mat)


for k, h in [('yel', '#E9BE4F'), ('yel_d', '#C99A35'), ('white', '#F3EEE4'), ('pink', '#E7AFA6'), ('pink_d', '#C98C84'),
             ('mint', '#9FC9B4'), ('mint_d', '#78A38E'), ('cream', '#EDE1C8'), ('cream_d', '#CDBB98'),
             ('blue', '#A9BCD8'), ('blue_d', '#8197BA'),
             ('roof_red', '#9A3F2F'), ('roof_slate', '#40465C'), ('chim', '#6E4B42'), ('door', '#5A3B2A'),
             ('cob1', '#55525F'), ('cob2', '#4B4855'), ('cob3', '#5E5B68'), ('side1', '#8E8A93'), ('side2', '#9A96A0'),
             ('tram_red', '#D52B32'), ('tram_cream', '#F1E6D0'), ('tram_dark', '#2A2D3A'),
             ('tree1', '#3F9157'), ('tree2', '#58AC6C'), ('tree3', '#2F7546'), ('trunk', '#6B4A35'), ('post', '#2B2E3B'),
             ('wheel_red', '#C0313A'), ('wheel_white', '#EFE9E0'), ('coral', '#FF5C7A'), ('amber', '#FFC24B'),
             ('violet', '#7C5CFF'), ('teal', '#3DD9C5'), ('skin', '#F2C7A5'), ('skin2', '#B98563'), ('hair', '#2B2230'),
             ('pants', '#2F3348'), ('pants2', '#4A3F35'), ('awn_c', '#FF5C7A'), ('awn_w', '#FFF3E3')]:
    pal(k, h)
pal('rail', '#B8B8C4', 'metal')
pal('shopglass', '#2A2338', 'shopglass')
pal('lamp', '#FFE2A8', 'lamp')
pal('wlight', '#FFD38A', 'wheel_light')

FACES = {
    (1, 0, 0): [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
    (-1, 0, 0): [(0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)],
    (0, 1, 0): [(1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)],
    (0, -1, 0): [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
    (0, 0, 1): [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
    (0, 0, -1): [(0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)],
}


def voxel_obj(name, vox, size=1.0, origin=(0, 0, 0), pivot=None, jitter=0.045, seed=1):
    """vox: {(x,y,z): ključ palete}. Pravi mesh samo od vidljivih strana; boja ide u atribut 'vcol'.
    pivot je u voxel koordinatama (podrazumevano: sredina osnove)."""
    rnd = random.Random(seed)
    if pivot is None:
        xs = [v[0] for v in vox]
        ys = [v[1] for v in vox]
        zs = [v[2] for v in vox]
        pivot = ((min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2, min(zs))
    px, py, pz = pivot
    verts, faces, cols, mats, names = [], [], [], [], []
    for (x, y, z), key in vox.items():
        base, mname = PAL[key]
        v = 1 + rnd.uniform(-jitter, jitter)
        c = (base[0] * v, base[1] * v, base[2] * v, 1.0)
        if mname not in names:
            names.append(mname)
        mi = names.index(mname)
        for d, quad in FACES.items():
            if (x + d[0], y + d[1], z + d[2]) in vox:
                continue
            i = len(verts)
            for q in quad:
                verts.append(((x + q[0] - px) * size, (y + q[1] - py) * size, (z + q[2] - pz) * size))
            faces.append((i, i + 1, i + 2, i + 3))
            cols.extend(c * 4)
            mats.append(mi)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    attr = me.color_attributes.new('vcol', 'FLOAT_COLOR', 'CORNER')
    attr.data.foreach_set('color', cols)
    for mn in names:
        me.materials.append(MAT[mn])
    me.polygons.foreach_set('material_index', mats)
    me.update()
    ob = link(bpy.data.objects.new(name, me))
    ob.location = (origin[0] + px * size, origin[1] + py * size, origin[2] + pz * size)
    return ob


# ------------------------------------------------------------------ svet: pod, nebo, svetlo
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
floor = bpy.context.object
floor.name = 'pod'
fm = bpy.data.materials.new('pod')
fm.use_nodes = True
nt = fm.node_tree
b = nt.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (*srgb('#0B0A12'), 1)
b.inputs['Roughness'].default_value = 0.28
# daleko se pod stapa sa horizontom (emisija boje horizonta raste sa razdaljinom)
tc = nt.nodes.new('ShaderNodeTexCoord')
ln = nt.nodes.new('ShaderNodeVectorMath')
ln.operation = 'LENGTH'
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = 60
mr.inputs['From Max'].default_value = 260
nt.links.new(tc.outputs['Object'], ln.inputs[0])
nt.links.new(ln.outputs['Value'], mr.inputs['Value'])
nt.links.new(mr.outputs['Result'], b.inputs['Emission Strength'])
FLOOR_HORIZON = b.inputs['Emission Color']
floor.data.materials.append(fm)

world = bpy.data.worlds.new('nebo')
sc.world = world
world.use_nodes = True
wn = world.node_tree
bg = wn.nodes['Background']
wtc = wn.nodes.new('ShaderNodeTexCoord')
sep = wn.nodes.new('ShaderNodeSeparateXYZ')
wmr = wn.nodes.new('ShaderNodeMapRange')
wmr.inputs['From Min'].default_value = -0.05
wmr.inputs['From Max'].default_value = 0.7
wn.links.new(wtc.outputs['Generated'], sep.inputs[0])
wn.links.new(sep.outputs['Z'], wmr.inputs['Value'])


def ramp(stops):
    r = wn.nodes.new('ShaderNodeValToRGB')
    els = r.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], (*srgb(stops[0][1]), 1)
    els[1].position, els[1].color = stops[-1][0], (*srgb(stops[-1][1]), 1)
    for p, h in stops[1:-1]:
        e = els.new(p)
        e.color = (*srgb(h), 1)
    wn.links.new(wmr.outputs['Result'], r.inputs['Fac'])
    return r


day = ramp([(0.0, '#F6B38E'), (0.3, '#B49AD6'), (0.65, '#5B57B0'), (1.0, '#24245E')])
dusk = ramp([(0.0, '#FF8A5C'), (0.22, '#8A4FA8'), (0.55, '#33287A'), (1.0, '#0D0B28')])
mix1 = wn.nodes.new('ShaderNodeMix')
mix1.data_type = 'RGBA'
mix2 = wn.nodes.new('ShaderNodeMix')
mix2.data_type = 'RGBA'
mix1.inputs['A'].default_value = (*srgb('#050409'), 1)
wn.links.new(day.outputs['Color'], mix1.inputs['B'])
wn.links.new(mix1.outputs['Result'], mix2.inputs['A'])
wn.links.new(dusk.outputs['Color'], mix2.inputs['B'])
wn.links.new(mix2.outputs['Result'], bg.inputs['Color'])
SKY1 = mix1.inputs['Factor']
SKY2 = mix2.inputs['Factor']
bg.inputs['Strength'].default_value = 1.0

# dan: od 3.4 s; sumrak: od 12.5 s (rez)
K(SKY1, 'default_value', 1, 0.0)
K(SKY1, 'default_value', F(3.45), 0.0)
K(SKY1, 'default_value', F(5.2), 1.0)
K(SKY2, 'default_value', F(12.45), 0.0, 'CONSTANT')
K(SKY2, 'default_value', F(12.5), 0.85)
K(SKY2, 'default_value', F(15.0), 1.0)
for t, h in [(0, '#050409'), (3.45, '#050409'), (5.2, '#E7A784'), (12.45, '#E7A784'), (12.5, '#C26A57'), (15.0, '#7A3F5C')]:
    K(FLOOR_HORIZON, 'default_value', F(t), (*srgb(h), 1), 'CONSTANT' if t == 12.45 else 'BEZIER')

sun_d = bpy.data.lights.new('sunce', 'SUN')
sun_d.color = srgb('#FFD2A8')
sun_d.angle = math.radians(4)
sun = link(bpy.data.objects.new('sunce', sun_d))
sun.rotation_euler = (math.radians(52), math.radians(8), math.radians(-38))
for t, e in [(0, 0.0), (3.45, 0.0), (4.8, 4.2), (12.45, 4.2), (12.5, 0.9), (15.0, 0.45)]:
    K(sun_d, 'energy', F(t), e, 'CONSTANT' if t == 12.45 else 'BEZIER')

fill_d = bpy.data.lights.new('popuna', 'AREA')
fill_d.size = 30
fill_d.color = srgb('#9DB4FF')
fill = link(bpy.data.objects.new('popuna', fill_d))
fill_d.use_shadow = False
fill.location = (-10, -40, 25)
fill.rotation_euler = (math.radians(60), 0, math.radians(-15))
for t, e in [(0, 0), (3.45, 0), (5.0, 9000), (12.45, 9000), (12.5, 5000)]:
    K(fill_d, 'energy', F(t), e, 'CONSTANT' if t == 12.45 else 'BEZIER')

# ------------------------------------------------------------------ zgrade
Y0 = 5  # prednja strana fasade


def house(x0, w, floors, fac, acc, roof, kind, gid, depth=8, fh=4):
    """Bečka zgrada (Gründerzeit): prizemlje (lokal ili obično), spratovi sa prozorima, venci, mansardni krov."""
    gh = 8 if kind == 'shop' else 5
    H = gh + floors * fh
    V = {}
    for x in range(w):
        for y in range(Y0, Y0 + depth):
            for z in range(H):
                V[(x0 + x, y, z)] = fac
    for x in range(w):  # sokla
        V[(x0 + x, Y0, 0)] = acc

    def window(xs, zs, key):
        for x in xs:
            for z in zs:
                V.pop((x0 + x, Y0, z), None)
                V[(x0 + x, Y0 + 1, z)] = key

    if kind == 'shop':
        mid = w // 2
        window(range(1, mid - 1), range(1, 5), 'shopglass')
        window(range(mid + 2, w - 1), range(1, 5), 'shopglass')
        for x in range(mid - 1, mid + 2):  # vrata
            for z in range(0, 5):
                V.pop((x0 + x, Y0, z), None)
                V[(x0 + x, Y0 + 1, z)] = 'door' if z < 4 else 'shopglass'
        for x in range(w):
            V[(x0 + x, Y0 - 1, gh - 1)] = acc  # venac iznad lokala
    else:
        mid = w // 2
        for x in range(mid - 1, mid + 1):
            for z in range(0, 4):
                V.pop((x0 + x, Y0, z), None)
                V[(x0 + x, Y0 + 1, z)] = 'door'
        for x in list(range(1, mid - 2, 3)) + list(range(mid + 2, w - 1, 3)):
            window([x, x + 1] if x + 1 < w - 1 else [x], range(1, 4), f'g_{gid}_0')
        for x in range(w):
            V[(x0 + x, Y0 - 1, gh - 1)] = acc

    n = (w - 1) // 3
    margin = (w - (n * 3 - 1)) // 2
    for f in range(floors):
        zb = gh + f * fh
        key = f'g_{gid}_{f + 1}'
        for i in range(n):
            xa = margin + i * 3
            window([xa, xa + 1], range(zb + 1, zb + 4), key)
            for x in (xa, xa + 1):
                V[(x0 + x, Y0 - 1, zb)] = 'white'  # prozorska daska
            if f == 0:
                for x in (xa - 1, xa, xa + 1, xa + 2):
                    if 0 <= x < w:
                        V[(x0 + x, Y0 - 1, zb + 3)] = acc  # zabat iznad prozora prvog sprata
    for x in range(w):
        V[(x0 + x, Y0 - 1, H - 1)] = acc  # krovni venac
    for s in range(4):  # mansarda
        z = H + s
        for x in range(w):
            for y in range(Y0 + s, Y0 + depth - s):
                V[(x0 + x, y, z)] = roof
    for cx in (2, w - 3):
        for z in range(H + 2, H + 6):
            V[(x0 + cx, Y0 + depth - 3, z)] = 'chim'
    return V, H


GLASS_KEYS = {}


def glass_mats(gid, floors):
    for f in range(floors + 1):
        key = f'g_{gid}_{f}'
        principled(key, srgb('#1C2440'), rough=0.12, emit=WARM, strength=0.0)
        pal(key, '#1C2440', key)
        GLASS_KEYS[key] = (gid, f)


BUILDINGS = [  # x0, širina, spratovi, fasada, akcenat, krov, vrsta, id, početak gradnje (s)
    (-7, 15, 3, 'yel', 'yel_d', 'roof_red', 'shop', 'h', 4.0),
    (-20, 13, 4, 'pink', 'pink_d', 'roof_slate', 'plain', 'l', 4.5),
    (-32, 12, 3, 'blue', 'blue_d', 'roof_red', 'plain', 'fl', 4.7),
    (8, 12, 3, 'mint', 'mint_d', 'roof_red', 'plain', 'r', 5.0),
    (20, 13, 4, 'cream', 'cream_d', 'roof_slate', 'plain', 'fr', 5.15),
]
for x0, w, fl, fac, acc, roof, kind, gid, tb in BUILDINGS:
    glass_mats(gid, fl)
    V, H = house(x0, w, fl, fac, acc, roof, kind, gid)
    zmax = max(v[2] for v in V)
    for z in range(zmax + 1):
        layer = {k: v for k, v in V.items() if k[2] == z}
        if not layer:
            continue
        ob = voxel_obj(f'zgrada_{gid}_{z:02d}', layer, seed=seed_of(gid, z))
        t = tb + z * 0.035
        final = ob.location.copy()
        show_at(ob, t)
        K(ob, 'location', 1, final + Vector((0, 0, 7)), 'CONSTANT')
        K(ob, 'location', F(t), final + Vector((0, 0, 7)), 'BOUNCE')
        K(ob, 'location', F(t + 0.32), final)

# ------------------------------------------------------------------ ulica (talas pločica od tačke udara)
IMPACT_A = (0.0, -3.0)
T_STREET = 3.5
rings = {}
rnd = random.Random(4)
for x in range(-44, 44):
    for y in range(-11, 5):
        if y >= 2:
            key = 'side1' if (x + y) % 2 else 'side2'
        elif y in (-4, -2):
            key = 'rail'
        else:
            key = rnd.choice(['cob1', 'cob2', 'cob3'])
        d = math.hypot(x + 0.5 - IMPACT_A[0], y + 0.5 - IMPACT_A[1])
        r = int(d / 2.6)
        rings.setdefault(r, {})[(x, y, 0)] = key
for r, vox in rings.items():
    ob = voxel_obj(f'ulica_{r:02d}', vox, pivot=(0, 0, 0), seed=r)
    ob.scale = (1, 1, 1)
    ob.location = (0, 0, 0)
    # trotoar je viši od kolovoza: posebno dizanje kroz z-skalu nije moguće po delu, pa je ulica ravna 0.3, trotoar ide preko ivičnjaka
    ob.scale = (1, 1, 0.3)
    t = T_STREET + r * 0.045
    K(ob, 'location', 1, (0, 0, -1.4), 'CONSTANT')
    K(ob, 'location', F(t), (0, 0, -1.4), 'BACK')
    K(ob, 'location', F(t + 0.35), (0, 0, 0))
curb = {}
for x in range(-44, 44):
    for y in range(2, 5):
        curb[(x, y, 0)] = 'side2' if (x + y) % 2 else 'side1'
ob = voxel_obj('trotoar', curb, pivot=(0, 0, 0), seed=9)
ob.scale = (1, 1, 0.25)
ob.location = (0, 0, 0.3)
show_at(ob, T_STREET + 0.25)

# ------------------------------------------------------------------ tenda i natpis CAFÉ
awn = {}
for x in range(-6, 7):
    for s in range(3):
        awn[(x, -s, -s)] = 'awn_c' if x % 2 == 0 else 'awn_w'
awning = voxel_obj('tenda', awn, size=1.0, pivot=(0.5, 1, 1), seed=3)
awning.location = (0, Y0, 5.2)
K(awning, 'scale', 1, (1, 0, 0), 'CONSTANT')
K(awning, 'scale', F(6.0), (1, 0.0, 0.0), 'ELASTIC')
K(awning, 'scale', F(6.8), (1, 1, 0.45))

FONTS = {}


def font(p):
    if p not in FONTS:
        FONTS[p] = bpy.data.fonts.load(p)
    return FONTS[p]


def glyph(name, ch, size, mat, fnt=FONT_BLACK, depth=0.06):
    cu = bpy.data.curves.new(name, 'FONT')
    cu.body = ch
    cu.font = font(fnt)
    cu.size = size
    cu.extrude = size * depth
    cu.bevel_depth = size * 0.01
    cu.bevel_resolution = 2
    cu.align_x = 'CENTER'
    cu.align_y = 'BOTTOM_BASELINE'
    ob = link(bpy.data.objects.new(name, cu))
    ob.data.materials.append(mat)
    return ob


def layout(chars, size, track):
    obs, xs, cur = [], [], 0.0
    for ob in chars:
        if ob is None:
            cur += size * 0.26
            obs.append(None)
            xs.append(None)
            continue
        bpy.context.view_layer.update()
        wdt = ob.dimensions.x
        obs.append(ob)
        xs.append(cur + wdt / 2)
        cur += wdt + size * track
    return obs, xs, cur - size * track


sign = [glyph(f'cafe_{i}', ch, 1.25, MAT['neon'], depth=0.12) for i, ch in enumerate('CAFÉ')]
obs, xs, tot = layout(sign, 1.25, 0.12)
for i, (ob, cx) in enumerate(zip(obs, xs)):
    ob.location = (cx - tot / 2, Y0 - 0.2, 5.3)
    ob.rotation_euler = (math.radians(90), 0, 0)
    ob.visible_shadow = True
    pop(ob, 6.15 + i * 0.07, 0.4)
K(emis(MAT['neon']), 'default_value', 1, 0.0)
K(emis(MAT['neon']), 'default_value', F(6.15), 0.0)
K(emis(MAT['neon']), 'default_value', F(6.5), 3.0)
K(emis(MAT['neon']), 'default_value', F(12.5), 3.0)
K(emis(MAT['neon']), 'default_value', F(13.0), 6.0)
K(emis(MAT['shopglass']), 'default_value', 1, 0.0)
K(emis(MAT['shopglass']), 'default_value', F(6.1), 0.0)
K(emis(MAT['shopglass']), 'default_value', F(6.6), 1.6)
K(emis(MAT['shopglass']), 'default_value', F(12.8), 1.6)
K(emis(MAT['shopglass']), 'default_value', F(13.1), 5.0)

# ------------------------------------------------------------------ drveće, fenjeri
def tree(x, y, seed, t):
    r = random.Random(seed)
    V = {}
    for z in range(0, 6):
        V[(0, 0, z)] = 'trunk'
    for dx in range(-4, 5):
        for dy in range(-4, 5):
            for dz in range(-3, 5):
                if dx * dx + dy * dy + (dz * 1.2) ** 2 <= 15 + r.uniform(-3, 3):
                    V[(dx, dy, 8 + dz)] = r.choice(['tree1', 'tree2', 'tree3'])
    ob = voxel_obj(f'drvo_{seed}', V, size=0.45, pivot=(0.5, 0.5, 0), seed=seed)
    ob.location = (x, y, 0.3)
    pop(ob, t, 0.7, 'ELASTIC')
    return ob


for i, (x, t) in enumerate([(-13.5, 5.6), (13.5, 5.75), (-27, 5.9), (27, 6.0)]):
    tree(x, 3.2, 20 + i, t)


def lamp_post(x, t):
    V = {}
    for z in range(0, 20):
        V[(0, 0, z)] = 'post'
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            V[(dx, dy, 20)] = 'post'
            V[(dx, dy, 21)] = 'lamp'
            V[(dx, dy, 22)] = 'lamp'
            V[(dx, dy, 23)] = 'post'
    V[(0, 0, 24)] = 'post'
    ob = voxel_obj(f'fenjer_{x}', V, size=0.28, pivot=(0.5, 0.5, 0), seed=int(abs(x)))
    ob.location = (x, 2.3, 0.3)
    pop(ob, t, 0.5, 'BACK')


for x, t in [(-9.5, 5.85), (9.5, 5.95), (-23, 6.05), (23, 6.1)]:
    lamp_post(x, t)
lamp_e = emis(MAT['lamp'])
for t, e in [(0, 0), (12.6, 0), (12.9, 8)]:
    K(lamp_e, 'default_value', F(t), e)

# ------------------------------------------------------------------ Riesenrad
RR_C = Vector((62, 8, 27))
RR_R = 26  # u voxelima od 0.5
wheel_v = {}
for a in range(0, 720):
    ang = math.radians(a / 2)
    for rr in (RR_R - 1, RR_R):
        x = int(round(math.cos(ang) * rr))
        z = int(round(math.sin(ang) * rr))
        for y in (-3, 3):
            wheel_v[(x, y, z)] = 'wheel_red'
for i in range(24):
    ang = math.radians(i * 15)
    for s in range(0, RR_R - 1):
        x = int(round(math.cos(ang) * s))
        z = int(round(math.sin(ang) * s))
        for y in (-3, 3):
            wheel_v.setdefault((x, y, z), 'wheel_white')
    lx = int(round(math.cos(ang) * (RR_R + 1)))
    lz = int(round(math.sin(ang) * (RR_R + 1)))
    wheel_v[(lx, 0, lz)] = 'wlight'
for y in range(-3, 4):
    for x in (-1, 0, 1):
        for z in (-1, 0, 1):
            wheel_v[(x, y, z)] = 'wheel_red'
wheel = voxel_obj('riesenrad', wheel_v, size=0.5, pivot=(0.5, 0.5, 0.5), seed=5)
wheel.location = RR_C
legs_v = {}
for side in (-1, 1):
    for i in range(0, 47):
        k = i / 46
        x = int(round(side * (18 - 18 * k)))
        z = int(round(46 * k))
        for y in (-6, 6):
            for dx in (0, 1):
                legs_v[(x + dx, y, z)] = 'wheel_white'
legs = voxel_obj('riesenrad_noge', legs_v, size=0.5, pivot=(0.5, 0.5, 0), seed=6)
legs.location = (RR_C.x, RR_C.y, 0)
pop(legs, 5.5, 0.6, 'BACK')
K(wheel, 'scale', 1, (0, 0, 0), 'CONSTANT')
K(wheel, 'scale', F(5.65), (0, 0, 0), 'BACK')
K(wheel, 'scale', F(6.35), (1, 1, 1))
K(wheel, 'rotation_euler', 1, (0, 0, 0), 'LINEAR')
K(wheel, 'rotation_euler', F(END_S) + 1, (0, math.radians(-150), 0), 'LINEAR')
K(emis(MAT['wheel_light']), 'default_value', 1, 1.5)
K(emis(MAT['wheel_light']), 'default_value', F(12.5), 1.5)
K(emis(MAT['wheel_light']), 'default_value', F(13.2), 9.0)
gond_v = {}
for x in range(-2, 2):
    for y in range(-2, 2):
        for z in range(-4, 0):
            gond_v[(x, y, z)] = 'wheel_red' if z in (-4, -1) else ('wheel_white' if (x in (-2, 1) or y in (-2, 1)) and z == -2 else 'wheel_red')
for i in range(12):
    g = voxel_obj(f'gondola_{i}', gond_v, size=0.5, pivot=(0, 0, 0), seed=40 + i)
    a0 = math.radians(i * 30)
    for fr in range(1, F(END_S) + 2, 4):
        ang = a0 + math.radians(150) * (fr - 1) / F(END_S)
        k = min(1.0, max(0.0, (fr - F(5.65)) / (F(6.35) - F(5.65))))
        rr = (RR_R + 0.5) * 0.5 * k
        g.location = RR_C + Vector((math.cos(ang) * rr, 0, math.sin(ang) * rr))
        PREF.keyframe_new_interpolation_type = 'LINEAR'
        g.keyframe_insert('location', frame=fr)
    pop(g, 6.2 + i * 0.02, 0.4, 'BACK')

# ------------------------------------------------------------------ tramvaj
tram_v = {}
for x in range(0, 36):
    for y in range(0, 6):
        for z in range(1, 8):
            if z <= 4:
                k = 'tram_red'
            elif z in (5, 6):
                k = 'tram_dark' if (x % 4 in (1, 2) and y in (0, 5)) or (x in (0, 35) and 1 <= y <= 4) else 'tram_cream'
            else:
                k = 'tram_red'
            tram_v[(x, y, z)] = k
    for y in range(0, 6):
        if x % 9 in (2, 3):
            tram_v[(x, y, 0)] = 'tram_dark'
for x in range(14, 22):
    tram_v[(x, 3, 8)] = 'tram_dark'
tram = voxel_obj('tramvaj', tram_v, size=0.5, seed=7)
tram.location = (-36, -3, 0.3)
pop(tram, 6.2, 0.5, 'BACK')
K(tram, 'location', F(6.7), (-36, -3, 0.3))
K(tram, 'location', F(12.5), (30, -3, 0.3), 'LINEAR')
K(tram, 'location', F(END_S), (52, -3, 0.3), 'LINEAR')

# ------------------------------------------------------------------ ljudi
PEOPLE = [('coral', 'pants', 'skin', -24.0, 12.9, -2.6), ('teal', 'pants2', 'skin2', -28.5, 13.0, -4.3),
          ('amber', 'pants', 'skin', -33.0, 13.15, -6.0), ('violet', 'pants2', 'skin2', -37.0, 13.3, -7.7)]
for i, (shirt, pants, skin, x_start, t0, x_end) in enumerate(PEOPLE):
    V = {}
    for x in range(4):
        for y in range(2):
            for z in range(0, 4):
                if x in (0, 3) or z >= 3:
                    V[(x, y, z)] = pants
            for z in range(4, 8):
                V[(x, y, z)] = shirt
    for x in (1, 2):
        for y in range(2):
            for z in (8, 9):
                V[(x, y, z)] = skin
            V[(x, y, 10)] = 'hair'
        V[(x, 1, 9)] = 'hair'
    p = voxel_obj(f'osoba_{i}', V, size=0.22, pivot=(2, 1, 0), seed=60 + i)
    p.rotation_euler = (0, 0, math.radians(90))
    t_arrive = t0 + 2.2
    fr0, fr1 = F(12.5), F(t_arrive)
    for fr in range(fr0, fr1 + 1, 3):
        k = (fr - fr0) / max(1, fr1 - fr0)
        k = 1 - (1 - k) ** 2
        x = x_start + (x_end - x_start) * k
        bob = abs(math.sin((fr - fr0) * 0.55 + i)) * 0.18 * (1 - k * 0.6)
        p.location = (x, 3.2 + 0.25 * math.sin(i), 0.3 + bob)
        PREF.keyframe_new_interpolation_type = 'BEZIER'
        p.keyframe_insert('location', frame=fr)
    show_at(p, 12.45)

# ------------------------------------------------------------------ ikone iznad lokala (srce, zvezda, pin)
ICONS = {
    'srce': ('coral', ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...']),
    'zvezda': ('amber', ['...X...', '..XXX..', 'XXXXXXX', '.XXXXX.', '.XX.XX.', 'XX...XX']),
    'pin': ('violet', ['.XXXXX.', 'XX...XX', 'XX...XX', '.XXXXX.', '..XXX..', '...X...']),
}
for i, (name, (col, rows)) in enumerate(ICONS.items()):
    V = {}
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == 'X':
                for y in (0, 1):
                    V[(c, y, len(rows) - r)] = col
    pal(col + '_e', '#FF5C7A' if col == 'coral' else '#FFC24B' if col == 'amber' else '#7C5CFF')
    ob = voxel_obj(f'ikona_{name}', V, size=0.38, pivot=(3.5, 1, 3.5), seed=80 + i)
    x = -4.2 + i * 4.2
    t = 13.0 + i * 0.5
    ob.location = (x, 2.0, 11.5)
    ob.rotation_euler = (0, 0, math.radians(-25 + i * 8))
    K(ob, 'scale', 1, (0, 0, 0), 'CONSTANT')
    K(ob, 'scale', F(t), (0, 0, 0), 'ELASTIC')
    K(ob, 'scale', F(t + 0.7), (1, 1, 1))
    K(ob, 'scale', F(15.2), (1, 1, 1), 'EXPO')
    K(ob, 'scale', F(15.45), (0, 0, 0))
    K(ob, 'location', F(t), (x, 2.0, 11.0))
    K(ob, 'location', F(15.3), (x, 2.0, 12.6))

# ------------------------------------------------------------------ telefon u vazduhu
PH = Vector((5.0, -4.0, 15.0))
rig = link(bpy.data.objects.new('telefon', None))
rig.location = PH + Vector((0, 0, -30))


def box(name, dims, loc, mat, bevel=0.0, parent=rig):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m = ob.modifiers.new('bevel', 'BEVEL')
        m.width = bevel
        m.segments = 6
    ob.data.materials.append(mat)
    ob.parent = parent
    ob.location = loc
    return ob


box('telefon_ivica', (7.22, 0.42, 14.22), (0, 0, 0), MAT['phone_rim'], 1.0)
box('telefon_telo', (7.0, 0.7, 14.0), (0, 0, 0), MAT['phone_body'], 0.95)
box('telefon_ekran', (6.3, 0.05, 13.2), (0, -0.36, 0), MAT['screen'], 0.6)
UI = [  # ime, dimenzije (x, z), pozicija (x, z), materijal, trenutak, sloj za 3D raspad
    ('status', (5.6, 0.22), (0, 6.05), 'ui_dim', 8.45, 1),
    ('logo', (0.5, 0.5), (-2.5, 5.3), 'ui_coral', 8.5, 2),
    ('meni1', (1.2, 0.16), (2.3, 5.45), 'ui_white', 8.55, 2),
    ('meni2', (1.2, 0.16), (2.3, 5.15), 'ui_white', 8.58, 2),
    ('hero', (5.6, 4.4), (0, 2.6), 'ui_violet', 8.55, 1),
    ('naslov1', (4.6, 0.55), (-0.5, -0.4), 'ui_white', 8.7, 3),
    ('naslov2', (3.2, 0.55), (-1.2, -1.25), 'ui_white', 8.75, 3),
    ('tekst', (4.2, 0.16), (-0.7, -2.0), 'ui_dim', 8.8, 2),
    ('dugme', (2.4, 0.75), (-1.6, -3.0), 'ui_amber', 8.85, 3),
    ('kartica1', (2.6, 2.4), (-1.45, -5.0), 'ui_coral', 8.95, 2),
    ('kartica2', (2.6, 2.4), (1.45, -5.0), 'ui_teal', 9.0, 2),
]
UI_OBS = []
for name, (w, h), (x, z), m, t, layer in UI:
    ob = box(f'ui_{name}', (w, 0.18, h), (x, -0.5, z), MAT[m], min(w, h) * 0.2)
    pop(ob, t, 0.4, 'BACK')
    UI_OBS.append((ob, layer, x, z))
# video: progres traka i trougao „play" preko tačke
prog = box('ui_progres', (5.0, 0.12, 0.16), (-2.5, -0.62, 0.55), MAT['ui_amber'], 0.05)
for v in prog.data.vertices:
    v.co.x += 2.5
K(prog, 'scale', 1, (0, 1, 1), 'CONSTANT')
K(prog, 'scale', F(9.5), (0.0, 1, 1), 'LINEAR')
K(prog, 'scale', F(12.0), (1, 1, 1))
tri_cu = bpy.data.curves.new('play', 'CURVE')
tri_cu.dimensions = '2D'
tri_cu.extrude = 0.08
spl = tri_cu.splines.new('POLY')
spl.points.add(2)
for p, co in zip(spl.points, [(-0.22, -0.28), (-0.22, 0.28), (0.3, 0.0)]):
    p.co = (co[0], co[1], 0, 1)
spl.use_cyclic_u = True
tri = link(bpy.data.objects.new('play', tri_cu))
tri.data.materials.append(MAT['text'])
tri.parent = rig
tri.rotation_euler = (math.radians(90), 0, 0)
tri.location = (0.05, -1.72, 2.6)
pop(tri, 9.5, 0.4, 'BACK')
K(tri, 'scale', F(10.3), (1, 1, 1), 'EXPO')
K(tri, 'scale', F(10.45), (0, 0, 0))

# telefon uleće, 3D okret sa raspadom slojeva, odlazi
K(rig, 'location', 1, PH + Vector((0, 0, -30)), 'CONSTANT')
K(rig, 'location', F(7.9), PH + Vector((0, 0, -30)), 'BACK')
K(rig, 'location', F(8.45), PH)
K(rig, 'rotation_euler', 1, (0, 0, math.radians(-14)), 'CONSTANT')
K(rig, 'rotation_euler', F(7.9), (0, 0, math.radians(-14)), 'BACK')
K(rig, 'rotation_euler', F(8.45), (0, 0, math.radians(-14)))
K(rig, 'rotation_euler', F(10.5), (0, 0, math.radians(-14)), 'BACK')
K(rig, 'rotation_euler', F(11.3), (0, 0, math.radians(-14 + 360)))
for ob, layer, x, z in UI_OBS:
    K(ob, 'location', F(10.45), (x, -0.5, z))
    K(ob, 'location', F(10.75), (x, -0.5 - layer * 0.9, z), 'BACK')
    K(ob, 'location', F(11.15), (x, -0.5 - layer * 0.9, z))
    K(ob, 'location', F(11.45), (x, -0.5, z))
K(rig, 'location', F(12.2), PH)
K(rig, 'location', F(12.5), PH + Vector((0, 0, 40)), 'CONSTANT')

# ------------------------------------------------------------------ kamere
def camera(name, lens=35):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.1
    cd.clip_end = 2000
    cam = link(bpy.data.objects.new(name, cd))
    tgt = link(bpy.data.objects.new(name + '_meta', None))
    shake = link(bpy.data.objects.new(name + '_tres', None))
    shake.parent = tgt
    c = cam.constraints.new('TRACK_TO')
    c.target = shake
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'
    return cam, tgt, shake


def path(cam, tgt, keys):
    for t, loc, look in keys:
        K(cam, 'location', F(t), loc)
        K(tgt, 'location', F(t), look)


def shake(sh, t, amp, n=7):
    fr = F(t)
    K(sh, 'location', fr - 1, (0, 0, 0))
    for i in range(1, n):
        a = amp * math.exp(-i * 0.55) * (1 if i % 2 else -1)
        K(sh, 'location', fr + i, (a * 0.4, 0, a))
    K(sh, 'location', fr + n, (0, 0, 0))


camA, tgtA, shA = camera('kameraA', 35)
camB, tgtB, shB = camera('kameraB', 40)
camC, tgtC, shC = camera('kameraC', 32)
path(camA, tgtA, [
    (0.0, (0.8, -12.0, 1.5), (0.0, -3.0, 1.6)),
    (2.85, (0.3, -10.2, 1.25), (0.0, -3.0, 1.0)),
    (3.25, (0.4, -11.5, 2.8), (0.0, -3.0, 3.0)),
    (3.7, (1.0, -18.0, 5.0), (0.0, -1.0, 3.0)),
    (4.6, (4.0, -38.0, 11.0), (0.0, 4.0, 10.5)),
    (5.9, (12.0, -62.0, 16.0), (1.0, 6.0, 13.0)),
    (8.1, (-8.0, -60.0, 14.5), (0.0, 5.0, 12.0)),
])
path(camB, tgtB, [
    (7.9, (-13.0, -30.0, 7.0), (1.0, -4.0, 16.0)),
    (12.5, (-10.0, -25.0, 8.0), (2.0, -4.0, 16.0)),
])
FINAL_CAM = ((-2.0, -34.0, 20.0), (0.0, 10.0, 34.0))
path(camC, tgtC, [
    (12.4, (-21.0, -6.5, 2.4), (4.0, 6.0, 5.5)),
    (15.2, (-16.0, -5.5, 2.9), (3.0, 5.5, 6.2)),
    (15.75, (-10.0, -20.0, 10.0), (0.0, 8.0, 22.0)),
    (16.4, FINAL_CAM[0], FINAL_CAM[1]),
    (END_S, FINAL_CAM[0], FINAL_CAM[1]),
])
for cam in (camA, camB, camC):
    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
sc.camera = camA
m = sc.timeline_markers.new('A', frame=1)
m.camera = camA
m = sc.timeline_markers.new('B', frame=F(8.0))
m.camera = camB
m = sc.timeline_markers.new('C', frame=F(12.5))
m.camera = camC

# ------------------------------------------------------------------ naslovi (3D slova vezana za kameru)
def title(name, text, cam, x, y, d, size, t_in, t_out, align='center', accent=(), fnt=FONT_BLACK, mat='text',
          stagger=0.035, track=0.06, style='drop', shadow=True):
    words = text.split(' ')
    chars, mats = [], []
    for wi, wd in enumerate(words):
        for ch in wd:
            mname = 'text_coral' if ch == '.' else ('text_coral' if wi in accent else mat)
            g = glyph(f'{name}_{len(chars)}', ch, size, MAT[mname], fnt)
            if shadow:
                sh = glyph(f'{name}_{len(chars)}_s', ch, size, MAT['text_shadow'], fnt)
                sh.parent = g
                sh.location = (size * 0.05, -size * 0.07, -size * 0.1)
                sh.visible_shadow = False
            chars.append(g)
        if wi < len(words) - 1:
            chars.append(None)
    obs, xs, tot = layout(chars, size, track)
    off = x - tot / 2 if align == 'center' else x
    k = 0
    for ob, cx in zip(obs, xs):
        if ob is None:
            continue
        ob.parent = cam
        ob.visible_shadow = False
        final = Vector((off + cx, y, -d))
        t = t_in + k * stagger
        if style == 'drop':
            start = final + Vector((0, size * 5.5, 0))
            K(ob, 'location', 1, start, 'CONSTANT')
            K(ob, 'location', F(t), start, 'BOUNCE')
            K(ob, 'location', F(t + 0.55), final)
            K(ob, 'rotation_euler', 1, (math.radians(-80), 0, 0), 'CONSTANT')
            K(ob, 'rotation_euler', F(t), (math.radians(-80), 0, 0), 'BACK')
            K(ob, 'rotation_euler', F(t + 0.45), (0, 0, 0))
            show_at(ob, t)
        else:  # 'pop': iz dubine, sa prebačajem
            K(ob, 'location', 1, final + Vector((0, 0, -size * 4)), 'CONSTANT')
            K(ob, 'location', F(t), final + Vector((0, 0, -size * 4)), 'BACK')
            K(ob, 'location', F(t + 0.4), final)
            pop(ob, t, 0.4, 'BACK')
        if t_out is not None:
            to = t_out + k * 0.02
            K(ob, 'scale', F(to), (1, 1, 1), 'EXPO')
            K(ob, 'scale', F(to + 0.22), (0, 0, 0))
            K(ob, 'location', F(to), final, 'EXPO')
            K(ob, 'location', F(to + 0.22), final + Vector((0, size * 0.8, 0)))
        k += 1
    return tot


D = 12.0
title('t1a', 'Alles beginnt', camA, 0, 1.55, D, 1.0, 0.75, 2.95)
title('t1b', 'mit einer Idee.', camA, 0, 0.35, D, 1.0, 1.45, 3.0, accent=(2,))
title('t2a', 'Wir geben ihr', camA, 0, 2.05, D, 0.85, 4.25, 7.35)
title('t2b', 'Form.', camA, 0, 0.65, D, 1.45, 4.85, 7.4, accent=(0,))
title('t3a', 'Websites.', camB, -4.7, 1.25, D, 1.05, 8.5, 12.05, align='left', style='pop')
title('t3b', 'Videos.', camB, -4.7, -0.05, D, 1.05, 9.5, 12.1, align='left', style='pop')
title('t3c', '3D.', camB, -4.7, -1.35, D, 1.05, 10.5, 12.15, align='left', style='pop')
title('t4a', 'Damit Wien', camC, 0, 1.75, D, 0.95, 13.15, 15.25)
title('t4b', 'dich sieht.', camC, 0, 0.6, D, 0.95, 13.6, 15.3, accent=(1,))

# kraj: logo NEMI. (tačku donosi lopta), STUDIO, slogan, adresa
DL = 26.0
LOGO_S = 4.6
logo = [glyph(f'logo_{i}', ch, LOGO_S, MAT['text'], depth=0.08) for i, ch in enumerate('NEMI')]
period = glyph('logo_tacka_mera', '.', LOGO_S, MAT['text'])
obs, xs, tot = layout(logo + [period], LOGO_S, 0.03)
LOGO_Y = 1.7
for i, (ob, cx) in enumerate(zip(obs[:4], xs[:4])):
    ob.parent = camC
    ob.visible_shadow = False
    final = Vector((cx - tot / 2, LOGO_Y, -DL))
    t = 16.0 + i * 0.09
    start = final + Vector((0, 22, 0))
    K(ob, 'location', 1, start, 'CONSTANT')
    K(ob, 'location', F(t), start, 'BOUNCE')
    K(ob, 'location', F(t + 0.6), final)
    show_at(ob, t)
bpy.context.view_layer.update()
PERIOD_LOCAL = Vector((xs[4] - tot / 2, LOGO_Y + period.dimensions.y / 2, -DL))
PERIOD_D = period.dimensions.x
bpy.data.objects.remove(period, do_unlink=True)
title('k_studio', 'S T U D I O', camC, 0, -1.1, DL, 1.15, 16.75, None, fnt=FONT_SEMI, stagger=0.03, track=0.12, style='pop')
title('k_slogan', 'Websites & Videos aus Wien', camC, 0, -2.9, DL, 0.95, 17.0, None, fnt=FONT_SEMI, stagger=0.012,
      track=0.04, style='pop')
title('k_url', 'nemistudio.at', camC, 0, -4.8, DL, 1.25, 17.25, None, fnt=FONT_BLACK, mat='text_amber',
      stagger=0.02, track=0.04, style='pop')

# ------------------------------------------------------------------ tačka (ideja) i njen put
dot = None
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, segments=48, ring_count=24, location=(0, 0, 0))
dot = bpy.context.object
dot.name = 'tacka'
bpy.ops.object.shade_smooth()
dot.data.materials.append(MAT['dot'])
dl_d = bpy.data.lights.new('tacka_svetlo', 'POINT')
dl_d.color = srgb('#FF6F8A')
dl_d.energy = 350
dl_d.shadow_soft_size = 0.4
dl_d.use_shadow = False
dlight = link(bpy.data.objects.new('tacka_svetlo', dl_d))
dlight.parent = dot

# položaj tačke u logu (kamera C miruje od 16.4 s)
camC.location = FINAL_CAM[0]
tgtC.location = FINAL_CAM[1]
sc.frame_set(F(17.0))
bpy.context.view_layer.update()
LOGO_DOT = camC.matrix_world @ PERIOD_LOCAL
LOGO_DOT_SCALE = PERIOD_D / 1.0

R = 0.5
REST = Vector((-4.6, 3.5, 4.75 + R))
SIGN_HIT = REST.copy()
PHONE_HIT = PH + Matrix.Rotation(math.radians(-14), 3, 'Z') @ Vector((0, -1.15, 2.6))
P0 = Vector((0, -3, R))
# (vreme, pozicija, vrsta): 'hit' = udar (squash), 'top' = vrh luka, 'hold' = mirovanje
WAY = [
    (0.0, P0 + Vector((0, 0, 13)), 'top'),
    (0.5, P0, 'hit'), (0.75, P0 + Vector((0, 0, 3.0)), 'top'),
    (1.0, P0, 'hit'), (1.2, P0 + Vector((0, 0, 1.4)), 'top'),
    (1.4, P0, 'hit'), (1.55, P0 + Vector((0, 0, 0.5)), 'top'),
    (1.7, P0, 'hit'), (1.8, P0 + Vector((0, 0, 0.15)), 'top'),
    (1.9, P0, 'hit'), (2.75, P0, 'hold'),
    (3.1, P0 + Vector((0, 0, 7.0)), 'top'),
    (3.5, P0, 'hit'),
    (3.75, Vector((0, 0.5, 5.5)), 'top'),
    (4.0, Vector((0, 3.4, 0.3 + R)), 'hit'),
    (4.25, Vector((-7, 3.4, 7.0)), 'top'),
    (4.5, Vector((-14, 3.4, 0.3 + R)), 'hit'),
    (4.75, Vector((0, 3.0, 10.0)), 'top'),
    (5.0, Vector((14, 3.4, 0.3 + R)), 'hit'),
    (5.25, Vector((7, 6.0, 30.0)), 'top'),
    (5.5, Vector((0, 8.5, 23.0 + R)), 'hit'),
    (5.75, Vector((0, 4.0, 16.0)), 'top'),
    (6.0, Vector((0, 1.5, 0.3 + R)), 'hit'),
    (6.25, Vector((-2.5, 2.5, 6.5)), 'top'),
    (6.5, REST, 'hit'), (6.75, REST + Vector((0, 0, 0.9)), 'top'),
    (7.0, REST, 'hit'), (7.25, REST + Vector((0, 0, 0.6)), 'top'),
    (7.5, REST, 'hit'), (7.75, REST + Vector((0, 0, 0.4)), 'top'),
    (8.0, REST, 'hit'),
    (8.25, PHONE_HIT + Vector((-1.5, 0, 5.0)), 'top'),
    (8.5, PHONE_HIT, 'hit'), (8.75, PHONE_HIT + Vector((0, 0, 0.7)), 'top'),
    (9.0, PHONE_HIT, 'hit'), (9.25, PHONE_HIT + Vector((0, 0, 0.5)), 'top'),
    (9.5, PHONE_HIT, 'hit'), (10.4, PHONE_HIT, 'hold'),
    (10.85, PHONE_HIT + Vector((0, -0.5, 4.5)), 'top'),
    (11.35, PHONE_HIT, 'hit'), (11.9, PHONE_HIT, 'hold'),
    (12.2, PHONE_HIT + Vector((-6, 4, 14)), 'top'),
    (12.45, SIGN_HIT + Vector((0, 0, 16)), 'top'),
    (12.8, SIGN_HIT, 'hit'), (13.05, SIGN_HIT + Vector((0, 0, 0.7)), 'top'),
    (13.3, SIGN_HIT, 'hit'), (13.55, SIGN_HIT + Vector((0, 0, 0.5)), 'top'),
    (13.8, SIGN_HIT, 'hit'), (14.05, SIGN_HIT + Vector((0, 0, 0.4)), 'top'),
    (14.3, SIGN_HIT, 'hit'), (14.55, SIGN_HIT + Vector((0, 0, 0.3)), 'top'),
    (14.8, SIGN_HIT, 'hit'), (15.2, SIGN_HIT, 'hold'),
    (15.9, (SIGN_HIT + LOGO_DOT) / 2 + Vector((0, 0, 9)), 'top'),
    (16.55, LOGO_DOT, 'hit'),
]
for t, pos, kind in WAY:
    fr = F(t)
    for i in (0, 1):
        KI(dot, 'location', i, fr, pos[i], 'LINEAR')
    if kind == 'hit':
        KI(dot, 'location', 2, fr, pos[2], 'QUAD', 'EASE_OUT')
    elif kind == 'top':
        KI(dot, 'location', 2, fr, pos[2], 'QUAD', 'EASE_IN')
    else:
        KI(dot, 'location', 2, fr, pos[2], 'BEZIER')
# poslednji udar ostaje na mestu
KI(dot, 'location', 0, F(END_S), LOGO_DOT[0], 'CONSTANT')
KI(dot, 'location', 1, F(END_S), LOGO_DOT[1], 'CONSTANT')
KI(dot, 'location', 2, F(END_S), LOGO_DOT[2], 'CONSTANT')

# squash & stretch, talasi na podu, tres kamere
HITS = [w for w in WAY if w[2] == 'hit']
K(dot, 'scale', 1, (1, 1, 1))
rings_made = 0
for t, pos, _ in HITS:
    fr = F(t)
    end = t == 16.55
    s = LOGO_DOT_SCALE if t >= 16.55 else 1.0
    if t > 15.0:
        K(dot, 'scale', F(15.95), (1, 1, 1))
    K(dot, 'scale', fr - 2, (0.86 * s, 0.86 * s, 1.25 * s))
    K(dot, 'scale', fr, (1.35 * s, 1.35 * s, 0.62 * s))
    K(dot, 'scale', fr + 3, (0.95 * s, 0.95 * s, 1.08 * s))
    K(dot, 'scale', fr + 6, (s, s, s))
    if t < 8.4 or 12.7 < t < 13.0:  # svetleći prsten na mestu udara
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.05, location=(pos[0], pos[1], pos[2] - R + 0.06))
        ring = bpy.context.object
        ring.name = f'talas_{rings_made}'
        rm = principled(f'talas_{rings_made}', srgb('#FF5C7A'), rough=0.5, emit=srgb('#FFB0C0'), strength=0.0)
        ring.data.materials.append(rm)
        big = 2.5 if t not in (0.5, 3.5) else 6.0
        K(ring, 'scale', 1, (0, 0, 0), 'CONSTANT')
        K(ring, 'scale', fr, (0.3, 0.3, 1), 'BACK')
        K(ring, 'scale', fr + 14, (big, big, 1))
        K(emis(rm), 'default_value', fr - 1, 0.0)
        K(emis(rm), 'default_value', fr, 8.0)
        K(emis(rm), 'default_value', fr + 14, 0.0)
        K(ring, 'scale', fr + 15, (big, big, 1), 'CONSTANT')
        K(ring, 'scale', fr + 16, (0, 0, 0))
        rings_made += 1
K(emis(MAT['dot']), 'default_value', 1, 7.0)
K(emis(MAT['dot']), 'default_value', F(16.5), 7.0)
K(emis(MAT['dot']), 'default_value', F(16.6), 30.0)
K(emis(MAT['dot']), 'default_value', F(17.1), 9.0)
for t, amp in [(0.5, 0.25), (3.5, 0.45), (4.0, 0.3), (4.5, 0.2), (5.0, 0.2), (5.5, 0.25), (6.0, 0.2)]:
    shake(shA, t, amp)
shake(shB, 8.5, 0.18)
shake(shB, 10.5, 0.12)
shake(shC, 12.8, 0.15)
shake(shC, 16.55, 0.35)

# prozori se pale u talasu od udara tačke na kafić (12.8 s)
for key, (gid, f) in GLASS_KEYS.items():
    x0 = [b_[0] + b_[1] / 2 for b_ in BUILDINGS if b_[7] == gid][0]
    t = 12.85 + abs(x0) * 0.022 + f * 0.09
    s = emis(MAT[key])
    K(s, 'default_value', 1, 0.0)
    K(s, 'default_value', F(t), 0.0, 'BACK')
    K(s, 'default_value', F(t + 0.25), 3.2 if (seed_of(key) % 3) else 1.4)

# ------------------------------------------------------------------ render
sc.render.fps = FPS
sc.frame_start = 1
sc.frame_end = F(END_S)
sc.render.engine = 'BLENDER_EEVEE_NEXT'
ee = sc.eevee
ee.use_shadows = True
ee.shadow_ray_count = 1
ee.shadow_step_count = 6
ee.use_raytracing = False
sc.view_settings.view_transform = 'AgX'
try:
    sc.view_settings.look = 'AgX - Punchy'
except TypeError:
    pass
sc.render.use_motion_blur = True
sc.render.motion_blur_shutter = 0.45
sc.render.motion_blur_position = 'START'  # zamućenje ne prelazi preko rezova kamere
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGB'

sc.use_nodes = True
ct = sc.node_tree
ct.nodes.clear()
rl = ct.nodes.new('CompositorNodeRLayers')
gl = ct.nodes.new('CompositorNodeGlare')
gl.glare_type = 'BLOOM'
gl.quality = 'MEDIUM'
gl.inputs['Threshold'].default_value = 1.6
gl.inputs['Strength'].default_value = 0.55
gl.inputs['Size'].default_value = 0.75
comp = ct.nodes.new('CompositorNodeComposite')
ct.links.new(rl.outputs['Image'], gl.inputs['Image'])
ct.links.new(gl.outputs['Image'], comp.inputs['Image'])

if MODE == 'final':
    res = ARGS[5] if len(ARGS) > 5 else '1920x1080'
    sc.render.resolution_x, sc.render.resolution_y = (int(v) for v in res.split('x'))
    sc.render.resolution_percentage = 100
    ee.taa_render_samples = int(ARGS[2]) if len(ARGS) > 2 else 12
    sc.render.filepath = OUT.rstrip('/') + '/f'
    if len(ARGS) > 4:
        sc.frame_start, sc.frame_end = int(ARGS[3]), int(ARGS[4])
    bpy.ops.render.render(animation=True)
elif MODE == 'preview':
    sc.render.resolution_x, sc.render.resolution_y = 640, 360
    ee.taa_render_samples = 3
    sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = 'JPEG'
    sc.frame_step = int(ARGS[2]) if len(ARGS) > 2 else 1
    sc.render.filepath = OUT.rstrip('/') + '/p'
    bpy.ops.render.render(animation=True)
elif MODE == 'stills':
    pct = 50
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = pct
    ee.taa_render_samples = 6
    sc.render.use_motion_blur = False
    sc.render.image_settings.file_format = 'JPEG'
    for s in ARGS[2:]:
        sc.frame_set(F(float(s)))
        sc.render.filepath = OUT.rstrip('/') + f'/s_{float(s):05.2f}.jpg'
        bpy.ops.render.render(write_still=True)
elif MODE == 'save':
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
