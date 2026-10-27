# Krume, smer 3 "Ein Fenster brennt": bake kvarta i izvoz za web (talas 2, Z6).
# Gradi kvart iz kvart.py (KRUME_WEB: bevel 1 segment), spaja delove po cvoru (kuca, Kriska, Tlo, lampe...),
# brise skrivene povrsine, pravi UV atlase i peca u Cycles-u (GPU):
#   albedo  osnovna boja bez svetla (DIFFUSE color), ide u GLB kao baseColorTexture (UV 0 "albedo")
#   noc     svetlo kao kadar 1: pekara (izlog, table, vrata), ulicne lampe, stona lampa makete, nebo pre zore
#   dan     jutro 06:30-07:00: nisko toplo sunce s jugoistoka, hladno nebo, lampe ugasene, izlog slabije
# Lightmap = samo svetlo (DIFFUSE direct + indirect, bez boje), na drugom UV setu "lightmap" (TEXCOORD_1).
# Prozori sa atributom _wake NE peku svoj sjaj (prag -1): sjaj pravi shader. Emisivni i providni delovi
# (lampice, glava lampe, staklo izloga, slabi izlozi preko puta, tramvaj) nisu u atlasu: cvor "<ime>_ziv".
# Pokretanje (iz ovog foldera):
#   Blender -b -P bake_izvoz.py                         (sve: gradnja, bake, teksture, GLB, provera, kamera.json)
#   Blender -b bake/grad_bake.blend -P bake_izvoz.py -- izvoz   (bez ponovnog bake-a: teksture iz bake/grad-raw-*.npz,
#                                                               koji ostaju samo uz KRUME_CUVAJ=1; GLB, provera)
#   Blender -b kvart.blend -P bake_izvoz.py -- kamera           (samo kamera.json, npr. kad enterijer doda Stanica_4/5)
# Okruzenje: KRUME_BAKE_SAMPLES (lightmap, podrazumevano 256), KRUME_ATLAS (2048), KRUME_SAMPLES (provera, 48).

import bpy, bmesh, json, math, os, sys, time
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

