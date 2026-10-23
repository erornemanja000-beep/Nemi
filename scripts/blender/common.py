"""Zajedničke funkcije za Blender scene (pokreće se preko blender -b -P, vidi .claude/agents/blender-umetnik.md).

Iz skripte scene:
    import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    import common as C

Dva sloja:
- prvi crteži (render_settings, world, studio_lights, mat_*): world() i studio_lights() su ZASTARELI
  (ravna svetla okolina, tri velika area svetla; dijagnoza u studio/kafa-skrol/dijagnoza-3d.md), ali ih
  grind.py i pour.py još koriste, pa ostaju dok te scene ne pređu na foto-studio;
- foto-studio (od 23.10.2026, iz sip.py): photo_render_settings, photo_studio_lights, area_light, flag,
  world_hdri, mat_surface, čvorovi (Nodes, new_material, srgb) i pečenje proceduralnih mapa u teksture
  (lathe(..., uv=...), bake_maps, load_maps, source_key).
"""
import hashlib
import inspect
import math
import pathlib
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

ASSETS = pathlib.Path(__file__).resolve().parent / 'assets'


def args():
    """Argumenti posle `--` u komandnoj liniji Blendera, kao lista."""
    return sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def reset():
    """Prazna scena bez podrazumevane kocke, svetla i kamere."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    return bpy.context.scene


def render_settings(scene, width=1600, height=1600, samples=64, transparent=True, fps=30):
    """Cycles na CPU-u sa OpenImageDenoise; PNG RGBA sa providnom pozadinom za web sekvence."""
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.max_bounces = 8
    scene.cycles.transparent_max_bounces = 16
    scene.cycles.transmission_bounces = 8
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.render.film_transparent = transparent
    # staklo propušta alfa kanal: kroz levak, bokal i V60 vidi se boja sajta, a ne crna
    scene.cycles.film_transparent_glass = transparent
    scene.cycles.film_transparent_roughness = 0.1
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA' if transparent else 'RGB'
    scene.render.image_settings.compression = 15
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'


def world(scene, color=(0.92, 0.89, 0.84), strength=0.6):
    """ZASTARELO (koriste ga još grind.py i pour.py): mekana topla okolina u boji sajta. Ravna svetla okolina
    skida tamne tonove i odsjaje; nove scene koriste world_hdri() + photo_studio_lights()."""
    w = bpy.data.worlds.new('World')
    scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = strength
    return w


def studio_lights(key=900, fill=250, rim=600):
    """ZASTARELO (koriste ga još grind.py i pour.py): tri ogromna area svetla (prozor levo gore, popuna desno,
    kontra iza). Daju ravno, „CG" svetlo; nove scene koriste photo_studio_lights()."""
    def area(name, loc, rot, size, power, color=(1.0, 0.96, 0.9)):
        d = bpy.data.lights.new(name, 'AREA')
        d.energy, d.size, d.color = power, size, color
        o = bpy.data.objects.new(name, d)
        o.location, o.rotation_euler = loc, [math.radians(a) for a in rot]
        bpy.context.collection.objects.link(o)
        return o
    return [
        area('Key', (-2.2, -2.0, 2.6), (55, 0, -45), 2.5, key),
        area('Fill', (2.4, -1.6, 1.2), (70, 0, 55), 3.0, fill, (0.95, 0.97, 1.0)),
        area('Rim', (0.6, 2.4, 2.2), (-60, 0, 170), 1.5, rim),
    ]


def camera(loc, target, lens=85, name='Camera'):
    """Kamera sa dugim objektivom (malo izobličenje, kao product shot) okrenuta ka tački target."""
    d = bpy.data.cameras.new(name)
    d.lens = lens
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o
    return o


