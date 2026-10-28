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
#   Blender -b -P kadrovi.py -- foto 3          (foto proba: proba-foto/<N>-<wide|hoch>.png, bez WebP-a)
# "foto" (krug 3, Z1): hoch je 720x1440 sa vodoravnim uglom kadra 9:16 (kao camera.js), rez kuce je zid od cigle
# sa malterom i Dippelbaum tavanica (umesto mrvice), enterijer dobija foto materijale kita, malo DOF-a.
# Render je u oba nacina kao foto kit (krug 2): samo Metal, seed 7, adaptivno 0,02, OIDN sa albedo + normal.
# Svaki Blender ide preko render_red.sh (jedan render u isto vreme): ./render_red.sh -b -P kadrovi.py -- foto 3
# Okruzenje: KRUME_SAMPLES (96, foto 192), KRUME_RES (procenat, 100), KRUME_PREFIX (folder za probe umesto
# kadrovi/; uz njega se WebP ne pise), KRUME_WEBP_DIR (umesto pekara/public/frames, za proveru),
# KRUME_HOCH_SY (foto hoch: dodatni shift_y), KRUME_FSTOP (foto: f-broj, 0 = bez DOF-a).

import bpy, math, os, sys, time
from mathutils import Vector

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
FOTO = "foto" in ARGS and "webp" not in ARGS
PNG_DIR = os.environ.get("KRUME_PREFIX") or os.path.join(HERE, "proba-foto" if FOTO else "kadrovi")
WEBP_DIR = os.environ.get("KRUME_WEBP_DIR") or os.path.join(ROOT, "pekara", "public", "frames")
ENTERIJER = os.path.join(HERE, "enterijer.blend")
SAMPLES = int(os.environ.get("KRUME_SAMPLES", "192" if FOTO else "96"))
GRANICA = {"hoch": 150 * 1024, "wide": 220 * 1024}
OBLICI = {"wide": (1600, 1000), "hoch": (900, 1600)}
if FOTO:
    OBLICI["hoch"] = (720, 1440)
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
        dv.use = dv.type == "METAL"           # samo GPU: CPU uz GPU na M1 usporava
    cy.device = "GPU"
except Exception as e:
    print("GPU nije dostupan, CPU:", e)
cy.samples = SAMPLES
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02                      # kao foto kit (krug 2): isti seed, kadrovi se ne "pomeraju"
cy.seed, cy.use_animated_seed = 7, False
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
cy.denoising_prefilter = "ACCURATE"
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
# foto kit (krug 2): "dan" pretapa noc (soba + HDRI_noc + Nebo_amb) u dan (konigsallee za svetlo, Sky za kameru)
W_DAN = WN.nodes["dan"].outputs[0] if "dan" in WN.nodes else None
W_JACINA = {n: WN.nodes[n].inputs["Strength"].default_value
            for n in ("HDRI_noc", "Nebo_amb", "HDRI_dan", "Nebo_dan") if n in WN.nodes}
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
    if W_DAN:
        # jutro i zora: nocni HDRI i hladno nebo ugaseni, dan = 1 (konigsallee); zora slabija kao gore (amb)
        W_DAN.default_value = 1.0 if dan else 0.0
        k = DAN[doba]["amb"] / DAN["jutro"]["amb"] if dan else 1.0
        for n, e in W_JACINA.items():
            noc_cvor = n in ("HDRI_noc", "Nebo_amb")
            WN.nodes[n].inputs["Strength"].default_value = (0.0 if dan else e) if noc_cvor else e * k


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


# ---------------------------------------------------------------- foto: rez kao prava prepolovljena maketa
# Krug 3 (Z1): umesto mrvice rez pokazuje sta je u zidu i tavanici gruenderzeit kuce. Zid: cigla sa fugama
# (brick_wall_006), spolja i iznutra kora maltera ~3 cm (AO "iznutra" nalazi ivicu reza, kao kora u kvart.py).
# Tavanice (Plafon iz enterijera): odozdo malter, Dippelbaum grede (godovi na celu grede, fuge), nasip, daske.
# Pod: beton, estrih, plocice. Tavanice po svetskom z (enterijer stoji), zid po koordinatama objekta (Kriska se mice).
TEKS = os.path.join(HERE, "teksture")
IZ_KITA = ["daska", "drvo_radnja", "metal", "staklo", "hleb", "trotoar", "ivicnjak"]   # kao u enterijer.py


