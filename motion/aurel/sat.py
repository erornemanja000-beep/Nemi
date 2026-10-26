"""AUREL: izmišljen luksuzni sat (ronilački stil, 40 mm), napravljen kodom u Blender-u.

Jedinice su centimetri: kućište ima poluprečnik 2,0. Brojčanik gleda u +Z.
Namerno bez obeležja tuđih brendova: bez krune na brojčaniku, bez lupe nad datumom,
bez „Mercedes" kazaljki; kazaljke su obične (baton), a natpis je AUREL.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


def lin(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return (c(rgb[0]), c(rgb[1]), c(rgb[2]), 1.0)


BOJE_BROJCANIKA = {
    "crna": lin((8, 8, 9)),
    "zelena": lin((10, 58, 38)),
    "plava": lin((10, 32, 78)),
    "sampanj": lin((196, 170, 122)),
}


# ---------------------------------------------------------------- materijali
def mat(ime, boja, hrap, metal=0.0, sjaj=0.0, aniz=0.0, prenos=0.0, ior=1.5, emisija=0.0):
    m = bpy.data.materials.get(ime) or bpy.data.materials.new(ime)
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = boja
    p.inputs["Roughness"].default_value = hrap
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = sjaj
    p.inputs["Coat Roughness"].default_value = 0.03
    p.inputs["Anisotropic"].default_value = aniz
    p.inputs["Transmission Weight"].default_value = prenos
    p.inputs["IOR"].default_value = ior
    if emisija:
        p.inputs["Emission Color"].default_value = boja
        p.inputs["Emission Strength"].default_value = emisija
    return m


def materijali():
    return {
        "polir": mat("celik_polir", lin((214, 214, 218)), 0.07, 1.0),
        "cetka": mat("celik_cetka", lin((200, 200, 204)), 0.24, 1.0, aniz=0.7),
        "brojcanik": mat("brojcanik", BOJE_BROJCANIKA["crna"], 0.16, 0.0, sjaj=1.0),
        "keramika": mat("keramika", lin((10, 10, 12)), 0.06, 0.0, sjaj=1.0),
        "lume": mat("lume", lin((236, 232, 214)), 0.35, emisija=0.04),
        "belo": mat("belo_stampa", lin((240, 238, 232)), 0.4),
        "safir": mat("safir", (1, 1, 1, 1), 0.0, prenos=1.0, ior=1.5),
    }


def postavi_boju_brojcanika(ime):
    bpy.data.materials["brojcanik"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = BOJE_BROJCANIKA[ime]


# ---------------------------------------------------------------- pomoćne za mreže
def objekat(ime, me, m, roditelj, glatko=True):
    if glatko:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(m)
    o = bpy.data.objects.new(ime, me)
    bpy.context.scene.collection.objects.link(o)
    o.parent = roditelj
    return o


def prsten_mreza(ime, profil, M=180, rebra=0, dubina_rebra=0.0, rebra_na=()):
    """Okretno telo od profila [(r, z), …]; svaki segment ima svoje temene tačke (oštre ivice).
    rebra_na: indeksi tačaka profila na koje se primenjuju rebra (npr. ivica bezela)."""
    verts, faces = [], []
    for k in range(len(profil) - 1):
        prstenovi = []
        for (r, z), idx in ((profil[k], k), (profil[k + 1], k + 1)):
            i0 = len(verts)
            for i in range(M):
                a = 2 * math.pi * i / M
                rr = r
                if rebra and idx in rebra_na:
                    rr = r - dubina_rebra * (0.5 - 0.5 * math.cos(rebra * a))
                verts.append((rr * math.cos(a), rr * math.sin(a), z))
            prstenovi.append(i0)
        a0, a1 = prstenovi
        for i in range(M):
            j = (i + 1) % M
            faces.append((a0 + i, a0 + j, a1 + j, a1 + i))
    me = bpy.data.meshes.new(ime)
    me.from_pydata(verts, [], faces)
    return me


def disk(ime, r, z, M=128, dole=False):
    verts = [(0, 0, z)] + [(r * math.cos(2 * math.pi * i / M), r * math.sin(2 * math.pi * i / M), z) for i in range(M)]
    faces = [((0, i + 1, (i + 1) % M + 1) if not dole else (0, (i + 1) % M + 1, i + 1)) for i in range(M)]
    me = bpy.data.meshes.new(ime)
    me.from_pydata(verts, [], faces)
    return me


def kutija(ime, dim, poz, m, roditelj, zaobli=0.0, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(ime)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=dim, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    o = objekat(ime, me, m, roditelj, glatko=False)
    o.location = poz
    o.rotation_euler = rot
    if zaobli:
        b = o.modifiers.new("zaobli", "BEVEL")
        b.width = zaobli
        b.segments = 3
        b.harden_normals = True
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    return o


def valjak(ime, r, h, poz, m, roditelj, M=64, rot=(0, 0, 0), zaobli=0.0):
    me = bpy.data.meshes.new(ime)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=M, radius1=r, radius2=r, depth=h)
    bm.to_mesh(me)
    bm.free()
    o = objekat(ime, me, m, roditelj, glatko=False)
    o.location = poz
    o.rotation_euler = rot
    if zaobli:
        b = o.modifiers.new("zaobli", "BEVEL")
        b.width = zaobli
        b.segments = 3
        b.harden_normals = True
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    return o


def tekst(ime, sadrzaj, vel, poz, m, roditelj, razmak=0.0, debljina=0.004, rot_z=0.0):
    cu = bpy.data.curves.new(ime, "FONT")
    cu.body = sadrzaj
    cu.size = vel
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_character = 1.0 + razmak
    cu.extrude = debljina
    cu.materials.append(m)
    o = bpy.data.objects.new(ime, cu)
    bpy.context.scene.collection.objects.link(o)
    o.parent = roditelj
    o.location = poz
    o.rotation_euler = (0, 0, rot_z)
    return o


# ---------------------------------------------------------------- sat
def napravi_sat(narukvica=True):
    M = materijali()
    koren = bpy.data.objects.new("AUREL", None)
    bpy.context.scene.collection.objects.link(koren)

    # kućište: bok, gornja kosina, dno
    objekat("kuciste", prsten_mreza("kuciste", [(1.62, -0.55), (1.98, -0.55), (2.02, -0.35), (2.02, 0.25), (1.96, 0.42), (1.66, 0.42)]), M["polir"], koren)
    objekat("dno", disk("dno", 1.62, -0.55, dole=True), M["cetka"], koren)

    # ušice
    for sx in (-1, 1):
        for sy in (-1, 1):
            kutija(f"usica_{sx}_{sy}", (0.42, 1.1, 0.5), (sx * 1.38, sy * 2.05, 0.0), M["cetka"], koren, 0.12, rot=(sy * 0.12, 0, 0))

    # kruna sa zaštitom
    valjak("kruna", 0.3, 0.38, (2.2, 0, -0.05), M["polir"], koren, M=36, rot=(0, math.pi / 2, 0), zaobli=0.05)
    for i in range(18):
        a = 2 * math.pi * i / 18
        kutija(f"nazubljenje_{i}", (0.36, 0.04, 0.035), (2.2, 0.3 * math.cos(a), -0.05 + 0.3 * math.sin(a)), M["polir"], koren, rot=(a, 0, 0))

    # bezel sa rebrima (60 zuba) i keramički umetak
    objekat(
        "bezel",
        prsten_mreza("bezel", [(1.64, 0.42), (1.64, 0.66), (2.06, 0.6), (2.06, 0.42)], M=360, rebra=120, dubina_rebra=0.05, rebra_na=(2, 3)),
        M["polir"],
        koren,
    )
    bezel = bpy.data.objects["bezel"]
    umetak = objekat("umetak", prsten_mreza("umetak", [(1.68, 0.665), (1.97, 0.615)], M=180), M["keramika"], koren)
    # oznake na umetku: crtice i brojevi, pa trougao na 12
    bezel_grupa = bpy.data.objects.new("bezel_grupa", None)
    bpy.context.scene.collection.objects.link(bezel_grupa)
    bezel_grupa.parent = koren
    bezel.parent = bezel_grupa
    umetak.parent = bezel_grupa
    for i in range(60):
        a = math.pi / 2 - 2 * math.pi * i / 60
        if i % 10 == 0 and i:
            br = tekst(f"bezel_br_{i}", str(i), 0.17, (1.83 * math.cos(a), 1.83 * math.sin(a), 0.645), M["belo"], bezel_grupa, debljina=0.003, rot_z=a - math.pi / 2)
            br.rotation_euler = (math.radians(7), 0, a - math.pi / 2)
        elif i < 15 or i % 5 == 0:
            d = 0.16 if i % 5 == 0 else 0.09
            kutija(f"bezel_crt_{i}", (0.025, d, 0.01), ((1.93 - d / 2) * math.cos(a), (1.93 - d / 2) * math.sin(a), 0.632), M["belo"], bezel_grupa, rot=(math.radians(7), 0, a - math.pi / 2))
    me = bpy.data.meshes.new("trougao")
    me.from_pydata([(0, 1.74, 0.646), (-0.11, 1.93, 0.636), (0.11, 1.93, 0.636)], [], [(0, 2, 1)])
    objekat("bezel_trougao", me, M["lume"], bezel_grupa)

    # brojčanik i prsten oko njega
    objekat("brojcanik", disk("brojcanik", 1.56, 0.3), M["brojcanik"], koren)
    objekat("rehaut", prsten_mreza("rehaut", [(1.56, 0.3), (1.66, 0.42)], M=180), M["cetka"], koren)

    # indeksi: trougao na 12, štapići na 3/6/9, tačke ostalo
    for h in range(12):
        a = math.pi / 2 - 2 * math.pi * h / 12
        r = 1.22
        x, y = r * math.cos(a), r * math.sin(a)
        if h == 0:
            # trougao na 12: metalni okvir i lume u njemu
            for ime, (w, y0, y1, z, m) in {
                "idx_12_okvir": (0.2, 0.98, 1.42, 0.335, M["polir"]),
                "idx_12_lume": (0.15, 1.05, 1.37, 0.345, M["lume"]),
            }.items():
                me = bpy.data.meshes.new(ime)
                me.from_pydata([(0, y0, z), (w, y1, z), (-w, y1, z)], [], [(0, 1, 2)])
                objekat(ime, me, m, koren, glatko=False)
        elif h in (3, 6, 9):
            kutija(f"idx_{h}_okvir", (0.16, 0.42, 0.05), (x, y, 0.33), M["polir"], koren, 0.015, rot=(0, 0, a - math.pi / 2))
            kutija(f"idx_{h}_lume", (0.11, 0.36, 0.02), (x, y, 0.36), M["lume"], koren, rot=(0, 0, a - math.pi / 2))
        else:
            valjak(f"idx_{h}_okvir", 0.12, 0.05, (x, y, 0.33), M["polir"], koren, M=32, zaobli=0.012)
            valjak(f"idx_{h}_lume", 0.095, 0.02, (x, y, 0.36), M["lume"], koren, M=32)
    # minutne crtice po obodu
    for i in range(60):
        if i % 5:
            a = math.pi / 2 - 2 * math.pi * i / 60
            kutija(f"min_{i}", (0.018, 0.07, 0.004), (1.48 * math.cos(a), 1.48 * math.sin(a), 0.302), M["belo"], koren, rot=(0, 0, a - math.pi / 2))

    tekst("natpis", "AUREL", 0.2, (0, 0.62, 0.302), M["belo"], koren, razmak=0.35)
    tekst("natpis_mali", "AUTOMATIK", 0.075, (0, -0.55, 0.302), M["belo"], koren, razmak=0.3)
    tekst("natpis_dubina", "200 m", 0.075, (0, -0.72, 0.302), M["belo"], koren, razmak=0.2)

    # kazaljke (baton), svaka u svom pivotu da se okreće oko centra
    kazaljke = {}
    for ime, duz, sir, z in (("sat", 0.92, 0.13, 0.4), ("minut", 1.34, 0.1, 0.44), ("sekund", 1.42, 0.03, 0.48)):
        p = bpy.data.objects.new(f"pivot_{ime}", None)
        bpy.context.scene.collection.objects.link(p)
        p.parent = koren
        p.location = (0, 0, z)
        if ime == "sekund":
            kutija("kaz_sekund", (sir, duz + 0.35, 0.012), (0, (duz - 0.35) / 2, 0), M["polir"], p)
            valjak("kaz_sekund_lizalica", 0.09, 0.02, (0, 1.0, 0.004), M["polir"], p, M=32)
            valjak("kaz_sekund_lume", 0.065, 0.02, (0, 1.0, 0.012), M["lume"], p, M=32)
        else:
            kutija(f"kaz_{ime}", (sir, duz, 0.025), (0, duz / 2 - 0.08, 0), M["polir"], p, 0.008)
            kutija(f"kaz_{ime}_lume", (sir * 0.6, duz * 0.62, 0.012), (0, duz * 0.5, 0.016), M["lume"], p)
        kazaljke[ime] = p
    valjak("centar", 0.07, 0.12, (0, 0, 0.46), M["polir"], koren, M=24)

    # safirno staklo
    objekat("staklo", prsten_mreza("staklo", [(0, 0.82), (1.6, 0.8), (1.64, 0.72), (1.64, 0.62)], M=180), M["safir"], koren)
    bpy.data.objects["staklo"].visible_shadow = False

    if narukvica:
        napravi_narukvicu(koren, M)
    return koren, kazaljke, bezel_grupa


def napravi_narukvicu(koren, M):
    """Trodelna narukvica: srednji polirani i dva brušena reda, savija se unazad kao na postolju."""
    R = 3.2
    korak = 0.62
    for strana in (1, -1):
        s = 0.25
        k = 0
        while s < math.pi * R * 0.92:
            u = s / R
            y = strana * (2.55 + R * math.sin(u))
            z = 0.05 - R * (1 - math.cos(u))
            nagib = strana * u
            for x, sir, m in ((0.0, 0.52, M["polir"]), (0.63, 0.66, M["cetka"]), (-0.63, 0.66, M["cetka"])):
                kutija(f"karika_{strana}_{k}_{x}", (sir, korak * 0.94, 0.32), (x, y, z), m, koren, 0.07, rot=(nagib, 0, 0))
            s += korak
            k += 1


def postavi_vreme(kazaljke, sekunde_od_pocetka, pocetno=(10, 9, 30)):
    """Kazaljke za vreme 10:09:30 + protekle sekunde (sekundara klizi kao automatik, 8 otkucaja u sekundi)."""
    h0, m0, s0 = pocetno
    s = s0 + math.floor(sekunde_od_pocetka * 8) / 8
    m = m0 + s / 60
    h = h0 + m / 60
    kazaljke["sekund"].rotation_euler = (0, 0, -2 * math.pi * s / 60)
    kazaljke["minut"].rotation_euler = (0, 0, -2 * math.pi * m / 60)
    kazaljke["sat"].rotation_euler = (0, 0, -2 * math.pi * h / 12)
