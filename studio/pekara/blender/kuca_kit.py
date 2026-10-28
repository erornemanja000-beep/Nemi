# Krume, smer 3 "Ein Fenster brennt": maketa ugla kvarta na dasci za hleb.
# Nastavak kuca_proba.py, ali modularno: klasa Kuca gradi kucu iz parametara
# (tlocrt, spratovi, boja, tip nadprozornika, ugao da/ne). To je "kit" za ceo kvart.
# Proceduralno, bez addon-a i bez preuzimanja. Pokretanje:
#   Blender -b -P kuca_kit.py              (gradi, cuva .blend, renderuje kadrove 3 i 4)
#   Blender -b -P kuca_kit.py -- 3         (samo kadar 3; "4" samo kadar 4)
#   Blender -b -P kuca_kit.py -- norender  (samo gradi i cuva .blend)
#   Blender -b -P kuca_kit.py -- bake      (zapece svetlo ugaone kuce i trotoara, izvozi kuca-test.glb)
# Jedinica je metar (kuca u pravoj velicini), "maketa" dolazi iz materijala,
# daske ispod i plitke dubinske ostrine kadra 3.
# Okruzenje: KRUME_SAMPLES, KRUME_BAKE_SAMPLES, KRUME_RES (procenat rezolucije), KRUME_EXPOSURE.

