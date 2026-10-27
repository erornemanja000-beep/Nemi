# Krume, smer 3 "Ein Fenster brennt": probni render jedne ugaone kuce.
# Proceduralno, bez addon-a i bez preuzimanja. Pokretanje:
#   Blender -b -P kuca_proba.py              (gradi, cuva .blend, renderuje oba kadra)
#   Blender -b -P kuca_proba.py -- norender  (samo gradi i cuva .blend)
#   Blender -b -P kuca_proba.py -- 1         (samo kadar 1; "2" samo kadar 2)
# Jedinica je metar (kuca u pravoj velicini), "maketa" dolazi iz materijala,
# daske ispod i plitke dubinske ostrine kadra 1.

import bpy, bmesh, math, os, random, sys, time
from mathutils import Vector, Matrix, Quaternion, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
random.seed(7)


def hexc(h, a=1.0):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


# Paleta iz brief-a i smera 3
NOC, KAMEN, KROV = "#14110f", "#2b2a28", "#3b4048"
KORA, ZAR, TESTO, BRASNO = "#7a4a24", "#e8792b", "#eadbc4", "#f6f1e7"

# ---------------------------------------------------------------- scena
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for d in list(coll):
        coll.remove(d)
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


def mat_plaster(name, col, var=0.06, bump=0.12, rough=0.88):
    """Mat fasadna boja, kao gips/karton: blaga mrlja u boji i sitna neravnina."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.35
    nz.inputs["Detail"].default_value = 4
    nt.links.new(co, nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    c0 = hexc(col)
    ramp.color_ramp.elements[0].color = tuple(max(0, c * (1 - var)) for c in c0[:3]) + (1,)
    ramp.color_ramp.elements[1].color = tuple(min(1, c * (1 + var)) for c in c0[:3]) + (1,)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    fine = nt.nodes.new("ShaderNodeTexNoise")
    fine.inputs["Scale"].default_value = 9.0
    fine.inputs["Detail"].default_value = 8
    fine.inputs["Roughness"].default_value = 0.65
    nt.links.new(co, fine.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.02
    nt.links.new(fine.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    return m, nt, p, co, bp


def mat_rustika(name, col):
    """Prizemlje: plaster sa vodoravnim fugama (rustika) svakih 0.5 m."""
    m, nt, p, co, bp = mat_plaster(name, col, var=0.08, bump=0.1)
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 2.0
    nt.links.new(sep.outputs["Z"], mul.inputs[0])
    fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"
    nt.links.new(mul.outputs[0], fr.inputs[0])
    gr = nt.nodes.new("ShaderNodeMapRange")
    gr.inputs["From Min"].default_value = 0.0
    gr.inputs["From Max"].default_value = 0.07
    nt.links.new(fr.outputs[0], gr.inputs["Value"])
    bp2 = nt.nodes.new("ShaderNodeBump")
    bp2.inputs["Strength"].default_value = 0.6
    bp2.inputs["Distance"].default_value = 0.03
    nt.links.new(gr.outputs["Result"], bp2.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], bp2.inputs["Normal"])
    nt.links.new(bp2.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_brick(name, c1, c2, mortar, scale, bump=0.4, rough=0.9, rot=False):
    """Kocka na ulici, ploce trotoara, crep: Brick Texture u XY ravni."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Color1"].default_value = hexc(c1)
    br.inputs["Color2"].default_value = hexc(c2)
    br.inputs["Mortar"].default_value = hexc(mortar)
    br.inputs["Scale"].default_value = scale
    br.inputs["Mortar Size"].default_value = 0.025
    br.inputs["Brick Width"].default_value = 0.5
    br.inputs["Row Height"].default_value = 0.25
    br.offset = 0.5
    nt.links.new(co, br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = bump
    bp.inputs["Distance"].default_value = 0.03
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = rough
    return m


def mat_wood_board(name):
    """Daska za hleb: kora boja sa godovima (Wave) i sitnom mrljom."""
    m, nt, p = node_mat(name)
    co = coord(nt)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.08, 1.0, 1.0)
    nt.links.new(co, mp.inputs["Vector"])
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "BANDS"; wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 0.9
    wv.inputs["Distortion"].default_value = 6
    wv.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = hexc("#6e4220")
    ramp.color_ramp.elements[1].color = hexc("#a8743f")
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.15
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.6
    return m