def shadow_catcher(size=6, z=0.0):
    """Ravan koja hvata samo senku, da predmet „stoji" na pozadini sajta."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    p = bpy.context.active_object
    p.name = 'ShadowCatcher'
    p.is_shadow_catcher = True
    return p


def _principled(name, **inputs):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    for key, value in inputs.items():
        bsdf.inputs[key].default_value = value
    return m, bsdf


def mat_steel(name='Steel', roughness=0.22):
    """Brušeni inox (mlin, kuvalo)."""
    m, _ = _principled(name, **{'Base Color': (0.78, 0.77, 0.75, 1), 'Metallic': 1.0, 'Roughness': roughness,
                                'Anisotropic': 0.6})
    return m


def mat_glass(name='Glass', tint=(0.98, 0.98, 0.97), roughness=0.02):
    """Bistro staklo (levak mlina, bokal, V60)."""
    m, _ = _principled(name, **{'Base Color': (*tint, 1), 'Roughness': roughness, 'IOR': 1.47,
                                'Transmission Weight': 1.0})
    return m


def mat_plastic(name='Plastic', color=(0.03, 0.03, 0.03), roughness=0.35):
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': roughness})
    return m


def mat_paper(name='Paper', color=(0.93, 0.91, 0.86)):
    """Papirni filter: mat, malo propušta svetlo."""
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.85,
                                'Subsurface Weight': 0.25, 'Subsurface Radius': (0.2, 0.2, 0.2)})
    return m


def mat_coffee_liquid(name='Coffee', color=(0.08, 0.035, 0.015)):
    """Tečna kafa: tamna, providna na ivicama, sjajna površina."""
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.05, 'IOR': 1.34,
                                'Transmission Weight': 0.85})
    return m


def mat_water(name='Water'):
    m, _ = _principled(name, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.333,
                                'Transmission Weight': 1.0})
    return m


def mat_bean(name='Bean', color=(0.13, 0.065, 0.03)):
    """Prženo zrno: tamnobraon, blag sjaj od ulja, sitna neravnina."""
    m, bsdf = _principled(name, **{'Base Color': (*color, 1), 'Roughness': 0.38,
                                   'Coat Weight': 0.25, 'Coat Roughness': 0.3})
    nt = m.node_tree
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 60
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def mat_ceramic(name='Ceramic', color=(0.32, 0.22, 0.16), roughness=0.45):
    m, _ = _principled(name, **{'Base Color': (*color, 1), 'Roughness': roughness, 'Coat Weight': 0.5,
                                'Coat Roughness': 0.15})
    return m


def assign(obj, material):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    return obj


def smooth(obj, subdiv=0):
    """Glatko senčenje i po želji subdivision modifier."""
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if subdiv:
        mod = obj.modifiers.new('Subsurf', 'SUBSURF')
        mod.levels = mod.render_levels = subdiv
    return obj


def lathe(name, profile, segments=96, uv=None):
    """Telo okretanja: profile je lista (r, z) tačaka od dna nagore; vraća mesh objekat oko Z ose.

    uv: lista v koordinata (po jedna za svaku tačku profila) -> UV mapa „UVMap": u = ugao / 360° (0..1, šav
    na +X), v = zadato. Za pečenje mapa (bake_maps); v se bira tako da skriveni delovi dobiju malo piksela."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    uv_layer = bm.loops.layers.uv.new('UVMap') if uv is not None else None
    for i in range(segments):
        a, b = rings[i], rings[(i + 1) % segments]
        for j in range(len(profile) - 1):
            f = bm.faces.new((a[j], b[j], b[j + 1], a[j + 1]))
            if uv_layer is not None:
                u0, u1 = i / segments, (i + 1) / segments
                for loop, co in zip(f.loops, ((u0, uv[j]), (u1, uv[j]), (u1, uv[j + 1]), (u0, uv[j + 1]))):
                    loop[uv_layer].uv = co
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return smooth(obj)


def render_frames(scene, out_dir, frames):
    """Renderuje samo zadate kadrove (npr. [1, 45, 90] za probu) u out_dir/kadar_0001.png."""
    for f in frames:
        scene.frame_set(f)
        scene.render.filepath = f'{out_dir}/kadar_{f:04d}.png'
        bpy.ops.render.render(write_still=True)