T_START = time.time()
BL = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BL, "..", "..", ".."))
PUB = os.path.join(ROOT, "pekara", "public")
BAKE_DIR = os.path.join(BL, "bake")
ENTERIJER = os.path.join(BL, "enterijer.blend")
MY_ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
S_FULL = int(os.environ.get("KRUME_ATLAS", "2048"))
LM_GAMMA = 4.0          # lightmap: enc = (L / max) ^ (1 / LM_GAMMA), sjaj = max * enc ^ LM_GAMMA
os.makedirs(BAKE_DIR, exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0          # bez .blend1

# cvorovi i atlasi: 0 ugaona kuca (blizu u pogl. 3-5), 1 blok, 2 preko puta + tlo + sitno
ATLAS = {"Ugao": 0, "Kriska": 0}
for n in ("A1", "A2", "A3", "B1", "B2", "B3"):
    ATLAS[n] = 1
POKRETNO = ("Kriska", "Tramvaj", "Figura_")             # ne zaklanjaju statican deo pri brisanju skrivenih lica
ZIVO = {"lampica", "lampa", "staklo", "staklo_slabo", "tram_okno", "tram_far", "zar", "dim"}
PROZOR = "staklo_tamno"


def log(*a):
    print(f"[{time.time() - T_START:7.1f} s]", *a, flush=True)


def gltf(v):
    """Blender (x, y, z) -> glTF (x, z, -y), zaokruzeno."""
    return [round(v[0], 3), round(v[2], 3), round(-v[1], 3)]


# ================================================================ kamera.json
# fix A (krug popravki posle zavrsne kontrole): pregazene vrednosti, Blender koordinate (x, y, z), metri.
# Stanice Zeit i Ofen (enterijer.blend se ne dira): (polozaj, cilj, lens). Zeit: dalje od police, da se vide
# korpe sa testom levo (tekst desno). Ofen: frontalno pred vratima peci (osa otvora x = 9,275, lice peci y = 4,4),
# 3 m od lica, u visini otvora (cepanice u nisi ostaju na donjoj ivici kadra), cilj malo levo od otvora, da pec
# stoji desno od sredine (tekst levo), a zar ispuni otvor.
STANICE_FIX = {"Zeit": ((3.0, 4.6, 1.6), (3.45, 8.1, 1.0), 28),
               "Ofen": ((9.27, 1.4, 1.62), (9.02, 4.4, 1.3), 32)}
# pogl. 5 na telefonu: kamera nize (1,30 m umesto 1,40), hlebovi na sredini kadra
TEL_5_FIX = {"tel_cilj": (3.21, 3.55, 1.0), "tel_shift_y": 0.0}
# kljucni kadrovi od 0,215 do 0,60: (u, polozaj, cilj, stop). "kriva": tacka sa krive (zadrzavanje pogl. 3 / 5);
# ime stanice ("4", "4_Zeit", "4_Ofen") sa "pocetak"/"kraj": stanica i njen drift. stop: brzina 0 u kljucu.
# 0,30-0,35 kamera prati krisku dok se izvlaci (cilj na kriski), 0,35-0,392 okrece se ka preseku i staje na
# trotoaru preko puta (x 4, y -12, z 2,8): otvorena pekara ~60 % sirine, levo mirna zapadna ulica za tekst;
# zaobilazi lampu (8, -10,4) i figuru (14, -11,4). 0,392-0,42 kroz otvor do stola (Kriska je vec ispod daske).
# U pekari obilazi pult (x 2,15-4,55, y 3,25-3,95) i sto (x 4,95-7,3, y 2,45-3,55) sa strane.
KLJUCEVI_3_4 = [
    # spustanje u ulicu (kraj pogl. 2): preko niskih kuca preko puta (krov ~3,6 m) najmanje 0,6 m iznad
    (0.215, "kriva", None, False),
    (0.23, (12.8, -14.5, 5.0), (6.1, 0.6, 3.95), False),
    (0.24, (15.2, -10.5, 3.0), (4.53, -0.27, 3.69), False),
    (0.25, "kriva", None, True),
    (0.30, "kriva", None, True),
    (0.345, (12.6, -8.9, 2.6), (5.6, -2.4, 3.4), False),
    (0.368, (7.4, -9.3, 2.7), (6.0, 1.2, 2.9), False),
    (0.382, (4.4, -11.5, 2.8), (6.0, 3.4, 2.6), False),
    (0.392, (4.0, -12.0, 2.8), (6.0, 3.5, 2.6), True),
    (0.405, (4.4, -4.6, 2.3), (6.1, 2.6, 1.6), False),
    (0.42, "4", "pocetak", True),
    (0.465, "4", "kraj", True),
    (0.475, (4.75, 2.0, 1.85), (5.0, 5.5, 1.0), False),
    (0.48, (4.3, 4.2, 1.75), (3.6, 7.5, 1.0), False),
    (0.485, "4_Zeit", "pocetak", True),
    (0.525, "4_Zeit", "kraj", True),
    (0.533, (5.5, 4.5, 1.75), (8.0, 6.0, 1.2), False),
    (0.539, (7.7, 3.6, 1.6), (9.2, 5.5, 1.2), False),
    (0.545, "4_Ofen", "pocetak", True),
    (0.58, "4_Ofen", "kraj", True),
    (0.59, (6.6, 1.3, 1.6), (5.0, 3.6, 1.15), False),
    (0.60, "kriva", None, True),
]


def hermite(kl, u):
    """Kubni Hermite po u kroz kljuceve (u, polozaj, cilj, stop): tangente kao Catmull-Rom, 0 u stop kljucu."""
    i = max(k for k in range(len(kl) - 1) if kl[k][0] <= u)

    def tang(k, idx):
        if len(kl[k]) > 4:                             # tangenta sa krive (kljuc "kriva" koji nije stop)
            return kl[k][4][idx - 1]
        if kl[k][3] or k == 0 or k == len(kl) - 1:
            return Vector()
        return (kl[k + 1][idx] - kl[k - 1][idx]) / (kl[k + 1][0] - kl[k - 1][0])

    u0, u1 = kl[i][0], kl[i + 1][0]
    h = u1 - u0
    t = (u - u0) / h
    h00, h10, h01, h11 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t, -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
    return tuple(kl[i][idx] * h00 + tang(i, idx) * (h10 * h) + kl[i + 1][idx] * h01 + tang(i + 1, idx) * (h11 * h)
                 for idx in (1, 2))


def svet(o):
    """Svetska matrica iz lanca roditelja (dodat objekat koji nije u sceni nema izracunatu matrix_world)."""
    m = o.matrix_basis.copy()
    while o.parent is not None:
        m = o.parent.matrix_basis @ o.matrix_parent_inverse @ m
        o = o.parent
    return m


def kamera_json():
    """Put kamere iz KameraPut + Pogl_N/Cilj_N (+ Stanica_4/5 i Hleb_1..4 iz enterijer.blend ako postoje)."""
    ob = bpy.data.objects
    pogl = {n: ob[f"Pogl_{n}"] for n in range(1, 8)}
    cilj = {n: ob[f"Cilj_{n}"].location.copy() for n in range(1, 8)}
    st4 = [(nm, ob[f"Pogl_4_{nm}"], ob[f"Cilj_4_{nm}"].location.copy()) for nm in ("Zeit", "Ofen")]
    # --- iz enterijera (samo citanje: objekti se dodaju privremeno i brisu)
    ent, izvor = {}, {"Stanica_4": False, "Stanica_5": False, "Kadar_pec": False, "hlebovi": False}
    if os.path.exists(ENTERIJER):
        with bpy.data.libraries.load(ENTERIJER, link=False) as (src, dst):
            dst.objects = [n for n in src.objects if n.startswith(("Stanica_", "Hleb_")) or n == "Kadar_pec"]
        for o in dst.objects:
            if o is None:
                continue
            props = {k: (v.to_list() if hasattr(v, "to_list") else v) for k, v in o.items()}
            if o.type == "CAMERA":
                props["lens"] = o.data.lens
            ent[o.name] = (svet(o), props)
        for o in dst.objects:
            if o is not None:
                d_ = o.data
                bpy.data.objects.remove(o)
                if d_ is not None and d_.users == 0:
                    (bpy.data.cameras if isinstance(d_, bpy.types.Camera) else bpy.data.meshes).remove(d_)
    cu = ob["KameraPut"].data
    sp = cu.splines[0]
    # Stanica_4/5 (prazni objekti enterijera, svojstva cilj i lens) zamenjuju Pogl_4/5; kamera Kadar_pec
    # iz enterijera zamenjuje stanicu "Ofen" (cilj 2,8 m ispred nje)
    zamene = [(f"Stanica_{n}", pogl[n], n) for n in (4, 5)] + [("Kadar_pec", st4[1][1], "Ofen")]
    for key, pe_, slot in zamene:
        if key not in ent:
            continue
        mw, props = ent[key]
        p_new = mw.translation.copy()
        c_new = Vector(props["cilj"]) if "cilj" in props else p_new + mw.to_3x3().normalized() @ Vector((0, 0, -2.8))
        old = pe_.location.copy()
        for bp in sp.bezier_points:                    # tacka krive na staroj poziciji kadra ide na stanicu
            if (bp.co - old).length < 1e-3:
                bp.co = p_new
        pe_.location = p_new
        if slot == "Ofen":
            st4[1] = ("Ofen", pe_, c_new)
        else:
            cilj[slot] = c_new
        if "lens" in props:
            pe_["lens"] = round(props["lens"], 1)
        izvor[key] = True
    # fix A (krug popravki): stanice Zeit i Ofen i telefon pogl. 5 pregaze vrednosti iz enterijer.blend
    for nm, (p_new, c_new, lens) in STANICE_FIX.items():
        i = [s[0] for s in st4].index(nm)
        pe_ = st4[i][1]
        for bp in sp.bezier_points:
            if (bp.co - pe_.location).length < 1e-3:
                bp.co = Vector(p_new)
        pe_.location = Vector(p_new)
        pe_["lens"] = lens
        st4[i] = (nm, pe_, Vector(c_new))
    for bp in sp.bezier_points:                        # AUTO rucke se racunaju ponovo posle pomeranja tacaka
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    for k, v in TEL_5_FIX.items():
        pogl[5][k] = list(v) if isinstance(v, tuple) else v
    # --- kriva u gustu polilinu sa duzinom luka
    dg = bpy.context.evaluated_depsgraph_get()
    pe = ob["KameraPut"].evaluated_get(dg)
    pm = pe.to_mesh()
    mw = ob["KameraPut"].matrix_world
    pts = [mw @ v.co for v in pm.vertices]
    pe.to_mesh_clear()
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + (b - a).length)
    L = cum[-1]

    def na_krivoj(s):                                   # s = udeo duzine 0-1
        d = min(max(s, 0.0), 1.0) * L
        i = max(0, min(len(cum) - 2, np.searchsorted(cum, d) - 1))
        f = (d - cum[i]) / max(1e-9, cum[i + 1] - cum[i])
        return pts[i].lerp(pts[i + 1], min(max(f, 0.0), 1.0))

    # tacke zadrzavanja redom po krivoj (monotona pretraga, kriva prolazi blizu sebe u pogl. 4)
    WP = [("1", pogl[1].location, cilj[1]), ("2", pogl[2].location, cilj[2]), ("3", pogl[3].location, cilj[3]),
          ("4", pogl[4].location, cilj[4]), ("4_Zeit", st4[0][1].location, st4[0][2]),
          ("4_Ofen", st4[1][1].location, st4[1][2]), ("5", pogl[5].location, cilj[5]),
          ("6", pogl[6].location, cilj[6]), ("7", pogl[7].location, cilj[7])]
    k0, tk = 0, {}
    for nm, p, _ in WP:
        k = min(range(k0, len(pts)), key=lambda i: (pts[i] - p).length)
        tk[nm] = cum[k] / L
        k0 = k
    # raspored po skrolu (mapa-skrola.md): [ime, u pocetka zadrzavanja, u kraja, drift (deo puta ka cilju ili +z)]
    PLAN = [("1", 0.0, 0.035, 0.05), ("2", 0.09, 0.12, 0.02), ("3", 0.25, 0.39, 0.015),
            ("4", 0.42, 0.465, 0.03), ("4_Zeit", 0.485, 0.525, 0.03), ("4_Ofen", 0.545, 0.58, 0.03),
            ("5", 0.60, 0.675, 0.03), ("6", 0.80, 0.86, 0.02), ("7", 0.88, 1.0, "gore")]
    # fix A (direktor): Kriska se vraca u u = 0,704-0,716, pa kamera napusta pekaru vec od 0,675: fasadu prelazi
    # oko 0,68 (Kriska je tada jos ispod daske), u 0,70 je vise metara ispred fasade A (u_napolju <= 0,70)
    wp = {nm: (Vector(p), Vector(c)) for nm, p, c in WP}

    def drift(nm, d, h):                               # pomak tokom zadrzavanja (h 0-1)
        p, c = wp[nm]
        if d == "gore":
            return Vector((0, 0, 2.5)) * h
        return (c - p) * d * h

    def sm(x):
        return x * x * (3 - 2 * x)

    N = 400
    P_out, C_out, B_out, T_out = [], [], [], []
    for j in range(N + 1):
        u = j / N
        for i, (nm, u0, u1, d) in enumerate(PLAN):
            nxt = PLAN[i + 1] if i + 1 < len(PLAN) else None
            if u <= u1 or nxt is None:
                h = 0.0 if u1 <= u0 else min(max((u - u0) / (u1 - u0), 0.0), 1.0)
                pos = na_krivoj(tk[nm]) + drift(nm, d, h)
                tgt = wp[nm][1].copy()
                break
            if u < nxt[1]:                             # putovanje do sledece tacke
                e = sm((u - u1) / (nxt[1] - u1))
                pos = na_krivoj(tk[nm] + (tk[nxt[0]] - tk[nm]) * e) + drift(nm, d, 1.0) * (1 - e)
                tgt = wp[nm][1].lerp(wp[nxt[0]][1], e)
                if nm == "2":                          # let pogl. 2: cilj ide desno od pravca pogleda, kuca levo,
                    dv = tgt - pos                     # desna strana kadra (tekst) ostaje nebo i ulica
                    rv = dv.cross(Vector((0, 0, 1))).normalized()
                    tgt = tgt + rv * dv.length * 0.45 * math.sin(math.pi * e) ** 0.7
                break
        B_out.append(pos.copy())
        T_out.append(tgt.copy())
    # fix A: od u = 0,215 do 0,60 put ne ide po krivoj nego kroz kljucne kadrove (KLJUCEVI_3_4), da kamera prati
    # krisku, okrene se ka preseku i obidje sto, pult i pec; prvi i poslednji kadar su tacke sa krive
    kl = []
    for u_k, p_k, c_k, stop in KLJUCEVI_3_4:
        j = round(u_k * N)
        if p_k == "kriva":
            p_k, c_k = B_out[j], T_out[j]
            if not stop:
                kl.append((u_k, p_k.copy(), c_k.copy(), stop, ((B_out[j + 1] - B_out[j - 1]) * N / 2,
                                                                 (T_out[j + 1] - T_out[j - 1]) * N / 2)))
                continue
        elif p_k in wp:                                # stanica: polozaj (+ drift na kraju zadrzavanja) i cilj
            pp, cc = wp[p_k]
            p_k = pp + (cc - pp) * (0.03 if c_k == "kraj" else 0.0)
            c_k = cc
        kl.append((u_k, Vector(p_k), Vector(c_k), stop))
    for j in range(N + 1):
        if kl[0][0] < j / N < kl[-1][0]:
            B_out[j], T_out[j] = hermite(kl, j / N)
    for pos, tgt in zip(B_out, T_out):
        P_out.append(gltf(pos))
        C_out.append(gltf(tgt))
    # od kog u je kamera opet ispred fasada ugaone kuce (najmanje 1 m), pa Kriska sme nazad
    unutra = [j for j, p in enumerate(B_out) if p.x > -1.0 and p.y > -1.0 and p.x + p.y > 1.6 and p.z < 12.0]
    u_napolju = round((max(unutra) + 1) / N, 4) if unutra else 0.6

    def fov(lens):                                      # senzor 36 mm po duzoj strani (Blender AUTO), kadar 16:10
        fh = 2 * math.degrees(math.atan(18.0 / lens))
        fv = 2 * math.degrees(math.atan(18.0 / lens / 1.6))
        return round(fv, 2), round(fh, 2)

    U0 = {1: 0.0, 2: 0.09, 3: 0.25, 4: 0.42, 5: 0.60, 6: 0.72, 7: 0.88}
    chapters = []
    for n in range(1, 8):
        pg = pogl[n]
        fv, fh = fov(pg["lens"])
        drz = [(u0, u1) for nm, u0, u1, _ in PLAN if nm == str(n)][0]
        ch = {"id": n, "u": U0[n], "drzi": [drz[0], drz[1]], "pogl": gltf(pg.location), "cilj": gltf(cilj[n]),
              "lens": pg["lens"], "fov": fv, "fov_h": fh, "shift_x": pg["shift_x"], "shift_y": pg["shift_y"],
              "tekst": pg["tekst"], "tel_cilj": gltf(pg["tel_cilj"]), "tel_blize": pg["tel_blize"],
              "tel_shift_y": pg["tel_shift_y"], "tel_tekst": pg["tel_tekst"]}
        if n == 4:
            ch["stanice"] = []
            for nm, u0, u1, _ in PLAN:
                if nm.startswith("4"):
                    pp, cc = wp[nm]
                    lens = pg["lens"] if nm == "4" else ob[f"Pogl_{nm}"]["lens"]
                    fv2, fh2 = fov(lens)
                    ch["stanice"].append({"ime": {"4": "Teig", "4_Zeit": "Zeit", "4_Ofen": "Ofen"}[nm], "u": u0,
                                          "drzi": [u0, u1], "pogl": gltf(pp), "cilj": gltf(cc), "lens": lens,
                                          "fov": fv2, "fov_h": fh2})
        chapters.append(ch)
    kr = ob["Kriska"]
    breads = []
    for i, nm in enumerate(("Kaisersemmel", "Mohnwecken", "Laugenbrezel", "Roggenlaib")):
        key = f"Hleb_{i + 1}"
        if key in ent:
            mw_, props = ent[key]
            breads.append({"name": props.get("ime", nm), "pos": gltf(mw_.translation)})
            izvor["hlebovi"] = True
        else:
            breads.append({"name": nm, "pos": gltf((2.82 + 0.26 * i, 3.55, 1.05))})
    blk = [o for o in ob if o.name == "Daska_za_hleb" or o.name == "Tlo"]
    if blk:
        bb = [blk[0].matrix_world @ Vector(c) for c in blk[0].bound_box]
        piv = Vector((sum(v.x for v in bb) / 8, sum(v.y for v in bb) / 8, 0))
    else:
        piv = Vector((6.0, 6.0, 0))
    data = {
        "_napomena": ("Iz Blendera (bake_izvoz.py, kvart.blend): put kamere KameraPut uzorkovan na 401 tacku "
                      "jednako po skrolu (param 'index': u = i/400), sa zadrzavanjem na kadru svakog poglavlja "
                      "(chapters[].drzi) i putovanjem izmedju. Koordinate glTF (Y gore), metri; Blender (x,y,z) = (x,z,-y). "
                      "Po poglavlju: lens (mm, senzor 36 mm po duzoj strani), fov (vertikalni, stepeni, za kadar 16:10), "
                      "fov_h (vodoravni), shift_x/shift_y (kao u Blenderu: deo duze strane kadra; + pomera kadar "
                      "desno/gore, sadrzaj ide suprotno), tel_* (telefon 9:16: tel_cilj, tel_blize = deo rastojanja "
                      "pogl-cilj, tel_shift_y). kriska: smer izvlacenja (jedinicni, glTF), izvuci/spusti u metrima, "
                      "u_* opsezi skrola; put kamere od Pogl_3 ka Pogl_4 krece tek na u_prolaz (Kriska spustena)."),
        "param": "index",
        "fov": 30,
        "near": 0.1,
        "far": 600,
        "portrait": {"fovFactorMax": 1.5, "shiftY": 0.1},
        "pivot": gltf(piv),
        "points": P_out,
        "targets": C_out,
        "chapters": chapters,
        "kriska": {
            "cvor": "Kriska",
            "pocetak": gltf(kr.matrix_world.translation),
            "smer": [round(x, 4) for x in gltf(Vector(kr["izvuci_smer"]))],
            "izvuci": kr["izvuci_m"],
            "spusti": kr["spusti_m"],
            "u_izvuci": [0.30, 0.35],
            "u_spusti": [0.35, 0.385],
            "u_prolaz": 0.39,
            "u_napolju": u_napolju,
            "opis": ("izvuci: pomeri cvor Kriska za smer*izvuci; spusti: zatim za -spusti po Y (kroz dasku). "
                     "u_prolaz: od ovog u kamera sme ka vratima/unutra. u_napolju: od ovog u je kamera opet ispred "
                     "linije fasade (Pogl_5), Kriska sme da se vrati."),
        },
        "breads": breads,
        "izvor": izvor,
    }
    path = os.path.join(PUB, "data", "kamera.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh_:
        json.dump(data, fh_, indent=1, ensure_ascii=False)
    log(f"kamera.json: {len(P_out)} tacaka, duzina krive {L:.1f} m, izvor {izvor}")
    provera_puta(data)
    return data


def provera_puta(data):
    """fix A: kamera nikad ne sme kroz geometriju. Za svih 401 tacaka (i 4 medjutacke) na desktopu i na telefonu
    (tel_cilj / tel_blize kao camera.js) meri najmanju udaljenost do kvarta, enterijera (privremeno iz
    enterijer.blend) i Kriske na njenom polozaju za taj u (timeline.js), i ray-cast izmedju susednih tacaka."""
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    pre = set(bpy.data.objects)
    kol = None
    if os.path.exists(ENTERIJER):
        with bpy.data.libraries.load(ENTERIJER, link=False) as (src, dst):
            dst.collections = ["Enterijer"]
        kol = dst.collections[0]
        sc.collection.children.link(kol)
        dg = bpy.context.evaluated_depsgraph_get()
    kr = bpy.data.objects["Kriska"]
    V, P, KV, KP = [], [], [], []
    for o in sc.objects:
        if o.type != "MESH" or o.hide_render or not o.users_collection:
            continue
        if o.users_collection[0].name in ("Rezaci", "Kamera") or o.name.startswith(("Dim", "Tramvaj", "Pomocno")):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        kriska = o == kr or o.parent == kr
        mw = (kr.matrix_world.inverted() @ o.matrix_world) if kriska else o.matrix_world
        vv, pp = (KV, KP) if kriska else (V, P)
        b = len(vv)
        vv.extend(mw @ v.co for v in me.vertices)
        pp.extend(tuple(b + i for i in t.vertices) for t in me.loop_triangles)
        ev.to_mesh_clear()
    tree = BVHTree.FromPolygons(V, P, all_triangles=True)
    ktree = BVHTree.FromPolygons(KV, KP, all_triangles=True)
    k0 = kr.matrix_world.translation.copy()
    smer, izv_m, sp_m = Vector(kr["izvuci_smer"]), kr["izvuci_m"], kr["spusti_m"]
    if kol is not None:
        for o in list(bpy.data.objects):
            if o not in pre:
                bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(kol)
        for coll in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
            for d_ in list(coll):
                if d_.users == 0:
                    coll.remove(d_)

    def S(a, b, x):
        t = min(max((x - a) / (b - a), 0.0), 1.0)
        return t * t * (3 - 2 * t)

    def kriska_pomak(u):                               # timeline.js: izvlacenje pa spustanje (u < 0,6)
        if u >= 0.6:                                   # povratak (animator, 0,704-0,716): od 0,70 do 0,72 se meri
            if 0.70 <= u <= 0.72:                      # i do izvucene (gore) i do Kriske na mestu
                return [smer * izv_m, Vector()]
            return []
        return [smer * izv_m * S(0.30, 0.35, u) + Vector((0, 0, -sp_m)) * S(0.35, 0.385, u)]

    bl = lambda a: Vector((a[0], -a[2], a[1]))
    pts, tgs = [bl(a) for a in data["points"]], [bl(a) for a in data["targets"]]
    keys = []
    for c in data["chapters"]:
        td = bl(c["tel_cilj"]) - bl(c["cilj"])
        for s_ in (c.get("stanice") or [c]):
            keys.append((s_["drzi"][0], s_["drzi"][1], td, c["tel_blize"]))
    keys.sort(key=lambda k: k[0])

    def tel(u, p, t):
        i = max([k for k in range(len(keys)) if keys[k][0] <= u] or [0])
        a, b = keys[i], keys[min(i + 1, len(keys) - 1)]
        w = S(a[1], b[0], u) if b is not a and u > a[1] else 0.0
        td = a[2].lerp(b[2], w)
        bz = a[3] + (b[3] - a[3]) * w
        t2 = t + td
        return t2 + (p - t) * bz, t2

    def cr(arr, x):                                     # tacka izmedju uzoraka (linearno, dovoljno gusto)
        j = min(int(x), len(arr) - 2)
        return arr[j].lerp(arr[j + 1], x - j)

    rez = {}
    for mod in ("desktop", "telefon"):
        najm, losi, prev = (9e9, None), [], None
        for k in range(0, (len(pts) - 1) * 4 + 1):
            x = k / 4
            u = x / (len(pts) - 1)
            p, t = cr(pts, x), cr(tgs, x)
            if mod == "telefon":
                p, t = tel(u, p, t)
            d = tree.find_nearest(p)[3]
            d = 9e9 if d is None else d
            for off in kriska_pomak(u):               # BVH Kriske je u njenim lokalnim koordinatama
                dk = ktree.find_nearest(p - (k0 + off))[3]
                d = min(d, dk if dk is not None else 9e9)
            kroz = False
            if prev is not None and (p - prev).length > 1e-6:
                dv = p - prev
                kroz = tree.ray_cast(prev, dv.normalized(), dv.length)[0] is not None
            if d < najm[0]:
                najm = (d, round(u, 4))
            if d < 0.2 or kroz:
                losi.append((round(u, 4), round(d, 3), kroz))
            prev = p
        rez[mod] = {"najmanje_m": round(najm[0], 3), "u": najm[1], "losi": losi[:12], "broj_losih": len(losi)}
    log("PROVERA PUTA (ray-cast, granica 0,2 m):", json.dumps(rez))
    return rez


# ================================================================ priprema geometrije
def ime_cvora(ob):
    nm = ob.name
    col = ob.users_collection[0].name if ob.users_collection else ""
    if col in ("Rezaci", "Kamera", "Svetla") or ob.type != "MESH":
        return None
    if col == "Kriska":
        return "Kriska"
    if col in ("Blok", "Naspram"):
        return nm.split("_")[0]
    if col in ("Ulica", "Drvece"):
        return "Tlo"
    if col in ("Lampe", "Tramvaj", "Figure"):
        return nm
    if col == "Dim":
        return nm
    return None


def provera_otvora():
    """Prostor Pekara_otvor mora biti prazan (enterijer ga puni): broji trouglove ciji je centar unutra."""
    ot = bpy.data.objects["Pekara_otvor"]
    tl = list(ot["tlocrt"])
    poly = list(zip(tl[0::2], tl[1::2]))
    z0, z1 = ot["z"]

    def unutra(p, eps=0.1):
        if not (z0 + eps < p.z < z1 - eps):
            return False
        for i in range(len(poly)):
            a, c = poly[i], poly[(i + 1) % len(poly)]
            if (c[0] - a[0]) * (p.y - a[1]) - (c[1] - a[1]) * (p.x - a[0]) < eps * math.hypot(c[0] - a[0], c[1] - a[1]):
                return False
        return True

    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        me = o.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n += sum(1 for t in me.loop_triangles if unutra(o.matrix_world @ t.center))
        o.evaluated_get(dg).to_mesh_clear()
    log(f"Pekara_otvor: {n} trouglova unutra (mora 0)")
    return n


def spoji_cvor(name, obs, mw):
    """Primenjeni modifikatori, spojeno u jedan objekat sa matricom mw (atributi i materijali po slotu)."""
    dg = bpy.context.evaluated_depsgraph_get()
    inv = mw.inverted()
    bm = bmesh.new()
    mats = []
    wl = bm.verts.layers.float.new("_wake")
    for ob in obs:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        me.transform(inv @ ob.matrix_world)
        at = me.attributes.get("_wake")
        wv = [0.0] * len(me.vertices)
        if at is not None and at.domain == "POINT":
            at.data.foreach_get("value", wv)
        slot = []
        for m in me.materials:
            if m not in mats:
                mats.append(m)
            slot.append(mats.index(m))
        vmap = [bm.verts.new(v.co) for v in me.vertices]
        for v, w in zip(vmap, wv):
            v[wl] = w
        for p in me.polygons:
            try:
                f = bm.faces.new([vmap[i] for i in p.vertices])
            except ValueError:                           # duplikat lica (preklapanje kutija): preskoci
                continue
            f.material_index = slot[p.material_index] if slot else 0
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(name, me)
    o.matrix_world = mw
    return o


def odvoji_zivo(o):
    """Lica sa zivim materijalom (emisija, providno) idu u poseban objekat <ime>_ziv (dete cvora)."""
    me = o.data
    zivi = [i for i, m in enumerate(me.materials) if m and m.name in ZIVO]
    if not zivi:
        return None
    bm = bmesh.new()
    bm.from_mesh(me)
    bz = bm.copy()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in zivi], context="FACES")
    bmesh.ops.delete(bz, geom=[f for f in bz.faces if f.material_index not in zivi], context="FACES")
    mz = me.copy()
    mz.name = o.name + "_ziv"
    bz.to_mesh(mz)
    bm.to_mesh(me)
    bm.free()
    bz.free()
    z = bpy.data.objects.new(o.name + "_ziv", mz)
    return z


