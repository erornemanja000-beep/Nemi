# Krume, smer 3 "Ein Fenster brennt": staticni kadrovi za reduced motion / bez WebGL-a (talas 3, Z8).
# Po jedan kadar za svako poglavlje iz mape skrola (studio/pekara/skice/mapa-skrola.md), u dva formata:
#   wide  16:10, 1600x1000, kamera Pogl_N (shift_x/shift_y: jedna strana mirna za tekst)
#   hoch   9:16,  900x1600, tel_cilj / tel_blize / tel_shift_y sa Pogl_N (tekst na dnu kadra)
# Ulaz: kvart.blend (otvara se, ne cuva se) + kolekcija "Enterijer" iz enterijer.blend (append) za 2-5.
# Poglavlja 4 i 5 gledaju sa Stanica_4 / Stanica_5 iz enterijera (kao kamera.json u bake_izvoz.py).
# Izlaz: studio/pekara/blender/kadrovi/kadar-<N>-<wide|hoch>.png, pa pekara/public/frames/kadar-<N>-<oblik>.webp
# (Blender-ov WebP; kvalitet se spusta dok fajl ne stane u granicu: hoch 150 KB, wide 220 KB).
# Pokretanje (iz ovog foldera):
#   Blender -b -P kadrovi.py                    (svi kadrovi: 1 2 3 4 5 6 7 7b, oba formata, pa WebP)
#   Blender -b -P kadrovi.py -- 3 7b            (samo izabrana poglavlja)
#   Blender -b -P kadrovi.py -- 4 hoch          (samo jedan format)
#   Blender -b -P kadrovi.py -- webp            (bez rendera: samo WebP iz postojecih PNG)
# Okruzenje: KRUME_SAMPLES (96), KRUME_RES (procenat, 100), KRUME_PREFIX (folder za probe umesto kadrovi/;
# uz njega se WebP ne pise).

import bpy, math, os, sys, time
from mathutils import Vector

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PNG_DIR = os.environ.get("KRUME_PREFIX") or os.path.join(HERE, "kadrovi")
WEBP_DIR = os.path.join(ROOT, "pekara", "public", "frames")
ENTERIJER = os.path.join(HERE, "enterijer.blend")
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = int(os.environ.get("KRUME_SAMPLES", "96"))
GRANICA = {"hoch": 150 * 1024, "wide": 220 * 1024}
OBLICI = {"wide": (1600, 1000), "hoch": (900, 1600)}
SVA = ["1", "2", "3", "4", "5", "6", "7", "7b"]
os.makedirs(PNG_DIR, exist_ok=True)