def _m(nt, op, a, b=None, c=None):
    """Math cvor; a, b, c su broj ili izlaz."""
    nd = nt.nodes.new("ShaderNodeMath")
    nd.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            nd.inputs[i].default_value = x
        else:
            nt.links.new(x, nd.inputs[i])
    return nd.outputs[0]


def _mr(nt, val, od, do):
    """0 kod od, 1 kod do (smoothstep, odseceno)."""
    nd = nt.nodes.new("ShaderNodeMapRange")
    nd.interpolation_type = "SMOOTHSTEP"
    nd.inputs["From Min"].default_value, nd.inputs["From Max"].default_value = od, do
    nt.links.new(val, nd.inputs["Value"])
    return nd.outputs["Result"]


def _mix(nt, fac, a, b, blend="MIX"):
    nd = nt.nodes.new("ShaderNodeMix")
    nd.data_type, nd.blend_type = "RGBA", blend
    for sock, x in (("Factor", fac), ("A", a), ("B", b)):
        if isinstance(x, str):
            nd.inputs[sock].default_value = hexc(x)
        elif isinstance(x, (int, float)):
            nd.inputs[sock].default_value = x
        else:
            nt.links.new(x, nd.inputs[sock])
    return nd.outputs["Result"]


def _rampa(nt, fac, boje):
    r = nt.nodes.new("ShaderNodeValToRGB")
    el = r.color_ramp.elements
    for i, (pos, h) in enumerate(boje):
        e = el[i] if i < len(el) else el.new(pos)
        e.position, e.color = pos, hexc(h)
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def _sum(nt, co, scale, detail=3.0):
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nt.links.new(co, nz.inputs["Vector"])
    return nz.outputs["Fac"]


def _slika(nt, fajl, co, boja=True):
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.projection, tx.projection_blend = "BOX", 0.2
    tx.image = bpy.data.images.load(os.path.join(TEKS, fajl), check_existing=True)
    if not boja:
        tx.image.colorspace_settings.name = "Non-Color"
    nt.links.new(co, tx.inputs["Vector"])
    return tx


def _novi(ime):
    m = bpy.data.materials.new(ime)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def _zavrsi(nt, p, boja, visina, rough=0.9, jacina=0.5):
    """Prasina od testere preko svega (krupne mrlje), bump iz visine."""
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    prl = _m(nt, "MULTIPLY_ADD", _sum(nt, co, 2.5, 5.0), -0.3, 1.12)
    nt.links.new(_mix(nt, 1.0, boja, prl, "MULTIPLY"), p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = jacina
    bp.inputs["Distance"].default_value = 0.01
    nt.links.new(visina, bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])


def mat_rez_zid():
    m, nt, p = _novi("rez_zid_foto")
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / 2.2, 1 / 2.2, 1 / 2.6)     # cigla ~21 x 7 cm (stari format, sa fugom)
    nt.links.new(co, mp.inputs["Vector"])
    dif = _slika(nt, "brick_wall_006/brick_wall_006_diff_2k.jpg", mp.outputs["Vector"])
    disp = _slika(nt, "brick_wall_006/brick_wall_006_disp_2k.png", mp.outputs["Vector"], boja=False)
    hs = nt.nodes.new("ShaderNodeHueSaturation")          # sveze presecena cigla: malo tamnija, manje narandzasta
    hs.inputs["Saturation"].default_value = 0.8
    hs.inputs["Value"].default_value = 0.85
    nt.links.new(dif.outputs["Color"], hs.inputs["Color"])
    # kora maltera: AO "iznutra" (samo sopstveni objekat) pada ispod 1 samo blizu ivice reza (~3 cm)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inside, ao.only_local, ao.samples = True, True, 16
    ao.inputs["Distance"].default_value = 0.07
    wob = _m(nt, "MULTIPLY_ADD", _sum(nt, co, 14.0), 0.06, ao.outputs["AO"])
    malt = _mr(nt, wob, 0.97, 0.92)
    malter = _rampa(nt, _sum(nt, co, 7.0, 4.0), [(0.3, "#b9ae9c"), (0.7, "#d3c9b8")])
    boja = _mix(nt, malt, hs.outputs["Color"], malter)
    vis = _m(nt, "MULTIPLY", disp.outputs["Color"], _m(nt, "SUBTRACT", 1.0, malt))
    _zavrsi(nt, p, boja, vis, rough=0.92, jacina=0.6)
    return m


