"""AUREL, 10 s za Reels i TikTok (1080 × 1920, 30 fps). Renderuje Blender delove:

  --mod paneli    8 fotografija sata za panele vrteške (render/paneli/)
  --mod karusel   kadrovi 1–90: POV vrteška oko kamere, staje i uleće u panel 1 (render/kadrovi/)
  --mod sat       kadrovi 91–300: makro brojčanika, match cut na boje, odmicanje do celog sata (render/kadrovi/)

Panel 1 je tačno prvi kadar moda „sat" (91), pa je rez u 3. sekundi neprimetan (match cut).
Pokretanje: blender -b --factory-startup --python motion/aurel/snimci.py -- --mod sat [--procenat 50] [--kadrovi 91,150]
"""
import math
import os
import sys

import bpy
from mathutils import Vector

OVDE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, OVDE)
import sat as S  # noqa: E402

ARG = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(ime, podr):
    return ARG[ARG.index(ime) + 1] if ime in ARG else podr


MOD = arg("--mod", "sat")
PROCENAT = int(arg("--procenat", 100))
KADROVI = [int(k) for k in arg("--kadrovi", "").split(",") if k]
KORAK = int(arg("--korak", 1))  # 2 = svaki drugi kadar (brzo), međukadrove pravi ffmpeg
UZORCI = int(arg("--uzorci", 0))
FPS = 30
RENDER = os.path.join(OVDE, "render")
HDRI = os.path.join(OVDE, "..", "assets", "polyhaven", "studio_small_09", "studio_small_09_2k.hdr")
REZ = 91  # prvi kadar makro snimka