def mat_simple(name, col, rough=0.7, metal=0.0, emit=None, strength=0.0):
    m, nt, p = node_mat(name)
    p.inputs["Base Color"].default_value = hexc(col)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
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


M = {
    "fasada": mat_plaster("fasada", "#b9ab92")[0],
    "stuko": mat_plaster("stuko", "#cfc3ab", var=0.04, bump=0.08)[0],
    "prizemlje": mat_rustika("prizemlje", "#8c8170"),
    "sokla": mat_plaster("sokla", "#55504a", var=0.1, bump=0.2)[0],
    "krov": mat_brick("krov", KROV, "#353a42", "#2a2e34", 1.4, bump=0.25, rough=0.75),
    "dimnjak": mat_plaster("dimnjak", "#8a7f70", var=0.1, bump=0.2)[0],
    "staklo_tamno": mat_simple("staklo_tamno", "#07090d", rough=0.12),
    "staklo_slabo": mat_simple("staklo_slabo", "#1a120c", rough=0.2, emit="#b8682a", strength=0.09),
    "okvir": mat_plaster("okvir", "#d9cfbd", var=0.03, bump=0.05, rough=0.6)[0],
    "drvo_radnja": mat_simple("drvo_radnja", "#3e2412", rough=0.55),
    "tabla": mat_plaster("tabla", "#5a3418", var=0.05, bump=0.05, rough=0.5)[0],
    "zar": mat_glow("zar", 1.8),
    "staklo": mat_glass("staklo"),
    "hleb": mat_plaster("hleb", KORA, var=0.25, bump=0.4, rough=0.55)[0],
    "kocka": mat_brick("kocka", "#34312d", "#46423c", "#141312", 3.2, bump=0.6),
    "trotoar": mat_brick("trotoar", "#4d4a46", "#55524d", "#2c2a28", 0.9, bump=0.3),
    "ivicnjak": mat_plaster("ivicnjak", "#6a6660", var=0.1, bump=0.2)[0],
    "daska": mat_wood_board("daska"),
    "metal": mat_simple("metal", "#1b221f", rough=0.45, metal=0.6),
    "lampa": mat_simple("lampa", "#cfd8e6", rough=0.3, emit="#bcd0f0", strength=2.0),
    "sanduk": mat_plaster("sanduk", "#6b4a2c", var=0.12, bump=0.2)[0],
}


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
            bv.segments = self.seg
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
        bm = b.bm
        r0 = [bm.verts.new(self.pt(s + u, o0, z + v)) for u, v in profile]
        r1 = [bm.verts.new(self.pt(s + u, o1, z + v)) for u, v in profile]
        k = len(profile)
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


def ellipsoid(b, center, size, rot=0.0):
    q = Quaternion((0, 0, 1), rot) @ jitter_q(4)
    bmesh.ops.create_uvsphere(b.bm, u_segments=14, v_segments=9, radius=0.5,
                              matrix=Matrix.LocRotScale(Vector(center), q, Vector(size)))


# ---------------------------------------------------------------- tlocrt
C = 3.0                                    # zakosen ugao (Eckabschrägung)
W, D = 14.0, 12.0
FOOT = [(C, 0), (W, 0), (W, D), (0, D), (0, C)]   # CCW
STREET = {0, 3, 4}                         # ivice ka ulici, 1 i 2 su kalkani


def offs(v, back=None):
    return [v if i in STREET else (min(v, -0.01) if back is None else back) for i in range(5)]


FA = Facade((C, 0), (W, 0))        # Fasada A, duza, ka jugu
FC = Facade((0, C), (C, 0))        # zakosen ugao
FB = Facade((0, D), (0, C))        # Fasada B, ka zapadu

GF = 4.5                            # visina prizemlja
FL = 3.4                            # visina sprata
NF = 4                              # spratova iznad prizemlja
TOP = GF + FL * NF                  # 18.1

axes = {"A": (FA, [1.5, 4.17, 6.83, 9.5]), "C": (FC, [FC.L / 2]), "B": (FB, [1.5, 4.5, 7.5])}