def bvh_od(obs, isklj=("staklo",)):
    """Jedan BVH u svetskim koordinatama (providno staklo ne zaklanja)."""
    V, P = [], []
    for o in obs:
        me = o.data
        me.calc_loop_triangles()
        mw = o.matrix_world
        ok = [m is not None and m.name not in isklj for m in me.materials] or [True]
        base = len(V)
        V.extend(mw @ v.co for v in me.vertices)
        P.extend(tuple(base + i for i in t.vertices) for t in me.loop_triangles if ok[min(t.material_index, len(ok) - 1)])
    return BVHTree.FromPolygons(V, P, all_triangles=True, epsilon=0.0)


def mreza(bm, cell=1.5, thr=3.0):
    """Velika lica se seku u mrezu (cell m), da skriveni delovi (pod susedom, ispod trotoara) mogu da se obrisu."""
    big = {f for f in bm.faces if f.calc_area() > thr}
    if not big:
        return
    lo = Vector([min(v.co[i] for f in big for v in f.verts) for i in range(3)])
    hi = Vector([max(v.co[i] for f in big for v in f.verts) for i in range(3)])
    for ax in range(3):
        no = Vector((0, 0, 0))
        no[ax] = 1.0
        for k in range(int(math.floor(lo[ax] / cell)) + 1, int(math.ceil(hi[ax] / cell))):
            val = k * cell
            gf = [f for f in big if f.is_valid and min(v.co[ax] for v in f.verts) < val - 1e-3
                  and max(v.co[ax] for v in f.verts) > val + 1e-3]
            if not gf:
                continue
            ge = list({e for f in gf for e in f.edges})
            gv = list({v for f in gf for v in f.verts})
            res = bmesh.ops.bisect_plane(bm, geom=gv + ge + gf, plane_co=no * val, plane_no=no)
            for el in res["geom_cut"]:
                if isinstance(el, bmesh.types.BMEdge):
                    big.update(el.link_faces)
        big = {f for f in big if f.is_valid}