def mat_rez_ploca(pod=False):
    """Presek tavanice (Plafon: 4,10-4,52 i 7,80-8,10) ili poda (Pod: -0,10-0,12), slojevi po svetskom z."""
    m, nt, p = _novi("rez_pod_foto" if pod else "rez_tavanica_foto")
    g = nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(g, sep.inputs["Vector"])
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    if pod:
        zl = _m(nt, "ADD", z, 0.1)
        beton = _rampa(nt, _sum(nt, co, 9.0, 5.0), [(0.35, "#5e5a54"), (0.65, "#77726a")])
        estrih = _rampa(nt, _sum(nt, co, 20.0, 3.0), [(0.4, "#8e887d"), (0.6, "#a29b8f")])
        boja = _mix(nt, _mr(nt, zl, 0.155, 0.16), beton, estrih)
        boja = _mix(nt, _mr(nt, zl, 0.2, 0.203), boja, "#4a3b30")                    # plocice
        vis = _m(nt, "MULTIPLY", _sum(nt, co, 40.0, 2.0), 0.3)
        _zavrsi(nt, p, boja, vis, rough=0.9, jacina=0.3)
        return m
    gore = _m(nt, "GREATER_THAN", z, 6.0)
    zl = _m(nt, "SUBTRACT", z, _m(nt, "MULTIPLY_ADD", gore, 3.7, 4.1))   # od dna tavanice
    h = _m(nt, "MULTIPLY_ADD", gore, -0.12, 0.42)                         # debljina: 0,42 / 0,30
    zt = _m(nt, "SUBTRACT", h, zl)                                        # do vrha (pod sprata)
    # grede: po 25 cm jedna do druge (Dippelbaum), koordinata duz reza je x - y (ravni y, x i x + y = konst.)
    s_ = _m(nt, "DIVIDE", _m(nt, "SUBTRACT", x, y), 0.25)
    u = _m(nt, "FRACT", s_)
    b = _m(nt, "FLOOR", s_)
    zc = _m(nt, "SUBTRACT", zl, _m(nt, "MULTIPLY_ADD", h, 0.5, -0.045))  # sredina grede (0,03 do h - 0,12)
    cv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(_m(nt, "MULTIPLY", _m(nt, "SUBTRACT", u, 0.5), 0.25), cv.inputs["X"])
    nt.links.new(zc, cv.inputs["Y"])
    nt.links.new(_m(nt, "MULTIPLY", b, 3.17), cv.inputs["Z"])
    wv = nt.nodes.new("ShaderNodeTexWave")                 # godovi na celu grede
    wv.wave_type, wv.rings_direction = "RINGS", "Z"
    wv.inputs["Scale"].default_value = 14.0
    wv.inputs["Distortion"].default_value = 6.0
    wv.inputs["Detail"].default_value = 3.0
    nt.links.new(cv.outputs["Vector"], wv.inputs["Vector"])
    wn_ = nt.nodes.new("ShaderNodeTexWhiteNoise")
    wn_.noise_dimensions = "1D"
    nt.links.new(b, wn_.inputs["W"])
    # godovi tihi (ne smeju da se citaju kao sara), razlika po gredi jaca od godova
    drvo = _rampa(nt, _m(nt, "MULTIPLY_ADD", wv.outputs["Fac"], 0.22, _m(nt, "MULTIPLY", wn_.outputs["Value"], 0.6)),
                  [(0.0, "#4e3320"), (0.5, "#6b4a2f"), (1.0, "#83603f")])
    drvo = _mix(nt, _m(nt, "MULTIPLY", _sum(nt, co, 25.0, 6.0), 0.5), drvo, "#3a2618")      # pukotine i prljavstina
    fuga = _mr(nt, _m(nt, "MULTIPLY_ADD", _sum(nt, co, 30.0), 0.02, _m(nt, "MINIMUM", u, _m(nt, "SUBTRACT", 1.0, u))),
               0.02, 0.04)                                                    # 0 u fugi (nejednake grede)
    drvo = _mix(nt, fuga, "#1f150e", drvo)
    nasip = _rampa(nt, _sum(nt, co, 60.0, 2.0), [(0.35, "#3e352e"), (0.65, "#62574b")])
    daske = _rampa(nt, _sum(nt, cv.outputs["Vector"], 3.0, 6.0), [(0.3, "#7c5a3a"), (0.7, "#9a7650")])
    malter = _rampa(nt, _sum(nt, co, 9.0, 4.0), [(0.3, "#c4bbab"), (0.7, "#d9d1c2")])
    boja = _mix(nt, _mr(nt, zl, 0.028, 0.034), malter, drvo)
    boja = _mix(nt, _mr(nt, zt, 0.122, 0.118), boja, nasip)
    boja = _mix(nt, _mr(nt, zt, 0.047, 0.043), boja, "#2a1d14")                 # slepi pod (tanka tamna linija)
    boja = _mix(nt, _mr(nt, zt, 0.04, 0.037), boja, daske)
    vis = _m(nt, "MULTIPLY", fuga, 0.5)
    _zavrsi(nt, p, boja, vis, rough=0.85, jacina=0.5)
    return m


