"""Blender scena za „Würfelwelt": ostrvo se gradi sloj po sloj, kamera se odmiče, pa pada noć.

Pokretanje (renderuje sve kadrove u motion/public/wuerfel/render/):
  blender -b --factory-startup --python motion/wuerfelwelt/blender_scena.py
Samo jedan kadar za proveru:            ... -- --kadar 120
Samo .blend fajl, bez rendera:          ... -- --samo-blend
"""
import math
import os
import sys

import bpy

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
import numpy as np  # noqa: E402

import voxel_welt as vw  # noqa: E402

ARG = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
KADAR = int(ARG[ARG.index("--kadar") + 1]) if "--kadar" in ARG else None
PROCENAT = int(ARG[ARG.index("--procenat") + 1]) if "--procenat" in ARG else 100
OD = int(ARG[ARG.index("--od") + 1]) if "--od" in ARG else 1  # nastavak prekinutog rendera
IZLAZ = os.path.join(OVDE, "..", "public", "wuerfel", "render")

KRAJ = 225  # poslednji Blender kadar
REZ_B = 101  # od ovog kadra druga kamera (rez pokriva pikselni prelaz u Remotion-u)
NOC_OD, NOC_DO = 150, 175
SVETLA_UPALJENA = 160


def lin(v):
    v = v / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def boja(rgb, a=1.0):
    return (lin(rgb[0]), lin(rgb[1]), lin(rgb[2]), a)


def glatko(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def mesaj(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- scena
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 16
sc.render.use_persistent_data = True
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 1080
sc.render.resolution_y = 1920
sc.render.resolution_percentage = PROCENAT
sc.render.fps = 30
sc.frame_start = 1
sc.frame_end = KRAJ
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
try:
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass

# ---------------------------------------------------------------- materijali
mats = []
for ime, rgb in vw.BOJE:
    m = bpy.data.materials.new(ime)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = boja(rgb)
    p.inputs["Roughness"].default_value = 0.85
    if ime == "prozor":
        p.inputs["Base Color"].default_value = boja((44, 50, 60))
        p.inputs["Roughness"].default_value = 0.25
    if ime in vw.SVETLE:
        p.inputs["Emission Color"].default_value = boja(rgb)
        jacina = p.inputs["Emission Strength"]
        # prozori trepnu pa se upale, lampa malo posle
        kljucevi = (
            [(SVETLA_UPALJENA - 1, 0), (SVETLA_UPALJENA + 1, 3), (SVETLA_UPALJENA + 2, 0.4), (SVETLA_UPALJENA + 5, 4)]
            if ime == "prozor"
            else [(SVETLA_UPALJENA + 7, 0), (SVETLA_UPALJENA + 9, 8)]
        )
        for k, v in kljucevi:
            jacina.default_value = v
            jacina.keyframe_insert("default_value", frame=k)
    mats.append(m)

# ---------------------------------------------------------------- kocke po slojevima
g = vw.napravi()
ima = g > 0
STRANE = {
    (1, 0, 0): ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
    (-1, 0, 0): ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)),
    (0, 1, 0): ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)),
    (0, -1, 0): ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
    (0, 0, 1): ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
    (0, 0, -1): ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)),
}


def vidljiva(x, y, z, n):
    if n[2] == 1:
        return True  # vrh sloja se vidi dok se gradi, pa ga uvek crtamo
    if n[2] == -1:
        return z == 0 or not ima[x, y, z - 1]
    nx, ny = x + n[0], y + n[1]
    if nx < 0 or ny < 0 or nx >= vw.W or ny >= vw.D:
        return True
    return not ima[nx, ny, z]


for s in vw.slojevi(g):
    z = s["z"]
    verts, faces, mat_idx = [], [], []
    for x, y in zip(*np.nonzero(g[:, :, z])):
        for n, uglovi in STRANE.items():
            if not vidljiva(x, y, z, n):
                continue
            i = len(verts)
            verts += [(x - vw.CX + a, y - vw.CY + b, c) for a, b, c in uglovi]
            faces.append((i, i + 1, i + 2, i + 3))
            mat_idx.append(int(g[x, y, z]) - 1)
    me = bpy.data.meshes.new(f"sloj_{z:02d}")
    me.from_pydata(verts, [], faces)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mat_idx)
    ob = bpy.data.objects.new(f"sloj_{z:02d}", me)
    sc.collection.objects.link(ob)

    # sloj pada odozgo i malo odskoči
    start, sleteo = s["start"], s["sleteo"]
    if start > 1:
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=start - 1)
        ob.hide_viewport = True
        ob.keyframe_insert("hide_viewport", frame=start - 1)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=start)
    ob.hide_viewport = False
    ob.keyframe_insert("hide_viewport", frame=start)
    visina = 10 if start == 1 else 14
    for k, dz in ((start, visina), (sleteo - 3, -0.3), (sleteo, 0.0)):
        ob.location.z = z + dz
        ob.keyframe_insert("location", index=2, frame=k)