import bpy, bmesh, math, os, random, sys, time
from mathutils import Vector, Matrix, Quaternion, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BAKE = "bake" in ARGS
random.seed(7)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def tint(h, f):
    """sRGB hex ka beloj (f > 0) ili ka crnoj (f < 0)."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    c = [round(v + (255 - v) * f) if f >= 0 else round(v * (1 + f)) for v in c]
    return "#%02x%02x%02x" % tuple(c)


# Paleta iz brief-a i smera 3
NOC, KAMEN, KROV = "#14110f", "#2b2a28", "#3b4048"
KORA, ZAR, TESTO, BRASNO = "#7a4a24", "#e8792b", "#eadbc4", "#f6f1e7"
CREP = "#6e4636"                 # crveno-smedji crep za par suseda

# ---------------------------------------------------------------- scena
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.images):
    for d in list(coll):
        try:
            coll.remove(d)
        except Exception:
            pass
scene = bpy.context.scene


# ---------------------------------------------------------------- materijali
def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    return m, nt, p


def coord(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["Object"]


def noise(nt, co, scale, detail, rough=0.5):
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rough
    nt.links.new(co, nz.inputs["Vector"])
    return nz


# ---- "fotografisana minijatura" (Cycles sekvenca, proba Z1): habanje, prljavstina, nepravilnosti.
# Za web bake (KRUME_WEB u globals, bake_izvoz.py) sve ostaje kao pre: FOTO = False.
FOTO = not globals().get("KRUME_WEB", False)


def sock(nd, ident, out=False):
    """Socket po identifikatoru (Mix ima vise "A"/"B" po tipu)."""
    return next(s for s in (nd.outputs if out else nd.inputs) if s.identifier == ident)


def math_n(nt, op, a, b=None, c=None, clamp=False):
    nd = nt.nodes.new("ShaderNodeMath")
    nd.operation, nd.use_clamp = op, clamp
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            nd.inputs[i].default_value = v
        else:
            nt.links.new(v, nd.inputs[i])
    return nd.outputs[0]


def map_n(nt, val, f0, f1, t0=0.0, t1=1.0):
    mr = nt.nodes.new("ShaderNodeMapRange")
    for k, v in (("From Min", f0), ("From Max", f1), ("To Min", t0), ("To Max", t1)):
        mr.inputs[k].default_value = v
    nt.links.new(val, mr.inputs["Value"])
    return mr.outputs["Result"]


def mix_c(nt, fac, a, b, blend="MIX"):
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type, mx.blend_type = "RGBA", blend
    for s, v in ((sock(mx, "Factor_Float"), fac), (sock(mx, "A_Color"), a), (sock(mx, "B_Color"), b)):
        if isinstance(v, tuple):
            s.default_value = v
        elif isinstance(v, (int, float)):
            s.default_value = v
        else:
            nt.links.new(v, s)
    return sock(mx, "Result_Color", out=True)


def stretched(nt, co, scale, sx=1.0, sy=1.0, sz=1.0, detail=4, rough=0.55):
    """Sum na izduzenim koordinatama (tragovi curenja po Z, pore i vlakna po X)."""
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (sx, sy, sz)
    nt.links.new(co, mp.inputs["Vector"])
    return noise(nt, mp.outputs["Vector"], scale, detail, rough)


def foto_boja(nt, p, co, col, prljav=0.6, ivice=0.0, cad=0.0, curenje=0.55, rough=0.86, ostrvo=0.04):
    """Base Color i Roughness kao na fotografiji makete:
    nijansa/hrapavost po objektu (Object Info Random) i po delu (Random Per Island),
    prljavstina u uglovima i spojevima (AO + Pointiness, pomesano sa sumom), prskanje uz zemlju,
    tragovi curenja ispod simsova (gradijent po spratu puta sum izduzen po Z), svetlije izlizane ivice
    (AO "iznutra") i cadj pri vrhu (dimnjaci). col: izlaz boje, vraca novi izlaz."""
    N = nt.nodes
    info = N.new("ShaderNodeObjectInfo")
    geo = N.new("ShaderNodeNewGeometry")
    # nepravilnost po objektu i po ostrvu (svaka kutija kita je svoje ostrvo)
    hsv = N.new("ShaderNodeHueSaturation")
    nt.links.new(col, hsv.inputs["Color"])
    rnd = info.outputs["Random"]
    nt.links.new(math_n(nt, "MULTIPLY_ADD", rnd, 0.03, 0.485), hsv.inputs["Hue"])
    nt.links.new(math_n(nt, "MULTIPLY_ADD", rnd, 0.16, 0.92), hsv.inputs["Saturation"])
    vi = math_n(nt, "MULTIPLY_ADD", geo.outputs["Random Per Island"], 2 * ostrvo, 1.0 - ostrvo)
    vo = math_n(nt, "MULTIPLY_ADD", rnd, 0.12, 0.94)
    nt.links.new(math_n(nt, "MULTIPLY", vi, vo), hsv.inputs["Value"])
    c = hsv.outputs["Color"]
    sep = N.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    z = sep.outputs["Z"]
    # prljavstina: AO (spolja, 0,6 m) i konkavna Pointiness, pomesano sa sumom
    ao = N.new("ShaderNodeAmbientOcclusion")
    ao.samples = 2                                 # konvergira kroz uzorke rendera
    ao.inputs["Distance"].default_value = 0.6
    kav = map_n(nt, ao.outputs["AO"], 0.97, 0.4)
    kon = map_n(nt, geo.outputs["Pointiness"], 0.5, 0.4)
    nz = noise(nt, co, 2.2, 6, 0.6)
    nzm = map_n(nt, nz.outputs["Fac"], 0.35, 0.7, 0.25, 1.15)
    prlj = math_n(nt, "MULTIPLY", math_n(nt, "ADD", kav, math_n(nt, "MULTIPLY", kon, 0.5)), nzm, clamp=True)
    # prskanje uz zemlju (0-0,9 m)
    tlo = math_n(nt, "MULTIPLY", map_n(nt, z, 0.9, 0.0), map_n(nt, noise(nt, co, 6.0, 4).outputs["Fac"], 0.3, 0.7))
    prlj = math_n(nt, "MAXIMUM", prlj, math_n(nt, "MULTIPLY", tlo, 0.8))
    if curenje:
        # sprat ~3,3 m; jaci trag odmah ispod simsa (1 - fract), izduzen sum po Z
        fr = math_n(nt, "FRACT", math_n(nt, "MULTIPLY_ADD", z, 1 / 3.3, math_n(nt, "MULTIPLY", rnd, 0.6)))
        grad = math_n(nt, "POWER", fr, 1.5)
        trag = map_n(nt, stretched(nt, co, 3.0, 1.0, 1.0, 0.08, 5).outputs["Fac"], 0.48, 0.66)
        prlj = math_n(nt, "MAXIMUM", prlj, math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", grad, trag), curenje))
    grime = (0.22, 0.18, 0.14, 1.0)
    c = mix_c(nt, math_n(nt, "MULTIPLY", prlj, prljav), c, grime, "MULTIPLY")
    if cad:
        gen = N.new("ShaderNodeTexCoord")
        sg = N.new("ShaderNodeSeparateXYZ")
        nt.links.new(gen.outputs["Generated"], sg.inputs["Vector"])
        cz = math_n(nt, "MULTIPLY", map_n(nt, sg.outputs["Z"], 0.55, 1.0),
                    map_n(nt, stretched(nt, co, 4.0, 1.0, 1.0, 0.15).outputs["Fac"], 0.3, 0.6, 0.4, 1.0))
        c = mix_c(nt, math_n(nt, "MULTIPLY", cz, cad, clamp=True), c, (0.035, 0.03, 0.028, 1.0))
    if ivice:
        ai = N.new("ShaderNodeAmbientOcclusion")
        ai.inside, ai.only_local, ai.samples = True, True, 2
        ai.inputs["Distance"].default_value = 0.06
        iz = math_n(nt, "MULTIPLY", map_n(nt, ai.outputs["AO"], 1.0, 0.75),
                    map_n(nt, noise(nt, co, 9.0, 5).outputs["Fac"], 0.4, 0.62), clamp=True)
        c = mix_c(nt, math_n(nt, "MULTIPLY", iz, ivice), c, (0.85, 0.82, 0.76, 1.0), "SCREEN")
    nt.links.new(c, p.inputs["Base Color"])
    # hrapavost: po objektu +-0,05, prljavo je hrapavije
    r = math_n(nt, "MULTIPLY_ADD", rnd, 0.1, rough - 0.05)
    nt.links.new(math_n(nt, "MULTIPLY_ADD", prlj, 0.08, r, clamp=True), p.inputs["Roughness"])
    return c


# ---- FOTO, krug 2: prave PBR teksture i HDRI (Poly Haven, CC0; izvori i MD5 u teksture/QUELLEN.md).
# Kit nema UV mape, pa sve ide Box projekcijom (blend 0,2) na Object koordinatama u stvarnoj velicini.
# vrsta: (folder, sirina celog snimka u m, deo U bez fuga ili None). plastered_wall_02 ima uspravne fuge na
# U = 0, 1/4, 1/2, 3/4: vodoravne koordinate idu "ping-pong" unutar jednog polja (0,27-0,48; Box ga za
# drugu stranu obrne u 0,52-0,73), pa se fuge nikad ne vide, a ogledalni spoj se u zrnu ne primeti.
TEKSTURE = os.path.join(HERE, "teksture")
TEX = {
    "malter": ("plastered_wall_02", 3.5, (0.27, 0.21)),
    "cigla": ("brick_wall_006", 3.5, None),           # ~46 redova: cigla 25 x 6,5 cm sa fugom
    "kocka": ("cobblestone_floor_08", 1.4, None),     # ~11 redova: kocka ~11 cm
    "drvo": ("wood_table_worn", 20.0, None),          # daska: maketa na dasci, vlakno krupno kao na pravoj dasci
    "lim": ("rusty_metal_02", 1.2, None),
}
TEX_SREDINA = {"malter": 0.70, "cigla": 0.49, "kocka": 0.55, "drvo": 0.21, "lim": 0.57}   # srednja svetlina diff
TEX_ROUGH = {"malter": 0.91, "cigla": 0.79, "kocka": 0.58, "drvo": 0.5, "lim": 0.42}      # srednja rough mapa


def slika(folder, mapa):
    ext = "png" if mapa == "disp" else "jpg"
    im = bpy.data.images.load(os.path.join(TEKSTURE, folder, f"{folder}_{mapa}_2k.{ext}"), check_existing=True)
    if mapa != "diff":
        im.colorspace_settings.name = "Non-Color"
    return im


def vmath(nt, op, a, b=None, c=None):
    nd = nt.nodes.new("ShaderNodeVectorMath")
    nd.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None:
            continue
        if isinstance(v, (tuple, list)):
            nd.inputs[i].default_value = v
        elif isinstance(v, (int, float)):
            nd.inputs[i].default_value = (v, v, v)
        else:
            nt.links.new(v, nd.inputs[i])
    return nd.outputs["Value" if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else "Vector"]


def vscale(nt, v, f):
    nd = nt.nodes.new("ShaderNodeVectorMath")
    nd.operation = "SCALE"
    for s, x in ((nd.inputs[0], v), (nd.inputs["Scale"], f)):
        if isinstance(x, (tuple, list, int, float)):
            s.default_value = x
        else:
            nt.links.new(x, s)
    return nd.outputs["Vector"]


def pbr(nt, vrsta, co, mape=("diff", "rough", "nor_gl"), nor=1.0, skala=1.0):
    """Teksture vrste u Box projekciji. Po objektu (Object Info Random) pomak i +-15 % razmere, da susedne
    kuce ne dele isti isecak. Normal mapa: tangente Box projekcije (iste U/V osi i obrtanja kao Cycles box,
    kernel/svm/image.h), tangentni -> object prostor, pa Normal Map cvor (Object). Vraca dict izlaza."""
    N = nt.nodes
    folder, S, polje = TEX[vrsta]
    rnd = N.new("ShaderNodeObjectInfo").outputs["Random"]
    k = math_n(nt, "DIVIDE", math_n(nt, "MULTIPLY_ADD", rnd, 0.3, 0.85), S * skala)
    vec = vmath(nt, "MULTIPLY_ADD", co, k, vscale(nt, (17.31, 11.93, 7.77), rnd))
    mx = my = None
    if polje:
        u0, w = polje
        sp = N.new("ShaderNodeSeparateXYZ")
        nt.links.new(vec, sp.inputs["Vector"])
        cm = N.new("ShaderNodeCombineXYZ")
        zn = []
        for ax in ("X", "Y"):
            t = sp.outputs[ax]
            nt.links.new(math_n(nt, "ADD", math_n(nt, "PINGPONG", t, w), u0), cm.inputs[ax])
            # smer ogledala (+1 rastuce, -1 obrnuto) za tangentu normal mape
            zn.append(math_n(nt, "MULTIPLY_ADD", math_n(nt, "FLOORED_MODULO", math_n(nt, "FLOOR", math_n(nt, "DIVIDE", t, w)), 2.0), -2.0, 1.0))
        nt.links.new(sp.outputs["Z"], cm.inputs["Z"])
        vec = cm.outputs["Vector"]
        mx, my = zn
    out = {}
    for mapa in mape:
        im = N.new("ShaderNodeTexImage")
        im.image = slika(folder, mapa)
        im.projection, im.projection_blend = "BOX", 0.2
        im.interpolation = "Linear"
        nt.links.new(vec, im.inputs["Vector"])
        out[mapa] = im.outputs["Color"]
    if "nor_gl" in out:
        # T, B po osi (Cycles box): X: u=+-y, v=z; Y: u=-+x, v=z; Z: u=-+y, v=x (znak po strani normale)
        tcn = N.new("ShaderNodeTexCoord").outputs["Normal"]                 # object prostor
        a = vmath(nt, "ABSOLUTE", tcn)
        a = vmath(nt, "MULTIPLY", a, a)
        a = vmath(nt, "MULTIPLY", a, a)
        a = vmath(nt, "MULTIPLY", a, a)                                     # |N|^8 ~ blend 0,2
        wv = vmath(nt, "DIVIDE", a, vmath(nt, "DOT_PRODUCT", a, (1.0, 1.0, 1.0)))
        sw, ss = N.new("ShaderNodeSeparateXYZ"), N.new("ShaderNodeSeparateXYZ")
        nt.links.new(wv, sw.inputs["Vector"])
        nt.links.new(vmath(nt, "SIGN", tcn), ss.inputs["Vector"])
        wx, wy, wz = sw.outputs["X"], sw.outputs["Y"], sw.outputs["Z"]
        sx, sy, sz = ss.outputs["X"], ss.outputs["Y"], ss.outputs["Z"]
        tx_ = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", wy, sy), -1.0)
        ty_ = math_n(nt, "SUBTRACT", math_n(nt, "MULTIPLY", wx, sx), math_n(nt, "MULTIPLY", wz, sz))
        bx_ = wz
        if mx is not None:
            tx_, ty_, bx_ = math_n(nt, "MULTIPLY", tx_, mx), math_n(nt, "MULTIPLY", ty_, my), math_n(nt, "MULTIPLY", wz, mx)
        T, B = N.new("ShaderNodeCombineXYZ"), N.new("ShaderNodeCombineXYZ")
        nt.links.new(tx_, T.inputs["X"])
        nt.links.new(ty_, T.inputs["Y"])
        nt.links.new(bx_, B.inputs["X"])
        nt.links.new(math_n(nt, "ADD", wx, wy), B.inputs["Z"])
        tn = N.new("ShaderNodeSeparateXYZ")
        nt.links.new(vmath(nt, "MULTIPLY_ADD", out["nor_gl"], 2.0, -1.0), tn.inputs["Vector"])
        n = vmath(nt, "ADD", vmath(nt, "ADD", vscale(nt, T.outputs["Vector"], tn.outputs["X"]),
                                   vscale(nt, B.outputs["Vector"], tn.outputs["Y"])), vscale(nt, tcn, tn.outputs["Z"]))
        nm = N.new("ShaderNodeNormalMap")
        nm.space = "OBJECT"
        nm.inputs["Strength"].default_value = nor
        nt.links.new(vmath(nt, "MULTIPLY_ADD", vmath(nt, "NORMALIZE", n), 0.5, 0.5), nm.inputs["Color"])
        out["normal"] = nm.outputs["Normal"]
    if "diff" in out:
        bw = N.new("ShaderNodeRGBToBW")
        nt.links.new(out["diff"], bw.inputs["Color"])
        out["svetlina"] = bw.outputs["Val"]
    if "rough" in out:
        out["rough_v"] = sock_bw(nt, out["rough"])
    if "disp" in out:
        out["disp_v"] = sock_bw(nt, out["disp"])
    return out


def sock_bw(nt, col):
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(col, bw.inputs["Color"])
    return bw.outputs["Val"]


def tex_boja(nt, t, vrsta, col, ton=1.0, kontrast=1.0):
    """Diff tekstura tonirana bojom objekta: boja * (svetlina / srednja, pojacan kontrast); ton < 1 ostavlja deo
    prave boje teksture (cigla na dimnjaku)."""
    m = TEX_SREDINA[vrsta]
    f = map_n(nt, t["svetlina"], m * (1 - 0.1 / kontrast), m * (1 + 0.1 / kontrast), 0.9, 1.1)
    c = mix_c(nt, 1.0, col, f, "MULTIPLY")
    if ton < 1.0:
        c = mix_c(nt, 1.0 - ton, c, t["diff"], "MIX")
    return c


def mrlje(nt, co, c, jacina=0.08):
    """Krupne mrlje u malteru (krpljenje, razlicito izbledelo): sum 2-5 m, +-jacina svetline, malo toplije/hladnije."""
    nz = noise(nt, co, 0.28, 3, 0.55)
    sv = map_n(nt, nz.outputs["Fac"], 0.35, 0.65, 1.0 - jacina, 1.0 + jacina)
    c = mix_c(nt, 1.0, c, sv, "MULTIPLY")
    zak = map_n(nt, noise(nt, co, 0.9, 2).outputs["Fac"], 0.55, 0.7)            # ostro ivicene zakrpe
    return mix_c(nt, math_n(nt, "MULTIPLY", zak, 0.35), c, mix_c(nt, 1.0, c, (1.08, 1.05, 1.0, 1.0), "MULTIPLY"))


def mat_plaster(name, col, var=0.07, bump=0.3, rough=0.86, prljav=0.75, ivice=0.0, cad=0.0, curenje=0.65, tex=None, ton=1.0, nor=0.8):
    """Rucno bojen gips/karton: mrlja u boji, krupna neravnina (gips) i sitno zrno (karton).
    FOTO + tex ("malter", "cigla", "kalkan" = malter sa otpalim delovima do cigle): prave teksture ispod maski."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    nz = noise(nt, co, 0.35, 4)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    c0 = hexc(col)
    ramp.color_ramp.elements[0].color = tuple(max(0, c * (1 - var)) for c in c0[:3]) + (1,)
    ramp.color_ramp.elements[1].color = tuple(min(1, c * (1 + var)) for c in c0[:3]) + (1,)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    coarse = noise(nt, co, 1.7, 3, 0.45)
    fine = noise(nt, co, 16.0, 6, 0.6)
    bp1 = nt.nodes.new("ShaderNodeBump")
    bp1.inputs["Strength"].default_value = bump
    bp1.inputs["Distance"].default_value = 0.05
    nt.links.new(coarse.outputs["Fac"], bp1.inputs["Height"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump * 0.7
    bp.inputs["Distance"].default_value = 0.012
    nt.links.new(fine.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp1.outputs["Normal"], bp.inputs["Normal"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    if FOTO:
        c = ramp.outputs["Color"]
        if tex:
            vr = "malter" if tex == "kalkan" else tex
            t = pbr(nt, vr, co, nor=nor)
            c = tex_boja(nt, t, vr, c, ton=ton, kontrast=2.0 if vr == "malter" else 1.0)
            nrm = t["normal"]
            if vr == "malter":
                c = mrlje(nt, co, c)
            if tex == "kalkan":
                # kalkan (Feuermauer): malter mestimicno otpao do cigle, vise pri dnu i uz ivice krova
                tc = pbr(nt, "cigla", co, nor=1.0)
                cig = tex_boja(nt, tc, "cigla", hexc("#9a5a40"), ton=0.35)
                mk = map_n(nt, noise(nt, co, 0.45, 5, 0.6).outputs["Fac"], 0.56, 0.585)
                c = mix_c(nt, mk, c, cig)
                mx = nt.nodes.new("ShaderNodeMix")
                mx.data_type = "VECTOR"
                nt.links.new(mk, mx.inputs["Factor"])
                nt.links.new(nrm, sock(mx, "A_Vector"))
                nt.links.new(tc["normal"], sock(mx, "B_Vector"))
                nrm = sock(mx, "Result_Vector", out=True)
            nt.links.new(nrm, bp1.inputs["Normal"])
            bp.inputs["Strength"].default_value = bump * 0.35          # sitno zrno sad daje tekstura
        foto_boja(nt, p, co, c, prljav=prljav, ivice=ivice, cad=cad, curenje=curenje, rough=rough)
        if tex:
            r0 = p.inputs["Roughness"].links[0].from_socket
            dr = math_n(nt, "SUBTRACT", t["rough_v"], TEX_ROUGH[vr])
            nt.links.new(math_n(nt, "MULTIPLY_ADD", dr, 0.6, r0, clamp=True), p.inputs["Roughness"])
    return m, nt, p, co, bp


def mat_ribs(name, col, freq=2.0, gap=0.07, strength=0.6, metal=0.0, rough=0.86, tex=None):
    """Vodoravne fuge: rustika prizemlja (2 po metru) ili rebra rolo-bedema (Rollbalken)."""
    m, nt, p, co, bp = mat_plaster(name, col, var=0.08, bump=0.22, rough=rough, tex=tex)
    p.inputs["Metallic"].default_value = metal
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = freq
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    gr = nt.nodes.new("ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.0
    gr.inputs["From Max"].default_value = gap
    nt.links.new(fr.outputs[0], gr.inputs["Value"])
    bp2 = nt.nodes.new("ShaderNodeBump")
    bp2.inputs["Strength"].default_value = strength
    bp2.inputs["Distance"].default_value = 0.03
    nt.links.new(gr.outputs["Result"], bp2.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bp2.inputs["Normal"])
    nt.links.new(bp2.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_brick(name, c1, c2, mortar, scale, bump=0.4, rough=0.9, mokro=0.0, nerav=0.0, tex=None):
    """Kocka na ulici, ploce trotoara, crep: Brick Texture u XY ravni.
    FOTO: nerav = iskrivljeni redovi (crep, lim, kocka), mokro = vlazna povrsina sa baricama
    (barice u fugama i udubljenjima, glatke i tamnije: noci hvataju odsjaje izloga i lampi)."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    vec = co
    if FOTO and nerav:
        w = noise(nt, co, 0.45, 2)
        wv = nt.nodes.new("ShaderNodeVectorMath")
        wv.operation = "MULTIPLY_ADD"
        wv.inputs[1].default_value = (nerav, nerav, nerav * 0.3)
        nt.links.new(w.outputs["Color"], wv.inputs[0])
        nt.links.new(co, wv.inputs[2])
        vec = wv.outputs["Vector"]
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = hexc(c1)
    br.inputs["Color2"].default_value = hexc(c2)
    br.inputs["Mortar"].default_value = hexc(mortar)
    br.inputs["Scale"].default_value = scale
    br.inputs["Mortar Size"].default_value = 0.025
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 0.25
    br.offset = 0.5
    nt.links.new(vec, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.03
    nt.links.new(br.outputs[1], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    if not FOTO:
        return m
    # varijacija po cigli: Bias uz Color1/Color2 ostaje, a svaka cigla dobija jos i sum po povrsini
    br.inputs["Color1"].default_value = hexc(tint(c1, -0.12))
    br.inputs["Color2"].default_value = hexc(tint(c2, 0.1))
    zr = noise(nt, co, 14.0, 6, 0.6)
    col = mix_c(nt, 0.35, br.outputs["Color"], zr.outputs["Color"], "OVERLAY")
    fuga = br.outputs[1]
    if tex:
        # prava kocka: diff toniran paletom (kamen ostaje sivo-smedj-plav po komadu), normal + disp kao bump,
        # fuge iz disp (nisko = fuga)
        t = pbr(nt, tex, co, mape=("diff", "rough", "nor_gl", "disp"))
        col = tex_boja(nt, t, tex, hexc(c2), kontrast=0.45)
        col = mix_c(nt, 0.4, col, mix_c(nt, 1.0, t["diff"], (0.62, 0.62, 0.62, 1.0), "MULTIPLY"))
        fuga = map_n(nt, t["disp_v"], 0.42, 0.18)
        nt.links.new(t["disp_v"], bp.inputs["Height"])
        bp.inputs["Distance"].default_value = 0.04
        nt.links.new(t["normal"], bp.inputs["Normal"])
    c = foto_boja(nt, p, co, col, prljav=0.35, curenje=0.0, rough=rough, ostrvo=0.0)
    if mokro:
        # mapa barica: krupni sum, fuge (Fac=1 u fugi) su vlaznije; "voda" = 0 suvo .. 1 barica
        bar = noise(nt, co, 0.11, 3, 0.5)
        fug = math_n(nt, "MULTIPLY", fuga, 0.08)
        voda = map_n(nt, math_n(nt, "ADD", bar.outputs["Fac"], fug), 0.56, 0.6)
        vl = map_n(nt, noise(nt, co, 0.6, 3).outputs["Fac"], 0.4, 0.6, 0.35, 0.55)   # vlazna, ne suva kocka
        if tex:   # mokro = rough mape smanjen (kamen ostaje hrapaviji od fuge), mestimicno vlaznije
            vl = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", t["rough_v"], 0.8), map_n(nt, vl, 0.35, 0.55, 0.6, 1.0))
        hr = math_n(nt, "MAXIMUM", math_n(nt, "MULTIPLY", map_n(nt, voda, 0.0, 1.0, 1.0, 0.0), vl), 0.03)
        nt.links.new(hr, p.inputs["Roughness"])
        tam = mix_c(nt, math_n(nt, "MULTIPLY_ADD", voda, 0.3, mokro), c, (0.0, 0.0, 0.0, 1.0), "MIX")
        nt.links.new(tam, p.inputs["Base Color"])
        nt.links.new(map_n(nt, voda, 0.0, 1.0, bump, 0.0), bp.inputs["Strength"])       # barica je ravna
    return m


def mat_wood_board(name):
    """Daska za hleb: kora boja sa godovima (Wave) i sitnom mrljom.
    FOTO: godovi Wave + Noise, pore duz vlakna, ogrebotine nozem (dva pravca), ulje (sjaj varira)."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.06, 1.0, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"; wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 0.7
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexc("#7a4a24")
    ramp.color_ramp.elements[1].color = hexc("#b9824a")
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.5
    if not FOTO:
        return m
    N = nt.nodes
    # godovi: Wave iskrivljen Noise-om (vektorski pomak), pa tanje tamne linije kasnog drveta
    dn = stretched(nt, co, 0.35, 0.08, 1.0, 1.0, 3)
    wq = N.new("ShaderNodeVectorMath")
    wq.operation = "MULTIPLY_ADD"
    wq.inputs[1].default_value = (0.0, 0.9, 0.4)
    nt.links.new(dn.outputs["Color"], wq.inputs[0])
    nt.links.new(mp.outputs["Vector"], wq.inputs[2])
    nt.links.new(wq.outputs["Vector"], wv.inputs["Vector"])
    wv.wave_type = "RINGS"
    mp.inputs["Location"].default_value = (0.0, 4.0, 14.0)
    wv.inputs["Scale"].default_value = 0.9
    wv.inputs["Distortion"].default_value = 1.5
    wv.inputs["Detail"].default_value = 4
    wv.inputs["Detail Roughness"].default_value = 0.6
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.0, 0.7
    ramp.color_ramp.elements[0].color = hexc("#80502a")
    ramp.color_ramp.elements[1].color = hexc("#b47c45")
    el = ramp.color_ramp.elements.new(0.92)
    el.color = hexc("#c8925a")
    # pore: sitan sum jako izduzen duz vlakna (X), tamne crtice
    pore = map_n(nt, stretched(nt, co, 22.0, 0.04, 1.0, 1.0, 2).outputs["Fac"], 0.62, 0.7)
    c = mix_c(nt, math_n(nt, "MULTIPLY", pore, 0.45), ramp.outputs["Color"], hexc("#3a1f0e"))
    # ogrebotine: ivice Voronoi celija na izduzenim koordinatama, dva pravca, samo mestimicno
    ogr = []
    for rot, sc in ((0.35, (0.15, 1.0, 1.0)), (-0.6, (0.12, 1.0, 1.0))):
        mr = N.new("ShaderNodeMapping")
        mr.inputs["Rotation"].default_value = (0.0, 0.0, rot)
        mr.inputs["Scale"].default_value = sc
        nt.links.new(co, mr.inputs["Vector"])
        vo = N.new("ShaderNodeTexVoronoi")
        vo.feature = "DISTANCE_TO_EDGE"
        vo.inputs["Scale"].default_value = 1.6
        nt.links.new(mr.outputs["Vector"], vo.inputs["Vector"])
        ogr.append(map_n(nt, vo.outputs["Distance"], 0.012, 0.0))
    gde = map_n(nt, noise(nt, co, 0.25, 2).outputs["Fac"], 0.45, 0.6)
    og = math_n(nt, "MULTIPLY", math_n(nt, "MAXIMUM", ogr[0], ogr[1]), gde, clamp=True)
    # krug 2: prava daska (wood_table_worn) nosi vlakno, istrosenost i sjaj; godovi ostaju kao ton ispod
    t = pbr(nt, "drvo", co, nor=0.7)
    c = tex_boja(nt, t, "drvo", c, kontrast=0.6)
    c = mix_c(nt, math_n(nt, "MULTIPLY", og, 0.5), c, hexc("#d9ad78"))
    # rub daske tamniji (ruke, ulje), sredina malo izbledela
    c = foto_boja(nt, p, co, c, prljav=0.25, curenje=0.0, rough=0.42, ostrvo=0.0)
    hr = math_n(nt, "ADD", math_n(nt, "MULTIPLY", og, 0.3),
                map_n(nt, noise(nt, co, 0.5, 3).outputs["Fac"], 0.3, 0.7, 0.32, 0.55))
    hr = math_n(nt, "MULTIPLY_ADD", math_n(nt, "SUBTRACT", t["rough_v"], TEX_ROUGH["drvo"]), 0.6, hr)
    nt.links.new(math_n(nt, "MINIMUM", hr, 1.0), p.inputs["Roughness"])
    bp.inputs["Strength"].default_value = 0.08
    b2 = N.new("ShaderNodeBump")
    b2.inputs["Strength"].default_value = 0.35
    b2.inputs["Distance"].default_value = 0.01
    nt.links.new(math_n(nt, "SUBTRACT", math_n(nt, "SUBTRACT", 1.0, og), math_n(nt, "MULTIPLY", pore, 0.5)), b2.inputs["Height"])
    nt.links.new(t["normal"], bp.inputs["Normal"])
    nt.links.new(bp.outputs["Normal"], b2.inputs["Normal"])
    nt.links.new(b2.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_simple(name, col, rough=0.7, metal=0.0, emit=None, strength=0.0, coat=0.0):
    m, nt, p = node_mat(name)
    p.inputs["Base Color"].default_value = hexc(col)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.18
    if emit:
        p.inputs["Emission Color"].default_value = hexc(emit)
        p.inputs["Emission Strength"].default_value = strength
    return m


def mat_glass(name):
    m, nt, p = node_mat(name)
    p.inputs["Base Color"].default_value = hexc("#d8e0e8")
    p.inputs["Roughness"].default_value = 0.03
    p.inputs["Transmission Weight"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.05
    return m


def mat_glow(name, strength):
    """Zadnji zid izloga: topla emisija, jaca dole (kao svetlo sa pulta)."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.4
    mr.inputs["From Max"].default_value = 3.8
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexc("#ffc27e")
    ramp.color_ramp.elements[1].color = hexc(ZAR)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    p.inputs["Base Color"].default_value = hexc(TESTO)
    nt.links.new(ramp.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = strength
    return m


def mat_smoke(name):
    """Dim iz dimnjaka: volumen u svakoj kugli, gust u sredini, rastrgan sumom (4D, W po objektu)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = nt.nodes["Material Output"]
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = hexc("#ece6de")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = "SPHERICAL"
    nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
    info = nt.nodes.new("ShaderNodeObjectInfo")
    wmul = nt.nodes.new("ShaderNodeMath"); wmul.operation = "MULTIPLY"
    wmul.inputs[1].default_value = 20.0
    nt.links.new(info.outputs["Random"], wmul.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 1.6
    nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(wmul.outputs[0], nz.inputs["W"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.4
    mr.inputs["From Max"].default_value = 0.68
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"
    nt.links.new(gr.outputs["Fac"], m1.inputs[0])
    nt.links.new(mr.outputs["Result"], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    m2.inputs[1].default_value = 5.0
    nt.links.new(m1.outputs[0], m2.inputs[0])
    nt.links.new(m2.outputs[0], pv.inputs["Density"])
    nt.links.new(pv.outputs["Volume"], out.inputs["Volume"])
    return m


def foto_staklo(m):
    """FOTO: okno nije jednako crno: po prozoru (ostrvu) tamna zavesa ili odsjaj, malo hrapavosti."""
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.interpolation = "CONSTANT"
    cr = rp.color_ramp
    cr.elements.new(0.6)
    cr.elements.new(0.85)
    for i, (pos, h) in enumerate(((0.0, "#0b0e13"), (0.35, "#1d1a17"), (0.6, "#2c2620"), (0.85, "#121418"))):
        cr.elements[i].position = pos
        cr.elements[i].color = hexc(h)
    nt.links.new(geo.outputs["Random Per Island"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    nt.links.new(map_n(nt, geo.outputs["Random Per Island"], 0.0, 1.0, 0.06, 0.2), p.inputs["Roughness"])
    return m


def foto_lim(m):
    """FOTO: lim (oluci, stubovi lampi, sine, opsavi): rusty_metal_02 potamnjen bojom, rdja samo kao topliji trag,
    hrapavost iz mape (rdja je hrapava, lim sjajniji)."""
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    co = coord(nt)
    t = pbr(nt, "lim", co, nor=0.4)
    col = p.inputs["Base Color"].default_value[:]
    c = tex_boja(nt, t, "lim", col, kontrast=0.7)
    c = mix_c(nt, 0.3, c, mix_c(nt, 1.0, t["diff"], (0.16, 0.14, 0.12, 1.0), "MULTIPLY"))
    c = foto_boja(nt, p, co, c, prljav=0.4, curenje=0.4, rough=0.5, ostrvo=0.03)
    nt.links.new(math_n(nt, "MULTIPLY_ADD", math_n(nt, "SUBTRACT", t["rough_v"], TEX_ROUGH["lim"]), 1.2, 0.5, clamp=True),
                 p.inputs["Roughness"])
    nt.links.new(t["normal"], p.inputs["Normal"])
    return m


M = {
    "sokla": mat_plaster("sokla", "#5e5850", var=0.1, bump=0.35, ivice=0.45, tex="cigla", ton=0.55)[0],
    "dimnjak": mat_plaster("dimnjak", "#9a8c7a", var=0.1, bump=0.35, cad=0.9, curenje=0.0, tex="cigla", ton=0.3)[0],
    "staklo_tamno": (foto_staklo if FOTO else (lambda m: m))(mat_simple("staklo_tamno", "#0b0e13", rough=0.12)),
    "staklo_slabo": mat_simple("staklo_slabo", "#1a120c", rough=0.2, emit="#b8682a", strength=0.12),
    "okvir": mat_plaster("okvir", "#e3dac8", var=0.03, bump=0.1, rough=0.6)[0],
    "drvo_radnja": mat_simple("drvo_radnja", "#4a2c16", rough=0.5),
    "tabla": mat_simple("tabla", "#5e1f17", rough=0.32, coat=0.6),            # lakirana, tamnocrvena
    "tabla_zel": mat_simple("tabla_zel", "#22382c", rough=0.36, coat=0.5),     # susedi: tamnozelena
    "zlato": mat_simple("zlato", "#c8963f", rough=0.32, metal=1.0),
    "zar": mat_glow("zar", 1.8),
    "staklo": mat_glass("staklo"),
    "hleb": mat_plaster("hleb", KORA, var=0.25, bump=0.4, rough=0.55, prljav=0.15, curenje=0.0)[0],
    "kocka": mat_brick("kocka", "#3a3631", "#4a453e", "#181614", 3.2, bump=0.6, mokro=0.3, nerav=0.02, tex="kocka"),
    "trotoar": mat_brick("trotoar", "#5a5650", "#625e57", "#34312e", 0.9, bump=0.3, mokro=0.15, nerav=0.01),
    "ivicnjak": mat_plaster("ivicnjak", "#7a756d", var=0.1, bump=0.3, ivice=0.6, curenje=0.0)[0],
    "dvoriste": mat_plaster("dvoriste", "#5b5145", var=0.18, bump=0.8, curenje=0.0)[0],
    "daska": mat_wood_board("daska"),
    "metal": (foto_lim if FOTO else (lambda m: m))(mat_simple("metal", "#1b221f", rough=0.45, metal=0.6)),
    "lampa": mat_simple("lampa", "#cfd8e6", rough=0.3, emit="#ffc58a" if FOTO else "#bcd0f0", strength=2.0),   # FOTO: ~2700 K,
    "lampica": mat_simple("lampica", "#ffe2b8", rough=0.3, emit="#ffc68a", strength=6.0),
    "sanduk": mat_plaster("sanduk", "#6b4a2c", var=0.12, bump=0.3, ivice=0.4, curenje=0.0)[0],
    "roleta": mat_ribs("roleta", "#6c6d6a", freq=12.0, gap=0.25, strength=0.35, metal=0.4, rough=0.5),
    "krosnja": mat_plaster("krosnja", "#4c5a36", var=0.2, bump=1.0, rough=0.95, prljav=0.2, curenje=0.0)[0],
    "stablo": mat_plaster("stablo", "#4a3a2c", var=0.1, bump=0.4, curenje=0.0)[0],
    "dim": mat_smoke("dim"),
}
if FOTO:   # poneki upaljen prozor u polusenci (kuce preko puta): topao iza zavese, slabiji od izloga pekare
    M["staklo_upaljen"] = mat_simple("staklo_upaljen", "#1a120c", rough=0.2, emit="#ffb36b", strength=1.4)


# ---------------------------------------------------------------- geometrija
class Builder:
    """Skuplja sve delove jednog materijala u jedan mesh, pa im da bevel."""

    def __init__(self, name, mat, bevel=0.025, seg=2, smooth=False):
        self.name, self.mat, self.bevel, self.seg, self.smooth = name, mat, bevel, seg, smooth
        self.bm = bmesh.new()

    def finish(self):
        bm = self.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        if self.smooth:
            for f in bm.faces:
                f.smooth = True
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(self.mat)
        if self.bevel > 0:
            bv = ob.modifiers.new("Bevel", "BEVEL")
            bv.width = self.bevel
            # FOTO: pun geometrijski bevel, 2-3 segmenta (zaobljena ivica hvata svetlo kao na pravoj maketi)
            bv.segments = max(2, min(3, self.seg + 1)) if FOTO and self.bevel < 0.3 else self.seg
            bv.limit_method = "ANGLE"
            bv.angle_limit = math.radians(35)
        return ob


def jitter_q(amount_deg=0.5):
    a = math.radians(amount_deg)
    return Euler((random.uniform(-a, a) * 0.5, random.uniform(-a, a) * 0.5, random.uniform(-a, a))).to_quaternion()


def wbox(b, center, size, angle=0.0, jit=True):
    q = Quaternion((0, 0, 1), angle)
    if jit:
        q = q @ jitter_q()
        center = Vector(center) + Vector([random.uniform(-0.006, 0.006) for _ in range(3)])
    bmesh.ops.create_cube(b.bm, size=1.0, matrix=Matrix.LocRotScale(Vector(center), q, Vector(size)))


class Facade:
    """Ulicna fasada: P pocetak, d pravac duz fasade, n spoljna normala, L duzina."""

    def __init__(self, P, Q):
        self.P = Vector((P[0], P[1], 0))
        v = Vector((Q[0] - P[0], Q[1] - P[1], 0))
        self.L = v.length
        self.d = v.normalized()
        self.n = Vector((self.d.y, -self.d.x, 0))
        self.ang = math.atan2(self.d.y, self.d.x)

    def pt(self, s, o, z):
        return self.P + self.d * s + self.n * o + Vector((0, 0, z))

    def box(self, b, s, z, w, depth, h, o, jit=True):
        """Kutija: s centar duz fasade, z dno, o centar po normali (+ napolje)."""
        wbox(b, self.pt(s, o, z + h / 2), (w, depth, h), self.ang, jit)

    def extrude(self, b, s, z, profile, o0, o1):
        """Profil (u duz fasade, v gore) izvucen po normali od o0 do o1."""
        self._prism(b, [self.pt(s + u, o0, z + v) for u, v in profile],
                    [self.pt(s + u, o1, z + v) for u, v in profile])

    def extrude_s(self, b, s0, s1, profile):
        """Profil (o po normali, z gore) izvucen duz fasade od s0 do s1 (krov, kalkan)."""
        self._prism(b, [self.pt(s0, o, z) for o, z in profile], [self.pt(s1, o, z) for o, z in profile])

    @staticmethod
    def _prism(b, p0, p1):
        bm = b.bm
        r0 = [bm.verts.new(p) for p in p0]
        r1 = [bm.verts.new(p) for p in p1]
        k = len(r0)
        bm.faces.new(r0)
        bm.faces.new(list(reversed(r1)))
        for i in range(k):
            j = (i + 1) % k
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))


def line_isect(p1, d1, p2, d2):
    den = d1.x * d2.y - d1.y * d2.x
    t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / den
    return p1 + d1 * t


def offset_poly(poly, dists):
    """Konveksan CCW poligon, svaka ivica pomerena napolje za svoje rastojanje."""
    k = len(poly)
    lines = []
    for i in range(k):
        a, c = Vector(poly[i]), Vector(poly[(i + 1) % k])
        d = (c - a).normalized()
        n = Vector((d.y, -d.x))
        lines.append((a + n * dists[i], d))
    out = []
    for i in range(k):
        p1, d1 = lines[i - 1]
        p2, d2 = lines[i]
        q = line_isect(p1, d1, p2, d2)
        out.append((q.x, q.y))
    return out


def frustum(b, polyA, zA, polyB, zB):
    bm = b.bm
    ra = [bm.verts.new((x, y, zA)) for x, y in polyA]
    rb = [bm.verts.new((x, y, zB)) for x, y in polyB]
    bm.faces.new(list(reversed(ra)))
    bm.faces.new(rb)
    k = len(ra)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((ra[i], ra[j], rb[j], rb[i]))


def prism(b, poly, z0, z1):
    frustum(b, poly, z0, poly, z1)


def ring(b, outer, z0, z1, inner, outer_top=None):
    """Prsten (venac, sokla, ivicnjak): spolja outer (gore outer_top), iznutra inner.
    Zatvoren je, a nema velike skrivene poklopce preko celog tlocrta (bitno za UV atlas)."""
    bm = b.bm
    ot = outer_top or outer
    ob = [bm.verts.new((x, y, z0)) for x, y in outer]
    oT = [bm.verts.new((x, y, z1)) for x, y in ot]
    ib = [bm.verts.new((x, y, z0)) for x, y in inner]
    iT = [bm.verts.new((x, y, z1)) for x, y in inner]
    k = len(outer)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((ob[i], ob[j], oT[j], oT[i]))
        bm.faces.new((iT[i], iT[j], ib[j], ib[i]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
        bm.faces.new((oT[i], oT[j], iT[j], iT[i]))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def lathe(b, center, profile, seg=16, rot=0.0):
    """Telo okretanja: profil (r, z), r=0 na krajevima zatvara vrh/dno."""
    bm = b.bm
    cx, cy, cz = center
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((cx, cy, cz + z))])
        else:
            rings.append([bm.verts.new((cx + r * math.cos(rot + 2 * math.pi * i / seg),
                                        cy + r * math.sin(rot + 2 * math.pi * i / seg), cz + z))
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
    if len(rings[0]) > 1:
        bm.faces.new(list(reversed(rings[0])))
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1])


def ellipsoid(b, center, size, rot=0.0, seg=(14, 9)):
    q = Quaternion((0, 0, 1), rot) @ jitter_q(4)
    bmesh.ops.create_uvsphere(b.bm, u_segments=seg[0], v_segments=seg[1], radius=0.5,
                              matrix=Matrix.LocRotScale(Vector(center), q, Vector(size)))


# ---------------------------------------------------------------- svetla (pravi ih i kit)
def add_light(name, typ, loc, rot_dir=None, **kw):
    ld = bpy.data.lights.new(name, typ)
    for k, v in kw.items():
        setattr(ld, k, v)
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    if rot_dir is not None:
        ob.rotation_euler = Vector(rot_dir).normalized().to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(ob)
    return ob


WARM = (1.0, 0.52, 0.2)

# ---------------------------------------------------------------- kit: kuca iz parametara
# Builder po kljucu: (materijal, bevel, segmenti). Materijal se prvo trazi u kuci (boja fasade), pa u M.
BSPEC = {
    "fasada": ("fasada", 0.08, 3), "krovfas": ("fasada", 0.05, 2), "stuko": ("stuko", 0.03, 2),
    "okvir": ("okvir", 0.01, 1), "tamno": ("staklo_tamno", 0, 1), "slabo": ("staklo_slabo", 0, 1),
    "cut_up": ("fasada", 0, 1), "cut_gf": ("fasada", 0, 1), "prizemlje": ("prizemlje", 0.07, 3),
    "sokla": ("sokla", 0.05, 2), "krov": ("krov", 0.07, 2), "dimnjak": ("dimnjak", 0.06, 2),
    "metal": ("metal", 0.01, 1), "drvo": ("drvo_radnja", 0.02, 1), "tabla": ("tabla", 0.04, 2),
    "tabla_zel": ("tabla_zel", 0.04, 2), "zlato": ("zlato", 0.012, 1), "zar": ("zar", 0, 1),
    "staklo": ("staklo", 0, 1), "hleb": ("hleb", 0, 1), "sanduk": ("sanduk", 0.03, 2),
    "roleta": ("roleta", 0.015, 1), "lampica": ("lampica", 0, 1), "kalkan": ("kalkan", 0.05, 2),
    "upaljen": ("staklo_upaljen", 0, 1),
}
CUTTERS = ("cut_up", "cut_gf")


class Kuca:
    """Gruenderzeit kuca. foot: konveksan CCW tlocrt; street: indeksi ivica ka ulici;
    axes: {ivica: [s osa prozora]}; nad: tip nadprozornika po spratu
    ("zabat", "ravna", "venac", "luk", "kamen"); ugao: zakosen ugao sa kupolom i balkonom
    (chamfer = indeks zakosene ivice); krov: "mansarda" ili "sattel" (zabat na bocnim zidovima)."""

    def __init__(self, name, foot, street, axes, boja, gf=4.5, fl=3.4, nf=4,
                 nad=("zabat", "ravna", "venac", "kamen"), ugao=False, chamfer=None,
                 krov="sattel", krov_boja=KROV, lit=(), mansarde=True):
        self.name, self.foot, self.street, self.axes = name, foot, set(street), axes
        self.gf, self.fl, self.nf, self.sc = gf, fl, nf, fl / 3.4
        self.top = gf + fl * nf
        self.R0 = self.top + 0.52
        self.nad, self.ugao, self.chamfer, self.krov_tip = nad, ugao, chamfer, krov
        self.lit, self.mansarde = set(lit), mansarde
        self.fac = {i: Facade(foot[i], foot[(i + 1) % len(foot)]) for i in range(len(foot))}
        self.M = {
            "fasada": mat_plaster(name + "_fasada", boja, tex="malter")[0],
            "stuko": mat_plaster(name + "_stuko", tint(boja, 0.38), var=0.04, bump=0.2, ivice=0.25, tex="malter", nor=0.5)[0],
            "prizemlje": mat_ribs(name + "_prizemlje", tint(boja, -0.3), tex="malter"),
            "krov": mat_brick(name + "_krov", krov_boja, tint(krov_boja, -0.12), tint(krov_boja, -0.35),
                              1.4, bump=0.35, rough=0.75, nerav=0.035),
        }
        if FOTO:   # kalkan (Feuermauer) je poseban materijal: malter sa otpalim delovima do cigle
            self.M["kalkan"] = mat_plaster(name + "_kalkan", tint(boja, -0.08), prljav=0.9, curenje=0.8, tex="kalkan")[0]
        self.B, self.obj, self.dim = {}, {}, []

    def b(self, key):
        if key not in self.B:
            mk, bev, seg = BSPEC[key]
            self.B[key] = Builder(f"{self.name}_{key}", self.M.get(mk) or M[mk], bev, seg, smooth=key == "hleb")
        return self.B[key]

    def offs(self, v, back=None):
        return [v if i in self.street else (min(v, -0.01) if back is None else back) for i in range(len(self.foot))]

    # --- masa i venci
    def masa(self):
        F, gf, top = self.foot, self.gf, self.top
        prism(self.b("fasada"), F, gf, top + 0.02)
        prism(self.b("prizemlje"), F, 0.0, gf)
        IN = offset_poly(F, [-0.35] * len(F))                               # unutrasnja ivica prstenova
        ring(self.b("sokla"), offset_poly(F, self.offs(0.06)), 0.0, 0.5, IN)
        st, o = self.b("stuko"), self.offs
        ring(st, offset_poly(F, o(0.16)), gf - 0.22, gf + 0.02, IN)          # venac prizemlja
        ring(st, offset_poly(F, o(0.28)), gf + 0.02, gf + 0.2, IN)
        for k in range(1, self.nf):
            zb = gf + self.fl * k
            ring(st, offset_poly(F, o(0.07)), zb + 0.6 * self.sc, zb + 0.76 * self.sc, IN)   # parapetni venac
        ring(st, offset_poly(F, o(0.04)), top - 0.55, top - 0.05, IN)        # friz
        ring(st, offset_poly(F, o(0.14)), top - 0.05, top + 0.1, IN)
        ring(st, offset_poly(F, o(0.55)), top + 0.3, top + 0.52, IN)          # krovni venac
        ring(st, offset_poly(F, o(0.2)), top + 0.1, top + 0.3, IN, outer_top=offset_poly(F, o(0.55)))
        for e, ax in self.axes.items():                                    # zubci i konzole
            fac = self.fac[e]
            n = int(fac.L / 0.34)
            for i in range(n):
                fac.box(st, 0.17 + i * fac.L / n, top + 0.1, 0.13, 0.2, 0.18, 0.26)
            for s in ax:
                for ds in (-0.85, 0.85):
                    if 0.3 < s + ds < fac.L - 0.3:
                        fac.box(st, s + ds, top - 0.6, 0.22, 0.4, 0.85, 0.22)
        for e in self.axes:                                                # lizene na krajevima
            fac = self.fac[e]
            for s in (0.18, fac.L - 0.18):
                fac.box(st, s, gf + 0.2, 0.36, 0.06, top - gf - 0.75, 0.03)

    # --- prozori na spratovima
    def prozor(self, e, s, k):
        fac, sc = self.fac[e], self.sc
        st, ok = self.b("stuko"), self.b("okvir")
        zb = self.gf + self.fl * k
        w = 1.25 if e == self.chamfer else 1.15
        hs = (2.3, 2.1, 2.0, 1.75) if self.nf >= 4 else (2.25, 2.0, 1.7)
        h = hs[min(k, len(hs) - 1)] * sc
        z0 = zb + 0.85 * sc
        balkon = self.ugao and e == self.chamfer and k == 0
        if balkon:                                   # balkonska vrata na uglu
            z0, h = zb + 0.95, 2.45
        fac.box(self.b("cut_up"), s, z0, w, 0.6, h, 0.0, jit=False)
        glass = self.b("slabo") if (e, k, self.axes[e].index(s)) in self.lit else self.b("tamno")
        fac.box(glass, s, z0, w, 0.03, h, -0.2, jit=False)
        # Kastenfenster: krst (stub + precka na 2/3)
        fac.box(ok, s, z0, 0.07, 0.06, h, -0.17)
        fac.box(ok, s, z0 + h * 0.68, w, 0.06, 0.07, -0.17)
        for sg in (-1, 1):
            fac.box(ok, s + sg * (w / 2 - 0.035), z0, 0.07, 0.06, h, -0.17)
        fac.box(ok, s, z0, w, 0.06, 0.07, -0.17)
        fac.box(ok, s, z0 + h - 0.07, w, 0.06, 0.07, -0.17)
        fw = 0.15                                    # sambrana (Fasche)
        for sg in (-1, 1):
            fac.box(st, s + sg * (w / 2 + fw / 2), z0 - fw, fw, 0.08, h + 2 * fw, 0.04)
        fac.box(st, s, z0 + h, w + 2 * fw, 0.08, fw, 0.04)
        if not balkon:
            fac.box(st, s, z0 - fw, w + 2 * fw, 0.08, fw, 0.04)
            fac.box(st, s, z0 - fw - 0.08, w + 0.45, 0.2, 0.09, 0.1)          # klupica
        top = z0 + h + fw
        tip = self.nad[min(k, len(self.nad) - 1)]
        if tip == "zabat":       # trouglasti zabat na konzolicama
            fac.box(st, s, top + 0.05, w + 0.6, 0.2, 0.12, 0.1)
            for sg in (-1, 1):
                fac.box(st, s + sg * (w / 2 + 0.2), top - 0.3, 0.12, 0.16, 0.36, 0.08)
            hw = (w + 0.6) / 2
            fac.extrude(st, s, top + 0.17, [(-hw, 0), (hw, 0), (0, 0.42)], 0.0, 0.18)
            if not balkon:       # parapetno polje ispod prozora
                fac.box(st, s, z0 - 0.75, w * 0.8, 0.05, 0.45, 0.02)
        elif tip == "luk":       # segmentni luk sa kljucnim kamenom
            hw = (w + 0.5) / 2
            arc = [(-hw * math.cos(math.pi * i / 10), 0.05 + 0.3 * math.sin(math.pi * i / 10)) for i in range(11)]
            fac.extrude(st, s, top - 0.02, [(-hw, 0.0)] + arc + [(hw, 0.0)], 0.0, 0.15)
            fac.box(st, s, top + 0.02, 0.2, 0.2, 0.38, 0.1)
            if not balkon:
                fac.box(st, s, z0 - 0.7, w * 0.8, 0.05, 0.4, 0.02)
        elif tip == "ravna":     # ravna nadprozornica sa frizom
            fac.box(st, s, top, w + 0.3, 0.05, 0.22, 0.03)
            fac.box(st, s, top + 0.22, w + 0.5, 0.2, 0.11, 0.1)
        elif tip == "venac":
            fac.box(st, s, top + 0.02, w + 0.4, 0.16, 0.1, 0.08)
        else:                    # "kamen": samo kljucni kamen
            fac.box(st, s, z0 + h - 0.05, 0.22, 0.12, 0.3, 0.06)

    def prozori(self):
        for e, ax in self.axes.items():
            for k in range(self.nf):
                for s in ax:
                    self.prozor(e, s, k)

    # --- krovovi
    def krov_mansarda(self):
        """Mansarda sa krovnim prozorima; na uglu jos i balkon i kupola (Eckkuppel)."""
        F, R0 = self.foot, self.R0
        kr, kf = self.b("krov"), self.b("krovfas")
        m_low = offset_poly(F, self.offs(0.25, back=-0.05))
        m_mid = offset_poly(F, [-1.3] * len(F))
        m_top = offset_poly(F, [-2.9] * len(F))
        frustum(kr, m_low, R0, m_mid, R0 + 3.0)
        frustum(kr, m_mid, R0 + 3.0, m_top, R0 + 3.7)
        prism(self.b("metal"), offset_poly(F, [-1.25] * len(F)), R0 + 2.98, R0 + 3.06)   # limeni opsav
        for e, ax in self.axes.items():
            if e == self.chamfer:
                continue
            fac = self.fac[e]
            for s in ax:
                if self.ugao and e == (self.chamfer - 1) % len(F) and s > fac.L - 2.0:
                    continue           # kupola je blizu ugla
                z = R0 + 0.35
                fac.box(kf, s, z, 1.25, 1.8, 1.55, -0.65)
                fac.box(self.b("cut_up"), s, z + 0.25, 0.8, 0.5, 1.05, 0.12, jit=False)
                fac.box(self.b("tamno"), s, z + 0.25, 0.8, 0.02, 1.05, 0.05, jit=False)
                fac.box(self.b("okvir"), s, z + 0.25, 0.06, 0.05, 1.05, 0.07)
                fac.box(self.b("stuko"), s, z + 1.5, 1.45, 0.25, 0.1, 0.3)
                fac.extrude(kr, s, z + 1.55, [(-0.78, 0), (0.78, 0), (0, 0.62)], 0.3, -1.6)
        if self.ugao:
            self.kupola()

    def kupola(self):
        FC, R0 = self.fac[self.chamfer], self.R0
        st, kr, kf, tm = self.b("stuko"), self.b("krov"), self.b("krovfas"), self.b("tamno")
        c = FC.pt(FC.L / 2, -1.9, 0)
        cx, cy = c.x, c.y
        KU = 1.6   # kupola mora da izadje iznad mansarde
        lathe(kf, (cx, cy, R0 - 0.2), [(0.0, 0), (1.75, 0), (1.75, 2.4 + KU), (0.0, 2.4 + KU)], seg=8, rot=math.pi / 8)
        lathe(st, (cx, cy, R0 + 2.2 + KU), [(0.0, 0), (1.95, 0), (1.95, 0.18), (0.0, 0.18)], seg=8, rot=math.pi / 8)
        lathe(kr, (cx, cy, R0 + 2.38 + KU), [(0.0, 0), (1.85, 0), (1.8, 0.4), (1.55, 1.1), (1.0, 1.7),
                                            (0.45, 2.0), (0.0, 2.05)], seg=16)
        lathe(self.b("metal"), (cx, cy, R0 + 4.35 + KU), [(0.0, 0), (0.25, 0), (0.25, 0.5), (0.32, 0.55),
                                                          (0.06, 0.95), (0.05, 1.5), (0.0, 1.6)], seg=8)
        for i in range(0, 8, 2):   # tamni okulus na svakoj drugoj strani tambura
            a = math.pi / 4 + 2 * math.pi * i / 8
            ang = a + math.pi / 2
            wbox(tm, (cx + math.cos(a) * 1.62, cy + math.sin(a) * 1.62, R0 + 1.05 + KU), (0.55, 0.3, 1.0), ang, jit=False)
            wbox(st, (cx + math.cos(a) * 1.76, cy + math.sin(a) * 1.76, R0 + 1.6 + KU), (0.75, 0.1, 0.12), ang)
        # balkon na uglu (prvi sprat)
        zb = self.gf
        FC.box(st, FC.L / 2, zb + 0.72, 2.6, 0.95, 0.2, 0.47)
        for sg in (-0.8, 0.8):
            FC.box(st, FC.L / 2 + sg, zb + 0.3, 0.2, 0.75, 0.42, 0.37)
        for i in range(11):
            u = -1.15 + i * 0.23
            lathe(st, FC.pt(FC.L / 2 + u, 0.82, 0), [(0.0, zb + 0.92), (0.05, zb + 0.92), (0.07, zb + 1.1),
                                                     (0.04, zb + 1.35), (0.05, zb + 1.6), (0.0, zb + 1.6)], seg=8)
        FC.box(st, FC.L / 2, zb + 1.6, 2.5, 0.16, 0.1, 0.83)
        for sg in (-1.2, 1.2):
            FC.box(st, FC.L / 2 + sg, zb + 0.92, 0.14, 0.14, 0.7, 0.82)

    def krov_sattel(self, mansarde=(), dimnjaci=(0.3, 0.75)):
        """Dvovodni krov, sleme paralelno sa ulicom (ivica 0). Bocni zidovi dobijaju kalkan (zabat)."""
        f, d, R0 = self.fac[0], self.fac[1].L, self.R0
        rh = d / 2 * 0.6
        L = f.L
        # kalkan u boji fasade: vidi se gde je sused nizi
        self.fac[0].extrude_s(self.b("kalkan" if FOTO else "krovfas"), 0.02, L - 0.02,
                              [(0.0, self.top), (0.0, R0 - 0.05), (-d / 2, R0 + rh - 0.1),
                               (-d, R0 - 0.05), (-d, self.top)])
        kr = self.b("krov")
        t = 0.24
        for o_e, o_r in ((0.48, -d / 2), (-d - 0.3, -d / 2)):     # prednja i zadnja ploca
            z_e = R0 - 0.08
            f.extrude_s(kr, 0.0, L, [(o_e, z_e), (o_r, R0 + rh + 0.1), (o_r, R0 + rh + 0.1 - t), (o_e, z_e - t)])
        f.extrude_s(self.b("metal"), 0.0, L, [(-d / 2 + 0.12, R0 + rh + 0.06), (-d / 2 - 0.12, R0 + rh + 0.06),
                                              (-d / 2, R0 + rh + 0.2)])               # slemenjak
        for s in mansarde:                               # krovni prozori na prednjoj ploci
            dz = R0 + 0.2
            f.box(self.b("krovfas"), s, dz, 1.2, 2.0, 1.75, -1.7)
            f.box(self.b("cut_up"), s, dz + 0.75, 0.75, 0.5, 0.85, -0.7, jit=False)
            f.box(self.b("tamno"), s, dz + 0.75, 0.75, 0.02, 0.85, -0.85, jit=False)
            f.box(self.b("okvir"), s, dz + 0.75, 0.06, 0.05, 0.85, -0.83)
            f.extrude(kr, s, dz + 1.72, [(-0.75, 0), (0.75, 0), (0, 0.55)], -0.55, -2.9)
        tops = []
        for u in dimnjaci:
            p = f.pt(L * u, -d / 2 - 0.5, 0)
            z1 = R0 + rh + 1.3
            wbox(self.b("dimnjak"), (p.x, p.y, (R0 + rh - 1.0 + z1) / 2), (0.65, 0.95, z1 - (R0 + rh - 1.0)), f.ang)
            wbox(self.b("dimnjak"), (p.x, p.y, z1 + 0.07), (0.83, 1.13, 0.14), f.ang)
            lathe(self.b("dimnjak"), (p.x, p.y, z1 + 0.14), [(0.0, 0), (0.12, 0), (0.1, 0.32), (0.13, 0.4), (0.0, 0.4)], seg=10)
            tops.append(Vector((p.x, p.y, z1 + 0.55)))
        return tops

    def dimnjaci_mansarda(self, spots):
        R0, tops = self.R0, []
        for (x, y, sx, sy) in spots:
            wbox(self.b("dimnjak"), (x, y, R0 + 2.6), (sx, sy, 3.8))
            wbox(self.b("dimnjak"), (x, y, R0 + 4.55), (sx + 0.18, sy + 0.18, 0.14))
            for i in range(2 if max(sx, sy) > 1 else 1):
                off = (i - 0.5) * 0.55 if max(sx, sy) > 1 else 0
                px, py = (x + off, y) if sx > sy else (x, y + off)
                lathe(self.b("dimnjak"), (px, py, R0 + 4.62), [(0.0, 0), (0.12, 0), (0.1, 0.35), (0.13, 0.42), (0.0, 0.42)], seg=10)
                tops.append(Vector((px, py, R0 + 5.15)))
        return tops

    # --- prizemlje
    def izlog(self, e, s0, s1, kind="pekara", z0=0.6, h=3.1):
        """kind: "pekara" (topao, hleb na policama, svetlo), "roleta" (spusten Rollbalken), "tamno"."""
        fac, w, sc = self.fac[e], s1 - s0, (s0 + s1) / 2
        dr, cg = self.b("drvo"), self.b("cut_gf")
        zt = z0 + h + 0.12                                                   # dno table
        if kind == "roleta":
            fac.box(cg, sc, 0.12, w, 1.0, h + 0.5, 0.0, jit=False)
            fac.box(self.b("roleta"), sc, 0.12, w, 0.04, h + 0.5, -0.25, jit=False)
            fac.box(self.b("metal"), sc, 0.1, w + 0.1, 0.14, 0.08, -0.2)
            fac.box(self.b("tabla_zel"), sc, zt, w + 0.2, 0.1, 0.42, 0.05)
            fac.box(self.b("zlato"), sc, zt - 0.03, w + 0.32, 0.06, 0.04, 0.09)
            fac.box(self.b("zlato"), sc, zt + 0.42, w + 0.32, 0.06, 0.04, 0.09)
            return
        fac.box(cg, sc, z0, w, 3.0 if kind == "pekara" else 1.2, h, -1.4 + 0.1 if kind == "pekara" else -0.3, jit=False)
        if kind == "pekara":
            fac.box(self.b("zar"), sc, 0.0, w, 0.05, self.gf - 0.3, -2.7)    # topao zadnji zid
            fac.box(self.b("staklo"), sc, z0, w, 0.02, h, -0.12, jit=False)
        else:
            fac.box(self.b("tamno"), sc, z0, w, 0.03, h, -0.2, jit=False)
        for s in [s0 + 0.06, s1 - 0.06] + [s0 + w * t for t in (1 / 3, 2 / 3)]:
            fac.box(dr, s, z0, 0.12, 0.14, h, -0.08)
        fac.box(dr, sc, z0, w, 0.16, 0.14, -0.06)
        fac.box(dr, sc, z0 + h - 0.12, w, 0.14, 0.12, -0.08)
        fac.box(dr, sc, z0 + h - 0.62, w, 0.12, 0.08, -0.08)
        fac.box(dr, sc, z0 - 0.08, w + 0.2, 0.32, 0.1, 0.0)                 # klupica izloga
        table = "tabla" if kind == "pekara" else "tabla_zel"
        fac.box(self.b(table), sc, zt, w + 0.2, 0.1, 0.42, 0.05)             # lakirana tabla, bez natpisa
        for zz in (zt - 0.03, zt + 0.42):                                    # pozlacen rub
            fac.box(self.b("zlato"), sc, zz, w + 0.32, 0.06, 0.04, 0.09)
        for s in (s0 - 0.06, s1 + 0.06):
            fac.box(self.b("zlato"), s, zt - 0.03, 0.04, 0.06, 0.49, 0.09)
        if kind != "pekara":
            return
        # police iza stakla sa hlebovima (silueta na toplom zidu)
        for zz, depth_o in ((0.6, -0.55), (1.45, -1.6), (2.2, -1.9)):
            fac.box(dr, sc, zz, w - 0.3, 0.55 if zz < 1 else 0.4, 0.07, depth_o)
            n = int((w - 0.6) / 0.42)
            for i in range(n):
                s = s0 + 0.45 + i * (w - 0.9) / max(1, n - 1) + random.uniform(-0.05, 0.05)
                kind_h = random.random()
                size = (0.36, 0.24, 0.17) if kind_h < 0.4 else (0.17, 0.17, 0.11) if kind_h < 0.75 else (0.42, 0.15, 0.13)
                ellipsoid(self.b("hleb"), fac.pt(s, depth_o + random.uniform(-0.08, 0.08), zz + 0.07 + size[2] * 0.42),
                          size, fac.ang + random.uniform(-0.4, 0.4))
        # lampice na labudovom vratu osvetljavaju tablu
        n_l = max(2, int(w / 2.2))
        for i in range(n_l):
            s = s0 + w * (i + 0.5) / n_l
            fac.box(self.b("metal"), s, zt + 0.5, 0.03, 0.45, 0.03, 0.3)
            fac.box(self.b("lampica"), s, zt + 0.42, 0.14, 0.1, 0.06, 0.52, jit=False)
        add_light(f"{self.name}_tabla_{e}", "AREA", fac.pt(sc, 0.75, zt + 0.55), rot_dir=-fac.n + Vector((0, 0, -0.9)),
                  shape="RECTANGLE", size=w, size_y=0.15, energy=26 * w / 6.5, color=(1.0, 0.72, 0.42))
        # glavni topli izvor: area svetla u nisi izloga, gledaju napolje i nadole
        add_light(f"{self.name}_izlog_{e}", "AREA", fac.pt(sc, -0.35, 3.45), rot_dir=fac.n + Vector((0, 0, -0.55)),
                  shape="RECTANGLE", size=w - 0.3, size_y=0.4, energy=520 * w / 6.5, color=WARM)
        add_light(f"{self.name}_izlog_unutra_{e}", "AREA", fac.pt(sc, -0.9, 3.4), rot_dir=Vector((0, 0, -1)) - fac.n * 0.3,
                  shape="RECTANGLE", size=w - 0.4, size_y=0.8, energy=90 * w / 6.5, color=(1.0, 0.62, 0.32))

    def haustor(self, e, s, h=3.4):
        fac, dr = self.fac[e], self.b("drvo")
        fac.box(self.b("cut_gf"), s, 0.0, 1.6, 1.2, h, -0.3, jit=False)
        fac.box(dr, s, 0.0, 1.6, 0.1, h, -0.5)
        for sg in (-0.38, 0.38):
            for zz in (0.35, h * 0.56):
                fac.box(dr, s + sg, zz, 0.6, 0.06, h * 0.35, -0.43)
        for sg in (-1, 1):
            fac.box(self.b("stuko"), s + sg * 0.92, 0.5, 0.24, 0.12, h - 0.25, 0.06)
        fac.box(self.b("stuko"), s, h, 2.1, 0.18, 0.2, 0.09)

    def prozor_prizemlja(self, e, s, z=1.2, h=2.2):
        fac = self.fac[e]
        fac.box(self.b("cut_gf"), s, z, 1.1, 0.6, h, 0.0, jit=False)
        fac.box(self.b("tamno"), s, z, 1.1, 0.03, h, -0.2, jit=False)
        for i in range(5):
            fac.box(self.b("metal"), s - 0.44 + i * 0.22, z, 0.035, 0.035, h, -0.05)

    # --- zatvaranje
    def finish(self):
        for key, b in self.B.items():
            self.obj[key] = b.finish()
        for key in CUTTERS:
            if key in self.obj:
                self.obj[key].hide_render = True
                self.obj[key].display_type = "WIRE"
        for key, cut in (("fasada", "cut_up"), ("krovfas", "cut_up"), ("prizemlje", "cut_gf"), ("sokla", "cut_gf")):
            if key in self.obj and cut in self.obj:
                md = self.obj[key].modifiers.new("Rez", "BOOLEAN")
                md.operation = "DIFFERENCE"
                md.object = self.obj[cut]
                md.solver = "EXACT"
                self.obj[key].modifiers.move(len(self.obj[key].modifiers) - 1, 0)   # boolean pre bevel-a
        if "staklo" in self.obj:
            self.obj["staklo"].visible_shadow = False    # toplo svetlo izlazi na trotoar
        return self


def red_kuca(name, x0, y0, w, d, smer, boja, **kw):
    """Kuca u nizu, pravougaona. smer "A": fasada ka jugu, niz ide ka +x od x0.
    smer "B": fasada ka zapadu, niz ide ka +y od y0. Ivica 0 je uvek ulicna."""
    g = 0.02   # mali razmak od suseda, da se zidovi ne preklapaju
    if smer == "A":
        foot = [(x0 + g, 0.0), (x0 + w - g, 0.0), (x0 + w - g, d), (x0 + g, d)]
    else:
        foot = [(0.0, y0 + w - g), (0.0, y0 + g), (d, y0 + g), (d, y0 + w - g)]
    L = w - 2 * g
    n = max(2, int(round((L - 1.2) / 2.75)))
    ax = [0.6 + (L - 1.2) * (i + 0.5) / n for i in range(n)]
    return Kuca(name, foot, [0], {0: ax}, boja, **kw), ax


# ---------------------------------------------------------------- kvart
UG_C, UG_W, UG_D = 3.0, 14.0, 12.0          # zakosen ugao, sirina, dubina ugaone kuce
ug = Kuca("Ugao", [(UG_C, 0), (UG_W, 0), (UG_W, UG_D), (0, UG_D), (0, UG_C)], [0, 3, 4],
          {0: [1.5, 4.17, 6.83, 9.5], 4: [UG_C * math.sqrt(2) / 2], 3: [1.5, 4.5, 7.5]},
          "#dccaa2", nad=("zabat", "ravna", "venac", "kamen"), ugao=True, chamfer=4, krov="mansarda",
          lit={(0, 2, 3), (3, 1, 0)})
ug.masa()
ug.prozori()
ug.krov_mansarda()
dim_tops = ug.dimnjaci_mansarda([(9.0, 9.0, 0.7, 1.4), (12.2, 4.5, 1.2, 0.6), (4.5, 10.2, 1.2, 0.6), (7.2, 6.0, 0.6, 0.6)])
smoke_spots = [dim_tops[0]]
ug.izlog(0, 0.9, 7.45, "pekara")
ug.izlog(3, 4.0, 8.3, "pekara")
ug.haustor(0, 9.5)
ug.prozor_prizemlja(3, 1.5)

# vrata pekare na uglu (samo ova kuca)
FA, FB, FC = ug.fac[0], ug.fac[3], ug.fac[4]
dz = 2.95
FC.box(ug.b("cut_gf"), FC.L / 2, 0.12, 1.7, 2.6, dz + 0.55, -0.7, jit=False)
FC.box(ug.b("zar"), FC.L / 2, 0.0, 1.7, 0.05, ug.gf - 0.3, -1.9)
for sg in (-1, 1):
    FC.box(ug.b("drvo"), FC.L / 2 + sg * 0.68, 0.12, 0.14, 0.1, dz, -0.5)
FC.box(ug.b("drvo"), FC.L / 2, 0.12, 1.5, 0.1, 0.55, -0.5)
FC.box(ug.b("metal"), FC.L / 2 + 0.45, 1.2, 0.04, 0.12, 0.55, -0.42)               # kvaka
FC.box(ug.b("staklo"), FC.L / 2, 0.12, 1.2, 0.02, dz + 0.5, -0.45, jit=False)
FC.box(ug.b("staklo"), FC.L / 2, 0.75, 1.1, 0.1, dz - 1.1, -0.55, jit=False)
FC.box(ug.b("drvo"), FC.L / 2, dz + 0.12, 1.7, 0.14, 0.1, -0.5)
FC.box(ug.b("sokla"), FC.L / 2, 0.0, 2.0, 0.55, 0.12, 0.1)                       # prag
FC.box(ug.b("drvo"), FC.L / 2, 0.0, 1.6, 0.6, 1.0, -1.35)                         # pult iza vrata
for i in range(4):
    ellipsoid(ug.b("hleb"), FC.pt(FC.L / 2 - 0.55 + i * 0.36, -1.35, 1.08), (0.3, 0.2, 0.15), FC.ang + 0.2 * i)
FC.box(ug.b("tabla"), FC.L / 2, 3.83, FC.L - 0.5, 0.1, 0.42, 0.05)
for zz in (3.8, 4.25):
    FC.box(ug.b("zlato"), FC.L / 2, zz, FC.L - 0.38, 0.06, 0.04, 0.09)
add_light("Vrata", "AREA", FC.pt(FC.L / 2, -0.25, 3.0), rot_dir=FC.n + Vector((0, 0, -0.7)), shape="RECTANGLE",
          size=1.4, size_y=0.3, energy=260, color=WARM)
# viseca tabla (Nasenschild) blizu ugla na A: lakirana sa zlatnim ramom
FA.box(ug.b("metal"), 0.55, 4.0, 0.05, 1.1, 0.05, 0.55)
for sg in (0.2, 0.9):
    FA.box(ug.b("metal"), 0.55, 3.75, 0.02, 0.02, 0.25, sg)
FA.box(ug.b("tabla"), 0.55, 3.0, 0.07, 0.85, 0.75, 0.55)
FA.box(ug.b("zlato"), 0.55, 2.97, 0.05, 0.92, 0.82, 0.55)
# sanduci sa brasnom pored vrata
for (s, z, rot) in ((0.5, 0.0, 0.05), (0.55, 0.42, -0.12), (1.3, 0.0, 0.2)):
    p = FB.pt(FB.L - s - 0.2, 0.55, z)
    wbox(ug.b("sanduk"), (p.x, p.y, p.z + 0.2), (0.6, 0.45, 0.4), FB.ang + rot)
ug.finish()

# susedi: jednostavnije varijante istog kita, 3-4 sprata, topli becki tonovi
SUSEDI_A = [  # (ime, sirina, spratova, boja, nadprozornici, krov, prizemlje)
    ("A1", 9.0, 3, "#cf9f52", ("luk", "venac", "kamen"), CREP, [("roleta", 1.0, 5.2), ("haustor", 7.0)]),
    ("A2", 8.4, 4, "#d9aa9c", ("zabat", "luk", "venac", "kamen"), KROV, [("haustor", 1.6), ("tamno", 3.1, 7.6)]),
    ("A3", 7.0, 3, "#a29f98", ("ravna", "venac", "kamen"), KROV, [("prozor", 1.6), ("haustor", 4.6)]),
]
SUSEDI_B = [
    ("B1", 8.6, 3, "#a9a59a", ("ravna", "venac", "kamen"), KROV, [("prozor", 1.6), ("roleta", 3.4, 7.6)]),
    ("B2", 9.0, 4, "#d6b06c", ("luk", "zabat", "venac", "kamen"), CREP, [("tamno", 1.0, 5.4), ("haustor", 7.2)]),
    ("B3", 6.8, 3, "#cc9c8f", ("venac", "venac", "kamen"), KROV, [("haustor", 2.0), ("prozor", 4.8)]),
]
DEPTH = 11.0
kuce = [ug]
for smer, niz, start in (("A", SUSEDI_A, UG_W), ("B", SUSEDI_B, UG_D)):
    pos = start
    for i, (nm, w, nf, boja, nad, kb, gfspec) in enumerate(niz):
        gf = 4.1 if nf == 3 else 4.3
        fl = 3.25 if nf == 3 else 3.15
        h, ax = red_kuca(nm, pos, pos, w, DEPTH, smer, boja, gf=gf, fl=fl, nf=nf, nad=nad, krov_boja=kb)
        h.masa()
        h.prozori()
        tops = h.krov_sattel(mansarde=ax[::2] if nf == 4 else (), dimnjaci=(0.28, 0.76))
        if nm == "A2":
            smoke_spots.append(tops[1])
        for it in gfspec:
            if it[0] == "haustor":
                h.haustor(0, it[1], h=min(3.4, gf - 0.9))
            elif it[0] == "prozor":
                h.prozor_prizemlja(0, it[1])
            else:
                h.izlog(0, it[1], it[2], it[0], z0=0.5, h=gf - 1.65)
        h.finish()
        kuce.append(h)
        pos += w
X_END, Y_END = UG_W + sum(s[1] for s in SUSEDI_A), UG_D + sum(s[1] for s in SUSEDI_B)

# --- ulica, trotoar, daska, dvoriste
BX0, BY0, BX1, BY1 = -14.5, -14.5, X_END + 2.0, Y_END + 2.0
RUB = 1.3                                                    # vidljiv rub daske oko ulice
amb = {}


def ambijent(name, mat, bevel=0.03, seg=2):
    amb[name] = Builder(name, M[mat], bevel=bevel, seg=seg)
    return amb[name]


b_daska = ambijent("Daska_za_hleb", "daska", bevel=0.45, seg=6)
wbox(b_daska, ((BX0 + BX1) / 2, (BY0 + BY1) / 2, -0.95), (BX1 - BX0, BY1 - BY0, 1.1), jit=False)
b_kocka = ambijent("Ulica_kocka", "kocka", bevel=0.05)
wbox(b_kocka, ((BX0 + BX1) / 2, (BY0 + BY1) / 2, -0.32), (BX1 - BX0 - 2 * RUB, BY1 - BY0 - 2 * RUB, 0.16), jit=False)
BLOK = [(UG_C, 0), (X_END, 0), (X_END, Y_END), (0, Y_END), (0, UG_C)]
b_ivic = ambijent("Ivicnjak", "ivicnjak", bevel=0.05)
b_trot = ambijent("Trotoar", "trotoar", bevel=0.02)
ring(b_ivic, offset_poly(BLOK, [3.0, 0.0, 0.0, 3.0, 3.0]), -0.24, -0.02, offset_poly(BLOK, [2.5, -0.5, -0.5, 2.5, 2.5]))
prism(b_trot, offset_poly(BLOK, [2.75, -0.1, -0.1, 2.75, 2.75]), -0.24, 0.0)
# trotoari preko puta (ulica je 7 m)
FAR = -10.0
for (x0, y0, x1, y1) in ((FAR, BY0 + RUB, BX1 - RUB, FAR), (BX0 + RUB, BY0 + RUB, FAR, BY1 - RUB)):
    prism(b_trot, rect(x0, y0, x1, y1), -0.24, 0.0)
prism(b_ivic, rect(FAR - 0.01, BY0 + RUB, BX1 - RUB, FAR + 0.25), -0.24, -0.02)
prism(b_ivic, rect(BX0 + RUB, BY0 + RUB, FAR + 0.25, BY1 - RUB), -0.24, -0.02)
b_dv = ambijent("Dvoriste", "dvoriste", bevel=0.03)
prism(b_dv, rect(DEPTH - 0.2, DEPTH - 0.2, X_END - 0.05, Y_END - 0.05), 0.0, 0.07)
# drvece u dvoristu: sundjeraste krosnje kao na maketi
b_kr = ambijent("Krosnje", "krosnja", bevel=0)
b_st = ambijent("Stabla", "stablo", bevel=0)
for (tx, ty, r) in ((23.0, 20.5, 2.4), (29.5, 26.0, 2.0), (18.0, 27.5, 1.7)):
    lathe(b_st, (tx, ty, 0.0), [(0.0, 0), (0.22, 0), (0.16, 1.2), (0.12, 3.2 * r / 2), (0.0, 3.3 * r / 2)], seg=8)
    for i in range(6):
        a = i * 2.1
        c = (tx + math.cos(a) * r * 0.45, ty + math.sin(a) * r * 0.45, 2.9 * r / 2 + r * 0.55 + random.uniform(-0.3, 0.5))
        ellipsoid(b_kr, c, (r * random.uniform(0.95, 1.25),) * 2 + (r * 0.95,), seg=(12, 8))
# ulicne lampe (bledo hladne, slabe)
b_met = ambijent("Lampe_metal", "metal", bevel=0.01, seg=1)
b_lampa = ambijent("Lampa_svetlo", "lampa", bevel=0)
for (lx, ly, dx, dy) in ((20.0, -2.55, 0, -1), (-2.55, 21.5, -1, 0)):
    lathe(b_met, (lx, ly, 0.0), [(0.0, 0), (0.16, 0), (0.16, 0.3), (0.09, 0.45), (0.06, 1.5),
                                 (0.045, 4.6), (0.0, 4.65)], seg=10)
    hx, hy = lx + dx * 1.1, ly + dy * 1.1
    wbox(b_met, (lx + dx * 0.55, ly + dy * 0.55, 4.55), (0.06 + abs(dx) * 1.04, 0.06 + abs(dy) * 1.04, 0.06), jit=False)
    lathe(b_met, (hx, hy, 4.1), [(0.0, 0.42), (0.32, 0.25), (0.34, 0.2), (0.0, 0.2)], seg=12)
    lathe(b_lampa, (hx, hy, 4.1), [(0.0, 0.0), (0.18, 0.05), (0.28, 0.2), (0.0, 0.2)], seg=12)
    add_light(f"Lampa_{lx:.0f}_{ly:.0f}", "POINT", (hx, hy, 4.2), energy=35, color=(0.75, 0.85, 1.0), shadow_soft_size=0.15)

# test-tlo samo oko ugaone kuce (za bake/GLB); u renderu je skriveno
b_ttrot = ambijent("Test_trotoar", "trotoar", bevel=0.02)
b_tiv = ambijent("Test_ivicnjak", "ivicnjak", bevel=0.05)
b_tul = ambijent("Test_ulica", "kocka", bevel=0.05)
UGF = ug.foot
prism(b_ttrot, offset_poly(UGF, [2.75, -0.1, -0.1, 2.75, 2.75]), -0.24, 0.0)
ring(b_tiv, offset_poly(UGF, [3.0, 0.0, 0.0, 3.0, 3.0]), -0.24, -0.02, offset_poly(UGF, [2.5, -0.5, -0.5, 2.5, 2.5]))
prism(b_tul, rect(-9.0, -9.0, UG_W + 4.0, UG_D + 4.0), -0.4, -0.24)
for b in amb.values():
    amb[b.name] = b.finish()
TEST = ("Test_trotoar", "Test_ivicnjak", "Test_ulica")
for n in TEST:
    amb[n].hide_render = True


# --- dim iz dva dimnjaka: kugle sa volumenom, rastu i nose se vetrom
def dim(top, seed):
    rnd = random.Random(seed)
    for i in range(9):
        t = i / 8
        r = 0.45 + 1.35 * t
        c = top + Vector((2.6 * t ** 1.6 + rnd.uniform(-0.2, 0.2), 1.0 * t ** 1.3 + rnd.uniform(-0.2, 0.2), 0.2 + 6.0 * t))
        me = bpy.data.meshes.new(f"Dim_{seed}_{i}")
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(M["dim"])
        ob = bpy.data.objects.new(me.name, me)
        ob.location = c
        ob.scale = (r, r, r * 0.85)
        scene.collection.objects.link(ob)


for i, tp in enumerate(smoke_spots):
    dim(tp, 11 + i)

# ---------------------------------------------------------------- svetlo
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wn = world.node_tree
for nd in list(wn.nodes):
    if nd.type != "OUTPUT_WORLD":
        wn.nodes.remove(nd)
wout = [nd for nd in wn.nodes if nd.type == "OUTPUT_WORLD"][0]
tc = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
wn.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = hexc("#1c2639")    # horizont, pre zore
ramp.color_ramp.elements[1].position = 0.55
ramp.color_ramp.elements[1].color = hexc("#07090f")    # zenit
wn.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
bg_cam = wn.nodes.new("ShaderNodeBackground")          # ono sto kamera vidi: noc
wn.links.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
bg_cam.inputs["Strength"].default_value = 1.6
bg_amb = wn.nodes.new("ShaderNodeBackground")          # ono sto osvetljava maketu: toplija soba
bg_amb.inputs["Color"].default_value = hexc("#3d3633")
bg_amb.inputs["Strength"].default_value = float(os.environ.get("KRUME_AMB", "0.9"))
lp = wn.nodes.new("ShaderNodeLightPath")
mix = wn.nodes.new("ShaderNodeMixShader")
wn.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
wn.links.new(bg_amb.outputs["Background"], mix.inputs[1])
wn.links.new(bg_cam.outputs["Background"], mix.inputs[2])
wn.links.new(mix.outputs["Shader"], wout.inputs["Surface"])
if FOTO:
    # dan: fizicko nebo (Sky Texture) umesto ravne rampe; cvor "dan" (0 noc, 1 dan) ih pretapa.
    # Nocu (dan = 0) world je isti kao pre, pa kadrovi.py i dalje radi sa svojim cvorovima.
    # Sunce kao "Jutro_sunce" u kadrovi.py: nisko (~27 stepeni), s jugoistoka; disk crta sun lampa, ne nebo.
    sky = wn.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_disc = False
    sky.sun_elevation = math.radians(27)
    sky.sun_rotation = math.atan2(0.62, -0.52)
    sky.altitude = 200.0
    sky.air_density, sky.aerosol_density = 1.0, 1.6       # becka izmaglica
    bg_sky = wn.nodes.new("ShaderNodeBackground")
    bg_sky.name = bg_sky.label = "Nebo_dan"
    bg_sky.inputs["Strength"].default_value = 0.22
    wn.links.new(sky.outputs["Color"], bg_sky.inputs["Color"])
    dan_v = wn.nodes.new("ShaderNodeValue")
    dan_v.name = dan_v.label = "dan"
    dan_v.outputs[0].default_value = 0.0
    mix_dan = wn.nodes.new("ShaderNodeMixShader")
    wn.links.new(dan_v.outputs[0], mix_dan.inputs["Fac"])
    wn.links.new(mix.outputs["Shader"], mix_dan.inputs[1])
    wn.links.new(bg_sky.outputs["Background"], mix_dan.inputs[2])
    wn.links.new(mix_dan.outputs["Shader"], wout.inputs["Surface"])

    # krug 2: HDRI samo za svetlo i odsjaje (staklo, lim, mokra kocka), kamera i dalje vidi nase nebo.
    # Noc: cobblestone_street_night, polu-desaturisan i slab, dodaje se sobi (bg_amb) zajedno sa hladnim
    # "nebom" odozgo: polusenka dobija plav detalj, a izlog ostaje jedini topao i najsvetliji izvor.
    # Dan: konigsallee umesto Sky Texture za svetlo (Sky ostaje za kameru). KRUME_HDRI_ROT u stepenima.
    def hdri(fajl, jacina, ime, sat=1.0, klip=None):
        mp_ = wn.nodes.new("ShaderNodeMapping")
        mp_.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(float(os.environ.get("KRUME_HDRI_ROT", "0"))))
        wn.links.new(wn.nodes.new("ShaderNodeTexCoord").outputs["Generated"], mp_.inputs["Vector"])
        en = wn.nodes.new("ShaderNodeTexEnvironment")
        en.image = bpy.data.images.load(os.path.join(TEKSTURE, "hdri", fajl), check_existing=True)
        wn.links.new(mp_.outputs["Vector"], en.inputs["Vector"])
        izl = en.outputs["Color"]
        if klip:   # lampe u HDRI-ju (do ~29000) bi bacale tvrde senke: odsecene, u odsjaju ostaju svetle tacke
            vm = wn.nodes.new("ShaderNodeVectorMath")
            vm.operation = "MINIMUM"
            vm.inputs[1].default_value = (klip, klip, klip)
            wn.links.new(izl, vm.inputs[0])
            izl = vm.outputs["Vector"]
        bg = wn.nodes.new("ShaderNodeBackground")
        bg.name = bg.label = ime
        bg.inputs["Strength"].default_value = jacina
        if sat != 1.0:
            hs_ = wn.nodes.new("ShaderNodeHueSaturation")
            hs_.inputs["Saturation"].default_value = sat
            wn.links.new(izl, hs_.inputs["Color"])
            wn.links.new(hs_.outputs["Color"], bg.inputs["Color"])
        else:
            wn.links.new(izl, bg.inputs["Color"])
        return bg

    bg_hn = hdri("cobblestone_street_night_2k.hdr", float(os.environ.get("KRUME_HDRI", "0.1")), "HDRI_noc", sat=0.45, klip=20.0)
    bg_neb = wn.nodes.new("ShaderNodeBackground")
    bg_neb.name = bg_neb.label = "Nebo_amb"
    bg_neb.inputs["Color"].default_value = hexc("#4c6290")
    bg_neb.inputs["Strength"].default_value = float(os.environ.get("KRUME_NEBO", "0.25"))
    add_a = wn.nodes.new("ShaderNodeAddShader")
    add_b = wn.nodes.new("ShaderNodeAddShader")
    wn.links.new(bg_amb.outputs["Background"], add_a.inputs[0])
    wn.links.new(bg_hn.outputs["Background"], add_a.inputs[1])
    wn.links.new(add_a.outputs["Shader"], add_b.inputs[0])
    wn.links.new(bg_neb.outputs["Background"], add_b.inputs[1])
    wn.links.new(add_b.outputs["Shader"], mix.inputs[1])
    bg_hd = hdri("konigsallee_2k.hdr", float(os.environ.get("KRUME_HDRI_DAN", "0.3")), "HDRI_dan")
    mix_dk = wn.nodes.new("ShaderNodeMixShader")
    wn.links.new(lp.outputs["Is Camera Ray"], mix_dk.inputs["Fac"])
    wn.links.new(bg_hd.outputs["Background"], mix_dk.inputs[1])
    wn.links.new(bg_sky.outputs["Background"], mix_dk.inputs[2])
    wn.links.new(mix_dk.outputs["Shader"], mix_dan.inputs[2])

CX, CY = (BX0 + BX1) / 2, (BY0 + BY1) / 2
# topla "stona lampa" iznad makete, s juga: modeluje fasade ka kameri
add_light("Lampa_stola", "AREA", (CX + 18, CY - 55, 62), rot_dir=Vector((CX - 4, CY + 4, 0)) - Vector((CX + 18, CY - 55, 62)),
          shape="DISK", size=34, energy=float(os.environ.get("KRUME_FILL", "9000")), color=(1.0, 0.8, 0.6))
# slaba hladna "mesecina" sa severozapada, za oblik krovova
add_light("Pre_zore", "SUN", (0, 0, 40), rot_dir=(0.55, -0.4, -0.6), energy=0.22,
          color=(0.55, 0.68, 1.0), angle=math.radians(3))


# ---------------------------------------------------------------- kamere
def add_cam(name, loc, target, lens, fstop=None, focus=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 500
    ob = bpy.data.objects.new(name, cd)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(ob)
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    return ob


tgt3 = Vector((CX - 2.5, CY - 2.5, 6.5))
loc3 = tgt3 + Vector((-1.0, -1.15, 0.8)).normalized() * 98
cam3 = add_cam("Kadar3_maketa", loc3, tgt3, 50, fstop=0.035,
               focus=(Vector((2.0, 2.0, 5.0)) - loc3).length)   # fokus na pekaru, lazni tilt-shift
cam4 = add_cam("Kadar4_pesak", (-5.6, -8.4, 1.55), (4.0, 0.6, 4.4), 22)

# ---------------------------------------------------------------- render
scene.render.engine = "CYCLES"
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.resolution_percentage = int(os.environ.get("KRUME_RES", "100"))
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
cy.samples = int(os.environ.get("KRUME_SAMPLES", "192"))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.03
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 6
cy.transmission_bounces = 4
cy.volume_bounces = 1
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.sample_clamp_indirect = 8.0
if FOTO:
    # Cycles sekvenca: adaptivno 0,02, OIDN sa albedo + normal, fiksan seed (kadrovi se ne "pomeraju"),
    # bez kaustika, glossy filter, magla sa najvise 1 odbijanjem, persistent data za niz kadrova
    cy.samples = int(os.environ.get("KRUME_SAMPLES", "192"))
    cy.adaptive_threshold = 0.02
    cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.denoising_prefilter = "ACCURATE"
    cy.denoising_use_gpu = True
    cy.seed, cy.use_animated_seed = 7, False
    cy.sample_clamp_indirect = 10.0
    cy.blur_glossy = 1.0
    cy.volume_bounces = 1
    cy.volume_biased = True
    cy.volume_step_rate = 3.0
    scene.render.use_persistent_data = True
    scene.render.use_motion_blur = False
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
scene.view_settings.exposure = float(os.environ.get("KRUME_EXPOSURE", "0.0"))


# ---------------------------------------------------------------- bake + GLB
def tri_count(me):
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def inside_convex(p, poly, eps=0.05):
    k = len(poly)
    for i in range(k):
        a, c = poly[i], poly[(i + 1) % k]
        if (c[0] - a[0]) * (p.y - a[1]) - (c[1] - a[1]) * (p.x - a[0]) < eps * math.hypot(c[0] - a[0], c[1] - a[1]):
            return False
    return True


def skrivene(bm, foot):
    """Velike vodoravne povrsine unutar tlocrta koje nista ne vidi (poklopci masa) i dna na zemlji."""
    from mathutils.bvhtree import BVHTree
    bm.normal_update()
    tree = BVHTree.FromBMesh(bm)
    out = []
    for f in bm.faces:
        n, c = f.normal, f.calc_center_median()
        if n.z < -0.9 and c.z < 0.05:
            out.append(f)
            continue
        if abs(n.z) < 0.9 or f.calc_area() < 0.8:
            continue
        pts = [c] + [c.lerp(v.co, 0.7) for v in f.verts]
        if foot is not None and not all(inside_convex(p, foot) for p in pts):
            continue
        if all(tree.ray_cast(p + n * 0.02, n, 80.0)[0] is not None for p in pts):
            out.append(f)
    return out


def spoji(objs, name, dg, foot=None):
    """Kopija objekata sa primenjenim modifikatorima, spojena u jedan mesh (materijal po slotu)."""
    bm = bmesh.new()
    mats = []
    for ob in objs:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        me.transform(ob.matrix_world)
        n0 = len(bm.faces)
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        mi = len(mats)
        mats.append(ob.active_material)
        for f in bm.faces[n0:]:
            f.material_index = mi
        bpy.data.meshes.remove(me)
    dele = skrivene(bm, foot)
    bmesh.ops.delete(bm, geom=dele, context="FACES")
    print(f"{name}: obrisano skrivenih povrsina {len(dele)}")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def uv_atlas(ob):
    for o in scene.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    ob.data.uv_layers.new(name="Bake")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0015, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake_u(ob, size, fn):
    img = bpy.data.images.new(fn, size, size, float_buffer=True)
    mats = list(dict.fromkeys(ob.data.materials))      # isti materijal moze biti u vise slotova
    for m in mats:
        nt = m.node_tree
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = img
        nt.nodes.active = node
    for o in scene.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    t = time.time()
    bpy.ops.object.bake(type="COMBINED", margin=6, use_clear=True)
    dt = time.time() - t
    for m in mats:                    # cvor ostaje u materijalu samo za ovaj bake
        nt = m.node_tree
        nt.nodes.remove(nt.nodes.active)
    # AgX + look kao u renderu, upisano u sRGB PNG: u pregledacu se prikazuje bez tone mapping-a
    path = os.path.join(HERE, "bake", fn + ".png")
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    img.save_render(path, scene=scene)
    print(f"BAKE {fn} {size}px: {dt:.1f} s")
    return path


def bake_mat(name, path):
    m, nt, p = node_mat(name)
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = bpy.data.images.load(path)
    nt.links.new(tx.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 1.0
    return m


def bake_i_izvoz():
    os.makedirs(os.path.join(HERE, "bake"), exist_ok=True)
    keep_live = {ug.obj[k] for k in ("zar", "staklo") if k in ug.obj}      # ostaju kao zivi materijali
    house = [o for k, o in ug.obj.items() if k not in CUTTERS and o not in keep_live]
    ground = [amb[n] for n in TEST]
    for o in scene.objects:            # u bake sceni je samo ugaona kuca i test-tlo
        if o.type == "MESH" and o not in keep_live:
            o.hide_render = True
    for o in house:                    # za web: ivice samo zakosene, manje trouglova
        for md in o.modifiers:
            if md.type == "BEVEL":
                md.segments = 1
    dg = bpy.context.evaluated_depsgraph_get()
    t = time.time()
    kuca = spoji(house, "Kuca_bake", dg, foot=ug.foot)
    tlo = spoji(ground, "Tlo_bake", dg, foot=offset_poly(ug.foot, [2.6, -0.1, -0.1, 2.6, 2.6]))
    svetlo = spoji(list(keep_live - {ug.obj.get("staklo")}), "Izlog_svetlo", dg)
    svetlo.hide_render = True
    uv_atlas(kuca)
    uv_atlas(tlo)
    print(f"UV atlas: {time.time() - t:.1f} s")
    cy.samples = int(os.environ.get("KRUME_BAKE_SAMPLES", "384"))
    scene.render.bake.use_pass_direct = True
    scene.render.bake.use_pass_indirect = True
    scene.render.bake.use_pass_diffuse = True
    scene.render.bake.use_pass_emit = True
    scene.render.bake.use_pass_glossy = False
    scene.render.bake.use_pass_transmission = False
    p_k = bake_u(kuca, int(os.environ.get("KRUME_ATLAS", "2048")), "kuca_bake")
    p_t = bake_u(tlo, 1024, "tlo_bake")
    for ob, path in ((kuca, p_k), (tlo, p_t)):
        ob.data.materials.clear()
        ob.data.materials.append(bake_mat(ob.name + "_mat", path))
        for f in ob.data.polygons:
            f.material_index = 0
    em = mat_simple("Izlog_svetlo", "#000000", emit="#ffb36b", strength=2.4)
    svetlo.data.materials.clear()
    svetlo.data.materials.append(em)
    tris = {ob.name: tri_count(ob.data) for ob in (kuca, tlo, svetlo)}
    for o in scene.objects:
        o.select_set(o in (kuca, tlo, svetlo))
    out = os.path.join(HERE, "kuca-test.glb")
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_normals=False, export_texcoords=True,
                              export_image_format="JPEG", export_image_quality=88,
                              export_draco_mesh_compression_enable=False, export_cameras=False,
                              export_lights=False)
    print("TRIS", tris, "ukupno", sum(tris.values()))
    print(f"GLB {out}: {os.path.getsize(out) / 1024 / 1024:.2f} MB")


if BAKE:
    bake_i_izvoz()
else:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kuca_kit.blend"))
    if "norender" not in ARGS:
        shots = [("3", cam3, "kuca-proba-3.png"), ("4", cam4, "kuca-proba-4.png")]
        for tag, cam, fn in shots:
            if ARGS and tag not in ARGS:
                continue
            scene.camera = cam
            scene.render.filepath = os.path.join(HERE, os.environ.get("KRUME_PREFIX", "") + fn)
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print(f"RENDER {fn}: {time.time() - t:.1f} s")
