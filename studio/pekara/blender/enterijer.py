# Krume, smer 3 "Ein Fenster brennt": enterijer pekare u prizemlju ugaone kuce i magacin na prvom spratu
# (poglavlja 3-5). Stoji tacno u praznom objektu "Pekara_otvor" iz kvart.blend: spoljne zidove (fasada A,
# zakosen ugao, fasada B, sa izlozima i vratima) nosi Kriska iz kvarta, ovde su samo pod, plafoni, unutrasnji
# zidovi (pregradni i zadnji) i namestaj. Lica u ravni unutrasnjeg lica Kriske su presek (ton kore).
# Proceduralno, bez addon-a; foto kadar jos koristi CC0 teksture iz teksture/ (Poly Haven, QUELLEN.md). Materijali zajednicki sa kitom se ucitavaju iz kuca_kit.blend.
# Bake i izvoz u glTF: bake_enterijer.py.
# Pokretanje:
#   Blender -b -P enterijer.py                  (gradi, cuva enterijer.blend, renderuje presek, vitrinu, pec)
#   Blender -b -P enterijer.py -- presek        (samo jedan kadar: presek | vitrina | pec)
#   Blender -b -P enterijer.py -- ofen          (foto proba Cycles: stanica Ofen, vrata otvorena, izmaglica,
#                                                proba-foto/4-ofen-wide.png 1600x1000)
#   Blender -b -P enterijer.py -- norender      (samo gradi i cuva .blend)
# Koordinate: kao u kitu i kvartu. Ishodiste (0, 0, 0) je zamisljeni ostar ugao zgrade (presek pravaca dve
# ulicne fasade) na visini trotoara. +X ide duz fasade A (ulica ka -Y), +Y duz fasade B (ulica ka -X),
# Z gore, metar. Pod pekare je na z = 0,12 (jedan stepenik).
# Okruzenje: KRUME_SAMPLES, KRUME_RES (procenat rezolucije), KRUME_EXPOSURE; za "ofen" jos KRUME_OFEN_EV,
# KRUME_OFEN_ZAR (svetlo zara, W), KRUME_OFEN_EM (emisija zara), KRUME_MAGLA (gustina izmaglice), KRUME_OFEN_IME,
# KRUME_ZRACI i KRUME_ODBIJENO (W), KRUME_HDRI (jacina u odsjajima), KRUME_CIGLA (svetlina foto cigle),
# KRUME_OFEN_POLICA (faktor svetla police), KRUME_NISA (odbijeno svetlo u nisi za drva, W). Krug 3 (samo "ofen",
# sve u Pomocno): liveno gvozdje vrata (mat_vrata_foto), slozena drva u nisi (Pomocno_drva_foto, stare cepanice
# u nisi sakriva Mask), sator od cepanica u komori sa svetlom zraka (light linking: osvetljava samo izmaglicu i
# prasinu), izmaglica brasna umesto pramenova dima. KRUME_WEB=1: bez foto sloja (PBR teksture iz teksture/, HDRI).

import bpy, bmesh, math, os, random, sys, time
from mathutils import Vector, Matrix, Quaternion, Euler
from mathutils import noise as mnoise

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
random.seed(11)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


# testo je krem-bez, brasno toplo belo (ne cisto belo): na sajtu je boja samo albedo * lightmap, bez SSS-a i sjaja
NOC, KORA, ZAR, TESTO, BRASNO = "#14110f", "#7a4a24", "#e8792b", "#d8c09c", "#ece3d3"

# Mere iz kvart.blend (Pekara_otvor, Kriska): zid Kriske je debeo 0,7, njena unutrasnja lica su
# y = 0,7 (fasada A), x = 0,7 (fasada B) i x + y = 3,99 (zakosen ugao). Otvor ide do x = 11,3, y = 8,7 i z = 8,1.
T_KR = 0.7
Y_CUT = T_KR           # ravan preseka uz fasadu A
X_IN = T_KR            # ravan preseka uz fasadu B
CH_IN = 3.0 + T_KR * math.sqrt(2)      # zakosen ugao: x + y = 3,99
X_OUT, Y_OUT, Z_TOP = 11.3, 8.7, 8.1   # granice otvora = spoljna lica pregradnog i zadnjeg zida (nista ne viri)
X_PREG = 11.0          # pregradni zid prema haustoru (unutrasnje lice), debeo 0,3 do X_OUT
Y_ZAD = 8.4            # zadnji zid (unutrasnje lice), debeo 0,3 do Y_OUT
Z_BOT = -0.1           # dno ploce poda, ispod trotoara kvarta (z = 0)
POD, PLAFON = 0.12, 4.1
SPRAT, PLAFON2 = 4.52, 7.8             # pod i plafon magacina na prvom spratu
# pec (zidana, lucni otvor): mere su ovde jer ih koriste i materijali (cadj oko otvora, izlizan prag)
PX0, PX1, PY0, PY1 = X_PREG - 3.45, X_PREG, 4.4, Y_ZAD
PCX = (PX0 + PX1) / 2                      # osa otvora peci
O_W, O_Z0, O_H = 0.86, 1.0, 0.62           # otvor: sirina, prag, visina do temena luka

# ---------------------------------------------------------------- scena
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.curves,
             bpy.data.collections):
    for d in list(coll):
        try:
            coll.remove(d)
        except Exception:
            pass
scene = bpy.context.scene
C_ENT = bpy.data.collections.new("Enterijer")
C_POM = bpy.data.collections.new("Pomocno")        # trotoar za kadar, kamere, rezaci: ne izvozi se
scene.collection.children.link(C_ENT)
scene.collection.children.link(C_POM)
KOREN = bpy.data.objects.new("Enterijer_koren", None)   # prazan objekat u ishodistu, roditelj svega
C_ENT.objects.link(KOREN)

# ---------------------------------------------------------------- materijali iz kita
KIT = os.path.join(HERE, "kuca_kit.blend")
IZ_KITA = ["daska", "drvo_radnja", "metal", "staklo", "hleb", "trotoar", "ivicnjak"]
with bpy.data.libraries.load(KIT, link=False) as (src, dst):
    dst.materials = [n for n in IZ_KITA if n in src.materials]
M = {m.name: m for m in bpy.data.materials if m.name in IZ_KITA}


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def obj_co(nt):
    return nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]


def noise(nt, co, scale, detail, rough=0.5):
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    nt.links.new(co, nz.inputs["Vector"])
    return nz


def ramp(nt, fac, c0, c1, p0=0.0, p1=1.0):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position, r.color_ramp.elements[1].position = p0, p1
    r.color_ramp.elements[0].color = hexc(c0) if isinstance(c0, str) else c0
    r.color_ramp.elements[1].color = hexc(c1) if isinstance(c1, str) else c1
    nt.links.new(fac, r.inputs["Fac"])
    return r.outputs["Color"]


def mixc(nt, fac, a, b):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    sock = {s.identifier: s for s in mx.inputs}
    if isinstance(fac, (int, float)):
        sock["Factor_Float"].default_value = fac
    else:
        nt.links.new(fac, sock["Factor_Float"])
    for key, v in (("A_Color", a), ("B_Color", b)):
        if isinstance(v, str):
            sock[key].default_value = hexc(v)
        elif isinstance(v, tuple):
            sock[key].default_value = v
        else:
            nt.links.new(v, sock[key])
    return [s for s in mx.outputs if s.identifier == "Result_Color"][0]


def math_n(nt, op, *vals, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation, n.use_clamp = op, clamp
    for i, v in enumerate(vals):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def bump(nt, height, strength, dist, normal=None):
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = strength
    bp.inputs["Distance"].default_value = dist
    nt.links.new(height, bp.inputs["Height"])
    if normal is not None:
        nt.links.new(normal, bp.inputs["Normal"])
    return bp.outputs["Normal"]


# ---- foto sloj (Cycles): zaobljene ivice u sencenju, habanje, cadj u udubljenjima, razlika po komadu.
# Sve je proceduralno; na sajtu (bake albeda) ostaje samo ono sto je u Base Color.
def bevel_n(nt, radius=0.004, samples=8):
    """Bevel cvor: ivica se zaobli samo u sencenju, pa svetlo "lize" ivicu kao na pravom predmetu."""
    bv = nt.nodes.new("ShaderNodeBevel")
    bv.samples = samples
    bv.inputs["Radius"].default_value = radius
    return bv.outputs["Normal"]


def ivica(nt, radius=0.01, gain=9.0):
    """1 na ispupcenoj ivici, 0 na ravnom: Bevel normala naspram prave normale (kao u mat_gvozdje)."""
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(bevel_n(nt, radius), dot.inputs[0])
    nt.links.new(nt.nodes.new("ShaderNodeNewGeometry").outputs["Normal"], dot.inputs[1])
    return math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), gain, clamp=True)


def supljina(nt, dist=0.08):
    """1 u uglovima i fugama (AO u blizini), 0 na otvorenom: tamo se skuplja cadj i prasina."""
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.samples = 8
    ao.inputs["Distance"].default_value = dist
    return math_n(nt, "SUBTRACT", 1.0, ao.outputs["AO"])


def po_komadu(nt, co, k=17.0):
    """Object Info Random: svaki objekat dobija svoj pomak suma (dve vekne nisu iste) i broj 0-1."""
    rnd = nt.nodes.new("ShaderNodeObjectInfo").outputs["Random"]
    add = nt.nodes.new("ShaderNodeVectorMath")
    add.operation = "ADD"
    nt.links.new(co, add.inputs[0])
    nt.links.new(math_n(nt, "MULTIPLY", rnd, k), add.inputs[1])
    return add.outputs["Vector"], rnd


def ogrebotine(nt, co, scale=9.0, sirina=0.025, gustina=0.5):
    """Ogrebotine od noza: tanke prave crte u tri pravca (Voronoi ivice razvucene duz crte), isprekidane sumom.
    Vraca masku 0-1."""
    acc = None
    for ang, seed in ((0.25, 0.0), (1.75, 4.1), (-0.9, 9.3)):
        rot = nt.nodes.new("ShaderNodeMapping")
        rot.inputs["Rotation"].default_value = (0, 0, ang)
        rot.inputs["Location"].default_value = (seed, seed * 0.7, 0)
        nt.links.new(co, rot.inputs["Vector"])
        st = nt.nodes.new("ShaderNodeMapping")
        st.inputs["Scale"].default_value = (0.12, 1.0, 1.0)
        nt.links.new(rot.outputs["Vector"], st.inputs["Vector"])
        vo = nt.nodes.new("ShaderNodeTexVoronoi")
        vo.feature = "DISTANCE_TO_EDGE"
        vo.inputs["Scale"].default_value = scale
        nt.links.new(st.outputs["Vector"], vo.inputs["Vector"])
        crta = math_n(nt, "LESS_THAN", vo.outputs["Distance"], sirina)
        prekid = math_n(nt, "GREATER_THAN", noise(nt, rot.outputs["Vector"], scale * 0.6, 2).outputs["Fac"], gustina)
        m_ = math_n(nt, "MULTIPLY", crta, prekid)
        acc = m_ if acc is None else math_n(nt, "MAXIMUM", acc, m_)
    return acc