# ---------------------------------------------------------------- svetla
def sunce(ime, rx, rz, rgb_boja, kljucevi):
    l = bpy.data.lights.new(ime, "SUN")
    l.angle = math.radians(4)
    o = bpy.data.objects.new(ime, l)
    o.rotation_euler = (math.radians(rx), 0, math.radians(rz))
    sc.collection.objects.link(o)
    for k, energija, c in kljucevi:
        l.energy = energija
        l.keyframe_insert("energy", frame=k)
        l.color = c if c else rgb_boja
        l.keyframe_insert("color", frame=k)
    return o


sunce("Sunce", 50, -30, (1.0, 0.93, 0.85), [(1, 4.0, None), (NOC_OD, 4.0, None), (NOC_OD + 12, 2.0, (1.0, 0.55, 0.3)), (NOC_DO, 0.0, (1.0, 0.45, 0.25))])
sunce("Mesec", 55, 150, (0.55, 0.65, 1.0), [(1, 0.0, None), (NOC_OD, 0.0, None), (NOC_DO, 0.35, None)])

lampa = bpy.data.lights.new("Lampa", "POINT")
lampa.color = (1.0, 0.78, 0.5)
lampa.shadow_soft_size = 0.3
lo = bpy.data.objects.new("Lampa", lampa)
lo.location = (13 - vw.CX + 0.5, 8 - vw.CY - 0.6, vw.VRH + 6.5)
sc.collection.objects.link(lo)
for k, e in ((SVETLA_UPALJENA + 7, 0.0), (SVETLA_UPALJENA + 9, 120.0)):
    lampa.energy = e
    lampa.keyframe_insert("energy", frame=k)

svet = bpy.data.worlds.new("Svet")
sc.world = svet
pozadina = svet.node_tree.nodes["Background"]
for k, c, jacina in ((1, (0.62, 0.66, 0.75), 0.6), (NOC_OD, (0.62, 0.66, 0.75), 0.6), (NOC_DO, (0.10, 0.12, 0.25), 0.25)):
    pozadina.inputs[0].default_value = (*c, 1)
    pozadina.inputs[0].keyframe_insert("default_value", frame=k)
    pozadina.inputs[1].default_value = jacina
    pozadina.inputs[1].keyframe_insert("default_value", frame=k)

# ---------------------------------------------------------------- kamere
def kamera(ime, lens):
    c = bpy.data.cameras.new(ime)
    c.lens = lens
    c.clip_end = 500
    o = bpy.data.objects.new(ime, c)
    sc.collection.objects.link(o)
    cilj = bpy.data.objects.new(ime + "_cilj", None)
    sc.collection.objects.link(cilj)
    t = o.constraints.new("TRACK_TO")
    t.target = cilj
    t.track_axis = "TRACK_NEGATIVE_Z"
    t.up_axis = "UP_Y"
    return o, cilj


def postavi(o, cilj, k, azimut, elevacija, daljina, meta):
    a, e = math.radians(azimut), math.radians(elevacija)
    cilj.location = meta
    cilj.keyframe_insert("location", frame=k)
    o.location = (
        meta[0] + daljina * math.cos(e) * math.cos(a),
        meta[1] + daljina * math.cos(e) * math.sin(a),
        meta[2] + daljina * math.sin(e),
    )
    o.keyframe_insert("location", frame=k)


# kamera A: blizu prve kocke, pa se odmiče dok se ostrvo gradi
kam_a, cilj_a = kamera("Kamera_A", 35)
for k in range(1, REZ_B):
    t = glatko((k - 18) / 80)
    postavi(
        kam_a, cilj_a, k,
        azimut=mesaj(-62, -38, glatko(k / REZ_B)),
        elevacija=mesaj(22, 27, t),
        daljina=mesaj(7, 54, t),
        meta=(0.5, 0.5, mesaj(0.6, 8.5, t)),
    )

# kamera B: niska, bliža, klizi ispred kafića, mutna prednja ivica
kam_b, cilj_b = kamera("Kamera_B", 50)
kam_b.data.dof.use_dof = True
kam_b.data.dof.focus_object = cilj_b
kam_b.data.dof.aperture_fstop = 3.5
for k in range(REZ_B, KRAJ + 1):
    t = glatko((k - REZ_B) / (KRAJ - REZ_B))
    postavi(
        kam_b, cilj_b, k,
        azimut=mesaj(-128, -62, t),
        elevacija=mesaj(12, 17, t),
        daljina=mesaj(44, 38, t),
        meta=(-5.0, -2.0, mesaj(12.5, 13.5, t)),
    )

sc.camera = kam_a
mark = sc.timeline_markers.new("B", frame=REZ_B)
mark.camera = kam_b
sc.timeline_markers.new("A", frame=1).camera = kam_a

# ---------------------------------------------------------------- izlaz
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OVDE, "diorama.blend"))
if "--samo-blend" in ARG:
    sys.exit(0)

os.makedirs(IZLAZ, exist_ok=True)
if KADAR is not None:
    sc.frame_set(KADAR)
    sc.camera = kam_b if KADAR >= REZ_B else kam_a
    sc.render.filepath = os.path.join(IZLAZ, f"proba_{KADAR:04d}.png")
    bpy.ops.render.render(write_still=True)
else:
    sc.frame_start = OD
    sc.render.filepath = os.path.join(IZLAZ, "")
    bpy.ops.render.render(animation=True)