def foto_materijali():
    """Rez kuce, Kriske i enterijera dobija foto rez; materijali kita u enterijeru (append ih je ostavio kao
    .001 iz enterijer.blend) prelaze na foto materijale kita iz kvart.blend (krug 2)."""
    zid, plafon, pod = mat_rez_zid(), mat_rez_ploca(), mat_rez_ploca(pod=True)
    n = 0
    for o in OB:
        if o.type != "MESH":
            continue
        for i, mt in enumerate(o.data.materials):
            if not mt:
                continue
            if mt.name == "presek" or mt.name.startswith("presek_kora"):
                o.data.materials[i] = pod if o.name == "Pod" else plafon if o.name == "Plafon" else zid
                n += 1
    remap = []
    for mt in list(bpy.data.materials):
        baza, _, suf = mt.name.rpartition(".")
        if baza in IZ_KITA and suf.isdigit() and baza in bpy.data.materials:
            mt.user_remap(bpy.data.materials[baza])
            remap.append(mt.name)
    print(f"FOTO rez: {n} slotova; kit u enterijeru -> foto kit: {remap}")


if FOTO:
    foto_materijali()


def hlebovi(veliki):
    """Poglavlje 5: hlebovi 1,4x i razmaknuti po pultu, da se na kadru citaju (etikete idu uz njih)."""
    for i, (nm, (loc, sc)) in enumerate(sorted(HLEB.items())):
        o = OB[nm]
        o.location, o.scale = loc.copy(), sc.copy()
        if veliki:
            o.location.x = 2.76 + 0.36 * i
            o.scale = sc * 1.4