# ================================================================ foto-studio (iz sip.py, 23.10.2026)
# Zajednički raspored svetla i kamere za sve scene (studio/kafa-skrol/fotorealizam.md, „Pravila izrade").
# Uglovi: azimut od +X (-90 = ka kameri na -Y, + = ka nazad), visina iznad horizonta, u stepenima.

def srgb(hex_color):
    """'#RRGGBB' (boja iz tokens.css) -> linearni RGB (Blender radi u linearnom prostoru)."""
    c = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


class Nodes:
    """Kratak zapis za čvorove (shader, world, compositor): ulazi mogu biti broj, torka ili izlaz drugog čvora.

        N = Nodes(material.node_tree)
        h = N.mul(N.noise(P, 40.0), 0.0002)      # P = izlaz Texture Coordinate
    """

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

    def rgb(self, r, g, b):
        """Tri broja ili izlaza -> boja (npr. za pakovanje tri mape u jednu teksturu)."""
        n = self.new('ShaderNodeCombineColor')
        for i, v in enumerate((r, g, b)):
            self.put(v, n.inputs[i])
        return n.outputs[0]

    def split(self, color):
        n = self.new('ShaderNodeSeparateColor')
        self.put(color, n.inputs[0])
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

    def tint(self, color, factors):
        """Boja pomnožena po kanalima (npr. (0.92, 1, 1) = crvena -8 %)."""
        return self.vmath('MULTIPLY', color, tuple(factors))

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

    def image(self, img, uv_map='UVMap', interpolation='Linear'):
        """Tekstura po UV mapi (npr. ispečena mapa iz load_maps); vraća (boja, alfa)."""
        n = self.new('ShaderNodeTexImage', interpolation=interpolation, extension='REPEAT')
        n.image = img
        uv = self.new('ShaderNodeUVMap', uv_map=uv_map)
        self.put(uv.outputs['UV'], n.inputs['Vector'])
        return n.outputs['Color'], n.outputs['Alpha']


def new_material(name):
    """Prazan Principled materijal; vraća (materijal, node_tree, Principled BSDF, Nodes)."""
    m = bpy.data.materials.new(name)
    if m.node_tree is None:  # u 5.x materijal uvek ima čvorove (use_nodes je zastareo)
        m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes['Principled BSDF'], Nodes(nt)


def direction(az_deg, el_deg):
    """Jedinični vektor za azimut (od +X) i visinu iznad horizonta, u stepenima."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    return Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


def ray_visibility(ob, camera=True, diffuse=True, glossy=True, transmission=True, scatter=True, shadow=True):
    """Za koje zrake je objekat (ili svetlo) vidljiv; npr. svetlo samo u odsjaju: diffuse=False."""
    ob.visible_camera, ob.visible_diffuse, ob.visible_glossy = camera, diffuse, glossy
    ob.visible_transmission, ob.visible_volume_scatter = transmission, scatter
    if hasattr(ob, 'visible_shadow'):
        ob.visible_shadow = shadow


def photo_render_settings(scene, width=1200, height=1200, samples=64, transparent=True, adaptive=0.02, fps=30,
                          exposure=0.0):
    """Foto render (dijagnoza, tačke 1 i 3): render_settings + AgX Medium High Contrast, ekspozicija 0,
    blur_glossy 0,2, clamp indirect 15, OIDN sa albedo+normal, bez kaustika, Persistent Data (BVH i
    teksture ostaju u memoriji između kadrova iste sekvence)."""
    render_settings(scene, width=width, height=height, samples=samples, transparent=transparent, fps=fps)
    cy = scene.cycles
    cy.adaptive_threshold = adaptive
    cy.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    cy.denoising_prefilter = 'ACCURATE'
    cy.denoising_quality = 'HIGH'
    cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 8, 4, 4
    cy.caustics_reflective = cy.caustics_refractive = False
    cy.blur_glossy = 0.2
    cy.sample_clamp_indirect = 15.0
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = exposure
    scene.render.use_persistent_data = True


def area_light(name, loc, aim, size, power, kelvin, shape='RECTANGLE', spread=180.0):
    """Area svetlo (softboks) na loc, okrenuto ka tački aim; size (širina, visina) u m, boja u kelvinima.
    spread < 180° = saće (grid): svetlo ne curi na sto. Kameri nevidljivo."""
    d = bpy.data.lights.new(name, 'AREA')
    d.shape, d.size, d.size_y = shape, size[0], size[1]
    d.energy = power
    d.spread = math.radians(spread)
    d.use_temperature, d.temperature = True, kelvin
    ob = link(bpy.data.objects.new(name, d))
    ob.location = loc
    ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    ob.visible_camera = False
    return ob


def flag(name, loc, aim, size, diffuse=True):
    """Crna zastava (molton) okrenuta ka aim: upija svetlo, a u sjajnoj površini daje tamnu traku = kontrast
    odsjaja. Kameri i senci nevidljiva; diffuse=False kad nema zida (bez sive koprene na shadow catcher-u)."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (size[0], size[1], 1.0)
    ob.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    ray_visibility(ob, camera=False, shadow=False, diffuse=diffuse)
    m, _, b, _ = new_material(name)
    b.inputs['Base Color'].default_value = (0.004, 0.004, 0.004, 1)
    b.inputs['Roughness'].default_value = 1.0
    b.inputs['Specular IOR Level'].default_value = 0.0
    assign(ob, m)
    return ob