def wall_uv(nt, co):
    """Za uspravne zidove u X, Y i zakosenom pravcu: u = x - y, v = z."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(math_n(nt, "SUBTRACT", sep.outputs["X"], sep.outputs["Y"]), cmb.inputs["X"])
    nt.links.new(sep.outputs["Z"], cmb.inputs["Y"])
    return cmb.outputs["Vector"]


def mat_plaster(name, col, var=0.07, bump_s=0.3, rough=0.86):
    """Isti gips/karton kao u kitu: mrlja u boji, krupna neravnina i sitno zrno."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    c0 = hexc(col)
    lo = tuple(max(0, c * (1 - var)) for c in c0[:3]) + (1,)
    hi = tuple(min(1, c * (1 + var)) for c in c0[:3]) + (1,)
    nt.links.new(ramp(nt, noise(nt, co, 0.35, 4).outputs["Fac"], lo, hi), p.inputs["Base Color"])
    n1 = bump(nt, noise(nt, co, 1.7, 3, 0.45).outputs["Fac"], bump_s, 0.05)
    nt.links.new(bump(nt, noise(nt, co, 16.0, 6, 0.6).outputs["Fac"], bump_s * 0.7, 0.012, n1), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    return m


def mat_presek(name):
    """Zid u preseku: ton kore #7a4a24 sa porama mrvice (krume), kao presek vekne."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 7.0
    vor.inputs["Randomness"].default_value = 1.0
    nt.links.new(co, vor.inputs["Vector"])
    vor2 = nt.nodes.new("ShaderNodeTexVoronoi")
    vor2.inputs["Scale"].default_value = 26.0
    nt.links.new(co, vor2.inputs["Vector"])
    pore = math_n(nt, "MAXIMUM",
                  math_n(nt, "LESS_THAN", vor.outputs["Distance"], 0.16),
                  math_n(nt, "LESS_THAN", vor2.outputs["Distance"], 0.12))
    nz = noise(nt, co, 3.0, 4)
    base = ramp(nt, nz.outputs["Fac"], "#704321", "#86522a", 0.35, 0.65)
    nt.links.new(mixc(nt, pore, base, "#3f230f"), p.inputs["Base Color"])
    nt.links.new(bump(nt, math_n(nt, "SUBTRACT", 1.0, pore), 0.5, 0.02), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.92
    return m


def mat_tiles(name, c1, c2, mortar, scale, wall=False, rough=0.6, b_s=0.35):
    """Kvadratne ploce: pod (XY) ili zid (u = x - y, v = z)."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    vec = wall_uv(nt, co) if wall else co
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = hexc(c1)
    br.inputs["Color2"].default_value = hexc(c2)
    br.inputs["Mortar"].default_value = hexc(mortar)
    br.inputs["Scale"].default_value = scale
    br.inputs["Mortar Size"].default_value = 0.02
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 0.5
    br.offset = 0.0
    nt.links.new(vec, br.inputs["Vector"])
    nz = noise(nt, co, 0.8, 3)
    nt.links.new(mixc(nt, math_n(nt, "MULTIPLY", nz.outputs["Fac"], 0.35), br.outputs["Color"], "#2a1f17"),
                 p.inputs["Base Color"])
    nt.links.new(bump(nt, br.outputs["Fac"], b_s, 0.02), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    return m


def cigle(nt, uv, w, h, fuga_w):
    """Sopstveni raspored cigli (Brick tekstura nema broj cigle): uv u metrima (u vodoravno, v uspravno),
    svaki drugi red pomeren za pola cigle. Vraca masku fuge (1 u fugi), id cigle (vektor za White Noise)
    i rastojanje do ivice cigle (m)."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv, sep.inputs["Vector"])
    u, v = sep.outputs["X"], sep.outputs["Y"]
    row = math_n(nt, "FLOOR", math_n(nt, "DIVIDE", v, h))
    us = math_n(nt, "ADD", u, math_n(nt, "MULTIPLY", math_n(nt, "FRACT", math_n(nt, "MULTIPLY", row, 0.5)), w))
    col = math_n(nt, "FLOOR", math_n(nt, "DIVIDE", us, w))
    fu = math_n(nt, "MULTIPLY", math_n(nt, "FRACT", math_n(nt, "DIVIDE", us, w)), w)
    fv = math_n(nt, "MULTIPLY", math_n(nt, "FRACT", math_n(nt, "DIVIDE", v, h)), h)
    du = math_n(nt, "MINIMUM", fu, math_n(nt, "SUBTRACT", w, fu))
    dv = math_n(nt, "MINIMUM", fv, math_n(nt, "SUBTRACT", h, fv))
    d = math_n(nt, "MINIMUM", du, dv)
    fuga = ramp(nt, d, (1, 1, 1, 1), (0, 0, 0, 1), fuga_w * 0.5, fuga_w * 0.5 + 0.004)
    idv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(col, idv.inputs["X"])
    nt.links.new(row, idv.inputs["Y"])
    return fuga, idv.outputs["Vector"], d


# ---- PBR teksture (Poly Haven, CC0; izvori u teksture/QUELLEN.md): samo foto kadar (Cycles), ne bake za sajt.
# Mape idu preko UV mape "foto_uv" (kocka po glavnoj osi lica, u metrima / velicina plocice, vidi foto_uv()),
# da Normal Map cvor (tangentni prostor) ima ispravne tangente; Box projekcija bi ih pokvarila.
TEKS = os.path.join(HERE, "teksture")
FOTO_UV = "foto_uv"


def slika(rel, boja=False):
    img = bpy.data.images.load(os.path.join(TEKS, rel), check_existing=True)
    img.colorspace_settings.name = "sRGB" if boja else "Non-Color"     # rough, normal, disp: Non-Color
    return img


def pbr(nt, ime, w, h, nor_s=1.0, disp=False):
    """diff, rough, normal (Normal Map cvor, nor_gl) i disp jednog aseta; plocica teksture je w x h metara."""
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = FOTO_UV
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.0 / w, 1.0 / h, 1.0)
    nt.links.new(uv.outputs["UV"], mp.inputs["Vector"])

    def tx(suf, boja=False):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = slika(f"{ime}/{ime}_{suf}", boja)
        t.interpolation = "Cubic" if suf.startswith("disp") else "Linear"
        nt.links.new(mp.outputs["Vector"], t.inputs["Vector"])
        return t.outputs["Color"]

    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.space, nm.uv_map = "TANGENT", FOTO_UV
    nm.inputs["Strength"].default_value = nor_s
    nt.links.new(tx("nor_gl_2k.jpg"), nm.inputs["Color"])
    r = {"diff": tx("diff_2k.jpg", True), "rough": tx("rough_2k.jpg"), "nor": nm.outputs["Normal"]}
    if disp:
        r["disp"] = tx("disp_2k.png")
    return r


def skala(nt, col, k):
    """Boja puta broj (posvetli ili potamni teksturu)."""
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "SCALE"
    nt.links.new(col, vm.inputs[0])
    if isinstance(k, (int, float)):
        vm.inputs["Scale"].default_value = k
    else:
        nt.links.new(k, vm.inputs["Scale"])
    return vm.outputs["Vector"]


def bevel_na(nt, normal, radius):
    """Bevel cvor preko vec izmenjene normale (normal mapa): zaobljena ivica + detalj teksture."""
    bv = nt.nodes.new("ShaderNodeBevel")
    bv.samples = 8
    bv.inputs["Radius"].default_value = radius
    nt.links.new(normal, bv.inputs["Normal"])
    return bv.outputs["Normal"]


def mat_cigla(name, c1="#8a4b2d", c2="#6e3a24", mortar="#a69a86", otvor=False, foto=0.0):
    """Cigla peci u pravoj meri (25 x 7,5 cm): svaka cigla svoj ton (White Noise po broju cigle), sitna mrlja
    i okrnjene ivice, malter uvucen i tamniji od prasine i cadji, cadj odozgo (gradijent po z).
    otvor=True: cadj iznad i oko lucnog otvora (dim izlazi gore uz lice peci), u prugama i u udubljenjima.
    foto > 0: cigla i malter su iz fotografije (brick_wall_006, plocica 2,75 x 3,25 m = cigla ~26 x 8,6 cm sa
    fugom), potamnjeni na ton peci (foto = faktor svetline); cadj, AO u fugama i krupna mrlja ostaju preko."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    if foto:
        return mat_cigla_foto(m, nt, p, co, foto, otvor)
    fuga, idv, d = cigle(nt, wall_uv(nt, co), 0.25, 0.075, 0.012)
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(idv, wn.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeValToRGB")
    els = cr.color_ramp.elements
    lo = tuple(c * 0.7 for c in hexc(c2)[:3]) + (1,)
    els[0].position, els[0].color = 0.0, lo
    els[1].position, els[1].color = 1.0, tuple(min(1, c * 1.12) for c in hexc(c1)[:3]) + (1,)
    for pos, c in ((0.25, hexc(c2)), (0.6, hexc(c1))):
        e = els.new(pos)
        e.color = c
    nt.links.new(wn.outputs["Value"], cr.inputs["Fac"])
    brick = mixc(nt, math_n(nt, "MULTIPLY", noise(nt, co, 22.0, 5, 0.6).outputs["Fac"], 0.35), cr.outputs["Color"],
                 tuple(c * 0.6 for c in hexc(c2)[:3]) + (1,))
    # okrnjene ivice: uz fugu sum "pojede" ivicu cigle, pa se tu vidi malter
    krn = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", d, 0.014),
                 math_n(nt, "GREATER_THAN", noise(nt, co, 40.0, 4, 0.7).outputs["Fac"], 0.62))
    fuga_m = math_n(nt, "MAXIMUM", fuga, krn)
    malter = ramp(nt, noise(nt, co, 9.0, 4).outputs["Fac"], tuple(c * 0.55 for c in hexc(mortar)[:3]) + (1,),
                  tuple(c * 0.85 for c in hexc(mortar)[:3]) + (1,), 0.3, 0.7)
    col = mixc(nt, fuga_m, brick, malter)
    cav = supljina(nt, 0.06)
    col = mixc(nt, math_n(nt, "MULTIPLY", cav, 0.55), col, "#1d1612")
    soot = cadj_peci(nt, co, cav, otvor)
    col = mixc(nt, math_n(nt, "MINIMUM", soot, 0.95), col, "#151010")
    nt.links.new(col, p.inputs["Base Color"])
    # malter uvucen 4 mm, svaka cigla malo nagnuta (id), sitno zrno; preko Bevel cvora (ivice peci)
    nag = nt.nodes.new("ShaderNodeTexWhiteNoise")
    nt.links.new(idv, nag.inputs["Vector"])
    nag.noise_dimensions = "4D"
    nag.inputs["W"].default_value = 3.3
    h_ = math_n(nt, "ADD", math_n(nt, "SUBTRACT", 1.0, fuga_m), math_n(nt, "MULTIPLY", nag.outputs["Value"], 0.12))
    n0 = bevel_n(nt, 0.012)
    n1 = bump(nt, noise(nt, co, 45.0, 5, 0.6).outputs["Fac"], 0.3, 0.003, n0)
    nt.links.new(bump(nt, h_, 0.8, 0.004, n1), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", fuga_m, 0.08, math_n(nt, "MULTIPLY_ADD", soot, -0.15, 0.88)),
                 p.inputs["Roughness"])
    return m


def mat_cigla_foto(m, nt, p, co, ton, otvor):
    """Foto cigla (vidi mat_cigla): albedo iz teksture puta ton, fuga iz disp mape (nisko = malter), normal mapa
    + disp kao bump (malter uvucen ~1 cm; prava displacement ne treba, kadar nije blize od 1,5 m)."""
    t = pbr(nt, "brick_wall_006", 2.75, 3.25, nor_s=0.9, disp=True)
    dsp = t["disp"]
    fuga_m = ramp(nt, dsp, (1, 1, 1, 1), (0, 0, 0, 1), 0.22, 0.34)
    hs = nt.nodes.new("ShaderNodeHueSaturation")          # foto cigla je narandzastija od cigle peci
    hs.inputs["Saturation"].default_value = 1.0
    nt.links.new(t["diff"], hs.inputs["Color"])
    col = skala(nt, hs.outputs["Color"], ton)
    # krupna mrlja (jace i slabije pecena polja), pa malter jos malo potamnjen od prasine
    col = mixc(nt, math_n(nt, "MULTIPLY", noise(nt, co, 1.3, 4).outputs["Fac"], 0.45), col,
               tuple(c * ton * 0.25 for c in (0.35, 0.12, 0.06)) + (1,))
    col = mixc(nt, math_n(nt, "MULTIPLY", fuga_m, 0.35), col, tuple(c * ton for c in (0.12, 0.1, 0.08)) + (1,))
    cav = supljina(nt, 0.06)
    col = mixc(nt, math_n(nt, "MULTIPLY", cav, 0.55), col, "#1d1612")
    soot = cadj_peci(nt, co, cav, otvor)
    col = mixc(nt, math_n(nt, "MINIMUM", soot, 0.95), col, "#151010")
    nt.links.new(col, p.inputs["Base Color"])
    n0 = bevel_na(nt, t["nor"], 0.012)
    nt.links.new(bump(nt, dsp, 0.55, 0.012, n0), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", soot, -0.12, math_n(nt, "MULTIPLY_ADD", t["rough"], 0.25, 0.7)),
                 p.inputs["Roughness"])
    return m


def cadj_peci(nt, co, cav, otvor):
    """Cadj odozgo (gradijent po z), a uz otvor=True i oko lucnog otvora: pruge navise i gusce u udubljenjima."""
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    soot = math_n(nt, "MULTIPLY", noise(nt, co, 2.5, 4).outputs["Fac"],
                  math_n(nt, "SUBTRACT", sep.outputs["Z"], 1.4, clamp=True))
    if otvor:
        dz = math_n(nt, "SUBTRACT", sep.outputs["Z"], O_Z0 + O_H * 0.8)
        zz = math_n(nt, "ADD", math_n(nt, "DIVIDE", math_n(nt, "MAXIMUM", dz, 0.0), 1.25),
                    math_n(nt, "DIVIDE", math_n(nt, "MINIMUM", dz, 0.0), 0.5))
        xx = math_n(nt, "DIVIDE", math_n(nt, "SUBTRACT", sep.outputs["X"], PCX),
                    math_n(nt, "MULTIPLY_ADD", math_n(nt, "MAXIMUM", dz, 0.0), 0.35, 0.62))
        r = math_n(nt, "SQRT", math_n(nt, "ADD", math_n(nt, "POWER", xx, 2.0), math_n(nt, "POWER", zz, 2.0)))
        oko = math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", r, 0.45), 0.0), clamp=True)
        oko = math_n(nt, "POWER", oko, 1.6)
        pr = nt.nodes.new("ShaderNodeMapping")                 # pruge: sum razvucen uspravno (dim se penje)
        pr.inputs["Scale"].default_value = (7.0, 7.0, 1.1)
        nt.links.new(co, pr.inputs["Vector"])
        pruge = ramp(nt, noise(nt, pr.outputs["Vector"], 1.0, 5, 0.65).outputs["Fac"], (0.35, 0.35, 0.35, 1),
                     (1, 1, 1, 1), 0.35, 0.65)
        lice = math_n(nt, "LESS_THAN", sep.outputs["Y"], PY0 + 0.06)   # samo lice peci, ne komora
        oko = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", oko, pruge), lice)
        oko = math_n(nt, "MAXIMUM", oko, math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", cav, oko), 2.0))
        soot = math_n(nt, "MAXIMUM", soot, math_n(nt, "MULTIPLY", oko, 0.95))
    return soot


def mat_simple(name, col, rough=0.7, metal=0.0, emit=None, strength=0.0, coat=0.0, sss=0.0):
    m, nt, p = node_mat(name)
    p.inputs["Base Color"].default_value = hexc(col)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.15
    if sss:
        p.inputs["Subsurface Weight"].default_value = sss
        p.inputs["Subsurface Radius"].default_value = (0.012, 0.008, 0.005)
    if emit:
        p.inputs["Emission Color"].default_value = hexc(emit)
        p.inputs["Emission Strength"].default_value = strength
    return m


def mat_zar(name, strength):
    """Zar: sum odredjuje gde je ugalj crn, gde tinja tamnocrveno, a gde gori narandzasto (najtoplije jedva zuto).
    Boja je zasicena crveno-narandzasta i jaka, da je AgX ne izbledi u zuto."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    nz = noise(nt, co, 5.0, 6, 0.62)
    # komadi uglja (Voronoi celije): pukotine izmedju njih gore, svaka celija tinja svojom jacinom
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 26.0
    nt.links.new(co, vo.inputs["Vector"])
    ve = nt.nodes.new("ShaderNodeTexVoronoi")
    ve.feature = "DISTANCE_TO_EDGE"
    ve.inputs["Scale"].default_value = 26.0
    nt.links.new(co, ve.inputs["Vector"])
    puk = ramp(nt, ve.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.11)
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(vo.outputs["Color"], bw.inputs["Color"])
    sitno = noise(nt, co, 60.0, 4, 0.6).outputs["Fac"]
    tinja = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", bw.outputs["Val"], 0.5, nz.outputs["Fac"]), sitno)
    heat = math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", puk, math_n(nt, "MULTIPLY_ADD", nz.outputs["Fac"], 0.6, 0.55)),
                  math_n(nt, "MULTIPLY", tinja, 0.75), clamp=True)
    col = nt.nodes.new("ShaderNodeValToRGB")
    els = col.color_ramp.elements
    els[0].position, els[0].color = 0.12, (0.0, 0.0, 0.0, 1)
    els[1].position, els[1].color = 0.92, hexc("#ffa23a")
    for pos, c in ((0.24, "#2a0800"), (0.4, "#8a2200"), (0.62, "#ee4a06"), (0.8, "#ff7a12")):
        e = els.new(pos)
        e.color = hexc(c)
    nt.links.new(heat, col.inputs["Fac"])
    p.inputs["Base Color"].default_value = hexc("#120c0a")
    p.inputs["Roughness"].default_value = 0.95
    p.inputs["Specular IOR Level"].default_value = 0.0     # bez odsjaja svetla zara (inace bledo ruzicasto)
    nt.links.new(col.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength
    nt.links.new(bump(nt, nz.outputs["Fac"], 0.6, 0.01), p.inputs["Normal"])
    return m


def mat_samot(name):
    """Pod komore: samotne ploce (XY) u dva tona, cadj u fugama i pepeo u mrljama."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = hexc("#7a4a2c")
    br.inputs["Color2"].default_value = hexc("#5e3820")
    br.inputs["Mortar"].default_value = hexc("#1a120d")
    br.inputs["Scale"].default_value = 3.2
    br.inputs["Mortar Size"].default_value = 0.012
    br.inputs["Brick Width"].default_value = 0.6
    br.inputs["Row Height"].default_value = 0.3
    br.offset = 0.5
    nt.links.new(co, br.inputs["Vector"])
    soot = ramp(nt, noise(nt, co, 3.0, 5, 0.6).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.45, 0.75)
    base = mixc(nt, math_n(nt, "MULTIPLY", soot, 0.8), br.outputs["Color"], "#1e140f")
    ash = ramp(nt, noise(nt, co, 7.0, 6, 0.7).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.55, 0.7)
    nt.links.new(mixc(nt, ash, base, "#8d8780"), p.inputs["Base Color"])
    n1 = bump(nt, noise(nt, co, 40.0, 4).outputs["Fac"], 0.3, 0.004)
    nt.links.new(bump(nt, br.outputs["Fac"], 0.5, 0.01, n1), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.95
    return m


def mat_drvo(name, c_lo, c_hi, rough=0.55, axis="X", scale=3.0, coat=0.0, vlakno=0.0):
    """Daska sa godovima (wave trake razvucene duz vlakna) i blagom mrljom u tonu.
    vlakno > 0: sitne tamne pruge duz vlakna (zrno), da se drvo cita i izbliza i u albedu bez sjaja."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.08, 1.0, 1.0) if axis == "X" else (1.0, 0.08, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type, wv.bands_direction = "BANDS", "Y" if axis == "X" else "X"
    wv.inputs["Scale"].default_value = scale
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    wood = ramp(nt, wv.outputs["Fac"], c_lo, c_hi)
    if vlakno:
        mp2 = nt.nodes.new("ShaderNodeMapping")
        mp2.inputs["Scale"].default_value = (0.025, 1.0, 1.0) if axis == "X" else (1.0, 0.025, 1.0)
        nt.links.new(co, mp2.inputs["Vector"])
        vl = noise(nt, mp2.outputs["Vector"], 90.0, 4, 0.6)
        pr = ramp(nt, vl.outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.52, 0.7)
        dark = tuple(c * 0.55 for c in hexc(c_lo)[:3]) + (1,)
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        sk = {s_.identifier: s_ for s_ in mx.inputs}
        nt.links.new(math_n(nt, "MULTIPLY", pr, vlakno), sk["Factor_Float"])
        nt.links.new(wood, sk["A_Color"])
        sk["B_Color"].default_value = dark
        wood = [s_ for s_ in mx.outputs if s_.identifier == "Result_Color"][0]
    nz = noise(nt, co, 1.2, 3)
    col = mixc(nt, math_n(nt, "MULTIPLY", nz.outputs["Fac"], 0.3), wood, c_lo)
    # pore: sitne izduzene tacke duz vlakna; izlizane ivice malo svetlije (Bevel)
    mpp = nt.nodes.new("ShaderNodeMapping")
    mpp.inputs["Scale"].default_value = (0.15, 1.0, 1.0) if axis == "X" else (1.0, 0.15, 1.0)
    nt.links.new(co, mpp.inputs["Vector"])
    vop = nt.nodes.new("ShaderNodeTexVoronoi")
    vop.inputs["Scale"].default_value = 260.0
    nt.links.new(mpp.outputs["Vector"], vop.inputs["Vector"])
    pore = math_n(nt, "LESS_THAN", vop.outputs["Distance"], 0.1)
    col = mixc(nt, math_n(nt, "MULTIPLY", pore, 0.45), col, tuple(c * 0.4 for c in hexc(c_lo)[:3]) + (1,))
    col = mixc(nt, math_n(nt, "MULTIPLY", ivica(nt, 0.006), 0.25), col, c_hi)
    nt.links.new(col, p.inputs["Base Color"])
    n0 = bevel_n(nt, 0.004)
    n1 = bump(nt, math_n(nt, "SUBTRACT", 1.0, pore), 0.15, 0.0008, n0)
    nt.links.new(bump(nt, wv.outputs["Fac"], 0.1, 0.006, n1), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.35
    return m


def mat_testo(name, flour=0.35):
    """Sirovo testo: mat krem-bez koza (topliji i tamniji ton u udubljenjima mrlje, sitni mehurici),
    preko nje trag brasna u mekim mrljama. Boja je u albedu (sajt), a za Cycles jos SSS (testo propusta svetlo),
    pomak suma po komadu (Object Info) i brasno kao drugi sloj: suvlje i hrapavije, gusce odozgo."""
    m, nt, p = node_mat(name)
    co, rnd = po_komadu(nt, obj_co(nt))
    koza = ramp(nt, noise(nt, co, 9.0, 4, 0.55).outputs["Fac"], "#cdb18a", "#e0caa8", 0.3, 0.7)
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 140.0
    nt.links.new(co, vo.inputs["Vector"])
    mehur = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", vo.outputs["Distance"], 0.12), 0.35)
    koza = mixc(nt, mehur, koza, "#bb9c74")
    koza = mixc(nt, math_n(nt, "MULTIPLY", rnd, 0.25), koza, "#c9a77c")
    nz = noise(nt, co, 16.0, 6, 0.62)
    fl = ramp(nt, nz.outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.6 - flour * 0.18, 0.74 - flour * 0.12)
    gn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nt.nodes.new("ShaderNodeNewGeometry").outputs["Normal"], gn.inputs["Vector"])
    gore = math_n(nt, "MULTIPLY_ADD", math_n(nt, "MAXIMUM", gn.outputs["Z"], 0.0), 0.5, 0.6)
    fl_m = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", fl, 0.35 + flour * 0.5), gore, clamp=True)
    nt.links.new(mixc(nt, fl_m, koza, BRASNO), p.inputs["Base Color"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", fl_m, 0.13, 0.82), p.inputs["Roughness"])
    p.inputs["Subsurface Weight"].default_value = 0.6
    p.inputs["Subsurface Radius"].default_value = (0.02, 0.011, 0.006)
    p.inputs["Subsurface Scale"].default_value = 0.5
    p.inputs["Specular IOR Level"].default_value = 0.35
    n1 = bump(nt, noise(nt, co, 120.0, 3).outputs["Fac"], 0.08, 0.002)
    nt.links.new(bump(nt, fl_m, 0.15, 0.0006, n1), p.inputs["Normal"])
    return m


def mat_sto(name):
    """Ploca radnog stola: svetla bukva sa godovima i porama, ogrebotine od noza i strugalice (svetlije, sveze
    drvo, u njima brasno), brasno u mrljama u dva sloja (krupne mrlje + sitan posip), izlizana ivica."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.08, 1.0, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type, wv.bands_direction = "BANDS", "Y"
    wv.inputs["Scale"].default_value = 3.0
    wv.inputs["Distortion"].default_value = 5
    wv.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    wood = ramp(nt, wv.outputs["Fac"], "#9c6b3c", "#c4925c")
    mpp = nt.nodes.new("ShaderNodeMapping")
    mpp.inputs["Scale"].default_value = (0.15, 1.0, 1.0)
    nt.links.new(co, mpp.inputs["Vector"])
    vop = nt.nodes.new("ShaderNodeTexVoronoi")
    vop.inputs["Scale"].default_value = 260.0
    nt.links.new(mpp.outputs["Vector"], vop.inputs["Vector"])
    pore = math_n(nt, "LESS_THAN", vop.outputs["Distance"], 0.1)
    wood = mixc(nt, math_n(nt, "MULTIPLY", pore, 0.4), wood, "#5a3b1f")
    ogr = ogrebotine(nt, co, 7.0, 0.02, 0.45)
    wood = mixc(nt, math_n(nt, "MULTIPLY", ogr, 0.7), wood, "#dcb98e")
    fl = noise(nt, co, 3.2, 6, 0.65)
    mask = ramp(nt, fl.outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.5, 0.66)
    posip = ramp(nt, noise(nt, co, 38.0, 4, 0.7).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.58, 0.68)
    fl_m = math_n(nt, "MAXIMUM", mask, math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", posip, ogr), 0.55))
    nt.links.new(mixc(nt, fl_m, wood, BRASNO), p.inputs["Base Color"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", fl_m, 0.2, 0.72), p.inputs["Roughness"])
    n0 = bevel_n(nt, 0.008)
    n1 = bump(nt, math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MAXIMUM", ogr, pore)), 0.25, 0.0008, n0)
    n2 = bump(nt, fl_m, 0.2, 0.0006, n1)
    nt.links.new(bump(nt, wv.outputs["Fac"], 0.12, 0.01, n2), p.inputs["Normal"])
    return m


def mat_tkanina(name, col, scale=900.0, b_s=0.25):
    """Platno ili juta: dve wave trake (osnova i potka) kao tkanje."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    w = []
    for d in ("X", "Y"):
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.wave_type, wv.bands_direction = "BANDS", d
        wv.inputs["Scale"].default_value = scale
        nt.links.new(co, wv.inputs["Vector"])
        w.append(wv.outputs["Fac"])
    h = math_n(nt, "MULTIPLY", w[0], w[1])
    nz = noise(nt, co, 4.0, 3)
    nt.links.new(ramp(nt, nz.outputs["Fac"], hexc(col)[:3] + (1,), tuple(c * 0.82 for c in hexc(col)[:3]) + (1,)),
                 p.inputs["Base Color"])
    nt.links.new(bump(nt, h, b_s, 0.002), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.95
    return m


def mat_pruce(name):
    """Korpa od trske (Gaerkorb): koncentricni prsteni oko dna (duzina vektora)."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(co, ln.inputs[0])
    s = math_n(nt, "SINE", math_n(nt, "MULTIPLY", ln.outputs["Value"], 270.0))     # trska oko 5 mm
    nt.links.new(ramp(nt, s, "#7c5530", "#b88a55", -1.0, 1.0), p.inputs["Base Color"])
    nt.links.new(bump(nt, s, 0.6, 0.003), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.8
    return m


def mat_kora(name, light, dark, rough=0.55, mode="semmel"):
    """Kora hleba. Atribut "boja" (po temenu): R = koliko je pecena, G = maska (mak, Ausbund, brasno)."""
    m, nt, p = node_mat(name)
    co, rnd = po_komadu(nt, obj_co(nt))                   # svaki komad pecen malo drugacije
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "boja"
    sp = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(at.outputs["Color"], sp.inputs["Color"])
    mott = noise(nt, co, 45.0, 4, 0.55)
    bake = math_n(nt, "MULTIPLY_ADD", mott.outputs["Fac"], 0.5, sp.outputs["Red"])
    bake = math_n(nt, "MULTIPLY_ADD", rnd, 0.16, math_n(nt, "SUBTRACT", bake, 0.08))
    # mehurici (plikovi u kori): sitne kupole, vrh tamniji (jace pecen)
    vb = nt.nodes.new("ShaderNodeTexVoronoi")
    vb.inputs["Scale"].default_value = 110.0
    nt.links.new(co, vb.inputs["Vector"])
    plik = ramp(nt, vb.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.05, 0.22)
    plik = math_n(nt, "MULTIPLY", plik, math_n(nt, "GREATER_THAN", noise(nt, co, 14.0, 2).outputs["Fac"], 0.52))
    bake = math_n(nt, "MULTIPLY_ADD", plik, 0.18, bake)
    col = ramp(nt, math_n(nt, "SUBTRACT", bake, 0.22, clamp=True), light, dark)
    # mikro-pukotine: tanka mreza (Voronoi ivice), svetlija (ispod kore je bleda)
    vp = nt.nodes.new("ShaderNodeTexVoronoi")
    vp.feature = "DISTANCE_TO_EDGE"
    vp.inputs["Scale"].default_value = 70.0
    nt.links.new(co, vp.inputs["Vector"])
    puk = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", vp.outputs["Distance"], 0.025),
                 math_n(nt, "GREATER_THAN", noise(nt, co, 9.0, 3).outputs["Fac"], 0.55))
    col = mixc(nt, math_n(nt, "MULTIPLY", puk, 0.55), col, light)
    fine = bump(nt, noise(nt, co, 260.0, 4).outputs["Fac"], 0.18, 0.0015)
    fine = bump(nt, plik, 0.25, 0.0012, fine)
    fine = bump(nt, math_n(nt, "SUBTRACT", 1.0, puk), 0.3, 0.0005, fine)
    if mode == "semmel":                                  # brasno kao drugi sloj: tanko, u mrljama, odozgo
        gn = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(nt.nodes.new("ShaderNodeNewGeometry").outputs["Normal"], gn.inputs["Vector"])
        fl = ramp(nt, noise(nt, co, 20.0, 6, 0.65).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.56, 0.7)
        fl = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", fl, math_n(nt, "MAXIMUM", gn.outputs["Z"], 0.0)), 0.45)
        col = mixc(nt, fl, col, BRASNO)
    G = sp.outputs["Green"]
    if mode == "mak":
        dots = []
        for sc, seed in ((430.0, 0.0), (500.0, 3.7)):
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.inputs["Location"].default_value = (seed, seed * 0.5, 0)
            nt.links.new(co, mp.inputs["Vector"])
            vo = nt.nodes.new("ShaderNodeTexVoronoi")
            vo.inputs["Scale"].default_value = sc
            nt.links.new(mp.outputs["Vector"], vo.inputs["Vector"])
            dots.append(math_n(nt, "LESS_THAN", vo.outputs["Distance"], 0.42))
        d = math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", dots[0], dots[1]), G)
        col = mixc(nt, d, col, "#1b1e26")
        fine = bump(nt, d, 0.35, 0.0006, fine)
        rr = math_n(nt, "MULTIPLY_ADD", d, -0.2, rough)
        nt.links.new(rr, p.inputs["Roughness"])
    elif mode == "lauge":
        col = mixc(nt, G, col, "#d8ad73")
        nt.links.new(math_n(nt, "MULTIPLY_ADD", G, 0.5, rough), p.inputs["Roughness"])
        p.inputs["Coat Weight"].default_value = 0.35
        p.inputs["Coat Roughness"].default_value = 0.3
    elif mode == "roggen":
        vo = nt.nodes.new("ShaderNodeTexVoronoi")
        vo.feature = "DISTANCE_TO_EDGE"
        vo.inputs["Scale"].default_value = 48.0
        nt.links.new(co, vo.inputs["Vector"])
        crack = math_n(nt, "LESS_THAN", vo.outputs["Distance"], 0.03)
        fl = math_n(nt, "MULTIPLY", noise(nt, co, 30.0, 6, 0.7).outputs["Fac"], 0.35)
        flour = math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", crack, 0.25), fl), G)
        col = mixc(nt, flour, col, "#cdb898")
        fine = bump(nt, math_n(nt, "SUBTRACT", 1.0, crack), 0.25, 0.003, fine)
        nt.links.new(math_n(nt, "MULTIPLY_ADD", flour, 0.35, rough), p.inputs["Roughness"])
    if mode in ("semmel",):
        p.inputs["Roughness"].default_value = rough
    nt.links.new(col, p.inputs["Base Color"])
    nt.links.new(fine, p.inputs["Normal"])
    return m


def mat_krume(name, c_lo, c_hi, pore="#3a2a1d"):
    """Sredina hleba (Krume): pore iz dva Voronoi sloja i blago udubljenje."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    pores = []
    for sc, th in ((160.0, 0.2), (420.0, 0.16)):
        vo = nt.nodes.new("ShaderNodeTexVoronoi")
        vo.inputs["Scale"].default_value = sc
        nt.links.new(co, vo.inputs["Vector"])
        pores.append(math_n(nt, "LESS_THAN", vo.outputs["Distance"], th))
    pr = math_n(nt, "MAXIMUM", pores[0], pores[1])
    base = ramp(nt, noise(nt, co, 60.0, 4).outputs["Fac"], c_lo, c_hi)
    nt.links.new(mixc(nt, pr, base, pore), p.inputs["Base Color"])
    nt.links.new(bump(nt, math_n(nt, "SUBTRACT", 1.0, pr), 0.5, 0.0015), p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.9
    p.inputs["Subsurface Weight"].default_value = 0.3     # mekana sredina propusta malo svetla
    p.inputs["Subsurface Radius"].default_value = (0.008, 0.005, 0.003)
    return m


def mat_gvozdje(name, c_lo, c_hi, edge, rough=0.55, metal=0.6):
    """Liveno gvozdje: tamna osnova sa mrljama patine i svetlije, izlizane ivice (Bevel cvor naspram prave
    normale: na ivici se razlikuju). Ivice i mrlje su u boji, da se oblik vrata cita i na sajtu (bez odsjaja)."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    base = ramp(nt, noise(nt, co, 14.0, 5, 0.6).outputs["Fac"], c_lo, c_hi, 0.35, 0.7)
    rdj = ramp(nt, noise(nt, co, 5.0, 4, 0.5).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.62, 0.78)
    base = mixc(nt, math_n(nt, "MULTIPLY", rdj, 0.45), base, "#4a2c1c")
    bv = nt.nodes.new("ShaderNodeBevel")
    bv.samples = 8
    bv.inputs["Radius"].default_value = 0.012
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(bv.outputs["Normal"], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    ivica = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), 9.0, clamp=True)
    ivica = math_n(nt, "MULTIPLY", ivica, math_n(nt, "MULTIPLY_ADD", noise(nt, co, 40.0, 3).outputs["Fac"], 0.8, 0.4))
    # prag peci (polica za lopatu) je izglacan od lopate: pojas na vrhu praga u osi otvora (svetske koordinate)
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs["Vector"])
    gn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], gn.inputs["Vector"])
    prag = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", gn.outputs["Z"], 0.8),
                  math_n(nt, "LESS_THAN", math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", pos.outputs["X"], PCX)), 0.4))
    prag = math_n(nt, "MULTIPLY", prag, math_n(nt, "GREATER_THAN", pos.outputs["Y"], PY0 - 0.21))
    prag = math_n(nt, "MULTIPLY", prag, math_n(nt, "LESS_THAN", math_n(nt, "ABSOLUTE",
                  math_n(nt, "SUBTRACT", pos.outputs["Z"], O_Z0 - 0.02)), 0.03))
    prag = math_n(nt, "MULTIPLY", prag, ramp(nt, noise(nt, co, 18.0, 4).outputs["Fac"], (0.3, 0.3, 0.3, 1),
                                             (1, 1, 1, 1), 0.35, 0.6))
    hab = math_n(nt, "MAXIMUM", math_n(nt, "MINIMUM", ivica, 1.0), prag)
    nt.links.new(mixc(nt, hab, base, edge), p.inputs["Base Color"])
    nt.links.new(bump(nt, noise(nt, co, 60.0, 4).outputs["Fac"], 0.25, 0.002, bv.outputs["Normal"]), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", hab, -0.3, rough), p.inputs["Roughness"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", hab, 0.35, metal, clamp=True), p.inputs["Metallic"])
    return m


def mat_cepanica(name):
    """Cepanice: atribut "drvo" (po uglu lica) nosi koordinate: R, G = presek (x, y od ose) ili kora (luk, duz ose),
    B = 1 na preseku, A = poluprecnik. Presek: godovi, tamnija srz, svetla beljika, radijalne pukotine i tamna
    kora po obodu. Kora: uzduzne brazde i ploce. U komori (z > 0,95) cepanice su ugljenisane."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "drvo"
    sp = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(at.outputs["Color"], sp.inputs["Color"])
    R, G, B, A = sp.outputs["Red"], sp.outputs["Green"], sp.outputs["Blue"], at.outputs["Alpha"]
    # presek
    v2 = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(R, v2.inputs["X"])
    nt.links.new(G, v2.inputs["Y"])
    ln = nt.nodes.new("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    nt.links.new(v2.outputs["Vector"], ln.inputs[0])
    r = ln.outputs["Value"]
    rn = math_n(nt, "DIVIDE", r, A)                                         # 0 u srzi, 1 na kori
    nzr = noise(nt, v2.outputs["Vector"], 30.0, 3).outputs["Fac"]
    god = math_n(nt, "SINE", math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", nzr, 0.012, r), 2 * math.pi * 85.0))   # god ~12 mm
    pres = ramp(nt, god, "#a87a4d", "#c79a68", -1.0, 1.0)
    pres = mixc(nt, ramp(nt, rn, (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.45), pres, "#7a5233")
    pres = mixc(nt, ramp(nt, rn, (0, 0, 0, 1), (1, 1, 1, 1), 0.72, 0.84), pres, "#d6b588")
    at2 = math_n(nt, "ARCTAN2", G, R)
    puk = math_n(nt, "SINE", math_n(nt, "MULTIPLY_ADD", nzr, 3.0, math_n(nt, "MULTIPLY_ADD", A, 900.0, at2)))  # jedna pukotina, ugao po cepanici
    puk = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", puk, 0.993), math_n(nt, "GREATER_THAN", rn, 0.35))
    # jos nekoliko kracih radijalnih pukotina od suvljenja (od kore ka srzi), svaka cepanica svoj ugao i broj
    puk2 = math_n(nt, "SINE", math_n(nt, "MULTIPLY_ADD", nzr, 5.0,
                                     math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", A, 1300.0, at2), 3.0)))
    puk2 = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", puk2, 0.985),
                  math_n(nt, "GREATER_THAN", rn, math_n(nt, "MULTIPLY_ADD", nzr, 0.4, 0.45)))
    puk = math_n(nt, "MAXIMUM", puk, puk2)
    # tragovi testere na celu: fine paralelne crte, preko njih prljavstina
    tes = math_n(nt, "SINE", math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", G, 0.2, R), 2 * math.pi * 420.0))
    pres = mixc(nt, math_n(nt, "MULTIPLY", ramp(nt, tes, (0, 0, 0, 1), (1, 1, 1, 1), 0.3, 1.0), 0.12), pres, "#6e4c2e")
    pres = mixc(nt, 0.35, pres, "#7d6a55")                    # odlezalo drvo: celo posivi
    pres = mixc(nt, puk, pres, "#3a2616")
    pres = mixc(nt, math_n(nt, "GREATER_THAN", rn, 0.9), pres, "#3b2a1e")
    # kora
    vk = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(math_n(nt, "MULTIPLY", R, 1.0), vk.inputs["X"])
    nt.links.new(math_n(nt, "MULTIPLY", G, 0.18), vk.inputs["Y"])
    nt.links.new(math_n(nt, "MULTIPLY", A, 7.0), vk.inputs["Z"])          # seme po cepanici
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 70.0
    nt.links.new(vk.outputs["Vector"], vo.inputs["Vector"])
    brazda = ramp(nt, vo.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.02, 0.09)
    kora = ramp(nt, noise(nt, vk.outputs["Vector"], 40.0, 5, 0.6).outputs["Fac"], "#4a3626", "#6e5a47", 0.35, 0.7)
    kora = mixc(nt, ramp(nt, noise(nt, co, 6.0, 3).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.6, 0.75), kora, "#77746b")
    kora = mixc(nt, brazda, kora, "#1e1610")
    col = mixc(nt, B, kora, pres)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    ugalj = math_n(nt, "GREATER_THAN", sep.outputs["Z"], 0.95)
    col = mixc(nt, math_n(nt, "MULTIPLY", ugalj, 0.85), col, "#141010")
    nt.links.new(col, p.inputs["Base Color"])
    # ugljenisane cepanice u komori: koza kao krokodilska (Voronoi ivice), pukotine tinjaju (samo emisija;
    # albedo za sajt ostaje isti)
    vu = nt.nodes.new("ShaderNodeTexVoronoi")
    vu.feature = "DISTANCE_TO_EDGE"
    vu.inputs["Scale"].default_value = 85.0
    nt.links.new(co, vu.inputs["Vector"])
    tinja = math_n(nt, "MULTIPLY", ramp(nt, vu.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.045),
                   ramp(nt, noise(nt, co, 4.0, 3).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.4, 0.7))
    tinja = math_n(nt, "MULTIPLY", tinja, ugalj)
    nt.links.new(ramp(nt, tinja, "#3a0a00", "#ff6a10", 0.0, 1.0), p.inputs["Emission Color"])
    nt.links.new(math_n(nt, "MULTIPLY", tinja, 4.0), p.inputs["Emission Strength"])
    hgt = math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", brazda, math_n(nt, "SUBTRACT", 1.0, B)), puk)
    hgt = math_n(nt, "MAXIMUM", hgt, math_n(nt, "MULTIPLY", tinja, 0.8))
    n1 = bump(nt, math_n(nt, "MULTIPLY", noise(nt, vk.outputs["Vector"], 25.0, 5, 0.65).outputs["Fac"],
                         math_n(nt, "SUBTRACT", 1.0, B)), 0.5, 0.004, bevel_n(nt, 0.006))
    nt.links.new(bump(nt, hgt, -0.5, 0.004, n1), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", B, -0.1, 0.92), p.inputs["Roughness"])
    return m


# ---- foto varijante (samo Cycles kadar "ofen"; sajt i bake koriste gornje materijale, vidi foto_sloj())
def mat_gvozdje_foto(name):
    """Pocrnelo gvozdje iz rusty_metal_02 (plocica 0,9 m): siva boja fotografije postaje skoro crno gvozdje,
    rdja (zasicena mesta) tamno smedja i mat; izlizane ivice i izglacan pojas lopate na pragu kao u mat_gvozdje."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    t = pbr(nt, "rusty_metal_02", 0.9, 0.9, nor_s=0.6)
    hsv = nt.nodes.new("ShaderNodeSeparateColor")
    hsv.mode = "HSV"
    nt.links.new(t["diff"], hsv.inputs["Color"])
    rdj = ramp(nt, hsv.outputs["Green"], (0, 0, 0, 1), (1, 1, 1, 1), 0.3, 0.6)
    gv = ramp(nt, hsv.outputs["Blue"], "#191512", "#3a332d", 0.4, 0.9)
    base = mixc(nt, math_n(nt, "MULTIPLY", rdj, 0.85), gv, "#3a2014")
    nb = bevel_na(nt, t["nor"], 0.012)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(nb, dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    ivica_ = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), 6.0, clamp=True)
    ivica_ = math_n(nt, "MULTIPLY", ivica_, math_n(nt, "MULTIPLY_ADD", noise(nt, co, 40.0, 3).outputs["Fac"], 0.8, 0.2))
    pos = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], pos.inputs["Vector"])
    gn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], gn.inputs["Vector"])
    prag = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", gn.outputs["Z"], 0.8),
                  math_n(nt, "LESS_THAN", math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", pos.outputs["X"], PCX)), 0.4))
    prag = math_n(nt, "MULTIPLY", prag, math_n(nt, "GREATER_THAN", pos.outputs["Y"], PY0 - 0.21))
    prag = math_n(nt, "MULTIPLY", prag, math_n(nt, "LESS_THAN", math_n(nt, "ABSOLUTE",
                  math_n(nt, "SUBTRACT", pos.outputs["Z"], O_Z0 - 0.02)), 0.03))
    prag = math_n(nt, "MULTIPLY", prag, ramp(nt, noise(nt, co, 18.0, 4).outputs["Fac"], (0.3, 0.3, 0.3, 1),
                                             (1, 1, 1, 1), 0.35, 0.6))
    hab = math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", math_n(nt, "MINIMUM", ivica_, 1.0), prag),
                 math_n(nt, "SUBTRACT", 1.0, rdj))
    nt.links.new(mixc(nt, hab, base, "#77706a"), p.inputs["Base Color"])
    nt.links.new(nb, p.inputs["Normal"])
    r_ = math_n(nt, "MULTIPLY_ADD", t["rough"], 0.35, math_n(nt, "MULTIPLY_ADD", rdj, 0.25, 0.42))
    nt.links.new(math_n(nt, "MULTIPLY_ADD", hab, -0.25, r_, clamp=True), p.inputs["Roughness"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", rdj, -0.55, math_n(nt, "MULTIPLY_ADD", hab, 0.3, 0.65), clamp=True),
                 p.inputs["Metallic"])
    return m


def mat_drvo_foto(name, k=1.15):
    """Drvo radnje (pult, lopata, polica, rukohvat) iz wood_table_worn (plocica 1,2 m), boja puta k."""
    m, nt, p = node_mat(name)
    t = pbr(nt, "wood_table_worn", 1.2, 1.2, nor_s=0.8)
    nt.links.new(skala(nt, t["diff"], k), p.inputs["Base Color"])
    nt.links.new(bevel_na(nt, t["nor"], 0.005), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", t["rough"], 0.5, 0.35), p.inputs["Roughness"])
    return m


def mat_sto_foto(name):
    """Ploca stola: wood_table_worn posvetljen u bukvu, preko njega ogrebotine od noza i brasno kao u mat_sto."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    t = pbr(nt, "wood_table_worn", 1.2, 1.2, nor_s=0.8)
    hs = nt.nodes.new("ShaderNodeHueSaturation")
    hs.inputs["Saturation"].default_value = 0.85
    nt.links.new(skala(nt, t["diff"], 3.0), hs.inputs["Color"])
    wood = hs.outputs["Color"]
    ogr = ogrebotine(nt, co, 7.0, 0.02, 0.45)
    wood = mixc(nt, math_n(nt, "MULTIPLY", ogr, 0.7), wood, "#dcb98e")
    mask = ramp(nt, noise(nt, co, 3.2, 6, 0.65).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.5, 0.66)
    posip = ramp(nt, noise(nt, co, 38.0, 4, 0.7).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.58, 0.68)
    fl_m = math_n(nt, "MAXIMUM", mask, math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", posip, ogr), 0.55))
    nt.links.new(mixc(nt, fl_m, wood, BRASNO), p.inputs["Base Color"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", fl_m, 0.2, math_n(nt, "MULTIPLY_ADD", t["rough"], 0.3, 0.5)),
                 p.inputs["Roughness"])
    n1 = bump(nt, math_n(nt, "SUBTRACT", 1.0, ogr), 0.25, 0.0008, bevel_na(nt, t["nor"], 0.008))
    nt.links.new(bump(nt, fl_m, 0.2, 0.0006, n1), p.inputs["Normal"])
    return m


def mat_zar_foto(name):
    """Zar za fotografiju (zar_pec ostaje za sajt): nepravilni grumeni uglja sa crnom korom i malo sivog pepela,
    a svetle samo pukotine i procepi izmedju grumena (AO). Boja je Blackbody 900-1300 K po toploti, jacina je
    "Emission Strength" (KRUME_OFEN_EM). Grumeni su u geometriji (Subdivision + Displace, foto_sloj())."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    vo = nt.nodes.new("ShaderNodeTexVoronoi")             # pukotine kore: Voronoi ivice, isprekidane sumom
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 30.0
    vo.inputs["Randomness"].default_value = 0.85
    nt.links.new(co, vo.inputs["Vector"])
    puk = math_n(nt, "MULTIPLY", ramp(nt, vo.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.045),
                 ramp(nt, noise(nt, co, 9.0, 3).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.42, 0.6))
    # tinjanje ispod pepela: nepravilna polja koja svetle tamnocrveno (ne mreza linija)
    tinja = ramp(nt, noise(nt, co, 14.0, 6, 0.7).outputs["Fac"], (0, 0, 0, 1), (0.55, 0.55, 0.55, 1), 0.55, 0.75)
    procep = math_n(nt, "POWER", supljina(nt, 0.04), 1.6)  # izmedju grumena je najtoplije
    zona = ramp(nt, noise(nt, co, 2.2, 4, 0.55).outputs["Fac"], (0.3, 0.3, 0.3, 1), (1, 1, 1, 1), 0.35, 0.7)
    heat = math_n(nt, "MAXIMUM", math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", puk, 0.75), tinja), procep)
    heat = math_n(nt, "MULTIPLY", heat, zona, clamp=True)
    bb = nt.nodes.new("ShaderNodeBlackbody")
    nt.links.new(math_n(nt, "MULTIPLY_ADD", heat, 400.0, 850.0), bb.inputs["Temperature"])
    nt.links.new(bb.outputs["Color"], p.inputs["Emission Color"])
    em = nt.nodes.new("ShaderNodeValue")                  # jacina (menja je render petlja)
    em.name, em.outputs[0].default_value = "jacina", 6.0
    nt.links.new(math_n(nt, "MULTIPLY", math_n(nt, "POWER", heat, 2.2), em.outputs[0]), p.inputs["Emission Strength"])
    p.inputs["Emission Strength"].default_value = 1.0
    gn = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(nt.nodes.new("ShaderNodeNewGeometry").outputs["Normal"], gn.inputs["Vector"])
    pepeo = math_n(nt, "MULTIPLY", ramp(nt, noise(nt, co, 11.0, 5, 0.6).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1),
                                        0.55, 0.75), math_n(nt, "MAXIMUM", gn.outputs["Z"], 0.0))
    pepeo = math_n(nt, "MULTIPLY", pepeo, math_n(nt, "SUBTRACT", 1.0, heat), clamp=True)
    kora = ramp(nt, noise(nt, co, 40.0, 4).outputs["Fac"], "#0b0908", "#1c1714", 0.3, 0.7)
    nt.links.new(mixc(nt, math_n(nt, "MULTIPLY", pepeo, 0.8), kora, "#5d5752"), p.inputs["Base Color"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", pepeo, 0.1, 0.82), p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.3
    n1 = bump(nt, noise(nt, co, 60.0, 5, 0.65).outputs["Fac"], 0.4, 0.002)
    nt.links.new(bump(nt, math_n(nt, "SUBTRACT", 1.0, puk), 0.6, 0.004, n1), p.inputs["Normal"])
    return m


def mat_vrata_foto(name, unutra=False):
    """Krug 3: vrata peci kao teško liveno gvozdje (samo foto kadar). rusty_metal_02 (plocica 0,6 m) daje rdju i
    rupice, preko toga livacka kora: krupno zrno peska i sitne pore (Voronoi), sve kao bump. Lokalni z vrata
    (0 na sarki, ~0,74 na temenu luka): gornja ivica je nagaravljena od plamena, ivice izlizane do sjajnog
    gvozdja. unutra=True: strana ka vatri (stit i rebra), skoro cela pod cadji i pahuljama pepela."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    t = pbr(nt, "rusty_metal_02", 0.6, 0.6, nor_s=0.7)
    hsv = nt.nodes.new("ShaderNodeSeparateColor")
    hsv.mode = "HSV"
    nt.links.new(t["diff"], hsv.inputs["Color"])
    rdj = ramp(nt, hsv.outputs["Green"], (0, 0, 0, 1), (1, 1, 1, 1), 0.28, 0.6)
    # livacka kora: zrno peska i pore (samo neke Voronoi celije postaju rupica)
    zrno = noise(nt, co, 420.0, 5, 0.7).outputs["Fac"]
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.inputs["Scale"].default_value = 160.0
    nt.links.new(co, vo.inputs["Vector"])
    pora = math_n(nt, "MULTIPLY", ramp(nt, vo.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.0, 0.22),
                  math_n(nt, "GREATER_THAN", _bw(nt, vo.outputs["Color"]), 0.72))
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    # cadj: gornja ivica (lokalni z) u jezicima plamena, gusca u udubljenjima
    jez = noise(nt, co, 9.0, 4, 0.6).outputs["Fac"]
    cadj = math_n(nt, "ADD", math_n(nt, "MULTIPLY", sep.outputs["Z"], 2.2),
                  math_n(nt, "MULTIPLY_ADD", jez, 0.9, -1.25))
    cadj = math_n(nt, "MINIMUM", math_n(nt, "MAXIMUM", cadj, 0.0), 1.0)
    cav = supljina(nt, 0.03)
    cadj = math_n(nt, "MAXIMUM", cadj, math_n(nt, "MULTIPLY", cav, 0.8))
    if unutra:
        cadj = math_n(nt, "MAXIMUM", cadj, ramp(nt, noise(nt, co, 6.0, 4).outputs["Fac"], (0.55, 0.55, 0.55, 1),
                                                (0.95, 0.95, 0.95, 1), 0.3, 0.7))
    gv = ramp(nt, hsv.outputs["Blue"], "#1a1613", "#36302b", 0.45, 0.95)
    gv = mixc(nt, math_n(nt, "MULTIPLY", zrno, 0.35), gv, "#100d0b")
    col = mixc(nt, math_n(nt, "MULTIPLY", rdj, 0.8), gv, "#3b1f12")
    col = mixc(nt, math_n(nt, "MULTIPLY", pora, 0.85), col, "#080605")
    col = mixc(nt, math_n(nt, "MULTIPLY", cadj, 0.92), col, "#0a0807")
    pep = math_n(nt, "MULTIPLY", ramp(nt, noise(nt, co, 26.0, 5, 0.7).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1),
                                      0.6, 0.72), 0.55 if unutra else 0.2)
    col = mixc(nt, math_n(nt, "MULTIPLY", pep, cadj), col, "#4a4540")
    # izlizane ivice: Bevel naspram prave normale, isprekidano; na cadji i rdji slabije
    nb = bevel_na(nt, t["nor"], 0.01)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dot = nt.nodes.new("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    nt.links.new(nb, dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    hab = math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), 7.0, clamp=True)
    hab = math_n(nt, "MULTIPLY", hab, ramp(nt, noise(nt, co, 30.0, 4).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1),
                                           0.4, 0.62))
    hab = math_n(nt, "MULTIPLY", hab, math_n(nt, "SUBTRACT", 1.0, math_n(nt, "MULTIPLY", rdj, 0.7)))
    hab = math_n(nt, "MULTIPLY", hab, 0.35 if unutra else 0.9)
    nt.links.new(mixc(nt, hab, col, "#6f6a64"), p.inputs["Base Color"])
    vis = math_n(nt, "ADD", math_n(nt, "MULTIPLY", zrno, 0.5), math_n(nt, "MULTIPLY", pora, -1.0))
    vis = math_n(nt, "ADD", vis, math_n(nt, "MULTIPLY", rdj, -0.35))
    nt.links.new(bump(nt, vis, 0.7, 0.0015, nb), p.inputs["Normal"])
    r_ = math_n(nt, "MULTIPLY_ADD", t["rough"], 0.25, math_n(nt, "MULTIPLY_ADD", rdj, 0.2, 0.55))
    r_ = math_n(nt, "MULTIPLY_ADD", cadj, 0.25, r_)
    nt.links.new(math_n(nt, "MULTIPLY_ADD", hab, -0.35, r_, clamp=True), p.inputs["Roughness"])
    met = math_n(nt, "MULTIPLY_ADD", cadj, -0.45, math_n(nt, "MULTIPLY_ADD", rdj, -0.45, 0.6))
    nt.links.new(math_n(nt, "MULTIPLY_ADD", hab, 0.5, met, clamp=True), p.inputs["Metallic"])
    return m


def mat_mesing_foto(name):
    """Mesing posle godina uz pec: potamneo, braon patina u mrljama, svetao samo gde ga ruka dodiruje (ivice)."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    pat = ramp(nt, noise(nt, co, 35.0, 5, 0.65).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.4, 0.65)
    hab = ivica(nt, 0.004, 6.0)
    col = mixc(nt, math_n(nt, "MULTIPLY", pat, 0.85), "#5e4421", "#2a1d10")
    nt.links.new(mixc(nt, hab, col, "#a07a3c"), p.inputs["Base Color"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", pat, 0.3, math_n(nt, "MULTIPLY_ADD", hab, -0.2, 0.45)), p.inputs["Roughness"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", pat, -0.5, 0.95), p.inputs["Metallic"])
    nt.links.new(bump(nt, noise(nt, co, 200.0, 4).outputs["Fac"], 0.2, 0.0008), p.inputs["Normal"])
    return m


def _bw(nt, col):
    bw_ = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(col, bw_.inputs["Color"])
    return bw_.outputs["Val"]


def mat_cepanica_foto(name):
    """Krug 3: cepanice u nisi za fotografiju (pile_drva_foto). Atribut "drvo" = (x, y, vrsta, R): na celu x, y
    od srzi, vrsta 1; na kori (luk, duz ose) vrsta 0; na cepanoj strani (preko, duz ose) vrsta 0,5. Atribut
    "drvo_s" (R) je seme komada: svaka cepanica ima svoj ton, sivilo, gustinu godova i svoje pukotine."""
    m, nt, p = node_mat(name)
    co = obj_co(nt)
    at = nt.nodes.new("ShaderNodeAttribute")
    at.attribute_name = "drvo"
    sp = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(at.outputs["Color"], sp.inputs["Color"])
    X, Y, B, A = sp.outputs["Red"], sp.outputs["Green"], sp.outputs["Blue"], at.outputs["Alpha"]
    at2 = nt.nodes.new("ShaderNodeAttribute")
    at2.attribute_name = "drvo_s"
    sp2 = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(at2.outputs["Color"], sp2.inputs["Color"])
    seme = sp2.outputs["Red"]

    def rnd(off):
        wn = nt.nodes.new("ShaderNodeTexWhiteNoise")
        wn.noise_dimensions = "1D"
        nt.links.new(math_n(nt, "ADD", seme, off), wn.inputs["W"])
        return wn.outputs["Value"]

    celo = math_n(nt, "GREATER_THAN", B, 0.75)
    cepano = math_n(nt, "MULTIPLY", math_n(nt, "GREATER_THAN", B, 0.25), math_n(nt, "LESS_THAN", B, 0.75))
    v2 = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(X, v2.inputs["X"])
    nt.links.new(Y, v2.inputs["Y"])
    nt.links.new(math_n(nt, "MULTIPLY", seme, 3.7), v2.inputs["Z"])
    sep2 = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(X, sep2.inputs["X"])
    nt.links.new(Y, sep2.inputs["Y"])
    ln2 = nt.nodes.new("ShaderNodeVectorMath")
    ln2.operation = "LENGTH"
    nt.links.new(sep2.outputs["Vector"], ln2.inputs[0])
    r = ln2.outputs["Value"]
    rn = math_n(nt, "DIVIDE", r, A)
    nzr = noise(nt, v2.outputs["Vector"], 22.0, 4, 0.6).outputs["Fac"]
    # godovi: 7-14 mm, krivudavi (sum), kasno drvo tamna tanka linija
    gust = math_n(nt, "MULTIPLY_ADD", rnd(0.1), 70.0, 70.0)
    god = math_n(nt, "FRACT", math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", nzr, 0.014, r), gust))
    god = ramp(nt, god, (0, 0, 0, 1), (1, 1, 1, 1), 0.72, 0.95)
    svetlo, tamno = "#866649", "#3e2c1e"
    pres = mixc(nt, math_n(nt, "MULTIPLY", _bw(nt, god), 0.85), svetlo, tamno)
    pres = mixc(nt, math_n(nt, "MULTIPLY", ramp(nt, rn, (1, 1, 1, 1), (0, 0, 0, 1), 0.15, 0.55), rnd(0.2)), pres,
                "#4a3324")                                                    # tamnija srz, ne kod svake
    # sivilo odlezalog drveta i prljavstina: svaka cepanica drugacije
    siv = math_n(nt, "MULTIPLY_ADD", rnd(0.3), 0.4, 0.1)
    mrlja = ramp(nt, noise(nt, v2.outputs["Vector"], 9.0, 5, 0.65).outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1), 0.4, 0.7)
    pres = mixc(nt, math_n(nt, "MULTIPLY", siv, math_n(nt, "MULTIPLY_ADD", mrlja, 0.5, 0.6), clamp=True), pres,
                "#6a6259")
    # tragovi testere (blago zakrivljeni lukovi lancane testere)
    tes = math_n(nt, "SINE", math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", nzr, 0.006,
                                                         math_n(nt, "MULTIPLY_ADD", X, 0.3, Y)), 2 * math.pi * 260.0))
    pres = mixc(nt, math_n(nt, "MULTIPLY", ramp(nt, tes, (0, 0, 0, 1), (1, 1, 1, 1), 0.4, 1.0),
                           math_n(nt, "MULTIPLY", rnd(0.4), 0.2)), pres, "#3e2e21")
    # radijalne pukotine od suvljenja: tri po komadu, svaka svoj ugao, duzina (od kore ka srzi) i sirina
    puk = None
    for k_ in range(3):
        a_ = math_n(nt, "MULTIPLY", rnd(1.0 + k_), 2 * math.pi)
        s_, c_ = math_n(nt, "SINE", a_), math_n(nt, "COSINE", a_)
        duz = math_n(nt, "ADD", math_n(nt, "MULTIPLY", X, c_), math_n(nt, "MULTIPLY", Y, s_))
        pop = math_n(nt, "ABSOLUTE", math_n(nt, "SUBTRACT", math_n(nt, "MULTIPLY", Y, c_), math_n(nt, "MULTIPLY", X, s_)))
        pop = math_n(nt, "ADD", pop, math_n(nt, "MULTIPLY", math_n(nt, "SUBTRACT", nzr, 0.5), 0.006))
        poc = math_n(nt, "MULTIPLY", A, math_n(nt, "MULTIPLY_ADD", rnd(2.0 + k_), 0.75, 0.05))    # odakle krece
        sir = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY_ADD", rnd(3.0 + k_), 0.004, 0.0015),
                     math_n(nt, "DIVIDE", math_n(nt, "SUBTRACT", duz, poc), math_n(nt, "MAXIMUM", math_n(nt, "SUBTRACT", A, poc), 0.005)))
        p_ = math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", pop, sir), math_n(nt, "GREATER_THAN", duz, poc))
        p_ = math_n(nt, "MULTIPLY", p_, math_n(nt, "GREATER_THAN", rnd(5.0 + k_), 0.25 if k_ else 0.0))
        puk = p_ if puk is None else math_n(nt, "MAXIMUM", puk, p_)
    pres = mixc(nt, puk, pres, "#120c08")
    # beljika (svetliji prsten) i kora po obodu cela; tamnija ivica cela (prljavstina, upijena vlaga)
    pres = mixc(nt, math_n(nt, "MULTIPLY", ramp(nt, rn, (0, 0, 0, 1), (1, 1, 1, 1), 0.78, 0.86), 0.35), pres, "#8a7258")
    kora_r = math_n(nt, "GREATER_THAN", rn, math_n(nt, "MULTIPLY_ADD", nzr, 0.04, 0.9))
    pres = mixc(nt, kora_r, pres, "#2b2019")
    pres = mixc(nt, math_n(nt, "MULTIPLY", math_n(nt, "LESS_THAN", r, 0.0035), 0.8), pres, "#2a1c12")   # srz
    # kora: uzduzne brazde i ploce, poneka cepanica bez kore (oljuštena mesta)
    vk = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(X, vk.inputs["X"])
    nt.links.new(math_n(nt, "MULTIPLY", Y, 0.18), vk.inputs["Y"])
    nt.links.new(math_n(nt, "MULTIPLY", seme, 7.0), vk.inputs["Z"])
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 70.0
    nt.links.new(vk.outputs["Vector"], vo.inputs["Vector"])
    brazda = ramp(nt, vo.outputs["Distance"], (1, 1, 1, 1), (0, 0, 0, 1), 0.02, 0.09)
    kora = ramp(nt, noise(nt, vk.outputs["Vector"], 40.0, 5, 0.6).outputs["Fac"], "#3a2b20", "#5a4a3c", 0.35, 0.7)
    kora = mixc(nt, brazda, kora, "#140f0b")
    oljust = math_n(nt, "MULTIPLY", ramp(nt, noise(nt, vk.outputs["Vector"], 6.0, 3).outputs["Fac"], (0, 0, 0, 1),
                                         (1, 1, 1, 1), 0.55, 0.6), rnd(6.0))
    # cepana strana: vlakna duz ose, sivo-smedja
    vl = nt.nodes.new("ShaderNodeMapping")
    vl.inputs["Scale"].default_value = (60.0, 2.0, 1.0)
    nt.links.new(vk.outputs["Vector"], vl.inputs["Vector"])
    vlak = noise(nt, vl.outputs["Vector"], 3.0, 6, 0.7).outputs["Fac"]
    cep = ramp(nt, vlak, "#4d3b2c", "#7a6650", 0.3, 0.75)
    kora = mixc(nt, oljust, kora, cep)
    col = mixc(nt, cepano, kora, cep)
    col = mixc(nt, celo, col, pres)
    # ton po komadu (neke tamnije, neke svetlije), pa AO izmedju cepanica
    col = skala(nt, col, math_n(nt, "MULTIPLY_ADD", rnd(7.0), 0.5, 0.55))
    cav = supljina(nt, 0.05)
    col = mixc(nt, math_n(nt, "MULTIPLY", cav, 0.75), col, "#0b0806")
    nt.links.new(col, p.inputs["Base Color"])
    hgt = math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", brazda, math_n(nt, "SUBTRACT", 1.0, celo)), puk)
    hgt = math_n(nt, "ADD", hgt, math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", vlak, cepano), 0.6))
    n1 = bump(nt, math_n(nt, "MULTIPLY", noise(nt, vk.outputs["Vector"], 25.0, 5, 0.65).outputs["Fac"],
                         math_n(nt, "SUBTRACT", 1.0, celo)), 0.5, 0.004, bevel_n(nt, 0.005))
    n1 = bump(nt, math_n(nt, "MULTIPLY", _bw(nt, god), celo), 0.15, 0.0008, n1)
    nt.links.new(bump(nt, hgt, -0.6, 0.003, n1), p.inputs["Normal"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", celo, 0.04, 0.88), p.inputs["Roughness"])
    p.inputs["Specular IOR Level"].default_value = 0.35
    return m


M.update({
    "zid": mat_plaster("zid_unutra", "#ddd2bf", var=0.06, bump_s=0.25),
    "plafon": mat_plaster("plafon", "#d6cbb8", var=0.05, bump_s=0.2),
    "presek": mat_presek("presek_kora"),
    "zid_gore": mat_plaster("zid_magacin", "#a39a8c", var=0.1, bump_s=0.4),
    "pod": mat_tiles("pod", "#5c524b", "#665a51", "#221c18", 1.6, rough=0.55),          # neutralno sivo-smedje
    "plocice": mat_tiles("plocice", "#c3cbbf", "#bcc5b8", "#7a8077", 6.0, wall=True, rough=0.25, b_s=0.5),  # hladno
    "daske_pod": mat_drvo("daske_pod", "#5e4b3b", "#76604b", rough=0.8, axis="X", scale=9.0),
    "pult": mat_drvo("pult_drvo", "#3a281b", "#62452e", rough=0.4, axis="X", scale=11.0, coat=0.3, vlakno=0.8),   # tamni orah
    "pult_daska": mat_drvo("pult_daska", "#8f6440", "#b4875a", rough=0.6, axis="X", scale=16.0, vlakno=0.6),        # topla bukva
    "samot": mat_samot("samot_pod"),
    "gvozdje_cadj": mat_simple("gvozdje_cadj", "#16110e", rough=0.85, metal=0.3),
    "cigla": mat_cigla("cigla", otvor=True),
    "cadj": mat_cigla("cadj", "#3b2116", "#2c1810", "#4a3a2e"),       # zagorela cigla u komori
    "gvozdje": mat_gvozdje("gvozdje", "#26211e", "#3d3530", "#8a8279"),
    "mesing": mat_simple("mesing", "#b8873a", rough=0.3, metal=1.0),
    "zar": mat_zar("zar_pec", 2.6),
    "testo": mat_testo("testo"),
    "testo_korpa": mat_testo("testo_korpa", flour=0.8),
    "brasno": mat_plaster("brasno", BRASNO, var=0.03, bump_s=0.4, rough=1.0),
    "sto": mat_sto("sto_ploca"),
    "platno": mat_tkanina("platno", "#e2d6bf", 700.0, 0.2),
    "juta": mat_tkanina("juta", "#a88d64", 260.0, 0.6),
    "pruce": mat_pruce("pruce"),
    "drva": mat_cepanica("drva"),
    "emajl": mat_simple("emajl", "#22382c", rough=0.25, coat=0.6),
    "emajl_unutra": mat_simple("emajl_unutra", "#f1ece2", rough=0.35),
    "sijalica": mat_simple("sijalica", "#ffe7c4", emit="#ffcf96", strength=40.0),
    "so": mat_simple("so", "#f3f0ea", rough=0.25),
    "k_semmel": mat_kora("kora_semmel", "#e2b46f", "#9a5a25", 0.6, "semmel"),
    "k_mak": mat_kora("kora_mohn", "#d9a660", "#8c5222", 0.55, "mak"),
    "k_lauge": mat_kora("kora_lauge", "#7a3a14", "#3a1806", 0.22, "lauge"),
    "k_roggen": mat_kora("kora_roggen", "#6b4426", "#2e1c10", 0.75, "roggen"),
    "krume_rog": mat_krume("krume_roggen", "#7d6248", "#937455"),
    "nebo_napolju": mat_simple("nebo_napolju", "#0b0f18", rough=1.0, emit="#1c2639", strength=0.6),
})
# foto materijali (PBR teksture): grade se samo bez KRUME_WEB, a dodeljuju samo za kadar "ofen" (foto_sloj)
FOTO = not os.environ.get("KRUME_WEB")
M_FOTO = {}


def potamni(mat, name, k, em=1.0):
    """Kopija materijala sa Base Color puta k (samo foto kadar: svetle povrsine koje u noci ne smeju da vode),
    em: faktor emisije (tinjanje cepanica u komori)."""
    m2 = mat.copy()
    m2.name = name
    nt = m2.node_tree
    p = nt.nodes["Principled BSDF"]
    nt.links.new(skala(nt, p.inputs["Base Color"].links[0].from_socket, k), p.inputs["Base Color"])
    if em != 1.0 and p.inputs["Emission Strength"].links:
        nt.links.new(math_n(nt, "MULTIPLY", p.inputs["Emission Strength"].links[0].from_socket, em),
                     p.inputs["Emission Strength"])
    return m2


if FOTO:
    M_FOTO = {
        "cigla": mat_cigla("cigla_foto", otvor=True, foto=float(os.environ.get("KRUME_CIGLA", "0.5"))),
        "cadj": mat_cigla("cadj_foto", foto=0.16),
        "gvozdje": mat_gvozdje_foto("gvozdje_foto"),
        "drvo_radnja": mat_drvo_foto("drvo_radnja_foto"),
        "sto_ploca": mat_sto_foto("sto_ploca_foto"),
        "zar_pec": mat_zar_foto("zar_foto"),
        "drva": potamni(M["drva"], "drva_foto", 0.45, em=2.5),          # cela cepanica ne sme da bude svetlija od zara
        "zid_unutra": potamni(M["zid"], "zid_unutra_foto", 0.4),  # svetao zid gore levo (naslov "Ofen.")
        # krug 3: vrata peci (samo na objektu PecVrata, vidi VRATA_FOTO), mesing, cepanice u nisi
        "vrata": mat_vrata_foto("vrata_foto"),
        "vrata_unutra": mat_vrata_foto("vrata_unutra_foto", unutra=True),
        "mesing": mat_mesing_foto("mesing_foto"),
        "drva_nisa": mat_cepanica_foto("drva_nisa_foto"),
    }


# ---------------------------------------------------------------- geometrija
def jitter_q(deg=0.5):
    a = math.radians(deg)
    return Euler((random.uniform(-a, a) * 0.5, random.uniform(-a, a) * 0.5, random.uniform(-a, a))).to_quaternion()


class Builder:
    """Skuplja delove jednog materijala u jedan mesh; bevel kao u kitu (rucno sece maketu)."""

    def __init__(self, name, mat, bevel=0.02, seg=2, smooth=False, coll=C_ENT):
        self.name, self.mat, self.bevel, self.seg, self.smooth, self.coll = name, mat, bevel, seg, smooth, coll
        self.bm = bmesh.new()

    def finish(self, origin=None, shift=True):
        """origin: pivot objekta. shift=True kad je mesh gradjen u svetu, False kad je vec lokalan."""
        bm = self.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            f.smooth = self.smooth
        if origin is not None and shift:
            bmesh.ops.translate(bm, verts=bm.verts, vec=-Vector(origin))
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(self.name, me)
        self.coll.objects.link(ob)
        ob.parent = KOREN
        if origin is not None:
            ob.location = origin
        for mt in (self.mat if isinstance(self.mat, (list, tuple)) else [self.mat]):
            me.materials.append(mt)
        if self.bevel > 0:
            bv = ob.modifiers.new("Bevel", "BEVEL")
            bv.width, bv.segments = self.bevel, self.seg
            bv.limit_method = "ANGLE"
            bv.angle_limit = math.radians(35)
        return ob


def box(b, center, size, rot=0.0, jit=True, mat=0):
    q = Quaternion((0, 0, 1), rot)
    c = Vector(center)
    if jit:
        q = q @ jitter_q()
        c += Vector([random.uniform(-0.004, 0.004) for _ in range(3)])
    r = bmesh.ops.create_cube(b.bm, size=1.0, matrix=Matrix.LocRotScale(c, q, Vector(size)))
    for v in r["verts"]:
        for f in v.link_faces:
            f.material_index = mat
    return r["verts"]


def bx(b, x0, y0, z0, x1, y1, z1, jit=True, mat=0):
    """Kutija iz dva ugla (lakse za citanje rasporeda)."""
    return box(b, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), jit=jit, mat=mat)


def lathe(b, center, profile, seg=16, rot=0.0, sx=1.0, sy=1.0, caps=True):
    """Telo okretanja: profil (r, z); r=0 na krajevima zatvara vrh/dno, caps=False ostavlja otvoren rub."""
    bm = b.bm
    cx, cy, cz = center
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((cx, cy, cz + z))])
        else:
            rings.append([bm.verts.new((cx + sx * r * math.cos(rot + 2 * math.pi * i / seg),
                                        cy + sy * r * math.sin(rot + 2 * math.pi * i / seg), cz + z))
                          for i in range(seg)])
    for ra, rb in zip(rings, rings[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            if len(ra) == 1:
                bm.faces.new((ra[0], rb[i], rb[j]))
            elif len(rb) == 1:
                bm.faces.new((ra[i], ra[j], rb[0]))
            else:
                bm.faces.new((ra[i], ra[j], rb[j], rb[i]))
    if caps and len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if caps and len(rings[-1]) > 1:
        bm.faces.new(rings[-1])


def cyl(b, p0, p1, r, seg=10):
    """Valjak izmedju dve tacke (drska, nogica, cepanica)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    q = d.to_track_quat("Z", "Y")
    r_ = bmesh.ops.create_cone(b.bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length,
                               matrix=Matrix.LocRotScale((p0 + p1) / 2, q, Vector((1, 1, 1))))
    return r_["verts"]


def ellipsoid(b, center, size, rot=0.0, seg=(14, 9), jit=4):
    q = Quaternion((0, 0, 1), rot) @ jitter_q(jit)
    bmesh.ops.create_uvsphere(b.bm, u_segments=seg[0], v_segments=seg[1], radius=0.5,
                              matrix=Matrix.LocRotScale(Vector(center), q, Vector(size)))


def prism(b, poly, z0, z1, mat=0):
    bm = b.bm
    ra = [bm.verts.new((x, y, z0)) for x, y in poly]
    rb = [bm.verts.new((x, y, z1)) for x, y in poly]
    fs = [bm.faces.new(list(reversed(ra))), bm.faces.new(rb)]
    k = len(ra)
    for i in range(k):
        j = (i + 1) % k
        fs.append(bm.faces.new((ra[i], ra[j], rb[j], rb[i])))
    for f in fs:
        f.material_index = mat


def clip(poly, axis, val, keep_ge=True):
    """Sutherland-Hodgman: deo konveksnog poligona sa jedne strane prave x=val ili y=val."""
    out = []
    k = len(poly)
    inside = (lambda p: p[axis] >= val - 1e-9) if keep_ge else (lambda p: p[axis] <= val + 1e-9)
    for i in range(k):
        a, c = poly[i], poly[(i + 1) % k]
        if inside(a):
            out.append(a)
        if inside(a) != inside(c):
            t = (val - a[axis]) / (c[axis] - a[axis])
            out.append((a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t))
    return out


def link(ob, coll=C_ENT):
    coll.objects.link(ob)
    ob.parent = KOREN
    return ob


def apply_mods(ob):
    """Primeni modifikatore (boolean, bevel) u mesh, da materijal preseka moze da se dodeli po licu."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    me.name = ob.name
    bpy.data.meshes.remove(old)


def boolean(ob, cutter):
    md = ob.modifiers.new("Rez", "BOOLEAN")
    md.operation, md.object, md.solver = "DIFFERENCE", cutter, "EXACT"
    md.use_self = True                       # delovi su namerno preklopljene kutije
    md.use_hole_tolerant = True
    ob.modifiers.move(len(ob.modifiers) - 1, 0)
    cutter.hide_render = True
    cutter.hide_viewport = True
    cutter.display_type = "WIRE"


def presek_lica(ob, slot):
    """Lica u ravni unutrasnjeg lica Kriske (y = 0,7, x = 0,7, x + y = 3,99, normala ka ulici) dobijaju
    materijal kore: kad se Kriska izvuce, to je presek kuce."""
    mw = ob.matrix_world
    d = 1 / math.sqrt(2)
    for f in ob.data.polygons:
        c, n = mw @ f.center, f.normal
        if ((n.y < -0.98 and abs(c.y - Y_CUT) < 0.012) or (n.x < -0.98 and abs(c.x - X_IN) < 0.012) or
                (n.x < -d + 0.02 and n.y < -d + 0.02 and abs(c.x + c.y - CH_IN) < 0.02)):
            f.material_index = slot


# ---------------------------------------------------------------- ljuska: unutrasnji zidovi, pod, plafoni
# Spoljni zidovi (fasade A i B, zakosen ugao, izlozi i vrata) su Kriska u kvartu. Ovde: pregradni i zadnji zid
# od dna poda do vrha otvora (z = 8,1) i tri ploce (pod, medjuspratna, plafon magacina) u tlocrtu do unutrasnjih
# lica Kriske. Spoljne strane zidova leze tacno na granici otvora (x = 11,3, y = 8,7), lice uz lice sa kvartom,
# ali okrenute od sobe, pa se ne vide (bake_enterijer.py ih brise pre izvoza).
b_zid = Builder("Zidovi", [M["zid"], M["presek"], M["zid_gore"]], bevel=0.015, seg=1)
prism(b_zid, [(X_PREG, Y_CUT), (X_OUT, Y_CUT), (X_OUT, Y_OUT), (X_PREG, Y_OUT)], Z_BOT, Z_TOP)
prism(b_zid, [(X_IN, Y_ZAD), (X_PREG, Y_ZAD), (X_PREG, Y_OUT), (X_IN, Y_OUT)], Z_BOT, Z_TOP)
ob_zid = b_zid.finish()
SLAB = [(CH_IN - Y_CUT, Y_CUT), (X_PREG, Y_CUT), (X_PREG, Y_ZAD), (X_IN, Y_ZAD), (X_IN, CH_IN - X_IN)]
b_pod = Builder("Pod", [M["presek"], M["pod"]], bevel=0.015, seg=1)
prism(b_pod, SLAB, Z_BOT, POD)
ob_pod = b_pod.finish()
b_plf = Builder("Plafon", [M["presek"], M["plafon"], M["daske_pod"], M["zid_gore"]], bevel=0.015, seg=1)
prism(b_plf, SLAB, PLAFON, SPRAT)
prism(b_plf, SLAB, PLAFON2, Z_TOP)
ob_plf = b_plf.finish()
for f in ob_pod.data.polygons:
    if f.normal.z > 0.9:
        f.material_index = 1
for f in ob_plf.data.polygons:
    if f.normal.z < -0.9:
        f.material_index = 1
    elif f.normal.z > 0.9 and f.center.z < SPRAT + 0.01:
        f.material_index = 2
    if f.normal.z < -0.9 and f.center.z > PLAFON2 - 0.01:
        f.material_index = 3
presek_lica(ob_zid, 1)                       # ploce: sva bocna lica su vec presek (slot 0)
# zid je jedno lice od z_bot do z_top: rez ga deli na pekaru (okrecen) i magacin (hladniji, neokrecen)
for ob in (ob_zid,):
    bm_ = bmesh.new()
    bm_.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm_, geom=bm_.verts[:] + bm_.edges[:] + bm_.faces[:], plane_co=(0, 0, SPRAT + 0.3),
                           plane_no=(0, 0, 1))
    bm_.to_mesh(ob.data)
    bm_.free()
    for f in ob.data.polygons:
        if f.material_index != 1 and abs(f.normal.z) < 0.5:
            f.material_index = 2 if f.center.z > SPRAT + 0.3 else 0

# lajsna, plocice do 1,5 m na zadnjem zidu i pregradi, dve grede na plafonu
b_lj = Builder("Lajsne", M["drvo_radnja"], bevel=0.008, seg=1)
b_plc = Builder("Plocice", M["plocice"], bevel=0.004, seg=1)
bx(b_plc, X_IN + 0.004, Y_ZAD - 0.02, POD, X_PREG, Y_ZAD, 1.6, jit=False)
bx(b_plc, X_PREG - 0.02, Y_CUT + 0.004, POD, X_PREG, Y_ZAD, 1.6, jit=False)
bx(b_lj, X_IN + 0.004, Y_ZAD - 0.04, 1.6, X_PREG, Y_ZAD, 1.66, jit=False)
bx(b_lj, X_PREG - 0.04, Y_CUT + 0.004, 1.6, X_PREG, Y_ZAD, 1.66, jit=False)
b_gr = Builder("Grede", M["drvo_radnja"], bevel=0.02, seg=2)
for x in (4.2, 7.6):
    bx(b_gr, x - 0.12, Y_CUT + 0.004, PLAFON - 0.24, x + 0.12, Y_ZAD, PLAFON)
# klupa izloga na fasadi B iznutra (izlog y 3,7 do 8,0 je u Kriski), sa zemickama
bx(b_lj, X_IN + 0.004, 3.75, 0.56, X_IN + 0.6, 7.95, 0.64)
b_hl = Builder("Izlog_hlebovi", M["hleb"], bevel=0, smooth=True)
for i in range(9):
    y = 4.05 + i * 0.46 + random.uniform(-0.05, 0.05)
    big = i % 3 == 1
    ellipsoid(b_hl, (X_IN + 0.27, y, 0.64 + (0.06 if big else 0.045)), (0.2, 0.34, 0.13) if big else (0.12, 0.12, 0.09),
              rot=math.pi / 2 + random.uniform(-0.3, 0.3), seg=(10, 6))
for b_ in (b_plc, b_gr, b_hl, b_lj):
    b_.finish()
# hladna noc iza preseka: samo tamna ravan neba daleko iza (na kvartu je zameni ulica)
b_nb = Builder("Pomocno_nebo", M["nebo_napolju"], bevel=0, coll=C_POM)
bx(b_nb, -6.0, -2.0, -0.5, -5.9, 14.0, 8.0, jit=False)
b_nb.finish()

# ---------------------------------------------------------------- pec (zidana, lucni otvor; mere PX0... gore)
b_pec = Builder("Pec", [M["cigla"], M["cadj"]], bevel=0.025, seg=2)
bx(b_pec, PX0, PY0, POD, PX1, PY1, 2.35, jit=False)
bx(b_pec, PX0 - 0.06, PY0 - 0.06, 2.35, PX1, PY1, 2.5, jit=False)          # venac od cigle
bx(b_pec, PX0 - 0.03, PY0 - 0.03, POD, PX1, PY1, POD + 0.18, jit=False)     # sokla
ob_pec = b_pec.finish()
b_prez = Builder("Rez_pec", M["cadj"], bevel=0, coll=C_POM)
bx(b_prez, PX0 + 0.45, PY0 + 0.55, O_Z0, PX1 - 0.4, PY1 - 0.35, O_Z0 + 0.62, jit=False)   # komora
lathe(b_prez, (0, 0, 0), [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)], seg=24)        # svod komore
b_prez.bm.verts.ensure_lookup_table()
vs = b_prez.bm.verts[-50:]
bmesh.ops.transform(b_prez.bm, verts=vs, matrix=Matrix.Translation((PCX, PY0 + 0.55, O_Z0 + 0.62)) @
                    Matrix.Rotation(-math.pi / 2, 4, "X") @ Matrix.Diagonal(((PX1 - PX0 - 0.85) / 2, 0.42, PY1 - PY0 - 0.9, 1)))
arch = [(-O_W / 2, 0.0), (O_W / 2, 0.0)] + [((O_W / 2) * math.cos(math.pi * i / 12), (O_H - O_W / 2) + (O_W / 2) * math.sin(math.pi * i / 12)) for i in range(13)]
ra = [b_prez.bm.verts.new((PCX + u, PY0 - 0.2, O_Z0 + v)) for u, v in arch]
rb = [b_prez.bm.verts.new((PCX + u, PY0 + 0.7, O_Z0 + v)) for u, v in arch]
b_prez.bm.faces.new(ra)
b_prez.bm.faces.new(list(reversed(rb)))
for i in range(len(ra)):
    j = (i + 1) % len(ra)
    b_prez.bm.faces.new((ra[i], rb[i], rb[j], ra[j]))
bx(b_prez, PX0 + 0.35, PY0 - 0.2, POD + 0.25, PX1 - 0.35, PY0 + 1.1, O_Z0 - 0.22, jit=False)   # nisa za drva
boolean(ob_pec, b_prez.finish())
apply_mods(ob_pec)
for f in ob_pec.data.polygons:               # unutrasnjost komore i nise je cadjava
    c = f.center
    if PX0 + 0.3 < c.x < PX1 - 0.3 and c.y > PY0 + 0.05 and c.z < 2.3:
        f.material_index = 1
# gvozdeni ram otvora, prag, rauchfang (dimna kapa) i cev do plafona
b_gv = Builder("Pec_gvozdje", M["gvozdje"], bevel=0.008, seg=1)
fr = [((O_W / 2 + 0.07) * math.cos(math.pi * i / 12), (O_H - O_W / 2) + (O_W / 2 + 0.07) * math.sin(math.pi * i / 12)) for i in range(13)]
for (u0, v0), (u1, v1) in zip(fr, fr[1:]):
    c = Vector((PCX + (u0 + u1) / 2, PY0 - 0.015, O_Z0 + (v0 + v1) / 2))
    ln = math.hypot(u1 - u0, v1 - v0) + 0.01
    box(b_gv, c, (ln, 0.04, 0.07), jit=False)
    b_gv.bm.verts.ensure_lookup_table()
    vv = b_gv.bm.verts[-8:]
    bmesh.ops.rotate(b_gv.bm, verts=vv, cent=c, matrix=Matrix.Rotation(-math.atan2(v1 - v0, u1 - u0), 3, "Y"))
for sg in (-1, 1):
    bx(b_gv, PCX + sg * (O_W / 2 + 0.035) - 0.035, PY0 - 0.035, O_Z0 - 0.04, PCX + sg * (O_W / 2 + 0.035) + 0.035,
       PY0 + 0.005, O_Z0 + O_H - O_W / 2, jit=False)
bx(b_gv, PCX - 0.62, PY0 - 0.2, O_Z0 - 0.07, PCX + 0.62, PY0 + 0.02, O_Z0 - 0.02, jit=False)   # prag (polica za lopatu)
bx(b_gv, PCX - 0.7, PY0 - 0.5, 2.5, PCX + 0.7, PY0 + 0.3, 2.56, jit=False)
b_kapa = Builder("Pec_kapa", M["plafon"], bevel=0.02, seg=1)
frust_lo = [(PCX - 0.7, PY0 - 0.5), (PCX + 0.7, PY0 - 0.5), (PCX + 0.7, PY0 + 0.3), (PCX - 0.7, PY0 + 0.3)]
frust_hi = [(PCX - 0.25, PY0 - 0.05), (PCX + 0.25, PY0 - 0.05), (PCX + 0.25, PY0 + 0.3), (PCX - 0.25, PY0 + 0.3)]
bmk = b_kapa.bm
lo = [bmk.verts.new((x, y, 2.56)) for x, y in frust_lo]
hi = [bmk.verts.new((x, y, 3.1)) for x, y in frust_hi]
bmk.faces.new(list(reversed(lo)))
bmk.faces.new(hi)
for i in range(4):
    j = (i + 1) % 4
    bmk.faces.new((lo[i], lo[j], hi[j], hi[i]))
bx(b_kapa, PCX - 0.25, PY0 - 0.05, 3.1, PCX + 0.25, PY0 + 0.3, PLAFON + 0.01)
# zar i ugljenisane cepanice u komori, drva u nisi
b_zar = Builder("Zar", M["zar"], bevel=0, smooth=True)
for i in range(90):                          # zar je odgurnut u dve gomile, levo i desno, sredina ostaje za hleb
    side = random.choice((-1, 1))
    gy = random.gauss(PY0 + 1.7 + side * 0.4, 0.5)
    ellipsoid(b_zar, (PCX + side * random.uniform(0.55, 1.1), min(PY1 - 0.45, max(PY0 + 0.9, gy)), O_Z0 + 0.03 + random.uniform(0, 0.06)),
              (random.uniform(0.07, 0.17),) * 2 + (random.uniform(0.05, 0.1),), rot=random.uniform(0, 3), seg=(8, 5), jit=15)
b_cep = Builder("Cepanice", M["drva"], bevel=0.006, seg=1)
RNG_CEP = random.Random(5)                   # svoj niz: globalni random (polozaji ostalog) ostaje isti


def cepanica(b, p0, p1, r, seg):
    """Valjak + atribut "drvo" po uglu lica (vidi mat_cepanica): presek ili kora, poluprecnik u A."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    u = d.orthogonal().normalized()
    w = d.cross(u)
    vs = cyl(b, p0, p1, r, seg)
    lay = b.bm.loops.layers.float_color.get("drvo") or b.bm.loops.layers.float_color.new("drvo")
    for f in {f for v in vs for f in v.link_faces}:
        cap = abs(f.normal.normalized().dot(d)) > 0.9
        ac = math.atan2((f.calc_center_median() - p0).dot(w), (f.calc_center_median() - p0).dot(u))
        for lp in f.loops:
            rel = lp.vert.co - p0
            x, y, a = rel.dot(u), rel.dot(w), rel.dot(d)
            if cap:
                lp[lay] = (x, y, 1.0, r)
            else:
                ang = math.atan2(y, x)
                ang = ac + (ang - ac + math.pi) % (2 * math.pi) - math.pi      # bez skoka na savu unutar lica
                lp[lay] = (ang * r, a, 0.0, r)


for i in range(3):
    y = PY0 + 2.0 + i * 0.35
    cepanica(b_cep, (PCX - 0.5, y, O_Z0 + 0.09), (PCX + 0.45, y + random.uniform(-0.3, 0.3), O_Z0 + 0.1), 0.06, 12)
for row in range(3):
    for i in range(6 - row):
        x0 = PX0 + 0.5 + i * 0.27 + row * 0.13
        cepanica(b_cep, (x0, PY0 - 0.12 - RNG_CEP.uniform(0, 0.05), POD + 0.32 + row * 0.15),
                 (x0 + random.uniform(-0.03, 0.03), PY0 + 0.9, POD + 0.32 + row * 0.15), RNG_CEP.uniform(0.058, 0.07), 14)
# zar: komadi uglja nisu glatka jaja, nego krti, nepravilni grumeni (sum pomera temena; bez globalnog random-a)
for v in b_zar.bm.verts:
    v.co += mnoise.noise_vector(v.co * 9.0) * 0.018
b_cep.bm.normal_update()
for ob_ in (b_gv, b_kapa, b_zar):
    ob_.finish()
b_cep.smooth, b_cep.seg = True, 2
ob_cep = b_cep.finish()
ob_cep.data.set_sharp_from_angle(angle=math.radians(40))    # glatka kora, ostro celo

# pod komore: samotne ploce sa cadji i pepelom (inace ravna cadjava povrsina), plus dve gomilice pepela uz zar
M["pepeo"] = mat_plaster("pepeo", "#5f5852", var=0.25, bump_s=0.8, rough=1.0)
b_spod = Builder("Pec_pod", M["samot"], bevel=0.004, seg=1)
bx(b_spod, PX0 + 0.46, PY0 + 0.01, O_Z0 - 0.01, PX1 - 0.41, PY1 - 0.36, O_Z0 + 0.012, jit=False)
b_spod.finish()
b_pep = Builder("Pec_pepeo", M["pepeo"], bevel=0, smooth=True)
for side in (-1, 1):
    for i in range(7):
        ellipsoid(b_pep, (PCX + side * random.uniform(0.3, 0.65), PY0 + random.uniform(0.9, 2.6), O_Z0 + 0.008),
                  (random.uniform(0.08, 0.22), random.uniform(0.1, 0.28), random.uniform(0.012, 0.03)), rot=random.uniform(0, 3),
                  seg=(10, 5), jit=0)
b_pep.finish()

# vrata peci: posebna, pivot na sarki (donja ivica, osa X). Otvaranje: rotation_euler.x od 0 do +85 stepeni.
# Livena ploca debela 6 cm sa uzdignutim okvirom i udubljenim poljem, unutra (ka vatri) cep koji ulazi u otvor,
# trakaste sarke sa nitnama, mesingani kontrolni otvor i drska sa drvenim rukohvatom na odstojnicima.
DOOR_W, DOOR_H, DOOR_T = O_W + 0.18, O_H + 0.12, 0.06
b_dv = Builder("PecVrata", [M["gvozdje"], M["mesing"], M["drvo_radnja"], M["gvozdje_cadj"]], bevel=0.006, seg=1)
bmv = b_dv.bm


def arch_prof(w, h, n=14, du=0.0):
    return [(-w / 2, du), (w / 2, du)] + [((w / 2) * math.cos(math.pi * i / n), du + (h - w / 2) + (w / 2) * math.sin(math.pi * i / n))
                                       for i in range(n + 1)]


def arch_slab(prof, y0, y1, mat=0):
    """Ploca u obliku luka izmedju y0 (pozadi, ka vatri) i y1 (napred, ka pekaru, y1 < y0)."""
    ra = [bmv.verts.new((u, y0, v)) for u, v in prof]
    rb = [bmv.verts.new((u, y1, v)) for u, v in prof]
    fs = [bmv.faces.new(list(reversed(ra))), bmv.faces.new(rb)]
    for i in range(len(ra)):
        j = (i + 1) % len(ra)
        fs.append(bmv.faces.new((ra[i], ra[j], rb[j], rb[i])))
    for f in fs:
        f.material_index = mat
    return fs


fs = arch_slab(arch_prof(DOOR_W, DOOR_H), DOOR_T / 2, -DOOR_T / 2)
front = fs[1]
ins = bmesh.ops.inset_region(bmv, faces=[front], thickness=0.075, depth=-0.014)     # udubljeno polje u okviru
# unutra (ka vatri): limeni stit na odstojanju, dva uspravna i jedno poprecno rebro, nitne po obodu stita
arch_slab(arch_prof(DOOR_W - 0.16, DOOR_H - 0.1, du=0.04), DOOR_T / 2 + 0.022, DOOR_T / 2 - 0.002, mat=3)
for xr in (-0.2, 0.2):
    box(b_dv, (xr, DOOR_T / 2 + 0.035, DOOR_H * 0.42), (0.03, 0.03, DOOR_H * 0.66), jit=False, mat=3)
box(b_dv, (0, DOOR_T / 2 + 0.035, DOOR_H * 0.3), (DOOR_W - 0.3, 0.03, 0.03), jit=False, mat=3)
for k in range(9):
    a_ = math.pi * k / 8
    rw, rh = (DOOR_W - 0.16) / 2 - 0.035, DOOR_H - 0.1 - (DOOR_W - 0.16) / 2
    ellipsoid(b_dv, (rw * math.cos(a_), DOOR_T / 2 + 0.024, 0.04 + rh + (rw) * math.sin(a_)), (0.022, 0.014, 0.022), seg=(8, 4), jit=0)
yf = -DOOR_T / 2
for sg in (-1, 1):                                                                       # trakaste sarke
    xs = sg * (DOOR_W / 2 - 0.17)
    box(b_dv, (xs, yf - 0.006, DOOR_H * 0.3), (0.055, 0.012, DOOR_H * 0.6), jit=False)
    for zz in (0.06, DOOR_H * 0.3, DOOR_H * 0.55):
        ellipsoid(b_dv, (xs, yf - 0.013, zz), (0.018, 0.012, 0.018), seg=(8, 4), jit=0)
    cyl(b_dv, (xs - 0.07, 0, 0), (xs + 0.07, 0, 0), 0.026, seg=10)                       # zglob sarke na osi
box(b_dv, (0, yf - 0.006, DOOR_H * 0.3), (DOOR_W - 0.2, 0.012, 0.05), jit=False)         # poprecno ojacanje
n0 = len(bmv.verts)
lathe(b_dv, (0, 0, 0), [(0.0, 0.0), (0.06, 0.0), (0.06, 0.015), (0.045, 0.022), (0.0, 0.024)], seg=18)   # kontrolni otvor
bmv.verts.ensure_lookup_table()
vs_ = bmv.verts[n0:]
bmesh.ops.transform(bmv, verts=vs_, matrix=Matrix.Translation((0, yf + 0.012, DOOR_H * 0.56)) @ Matrix.Rotation(math.pi / 2, 4, "X"))
for f in {f for v in vs_ for f in v.link_faces}:
    f.material_index = 1
HZ = DOOR_H * 0.78                                                                       # drska blizu slobodne ivice
for sg in (-1, 1):
    cyl(b_dv, (sg * 0.17, yf - 0.01, HZ), (sg * 0.17, yf - 0.085, HZ), 0.011, seg=8)
    vv = cyl(b_dv, (sg * 0.185, yf - 0.085, HZ), (sg * 0.215, yf - 0.085, HZ), 0.02, seg=10)
    for f in {f for v in vv for f in v.link_faces}:
        f.material_index = 1
cyl(b_dv, (-0.19, yf - 0.085, HZ), (0.19, yf - 0.085, HZ), 0.009, seg=8)
vv = cyl(b_dv, (-0.13, yf - 0.085, HZ), (0.13, yf - 0.085, HZ), 0.021, seg=12)                  # drveni rukohvat
for f in {f for v in vv for f in v.link_faces}:
    f.material_index = 2
for u in (-0.42, -0.21, 0.0, 0.21, 0.42):                                               # nitne po okviru dole
    ellipsoid(b_dv, (u * DOOR_W / 1.1, yf - 0.004, 0.035), (0.016, 0.012, 0.016), seg=(8, 4), jit=0)
HINGE = (PCX, PY0 - 0.075, O_Z0 - 0.04)
ob_vrata = b_dv.finish(origin=(0, 0, 0))
for f in ob_vrata.data.polygons:             # unutrasnja strana (ka vatri) je zagorela; vidi se kad su vrata otvorena
    if f.normal.y > 0.9 and f.material_index == 0:
        f.material_index = 3
ob_vrata.location = HINGE
ob_vrata.rotation_mode = "XYZ"
OPEN = math.radians(85)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
for fr_, ang in ((1, 0.0), (40, OPEN)):
    ob_vrata.rotation_euler = (ang, 0, 0)
    ob_vrata.keyframe_insert("rotation_euler", index=0, frame=fr_)
ob_vrata["otvoreno_rad"] = OPEN
# dva gvozdena nosaca sarke na pragu (fiksna, deo peci)
b_ns = Builder("Pec_sarke", M["gvozdje"], bevel=0.004, seg=1)
for sg in (-1, 1):
    xs = PCX + sg * (DOOR_W / 2 - 0.08)
    bx(b_ns, xs - 0.03, PY0 - 0.11, O_Z0 - 0.09, xs + 0.03, PY0 - 0.01, O_Z0 - 0.02, jit=False)
    cyl(b_ns, (xs - 0.025, HINGE[1], HINGE[2]), (xs + 0.025, HINGE[1], HINGE[2]), 0.026, seg=10)
b_ns.finish()

# lopata (Brotschieber) naslonjena na pec
b_lop = Builder("Lopata", M["drvo_radnja"], bevel=0.004, seg=1)
cyl(b_lop, (PX0 - 0.12, PY0 + 0.6, POD), (PX0 - 0.1, PY0 + 0.55, 2.3), 0.018, seg=8)
box(b_lop, (PX0 - 0.1, PY0 + 0.55, 2.55), (0.012, 0.32, 0.42), jit=False)
b_lop.finish()

# ---------------------------------------------------------------- radni sto, brasno, testo
TX0, TX1, TY0, TY1, TZ = 4.95, 7.3, 2.45, 3.55, 0.92
b_sto = Builder("Sto", M["drvo_radnja"], bevel=0.015, seg=1)
for x, y in ((TX0 + 0.1, TY0 + 0.1), (TX1 - 0.1, TY0 + 0.1), (TX0 + 0.1, TY1 - 0.1), (TX1 - 0.1, TY1 - 0.1)):
    bx(b_sto, x - 0.05, y - 0.05, POD, x + 0.05, y + 0.05, TZ - 0.09)
bx(b_sto, TX0 + 0.1, TY0 + 0.1, 0.3, TX1 - 0.1, TY1 - 0.1, 0.34)
bx(b_sto, TX0 + 0.08, TY0 + 0.08, TZ - 0.2, TX1 - 0.08, TY1 - 0.08, TZ - 0.09)
b_sto.finish()
b_pl = Builder("Sto_ploca", M["sto"], bevel=0.02, seg=2)
bx(b_pl, TX0, TY0, TZ - 0.09, TX1, TY1, TZ, jit=False)
b_pl.finish()
b_br = Builder("Brasno", M["brasno"], bevel=0, smooth=True)
lathe(b_br, (TX0 + 0.45, TY0 + 0.6, TZ), [(0.0, 0.0), (0.24, 0.0), (0.16, 0.025), (0.08, 0.06), (0.02, 0.08), (0.0, 0.082)], seg=20)
for i in range(30):
    # Posip oko gomilice je sada samo u boji ploce stola (mat_sto): kao geometrija je na sajtu izgledao kao beli
    # kamencici. Pozivi random-a ostaju (isti redosled), da se ne pomeri nista sto se gradi posle.
    a, r = random.uniform(0, 6.28), random.uniform(0.2, 0.55)
    random.uniform(0.04, 0.12), random.uniform(0.03, 0.08)
    jitter_q(0)
b_br.finish()
b_alat = Builder("Alat", [M["drvo_radnja"], M["metal"]], bevel=0.003, seg=1)
cyl(b_alat, (TX1 - 0.35, TY0 + 0.2, TZ + 0.035), (TX1 - 0.35, TY0 + 0.65, TZ + 0.035), 0.035, seg=14)   # oklagija
for sg in (-1, 1):
    cyl(b_alat, (TX1 - 0.35, TY0 + 0.425 + sg * 0.225, TZ + 0.035), (TX1 - 0.35, TY0 + 0.425 + sg * 0.33, TZ + 0.035), 0.014, seg=8)
box(b_alat, (TX0 + 1.05, TY0 + 0.25, TZ + 0.003), (0.12, 0.09, 0.006), rot=0.4, mat=1)                # strugalica
b_alat.finish()
# zdela sa vodom i kanta brasna ispod stola
b_zd = Builder("Zdela", M["emajl_unutra"], bevel=0, smooth=True)
lathe(b_zd, (TX1 - 0.55, TY1 - 0.3, TZ), [(0.0, 0.0), (0.07, 0.0), (0.13, 0.05), (0.15, 0.09), (0.14, 0.09), (0.12, 0.05), (0.0, 0.03)], seg=20)
b_zd.finish()
b_kanta = Builder("Kanta_brasna", M["juta"], bevel=0, smooth=True)
for i, x in enumerate((TX0 + 0.5, TX0 + 1.2)):
    lathe(b_kanta, (x, (TY0 + TY1) / 2, 0.34), [(0.0, 0.0), (0.25, 0.0), (0.27, 0.15), (0.26, 0.35), (0.2, 0.43), (0.08, 0.46), (0.06, 0.52), (0.0, 0.53)], seg=14, sx=1.0, sy=0.85)
b_kanta.finish()

# Testo: 2 shape key-a (mesenje, naraslo). Basis = grumen posle oblikovanja, pivot na dnu.
TESTO_P = Vector(((TX0 + TX1) / 2 + 0.25, (TY0 + TY1) / 2 + 0.02, TZ))
bmt = bmesh.new()
bmesh.ops.create_uvsphere(bmt, u_segments=40, v_segments=20, radius=1.0)
for v in bmt.verts:
    x, y, z = v.co
    z = max(z, -0.15) + 0.15
    n = 0.06 * math.sin(3.1 * x + 1.3 * y) * math.cos(2.3 * y - 0.7 * x)
    v.co = Vector((x * 0.2 * (1 + n), y * 0.165 * (1 + n), z * 0.095 / 1.15))
me_t = bpy.data.meshes.new("Testo")
bmt.to_mesh(me_t)
bmt.free()
for p_ in me_t.polygons:
    p_.use_smooth = True
ob_t = link(bpy.data.objects.new("Testo", me_t))
ob_t.location = TESTO_P
me_t.materials.append(M["testo"])
ob_t.shape_key_add(name="Basis")
sk_m = ob_t.shape_key_add(name="mesenje", from_mix=False)
sk_n = ob_t.shape_key_add(name="naraslo", from_mix=False)
for i, v in enumerate(me_t.vertices):
    x, y, z = v.co
    # mesenje: spljosteno, izduzeno pod dlanom, sa preklopom i dva otiska prstiju
    fold = 0.018 * math.exp(-((y - 0.02) / 0.03) ** 2) * (z / 0.09)
    dent = sum(0.022 * math.exp(-(((x - dx) / 0.04) ** 2 + ((y - dy) / 0.04) ** 2)) for dx, dy in ((-0.06, -0.03), (0.04, -0.05)))
    sk_m.data[i].co = Vector((x * 1.45, y * 1.12, max(0.0, z * 0.62 + fold - dent * (z / 0.09))))
    # naraslo: glatka, puna kupola, oko 1,6 puta zapremine
    sk_n.data[i].co = Vector((x * 1.12, y * 1.12, z * 1.45))
sk_m.value, sk_n.value = 0.0, 0.0

# ---------------------------------------------------------------- polica sa platnom i korpe za narastanje
SX0, SX1, SY0, SY1 = 1.6, 6.4, Y_ZAD - 0.56, Y_ZAD - 0.02
DASKE = (0.45, 1.1, 1.75, 2.4)
b_pol = Builder("Polica", M["drvo_radnja"], bevel=0.01, seg=1)
for x in (SX0, (SX0 + SX1) / 2, SX1):
    for y in (SY0 + 0.03, SY1 - 0.03):
        bx(b_pol, x - 0.03, y - 0.03, POD, x + 0.03, y + 0.03, 2.75)
for z in DASKE:
    bx(b_pol, SX0 - 0.03, SY0, z - 0.035, SX1 + 0.03, SY1, z)
b_pol.finish()

# platno (Bäckerleinen) na drugoj dasci: nabori izmedju vekni, prednji kraj visi preko ivice
b_plt = Builder("Platno", M["platno"], bevel=0, smooth=True)
PL_X0, PL_X1, z0 = 3.95, 6.3, DASKE[1]
NX, YS = 120, [SY1 - 0.02, SY1 - 0.15, SY1 - 0.3, SY1 - 0.42, SY0 + 0.02, SY0 - 0.01]
ZS = [0, 0, 0, 0, 0, -0.03]
loaf_xs = [PL_X0 + 0.16 + i * 0.3 for i in range(8)]
bmp = b_plt.bm
grid = []
for j, (y, dz) in enumerate(zip(YS, ZS)):
    row = []
    for i in range(NX + 1):
        x = PL_X0 + (PL_X1 - PL_X0) * i / NX
        ph = min(abs(x - (lx + 0.15)) for lx in loaf_xs[:-1])          # nabor je izmedju dve vekne
        pleat = 0.075 * math.exp(-(ph / 0.018) ** 2) * (1.0 if j < 5 else 0.3)
        row.append(bmp.verts.new((x, y, z0 + 0.003 + pleat + dz)))
    grid.append(row)
for drop in (0.06, 0.16, 0.24):                                       # visi preko prednje ivice
    row = []
    for i in range(NX + 1):
        x = PL_X0 + (PL_X1 - PL_X0) * i / NX
        row.append(bmp.verts.new((x, SY0 - 0.015 - 0.004 * math.sin(x * 9), z0 - 0.03 - drop)))
    grid.append(row)
for ra_, rb_ in zip(grid, grid[1:]):
    for i in range(NX):
        bmp.faces.new((ra_[i], ra_[i + 1], rb_[i + 1], rb_[i]))
bmesh.ops.solidify(bmp, geom=bmp.faces[:], thickness=0.004)
ob_plt = b_plt.finish()
ob_plt.data.set_sharp_from_angle(angle=math.radians(50))   # rub debljine 4 mm ne sme da kvari glatke normale lica
b_wk = Builder("Platno_vekne", M["testo_korpa"], bevel=0, smooth=True)
for lx in loaf_xs[:-1]:
    ellipsoid(b_wk, (lx, (SY0 + SY1) / 2, z0 + 0.05), (0.13, 0.42, 0.095), rot=random.uniform(-0.04, 0.04), seg=(14, 8), jit=2)
b_wk.finish()
# drugo platno, presavijeno, na trecoj dasci
b_plt2 = Builder("Platno_slozeno", M["platno"], bevel=0.008, seg=1)
for k in range(5):
    bx(b_plt2, 4.2 + k * 0.006, SY0 + 0.05, DASKE[2] + k * 0.012, 5.0 - k * 0.004, SY1 - 0.05, DASKE[2] + k * 0.012 + 0.011)
b_plt2.finish()


def korpa(name, pos, r_top=0.12, h=0.085, oval=1.0, dough=True):
    """Gaerkorb: zdela od trske i testo u njoj; oba sa pivotom na dnu (za skaliranje testa)."""
    b = Builder(name, M["pruce"], bevel=0, smooth=True)
    rb_ = r_top * 0.72
    lathe(b, (0, 0, 0), [(0.0, 0.0), (rb_, 0.0), (r_top * 0.93, h * 0.55), (r_top, h), (r_top - 0.012, h + 0.004),
                         (r_top - 0.016, h * 0.95), (rb_ - 0.012, 0.012), (0.0, 0.012)], seg=28, sy=oval)
    ob = b.finish(origin=pos, shift=False)
    if dough:
        d = Builder(name.replace("Korpa", "Korpa_testo"), M["testo_korpa"], bevel=0, smooth=True)
        lathe(d, (0, 0, 0), [(0.0, 0.0), (r_top - 0.02, 0.0), (r_top - 0.025, 0.03), (r_top * 0.7, 0.055), (r_top * 0.35, 0.068), (0.0, 0.07)],
              seg=28, sy=oval)
        od = d.finish(origin=Vector(pos) + Vector((0, 0, h * 0.45)), shift=False)
        od["skala_naraslo"] = 1.35
    return ob


k_pos = [(1.95, (SY0 + SY1) / 2, DASKE[1]), (2.45, (SY0 + SY1) / 2, DASKE[1]), (2.95, (SY0 + SY1) / 2, DASKE[1]),
         (3.45, (SY0 + SY1) / 2, DASKE[1]), (2.1, (SY0 + SY1) / 2, DASKE[0]), (2.65, (SY0 + SY1) / 2, DASKE[0])]
for i, p_ in enumerate(k_pos):
    korpa(f"Korpa_{i + 1}", p_, oval=1.0 if i % 2 == 0 else 1.6)
for i, x in enumerate((1.9, 2.4, 2.9, 3.4, 3.9)):          # prazne korpe naslagane na gornjoj dasci
    for k in range(2 if i % 2 == 0 else 1):
        korpa(f"Korpa_prazna_{i + 1}_{k}", (x, (SY0 + SY1) / 2, DASKE[3] + k * 0.05), dough=False)
# dve korpe na stolu, uz testo
korpa("Korpa_7", (TX0 + 1.15, TY1 - 0.32, TZ), oval=1.0)
korpa("Korpa_8", (TX0 + 1.5, TY1 - 0.28, TZ), oval=1.6)

# dzakovi brasna u uglu i na donjoj dasci
def dzak(b, x, y, z, s, rot=None, lezi=False):
    """Dzak od jute: kruska suzena ka vezanom vrhu; lezi=True je polegnut dzak (za slaganje na paletu)."""
    bmd = bmesh.new()
    bmesh.ops.create_uvsphere(bmd, u_segments=14, v_segments=9, radius=1.0)
    for v in bmd.verts:
        a, b_, c = v.co
        if lezi:
            v.co = Vector((a * 0.42 * s * (1 - 0.25 * abs(a) ** 4), b_ * 0.27 * s, (max(c, -0.75) + 0.75) * 0.1 * s))
            continue
        c = max(c, -0.7)
        top = 1.0 + 0.5 * max(0.0, c) ** 3
        w = 1.0 - 0.45 * max(0.0, c) ** 2
        v.co = Vector((a * 0.27 * s * w * (1 + 0.05 * math.sin(c * 7 + a)), b_ * 0.21 * s * w, (c + 0.7) * 0.36 * s * top))
    rq = Quaternion((0, 0, 1), random.uniform(-0.5, 0.5) if rot is None else rot)
    bmd.transform(Matrix.LocRotScale(Vector((x, y, z)), rq, Vector((1, 1, 1))))
    tmp = bpy.data.meshes.new("tmp")
    bmd.to_mesh(tmp)
    bmd.free()
    b.bm.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)


b_dz = Builder("Dzakovi", M["juta"], bevel=0, smooth=True)
for (x, y, s) in ((1.02, 7.75, 0.92), (1.33, 8.08, 0.8), (1.0, 7.15, 0.95)):
    dzak(b_dz, x, y, POD, s)
b_dz.finish()

# ---------------------------------------------------------------- pult i vitrina sa 4 hleba
VX0, VX1, VY0, VY1, VZ = 2.15, 4.55, 3.25, 3.95, 1.02
b_pu = Builder("Pult", M["drvo_radnja"], bevel=0.012, seg=1)
bx(b_pu, VX0, VY0 + 0.12, POD, VX1, VY1, VZ - 0.05)                    # telo pulta
bx(b_pu, VX0 - 0.03, VY0 - 0.02, POD, VX1 + 0.03, VY0 + 0.14, 0.28)   # sokla vitrine
bx(b_pu, VX0 - 0.03, VY0 - 0.02, 0.5, VX1 + 0.03, VY0 + 0.14, 0.53)   # polica u vitrini
for x in (VX0, (VX0 + VX1) / 2, VX1):
    bx(b_pu, x - 0.03, VY0 - 0.02, 0.28, x + 0.03, VY0 + 0.14, VZ - 0.05)
b_pu.finish()
b_pp = Builder("Pult_ploca", M["pult"], bevel=0.015, seg=2)
bx(b_pp, VX0 - 0.06, VY0 - 0.06, VZ - 0.05, VX1 + 0.06, VY1 + 0.02, VZ, jit=False)
b_pp.finish()
b_vs = Builder("Vitrina_staklo", M["staklo"], bevel=0)
bx(b_vs, VX0 + 0.03, VY0 - 0.015, 0.28, VX1 - 0.03, VY0 - 0.005, VZ - 0.05, jit=False)
b_vs.finish()
b_vh = Builder("Vitrina_hlebovi", M["hleb"], bevel=0, smooth=True)
for z in (0.3, 0.53):
    for i in range(7):
        ellipsoid(b_vh, (VX0 + 0.2 + i * 0.36, VY0 + 0.35, z + 0.05), (0.11, 0.11, 0.08) if i % 2 else (0.26, 0.12, 0.09),
                  rot=random.uniform(-0.3, 0.3), seg=(12, 7))
b_vh.finish()
# daska za izlaganje na pultu i kasa (stara, mesing)
b_dk = Builder("Pult_daska", M["pult_daska"], bevel=0.01, seg=2)
bx(b_dk, VX0 + 0.2, VY0 + 0.08, VZ, VX1 - 0.2, VY0 + 0.52, VZ + 0.025, jit=False)
b_dk.finish()
b_ks = Builder("Kasa", [M["mesing"], M["gvozdje"]], bevel=0.008, seg=1)
bx(b_ks, VX0 + 0.05, VY1 - 0.4, VZ, VX0 + 0.38, VY1 - 0.05, VZ + 0.16)
box(b_ks, (VX0 + 0.215, VY1 - 0.3, VZ + 0.21), (0.3, 0.12, 0.1), rot=0.0, mat=1)
b_ks.finish()


def bread_obj(name, bm, mats, pos, rot=0.0):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    for m_ in mats:
        me.materials.append(m_)
    ob.location = pos
    ob.rotation_euler = (0, 0, rot)
    return ob


def smooth01(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


BREAD_Z = VZ + 0.025
# Hleb_1 Kaisersemmel: 5 zakrivljenih latica (zvezda), svetle brazde, rumeni vrhovi
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=26, radius=1.0)
lay = bm.verts.layers.float_color.new("boja")
R1, H1 = 0.052, 0.046
for v in bm.verts:
    x, y, z = v.co
    r = math.hypot(x, y)
    ph = math.atan2(y, x)
    g = 0.0
    for k in range(5):
        a = ph - (2 * math.pi * k / 5 + 1.15 * r)
        a = (a + math.pi) % (2 * math.pi) - math.pi
        g = max(g, math.exp(-((r * a) / 0.085) ** 2))
    g *= smooth01(0.1, 0.32, r) * (1 - smooth01(0.8, 0.98, r)) * (z > 0)
    g = max(g, 0.7 * math.exp(-(r / 0.1) ** 2) * (z > 0))
    zz = z * H1 if z > 0 else z * 0.012
    puff = 1.0 + 0.04 * (1 - g) * (z > 0)
    s = (1 - 0.12 * g)
    v.co = Vector((x * R1 * s * puff, y * R1 * s * puff, max(-0.002, zz * (1 - 0.16 * g)) + 0.002))
    bake = (0.95 - 0.75 * g) * smooth01(-0.2, 0.55, z) + 0.1
    if 0.85 < r and -0.1 < z < 0.25:
        bake *= 0.5                                  # svetliji pojas na boku (Ausbund)
    v[lay] = (bake, 0.0, 0.0, 1.0)
for f in bm.faces:
    f.smooth = True
h1 = bread_obj("Hleb_1", bm, [M["k_semmel"]], (2.82, VY0 + 0.3, BREAD_Z), 0.3)

# Hleb_2 Mohnwecken: izduzena vekna, cetiri kosa reza, mak gusto po vrhu (Voronoi tacke u shaderu)
bm = bmesh.new()
bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=24, radius=1.0)
lay = bm.verts.layers.float_color.new("boja")
L2, W2, H2 = 0.15, 0.058, 0.075
for v in bm.verts:
    x, y, z = v.co
    xs = math.copysign(abs(x) ** 0.75, x)                      # punija, kockastija vekna
    X, Y = xs * L2, y * W2 * (1 - 0.15 * abs(x) ** 3)
    zz = z * H2 if z > 0 else z * 0.012
    g = 0.0
    for xc in (-0.075, -0.025, 0.025, 0.075):
        d = abs((X - xc) - 0.55 * Y) / math.sqrt(1 + 0.55 ** 2)
        g = max(g, math.exp(-(d / 0.007) ** 2))
    g *= smooth01(0.35, 0.7, z) * (1 - smooth01(0.035, 0.05, abs(Y)))
    zz -= 0.007 * g
    v.co = Vector((X, Y, max(-0.002, zz) + 0.002))
    top = smooth01(0.05, 0.35, z)
    v[lay] = ((0.9 - 0.6 * g) * smooth01(-0.3, 0.5, z) + 0.1, top * (1 - g), 0.0, 1.0)
for f in bm.faces:
    f.smooth = True
h2 = bread_obj("Hleb_2", bm, [M["k_mak"]], (3.05, VY0 + 0.3, BREAD_Z), -0.55)

# Hleb_3 Laugenbrezel: cev po krivoj sa debljinom po tacki, sjajna kora, svetao rascep na trbuhu, krupna so
cu = bpy.data.curves.new("brezel_kriva", "CURVE")
cu.dimensions = "3D"
cu.bevel_mode = "ROUND"
cu.bevel_depth = 1.0
cu.bevel_resolution = 5
cu.resolution_u = 8
cu.use_fill_caps = True
P = [(-0.046, -0.030, 0.034, 0.0085), (-0.026, -0.008, 0.030, 0.0095), (0.0, 0.016, 0.029, 0.0105),
     (0.026, 0.042, 0.017, 0.011), (0.054, 0.060, 0.0115, 0.0115), (0.082, 0.047, 0.0125, 0.0125),
     (0.093, 0.012, 0.014, 0.014), (0.080, -0.028, 0.016, 0.016), (0.047, -0.054, 0.019, 0.019),
     (0.0, -0.062, 0.020, 0.020), (-0.047, -0.054, 0.019, 0.019), (-0.080, -0.028, 0.016, 0.016),
     (-0.093, 0.012, 0.014, 0.014), (-0.082, 0.047, 0.0125, 0.0125), (-0.054, 0.060, 0.0115, 0.0115),
     (-0.026, 0.042, 0.011, 0.011), (0.0, 0.016, 0.0105, 0.0105), (0.026, -0.008, 0.024, 0.0095),
     (0.046, -0.030, 0.034, 0.0085)]
sp_ = cu.splines.new("BEZIER")
sp_.bezier_points.add(len(P) - 1)
for bp_, (x, y, z, r) in zip(sp_.bezier_points, P):
    bp_.co = (x, y, z)
    bp_.handle_left_type = bp_.handle_right_type = "AUTO"
    bp_.radius = r
tmp_ob = bpy.data.objects.new("brezel_tmp", cu)
C_POM.objects.link(tmp_ob)
dg = bpy.context.evaluated_depsgraph_get()
me_b = bpy.data.meshes.new_from_object(tmp_ob.evaluated_get(dg))
bpy.data.objects.remove(tmp_ob)
bpy.data.curves.remove(cu)
bm = bmesh.new()
bm.from_mesh(me_b)
bpy.data.meshes.remove(me_b)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
bm.normal_update()
lay = bm.verts.layers.float_color.new("boja")
for v in bm.verts:
    x, y, z = v.co
    belly = smooth01(-0.035, -0.05, y)
    rifs = belly * smooth01(0.6, 0.9, v.normal.z) * (0.6 + 0.4 * math.sin(x * 220) ** 2)
    v[lay] = (0.75 + 0.25 * smooth01(0.0, 0.8, v.normal.z), rifs, 0.0, 1.0)
for f in bm.faces:
    f.smooth = True
# krupna so: male nepravilne kocke na gornjoj strani (deo istog objekta, materijal 1)
rnd = random.Random(5)
faces = [f for f in bm.faces if f.normal.z > 0.55 and f.calc_center_median().z > 0.012]
salt = 0
for f in rnd.sample(faces, min(len(faces), 300)):
    if rnd.random() > 0.3:
        continue
    c = f.calc_center_median() + f.normal * 0.0008
    s = rnd.uniform(0.0022, 0.0042)
    r_ = bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.LocRotScale(
        c, Euler([rnd.uniform(0, 3.14) for _ in range(3)]).to_quaternion(), Vector((s, s * rnd.uniform(0.7, 1.1), s * 0.8))))
    for v in r_["verts"]:
        v[lay] = (0, 0, 0, 1)
        for ff in v.link_faces:
            ff.material_index = 1
            ff.smooth = False
    salt += 1
h3 = bread_obj("Hleb_3", bm, [M["k_lauge"], M["so"]], (3.32, VY0 + 0.31, BREAD_Z), 0.05)
h3["so_kristala"] = salt

# Hleb_4 Roggenlaib: okrugla rzena vekna, ispucala i posuta brasnom, zasecena (vidi se krume) + kriska
def rog_profile(n=18, R=0.118, H=0.098):
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        t = i / n * math.pi / 2
        pts.append((R * math.cos(t) ** 0.55 * (1 - 0.05 * (i == 0)), H * math.sin(t) ** 0.9 + 0.004))
    pts[1] = (R * 0.9, 0.0)
    pts[-1] = (0.0, H + 0.004)
    return pts


def roggen_bm():
    b = Builder("tmp", M["k_roggen"], bevel=0)
    lathe(b, (0, 0, 0), rog_profile(), seg=72)
    bm_ = b.bm
    bmesh.ops.remove_doubles(bm_, verts=bm_.verts, dist=1e-6)
    lay_ = bm_.verts.layers.float_color.new("boja")
    for v in bm_.verts:
        x, y, z = v.co
        wob = 0.004 * math.sin(math.atan2(y, x) * 5 + 1.0) * smooth01(0.02, 0.09, z)
        rr = math.hypot(x, y)
        if rr > 1e-6:
            v.co.x += x / rr * wob
            v.co.y += y / rr * wob
        v[lay_] = (0.5 + 0.5 * smooth01(0.0, 0.08, z), smooth01(0.05, 0.09, z), 0.0, 1.0)
    return bm_, lay_


def cut_fill(bm_, co, no, keep_outer_side):
    """Prerez ravnim nozem: ostavi jednu stranu, zatvori rupu licem krume (materijal 1, ostra ivica)."""
    geom = bm_.verts[:] + bm_.edges[:] + bm_.faces[:]
    bmesh.ops.bisect_plane(bm_, geom=geom, plane_co=co, plane_no=no, clear_outer=not keep_outer_side,
                           clear_inner=keep_outer_side, dist=1e-6)
    edges = [e for e in bm_.edges if len(e.link_faces) == 1]
    res = bmesh.ops.edgeloop_fill(bm_, edges=edges)
    for f in res["faces"]:
        f.material_index = 1
        f.smooth = False
    for e in edges:
        e.smooth = False
    return res["faces"]


bm, lay = roggen_bm()
for f in bm.faces:
    f.smooth = True
CUTX = 0.045
cut_fill(bm, (CUTX, 0, 0), (1, 0, 0), keep_outer_side=False)
bms, lay_s = roggen_bm()                                # kriska: deo vekne izmedju CUTX+0,004 i CUTX+0,02
for f in bms.faces:
    f.smooth = True
cut_fill(bms, (CUTX + 0.004, 0, 0), (1, 0, 0), keep_outer_side=True)
cut_fill(bms, (CUTX + 0.02, 0, 0), (1, 0, 0), keep_outer_side=False)
# kriska lezi na dasci ispred vekne, krume gore
bmesh.ops.transform(bms, verts=bms.verts, matrix=Matrix.Translation((0.175, -0.035, -(CUTX + 0.004))) @ Matrix.Rotation(-math.pi / 2, 4, "Y"))
tmp = bpy.data.meshes.new("tmp_k")
bms.to_mesh(tmp)
bms.free()
off = len(bm.verts)
bm.from_mesh(tmp)
bpy.data.meshes.remove(tmp)
h4 = bread_obj("Hleb_4", bm, [M["k_roggen"], M["krume_rog"]], (3.6, VY0 + 0.32, BREAD_Z), -1.0)
HLEBOVI = [h1, h2, h3, h4]
for i, h in enumerate(HLEBOVI):
    h["ime"] = ("Kaisersemmel", "Mohnwecken", "Laugenbrezel", "Roggenlaib")[i]

# ---------------------------------------------------------------- magacin na prvom spratu (iza prozora Kriske)
# Noc, ugaseno: palete sa dzakovima brasna, regal sa sanducima. Vidi se kroz prozore prvog sprata i u preseku.
b_pal = Builder("Magacin_palete", M["drvo_radnja"], bevel=0.006, seg=1)
b_mdz = Builder("Magacin_dzakovi", M["juta"], bevel=0, smooth=True)
for (px, py, slojeva) in ((2.2, 7.65, 3), (3.6, 7.65, 2), (8.9, 7.65, 3), (8.9, 6.55, 1)):
    for dy in (-0.32, 0.0, 0.32):
        bx(b_pal, px - 0.6, py + dy - 0.05, SPRAT, px + 0.6, py + dy + 0.05, SPRAT + 0.08)
    for k in range(5):
        x = px - 0.55 + k * 0.275
        bx(b_pal, x - 0.05, py - 0.4, SPRAT + 0.08, x + 0.05, py + 0.4, SPRAT + 0.105)
    for sl in range(slojeva):
        z = SPRAT + 0.105 + sl * 0.13
        if sl % 2 == 0:
            for dy in (-0.2, 0.2):
                dzak(b_mdz, px + random.uniform(-0.03, 0.03), py + dy, z, 1.25, rot=random.uniform(-0.06, 0.06), lezi=True)
        else:
            for dx in (-0.3, 0.3):
                dzak(b_mdz, px + dx, py + random.uniform(-0.03, 0.03), z, 0.95, rot=math.pi / 2 + random.uniform(-0.06, 0.06),
                     lezi=True)
for (x, y, s_) in ((5.2, 8.0, 1.0), (5.6, 7.95, 0.95), (1.2, 4.6, 0.9)):
    dzak(b_mdz, x, y, SPRAT, s_)
b_pal.finish()
b_mdz.finish()
b_rg = Builder("Magacin_regal", M["drvo_radnja"], bevel=0.008, seg=1)
RX0, RX1, RY0, RY1 = X_PREG - 0.5, X_PREG - 0.02, 2.4, 5.2
for y in (RY0, (RY0 + RY1) / 2, RY1):
    for x in (RX0 + 0.03, RX1 - 0.03):
        bx(b_rg, x - 0.025, y - 0.025, SPRAT, x + 0.025, y + 0.025, SPRAT + 2.2)
for z in (0.25, 0.95, 1.65):
    bx(b_rg, RX0, RY0 - 0.03, SPRAT + z - 0.03, RX1, RY1 + 0.03, SPRAT + z)
for i, (z, y, w, h) in enumerate(((0.25, 2.8, 0.5, 0.3), (0.25, 3.45, 0.55, 0.3), (0.95, 2.75, 0.45, 0.25),
                                  (0.95, 4.5, 0.6, 0.35), (1.65, 3.2, 0.5, 0.22), (0.25, 4.6, 0.5, 0.42))):
    bx(b_rg, RX0 + 0.04, y - w / 2, SPRAT + z, RX1 - 0.06, y + w / 2, SPRAT + z + h)
b_rg.finish()

# ---------------------------------------------------------------- lampa nad stolom (jedini topao izvor)
LX, LY = (TX0 + TX1) / 2, (TY0 + TY1) / 2
LZ = 2.3                                            # donja ivica sesira
b_lm = Builder("Lampa_sesir", [M["emajl"], M["emajl_unutra"]], bevel=0, smooth=True)
lathe(b_lm, (LX, LY, LZ), [(0.0, 0.3), (0.032, 0.3), (0.036, 0.25), (0.12, 0.18), (0.26, 0.05), (0.3, 0.0)], seg=40, caps=False)
nfo = len(b_lm.bm.faces)
lathe(b_lm, (LX, LY, LZ), [(0.297, -0.002), (0.255, 0.045), (0.115, 0.172), (0.03, 0.235), (0.0, 0.236)], seg=40, caps=False)
b_lm.bm.faces.ensure_lookup_table()
for f in b_lm.bm.faces[nfo:]:
    f.material_index = 1
ob_lm = b_lm.finish()
b_kab = Builder("Lampa_kabl", M["gvozdje"], bevel=0)
cyl(b_kab, (LX, LY, LZ + 0.3), (LX, LY, PLAFON), 0.006, seg=6)
lathe(b_kab, (LX, LY, PLAFON - 0.04), [(0.0, 0.0), (0.05, 0.0), (0.05, 0.04), (0.0, 0.04)], seg=12)
b_kab.finish()
b_sj = Builder("Lampa_sijalica", M["sijalica"], bevel=0, smooth=True)
ellipsoid(b_sj, (LX, LY, LZ + 0.1), (0.07, 0.07, 0.085), seg=(14, 9), jit=0)
ob_sj = b_sj.finish()
ob_sj.visible_shadow = False


def add_light(name, typ, loc, rot_dir=None, coll=C_ENT, **kw):
    ld = bpy.data.lights.new(name, typ)
    for k, v in kw.items():
        setattr(ld, k, v)
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    if rot_dir is not None:
        ob.rotation_euler = Vector(rot_dir).normalized().to_track_quat("-Z", "Y").to_euler()
    link(ob, coll)
    return ob


L_LAMPA = add_light("Svetlo_lampa", "POINT", (LX, LY, LZ + 0.08), energy=float(os.environ.get("KRUME_LAMPA", "260")),
                    color=(1.0, 0.66, 0.36), shadow_soft_size=0.05)
L_ZAR = add_light("Svetlo_zar", "POINT", (PCX, PY0 + 1.7, O_Z0 + 0.4), energy=80, color=(1.0, 0.3, 0.06),
                  shadow_soft_size=0.35)
# hladna noc sa ulice (kad je Kriska izvucena): hladan kontrast toploj lampi, na pultu i hlebovima spreda
L_ULICA = add_light("Svetlo_ulica", "AREA", (2.2, -2.2, 3.4), rot_dir=(0.35, 1, -0.45), shape="RECTANGLE",
                    size=5.0, size_y=3.0, energy=float(os.environ.get("KRUME_ULICA", "70")), color=(0.5, 0.64, 1.0))
# slab topao odsjaj lampe na polici sa korpama i platnom (inace su u mraku na zadnjem zidu)
L_POLICA = add_light("Svetlo_polica", "AREA", (3.9, 6.6, 3.3), rot_dir=(0, 0.7, -1), shape="RECTANGLE",
                     size=4.0, size_y=1.0, energy=float(os.environ.get("KRUME_POLICA", "110")), color=(1.0, 0.7, 0.45))
# magacin na spratu: samo hladan odsjaj ulice kroz prozore
L_SPRAT = add_light("Svetlo_magacin", "AREA", (5.6, 1.2, 7.4), rot_dir=(0, 1, -0.7), shape="RECTANGLE",
                    size=8.0, size_y=1.5, energy=25, color=(0.5, 0.62, 1.0))

# slaba topla "stona lampa" makete s juga (kao Lampa_stola u kitu): samo da presek kore cita boju
L_FILL = add_light("Pomocno_lampa_stola", "AREA", (5.9, -14.0, 7.0), rot_dir=(0, 1, -0.45), coll=C_POM,
                   shape="DISK", size=10.0, energy=float(os.environ.get("KRUME_FILL", "900")), color=(1.0, 0.8, 0.6))

# ---------------------------------------------------------------- pomocno: trotoar ispred preseka (samo za kadar)
b_tr = Builder("Pomocni_trotoar", M["trotoar"], bevel=0.02, coll=C_POM)
prism(b_tr, [(-3.0, -2.75), (X_OUT, -2.75), (X_OUT, Y_CUT), (CH_IN - Y_CUT, Y_CUT), (X_IN, CH_IN - X_IN), (X_IN, Y_OUT),
             (-3.0, Y_OUT)], -0.4, 0.0)
b_tr.finish()
b_iv = Builder("Pomocni_ivicnjak", M["ivicnjak"], bevel=0.04, coll=C_POM)
bx(b_iv, -3.0, -3.0, -0.4, X_OUT, -2.75, -0.02, jit=False)
b_iv.finish()

# ---------------------------------------------------------------- pomocno: izmaglica brasna i toplote (samo foto kadar)
# Volumen samo ispred peci (ne globalno, ni u komori: tamo bi zar izgubio kontrast). Krug 3: ne vise pramenovi
# dima, nego mirna izmaglica brasna i pepela koja lebdi u vazduhu: gusca pri dnu i uz lice peci, siroka preko
# celog lica, sa krupnim oblacima i sitnim zrnom. Svetlo je samo zraci iz vatre (L_ZRACI), pa se u izmaglici
# vide snopovi i tamne pruge senki cepanica (ostala svetla ne osvetljavaju volumen). Pali je samo kadar "ofen".
M_MAGLA = bpy.data.materials.new("izmaglica")
M_MAGLA.use_nodes = True
ntm = M_MAGLA.node_tree
ntm.nodes.remove(ntm.nodes["Principled BSDF"])
vol = ntm.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = hexc("#d9cbb6")
vol.inputs["Anisotropy"].default_value = 0.45            # svetlo se rasipa napred: zraci se vide ka kameri
co_m = ntm.nodes.new("ShaderNodeTexCoord").outputs["Object"]
mp_m = ntm.nodes.new("ShaderNodeMapping")                # oblaci malo razvuceni vodoravno (prasina se slegla)
mp_m.inputs["Scale"].default_value = (0.8, 1.0, 1.3)
ntm.links.new(co_m, mp_m.inputs["Vector"])


def _f(col):
    bw_ = ntm.nodes.new("ShaderNodeRGBToBW")
    ntm.links.new(col, bw_.inputs["Color"])
    return bw_.outputs["Val"]


oblak = _f(ramp(ntm, noise(ntm, mp_m.outputs["Vector"], 1.6, 4, 0.55).outputs["Fac"], (0.4, 0.4, 0.4, 1),
                (1, 1, 1, 1), 0.3, 0.72))
zrno_m = _f(ramp(ntm, noise(ntm, co_m, 16.0, 3, 0.6).outputs["Fac"], (0.65, 0.65, 0.65, 1), (1, 1, 1, 1), 0.35, 0.7))
sep_m = ntm.nodes.new("ShaderNodeSeparateXYZ")
ntm.links.new(co_m, sep_m.inputs["Vector"])


def _opseg(val, a, b, lo):
    """Linearno lo..1 izmedju a i b (metri; Color Ramp prima samo polozaje 0-1)."""
    mr = ntm.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = a, b
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = lo, 1.0
    ntm.links.new(val, mr.inputs["Value"])
    return mr.outputs["Result"]


uz_pec = _opseg(sep_m.outputs["Y"], PY0 - 1.7, PY0 - 0.1, 0.3)
visina = _opseg(sep_m.outputs["Z"], 2.45, O_Z0 - 0.2, 0.3)            # gusca nisko (brasno se slegne)
visina = math_n(ntm, "MULTIPLY", visina, _opseg(sep_m.outputs["Z"], POD, O_Z0 - 0.1, 0.4))   # ali ne veo preko drva
sredina = _f(ramp(ntm, math_n(ntm, "ABSOLUTE", math_n(ntm, "SUBTRACT", sep_m.outputs["X"], PCX)),
                  (1, 1, 1, 1), (0.35, 0.35, 0.35, 1), 0.45, 1.0))
gust = math_n(ntm, "MULTIPLY", math_n(ntm, "MULTIPLY", oblak, zrno_m), math_n(ntm, "MULTIPLY", visina, sredina))
gust = math_n(ntm, "MULTIPLY", gust, uz_pec)
ntm.links.new(math_n(ntm, "MULTIPLY", gust, float(os.environ.get("KRUME_MAGLA", "0.5"))), vol.inputs["Density"])
ntm.links.new(vol.outputs["Volume"], ntm.nodes["Material Output"].inputs["Volume"])
M_MAGLA.cycles.volume_step_rate = 2.0              # sitniji korak: ostrije ivice senki u snopu
b_mg = Builder("Pomocno_izmaglica", M_MAGLA, bevel=0, coll=C_POM)
bx(b_mg, PCX - 1.65, PY0 - 1.75, POD + 0.02, PCX + 1.65, PY0 - 0.02, 2.48, jit=False)
OB_MAGLA = b_mg.finish()
OB_MAGLA.hide_render = True
# svetlo koje izlazi kroz otvor (spot duboko u komori, okrenut ka pekari): otvor ga oblikuje u snop, pa se u
# izmaglici vide zraci, a vrata, prag i cepanice dobijaju topao odsjaj odozgo. Samo foto kadar.
ld_ot = bpy.data.lights.new("Pomocno_svetlo_otvor", "SPOT")
ld_ot.energy, ld_ot.color, ld_ot.shadow_soft_size = float(os.environ.get("KRUME_OTVOR", "150")), (1.0, 0.42, 0.12), 0.2
ld_ot.spot_size, ld_ot.spot_blend = math.radians(62), 0.35
L_OTVOR = bpy.data.objects.new("Pomocno_svetlo_otvor", ld_ot)
L_OTVOR.location = (PCX, PY0 + 0.35, O_Z0 + 0.5)
L_OTVOR.rotation_euler = (Vector((PCX - 0.15, PY0 - 3.0, 0.75)) - L_OTVOR.location).to_track_quat("-Z", "Y").to_euler()
C_POM.objects.link(L_OTVOR)
L_OTVOR.hide_render = True

# ---------------------------------------------------------------- foto sloj (krug 2): PBR teksture, zar, svetla, HDRI
# Sve ovo vazi samo za kadar "ofen" i dodaje se tek posle cuvanja enterijer.blend (bake za sajt vidi stare
# materijale, bez UV mape "foto_uv" i bez modifikatora na zaru).
# Zraci: malo tacka-svetlo duboko u komori, u visini cepanica koje gore; deluje samo na izmaglicu. Cepanice,
# gomile zara i ivice luka ga seku, pa iz otvora izlaze snopovi sa tamnim prugama izmedju (ne jednolik veo).
ld_zr = bpy.data.lights.new("Pomocno_svetlo_zraci", "POINT")
ld_zr.energy = float(os.environ.get("KRUME_ZRACI", "1400"))
ld_zr.color, ld_zr.shadow_soft_size = (1.0, 0.45, 0.13), 0.02
L_ZRACI = bpy.data.objects.new("Pomocno_svetlo_zraci", ld_zr)
L_ZRACI.location = (PCX + 0.05, PY0 + 3.15, O_Z0 + 0.14)
L_ZRACI.visible_diffuse = L_ZRACI.visible_glossy = False     # samo u izmaglici (zraci), povrsine osvetljava zar
C_POM.objects.link(L_ZRACI)
# odbijeno svetlo: zar osvetli pod, sto i zidove pekare, a oni vrate slab topao sjaj na lice peci, drva i pod.
# Velika meka povrsina iza kamere, da senke imaju detalj (na fotografiji nema potpuno crnog).
ld_ob = bpy.data.lights.new("Pomocno_svetlo_odbijeno", "AREA")
ld_ob.shape, ld_ob.size, ld_ob.size_y = "RECTANGLE", 3.2, 1.8
ld_ob.energy = float(os.environ.get("KRUME_ODBIJENO", "55"))
ld_ob.color = (1.0, 0.6, 0.36)
L_ODB = bpy.data.objects.new("Pomocno_svetlo_odbijeno", ld_ob)
L_ODB.location = (PCX + 0.9, 1.1, 2.4)          # malo desno: leva trecina ostaje mirnija
L_ODB.rotation_euler = (Vector((PCX + 0.3, PY0, 0.9)) - L_ODB.location).to_track_quat("-Z", "Y").to_euler()
C_POM.objects.link(L_ODB)
L_ODB.visible_camera = False
for l_ in (L_ZRACI, L_ODB):
    l_.hide_render = True

# ---- krug 3 (samo foto kadar, sve u Pomocno, sakriveno van "ofen"): drva u nisi, vatra u komori, prasina
NISA_X0, NISA_X1, NISA_Z0, NISA_Z1 = PX0 + 0.35, PX1 - 0.35, POD + 0.25, O_Z0 - 0.22     # vidi Rez_pec
FOTO_OBJ = []


def cepanica_foto(b, lay, lay2, c, d, L, R, vrsta, seme, rng):
    """Cepanica za foto kadar: oblica (vrsta 0), polovina (1) ili klin (2), c je teziste prednjeg cela, d osa
    (ka nazad), L duzina. Celo je blago koso i nije u ravni sa susedima, ivice preseka su neravne. Atributi
    "drvo" i "drvo_s" kao u mat_cepanica_foto. Vraca poluprecnik obuhvatnog kruga (za slaganje)."""
    bm = b.bm
    d = Vector(d).normalized()
    u = Vector((0, 0, 1)).cross(d).normalized()
    w = d.cross(u)
    if vrsta == 0:
        n = 16
        prof = [(R * (1 + rng.uniform(-0.05, 0.05)), 2 * math.pi * i / n, 0) for i in range(n)]
        prof = [(r_ * math.cos(a_), r_ * math.sin(a_), k_) for r_, a_, k_ in prof]
    else:
        ug = math.pi if vrsta == 1 else rng.uniform(1.1, 1.8)
        n = max(5, int(16 * ug / (2 * math.pi)) + 2)
        prof = [(R * (1 + rng.uniform(-0.05, 0.05)) * math.cos(ug * i / n), R * (1 + rng.uniform(-0.05, 0.05)) *
                 math.sin(ug * i / n), 0 if i < n else 1) for i in range(n + 1)]
        for t_ in (0.62, 0.3):                            # cepana strana od kraja luka ka srzi, neravna
            prof.append((t_ * R * math.cos(ug) + rng.uniform(-0.006, 0.006), t_ * R * math.sin(ug) +
                         rng.uniform(-0.006, 0.006), 1))
        prof.append((rng.uniform(-0.004, 0.004), rng.uniform(-0.004, 0.004), 1))
        for t_ in (0.3, 0.62):
            prof.append((t_ * R + rng.uniform(-0.006, 0.006), rng.uniform(-0.006, 0.006), 1))
    rot = rng.uniform(0, 2 * math.pi)
    prof = [(x * math.cos(rot) - y * math.sin(rot), x * math.sin(rot) + y * math.cos(rot), k_) for x, y, k_ in prof]
    cx, cy = sum(q[0] for q in prof) / len(prof), sum(q[1] for q in prof) / len(prof)
    rb = max(math.hypot(x - cx, y - cy) for x, y, _ in prof)
    tf, tb = (rng.uniform(-0.09, 0.09), rng.uniform(-0.09, 0.09)), (rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06))
    F, Bk = [], []
    for x, y, _ in prof:
        q = Vector(c) + (x - cx) * u + (y - cy) * w
        F.append(bm.verts.new(q + d * (tf[0] * (x - cx) + tf[1] * (y - cy))))
        Bk.append(bm.verts.new(q + d * (L + tb[0] * (x - cx) + tb[1] * (y - cy))))
    fs = [(bm.faces.new(F), 2), (bm.faces.new(list(reversed(Bk))), 2)]
    k = len(prof)
    for i in range(k):
        j = (i + 1) % k
        fs.append((bm.faces.new((F[i], Bk[i], Bk[j], F[j])), prof[i][2]))
    for f, vr in fs:
        if vr == 0:                                       # kora: luk oko srzi bez skoka na savu
            ce = f.calc_center_median() - Vector(c)
            ac = math.atan2(ce.dot(w) + cy, ce.dot(u) + cx)
        for lp in f.loops:
            rel = lp.vert.co - Vector(c)
            x, y, a = rel.dot(u) + cx, rel.dot(w) + cy, rel.dot(d)
            if vr == 2:
                lp[lay] = (x, y, 1.0, R)
            elif vr == 0:
                ang = math.atan2(y, x)
                ang = ac + (ang - ac + math.pi) % (2 * math.pi) - math.pi
                lp[lay] = (ang * R, a, 0.0, R)
            else:
                lp[lay] = (math.hypot(x, y), a, 0.5, R)
            lp[lay2] = (seme, 0.0, 0.0, 1.0)
    return rb


if FOTO:
    # drva u nisi: slozena gomila oblica, polovina i klinova razlicitih precnika (najnize mesto prvo, kao kad se
    # slaze rukom); cela vire razlicito (0-13 cm ispred lica), svako malo koso
    rng_d = random.Random(31)
    b_df = Builder("Pomocno_drva_foto", M_FOTO["drva_nisa"], bevel=0.003, seg=1, smooth=True, coll=C_POM)
    lay_d = b_df.bm.loops.layers.float_color.new("drvo")
    lay_s = b_df.bm.loops.layers.float_color.new("drvo_s")
    slozeno, GOM_X1 = [], NISA_X0 + 1.75
    for i in range(70):
        vrsta = rng_d.choice((0, 0, 1, 2, 2, 2))
        R = rng_d.uniform(0.04, 0.075) if vrsta == 0 else rng_d.uniform(0.07, 0.115)
        rb_ = R * (1.0 if vrsta == 0 else 0.62 if vrsta == 1 else 0.7)
        naj = None
        for _ in range(40):
            x = rng_d.uniform(NISA_X0 + rb_ + 0.01, GOM_X1)
            z = NISA_Z0 + rb_
            for xj, zj, rj in slozeno:
                dx = abs(x - xj)
                if dx < rb_ + rj:
                    z = max(z, zj + math.sqrt((rb_ + rj) ** 2 - dx ** 2) * 0.96)
            vrh = NISA_Z1 - 0.012 - max(0.0, x - (GOM_X1 - 0.45)) * 0.55       # desni kraj gomile se spusta
            if z + rb_ <= vrh and (naj is None or z < naj[1]):
                naj = (x, z)
        if naj is None:
            continue
        x, z = naj
        rb2 = cepanica_foto(b_df, lay_d, lay_s, (x, PY0 + rng_d.uniform(-0.13, 0.0), z),
                            (rng_d.uniform(-0.03, 0.03), 1, rng_d.uniform(-0.02, 0.02)), rng_d.uniform(0.55, 0.95), R,
                            vrsta, rng_d.uniform(0, 100), rng_d)
        slozeno.append((x, z, min(rb2, rb_ * 1.1)))
    # desno u nisi: dve cepanice bacene ukoso dublje unutra i komadi kore na podu
    for x, yaw in ((NISA_X1 - 0.75, 0.5), (NISA_X1 - 0.4, -0.3)):
        R = rng_d.uniform(0.07, 0.1)
        cepanica_foto(b_df, lay_d, lay_s, (x, PY0 + 0.35, NISA_Z0 + R * 0.55), (math.sin(yaw), math.cos(yaw), 0), 0.5,
                      R, 2, rng_d.uniform(0, 100), rng_d)
    for i in range(14):
        cepanica_foto(b_df, lay_d, lay_s, (rng_d.uniform(GOM_X1 - 0.2, NISA_X1 - 0.1), PY0 + rng_d.uniform(-0.05, 0.9),
                                           NISA_Z0 + 0.004), (rng_d.uniform(-1, 1), rng_d.uniform(-1, 1), 0.0),
                      rng_d.uniform(0.03, 0.09), rng_d.uniform(0.015, 0.03), 1, rng_d.uniform(0, 100), rng_d)
    ob_df = b_df.finish()
    ob_df.data.set_sharp_from_angle(angle=math.radians(40))
    FOTO_OBJ.append(ob_df)
    # vatra u komori: sator od cepanica oko gomilice zara (pocetak lozenja); svetlo zraka je u njemu, pa cepanice
    # seku snopove koji izlaze kroz otvor (tamne pruge u izmaglici)
    VC = Vector((PCX + 0.04, PY0 + 2.1, O_Z0 + 0.012))     # iza svetla zara (L_ZAR), da ga ne zaseni
    b_vt = Builder("Pomocno_vatra_foto", potamni(M["drva"], "drva_vatra_foto", 0.4, em=0.7), bevel=0.004, seg=1,
                   smooth=True, coll=C_POM)
    for i in range(11):
        a_ = 2 * math.pi * i / 11 + rng_d.uniform(-0.12, 0.12) + 0.3
        p0 = VC + Vector((0.26 * math.cos(a_), 0.24 * math.sin(a_), 0.03))
        top = VC + Vector((rng_d.uniform(-0.03, 0.03), rng_d.uniform(-0.03, 0.03), 0.4))
        cepanica(b_vt, p0, p0 + (top - p0) * 1.12, rng_d.uniform(0.032, 0.05), 10)
    ob_vt = b_vt.finish()
    ob_vt.data.set_sharp_from_angle(angle=math.radians(40))
    b_vz = Builder("Pomocno_vatra_zar", M_FOTO["zar_pec"], bevel=0, smooth=True, coll=C_POM)
    for i in range(9):
        ellipsoid(b_vz, VC + Vector((rng_d.uniform(-0.12, 0.12), rng_d.uniform(-0.12, 0.12), 0.02)),
                  (rng_d.uniform(0.05, 0.1),) * 2 + (rng_d.uniform(0.03, 0.06),), rot=rng_d.uniform(0, 3), seg=(8, 5), jit=0)
    FOTO_OBJ += [ob_vt, b_vz.finish()]
    L_ZRACI.location = VC + Vector((0, 0.02, 0.15))
    # prasina: sitne pahulje brasna i pepela u vazduhu; osvetljava ih samo svetlo zraka (light linking), pa
    # zasvetle samo u snopu, kao na fotografiji
    M_PRAH = mat_simple("prasina_foto", "#e6dccd", rough=1.0)
    b_pr = Builder("Pomocno_prasina_foto", M_PRAH, bevel=0, smooth=True, coll=C_POM)
    for i in range(500):
        q = Vector((PCX + rng_d.gauss(0, 0.55), PY0 - 0.06 - abs(rng_d.gauss(0, 0.55)), O_Z0 + 0.3 + rng_d.gauss(0, 0.32)))
        if q.y < PY0 - 1.6 or q.z < POD + 0.1:
            continue
        bmesh.ops.create_icosphere(b_pr.bm, subdivisions=1, radius=rng_d.uniform(0.0005, 0.0014),
                                   matrix=Matrix.Translation(q))
    FOTO_OBJ.append(b_pr.finish())
    C_ZRACI = bpy.data.collections.new("Pomocno_zraci_primaju")
    for ob_ in (FOTO_OBJ[-1], OB_MAGLA):
        C_ZRACI.objects.link(ob_)
    L_ZRACI.light_linking.receiver_collection = C_ZRACI
    L_ZRACI.visible_diffuse = True
    # odbijeno svetlo u nisi: slab topao odsjaj sa poda pekare, da se vidi dubina nise desno od drva
    ld_ns = bpy.data.lights.new("Pomocno_svetlo_nisa", "AREA")
    ld_ns.shape, ld_ns.size, ld_ns.size_y = "RECTANGLE", 1.3, 0.2
    ld_ns.energy, ld_ns.color = float(os.environ.get("KRUME_NISA", "2.5")), (1.0, 0.58, 0.32)
    L_NISA = bpy.data.objects.new("Pomocno_svetlo_nisa", ld_ns)
    L_NISA.location = (NISA_X1 - 0.65, PY0 + 0.25, NISA_Z1 - 0.03)
    L_NISA.rotation_euler = Vector((0, 0.8, -1)).to_track_quat("-Z", "Y").to_euler()
    C_POM.objects.link(L_NISA)
    L_NISA.visible_camera = False
    FOTO_OBJ.append(L_NISA)
    for ob_ in FOTO_OBJ:
        ob_.hide_render = True
SWAP, FOTO_STANJE = [], {"uv": False}
VRATA_FOTO = {"gvozdje": "vrata", "gvozdje_cadj": "vrata_unutra"}     # vrata imaju svoje gvozdje (cadj po z vrata)
if FOTO:
    for ob in C_ENT.objects:
        if ob.type == "MESH":
            for i, mt in enumerate(ob.data.materials):
                kljuc = VRATA_FOTO.get(mt.name, mt.name) if mt and ob.name == "PecVrata" else mt and mt.name
                if kljuc in M_FOTO:
                    SWAP.append((ob, i, mt, M_FOTO[kljuc]))


def foto_uv(ob):
    """UV "foto_uv" u metrima: svako lice se projektuje po glavnoj osi svoje normale (kocka, lokalne koordinate),
    v je uvek uspravno (z) na zidovima, pa redovi cigli i vlakna drveta stoje vodoravno."""
    me = ob.data
    if FOTO_UV in me.uv_layers:
        return
    uvl = me.uv_layers.new(name=FOTO_UV)
    for poly in me.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda k: abs(n[k]))
        for li in poly.loop_indices:
            c = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (c.y, c.z) if ax == 0 else (c.x, c.z) if ax == 1 else (c.x, c.y)


def foto_sloj(on):
    """Ukljuci ili iskljuci foto sloj: materijali sa teksturama, grumeni zara, svetla zraka i odbijeno, HDRI."""
    if not FOTO:
        return
    if on and not FOTO_STANJE["uv"]:
        for ob in {s_[0] for s_ in SWAP}:
            foto_uv(ob)
        ob_zar = bpy.data.objects["Zar"]
        sd = ob_zar.modifiers.new("Foto_grumeni_sub", "SUBSURF")
        sd.levels, sd.render_levels = 0, 2
        tx_ = bpy.data.textures.new("zar_grumeni", "VORONOI")
        tx_.noise_scale = 0.035
        ds = ob_zar.modifiers.new("Foto_grumeni", "DISPLACE")
        ds.texture, ds.texture_coords, ds.strength, ds.mid_level = tx_, "GLOBAL", 0.03, 0.6
        # krug 3: cepanice u nisi zamenjuje Pomocno_drva_foto (Mask zadrzava samo cepanice u komori)
        ob_c = bpy.data.objects["Cepanice"]
        vg = ob_c.vertex_groups.new(name="foto_komora")
        vg.add([v.index for v in ob_c.data.vertices if v.co.z > O_Z0 - 0.1], 1.0, "REPLACE")
        mk = ob_c.modifiers.new("Foto_bez_nise", "MASK")
        mk.vertex_group = "foto_komora"
        ob_c.modifiers.move(len(ob_c.modifiers) - 1, 0)
        FOTO_STANJE["uv"] = True
    for ob, i, web, fm in SWAP:
        ob.data.materials[i] = fm if on else web
    for ob_ in (bpy.data.objects["Zar"], bpy.data.objects["Cepanice"]):
        for md in ob_.modifiers:
            if md.name.startswith("Foto_"):
                md.show_render = on
    L_ZRACI.hide_render = L_ODB.hide_render = not on
    for ob_ in FOTO_OBJ:
        ob_.hide_render = not on
    # volumen osvetljavaju samo zraci (pruge); ostala svetla bi u izmaglici dala jednolik veo
    for l_ in (L_OTVOR, L_ZAR, L_ODB, L_LAMPA, L_ULICA, L_POLICA) + tuple(o for o in FOTO_OBJ if o.type == "LIGHT"):
        l_.visible_volume_scatter = not on
    HDRI_ON.outputs[0].default_value = 1.0 if on else 0.0

# ---------------------------------------------------------------- svet, kamere, render
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wn = world.node_tree
for nd in list(wn.nodes):
    if nd.type != "OUTPUT_WORLD":
        wn.nodes.remove(nd)
bg = wn.nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = hexc(NOC)
bg.inputs["Strength"].default_value = float(os.environ.get("KRUME_AMB", "0.25"))
w_out = [nd for nd in wn.nodes if nd.type == "OUTPUT_WORLD"][0]
HDRI_ON = wn.nodes.new("ShaderNodeValue")
HDRI_ON.outputs[0].default_value = 0.0
if FOTO:
    # HDRI (nocna ulica) samo u odsjajima (Is Glossy Ray) i veoma slabo: metal, staklo i glazura dobijaju nesto
    # da odraze, a osvetljenje scene ostaje zar. Van foto kadra je HDRI_ON = 0, pa je svet isti kao pre.
    env = wn.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(TEKS, "hdri", "cobblestone_street_night_2k.hdr"), check_existing=True)
    bg_h = wn.nodes.new("ShaderNodeBackground")
    bg_h.inputs["Strength"].default_value = float(os.environ.get("KRUME_HDRI", "0.12"))
    wn.links.new(env.outputs["Color"], bg_h.inputs["Color"])
    lp = wn.nodes.new("ShaderNodeLightPath")
    fac = math_n(wn, "MULTIPLY", lp.outputs["Is Glossy Ray"], HDRI_ON.outputs[0])
    mxs = wn.nodes.new("ShaderNodeMixShader")
    wn.links.new(fac, mxs.inputs["Fac"])
    wn.links.new(bg.outputs["Background"], mxs.inputs[1])
    wn.links.new(bg_h.outputs["Background"], mxs.inputs[2])
    wn.links.new(mxs.outputs["Shader"], w_out.inputs["Surface"])
else:
    wn.links.new(bg.outputs["Background"], w_out.inputs["Surface"])


def add_cam(name, loc, target, lens, fstop=None, focus=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_start = 0.02
    cd.clip_end = 200
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    C_POM.objects.link(ob)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    return ob


cam_presek = add_cam("Kadar_presek", (5.8, -14.6, 3.6), (5.8, 4.5, 3.75), 36)
BRT = Vector((3.26, VY0 + 0.3, BREAD_Z + 0.03))
cam_vitrina = add_cam("Kadar_vitrina", BRT + Vector((0.02, -0.98, 0.5)), BRT, 35, fstop=2.0)
cam_pec = add_cam("Kadar_pec", (PCX - 0.95, PY0 - 1.75, 1.58), (PCX + 0.1, PY0 + 1.2, 1.02), 30)
# foto kadar Ofen: stanica Ofen iz kamera.json (glTF -> Blender: x, -z, y), umeren DOF, fokus na otvoru peci
OFEN_P, OFEN_C = Vector((9.27, 1.4, 1.62)), Vector((9.02, 4.4, 1.3))
cam_ofen = add_cam("Kadar_ofen", OFEN_P, OFEN_C, 32, fstop=2.8,
                   focus=(Vector((PCX, PY0 - 0.1, O_Z0 + 0.15)) - OFEN_P).length)

# Stanice kamere za poglavlja 4 i 5: prazni objekti (polozaj kamere), custom property "cilj" (tacka pogleda,
# Blender x/y/z u metrima) i "lens" (mm, senzor 36 mm po duzoj strani). Kamera ulazi spolja, kroz otvor posle
# spustene Kriske (unutrasnje lice fasade A je na y = 0,7). Programer A ih cita za kamera.json.
C_ST = bpy.data.collections.new("Stanice")
scene.collection.children.link(C_ST)


def stanica(name, loc, cilj, lens, opis):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = "ARROWS"
    ob.location = loc
    ob.rotation_euler = (Vector(cilj) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    ob["cilj"] = list(cilj)
    ob["lens"] = lens
    ob["opis"] = opis
    C_ST.objects.link(ob)
    cd = bpy.data.cameras.new(name + "_kam")                 # kamera za probni kadar, ne izvozi se
    cd.lens, cd.clip_start, cd.clip_end = lens, 0.02, 200
    cam = bpy.data.objects.new(name + "_kam", cd)
    cam.location, cam.rotation_euler = ob.location, ob.rotation_euler
    C_POM.objects.link(cam)
    return ob, cam


ST4, cam_st4 = stanica("Stanica_4", (5.75, 0.55, 1.95), (6.25, 3.05, 1.0), 30,
                       "pogl. 4: radni sto, testo (mesenje/naraslo) i dve korpe na stolu, lampa iznad")
ST5, cam_st5 = stanica("Stanica_5", (3.15, 1.55, 1.55), (3.22, 3.6, 1.12), 32,
                       "pogl. 5: cetiri hleba na pultu spreda, iza njih polica sa korpama i platnom")

scene.render.engine = "CYCLES"
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.resolution_percentage = int(os.environ.get("KRUME_RES", "100"))
cy = scene.cycles
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for dv in prefs.devices:
        dv.use = dv.type == "METAL"           # samo GPU: CPU uz GPU na M1 usporava (sporiji uzima deo slike)
    cy.device = "GPU"
    print("UREDJAJI", [(dv.name, dv.use) for dv in prefs.devices])
except Exception as e:
    print("GPU nije dostupan, CPU:", e)
cy.samples = int(os.environ.get("KRUME_SAMPLES", "256"))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.02
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 8
cy.transmission_bounces = 6
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.sample_clamp_indirect = 6.0
# foto podesavanja (vaze i za ostale kadrove): fiksan seed, OIDN sa albedo i normal prolazom, mekse odsjaje,
# volumen sa korakom i najvise jednim odbijanjem, persistent data (isti BVH za vise kadrova)
cy.seed, cy.use_animated_seed = 7, False
cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
cy.denoising_prefilter = "ACCURATE"
cy.blur_glossy = 1.0
cy.volume_bounces = 1
cy.volume_step_rate = 3.0
cy.volume_biased = True
scene.render.use_motion_blur = False
scene.render.use_persistent_data = True
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
scene.frame_start, scene.frame_end = 1, 40


def tris(ob, dg):
    me = ob.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    ob.evaluated_get(dg).to_mesh_clear()
    return n


dg = bpy.context.evaluated_depsgraph_get()
cnt = {o.name: tris(o, dg) for o in C_ENT.objects if o.type == "MESH"}
print("TRIS hlebovi", {h.name: cnt[h.name] for h in HLEBOVI})
print("TRIS enterijer ukupno", sum(cnt.values()), "objekata", len(cnt))
print("TRIS top", sorted(cnt.items(), key=lambda kv: -kv[1])[:12])
print("OBJEKTI", sorted(o.name for o in C_ENT.objects))

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "enterijer.blend"))
blend1 = os.path.join(HERE, "enterijer.blend1")
if os.path.exists(blend1):
    os.remove(blend1)

def sjaj(on, blago=False):
    """Bloom iz kompozitora (samo kadar peci): zar i sijalica dobijaju oreol, kao bloom na sajtu.
    blago=True (foto kadar): samo najsvetlije tacke i slabije, kao rasipanje u objektivu."""
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
        gl.inputs["Threshold"].default_value = 1.2 if blago else 0.7
        gl.inputs["Strength"].default_value = 0.25 if blago else 0.9
        gl.inputs["Size"].default_value = 0.6
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        scene.compositing_node_group = ng
    except Exception as e:
        print("Sjaj (glare) nije uspeo:", e)


if "norender" not in ARGS:
    # (kadar, kamera, frejm vrata, mesenje, naraslo, ekspozicija, zar)
    shots = [("presek", cam_presek, 10, 0.4, 0.0, 0.6, 220),
             ("vitrina", cam_vitrina, 1, 0.0, 0.0, 0.9, 80),
             ("pec", cam_pec, 40, 0.0, 0.0, 0.0, 130)]
    # probni kadrovi sa stanica (samo na zahtev: -- st4 st5), u bake/
    shots += [("st4", cam_st4, 1, 0.0, 0.0, 0.6, 80), ("st5", cam_st5, 1, 0.0, 0.0, 0.6, 80)]
    # foto proba (samo na zahtev: -- ofen): Cycles kadar za sekvencu na skrol, u proba-foto/
    shots += [("ofen", cam_ofen, 40, 0.0, 1.0, float(os.environ.get("KRUME_OFEN_EV", "0.3")),
               float(os.environ.get("KRUME_OFEN_ZAR", "110")))]
    STAT = {}

    def _stat(st, *a):
        """Poslednji red statistike rendera sa "Peak" (memorija), za izvestaj."""
        if "Mem" in str(st) or "Peak" in str(st):
            STAT["s"] = str(st).strip()

    bpy.app.handlers.render_stats.append(_stat)
    ZAR_EM = M["zar"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    zar_em0 = ZAR_EM.default_value
    for tag, cam, frame, km, kn, ex, ez in shots:
        if (ARGS and tag not in ARGS) or (not ARGS and tag in ("st4", "st5", "ofen")):
            continue
        foto = tag == "ofen"
        scene.frame_set(frame)
        sk_m.value, sk_n.value = km, kn
        L_ZAR.data.energy = ez
        scene.view_settings.exposure = float(os.environ.get("KRUME_EXPOSURE", ex))
        scene.camera = cam
        sjaj(tag in ("pec", "ofen"), blago=foto)
        OB_MAGLA.hide_render = not foto or os.environ.get("KRUME_MAGLA") == "0"
        L_OTVOR.hide_render = not foto
        L_FILL.hide_render = foto                   # stona lampa makete ne postoji u "fotografiji"
        ZAR_EM.default_value = float(os.environ.get("KRUME_OFEN_EM", "3.0")) if foto else zar_em0
        # u fotografiji je zar glavno svetlo: ulica i nebo samo kao slab hladan odsjaj, da zid ima pad svetla
        bg.inputs["Strength"].default_value = 0.06 if foto else float(os.environ.get("KRUME_AMB", "0.25"))
        L_ULICA.data.energy = (0.35 if foto else 1.0) * float(os.environ.get("KRUME_ULICA", "70"))
        L_LAMPA.data.energy = (0.12 if foto else 1.0) * float(os.environ.get("KRUME_LAMPA", "260"))
        # krug 2: polica sa svetlim zidom gore levo (tu je naslov "Ofen.") samo kao slab trag, leva trecina mirna
        L_POLICA.data.energy = (float(os.environ.get("KRUME_OFEN_POLICA", "0.08")) if foto else 1.0) * \
            float(os.environ.get("KRUME_POLICA", "110"))
        foto_sloj(foto)
        if foto and FOTO:
            M_FOTO["zar_pec"].node_tree.nodes["jacina"].outputs[0].default_value = \
                float(os.environ.get("KRUME_OFEN_EM", "3.0"))
        cy.samples = int(os.environ.get("KRUME_SAMPLES", "192" if foto else "256"))
        cy.sample_clamp_indirect = 10.0 if foto else 6.0
        cy.max_bounces = 6 if foto else 8
        if foto and os.environ.get("KRUME_BORDER"):          # isecak za proveru detalja: "x0,x1,y0,y1" (0-1)
            b_ = [float(v) for v in os.environ["KRUME_BORDER"].split(",")]
            scene.render.use_border = scene.render.use_crop_to_border = True
            r_ = scene.render
            r_.border_min_x, r_.border_max_x, r_.border_min_y, r_.border_max_y = b_
        if foto:
            os.makedirs(os.path.join(HERE, "proba-foto"), exist_ok=True)
            scene.render.filepath = os.path.join(HERE, "proba-foto", os.environ.get("KRUME_OFEN_IME", "4-ofen-wide.png"))
        else:
            scene.render.filepath = os.path.join(HERE, "bake" if tag.startswith("st") else "", f"enterijer-{tag}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"RENDER {os.path.basename(scene.render.filepath)}: {time.time() - t:.1f} s | {STAT.get('s', '')}")