b_fasada = Builder("Fasada", M["fasada"], bevel=0.04)
b_krovfas = Builder("Fasada_krov", M["fasada"], bevel=0.03)
b_stuko = Builder("Stuko", M["stuko"], bevel=0.018)
b_okvir = Builder("Prozorski_okviri", M["okvir"], bevel=0.008, seg=1)
b_tamno = Builder("Staklo_tamno", M["staklo_tamno"], bevel=0)
b_slabo = Builder("Staklo_slabo_svetlo", M["staklo_slabo"], bevel=0)
b_cut_up = Builder("Rezac_spratovi", M["fasada"], bevel=0)
b_prizemlje = Builder("Prizemlje", M["prizemlje"], bevel=0.04)
b_sokla = Builder("Sokla", M["sokla"], bevel=0.03)
b_cut_gf = Builder("Rezac_prizemlje", M["fasada"], bevel=0)
b_krov = Builder("Mansarda", M["krov"], bevel=0.05)
b_dimnjak = Builder("Dimnjaci", M["dimnjak"], bevel=0.03)
b_metal = Builder("Metal", M["metal"], bevel=0.01, seg=1)
b_drvo = Builder("Drvo_radnje", M["drvo_radnja"], bevel=0.015)
b_tabla = Builder("Tabla", M["tabla"], bevel=0.03)
b_zar = Builder("Izlog_zid_zar", M["zar"], bevel=0)
b_staklo = Builder("Izlog_staklo", M["staklo"], bevel=0)
b_hleb = Builder("Hlebovi", M["hleb"], bevel=0, smooth=True)
b_sanduk = Builder("Sanduci", M["sanduk"], bevel=0.02)

# --- masa kuce
prism(b_fasada, FOOT, GF, TOP + 0.02)
prism(b_prizemlje, FOOT, 0.0, GF)
prism(b_sokla, offset_poly(FOOT, offs(0.06)), 0.0, 0.5)

# --- venci
prism(b_stuko, offset_poly(FOOT, offs(0.16)), GF - 0.22, GF + 0.02)       # venac prizemlja
prism(b_stuko, offset_poly(FOOT, offs(0.28)), GF + 0.02, GF + 0.2)
for k in range(1, NF):
    zb = GF + FL * k
    prism(b_stuko, offset_poly(FOOT, offs(0.07)), zb + 0.6, zb + 0.76)     # parapetni venac
prism(b_stuko, offset_poly(FOOT, offs(0.04)), TOP - 0.55, TOP - 0.05)      # friz
prism(b_stuko, offset_poly(FOOT, offs(0.14)), TOP - 0.05, TOP + 0.1)
prism(b_stuko, offset_poly(FOOT, offs(0.55)), TOP + 0.3, TOP + 0.52)       # krovni venac
frustum(b_stuko, offset_poly(FOOT, offs(0.2)), TOP + 0.1, offset_poly(FOOT, offs(0.55)), TOP + 0.3)
# zubci (dentili) i konzole ispod krovnog venca
for fac, ax in axes.values():
    n = int(fac.L / 0.34)
    for i in range(n):
        fac.box(b_stuko, 0.17 + i * fac.L / n, TOP + 0.1, 0.13, 0.2, 0.18, 0.26)
    for s in ax:
        for ds in (-0.85, 0.85):
            if 0.3 < s + ds < fac.L - 0.3:
                fac.box(b_stuko, s + ds, TOP - 0.6, 0.22, 0.4, 0.85, 0.22)

# --- prozori na spratovima
LIT = {("A", 2, 3), ("B", 1, 0)}   # samo dva jedva upaljena prozora