# raspored foto-studija (podrazumevano, iz SIP dokaza); svaka vrednost se menja kao ključna reč u
# photo_studio_lights(..., key_az=-150) itd.
STUDIO = dict(
    key_az=-140.0, key_el=20.0, key_dist=1.30,   # key prozor levo-gore-napred, nisko: odsjaj pada na obode
    key_size=(0.60, 0.90), key_kelvin=5800,
    strip_az=(158.0, 22.0), strip_el=18.0, strip_dist=0.40, strip_lift=0.10,   # uske trake pozadi
    strip_size=(0.12, 1.0),
    flag_az=-30.0, flag_el=12.0, flag_dist=0.42, flag_size=(0.45, 0.70),       # crna zastava desno napred
    frame_tilt=30.0, frame_bar=0.06, frame_grid=(3, 4),                       # prozorski okvir (samo uz zid)
    sun_spot=(0.0, 0.10),                        # (x, z) na zidu kroz koju sunce gađa sredinu prozora
    # niska blenda: svetla traka levo-napred, tik iznad stola, vidljiva SAMO u odsjaju (ne osvetljava
    # difuzno). Kamera nisko (13-16°) na strmom boku vidi sto, ne prozor; ova traka daje odsjaj prozora.
    refl_az=-128.0, refl_dist=0.24, refl_z=(0.004, 0.044), refl_w=0.12, refl_kelvin=5800,
)