def obrisi_skriveno(o, tree, mw_tree=None, d_close=0.05, eps=0.004):
    """Brise lica koja niko ne vidi: uz susednu povrsinu (< d_close) ili unutar drugog tela (prvi pogodak je
    nalicje). Proverava se centar i tacke ka temenima; brise se samo ako su sve skrivene."""
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    mreza(bm)
    bm.normal_update()
    mw = o.matrix_world if mw_tree is None else mw_tree
    m3 = mw.to_3x3()
    dele = []
    for f in bm.faces:
        n = (m3 @ f.normal).normalized()
        c = mw @ f.calc_center_median()
        if n.z < -0.9 and c.z < -1.4:                # dno daske
            dele.append(f)
            continue
        smp = [c] + [c.lerp(mw @ v.co, 0.85) for v in f.verts[:8]]
        sakriveno = True
        for p in smp:
            hit, hn, _, dist = tree.ray_cast(p + n * eps, n, 200.0)
            if hit is None:
                sakriveno = False
                break
            if dist > d_close and hn.dot(n) <= 0:     # pogodak lica (ne nalicja) daleko: vidi se
                sakriveno = False
                break
        if sakriveno:
            dele.append(f)
    n_del = len(dele)
    bmesh.ops.delete(bm, geom=dele, context="FACES")
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), use_dissolve_boundaries=False,
                             verts=bm.verts[:], edges=bm.edges[:], delimit={"MATERIAL"})
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    return n_del