def window(key, fac, s, k):
    zb = GF + FL * k
    w = 1.15 if key != "C" else 1.25
    h = (2.3, 2.1, 2.0, 1.75)[k]
    z0 = zb + 0.85
    balkon = key == "C" and k == 0
    if balkon:                                   # balkonska vrata na uglu
        z0, h = zb + 0.95, 2.45
    fac.box(b_cut_up, s, z0, w, 0.6, h, 0.0, jit=False)
    glass = b_slabo if (key, k, axes[key][1].index(s)) in LIT else b_tamno
    fac.box(glass, s, z0, w, 0.03, h, -0.2, jit=False)
    # Kastenfenster: krst (stub + precka na 2/3)
    fac.box(b_okvir, s, z0, 0.07, 0.06, h, -0.17)
    fac.box(b_okvir, s, z0 + h * 0.68, w, 0.06, 0.07, -0.17)
    for e in (-1, 1):
        fac.box(b_okvir, s + e * (w / 2 - 0.035), z0, 0.07, 0.06, h, -0.17)
    fac.box(b_okvir, s, z0, w, 0.06, 0.07, -0.17)
    fac.box(b_okvir, s, z0 + h - 0.07, w, 0.06, 0.07, -0.17)
    # sambrana (Fasche)
    fw = 0.15
    for e in (-1, 1):
        fac.box(b_stuko, s + e * (w / 2 + fw / 2), z0 - fw, fw, 0.08, h + 2 * fw, 0.04)
    fac.box(b_stuko, s, z0 + h, w + 2 * fw, 0.08, fw, 0.04)
    if not balkon:
        fac.box(b_stuko, s, z0 - fw, w + 2 * fw, 0.08, fw, 0.04)
        fac.box(b_stuko, s, z0 - fw - 0.08, w + 0.45, 0.2, 0.09, 0.1)          # klupica
    top = z0 + h + fw
    if k == 0:   # piano nobile: trouglasti zabat na konzolicama
        fac.box(b_stuko, s, top + 0.05, w + 0.6, 0.2, 0.12, 0.1)
        for e in (-1, 1):
            fac.box(b_stuko, s + e * (w / 2 + 0.2), top - 0.3, 0.12, 0.16, 0.36, 0.08)
        hw = (w + 0.6) / 2
        fac.extrude(b_stuko, s, top + 0.17, [(-hw, 0), (hw, 0), (0, 0.42)], 0.0, 0.18)
        if not balkon:   # parapetno polje ispod prozora
            fac.box(b_stuko, s, z0 - 0.75, w * 0.8, 0.05, 0.45, 0.02)
    elif k == 1:  # ravna nadprozornica sa frizom
        fac.box(b_stuko, s, top, w + 0.3, 0.05, 0.22, 0.03)
        fac.box(b_stuko, s, top + 0.22, w + 0.5, 0.2, 0.11, 0.1)
    elif k == 2:
        fac.box(b_stuko, s, top + 0.02, w + 0.4, 0.16, 0.1, 0.08)
    else:         # potkrovni sprat: samo kljucni kamen
        fac.box(b_stuko, s, z0 + h - 0.05, 0.22, 0.12, 0.3, 0.06)


for key, (fac, ax) in axes.items():
    for k in range(NF):
        for s in ax:
            window(key, fac, s, k)

# vertikalne lizene na krajevima ulicnih fasada i oko ugla
for fac in (FA, FB, FC):
    for s in (0.18, fac.L - 0.18):
        fac.box(b_stuko, s, GF + 0.2, 0.36, 0.06, TOP - GF - 0.75, 0.03)

# balkon na uglu (prvi sprat)
zb = GF + FL * 0
FC.box(b_stuko, FC.L / 2, zb + 0.72, 2.6, 0.95, 0.2, 0.47)
for e in (-0.8, 0.8):
    FC.box(b_stuko, FC.L / 2 + e, zb + 0.3, 0.2, 0.75, 0.42, 0.37)
for i in range(11):
    u = -1.15 + i * 0.23
    lathe(b_stuko, FC.pt(FC.L / 2 + u, 0.82, 0), [(0.0, zb + 0.92), (0.05, zb + 0.92), (0.07, zb + 1.1),
                                                    (0.04, zb + 1.35), (0.05, zb + 1.6), (0.0, zb + 1.6)], seg=8)
FC.box(b_stuko, FC.L / 2, zb + 1.6, 2.5, 0.16, 0.1, 0.83)
for e in (-1.2, 1.2):
    FC.box(b_stuko, FC.L / 2 + e, zb + 0.92, 0.14, 0.14, 0.7, 0.4 + 0.42)

# --- mansarda, krovni prozori, dimnjaci, ugaona kupola
R0 = TOP + 0.52
m_low = offset_poly(FOOT, offs(0.25, back=-0.05))
m_mid = offset_poly(FOOT, [-1.3] * 5)
m_top = offset_poly(FOOT, [-2.9] * 5)
frustum(b_krov, m_low, R0, m_mid, R0 + 3.0)
frustum(b_krov, m_mid, R0 + 3.0, m_top, R0 + 3.7)
prism(b_metal, offset_poly(FOOT, [-1.25] * 5), R0 + 2.98, R0 + 3.06)        # limeni opsav

