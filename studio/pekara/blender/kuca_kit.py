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


def mat_plaster(name, col, var=0.07, bump=0.3, rough=0.86):
    """Rucno bojen gips/karton: mrlja u boji, krupna neravnina (gips) i sitno zrno (karton)."""
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
    return m, nt, p, co, bp


def mat_ribs(name, col, freq=2.0, gap=0.07, strength=0.6, metal=0.0, rough=0.86):
    """Vodoravne fuge: rustika prizemlja (2 po metru) ili rebra rolo-bedema (Rollbalken)."""
    m, nt, p, co, bp = mat_plaster(name, col, var=0.08, bump=0.22, rough=rough)
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


def mat_brick(name, c1, c2, mortar, scale, bump=0.4, rough=0.9):
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


M = {
    "sokla": mat_plaster("sokla", "#5e5850", var=0.1, bump=0.35)[0],
    "dimnjak": mat_plaster("dimnjak", "#9a8c7a", var=0.1, bump=0.35)[0],
    "staklo_tamno": mat_simple("staklo_tamno", "#0b0e13", rough=0.12),
    "staklo_slabo": mat_simple("staklo_slabo", "#1a120c", rough=0.2, emit="#b8682a", strength=0.12),
    "okvir": mat_plaster("okvir", "#e3dac8", var=0.03, bump=0.1, rough=0.6)[0],
    "drvo_radnja": mat_simple("drvo_radnja", "#4a2c16", rough=0.5),
    "tabla": mat_simple("tabla", "#5e1f17", rough=0.32, coat=0.6),            # lakirana, tamnocrvena
    "tabla_zel": mat_simple("tabla_zel", "#22382c", rough=0.36, coat=0.5),     # susedi: tamnozelena
    "zlato": mat_simple("zlato", "#c8963f", rough=0.32, metal=1.0),
    "zar": mat_glow("zar", 1.8),
    "staklo": mat_glass("staklo"),
    "hleb": mat_plaster("hleb", KORA, var=0.25, bump=0.4, rough=0.55)[0],
    "kocka": mat_brick("kocka", "#3a3631", "#4a453e", "#181614", 3.2, bump=0.6),
    "trotoar": mat_brick("trotoar", "#5a5650", "#625e57", "#34312e", 0.9, bump=0.3),
    "ivicnjak": mat_plaster("ivicnjak", "#7a756d", var=0.1, bump=0.3)[0],
    "dvoriste": mat_plaster("dvoriste", "#5b5145", var=0.18, bump=0.8)[0],
    "daska": mat_wood_board("daska"),
    "metal": mat_simple("metal", "#1b221f", rough=0.45, metal=0.6),
    "lampa": mat_simple("lampa", "#cfd8e6", rough=0.3, emit="#bcd0f0", strength=2.0),
    "lampica": mat_simple("lampica", "#ffe2b8", rough=0.3, emit="#ffc68a", strength=6.0),
    "sanduk": mat_plaster("sanduk", "#6b4a2c", var=0.12, bump=0.3)[0],
    "roleta": mat_ribs("roleta", "#6c6d6a", freq=12.0, gap=0.25, strength=0.35, metal=0.4, rough=0.5),
    "krosnja": mat_plaster("krosnja", "#4c5a36", var=0.2, bump=1.0, rough=0.95)[0],
    "stablo": mat_plaster("stablo", "#4a3a2c", var=0.1, bump=0.4)[0],
    "dim": mat_smoke("dim"),
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
    "roleta": ("roleta", 0.015, 1), "lampica": ("lampica", 0, 1),
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
            "fasada": mat_plaster(name + "_fasada", boja)[0],
            "stuko": mat_plaster(name + "_stuko", tint(boja, 0.38), var=0.04, bump=0.2)[0],
            "prizemlje": mat_ribs(name + "_prizemlje", tint(boja, -0.3)),
            "krov": mat_brick(name + "_krov", krov_boja, tint(krov_boja, -0.12), tint(krov_boja, -0.35),
                              1.4, bump=0.35, rough=0.75),
        }
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
        self.fac[0].extrude_s(self.b("krovfas"), 0.02, L - 0.02,
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
        dv.use = True
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