def pripremi():
    scene = bpy.context.scene
    provera_otvora()
    scene.frame_set(1)
    grupe = {}
    for ob in list(scene.objects):
        if ob.hide_render and not ob.name.startswith("Dim"):
            continue
        nm = ime_cvora(ob)
        if nm:
            grupe.setdefault(nm, []).append(ob)
    kol = bpy.data.collections.new("Grad")
    scene.collection.children.link(kol)
    cvorovi, zivi = {}, {}
    for nm, obs in grupe.items():
        if nm.startswith("Dim"):
            continue
        if nm == "Kriska":
            mw = bpy.data.objects["Kriska"].matrix_world.copy()
        elif nm in ("Tlo",) or nm in ATLAS or nm.startswith(("NS", "NZ")):
            mw = Matrix.Identity(4)
        else:
            mw = obs[0].matrix_world.copy()
        o = spoji_cvor(nm + "_novo", obs, mw)
        kol.objects.link(o)
        props = {}
        for s_ in obs:
            for k, v in s_.items():
                if k not in ("wake", "prozora") and not k.startswith("_"):
                    props.setdefault(k, v)
        wk = [(s_["wake"], s_["prozora"]) for s_ in obs if "wake" in s_ and s_.get("prozora", 0)]
        for k, v in props.items():
            o[k] = v
        if wk:
            o["prozora"] = sum(c for _, c in wk)
            o["wake"] = round(sum(w * c for w, c in wk) / o["prozora"], 4)
        cvorovi[nm] = o
    # dim: niske kugle (polozaj i velicina za cestice u motoru), bez bake-a
    dm = bpy.data.materials.new("Dim")
    dm.use_nodes = True
    pb = dm.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.84, 0.8, 0.76, 1)
    pb.inputs["Alpha"].default_value = 0.35
    dm.surface_render_method = "BLENDED"
    for nm, obs in grupe.items():
        if not nm.startswith("Dim"):
            continue
        s_ = obs[0]
        me = bpy.data.meshes.new(nm + "_novo")
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(dm)
        o = bpy.data.objects.new(nm + "_novo", me)
        o.matrix_world = s_.matrix_world.copy()
        kol.objects.link(o)
        cvorovi[nm] = o
    # stari objekti se brisu (svetla ostaju; deca svetla lampi gube roditelja, ali zadrzavaju polozaj)
    stari = {s_ for obs in grupe.values() for s_ in obs}
    for o in list(scene.objects):
        if o.type == "LIGHT" and o.parent in stari:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    for s_ in stari:
        bpy.data.objects.remove(s_, do_unlink=True)
    for o in list(scene.objects):
        if o.users_collection and o.users_collection[0].name == "Rezaci":
            bpy.data.objects.remove(o, do_unlink=True)
    for nm, o in cvorovi.items():
        o.name = nm
        o.data.name = nm
        z = odvoji_zivo(o) if not nm.startswith("Dim") else None
        if z:
            kol.objects.link(z)
            z.parent = o
            z.matrix_parent_inverse = Matrix.Identity(4)
            z.matrix_basis = Matrix.Identity(4)
            zivi[nm] = z
    # Pekara_otvor i Kriska props ostaju; empty Pekara_otvor ide u izvoz kao cvor
    # --- skrivena lica
    t = time.time()
    staticni = [o for nm, o in cvorovi.items() if not nm.startswith(POKRETNO + ("Dim",))]
    tree = bvh_od(staticni + [zivi[n] for n in zivi if not n.startswith(POKRETNO)])
    n_del = 0
    for nm, o in cvorovi.items():
        if nm.startswith("Dim"):
            continue
        if nm.startswith(POKRETNO):
            own = bvh_od([o] + ([zivi[nm]] if nm in zivi else []))
            n_del += obrisi_skriveno(o, own)
        else:
            n_del += obrisi_skriveno(o, tree)
    log(f"skrivena lica obrisana: {n_del} ({time.time() - t:.1f} s)")
    return cvorovi, zivi


# ================================================================ UV i bake
def atlas_za(nm):
    if nm in ATLAS:
        return ATLAS[nm]
    return 2


UV_SKALA = {"presek": 4.0, "unutra": 0.1}     # fix A: rez kriske (krajevi, ~60 m2) dobija 16x vise piksela,
                                              # zidovi "unutra" (iza zidova enterijera) skoro nista


def uv_presek(obs):
    """Ostrva UV-a sa materijalom iz UV_SKALA (vecina povrsine) se skaliraju oko svog centra, pa se atlas
    ponovo pakuje (pack_islands zadrzava odnos velicina ostrva)."""
    for o in obs:
        me = o.data
        bm = bmesh.new()
        bm.from_mesh(me)
        uvl = bm.loops.layers.uv["albedo"]
        bm.faces.ensure_lookup_table()
        roditelj = list(range(len(bm.faces)))

        def koren(i):
            while roditelj[i] != i:
                roditelj[i] = roditelj[roditelj[i]]
                i = roditelj[i]
            return i

        for e in bm.edges:
            lf = e.link_loops
            if len(lf) != 2:
                continue
            l1, l2 = lf
            # ista ivica u UV-u: l1 (v1 -> v2) i l2 (v2 -> v1)
            a1, b1 = l1[uvl].uv, l1.link_loop_next[uvl].uv
            a2, b2 = l2[uvl].uv, l2.link_loop_next[uvl].uv
            if (a1 - b2).length < 1e-6 and (b1 - a2).length < 1e-6:
                roditelj[koren(l1.face.index)] = koren(l2.face.index)
        ostrva = {}
        for f in bm.faces:
            ostrva.setdefault(koren(f.index), []).append(f)
        mats = [m.name if m else "" for m in me.materials]
        n_sk = {k: 0 for k in UV_SKALA}
        for fs in ostrva.values():
            pov = {}
            for f in fs:
                m = mats[f.material_index] if f.material_index < len(mats) else ""
                pov[m] = pov.get(m, 0.0) + f.calc_area()
            m = max(pov, key=pov.get)
            if m not in UV_SKALA or (m == "unutra" and o.name == "Kriska"):   # unutra Kriske se vidi kroz izlog
                continue
            k = UV_SKALA[m]
            uvs = [l[uvl].uv for f in fs for l in f.loops]
            c = sum((Vector(uv) for uv in uvs), Vector((0, 0))) / len(uvs)
            for f in fs:
                for l in f.loops:
                    l[uvl].uv = c + (l[uvl].uv - c) * k
            n_sk[m] += 1
        bm.to_mesh(me)
        bm.free()
        log(f"UV {o.name}: skalirana ostrva {n_sk}")
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.select_all(action="SELECT")
    bpy.ops.uv.pack_islands(udim_source="CLOSEST_UDIM", rotate=True, scale=True, margin_method="FRACTION",
                            margin=min(7.0 / S_FULL, 0.004))
    bpy.ops.object.mode_set(mode="OBJECT")