for key in ("A", "B"):
    fac, ax = axes[key]
    for s in ax:
        if key == "B" and s > 7:
            continue           # kupola je blizu ugla
        z = R0 + 0.35
        fac.box(b_krovfas, s, z, 1.25, 1.8, 1.55, -0.65)
        fac.box(b_cut_up, s, z + 0.25, 0.8, 0.5, 1.05, 0.12, jit=False)
        fac.box(b_tamno, s, z + 0.25, 0.8, 0.02, 1.05, 0.05, jit=False)
        fac.box(b_okvir, s, z + 0.25, 0.06, 0.05, 1.05, 0.07)
        fac.box(b_stuko, s, z + 1.5, 1.45, 0.25, 0.1, 0.3)
        fac.extrude(b_krov, s, z + 1.55, [(-0.78, 0), (0.78, 0), (0, 0.62)], 0.3, -1.6)

for (x, y, sx, sy) in [(9.0, 9.0, 0.7, 1.4), (12.2, 4.5, 1.2, 0.6), (4.5, 10.2, 1.2, 0.6), (7.2, 6.0, 0.6, 0.6)]:
    wbox(b_dimnjak, (x, y, R0 + 2.6), (sx, sy, 3.8))
    wbox(b_dimnjak, (x, y, R0 + 4.55), (sx + 0.18, sy + 0.18, 0.14))
    for i in range(2 if max(sx, sy) > 1 else 1):
        off = (i - 0.5) * 0.55 if max(sx, sy) > 1 else 0
        px, py = (x + off, y) if sx > sy else (x, y + off)
        lathe(b_dimnjak, (px, py, R0 + 4.62), [(0.0, 0), (0.12, 0), (0.1, 0.35), (0.13, 0.42), (0.0, 0.42)], seg=10)

# kupola nad uglom (Eckkuppel): osmougaoni tambur, zvono, lanterna, vrh
cx, cy = 2.75, 2.75
KU = 1.6   # kupola mora da izadje iznad mansarde
lathe(b_krovfas, (cx, cy, R0 - 0.2), [(0.0, 0), (1.75, 0), (1.75, 2.4 + KU), (0.0, 2.4 + KU)], seg=8, rot=math.pi / 8)
lathe(b_stuko, (cx, cy, R0 + 2.2 + KU), [(0.0, 0), (1.95, 0), (1.95, 0.18), (0.0, 0.18)], seg=8, rot=math.pi / 8)
lathe(b_krov, (cx, cy, R0 + 2.38 + KU), [(0.0, 0), (1.85, 0), (1.8, 0.4), (1.55, 1.1), (1.0, 1.7),
                                    (0.45, 2.0), (0.0, 2.05)], seg=16)
lathe(b_metal, (cx, cy, R0 + 4.35 + KU), [(0.0, 0), (0.25, 0), (0.25, 0.5), (0.32, 0.55), (0.06, 0.95),
                                     (0.05, 1.5), (0.0, 1.6)], seg=8)
for i in range(8):
    a = math.pi / 8 + 2 * math.pi * i / 8 + math.pi / 8
    r = 1.62
    ang = a + math.pi / 2
    # tamni okulus na svakoj drugoj strani
    if i % 2 == 0:
        wbox(b_tamno, (cx + math.cos(a) * r, cy + math.sin(a) * r, R0 + 1.05 + KU), (0.55, 0.3, 1.0), ang, jit=False)
        wbox(b_stuko, (cx + math.cos(a) * 1.76, cy + math.sin(a) * 1.76, R0 + 1.6 + KU), (0.75, 0.1, 0.12), ang)

