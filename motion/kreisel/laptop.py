"""KREISEL, laptop na drvenom stolu: na ekranu je sajt (render/sajt/0001.png …), kamera se polako primiče
pa na kraju uleće u ekran. Bez logotipa i natpisa na laptopu.

Pokretanje:
  blender -b --factory-startup --python motion/kreisel/laptop.py -- [--od 1] [--do 255] [--procenat 100] [--kadrovi 1,120,255]
"""
import math
import os
import sys

import bpy
from mathutils import Vector

OVDE = os.path.dirname(os.path.abspath(__file__))
SAJT = os.path.join(OVDE, "render", "sajt")
IZLAZ = os.path.join(OVDE, "render", "laptop")
ARG = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(ime, podr):
    return ARG[ARG.index(ime) + 1] if ime in ARG else podr


UKUPNO = 255
FPS = 30
OD = int(arg("--od", 1))
DO = int(arg("--do", UKUPNO))
PROCENAT = int(arg("--procenat", 100))
KADROVI = [int(k) for k in arg("--kadrovi", "").split(",") if k]


def e(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def glatko(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lin(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return (c(rgb[0]), c(rgb[1]), c(rgb[2]), 1.0)


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 20
sc.cycles.adaptive_threshold = 0.04
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.cycles.glossy_bounces = 3
sc.cycles.diffuse_bounces = 3
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.render.use_persistent_data = True
sc.render.resolution_x = 1080
sc.render.resolution_y = 1920
sc.render.resolution_percentage = PROCENAT
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, UKUPNO
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"

svet = bpy.data.worlds.new("Svet")
sc.world = svet
svet.node_tree.nodes["Background"].inputs[0].default_value = lin((150, 140, 128))
svet.node_tree.nodes["Background"].inputs[1].default_value = 0.35


# ---------------------------------------------------------------- pomoćne
def kutija(ime, dim, poz, mat, zaobli=0.0, segmenti=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=poz)
    o = bpy.context.active_object
    o.name = ime
    o.scale = dim
    bpy.ops.object.transform_apply(scale=True)
    if zaobli:
        b = o.modifiers.new("zaobli", "BEVEL")
        b.width = zaobli
        b.segments = segmenti
        b.limit_method = "ANGLE"
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def principled(ime, boja, hrap=0.5, metal=0.0, spec=0.5):
    m = bpy.data.materials.new(ime)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = boja
    p.inputs["Roughness"].default_value = hrap
    p.inputs["Metallic"].default_value = metal
    p.inputs["Specular IOR Level"].default_value = spec
    return m


# ---------------------------------------------------------------- materijali
def drvo():
    m = bpy.data.materials.new("orah")
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tk = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.25, 1.0, 1.0)
    talas = nt.nodes.new("ShaderNodeTexWave")
    talas.wave_type = "BANDS"
    talas.bands_direction = "Y"
    talas.inputs["Scale"].default_value = 26.0
    talas.inputs["Distortion"].default_value = 3.5
    talas.inputs["Detail"].default_value = 4.0
    talas.inputs["Detail Scale"].default_value = 1.2
    sum_ = nt.nodes.new("ShaderNodeTexNoise")
    sum_.inputs["Scale"].default_value = 60.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = lin((38, 22, 14))
    ramp.color_ramp.elements[1].color = lin((70, 42, 26))
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.25
    nt.links.new(tk.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], talas.inputs["Vector"])
    nt.links.new(talas.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["A"])
    nt.links.new(sum_.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.42
    p.inputs["Coat Weight"].default_value = 0.25
    p.inputs["Coat Roughness"].default_value = 0.25
    return m


def zid():
    m = bpy.data.materials.new("zid")
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = lin((150, 144, 136))
    p.inputs["Roughness"].default_value = 0.9
    sum_ = nt.nodes.new("ShaderNodeTexNoise")
    sum_.inputs["Scale"].default_value = 25.0
    sum_.inputs["Detail"].default_value = 8.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    nt.links.new(sum_.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    return m


ORAH = drvo()
ZID = zid()
ALU = principled("aluminijum", lin((62, 62, 66)), 0.32, 1.0)
CRNO = principled("crno", lin((10, 10, 11)), 0.45)
TASTER = principled("taster", lin((14, 14, 15)), 0.55)
PAD = principled("trackpad", lin((52, 52, 56)), 0.38, 0.6)
BELO = principled("mis", lin((236, 234, 230)), 0.3)

# ekran: sekvenca slika sajta kao emisija, preko toga tanak sjaj stakla
EKRAN = bpy.data.materials.new("ekran")
_nt = EKRAN.node_tree
_p = _nt.nodes["Principled BSDF"]
_p.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
_p.inputs["Roughness"].default_value = 0.08
_p.inputs["Emission Strength"].default_value = 1.0
_slika = _nt.nodes.new("ShaderNodeTexImage")
_prva = os.path.join(SAJT, "0001.png")
if os.path.exists(_prva):
    img = bpy.data.images.load(_prva)
    img.source = "SEQUENCE"
    _slika.image = img
    _slika.image_user.frame_duration = UKUPNO
    _slika.image_user.frame_start = 1
    _slika.image_user.frame_offset = 0
    _slika.image_user.use_auto_refresh = True
_nt.links.new(_slika.outputs["Color"], _p.inputs["Emission Color"])

# ---------------------------------------------------------------- sto i zid
kutija("sto", (2.4, 0.72, 0.035), (0.05, 0.15, -0.0175), ORAH, 0.004)
kutija("sto_front", (2.4, 0.03, 0.16), (0.05, -0.205, -0.115), ORAH, 0.003)
kutija("fioka_linija", (2.4, 0.004, 0.004), (0.05, -0.221, -0.075), CRNO)
kutija("zid", (3.0, 0.02, 2.0), (0.0, 0.52, 0.8), ZID)

# sunce kroz prozor: ploča sa otvorom baca kosu traku svetla na zid
sunce = bpy.data.lights.new("Sunce", "SUN")
sunce.energy = 4.5
sunce.angle = math.radians(6)
sunce.color = (1.0, 0.86, 0.68)
so = bpy.data.objects.new("Sunce", sunce)
so.rotation_euler = (math.radians(52), math.radians(-38), math.radians(-35))
sc.collection.objects.link(so)


def ploca_sa_otvorom(ime, sirina, visina, otvor_w, otvor_h):
    W, H, w, h = sirina / 2, visina / 2, otvor_w / 2, otvor_h / 2
    v = [(-W, -H, 0), (W, -H, 0), (W, H, 0), (-W, H, 0), (-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)]
    f = [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(ime)
    me.from_pydata(v, [], f)
    o = bpy.data.objects.new(ime, me)
    o.visible_camera = False
    o.visible_glossy = False
    sc.collection.objects.link(o)
    return o


prozor = ploca_sa_otvorom("prozor", 6, 6, 0.45, 2.2)
prozor.location = (-1.1, -0.2, 1.4)
prozor.rotation_euler = (math.radians(52), math.radians(-38), math.radians(-35))

traka = bpy.data.lights.new("TrakaNaZidu", "SPOT")
traka.energy = 140
traka.spot_size = math.radians(40)
traka.spot_blend = 0.85
traka.color = (1.0, 0.88, 0.72)
traka.shadow_soft_size = 0.05
to = bpy.data.objects.new("TrakaNaZidu", traka)
to.location = (0.35, -0.25, 1.05)
to.scale = (0.22, 1.0, 1.0)
sc.collection.objects.link(to)
_ct = bpy.data.objects.new("TrakaCilj", None)
_ct.location = (-0.05, 0.51, 0.62)
sc.collection.objects.link(_ct)
_c = to.constraints.new("TRACK_TO")
_c.target = _ct
_c.track_axis = "TRACK_NEGATIVE_Z"
_c.up_axis = "UP_Y"
to.rotation_mode = "XYZ"

meko = bpy.data.lights.new("Meko", "AREA")
meko.energy = 60
meko.size = 1.5
meko.color = (1.0, 0.9, 0.78)
mo = bpy.data.objects.new("Meko", meko)
mo.location = (-0.6, -0.9, 0.9)
mo.rotation_euler = (math.radians(55), 0, math.radians(-30))
mo.visible_camera = False
sc.collection.objects.link(mo)

# ---------------------------------------------------------------- laptop (bez logotipa)
SIR, DUB, DEB = 0.304, 0.215, 0.011
osnova = kutija("osnova", (SIR, DUB, DEB), (0, 0, DEB / 2), ALU, 0.004, 4)
kutija("tastatura_udubljenje", (0.272, 0.112, 0.0012), (0, 0.035, DEB - 0.0004), CRNO)
redovi = [14, 14, 14, 13, 12, 10]
for r, n in enumerate(redovi):
    w = 0.0165
    razmak = 0.0193
    y = 0.08 - r * 0.0186
    x0 = -razmak * (n - 1) / 2
    for k in range(n):
        sir = w * (5.2 if (r == 5 and k == n // 2) else 1)
        if r == 5 and k > n // 2 and k < n // 2 + 3:
            continue
        kutija(f"taster_{r}_{k}", (sir, 0.0155, 0.0018), (x0 + k * razmak if not (r == 5 and k == n // 2) else 0, y, DEB + 0.0004), TASTER, 0.0015, 2)
kutija("trackpad", (0.13, 0.08, 0.0008), (0, -0.058, DEB + 0.0001), PAD, 0.003, 3)

# poklopac: otvoren 112° od osnove, šarka na zadnjoj ivici
SARKA = Vector((0, DUB / 2 - 0.004, DEB))
NAGIB = math.radians(112 - 90)
pivot = bpy.data.objects.new("sarka", None)
pivot.location = SARKA
pivot.rotation_euler = (-NAGIB, 0, 0)
sc.collection.objects.link(pivot)
VIS = 0.205
pok = kutija("poklopac", (SIR, 0.006, VIS), (0, 0, 0), ALU, 0.004, 4)
pok.parent = pivot
pok.location = (0, 0.003, VIS / 2 + 0.002)
okvir = kutija("okvir", (SIR - 0.004, 0.001, VIS - 0.004), (0, 0, 0), CRNO, 0.006, 4)
okvir.parent = pivot
okvir.location = (0, -0.0005, VIS / 2 + 0.002)
EW, EH = 0.284, 0.284 * 900 / 1440
bpy.ops.mesh.primitive_plane_add(size=1)
ekran = bpy.context.active_object
ekran.name = "ekran"
ekran.scale = (EW, EH, 1)
ekran.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(scale=True, rotation=True)
ekran.data.materials.append(EKRAN)
ekran.parent = pivot
ekran.location = (0, -0.0012, VIS / 2 + 0.006)
bpy.context.view_layer.update()
CENTAR_EKRANA = ekran.matrix_world.translation.copy()

# miš desno
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1, location=(0.3, -0.04, 0.012))
mis = bpy.context.active_object
mis.name = "mis"
mis.scale = (0.03, 0.055, 0.014)
mis.rotation_euler = (0, 0, math.radians(-12))
bpy.ops.object.shade_smooth()
mis.data.materials.append(BELO)

# ---------------------------------------------------------------- kamera
kam = bpy.data.objects.new("Kamera", bpy.data.cameras.new("Kamera"))
kam.data.lens = 50
kam.data.dof.use_dof = True
kam.data.dof.aperture_fstop = 4.0
sc.collection.objects.link(kam)
sc.camera = kam
cilj = bpy.data.objects.new("cilj", None)
sc.collection.objects.link(cilj)
kam.data.dof.focus_object = cilj
tr = kam.constraints.new("TRACK_TO")
tr.target = cilj
tr.track_axis = "TRACK_NEGATIVE_Z"
tr.up_axis = "UP_Y"


# ključni položaji kamere: (vreme, azimut°, visina iznad centra ekrana, daljina, pomak cilja x, pomak cilja z)
KLJUCEVI = [
    (0.0, -23.0, 0.13, 1.0, 0.055, -0.07),
    (6.35, -17.0, 0.11, 0.9, 0.045, -0.065),
    (8.47, -9.0, 0.04, 0.6, 0.03, -0.055),
]


def kamera_u(t):
    """Polako približavanje i okret do 6,35 s, pa ulet u ekran do kraja."""
    (t0, *a0), (t1, *a1), (t2, *a2) = KLJUCEVI
    if t <= t1:
        w = glatko(t / t1)
        v = [x + (y - x) * w for x, y in zip(a0, a1)]
    else:
        w = e((t - t1) / (t2 - t1))
        v = [x + (y - x) * w for x, y in zip(a1, a2)]
    azimut, visina, daljina, dx, dz = v
    c = CENTAR_EKRANA
    az = math.radians(azimut)
    smer = Vector((math.sin(az), -math.cos(az), 0))
    poz = c + smer * daljina + Vector((0, 0, visina))
    desno = Vector((math.cos(az), math.sin(az), 0))
    cil = c + desno * dx + Vector((0, 0, dz))
    return poz, cil


# ---------------------------------------------------------------- render
os.makedirs(IZLAZ, exist_ok=True)
lista = KADROVI or list(range(OD, DO + 1))
for f in lista:
    sc.frame_set(f)
    t = (f - 1) / FPS
    poz, cil = kamera_u(t)
    kam.location = poz
    cilj.location = cil
    sc.render.filepath = os.path.join(IZLAZ, f"{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"KADAR {f} t={t:.2f}", flush=True)