def uv_atlasi(cvorovi):
    sc = bpy.context.scene
    grupe = {}
    for nm, o in cvorovi.items():
        if nm.startswith("Dim"):
            continue
        a = atlas_za(nm)
        o["atlas"] = a
        grupe.setdefault(a, []).append(o)
        me = o.data
        while me.uv_layers:
            me.uv_layers.remove(me.uv_layers[0])
        me.uv_layers.new(name="albedo")
        me.uv_layers.new(name="lightmap")
        me.uv_layers.active = me.uv_layers["albedo"]
    for a, obs in sorted(grupe.items()):
        t = time.time()
        for o in sc.objects:
            o.select_set(False)
        for o in obs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = obs[0]
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), margin_method="FRACTION",
                                 island_margin=min(7.0 / S_FULL, 0.004), area_weight=0.0, correct_aspect=True,
                                 scale_to_bounds=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        if a == 0:
            uv_presek(obs)
        _b = np.empty(len(obs[0].data.loops) * 2, np.float32)
        obs[0].data.uv_layers["albedo"].data.foreach_get("uv", _b)
        if _b.max() > 1.001:                            # prevelika margina: smart_project ne spakuje ostrva
            raise RuntimeError(f"UV atlas {a} nije spakovan ({_b.max():.2f})")
        area = 0.0
        for o in obs:                                   # isti raspored i za lightmap
            me = o.data
            buf = np.empty(len(me.loops) * 2, np.float32)
            me.uv_layers["albedo"].data.foreach_get("uv", buf)
            me.uv_layers["lightmap"].data.foreach_get("uv", buf.copy())
            me.uv_layers["lightmap"].data.foreach_set("uv", buf)
            area += sum(p.area for p in me.polygons)
        log(f"UV atlas {a}: {len(obs)} cvorova, povrsina {area:.0f} m2, "
            f"~{math.sqrt(S_FULL * S_FULL * 0.6 / max(area, 1)):.1f} px/m ({time.time() - t:.1f} s)")
    return grupe


def svetlo(stanje):
    """Noc (kadar 1 + lampe) ili jutro. Prozori sa _wake su ugaseni u oba (prag -1)."""
    sc = bpy.context.scene
    ob = bpy.data.objects
    wn = sc.world.node_tree
    bgs = [n for n in wn.nodes if n.type == "BACKGROUND"]
    bg_cam, bg_amb = bgs[0], bgs[1]
    noc = stanje == "noc"
    for o in sc.objects:
        if o.type != "LIGHT":
            continue
        nm = o.name
        if nm.startswith("Lampa_") and nm.endswith("_svetlo"):
            o.hide_render = not noc
        elif nm == "Lampa_stola":
            o.hide_render = False
            o.data.energy = float(os.environ.get("KRUME_FILL", "9000")) if noc else 2500.0
            o.data.color = (1.0, 0.8, 0.6) if noc else (1.0, 0.93, 0.85)
        elif nm == "Pre_zore":
            o.hide_render = not noc
        elif nm == "Jutro_sunce":
            o.hide_render = noc
        elif "izlog" in nm or "tabla" in nm or nm in ("Vrata", "Pekara_unutra"):
            o.hide_render = False
            o["_e0"] = o.get("_e0", o.data.energy)
            o.data.energy = o["_e0"] * (1.0 if noc else 0.45)
    if "Jutro_sunce" not in ob:
        ld = bpy.data.lights.new("Jutro_sunce", "SUN")
        su = bpy.data.objects.new("Jutro_sunce", ld)
        sc.collection.objects.link(su)
        # nisko sunce s jugoistoka (iza kamere kadra 6 desno): greje juzne fasade i krovove, zapadne ostaju hladne
        su.rotation_euler = Vector((-0.62, 0.52, -0.42)).to_track_quat("-Z", "Y").to_euler()
        ld.energy = 3.2
        ld.color = (1.0, 0.78, 0.55)
        ld.angle = math.radians(6)
        su.hide_render = noc
    lm = bpy.data.materials.get("lampa")
    if lm:
        lm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0 if noc else 0.0
    tm = bpy.data.materials.get(PROZOR)
    if tm and "prag" in tm.node_tree.nodes:
        tm.node_tree.nodes["prag"].outputs[0].default_value = -1.0
    if noc:
        bg_amb.inputs["Color"].default_value = (0.0461, 0.0368, 0.0331, 1)     # #3d3633 (kit)
        bg_amb.inputs["Strength"].default_value = float(os.environ.get("KRUME_AMB", "0.9"))
        bg_cam.inputs["Strength"].default_value = 1.6
    else:
        bg_amb.inputs["Color"].default_value = (0.42, 0.52, 0.72, 1)           # hladno jutarnje nebo
        bg_amb.inputs["Strength"].default_value = 1.1
        bg_cam.inputs["Strength"].default_value = 4.0


def pripremi_materijale_za_bake(mats):
    """Metal, providnost i lak se iskljucuju: bake difuzne boje i svetla vazi i za zlato i limove."""
    for m in mats:
        if not m or not m.use_nodes or m.name in ZIVO:
            continue
        for n in m.node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                for k in ("Metallic", "Transmission Weight", "Coat Weight"):
                    if k in n.inputs and not n.inputs[k].is_linked:
                        n.inputs[k].default_value = 0.0


def spojena_kopija(obs):
    """Privremena spojena kopija (svetske koordinate, isti UV i materijali); originali se sakriju za bake."""
    sc = bpy.context.scene
    kop = []
    for o in obs:
        c = o.copy()
        c.data = o.data.copy()
        c.parent = None
        c.matrix_world = o.matrix_world.copy()
        sc.collection.objects.link(c)
        kop.append(c)
        o.hide_render = True
    with bpy.context.temp_override(active_object=kop[0], object=kop[0], selected_objects=kop,
                                   selected_editable_objects=kop):
        bpy.ops.object.join()
    kop[0].hide_render = False
    return kop[0]