def photo_studio_lights(target, subjects, wall=None, key=70.0, strip=10.0, sun=5.0, bg=6.0, reflector=0.0,
                        flags=True, **layout):
    """Foto-studio (dijagnoza, tačka 1): jedan key prozor levo-gore-napred iza prozorskog okvira, dve uske
    trake pozadi, crna zastava desno, po želji niska blenda; uz zid i toplo sunce kroz isti okvir koje pada
    samo na zid. Vraća listu svetala.

    target: tačka na predmetu (m); subjects: objekti predmeta (trake i blenda svetle samo njih);
    wall: objekat zida ili None (providna pozadina); key/strip/bg u W, sun u W/m², reflector = snaga
    blende u W (0 = bez); layout: izmene rasporeda iz STUDIO.

    Fill skoro ne postoji (samo tamni HDRI iz world_hdri, 0,1-0,15), pa je odnos key:fill oko 5-8:1.
    Zid ne dobija key (light linking = „cutter"), nego svoje meko svetlo sleva + sunce kroz okvir.
    Bez zida nema ni okvira: prečke bi delimično zaklonile key po stolu, pa bi shadow catcher dao sivu
    koprenu preko celog kadra."""
    L = dict(STUDIO, **layout)
    only_subj = bpy.data.collections.new('OnlySubjects')
    for ob in subjects:
        only_subj.objects.link(ob)
    tgt = Vector(target)
    kdir = direction(L['key_az'], L['key_el'])
    key_pos = tgt + L['key_dist'] * kdir
    a = Vector((kdir.x, kdir.y, 0.0)).normalized()    # horizontalno, od predmeta ka prozoru
    t = Vector((a.y, -a.x, 0.0))                      # horizontala u ravni prozora (t x a = +Z)
    win = key_pos - 0.06 * a                          # ravan okvira 6 cm ispred key svetla
    ksize = L['key_size']

    if wall is not None:
        # okvir: zid oko otvora + okna sa prečkama; baca senku i vidi se u odsjaju, kameri nevidljiv
        W, H, bar, margin = ksize[0] + 0.04, ksize[1] + 0.04, L['frame_bar'], 0.55
        cols, rows = L['frame_grid']
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
                                     (0.0, 0.0, 1.0, win.z), (0.0, 0.0, 0.0, 1.0))) @ \
            Matrix.Rotation(math.radians(L['frame_tilt']), 4, 'Y')   # nagnut okvir: kose trake senke
        ray_visibility(frame, camera=False, diffuse=False, transmission=False, scatter=False)
        fm, _, fb, _ = new_material('WindowFrame')
        fb.inputs['Base Color'].default_value = (0.02, 0.018, 0.016, 1)
        fb.inputs['Roughness'].default_value = 0.9
        assign(frame, fm)

    # key: vertikalan prozor (kao pravi); toplinu daju sunce na zidu (4200 K) i boje scene
    kd = bpy.data.lights.new('Key', 'AREA')
    kd.shape, kd.size, kd.size_y = 'RECTANGLE', ksize[0], ksize[1]
    kd.energy = key
    kd.use_temperature, kd.temperature = True, L['key_kelvin']
    ko = link(bpy.data.objects.new('Key', kd))
    ko.location = key_pos
    ko.rotation_euler = (-a).to_track_quat('-Z', 'Z').to_euler()
    ko.visible_camera = False
    lights = [ko]

    # trake pozadi: tanke svetle linije duž leve i desne ivice predmeta
    for i, az in enumerate(L['strip_az']):
        pos = tgt + L['strip_dist'] * direction(az, L['strip_el']) + Vector((0.0, 0.0, L['strip_lift']))
        so = area_light(f'Strip{i}', pos, tgt + Vector((0.0, 0.0, 0.01)), L['strip_size'], strip, 6500,
                        spread=40.0)
        so.light_linking.receiver_collection = only_subj
        lights.append(so)
    if flags:
        fpos = tgt + L['flag_dist'] * direction(L['flag_az'], L['flag_el'])
        flag('FlagRight', fpos, tgt, L['flag_size'], diffuse=wall is not None)

    if reflector > 0:
        # niska blenda: odsjaj „prozora" na boku pri niskoj kameri; samo glossy, samo predmet
        d = direction(L['refl_az'], 0.0)
        z0, z1 = L['refl_z']
        pos = Vector((tgt.x, tgt.y, 0.0)) + L['refl_dist'] * d + Vector((0.0, 0.0, (z0 + z1) / 2))
        ro = area_light('Reflector', pos, Vector((tgt.x, tgt.y, pos.z)), (L['refl_w'], z1 - z0), reflector,
                        L['refl_kelvin'])
        ray_visibility(ro, camera=False, diffuse=False, glossy=True, transmission=False, scatter=False)
        ro.light_linking.receiver_collection = only_subj
        lights.append(ro)

    if wall is not None:
        bpy.context.view_layer.update()
        wall_y = wall.matrix_world.translation.y
        only_wall = bpy.data.collections.new('OnlyWall')
        only_wall.objects.link(wall)
        no_wall = bpy.data.collections.new('NoWall')
        no_wall.objects.link(wall)
        for co in no_wall.collection_objects:
            co.light_linking.link_state = 'EXCLUDE'
        ko.light_linking.receiver_collection = no_wall
        # pozadina: meko svetlo sleva koje pada udesno, samo na zid
        bgl = area_light('WallLight', tgt + Vector((-0.55, -0.15, 0.25)),
                         Vector((tgt.x + 0.10, wall_y, tgt.z + 0.025)), (0.5, 0.5), bg, 5200)
        bgl.light_linking.receiver_collection = only_wall
        lights.append(bgl)
        # sunce kroz isti okvir, samo na zid (light linking): kosa senka okvira kao u videu
        spot = L['sun_spot']
        s = (win - Vector((spot[0], wall_y, spot[1]))).normalized()
        sd = bpy.data.lights.new('Sun', 'SUN')
        sd.energy = sun
        sd.angle = math.radians(1.5)                  # malo mekša ivica senke nego pravo sunce (0,53°)
        sd.use_temperature, sd.temperature = True, 4200
        so = link(bpy.data.objects.new('Sun', sd))
        so.rotation_euler = (-s).to_track_quat('-Z', 'Y').to_euler()
        so.light_linking.receiver_collection = only_wall
        # predmet ne baca senku od ovog sunca (ono ga ne osvetljava), pa na zidu ostaje samo šara okvira
        not_subj = bpy.data.collections.new('NotSubjects')
        for ob in subjects:
            not_subj.objects.link(ob)
        for co in not_subj.collection_objects:
            co.light_linking.link_state = 'EXCLUDE'
        so.light_linking.blocker_collection = not_subj
        lights.append(so)
    return lights


