"""KREISEL, 3D proizvod za sajt: čaša cold brew-a, traka karamele, mleko, nova čaša sa latteom.

Kadrovi su providni PNG (960 × 600, isti odnos kao ekran 1440 × 900). Sajt ih crta preko sadržaja
dok se skroluje. Vreme t (sekunde) prati isti raspored kao sajt (site/app.js) i video:
  0,0–1,4  hero: karamela kruži oko čaše
  1,4–2,6  skrol na sekciju 2: čaša odlazi gore, karamela postaje ∞
  3,0–4,2  mleko pada u ∞, sve se uvija u vrtlog, kapi lete
  4,2–5,4  skrol na sekciju 3: vrtlog postaje mlaz koji puni novu čašu
  5,8–6,6  karamela postaje prsten oko čaše, do kraja se polako okreće

Pokretanje:
  blender -b --factory-startup --python motion/kreisel/produkt.py -- [--od 1] [--do 255] [--procenat 100] [--kadrovi 15,60,90]
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix

OVDE = os.path.dirname(os.path.abspath(__file__))
IZLAZ = os.path.join(OVDE, "render", "produkt")
ARG = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def arg(ime, podr):
    return ARG[ARG.index(ime) + 1] if ime in ARG else podr


FPS = 30
UKUPNO = 255
OD = int(arg("--od", 1))
DO = int(arg("--do", UKUPNO))
PROCENAT = int(arg("--procenat", 100))
KADROVI = [int(k) for k in arg("--kadrovi", "").split(",") if k]

VISINA_EKRANA = 5.294  # visina vidnog polja u jedinicama na dubini 0 (900 px)


# ---------------------------------------------------------------- vreme
def e(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x * x * x if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def skrol(t):
    """Pomeraj stranice u jedinicama (900 px = 5,294)."""
    return VISINA_EKRANA * (e((t - 1.4) / 1.2) + e((t - 4.2) / 1.2))


def mesaj(a, b, w):
    return tuple(x + (y - x) * w for x, y in zip(a, b))


def lin(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return (c(rgb[0]), c(rgb[1]), c(rgb[2]), 1.0)


# ---------------------------------------------------------------- scena
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 32
sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 12
sc.cycles.transmission_bounces = 12
sc.cycles.transparent_max_bounces = 8
sc.cycles.glossy_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
sc.render.use_persistent_data = True
sc.render.film_transparent = True
sc.render.resolution_x = 960
sc.render.resolution_y = 600
sc.render.resolution_percentage = PROCENAT
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
# Standard, da krem iza stakla bude tačno boja sajta (#f3ece2)
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "Medium High Contrast"

svet = bpy.data.worlds.new("Svet")
sc.world = svet
# kroz staklo (prenos) se vidi tačna krem boja sajta, a za osvetljenje svet je slabiji
KREM = None  # postavlja se posle lin()

kam = bpy.data.objects.new("Kamera", bpy.data.cameras.new("Kamera"))
kam.data.lens = 85
kam.location = (0, -20, 0)
kam.rotation_euler = (math.radians(90), 0, 0)
sc.collection.objects.link(kam)
sc.camera = kam


def svetlo(ime, poz, energija, boja, velicina, cilj=(0, 0, 0), oblik="SQUARE", vel_y=None):
    l = bpy.data.lights.new(ime, "AREA")
    l.energy = energija
    l.color = boja
    l.shape = oblik
    l.size = velicina
    if vel_y:
        l.size_y = vel_y
    o = bpy.data.objects.new(ime, l)
    o.location = poz
    o.visible_camera = False
    sc.collection.objects.link(o)
    smer = o.constraints.new("TRACK_TO")
    p = bpy.data.objects.new(ime + "_cilj", None)
    p.location = cilj
    sc.collection.objects.link(p)
    smer.target = p
    smer.track_axis = "TRACK_NEGATIVE_Z"
    smer.up_axis = "UP_Y"


svetlo("Glavno", (-7, -9, 7), 2100, (1.0, 0.93, 0.84), 5)
svetlo("Kontra", (7, 7, 4), 1700, (1.0, 0.72, 0.5), 4)
svetlo("Traka", (-3, -7, 2), 600, (1.0, 0.97, 0.92), 0.5, oblik="RECTANGLE", vel_y=7)


KREM = lin((243, 236, 226))
_nt = svet.node_tree
_bg = _nt.nodes["Background"]
_bg.inputs[0].default_value = KREM
_bg.inputs[1].default_value = 0.45
_kroz = _nt.nodes.new("ShaderNodeBackground")
_kroz.inputs[0].default_value = KREM
_kroz.inputs[1].default_value = 1.0
_put = _nt.nodes.new("ShaderNodeLightPath")
_mix = _nt.nodes.new("ShaderNodeMixShader")
_nt.links.new(_put.outputs["Is Transmission Ray"], _mix.inputs[0])
_nt.links.new(_bg.outputs[0], _mix.inputs[1])
_nt.links.new(_kroz.outputs[0], _mix.inputs[2])
_nt.links.new(_mix.outputs[0], _nt.nodes["World Output"].inputs["Surface"])

# ---------------------------------------------------------------- materijali
def materijal(ime, boja, hrapavost=0.3, prenos=0.0, ior=1.45, sss=0.0, sss_r=(1, 0.5, 0.25), sjaj=0.0):
    m = bpy.data.materials.new(ime)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = boja
    p.inputs["Roughness"].default_value = hrapavost
    p.inputs["Transmission Weight"].default_value = prenos
    p.inputs["IOR"].default_value = ior
    p.inputs["Subsurface Weight"].default_value = sss
    p.inputs["Subsurface Radius"].default_value = sss_r
    p.inputs["Coat Weight"].default_value = sjaj
    p.inputs["Coat Roughness"].default_value = 0.08
    return m


STAKLO = materijal("staklo", (1, 1, 1, 1), 0.04, 1.0, 1.5)
LED = materijal("led", (0.96, 0.98, 1, 1), 0.12, 1.0, 1.31)
KAFA = materijal("kafa", lin((46, 22, 10)), 0.06, 0.0, 1.33, sjaj=0.4)
LATTE_DNO = materijal("latte_dno", lin((96, 54, 26)), 0.12, 0.0, 1.33, sss=0.3, sss_r=(1, 0.5, 0.2))
LATTE_VRH = materijal("latte_vrh", lin((188, 146, 104)), 0.25, 0.0, 1.35, sss=0.5, sss_r=(1, 0.7, 0.45))
KARAMELA = materijal("karamela", lin((176, 92, 30)), 0.14, 0.0, 1.5, sss=0.45, sss_r=(1, 0.45, 0.15), sjaj=0.6)
MLEKO = materijal("mleko", lin((246, 240, 230)), 0.2, 0.0, 1.35, sss=1.0, sss_r=(1, 0.9, 0.8))


# ---------------------------------------------------------------- čaša sa rebrima
def casa(ime, R=0.62, H=1.9, zid=0.06, dno=0.16, rebra=32, dubina=0.028):
    """Čaša sa rebrima. Svaki deo (zid, rub, unutrašnji zid, dna) ima svoje temene tačke,
    da glatko senčenje ne meša normale preko oštrih ivica (inače staklo izgleda kao ogledalo)."""
    M = 128
    verts, faces = [], []

    def prsten(r, z, rebra_da):
        i0 = len(verts)
        for i in range(M):
            a = 2 * math.pi * i / M
            rr = r * (1 - dubina * (0.5 - 0.5 * math.cos(rebra * a))) if rebra_da else r
            verts.append((rr * math.cos(a), rr * math.sin(a), z))
        return i0

    def zid_izmedju(a0, a1):
        for i in range(M):
            j = (i + 1) % M
            faces.append((a0 + i, a0 + j, a1 + j, a1 + i))

    def lepeza(a0, z, gore):
        c = len(verts)
        verts.append((0, 0, z))
        for i in range(M):
            j = (i + 1) % M
            faces.append((c, a0 + i, a0 + j) if gore else (c, a0 + j, a0 + i))

    # spoljni zid u 6 redova (rebra), rub, unutrašnji zid, unutrašnje dno, spoljno dno
    redovi = [prsten(R, H * k / 6, True) for k in range(7)]
    for a0, a1 in zip(redovi, redovi[1:]):
        zid_izmedju(a0, a1)
    r1, r2 = prsten(R, H, True), prsten(R - zid, H, False)
    zid_izmedju(r1, r2)
    u1, u2 = prsten(R - zid, H, False), prsten(R - zid, dno, False)
    zid_izmedju(u1, u2)
    lepeza(prsten(R - zid, dno, False), dno, True)
    lepeza(prsten(R, 0.0, True), 0.0, False)
    me = bpy.data.meshes.new(ime)
    me.from_pydata(verts, [], faces)
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(STAKLO)
    o = bpy.data.objects.new(ime, me)
    o.visible_shadow = False  # svetlo prolazi do tečnosti (kaustike su isključene radi brzine)
    sc.collection.objects.link(o)
    return o


def valjak(ime, r, mat, visina=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=72, radius=r, depth=visina)
    o = bpy.context.active_object
    o.name = ime
    bpy.ops.object.shade_smooth()
    # osnova na z = 0, da skaliranje po z puni odozdo
    o.data.transform(Matrix.Translation((0, 0, visina / 2)))
    o.data.materials.append(mat)
    return o


def kocka_leda(ime, vel):
    bpy.ops.mesh.primitive_cube_add(size=vel)
    o = bpy.context.active_object
    o.name = ime
    b = o.modifiers.new("zaobli", "BEVEL")
    b.width = vel * 0.18
    b.segments = 3
    bpy.ops.object.shade_smooth()
    o.data.materials.append(LED)
    o.visible_shadow = False
    return o


def hvatac_senke(ime):
    bpy.ops.mesh.primitive_plane_add(size=9)
    o = bpy.context.active_object
    o.name = ime
    o.is_shadow_catcher = True
    o.visible_transmission = False
    o.visible_glossy = False
    o.visible_diffuse = False
    return o


def roditelj(dete, otac, poz=(0, 0, 0), rot=(0, 0, 0)):
    dete.parent = otac
    dete.location = poz
    dete.rotation_euler = rot


# čaša 1: cold brew sa ledom (hero)
CASA1 = bpy.data.objects.new("casa1", None)
sc.collection.objects.link(CASA1)
roditelj(casa("casa1_staklo"), CASA1)
kafa1 = valjak("casa1_kafa", 0.555, KAFA, 1.3)
roditelj(kafa1, CASA1, (0, 0, 0.165))
for i, (p, r) in enumerate([((0.15, 0.1, 1.28), (0.4, 0.2, 0.3)), ((-0.18, -0.12, 1.33), (0.1, 0.6, 1.0)), ((0.05, -0.22, 1.05), (0.7, 0.1, 0.4)), ((-0.1, 0.2, 0.98), (0.2, 0.9, 0.1))]):
    roditelj(kocka_leda(f"casa1_led{i}", 0.34), CASA1, p, r)
senka1 = hvatac_senke("senka1")
roditelj(senka1, CASA1, (0, 0, 0.001))

# čaša 2: latte sa ledom (sekcija 3)
CASA2 = bpy.data.objects.new("casa2", None)
sc.collection.objects.link(CASA2)
S2 = 1.2
CASA2.scale = (S2, S2, S2)
roditelj(casa("casa2_staklo", R=0.66, H=2.0), CASA2)
latte_dno = valjak("casa2_dno", 0.595, LATTE_DNO, 1.0)
roditelj(latte_dno, CASA2, (0, 0, 0.165))
latte_vrh = valjak("casa2_vrh", 0.594, LATTE_VRH, 1.0)
roditelj(latte_vrh, CASA2, (0, 0, 0.9))
led2 = []
for i, (p, r) in enumerate([((0.17, 0.08, 1.62), (0.5, 0.2, 0.3)), ((-0.2, -0.1, 1.7), (0.1, 0.7, 1.1)), ((0.02, -0.25, 1.4), (0.8, 0.1, 0.5)), ((-0.12, 0.22, 1.25), (0.3, 0.9, 0.2))]):
    k = kocka_leda(f"casa2_led{i}", 0.36)
    roditelj(k, CASA2, p, r)
    led2.append(k)
senka2 = hvatac_senke("senka2")
roditelj(senka2, CASA2, (0, 0, 0.001))


# ---------------------------------------------------------------- trake (karamela i mleko)
def traka(ime, n, mat, sirina, debljina):
    cu = bpy.data.curves.new(ime, "CURVE")
    cu.dimensions = "3D"
    cu.twist_mode = "MINIMUM"
    cu.bevel_depth = debljina
    cu.bevel_resolution = 4
    cu.extrude = sirina
    cu.use_fill_caps = True
    cu.bevel_factor_mapping_start = "SPLINE"
    cu.bevel_factor_mapping_end = "SPLINE"
    sp = cu.splines.new("POLY")
    sp.points.add(n - 1)
    cu.materials.append(mat)
    o = bpy.data.objects.new(ime, cu)
    sc.collection.objects.link(o)
    return o


N_K = 220
N_M = 220
KAR = traka("karamela", N_K, KARAMELA, 0.085, 0.05)
MLK = traka("mleko", N_M, MLEKO, 0.0, 0.11)


def postavi(traka_obj, tacke, od=0.0, do=1.0):
    sp = traka_obj.data.splines[0]
    for p, (x, y, z) in zip(sp.points, tacke):
        p.co = (x, y, z, 1.0)
    traka_obj.data.bevel_factor_start = od
    traka_obj.data.bevel_factor_end = do


def rotx(p, ugao, centar):
    x, y, z = (p[0] - centar[0], p[1] - centar[1], p[2] - centar[2])
    c, s = math.cos(ugao), math.sin(ugao)
    return (x + centar[0], y * c - z * s + centar[1], y * s + z * c + centar[2])


# ---------------------------------------------------------------- oblici
CASA1_X = 1.55
CASA1_Z = -1.3


def spirala(t, n):
    cx, cz = CASA1_X, CASA1_Z + skrol(t)
    faza = t * 2 * math.pi / 3.2
    out = []
    for i in range(n):
        u = i / (n - 1)
        a = faza + u * 2 * math.pi * 2.3
        r = 1.0 + 0.1 * math.sin(u * 7 + t)
        p = (cx + r * math.cos(a), r * math.sin(a), cz - 0.1 + 2.5 * u)
        out.append(rotx(p, math.radians(-14), (cx, 0, cz + 1)))
    return out


def osmica(t, n, z2):
    a = 2.75
    out = []
    for i in range(n):
        th = math.pi / 2 + 2 * math.pi * i / (n - 1)
        d = 1 + math.sin(th) ** 2
        x = a * math.cos(th) / d
        z = a * math.sin(th) * math.cos(th) / d * 1.25
        y = 0.38 * math.sin(th) + 0.15 * math.sin(2 * th + t)
        p = (x, y, z + z2 - 0.25)
        out.append(rotx(p, math.radians(-22), (0, 0, z2)))
    return out


def kupa(t, n, z2, faza0, vertikalno=0.0):
    """Vrtlog: zavojnica po kupi. vertikalno = deo tačaka koje su mlaz odozgo do vrha kupe."""
    zt, zb = z2 + 1.25, z2 - 1.75
    faza = faza0 + t * 2 * math.pi * 1.15
    out = []
    for i in range(n):
        u = i / (n - 1)
        if u < vertikalno:
            w = u / vertikalno
            a0 = faza
            r0 = 1.55
            k = e((w - 0.45) / 0.55)
            out.append((r0 * math.cos(a0) * k, r0 * math.sin(a0) * k, 3.6 + (zt - 3.6) * w))
            continue
        v = (u - vertikalno) / (1 - vertikalno)
        r = 1.45 * (1 - v) ** 1.25 + 0.1
        a = faza + v * 2 * math.pi * 2.6
        out.append((r * math.cos(a), r * math.sin(a), zt + (zb - zt) * v))
    return out


def mlaz(t, n, dno_z, faza0, sirina=0.12):
    faza = faza0 + t * 2 * math.pi * 1.6
    out = []
    for i in range(n):
        u = i / (n - 1)
        a = faza + u * 2 * math.pi * 5
        z = 3.6 + (dno_z - 3.6) * u
        out.append((sirina * math.cos(a), sirina * math.sin(a), z))
    return out


def mlaz_mleka(n, kraj_z):
    return [(0.0, 0.0, 3.6 + (kraj_z - 3.6) * i / (n - 1)) for i in range(n)]


def prsten(t, n, centar_z):
    out = []
    pocetak = t * 0.55
    for i in range(n):
        u = i / (n - 1)
        a = pocetak + u * 2 * math.pi * 0.86
        r = 1.75 + 0.07 * math.sin(3 * a)
        p = (r * math.cos(a), r * math.sin(a), centar_z + 0.08 * math.sin(2 * a))
        out.append(rotx(p, math.radians(16), (0, 0, centar_z)))
    return out


# ---------------------------------------------------------------- kapi
random.seed(11)
kap_mesh = None
KAPI = []
for i in range(44):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=1)
    o = bpy.context.active_object
    o.name = f"kap{i}"
    bpy.ops.object.shade_smooth()
    o.data.materials.append(KARAMELA if i % 3 else MLEKO)
    start = 3.35 + random.random() * 0.8
    u = 0.15 + random.random() * 0.75
    ugao = random.random() * 2 * math.pi
    brzina = 1.6 + random.random() * 1.8
    KAPI.append(
        {
            "o": o,
            "start": start,
            "zivot": 0.55 + random.random() * 0.5,
            "r": 0.035 + random.random() * 0.05,
            "p0": ((1.45 * (1 - u) + 0.1) * math.cos(ugao), (1.45 * (1 - u) + 0.1) * math.sin(ugao), 1.25 - 3.0 * u),
            "v": (brzina * math.cos(ugao), brzina * math.sin(ugao) * 0.6, 1.0 + random.random() * 1.6),
        }
    )


# ---------------------------------------------------------------- stanje u trenutku t
def stanje(t):
    s = skrol(t)
    z2 = -VISINA_EKRANA + s
    z3 = -2 * VISINA_EKRANA + s

    # čaša 1
    CASA1.location = (CASA1_X, 0, CASA1_Z + s)
    CASA1.rotation_euler = (0, 0, t * 0.25)
    vidi1 = t < 3.0
    for o in [CASA1] + list(CASA1.children):
        o.hide_render = not vidi1
    senka1.hide_render = t > 1.45

    # čaša 2: dno na z3 - 2.25, puni se 4,9–5,9 s
    CASA2.location = (0, 0, z3 - 2.35)
    CASA2.rotation_euler = (0, 0, -0.4 + t * 0.12)
    vidi2 = t > 3.9
    for o in [CASA2] + list(CASA2.children):
        o.hide_render = not vidi2
    puno = e((t - 4.85) / 1.05)
    h_dno = 0.02 + 0.95 * e((t - 4.85) / 0.7)
    h_vrh = 0.02 + 0.78 * e((t - 5.15) / 0.75)
    latte_dno.scale = (1, 1, h_dno)
    latte_vrh.location = (0, 0, 0.165 + h_dno)
    latte_vrh.scale = (1, 1, h_vrh)
    latte_dno.hide_render = not vidi2 or puno <= 0.001
    latte_vrh.hide_render = not vidi2 or t < 5.15
    nivo = CASA2.location[2] + S2 * (0.165 + h_dno + (h_vrh if t >= 5.15 else 0))

    # karamela: spirala → ∞ → vrtlog → mlaz → prsten
    w1 = e((t - 1.45) / 1.15)
    w2 = e((t - 3.35) / 0.6)
    w3 = e((t - 4.2) / 0.85)
    w4 = e((t - 5.8) / 0.8)
    A = spirala(t, N_K)
    B = osmica(t, N_K, z2)
    C = kupa(t, N_K, z2, math.pi)
    D = mlaz(t, N_K, nivo - 0.05, math.pi)
    E = prsten(t, N_K, z3 - 2.35 + S2 * 1.05)
    tacke = []
    for a, b, c, d, ee in zip(A, B, C, D, E):
        p = mesaj(a, b, w1)
        p = mesaj(p, c, w2)
        p = mesaj(p, d, w3)
        p = mesaj(p, ee, w4)
        tacke.append(p)
    # dok je mlaz, traka ide od vrha ekrana; kad postane prsten, ne treba joj vrh
    postavi(KAR, tacke)

    # mleko: mlaz pada 3,0–3,35, uvija se u vrtlog, puni čašu, pa se povlači 5,9–6,3
    vidim = 3.0 <= t < 6.35
    MLK.hide_render = not vidim
    if vidim:
        kraj = 3.6 + (z2 - 0.1 - 3.6) * e((t - 3.0) / 0.35)
        S = mlaz_mleka(N_M, kraj)
        C2 = kupa(t, N_M, z2, 0.0, vertikalno=0.22)
        D2 = mlaz(t, N_M, nivo - 0.05, 0.0, sirina=0.1)
        m = []
        for a, b, c in zip(S, C2, D2):
            p = mesaj(a, b, w2)
            m.append(mesaj(p, c, w3))
        postavi(MLK, m, od=e((t - 5.9) / 0.4), do=1.0)

    # kapi
    for k in KAPI:
        dt = t - k["start"]
        ziv = 0 <= dt < k["zivot"] and k["start"] < 4.3
        k["o"].hide_render = not ziv
        if ziv:
            x = k["p0"][0] + k["v"][0] * dt
            y = k["p0"][1] + k["v"][1] * dt
            z = k["p0"][2] + z2 + k["v"][2] * dt - 3.2 * dt * dt
            r = k["r"] * (1 - (dt / k["zivot"]) ** 3)
            k["o"].location = (x, y, z)
            k["o"].scale = (r, r, r * 1.15)


# ---------------------------------------------------------------- render
os.makedirs(IZLAZ, exist_ok=True)
lista = KADROVI or list(range(OD, DO + 1))
for f in lista:
    t = (f - 1) / FPS
    stanje(t)
    sc.render.filepath = os.path.join(IZLAZ, f"{f:04d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"KADAR {f} t={t:.2f}", flush=True)