def bake_atlas(a, obs, kind, size, samples):
    sc = bpy.context.scene
    img = bpy.data.images.new(f"grad-{kind}-{a}", size, size, alpha=True, float_buffer=True)
    img.generated_color = (0, 0, 0, 0)
    mats = {m for o in obs for m in o.data.materials if m}
    nodes = []
    for m in mats:
        nt = m.node_tree
        nd = nt.nodes.new("ShaderNodeTexImage")
        nd.image = img
        nt.nodes.active = nd
        nodes.append((nt, nd))
    sc.cycles.samples = samples
    stat = [o for o in obs if not o.name.startswith(POKRETNO[1:])]
    pokr = [o for o in obs if o.name.startswith(POKRETNO[1:])]
    pokr_svi = [o for o in sc.objects if o.name.startswith(POKRETNO[1:]) and o.type == "MESH"]
    t = time.time()
    for k, grupa in enumerate((stat, pokr)):
        if not grupa:
            continue
        for o in pokr_svi:                               # tramvaj i figure ne bacaju senku na statican deo
            o.hide_render = k == 0
        tmp = spojena_kopija(grupa)                      # Cycles peca objekat po objekat preko cele slike: jedan je brzi
        for o in sc.objects:
            o.select_set(False)
        tmp.select_set(True)
        bpy.context.view_layer.objects.active = tmp
        pf = {"COLOR"} if kind == "alb" else {"DIRECT", "INDIRECT"}
        bpy.ops.object.bake(type="DIFFUSE", pass_filter=pf, margin=max(2, size // 256), margin_type="EXTEND",
                            use_clear=(k == 0 or not stat), uv_layer="lightmap" if kind != "alb" else "albedo",
                            target="IMAGE_TEXTURES")
        bpy.data.meshes.remove(tmp.data)
        for o in grupa:
            o.hide_render = False
            if o.name.startswith(POKRETNO[1:]):
                o.hide_render = k == 0
    for o in pokr_svi:
        o.hide_render = False
    for nt, nd in nodes:
        nt.nodes.remove(nd)
    buf = np.empty(size * size * 4, np.float32)
    img.pixels.foreach_get(buf)
    bpy.data.images.remove(img)
    arr = buf.reshape(size, size, 4)
    np.savez_compressed(os.path.join(BAKE_DIR, f"grad-raw-{kind}-{a}.npz"), a=arr.astype(np.float16))
    log(f"BAKE {kind} atlas {a}: {size}px, {samples} smp, {time.time() - t:.1f} s")
    return arr


def bake_sve(grupe):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.use_denoising = False
    sc.render.bake.use_selected_to_active = False
    sm = int(os.environ.get("KRUME_BAKE_SAMPLES", "256"))
    for o in sc.objects:                               # dim (volumen) ne ucestvuje u bake-u
        if o.name.startswith("Dim"):
            o.hide_render = True
    mats = {m for o in sc.objects if o.type == "MESH" for m in o.data.materials if m}
    pripremi_materijale_za_bake(mats)
    vreme = {}
    for kind in ("alb", "noc", "dan"):
        t = time.time()
        if kind != "alb":
            svetlo(kind)
        for a, obs in sorted(grupe.items()):
            bake_atlas(a, obs, kind, S_FULL, 8 if kind == "alb" else sm)
        vreme[kind] = round(time.time() - t, 1)
    for o in sc.objects:
        if o.name.startswith("Dim"):
            o.hide_render = False
    sc["krume_bake_vreme"] = vreme
    log("BAKE vreme po vrsti (s):", vreme)


# ================================================================ teksture
def srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def upisi_webp(arr_rgb, path, q):
    h, w = arr_rgb.shape[:2]
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :3] = arr_rgb
    img.pixels.foreach_set(rgba.ravel())
    img.file_format = "WEBP"
    img.save(filepath=path, quality=q)
    bpy.data.images.remove(img)
    return os.path.getsize(path)