def e(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def izlaz(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def mesaj(a, b, w):
    return a + (b - a) * w


# ---------------------------------------------------------------- scena
def osnovna_scena(uzoraka=32):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = UZORCI or uzoraka
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 10
    sc.cycles.glossy_bounces = 6
    sc.cycles.transmission_bounces = 6
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.resolution_x = 1080
    sc.render.resolution_y = 1920
    sc.render.resolution_percentage = PROCENAT
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    return sc


def studijsko_svetlo(sc, jacina=0.7):
    svet = bpy.data.worlds.new("Studio")
    sc.world = svet
    nt = svet.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    tk = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(tk.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    bg = nt.nodes["Background"]
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = jacina
    # kamera ne vidi HDRI: pozadina je tamna, a odsjaji su iz studija
    put = nt.nodes.new("ShaderNodeLightPath")
    tamno = nt.nodes.new("ShaderNodeBackground")
    tamno.inputs["Color"].default_value = (0.006, 0.006, 0.007, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(put.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(tamno.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes["World Output"].inputs["Surface"])
    return mp


def svetlo_traka(sc, ime, poz, cilj, energija, w=0.4, h=8.0, boja=(1, 0.97, 0.92)):
    l = bpy.data.lights.new(ime, "AREA")
    l.shape = "RECTANGLE"
    l.size, l.size_y = w, h
    l.energy = energija
    l.color = boja
    o = bpy.data.objects.new(ime, l)
    o.location = poz
    o.visible_camera = False
    sc.collection.objects.link(o)
    c = bpy.data.objects.new(ime + "_cilj", None)
    c.location = cilj
    sc.collection.objects.link(c)
    t = o.constraints.new("TRACK_TO")
    t.target = c
    t.track_axis = "TRACK_NEGATIVE_Z"
    t.up_axis = "UP_Y"
    return o


def kamera(sc, lens):
    k = bpy.data.objects.new("Kamera", bpy.data.cameras.new("Kamera"))
    k.data.lens = lens
    k.data.clip_start = 0.05
    k.data.clip_end = 400
    sc.collection.objects.link(k)
    sc.camera = k
    c = bpy.data.objects.new("Kamera_cilj", None)
    sc.collection.objects.link(c)
    t = k.constraints.new("TRACK_TO")
    t.target = c
    t.track_axis = "TRACK_NEGATIVE_Z"
    t.up_axis = "UP_Y"
    return k, c


def pod(sc):
    """Tamna ploča ispod sata (blag odsjaj), van kadra u makrou."""
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -7.0))
    o = bpy.context.active_object
    m = bpy.data.materials.new("pod")
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.012, 0.012, 0.013, 1)
    p.inputs["Roughness"].default_value = 0.35
    o.data.materials.append(m)
    return o


# ---------------------------------------------------------------- položaj kamere za snimak „sat"
def kamera_sat(f):
    """Vraća (pozicija, cilj, objektiv, boja brojčanika) za kadar f (91–300)."""
    t = (f - REZ) / FPS  # 0 … 7
    # makro: kamera iznad brojčanika, polako kruži i prilazi (0–2,6 s)
    a = math.radians(-90 + 14 * t)
    visina = mesaj(9.5, 8.3, e(t / 2.6))
    nagib = 1.2
    poz_makro = Vector((nagib * math.cos(a), nagib * math.sin(a) - 0.2, visina))
    cilj_makro = Vector((0, 0.05, 0.3))
    # odmicanje do celog sata u 3/4 pogledu (3,4–6,2 s)
    w = e((t - 3.4) / 2.8)
    poz_hero = Vector((3.2, -8.5, 15.5))
    cilj_hero = Vector((0, -0.2, 0.0))
    poz = poz_makro.lerp(poz_hero, w)
    cil = cilj_makro.lerp(cilj_hero, w)
    lens = mesaj(85, 62, w)
    # match cut na udarac: boja brojčanika se menja na svaka 4 kadra (5,6–6,4 s u videu)
    boje = ["crna", "zelena", "plava", "sampanj", "crna"]
    k = f - 168
    boja = boje[min(max(k // 5, 0), 4)] if 168 <= f < 193 else "crna"
    return poz, cil, lens, boja


def render_sat():
    sc = osnovna_scena(uzoraka=28)
    sc.render.motion_blur_shutter = 0.35
    sc.render.use_motion_blur = False
    mp = studijsko_svetlo(sc, 0.75)
    koren, kazaljke, bezel = S.napravi_sat(narukvica=True)
    koren.rotation_euler = (0, 0, 0)
    pod(sc)
    traka = svetlo_traka(sc, "Traka", (6, -3, 10), (0, 0, 0), 260, w=1.6)
    svetlo_traka(sc, "Kontra", (-8, 9, 5), (0, 0, 0), 500, w=1.0, h=6.0, boja=(1, 0.88, 0.72))
    k, c = kamera(sc, 85)
    k.data.dof.use_dof = True
    k.data.dof.focus_object = c
    k.data.dof.aperture_fstop = 5.6
    os.makedirs(os.path.join(RENDER, "kadrovi"), exist_ok=True)
    lista = KADROVI or list(range(REZ, 301, KORAK))
    for f in lista:
        t = (f - REZ) / FPS
        poz, cil, lens, boja = kamera_sat(f)
        k.location, c.location, k.data.lens = poz, cil, lens
        S.postavi_boju_brojcanika(boja)
        S.postavi_vreme(kazaljke, t)
        # svetlosni odsjaj klizi preko brojčanika
        traka.location = (6 * math.cos(0.6 + 0.35 * t), 6 * math.sin(0.6 + 0.35 * t) - 2, 10)
        mp.inputs["Rotation"].default_value = (0, 0, 0.25 * t)
        # bezel škljocne za 30° (5,0–5,5 s), u pet koraka
        koraci = min(max(int((f - 150) / 3), 0), 5)
        bezel.rotation_euler = (0, 0, math.radians(6 * koraci))
        # sat se polako okreće kad kamera ode unazad
        koren.rotation_euler = (0, 0, math.radians(-12 * e((t - 4.0) / 3.0)))
        sc.render.filepath = os.path.join(RENDER, "kadrovi", f"{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"KADAR {f}", flush=True)


# ---------------------------------------------------------------- paneli za vrtešku
PANELI = [
    # (boja brojčanika, pozicija kamere, cilj, objektiv) – panel 0 se pravi iz kadra 91
    ("zelena", (6.0, -11.0, 6.5), (0, -0.3, -0.2), 70),
    ("plava", (0.0, -0.6, 9.0), (0, 0.0, 0.3), 70),
    ("sampanj", (-8.5, -9.0, 4.0), (0, -0.4, -0.3), 75),
    ("crna", (9.0, 0.2, 1.8), (1.2, 0.0, 0.0), 110),
    ("zelena", (2.5, -5.5, 5.5), (0.6, 0.6, 0.4), 120),
    ("plava", (10.0, -14.0, 3.0), (0, -1.0, -1.0), 60),
    ("sampanj", (0.0, -4.0, 7.0), (0, 0.2, 0.3), 105),
]


def render_paneli():
    sc = osnovna_scena(uzoraka=32)
    sc.render.resolution_percentage = 50
    studijsko_svetlo(sc, 0.75)
    koren, kazaljke, bezel = S.napravi_sat(narukvica=True)
    S.postavi_vreme(kazaljke, 0)
    pod(sc)
    svetlo_traka(sc, "Traka", (6, -3, 10), (0, 0, 0), 900)
    svetlo_traka(sc, "Kontra", (-8, 9, 5), (0, 0, 0), 500, w=1.0, h=6.0, boja=(1, 0.88, 0.72))
    k, c = kamera(sc, 70)
    os.makedirs(os.path.join(RENDER, "paneli"), exist_ok=True)
    for i, (boja, poz, cil, lens) in enumerate(PANELI, start=1):
        S.postavi_boju_brojcanika(boja)
        k.location, c.location, k.data.lens = poz, cil, lens
        sc.render.filepath = os.path.join(RENDER, "paneli", f"panel_{i}.png")
        bpy.ops.render.render(write_still=True)
        print(f"PANEL {i}", flush=True)


# ---------------------------------------------------------------- POV vrteška
def render_karusel():
    sc = osnovna_scena(uzoraka=16)
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.6
    sc.render.fps = FPS
    # Standard: slika na panelu ostaje tačno kakva je (već je prošla AgX u svom renderu), za neprimetan rez
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.frame_start, sc.frame_end = 1, REZ - 1
    svet = bpy.data.worlds.new("Tama")
    sc.world = svet
    svet.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.004, 0.005, 1)

    R = 3.2
    N = 8
    W, H = 1.62, 2.88  # 9:16 kao kadar
    vrtesko = bpy.data.objects.new("vrtesko", None)
    sc.collection.objects.link(vrtesko)
    slike = [os.path.join(RENDER, "kadrovi", f"{REZ:04d}.png")] + [os.path.join(RENDER, "paneli", f"panel_{i}.png") for i in range(1, N)]
    for i, put in enumerate(slike):
        m = bpy.data.materials.new(f"panel_{i}")
        nt = m.node_tree
        p = nt.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (0, 0, 0, 1)
        p.inputs["Roughness"].default_value = 0.18
        p.inputs["Emission Strength"].default_value = 1.0
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = bpy.data.images.load(put)
        tx.interpolation = "Cubic"
        nt.links.new(tx.outputs["Color"], p.inputs["Emission Color"])
        bpy.ops.mesh.primitive_plane_add(size=1)
        o = bpy.context.active_object
        o.name = f"panel_{i}"
        o.scale = (W, H, 1)
        bpy.ops.object.transform_apply(scale=True)
        o.data.materials.append(m)
        ugao = 2 * math.pi * i / N
        # panel stoji na krugu, okrenut ka centru (kamera je u centru)
        o.parent = vrtesko
        o.location = (R * math.sin(ugao), R * math.cos(ugao), 0)
        o.rotation_euler = (math.radians(90), 0, -ugao)
    # odsjaj panela na tamnom podu
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, -H / 2 - 0.02))
    podloga = bpy.context.active_object
    m = bpy.data.materials.new("sjajni_pod")
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1)
    p.inputs["Roughness"].default_value = 0.22
    podloga.data.materials.append(m)

    k = bpy.data.objects.new("Kamera", bpy.data.cameras.new("Kamera"))
    k.data.lens = 18
    sc.collection.objects.link(k)
    sc.camera = k
    k.rotation_euler = (math.radians(90), 0, 0)

    # vrtnja: dva i po kruga, usporava i staje tačno na panelu 0 (2,4 s), pa kamera uleće u njega
    STANE = 72
    ukupno = 2.5 * 2 * math.pi
    for f in range(1, REZ):
        w = izlaz((f - 1) / (STANE - 1))
        vrtesko.rotation_euler = (0, 0, ukupno * (1 - w))
        vrtesko.keyframe_insert("rotation_euler", index=2, frame=f)
        # ulet: od centra do tačke gde panel tačno popuni kadar (vidno polje 18 mm, visina 2,88)
        u = e((f - STANE) / (REZ - 1 - STANE))
        fov_v = 2 * math.atan(36 / 2 / 18)
        do = R - (H / 2) / math.tan(fov_v / 2)
        k.location = (0, mesaj(0, do, u), 0)
        k.keyframe_insert("location", index=1, frame=f)
    os.makedirs(os.path.join(RENDER, "kadrovi"), exist_ok=True)
    lista = KADROVI or list(range(1, REZ, KORAK))
    for f in lista:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(RENDER, "kadrovi", f"{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"KADAR {f}", flush=True)


{"sat": render_sat, "paneli": render_paneli, "karusel": render_karusel}[MOD]()