# --- prizemlje: izlog pekare, vrata na uglu, kucna vrata, tabla
SHOP = [("A", FA, 0.9, 7.45), ("B", FB, 4.0, 8.3)]
for key, fac, s0, s1 in SHOP:
    w = s1 - s0
    sc = (s0 + s1) / 2
    z0, h = 0.6, 3.1
    fac.box(b_cut_gf, sc, z0, w, 3.0, h, -1.4 + 0.1, jit=False)          # duboka nisa izloga
    fac.box(b_zar, sc, 0.0, w, 0.05, GF - 0.3, -2.7)                      # topao zadnji zid
    fac.box(b_staklo, sc, z0, w, 0.02, h, -0.12, jit=False)
    # drveni ram, stubici, precka sa nadsvetlom
    for s in [s0 + 0.06, s1 - 0.06] + [s0 + w * t for t in (1 / 3, 2 / 3)]:
        fac.box(b_drvo, s, z0, 0.12, 0.14, h, -0.08)
    fac.box(b_drvo, sc, z0, w, 0.16, 0.14, -0.06)
    fac.box(b_drvo, sc, z0 + h - 0.12, w, 0.14, 0.12, -0.08)
    fac.box(b_drvo, sc, z0 + h - 0.62, w, 0.12, 0.08, -0.08)
    fac.box(b_drvo, sc, z0 - 0.08, w + 0.2, 0.32, 0.1, 0.0)              # klupica izloga
    # police iza stakla sa hlebovima (silueta na toplom zidu)
    for zz, depth_o in ((0.6, -0.55), (1.45, -1.6), (2.2, -1.9)):
        fac.box(b_drvo, sc, zz, w - 0.3, 0.55 if zz < 1 else 0.4, 0.07, depth_o)
        n = int((w - 0.6) / 0.42)
        for i in range(n):
            s = s0 + 0.45 + i * (w - 0.9) / max(1, n - 1) + random.uniform(-0.05, 0.05)
            kind = random.random()
            if kind < 0.4:   # vekna
                size = (0.36, 0.24, 0.17)
            elif kind < 0.75:  # zemicka
                size = (0.17, 0.17, 0.11)
            else:            # dugi vekn
                size = (0.42, 0.15, 0.13)
            ellipsoid(b_hleb, fac.pt(s, depth_o + random.uniform(-0.08, 0.08), zz + 0.07 + size[2] * 0.42),
                      size, fac.ang + random.uniform(-0.4, 0.4))
    # natpisna tabla bez brenda iznad izloga
    fac.box(b_tabla, sc, 3.85, w + 0.2, 0.1, 0.42, 0.05)
    fac.box(b_okvir, sc, 3.82, w + 0.32, 0.06, 0.04, 0.09)
    fac.box(b_okvir, sc, 4.27, w + 0.32, 0.06, 0.04, 0.09)

# vrata pekare na uglu
dz = 2.95
FC.box(b_cut_gf, FC.L / 2, 0.12, 1.7, 2.6, dz + 0.55, -0.7, jit=False)
FC.box(b_zar, FC.L / 2, 0.0, 1.7, 0.05, GF - 0.3, -1.9)
for e in (-1, 1):                                                         # ram staklenih vrata
    FC.box(b_drvo, FC.L / 2 + e * 0.68, 0.12, 0.14, 0.1, dz, -0.5)
FC.box(b_drvo, FC.L / 2, 0.12, 1.5, 0.1, 0.55, -0.5)
FC.box(b_metal, FC.L / 2 + 0.45, 1.2, 0.04, 0.12, 0.55, -0.42)               # kvaka
FC.box(b_staklo, FC.L / 2, 0.12, 1.2, 0.02, dz + 0.5, -0.45, jit=False)
FC.box(b_staklo, FC.L / 2, 0.75, 1.1, 0.1, dz - 1.1, -0.55, jit=False)
FC.box(b_drvo, FC.L / 2, dz + 0.12, 1.7, 0.14, 0.1, -0.5)
FC.box(b_sokla, FC.L / 2, 0.0, 2.0, 0.55, 0.12, 0.1)                     # prag
FC.box(b_drvo, FC.L / 2, 0.0, 1.6, 0.6, 1.0, -1.35)                        # pult iza vrata
for i in range(4):
    ellipsoid(b_hleb, FC.pt(FC.L / 2 - 0.55 + i * 0.36, -1.35, 1.08), (0.3, 0.2, 0.15), FC.ang + 0.2 * i)
FC.box(b_tabla, FC.L / 2, 3.85, FC.L - 0.5, 0.1, 0.42, 0.05)