def pola(arr):
    h, w = arr.shape[:2]
    return arr.reshape(h // 2, 2, w // 2, 2, -1).mean(axis=(1, 3))


def teksture(atlasi):
    """Albedo (sRGB) u bake/ za GLB; lightmap-ovi u public/textures, kodirani (L/max)^(1/LM_GAMMA)."""
    os.makedirs(os.path.join(PUB, "textures"), exist_ok=True)
    raw = {(k, a): np.load(os.path.join(BAKE_DIR, f"grad-raw-{k}-{a}.npz"))["a"].astype(np.float32)
           for k in ("alb", "noc", "dan") for a in atlasi}
    info = {"gamma": LM_GAMMA}
    velicine = {}
    for k in ("noc", "dan"):
        lum = np.concatenate([raw[(k, a)][..., :3].max(axis=2)[raw[(k, a)][..., 3] > 0.5] for a in atlasi])
        mx = float(np.percentile(lum, 99.7))
        info[k] = {"max": round(mx, 4), "p50": round(float(np.percentile(lum, 50)), 4),
                   "p05": round(float(np.percentile(lum, 5)), 5)}
        for a in atlasi:
            enc = np.power(np.clip(raw[(k, a)][..., :3] / mx, 0, 1), 1 / LM_GAMMA)
            p = os.path.join(PUB, "textures", f"grad-{k}-{a}.webp")
            velicine[os.path.basename(p)] = upisi_webp(enc, p, 88)
            p = os.path.join(PUB, "textures", f"grad-{k}-{a}-m.webp")
            velicine[os.path.basename(p)] = upisi_webp(pola(enc), p, 85)
    for a in atlasi:
        al = srgb(raw[("alb", a)][..., :3])
        velicine[f"grad-alb-{a}.webp"] = upisi_webp(al, os.path.join(BAKE_DIR, f"grad-alb-{a}.webp"), 86)
        velicine[f"grad-alb-{a}-m.webp"] = upisi_webp(pola(al), os.path.join(BAKE_DIR, f"grad-alb-{a}-m.webp"), 82)
    log("lightmap info", info)
    log("teksture (B):", velicine)
    return info, velicine


# ================================================================ materijali za izvoz, GLB
def mat_atlas(name, img, a):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ("OUTPUT_MATERIAL",):
            nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "albedo"
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img
    nt.links.new(uv.outputs["UV"], tx.inputs["Vector"])
    nt.links.new(tx.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 1.0
    p.inputs["Metallic"].default_value = 0.0
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    m["atlas"] = a
    return m


def slika_albeda(a, mobil):
    p = os.path.join(BAKE_DIR, f"grad-alb-{a}{'-m' if mobil else ''}.webp")
    im = bpy.data.images.load(p, check_existing=True)
    im.colorspace_settings.name = "sRGB"
    return im


def postavi_slike(atlasi, mobil):
    for a in atlasi:
        for nm in (f"Atlas_{a}", f"Prozor_{a}"):
            for n in bpy.data.materials[nm].node_tree.nodes:
                if n.type == "TEX_IMAGE":
                    n.image = slika_albeda(a, mobil)


def dodeli_atlas_materijale(cvorovi, atlasi):
    """Posle bake-a: sva lica cvora dobijaju Atlas_N, prozori (staklo_tamno, nose _wake) Prozor_N."""
    for nm, o in cvorovi.items():
        if "atlas" not in o:
            continue
        a = o["atlas"]
        ma = bpy.data.materials.get(f"Atlas_{a}") or mat_atlas(f"Atlas_{a}", slika_albeda(a, False), a)
        mp = bpy.data.materials.get(f"Prozor_{a}") or mat_atlas(f"Prozor_{a}", slika_albeda(a, False), a)
        mp["prozor"] = True
        me = o.data
        idx = [1 if (m and m.name == PROZOR) else 0 for m in me.materials]
        mi = np.empty(len(me.polygons), np.int32)
        me.polygons.foreach_get("material_index", mi)
        new = np.array(idx, np.int32)[np.clip(mi, 0, len(idx) - 1)] if idx else np.zeros_like(mi)
        me.materials.clear()
        me.materials.append(ma)
        me.materials.append(mp)
        me.polygons.foreach_set("material_index", new)
        me.update()


def ziv_za_izvoz():
    """Staklo izloga: providno bez prelamanja (alpha), ostalo ostaje emisija iz kita."""
    lm = bpy.data.materials.get("lampa")                 # provera dana ih gasi; u GLB-u idu upaljene
    if lm:
        lm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    st = bpy.data.materials.get("staklo")
    if st:
        p = st.node_tree.nodes["Principled BSDF"]
        p.inputs["Transmission Weight"].default_value = 0.0
        p.inputs["Alpha"].default_value = 0.18
        p.inputs["Base Color"].default_value = (0.55, 0.62, 0.7, 1)
        st.surface_render_method = "BLENDED"


def izvoz(cvorovi, zivi, path, mobil):
    sc = bpy.context.scene
    for o in sc.objects:
        o.select_set(False)
    sel = list(cvorovi.values()) + list(zivi.values())
    ot = bpy.data.objects.get("Pekara_otvor")
    if ot:
        sel.append(ot)
    for o in sel:
        o.select_set(True)
    bpy.context.view_layer.objects.active = sel[0]
    sc.frame_set(1)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=False, export_yup=True,
        export_normals=False, export_texcoords=True, export_attributes=True, export_extras=True,
        export_vertex_color="NONE", export_materials="EXPORT", export_cameras=False, export_lights=False,
        export_animations=False, export_image_format="WEBP", export_image_quality=86 if not mobil else 82,
        export_image_add_webp=False, export_image_webp_fallback=False,
        export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
        export_draco_position_quantization=14, export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12, export_draco_generic_quantization=10)
    log(f"GLB {os.path.basename(path)}: {os.path.getsize(path) / 1024 / 1024:.2f} MB")


def trouglovi(cvorovi, zivi):
    out = {}
    for d in (cvorovi, zivi):
        for nm, o in d.items():
            o.data.calc_loop_triangles()
            out[o.name] = len(o.data.loop_triangles)
    return out


# ================================================================ provera: render iz tekstura
def gpu():
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for dv in prefs.devices:
            dv.use = True
        bpy.context.scene.cycles.device = "GPU"
    except Exception as e:
        print("GPU nije dostupan, CPU:", e)


def provera(cvorovi, info, atlasi):
    """Cycles render u kojem su atlas materijali samo emisija albedo * lightmap (iz izvezenih WebP fajlova),
    bez svetala: tako se vidi tacno ono sto shader na sajtu dobija."""
    sc = bpy.context.scene
    gpu()
    for o in sc.objects:
        if o.type == "LIGHT":
            o.hide_render = True
    stari = {o.name: [m for m in o.data.materials] for o in cvorovi.values() if "atlas" in o}
    cd = bpy.data.cameras.get("Provera") or bpy.data.cameras.new("Provera")
    cam = bpy.data.objects.get("Provera") or bpy.data.objects.new("Provera", cd)
    if cam.name not in sc.collection.objects:
        sc.collection.objects.link(cam)
    sc.camera = cam
    cd.clip_end = 600
    sc.cycles.samples = int(os.environ.get("KRUME_SAMPLES", "48"))
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    for kind, n in (("noc", 1), ("dan", 6)):
        pg, cj = bpy.data.objects[f"Pogl_{n}"], bpy.data.objects[f"Cilj_{n}"]
        cam.location = pg.location
        cam.rotation_euler = (cj.location - pg.location).to_track_quat("-Z", "Y").to_euler()
        cd.lens, cd.shift_x, cd.shift_y = pg["lens"], pg["shift_x"], pg["shift_y"]
        wn = sc.world.node_tree
        bgs = [nd for nd in wn.nodes if nd.type == "BACKGROUND"]
        bgs[0].inputs["Strength"].default_value = 1.6 if kind == "noc" else 4.0
        lm = bpy.data.materials.get("lampa")
        if lm:
            lm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0 if kind == "noc" else 0.0
        mats = {}
        for a in atlasi:
            m = bpy.data.materials.new(f"_provera_{kind}_{a}")
            m.use_nodes = True
            nt = m.node_tree
            nt.nodes.remove(nt.nodes["Principled BSDF"])
            out = nt.nodes["Material Output"]
            ua, ul = nt.nodes.new("ShaderNodeUVMap"), nt.nodes.new("ShaderNodeUVMap")
            ua.uv_map, ul.uv_map = "albedo", "lightmap"
            ta, tl = nt.nodes.new("ShaderNodeTexImage"), nt.nodes.new("ShaderNodeTexImage")
            ta.image = bpy.data.images.load(os.path.join(BAKE_DIR, f"grad-alb-{a}.webp"), check_existing=True)
            tl.image = bpy.data.images.load(os.path.join(PUB, "textures", f"grad-{kind}-{a}.webp"), check_existing=True)
            tl.image.colorspace_settings.name = "Non-Color"
            nt.links.new(ua.outputs["UV"], ta.inputs["Vector"])
            nt.links.new(ul.outputs["UV"], tl.inputs["Vector"])
            gm = nt.nodes.new("ShaderNodeGamma")
            gm.inputs["Gamma"].default_value = LM_GAMMA
            nt.links.new(tl.outputs["Color"], gm.inputs["Color"])
            mx = nt.nodes.new("ShaderNodeVectorMath")
            mx.operation = "MULTIPLY"
            nt.links.new(ta.outputs["Color"], mx.inputs[0])
            nt.links.new(gm.outputs["Color"], mx.inputs[1])
            em = nt.nodes.new("ShaderNodeEmission")
            nt.links.new(mx.outputs["Vector"], em.inputs["Color"])
            em.inputs["Strength"].default_value = info[kind]["max"]
            nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
            mats[a] = m
        for o in cvorovi.values():
            if "atlas" in o:
                o.data.materials[0] = mats[o["atlas"]]
                o.data.materials[1] = mats[o["atlas"]]
        sc.render.filepath = os.path.join(BAKE_DIR, f"grad-{kind}-provera.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        log(f"provera {kind}: {time.time() - t:.1f} s")
    for nm, ms in stari.items():
        o = bpy.data.objects[nm]
        for i, m in enumerate(ms):
            o.data.materials[i] = m


# ================================================================ glavni tok
def cvorovi_iz_scene():
    kol = bpy.data.collections["Grad"]
    cv, zv = {}, {}
    for o in kol.objects:
        if o.name.endswith("_ziv"):
            zv[o.name[:-4]] = o
        elif o.type == "MESH":
            cv[o.name] = o
    return cv, zv


# popravka krive pogl. 2 (talas 3) u vec sacuvanom kvart.blend: menja samo tacke 4-6 krive KameraPut
# i tel_blize poglavlja 5, kamere Pogl_N/Cilj_N i geometrija ostaju; "-- kamera sacuvaj" cuva kvart.blend
KRIVA_POGL_2 = [(-30.0, 18.0, 25.0), (-28.0, -22.0, 15.0), (4.0, -21.0, 7.0)]
TEL_BLIZE_5 = 0.7


def popravi_krivu():
    sp = bpy.data.objects["KameraPut"].data.splines[0]
    for bp, co in zip(sp.bezier_points[4:7], KRIVA_POGL_2):
        bp.co = Vector(co)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    bpy.data.objects["Pogl_5"]["tel_blize"] = TEL_BLIZE_5


if "kamera" in MY_ARGS:
    if "KameraPut" in bpy.data.objects:
        popravi_krivu()
        if "sacuvaj" in MY_ARGS:
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    if "KameraPut" not in bpy.data.objects:
        KRUME_WEB = True
        exec(compile(open(os.path.join(BL, "kvart.py")).read(), os.path.join(BL, "kvart.py"), "exec"), globals())
    kamera_json()
elif "izvoz" in MY_ARGS:
    cvorovi, zivi = cvorovi_iz_scene()
    atlasi = sorted({o["atlas"] for o in cvorovi.values() if "atlas" in o})
    info, vel = teksture(atlasi)
else:
    KRUME_WEB = True
    exec(compile(open(os.path.join(BL, "kvart.py")).read(), os.path.join(BL, "kvart.py"), "exec"), globals())
    log("kvart izgradjen (web)")
    kamera_json()
    cvorovi, zivi = pripremi()
    grupe = uv_atlasi(cvorovi)
    atlasi = sorted(grupe)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BAKE_DIR, "grad_bake.blend"))
    gpu()
    bake_sve(grupe)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BAKE_DIR, "grad_bake.blend"))
    info, vel = teksture(atlasi)

if "kamera" not in MY_ARGS:
    sc = bpy.context.scene
    sc["krume"] = {"lightmap_uv": "TEXCOORD_1 (Blender UV 'lightmap')", "albedo_uv": "TEXCOORD_0 (Blender UV 'albedo')",
                   "lightmap_gamma": LM_GAMMA, "noc_max": info["noc"]["max"], "dan_max": info["dan"]["max"],
                   "atlasi": len(atlasi),
                   "fajlovi": "textures/grad-{noc|dan}-{atlas}.webp, telefon: grad-{noc|dan}-{atlas}-m.webp"}
    dodeli_atlas_materijale(cvorovi, atlasi)
    provera(cvorovi, info, atlasi)
    ziv_za_izvoz()
    os.makedirs(os.path.join(PUB, "models"), exist_ok=True)
    for mobil, fn in ((False, "grad.glb"), (True, "grad-m.glb")):
        postavi_slike(atlasi, mobil)
        izvoz(cvorovi, zivi, os.path.join(PUB, "models", fn), mobil)
    tr = trouglovi(cvorovi, zivi)
    log("TRIS ukupno", sum(tr.values()), "najvise:", sorted(tr.items(), key=lambda kv: -kv[1])[:10])
    log("vreme bake-a:", dict(sc.get("krume_bake_vreme", {})))
if os.environ.get("KRUME_CUVAJ") != "1" and "kamera" not in MY_ARGS:     # sirovi bake (~100 MB) ne ostaje u repou
    for f in os.listdir(BAKE_DIR):
        if f.startswith("grad-raw-") and f.endswith(".npz"):
            os.remove(os.path.join(BAKE_DIR, f))
log("GOTOVO")