def kadar(n, oblik, fstop=None, izmena=None, fokus=None):
    """Kamera kao kadar() u kvart.py; za 4 i 5 polozaj i cilj sa Stanica_N iz enterijera.
    izmena: dict za kadar gde Pogl_N ne pokazuje ono sto alt opisuje (p, c, lens, blize, sx, sy, foto_sy).
    fokus: tacka u fokusu (podrazumevano pekara, kao lazni tilt-shift)."""
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
    cd.sensor_fit, cd.sensor_width = "AUTO", 36.0
    cd.clip_start = 0.02 if n in STANICA else 0.1
    cd.shift_x = 0.0 if tel else iz.get("sx", pe["shift_x"])
    cd.shift_y = iz.get("sy", pe["tel_shift_y"]) if tel else iz.get("sy", pe["shift_y"])
    if FOTO and tel:
        # foto hoch 720x1440 (render2.py, krug 2): isti vodoravni ugao kao kadar 9:16 (camera.js: uze od 9:16
        # cuva vodoravni ugao), senzor 36 mm na visini 9:16 -> 20,25 mm sirine. Shift se uz HORIZONTAL meri
        # sirinom (720 px), a u 9:16 visinom (1280 px): sy * 1280 / 720, pa jos foto_sy (kuca u gornjih ~60 %)
        cd.sensor_fit, cd.sensor_width = "HORIZONTAL", 36.0 * 9 / 16
        cd.shift_y = cd.shift_y * 1280 / 720 + float(os.environ.get("KRUME_HOCH_SY", iz.get("foto_sy", 0.0)))
    cd.dof.use_dof = bool(fstop)
    if fstop:                                       # lazni tilt-shift: fokus na pekaru
        cd.dof.aperture_fstop = fstop
        cd.dof.aperture_blades = 6
        cd.dof.focus_distance = (Vector(fokus or (1.5, 1.5, 4.0)) - loc).length
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
              st=dict(frame=40, enterijer=True, testo=(0.4, 0.0), zar=220.0, ekspozicija=0.3),
              # foto (krug 3): malo DOF-a, fokus na rezu izvucene Kriske (kraj fasade A posle izvlacenja 4,5 m)
              # svetla: manje hladne ulice u pekari, jaca topla lampa i polica (pekara se cita kao topla soba)
              # hoch: jaci DOF, kaldrma u prvom planu (pod tekstom na dnu) je mutna i mirna
              foto=dict(fstop=0.5, fstop_hoch=0.1, fokus=(8.0, -2.8, 3.0),
                        svetla={"Svetlo_ulica": 0.35, "Svetlo_lampa": 1.8, "Svetlo_polica": 1.6,
                                "Svetlo_magacin": 2.5})),
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

VREME, MEM = {}, {}


def _stat(*a):
    """Poslednja statistika rendera (sadrzi "Peak"), za izvestaj o memoriji."""
    for x in a:
        if isinstance(x, str) and "Peak" in x:
            MEM["s"] = x


bpy.app.handlers.render_stats.append(_stat)
for key in IZBOR:
    d = POGLAVLJA[key]
    svetlo(**d["svetlo"])
    stanje(**d["st"])
    hlebovi(d.get("hleb", False))
    sjaj(d.get("sjaj", False))
    for oblik in FORMATI:
        tel = oblik == "hoch"
        fstop, fokus = (None if tel else d.get("fstop")), None
        if FOTO and "foto" in d:                    # foto: DOF i na telefonu (fotografija makete), fokus na rezu
            fstop = float(os.environ.get("KRUME_FSTOP", d["foto"].get("fstop_" + oblik, d["foto"]["fstop"])))
            fokus = d["foto"]["fokus"]
            for n_, k_ in d["foto"].get("svetla", {}).items():
                if n_ in SVETLA:
                    OB[n_].data.energy = SVETLA[n_] * k_
        kadar(d["n"], oblik, fstop=fstop, izmena=d.get(oblik), fokus=fokus)
        ime = f"{key}-{oblik}.png" if FOTO else f"kadar-{key}-{oblik}.png"
        scene.render.filepath = os.path.join(PNG_DIR, ime)
        t = time.time()
        bpy.ops.render.render(write_still=True)
        VREME[f"{key}-{oblik}"] = time.time() - t
        pk = MEM.get("s", "").split("Peak")[-1].split("|")[0].strip(" :,") if MEM else "?"
        print(f"RENDER {ime}: {VREME[f'{key}-{oblik}']:.1f} s, Mem Peak {pk}")
    for n_ in d.get("foto", {}).get("svetla", {}):     # sledece poglavlje dobija svetla kao pre
        if n_ in SVETLA:
            OB[n_].data.energy = SVETLA[n_]

if not os.environ.get("KRUME_PREFIX") and not FOTO:
    svi_webp(IZBOR)
print("VREME", {k: round(v) for k, v in VREME.items()}, f"ukupno {time.time() - T0:.0f} s")