def hexc(h):
    """#rrggbb u linearni RGBA (kao u kitu)."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def webp(png, path, granica):
    """PNG -> WebP. Kvalitet od 90 nanize dok fajl ne stane u granicu (dither iz rendera ostaje, nema stepenica).
    Image.save(quality=) za WebP pise bez gubitka, pa ide save_render sa posebnom scenom (Standard, bez AgX-a:
    PNG je vec tone-mapovan)."""
    sc = bpy.data.scenes.get("webp") or bpy.data.scenes.new("webp")
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.dither_intensity = 0.0
    st = sc.render.image_settings
    st.file_format = "WEBP"
    st.color_mode = "RGB"
    img = bpy.data.images.load(png)
    for q in (90, 86, 82, 78, 74, 70, 65, 60, 55, 50):
        st.quality = q
        img.save_render(path, scene=sc)
        if os.path.getsize(path) <= granica:
            break
    bpy.data.images.remove(img)
    return q, os.path.getsize(path)


def svi_webp(izbor):
    os.makedirs(WEBP_DIR, exist_ok=True)
    for n in izbor:
        for ob_ in OBLICI:
            png = os.path.join(PNG_DIR, f"kadar-{n}-{ob_}.png")
            if not os.path.exists(png):
                print(f"WEBP nema {png}")
                continue
            q, sz = webp(png, os.path.join(WEBP_DIR, f"kadar-{n}-{ob_}.webp"), GRANICA[ob_])
            print(f"WEBP kadar-{n}-{ob_}.webp: q {q}, {sz / 1024:.0f} KB")


IZBOR = [a for a in ARGS if a in SVA] or SVA
FORMATI = [a for a in ARGS if a in OBLICI] or list(OBLICI)
if "webp" in ARGS:
    svi_webp(IZBOR)
    sys.exit(0)

# ---------------------------------------------------------------- scena: kvart + enterijer
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "kvart.blend"))
bpy.context.preferences.filepaths.save_version = 0        # kvart.blend se ne cuva, ali ni slucajno .blend1
scene = bpy.context.scene
OB = bpy.data.objects

with bpy.data.libraries.load(ENTERIJER, link=False) as (src, dst):
    dst.collections = ["Enterijer"]
    dst.objects = ["Stanica_4", "Stanica_5"]
C_ENT = dst.collections[0]
scene.collection.children.link(C_ENT)
STANICA = {}
for o in dst.objects:                       # samo polozaj i cilj; prazni objekti se ne linkuju u scenu
    STANICA[int(o.name[-1])] = (o.location.copy(), Vector(o["cilj"]), float(o["lens"]))
    bpy.data.objects.remove(o)
TESTO = OB["Testo"].data.shape_keys.key_blocks
ZAR = OB["Svetlo_zar"]
HLEB = {o.name: (o.location.copy(), o.scale.copy()) for o in C_ENT.all_objects if o.name.startswith("Hleb_")}

# render (GPU, AgX kao u kitu); preference se ne cuvaju u .blend, pa se biraju ponovo
cy = scene.cycles
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = True
    cy.device = "GPU"
except Exception as e:
    print("GPU nije dostupan, CPU:", e)
cy.samples = SAMPLES
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.03
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
scene.render.resolution_percentage = int(os.environ.get("KRUME_RES", "100"))
scene.render.dither_intensity = 1.0               # sum preko nocnih gradijenata: bez stepenica u WebP-u
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.image_settings.color_depth = "8"

kam = scene.camera
cd = kam.data
WN = scene.world.node_tree
BG_CAM, BG_AMB = WN.nodes["Background"], WN.nodes["Background.001"]
RAMP = WN.nodes["Color Ramp"].color_ramp.elements
PRAG = bpy.data.materials["staklo_tamno"].node_tree.nodes["prag"].outputs[0]
LAMPA_MAT = bpy.data.materials["lampa"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
SVETLA = {o.name: o.data.energy for o in OB if o.type == "LIGHT"}
IZLOG = [n for n in SVETLA if "izlog" in n or "tabla" in n or n == "Vrata"]

# jutarnje sunce kao "dan" u bake_izvoz.py: nisko, toplo, s jugoistoka
ld = bpy.data.lights.new("Jutro_sunce", "SUN")
SUNCE = bpy.data.objects.new("Jutro_sunce", ld)
scene.collection.objects.link(SUNCE)
SUNCE.rotation_euler = Vector((-0.62, 0.52, -0.42)).to_track_quat("-Z", "Y").to_euler()
ld.energy, ld.color, ld.angle = 3.2, (1.0, 0.78, 0.55), math.radians(6)

# nebo (ono sto kamera vidi): horizont i zenit po dobu
# (kamera kadrova gleda nadole, pa se u kadru vidi uglavnom boja horizonta)
NEBO = {"noc": ("#1c2639", "#07090f"), "pre_zore": ("#26314a", "#0a0d16"), "zora": ("#a89aa0", "#56709c"),
        "jutro": ("#d9e2e8", "#7d9fca"), "vece": ("#33283a", "#0e1020")}
# zora je tamnija od jutra: sunce i nebo slabiji, da upaljeni prozori (talas) i dalje svetle
DAN = {"zora": dict(sunce=1.6, amb=0.55, sto=1200.0), "jutro": dict(sunce=3.2, amb=1.1, sto=2500.0)}


def svetlo(doba, lampe, izlog=1.0, unutra=True):
    """doba: noc | pre_zore | vece (noc iz kita) ili zora | jutro (dan iz bake_izvoz.py)."""
    dan = doba in ("zora", "jutro")
    for n, e in SVETLA.items():
        o = OB[n]
        if n.startswith("Lampa_") and n.endswith("_svetlo"):
            o.hide_render = not lampe
        elif n == "Lampa_stola":
            o.data.energy = DAN[doba]["sto"] if dan else e
            o.data.color = (1.0, 0.93, 0.85) if dan else (1.0, 0.8, 0.6)
        elif n == "Pre_zore":
            o.hide_render = dan
        elif n in IZLOG:
            o.hide_render = izlog <= 0
            o.data.energy = e * izlog
        elif n == "Pekara_unutra":                  # svetli praznu sobu; kad je enterijer tu, svetla su njegova
            o.hide_render = not unutra
    SUNCE.hide_render = not dan
    SUNCE.data.energy = DAN[doba]["sunce"] if dan else 0.0
    LAMPA_MAT.default_value = 2.0 if lampe else 0.0
    h, z = NEBO[doba]
    RAMP[0].color, RAMP[1].color = hexc(h), hexc(z)
    if dan:
        BG_AMB.inputs["Color"].default_value = (0.42, 0.52, 0.72, 1)        # hladno jutarnje nebo
        BG_AMB.inputs["Strength"].default_value = DAN[doba]["amb"]
        BG_CAM.inputs["Strength"].default_value = 1.0
    else:
        BG_AMB.inputs["Color"].default_value = (0.0461, 0.0368, 0.0331, 1)  # #3d3633 (kit)
        BG_AMB.inputs["Strength"].default_value = 0.9
        BG_CAM.inputs["Strength"].default_value = 1.6


def sjaj(on):
    """Bloom iz kompozitora (kao kadar peci u enterijer.py): zar dobija oreol."""
    scene.compositing_node_group = None
    if not on:
        return
    try:
        ng = bpy.data.node_groups.get("Sjaj_zara") or bpy.data.node_groups.new("Sjaj_zara", "CompositorNodeTree")
        ng.nodes.clear()
        if not ng.interface.items_tree:
            ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Bloom"
        gl.inputs["Threshold"].default_value = 0.8
        gl.inputs["Strength"].default_value = 0.7
        gl.inputs["Size"].default_value = 0.6
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        scene.compositing_node_group = ng
    except Exception as e:
        print("Sjaj (glare) nije uspeo:", e)


def hlebovi(veliki):
    """Poglavlje 5: hlebovi 1,4x i razmaknuti po pultu, da se na kadru citaju (etikete idu uz njih)."""
    for i, (nm, (loc, sc)) in enumerate(sorted(HLEB.items())):
        o = OB[nm]
        o.location, o.scale = loc.copy(), sc.copy()
        if veliki:
            o.location.x = 2.76 + 0.36 * i
            o.scale = sc * 1.4


def kadar(n, oblik, fstop=None, izmena=None):
    """Kamera kao kadar() u kvart.py; za 4 i 5 polozaj i cilj sa Stanica_N iz enterijera.
    izmena: dict za kadar gde Pogl_N ne pokazuje ono sto alt opisuje (p, c, lens, blize, sx, sy)."""
    pe = OB[f"Pogl_{n}"]
    tel = oblik == "hoch"
    iz = izmena or {}
    if n in STANICA:
        p, c, lens = STANICA[n]
    else:
        p, c, lens = pe.location.copy(), OB[f"Cilj_{n}"].location.copy(), pe["lens"]
    p, c = Vector(iz.get("p", p)), Vector(iz.get("c", c))
    cilj = Vector(iz.get("tel_cilj", pe["tel_cilj"])) if tel else c
    loc = cilj + (p - c) * (iz.get("blize", pe["tel_blize"]) if tel else 1.0)
    kam.location = loc
    kam.rotation_euler = (cilj - loc).to_track_quat("-Z", "Y").to_euler()
    cd.lens = iz.get("lens", lens)
    cd.sensor_fit = "AUTO"
    cd.clip_start = 0.02 if n in STANICA else 0.1
    cd.shift_x = 0.0 if tel else iz.get("sx", pe["shift_x"])
    cd.shift_y = iz.get("sy", pe["tel_shift_y"]) if tel else iz.get("sy", pe["shift_y"])
    cd.dof.use_dof = fstop is not None
    if fstop:                                       # lazni tilt-shift: fokus na pekaru
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = (Vector((1.5, 1.5, 4.0)) - loc).length
    scene.render.resolution_x, scene.render.resolution_y = OBLICI[oblik]


def stanje(frame, enterijer=False, testo=(0.0, 0.0), zar=80.0, ekspozicija=0.0, tram=False, prag=-1.0):
    scene.frame_set(frame)                          # Kriska: 1 na mestu, 40 izvucena, 70 spustena; vrata peci 1-40
    C_ENT.hide_render = not enterijer
    TESTO["mesenje"].value, TESTO["naraslo"].value = testo
    ZAR.data.energy = zar
    scene.view_settings.exposure = ekspozicija
    OB["Tramvaj"].hide_render = not tram
    PRAG.default_value = prag                       # prozori sa _wake < prag svetle (talas iz pekare)


# (svetlo, stanje, kadar wide, kadar hoch) po poglavlju; hoch bez DOF-a (mapa skrola: telefon bez DOF-a)
POGLAVLJA = {
    "1": dict(n=1, svetlo=dict(doba="noc", lampe=False), st=dict(frame=1), fstop=0.04),
    "2": dict(n=2, svetlo=dict(doba="pre_zore", lampe=True), st=dict(frame=1, enterijer=True, tram=True)),
    # fix A: izvucena kriska spreda-desno, da se rez (mrvica i kora) vidi, a iza nje otvorena pekara;
    # hoch dalje (figura ispred izloga ceo u kadru, ne na ivici)
    "3": dict(n=3, wide=dict(p=(13.6, -8.6, 2.4), c=(6.2, -1.2, 3.3)),
              hoch=dict(p=(12.8, -9.5, 2.3), c=(6.6, -0.5, 2.9), tel_cilj=(6.6, -0.5, 2.9), blize=1.0, sy=-0.06),
              svetlo=dict(doba="noc", lampe=True, unutra=False),
              st=dict(frame=40, enterijer=True, testo=(0.4, 0.0), zar=220.0, ekspozicija=0.3)),
    # kadar pomeren udesno da se vide otvorena vrata peci (na stanici su na samoj ivici)
    "4": dict(n=4, wide=dict(sx=0.1), hoch=dict(tel_cilj=(7.4, 3.6, 1.1), lens=22), svetlo=dict(doba="noc", lampe=True, unutra=False), sjaj=True,
              st=dict(frame=70, enterijer=True, testo=(0.0, 1.0), zar=220.0, ekspozicija=0.6)),
    # blize pultu nego Stanica_5, u visini hlebova; hoch odozgo i sire (uzak kadar), hlebovi u gornjoj polovini
    "5": dict(n=5, wide=dict(p=(3.3, 2.25, 1.55), c=(3.3, 3.6, 1.08), lens=28),
              hoch=dict(p=(3.3, 2.2, 1.8), c=(3.3, 3.6, 1.05), lens=24, tel_cilj=(3.3, 3.5, 1.0), blize=1.1, sy=-0.12),
              svetlo=dict(doba="noc", lampe=True, unutra=False), hleb=True,
              st=dict(frame=70, enterijer=True, zar=80.0, ekspozicija=0.6)),
    "6": dict(n=6, svetlo=dict(doba="zora", lampe=False, izlog=0.45), st=dict(frame=1, tram=True, prag=0.9),
              fstop=0.04),
    "7": dict(n=7, svetlo=dict(doba="jutro", lampe=False, izlog=0.45), st=dict(frame=1, tram=True), fstop=0.04),
    "7b": dict(n=7, svetlo=dict(doba="vece", lampe=True), st=dict(frame=1), fstop=0.04),
}

VREME = {}
for key in IZBOR:
    d = POGLAVLJA[key]
    svetlo(**d["svetlo"])
    stanje(**d["st"])
    hlebovi(d.get("hleb", False))
    sjaj(d.get("sjaj", False))
    for oblik in FORMATI:
        tel = oblik == "hoch"
        kadar(d["n"], oblik, fstop=None if tel else d.get("fstop"), izmena=d.get(oblik))
        scene.render.filepath = os.path.join(PNG_DIR, f"kadar-{key}-{oblik}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        VREME[f"{key}-{oblik}"] = time.time() - t
        print(f"RENDER kadar-{key}-{oblik}.png: {VREME[f'{key}-{oblik}']:.1f} s")

if not os.environ.get("KRUME_PREFIX"):
    svi_webp(IZBOR)
print("VREME", {k: round(v) for k, v in VREME.items()}, f"ukupno {time.time() - T0:.0f} s")