# HDRI „Lebombo" (autor Greg Zaal, Poly Haven), 2k OpenEXR, CC0 1.0 (https://polyhaven.com/license),
# stranica https://polyhaven.com/a/lebombo, fajl https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/2k/lebombo_2k.exr,
# md5 15daa3dc91907106756355aa0d2a3517; preuzet 23.10.2026 pre pokretanja Blendera (manifest: assets/IZVORI.md).
HDRI_LEBOMBO = ASSETS / 'lebombo_2k.exr'
HDRI_LEBOMBO_WINDOW_AZ = -42.0     # azimut prozora u neokrenutom HDRI-ju (izmereno iz EXR-a)


def world_hdri(scene, strength=0.15, rot_deg=None, path=None, window_az=HDRI_LEBOMBO_WINDOW_AZ):
    """Tamna HDRI okolina (0,05-0,15) kao jedini fill; rot_deg=None okreće prozor HDRI-ja u pravac key
    svetla iz STUDIO (odsjaji okoline i key-a se slažu)."""
    w = bpy.data.worlds.new('World')
    scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    N = Nodes(nt)
    if rot_deg is None:
        rot_deg = window_az - STUDIO['key_az']
    env = N.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(str(path or HDRI_LEBOMBO), check_existing=True)
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0.0, 0.0, math.radians(rot_deg))
    N.put(tc.outputs['Generated'], mp.inputs['Vector'])
    N.put(mp.outputs['Vector'], env.inputs['Vector'])
    bg = nt.nodes['Background']
    N.put(env.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    return w


def mat_surface(name, hex_color, rough=(0.5, 0.7), spec=0.4, bump=0.00004, scale=1.0, gain=1.0, desat=0.3):
    """Mat farbana ploča (sto, zid): boja iz dizajna, blaga mrljavost, sitna tekstura gleta.

    gain, desat: albedo u odnosu na boju iz dizajna (toplo svetlo i AgX dodaju zasićenje),
    da render izađe blizu tokena."""
    m, nt, bsdf, N = new_material(name)
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    lin = srgb(hex_color)
    grey = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    base = tuple(gain * (c + (grey - c) * desat) for c in lin)
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


# ---------------------------------------------------------------- pečenje proceduralnih mapa u teksture
# Proceduralni shader sa stotinama čvorova se po kadru računa milionima puta (a bump ga računa 3x).
# Ispečen jednom u teksture (EXR half, po UV mapi) render je višestruko brži, a izgled isti.

def source_key(*parts):
    """Kratak otisak (sha1) izvornog koda funkcija i vrednosti: promena koda materijala = novo pečenje."""
    h = hashlib.sha1(bpy.app.version_string.encode())
    for p in parts:
        try:
            h.update(inspect.getsource(p).encode() if callable(p) else repr(p).encode())
        except (OSError, TypeError):
            h.update(repr(p).encode())
    return h.hexdigest()[:10]


def save_exr(image, path, scene=None):
    """Float slika -> OpenEXR half (ZIP), bez view transforma (linearne vrednosti, i negativne)."""
    scene = scene or bpy.context.scene
    s = scene.render.image_settings
    old = (s.file_format, s.color_depth, s.exr_codec, s.color_mode)
    s.file_format, s.color_depth, s.exr_codec, s.color_mode = 'OPEN_EXR', '16', 'ZIP', 'RGB'
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    image.save_render(str(path), scene=scene)
    s.file_format, s.color_depth, s.exr_codec, s.color_mode = old


def bake_maps(obj, material, channels, paths, width, height, samples=4, margin=16):
    """Ispeče izlaze čvorova materijala (EMIT bake po UV mapi objekta) i sačuva ih kao EXR half.

    channels: {ime: izlaz čvora (boja ili broj; tri broja se pakuju preko Nodes.rgb)}; paths: {ime: .exr}.
    Za vreme pečenja materijal svetli samo tim izlazom, a displacement je isključen (peče se po
    neispomeranoj površini; pomak je < 1 mm, pa se šare ne pomeraju vidljivo). Posle se sve vraća.
    samples > 1 = antialiasing unutar teksela. Vraća {ime: bpy.types.Image}."""
    scene = bpy.context.scene
    cy = scene.cycles
    old = (scene.render.engine, cy.samples, cy.use_adaptive_sampling, cy.use_denoising,
           material.displacement_method)
    scene.render.engine = 'CYCLES'
    cy.samples, cy.use_adaptive_sampling, cy.use_denoising = samples, False, False
    nt = material.node_tree
    out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial' and n.is_active_output)
    old_surf = [lk.from_socket for lk in out.inputs['Surface'].links]
    old_disp = [lk.from_socket for lk in out.inputs['Displacement'].links]
    for lk in list(out.inputs['Displacement'].links):
        nt.links.remove(lk)
    material.displacement_method = 'BUMP'
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    tex = nt.nodes.new('ShaderNodeTexImage')
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bake = scene.render.bake
    bake.target, bake.margin, bake.use_clear = 'IMAGE_TEXTURES', margin, True
    images = {}
    for name, sock in channels.items():
        img = bpy.data.images.new(f'bake_{name}', width, height, float_buffer=True, alpha=False)
        tex.image = img
        nt.nodes.active = tex
        nt.links.new(sock, em.inputs['Color'])
        bpy.ops.object.bake(type='EMIT', margin=margin, use_clear=True)
        save_exr(img, paths[name], scene)
        images[name] = img
    nt.nodes.remove(em)
    nt.nodes.remove(tex)
    for s in old_surf:
        nt.links.new(s, out.inputs['Surface'])
    for s in old_disp:
        nt.links.new(s, out.inputs['Displacement'])
    scene.render.engine, cy.samples, cy.use_adaptive_sampling, cy.use_denoising, material.displacement_method = old
    return images


def load_maps(paths, color=('albedo',)):
    """Učita ispečene EXR mape; imena iz color su boja (linearno), ostalo su podaci (Non-Color)."""
    imgs = {}
    for name, p in paths.items():
        img = bpy.data.images.load(str(p), check_existing=True)
        img.colorspace_settings.name = 'Linear Rec.709' if name in color else 'Non-Color'
        imgs[name] = img
    return imgs