# kucna vrata (Haustor) na fasadi A
FA.box(b_cut_gf, 9.5, 0.0, 1.6, 1.2, 3.4, -0.3, jit=False)
FA.box(b_drvo, 9.5, 0.0, 1.6, 0.1, 3.4, -0.5)
for e in (-0.38, 0.38):
    for zz in (0.35, 1.9):
        FA.box(b_drvo, 9.5 + e, zz, 0.6, 0.06, 1.2, -0.43)
for e in (-1, 1):
    FA.box(b_stuko, 9.5 + e * 0.92, 0.5, 0.24, 0.12, 3.15, 0.06)
FA.box(b_stuko, 9.5, 3.4, 2.1, 0.18, 0.2, 0.09)
# mali tamni prozor prizemlja na B
FB.box(b_cut_gf, 1.5, 1.2, 1.1, 0.6, 2.2, 0.0, jit=False)
FB.box(b_tamno, 1.5, 1.2, 1.1, 0.03, 2.2, -0.2, jit=False)
for i in range(5):
    FB.box(b_metal, 1.5 - 0.44 + i * 0.22, 1.2, 0.035, 0.035, 2.2, -0.05)

# viseca tabla bez natpisa (Nasenschild) blizu ugla na A
FA.box(b_metal, 0.55, 4.0, 0.05, 1.1, 0.05, 0.55)
for e in (0.2, 0.9):
    FA.box(b_metal, 0.55, 3.75, 0.02, 0.02, 0.25, e)
FA.box(b_tabla, 0.55, 3.0, 0.07, 0.85, 0.75, 0.55)
FA.box(b_okvir, 0.55, 2.97, 0.05, 0.92, 0.82, 0.55)

# sanduci sa brasnom pored vrata
for (s, z, rot) in ((0.5, 0.0, 0.05), (0.55, 0.42, -0.12), (1.3, 0.0, 0.2)):
    p = FB.pt(FB.L - s - 0.2, 0.55, z)
    wbox(b_sanduk, (p.x, p.y, p.z + 0.2), (0.6, 0.45, 0.4), FB.ang + rot)

# --- ulica, trotoar, daska
BX0, BX1, BY0, BY1 = -10.0, 18.5, -10.0, 15.5
b_daska = Builder("Daska_za_hleb", M["daska"], bevel=0.35, seg=5)
wbox(b_daska, ((BX0 + BX1) / 2, (BY0 + BY1) / 2, -0.95), (BX1 - BX0, BY1 - BY0, 1.1), jit=False)
b_kocka = Builder("Ulica_kocka", M["kocka"], bevel=0.05)
wbox(b_kocka, ((BX0 + BX1) / 2, (BY0 + BY1) / 2, -0.32), (BX1 - BX0 - 2.6, BY1 - BY0 - 2.6, 0.16), jit=False)
b_trot = Builder("Trotoar", M["trotoar"], bevel=0.02)
b_ivic = Builder("Ivicnjak", M["ivicnjak"], bevel=0.04)
side = offset_poly(FOOT, [3.0, 0.0, 0.0, 3.0, 3.0])
prism(b_ivic, side, -0.24, -0.02)
prism(b_trot, offset_poly(FOOT, [2.75, -0.1, -0.1, 2.75, 2.75]), -0.24, 0.0)

# ulicna lampa (bledo hladna, slaba), dalje niz fasadu A
lx, ly = 13.0, -2.55
lathe(b_metal, (lx, ly, 0.0), [(0.0, 0), (0.16, 0), (0.16, 0.3), (0.09, 0.45), (0.06, 1.5),
                               (0.045, 4.6), (0.0, 4.65)], seg=10)
wbox(b_metal, (lx, ly - 0.55, 4.55), (0.06, 1.1, 0.06), jit=False)
b_lampa = Builder("Lampa_svetlo", M["lampa"], bevel=0)
lathe(b_metal, (lx, ly - 1.1, 4.1), [(0.0, 0.42), (0.32, 0.25), (0.34, 0.2), (0.0, 0.2)], seg=12)
lathe(b_lampa, (lx, ly - 1.1, 4.1), [(0.0, 0.0), (0.18, 0.05), (0.28, 0.2), (0.0, 0.2)], seg=12)

# --- zatvaranje, booleani
objs = {}
for b in (b_fasada, b_krovfas, b_stuko, b_okvir, b_tamno, b_slabo, b_prizemlje, b_sokla, b_krov, b_dimnjak,
          b_metal, b_drvo, b_tabla, b_zar, b_staklo, b_hleb, b_sanduk, b_daska, b_kocka, b_trot,
          b_ivic, b_lampa):
    objs[b.name] = b.finish()
cut_up = b_cut_up.finish()
cut_gf = b_cut_gf.finish()
for cut in (cut_up, cut_gf):
    cut.hide_render = True
    cut.display_type = "WIRE"


def add_bool(ob, cutter):
    md = ob.modifiers.new("Rez", "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.object = cutter
    md.solver = "EXACT"
    # boolean pre bevel-a
    ob.modifiers.move(len(ob.modifiers) - 1, 0)


add_bool(objs["Fasada"], cut_up)
add_bool(objs["Prizemlje"], cut_gf)
add_bool(objs["Sokla"], cut_gf)
add_bool(objs["Fasada_krov"], cut_up)

# staklo izloga ne baca senku, da toplo svetlo izadje na trotoar
objs["Izlog_staklo"].visible_shadow = False

# ---------------------------------------------------------------- svetlo
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wn = world.node_tree
bg = wn.nodes["Background"]
tc = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
wn.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = hexc("#1c2639")    # horizont, pre zore
ramp.color_ramp.elements[1].position = 0.55
ramp.color_ramp.elements[1].color = hexc("#07090f")    # zenit
wn.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.6


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
# glavni (jedini topli) izvor: area svetla u nisi izloga, gledaju napolje i nadole
for key, fac, s0, s1 in SHOP:
    w = s1 - s0
    c = fac.pt((s0 + s1) / 2, -0.35, 3.45)
    add_light("Izlog_" + key, "AREA", c, rot_dir=fac.n + Vector((0, 0, -0.55)), shape="RECTANGLE",
              size=w - 0.3, size_y=0.4, energy=520 * w / 6.5, color=WARM)
    c2 = fac.pt((s0 + s1) / 2, -0.9, 3.4)
    add_light("Izlog_unutra_" + key, "AREA", c2, rot_dir=Vector((0, 0, -1)) - fac.n * 0.3, shape="RECTANGLE",
              size=w - 0.4, size_y=0.8, energy=90 * w / 6.5, color=(1.0, 0.62, 0.32))
add_light("Vrata", "AREA", FC.pt(FC.L / 2, -0.25, 3.0), rot_dir=FC.n + Vector((0, 0, -0.7)), shape="RECTANGLE",
          size=1.4, size_y=0.3, energy=260, color=WARM)
# slaba hladna "mesecina" samo za oblik krovova
add_light("Pre_zore", "SUN", (0, 0, 40), rot_dir=(0.55, 0.9, -0.55), energy=0.16,
          color=(0.55, 0.68, 1.0), angle=math.radians(3))
add_light("Lampa", "POINT", (lx, ly - 1.1, 4.2), energy=35, color=(0.75, 0.85, 1.0), shadow_soft_size=0.15)

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


tgt1 = Vector((4.2, 3.2, 9.0))
loc1 = tgt1 + Vector((-1.0, -1.15, 1.2)).normalized() * 105
cam1 = add_cam("Kadar1_maketa", loc1, tgt1, 70, fstop=0.03,
               focus=(Vector((1.5, 1.5, 4.0)) - loc1).length)   # fokus na izlog, lazni tilt-shift
cam2 = add_cam("Kadar2_pesak", (-5.2, -8.2, 1.55), (3.6, 0.3, 4.2), 22)

# ---------------------------------------------------------------- render
scene.render.engine = "CYCLES"
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.resolution_percentage = 100
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
cy.samples = int(os.environ.get("KRUME_SAMPLES", "160"))
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.03
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 6
cy.transmission_bounces = 4
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.sample_clamp_indirect = 8.0
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
scene.view_settings.exposure = float(os.environ.get("KRUME_EXPOSURE", "0.0"))

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kuca_proba.blend"))

if "norender" not in ARGS:
    shots = [("1", cam1, "kuca-proba-1.png"), ("2", cam2, "kuca-proba-2.png")]
    for tag, cam, fn in shots:
        if ARGS and tag not in ARGS:
            continue
        scene.camera = cam
        scene.render.filepath = os.path.join(HERE, fn)
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"RENDER {fn}: {time.time() - t:.1f} s")
