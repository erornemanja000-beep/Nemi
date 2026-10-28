# Krume, smer 3 "Ein Fenster brennt": ceo kvart na dasci za hleb (talas 1, Z1).
# Ugaona kuca sa pekarom + po 3 suseda niz obe ulice (kao kuca-proba-3), niske fasade preko puta
# (presecene kao maketa), kocka, sine i tramvaj, lampe, figure, drvece.
# Fasada ugla iznad i oko izloga je poseban objekat "Kriska" sa zatvorenim presekom (boja kore),
# iza nje je prazan prostor za enterijer (drugi programer). Kriva "KameraPut" + Cilj_N + Pogl_N po mapi skrola.
# Kit se ne menja: iz kuca_kit.py se izvrsava samo deo do "kvart" (materijali, Builder, Facade, Kuca, red_kuca),
# plus svetlo/render iz njegovih odeljaka. Pokretanje:
#   Blender -b -P kvart.py                 (gradi, cuva kvart.blend, renderuje 1, 916, 3, 6)
#   Blender -b -P kvart.py -- norender     (samo gradi i cuva .blend)
#   Blender -b -P kvart.py -- 1 3          (samo izabrani kadrovi: 1, 916, 3, 6)
# bake_izvoz.py izvrsava ovaj fajl sa KRUME_WEB = True u globals: bevel 1 segment, bez cuvanja .blend i rendera.
# Okruzenje kao u kitu: KRUME_SAMPLES, KRUME_RES, KRUME_EXPOSURE, KRUME_AMB, KRUME_FILL, KRUME_PREFIX.

import bpy, bmesh, math, os, random, sys, time
from mathutils import Vector, Matrix

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(HERE, "kuca_kit.py")
with open(KIT) as fh:
    KIT_SRC = fh.read()


def kit_deo(od, do):
    """Odsecak kita izmedju dva komentara (od=None: od pocetka)."""
    a = KIT_SRC.index(od) if od else 0
    return compile(KIT_SRC[a:KIT_SRC.index(do, a)], KIT, "exec")


SEC = "# ---------------------------------------------------------------- "
exec(kit_deo(None, SEC + "kvart\n"), globals())        # paleta, materijali, Builder, Facade, Kuca, red_kuca
exec(kit_deo("# --- dim iz dva dimnjaka", "\nfor i, tp in enumerate(smoke_spots)"), globals())   # dim()
HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
WEB = globals().get("KRUME_WEB", False)
if WEB:                      # kao bake kita: ivice samo zakosene (daska zadrzava 2 segmenta), manje trouglova
    _kit_finish = Builder.finish

    def _web_finish(self):
        self.seg = 1 if self.bevel < 0.3 else 2
        return _kit_finish(self)

    Builder.finish = _web_finish

def mat_presek(name):
    """Rez kuce kao kriska hleba (fix A, krug popravki): topla porozna mrvica (dve velicine Voronoi pora) i tamna
    kora uz svaku ivicu reza. Kora je AO "iznutra" (Inside, samo sopstveni objekat, 0,22 m): tacka blizu ivice
    vidi susedno lice kroz telo zida. Sve ide u Base Color, pa ga bake albeda (DIFFUSE COLOR) nosi u GLB."""
    m, nt, p = node_mat(name)
    N = nt.nodes
    co = coord(nt)
    dist = noise(nt, co, 3.0, 2)                                  # pore nisu okrugle: koordinate malo iskrivljene
    mix_co = N.new("ShaderNodeVectorMath")
    mix_co.operation = "MULTIPLY_ADD"
    mix_co.inputs[1].default_value = (0.09, 0.09, 0.09)
    nt.links.new(dist.outputs["Color"], mix_co.inputs[0])
    nt.links.new(co, mix_co.inputs[2])
    pore = []
    for sc, r in ((5.5, 0.36), (14.0, 0.34)):                     # krupne (~6 cm) i sitne (~2,5 cm) pore
        vo = N.new("ShaderNodeTexVoronoi")
        vo.inputs["Scale"].default_value = sc
        nt.links.new(mix_co.outputs["Vector"], vo.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = r * 0.7
        mr.inputs["From Max"].default_value = r
        nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
        pore.append(mr)
    mn = N.new("ShaderNodeMath")
    mn.operation = "MINIMUM"
    nt.links.new(pore[0].outputs["Result"], mn.inputs[0])
    nt.links.new(pore[1].outputs["Result"], mn.inputs[1])
    var = noise(nt, co, 1.4, 3)
    mrv = N.new("ShaderNodeValToRGB")                             # mrvica: svetlija i tamnija mesta
    mrv.color_ramp.elements[0].color = hexc("#c79a5e")
    mrv.color_ramp.elements[1].color = hexc("#e4c590")
    nt.links.new(var.outputs["Fac"], mrv.inputs["Fac"])
    rupa = N.new("ShaderNodeMix")                                 # pora: senka u rupi
    rupa.data_type = "RGBA"
    nt.links.new(mn.outputs[0], rupa.inputs["Factor"])
    nt.links.new(mrv.outputs["Color"], rupa.inputs["B"])
    rupa.inputs["A"].default_value = hexc("#7e5128")
    ao = N.new("ShaderNodeAmbientOcclusion")
    ao.inside, ao.only_local, ao.samples = True, True, 16
    ao.inputs["Distance"].default_value = 0.22
    wob = noise(nt, co, 9.0, 2)                                   # rub kore nije ravan
    wa = N.new("ShaderNodeMath")
    wa.operation = "MULTIPLY_ADD"
    wa.inputs[1].default_value = 0.12
    nt.links.new(wob.outputs["Fac"], wa.inputs[0])
    nt.links.new(ao.outputs["AO"], wa.inputs[2])
    kr = N.new("ShaderNodeMapRange")                              # AO 1 u sredini reza, ~0,5 na ivici
    kr.inputs["From Min"].default_value = 1.0
    kr.inputs["From Max"].default_value = 0.86
    nt.links.new(wa.outputs[0], kr.inputs["Value"])
    kc = N.new("ShaderNodeValToRGB")                              # kora: zlatna ka mrvici, tamna spolja
    kc.color_ramp.elements[0].color = hexc("#b0682c")
    kc.color_ramp.elements[1].color = hexc("#5a2c12")
    nt.links.new(kr.outputs["Result"], kc.inputs["Fac"])
    kora = N.new("ShaderNodeMath")
    kora.operation = "MINIMUM"
    kora.inputs[1].default_value = 1.0
    gt = N.new("ShaderNodeMath")
    gt.operation = "MULTIPLY"
    gt.inputs[1].default_value = 3.0
    nt.links.new(kr.outputs["Result"], gt.inputs[0])
    nt.links.new(gt.outputs[0], kora.inputs[0])
    fin = N.new("ShaderNodeMix")
    fin.data_type = "RGBA"
    nt.links.new(kora.outputs[0], fin.inputs["Factor"])
    nt.links.new(rupa.outputs["Result"], fin.inputs["A"])
    nt.links.new(kc.outputs["Color"], fin.inputs["B"])
    nt.links.new(fin.outputs["Result"], p.inputs["Base Color"])
    bp = N.new("ShaderNodeBump")                                  # pore malo udubljene (render kadrova)
    bp.inputs["Strength"].default_value = 0.5
    bp.inputs["Distance"].default_value = 0.02
    nt.links.new(mn.outputs[0], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.95
    return m


PRESEK = mat_presek("presek")                                              # rez ugaone kuce: kriska hleba
UNUTRA = mat_plaster("unutra", TESTO, var=0.05, bump=0.15)[0]              # zidovi praznog prostora pekare
KROV_NASPRAM = mat_plaster("krov_naspram", "#2b2a2b", var=0.08, bump=0.2, rough=0.95)[0]  # ravni krovovi preko puta
SQ2 = math.sqrt(2)

# ---------------------------------------------------------------- ugaona kuca (pekara)
UG_C, UG_W, UG_D = 3.0, 14.0, 12.0
T = 0.7                     # debljina zida Kriske (gruenderzeit zid), izlog i vrata su unutar nje
XC, YC = 11.15, 9.0         # bocni rezovi Kriske: izmedju prozora, posle izloga na obe ulice
N_UG = Vector((-1, -1, 0)).normalized()          # spoljna normala zakosenog ugla
ORIGIN = Vector((UG_C / 2, UG_C / 2, 1.5))       # vrata pekare: odatle krece talas prozora


class Ugaona(Kuca):
    def izlog_pekara(self, e, s0, s1, z0=0.6, h=3.1):
        """Kao izlog "pekara" u kitu, ali bez polica i toplog zadnjeg zida: otvor ide kroz ceo zid,
        iza je prazan prostor za enterijer. Svetla ostaju (topao izvor scene)."""
        fac, w, sc = self.fac[e], s1 - s0, (s0 + s1) / 2
        dr = self.b("drvo")
        zt = z0 + h + 0.12
        fac.box(self.b("cut_gf"), sc, z0, w, T + 0.8, h, -T / 2 + 0.25, jit=False)
        fac.box(self.b("staklo"), sc, z0, w, 0.02, h, -0.12, jit=False)
        for s in [s0 + 0.06, s1 - 0.06] + [s0 + w * t for t in (1 / 3, 2 / 3)]:
            fac.box(dr, s, z0, 0.12, 0.14, h, -0.08)
        fac.box(dr, sc, z0, w, 0.16, 0.14, -0.06)
        fac.box(dr, sc, z0 + h - 0.12, w, 0.14, 0.12, -0.08)
        fac.box(dr, sc, z0 + h - 0.62, w, 0.12, 0.08, -0.08)
        fac.box(dr, sc, z0 - 0.08, w + 0.2, 0.32, 0.1, 0.0)
        fac.box(self.b("tabla"), sc, zt, w + 0.2, 0.1, 0.42, 0.05)
        for zz in (zt - 0.03, zt + 0.42):
            fac.box(self.b("zlato"), sc, zz, w + 0.32, 0.06, 0.04, 0.09)
        for s in (s0 - 0.06, s1 + 0.06):
            fac.box(self.b("zlato"), s, zt - 0.03, 0.04, 0.06, 0.49, 0.09)
        n_l = max(2, int(w / 2.2))
        for i in range(n_l):
            s = s0 + w * (i + 0.5) / n_l
            fac.box(self.b("metal"), s, zt + 0.5, 0.03, 0.45, 0.03, 0.3)
            fac.box(self.b("lampica"), s, zt + 0.42, 0.14, 0.1, 0.06, 0.52, jit=False)
        self.tabla_svetla.append(add_light(f"{self.name}_tabla_{e}", "AREA", fac.pt(sc, 0.75, zt + 0.55),
                                           rot_dir=-fac.n + Vector((0, 0, -0.9)), shape="RECTANGLE", size=w,
                                           size_y=0.15, energy=26 * w / 6.5, color=(1.0, 0.72, 0.42)))
        add_light(f"{self.name}_izlog_{e}", "AREA", fac.pt(sc, -0.35, 3.45), rot_dir=fac.n + Vector((0, 0, -0.55)),
                  shape="RECTANGLE", size=w - 0.3, size_y=0.4, energy=520 * w / 6.5, color=WARM)


ug = Ugaona("Ugao", [(UG_C, 0), (UG_W, 0), (UG_W, UG_D), (0, UG_D), (0, UG_C)], [0, 3, 4],
            {0: [1.5, 4.17, 6.83, 9.5], 4: [UG_C * SQ2 / 2], 3: [1.5, 4.5, 7.5]},
            "#dccaa2", nad=("zabat", "ravna", "venac", "kamen"), ugao=True, chamfer=4, krov="mansarda")
ug.tabla_svetla = []
ug.masa()
ug.prozori()
ug.krov_mansarda()
dim_tops = ug.dimnjaci_mansarda([(9.0, 9.0, 0.7, 1.4), (12.2, 4.5, 1.2, 0.6), (4.5, 10.2, 1.2, 0.6), (7.2, 6.0, 0.6, 0.6)])
ug.izlog_pekara(0, 0.9, 7.45)
ug.izlog_pekara(3, 4.0, 8.3)
ug.haustor(0, 9.5)
ug.prozor_prizemlja(3, 1.5)
Z1 = ug.gf + ug.fl + 0.55   # gornji rez Kriske: iznad zabata prvog sprata, ispod klupica drugog

FA, FB, FC = ug.fac[0], ug.fac[3], ug.fac[4]
dz = 2.95                    # vrata pekare na uglu (kao u kitu, bez pulta i hleba iza: to je enterijer)
FC.box(ug.b("cut_gf"), FC.L / 2, 0.12, 1.7, T + 0.8, dz + 0.55, -T / 2 + 0.25, jit=False)
for sg in (-1, 1):
    FC.box(ug.b("drvo"), FC.L / 2 + sg * 0.68, 0.12, 0.14, 0.1, dz, -0.5)
FC.box(ug.b("drvo"), FC.L / 2, 0.12, 1.5, 0.1, 0.55, -0.5)
FC.box(ug.b("metal"), FC.L / 2 + 0.45, 1.2, 0.04, 0.12, 0.55, -0.42)
FC.box(ug.b("staklo"), FC.L / 2, 0.12, 1.2, 0.02, dz + 0.5, -0.45, jit=False)
FC.box(ug.b("drvo"), FC.L / 2, dz + 0.12, 1.7, 0.14, 0.1, -0.5)
FC.box(ug.b("sokla"), FC.L / 2, 0.0, 2.0, 0.55, 0.12, 0.1)
# fix A: tabla nad vratima ugla (3,8-4,3 m) stajala je tik ispod balkona i odozgo se citala kao narandzast
# pravougaonik; ugao nosi samo Nasenschild, natpisi su table nad izlozima
add_light("Vrata", "AREA", FC.pt(FC.L / 2, -0.25, 3.0), rot_dir=FC.n + Vector((0, 0, -0.7)), shape="RECTANGLE",
          size=1.4, size_y=0.3, energy=260, color=WARM)
FA.box(ug.b("metal"), 0.55, 4.0, 0.05, 1.1, 0.05, 0.55)                  # Nasenschild
for sg in (0.2, 0.9):
    FA.box(ug.b("metal"), 0.55, 3.75, 0.02, 0.02, 0.25, sg)
FA.box(ug.b("tabla"), 0.55, 3.0, 0.07, 0.85, 0.75, 0.55)
FA.box(ug.b("zlato"), 0.55, 2.97, 0.05, 0.92, 0.82, 0.55)
for (s, z, rot) in ((0.5, 0.0, 0.05), (0.55, 0.42, -0.12), (1.3, 0.0, 0.2)):
    p = FB.pt(FB.L - s - 0.2, 0.55, z)
    wbox(ug.b("sanduk"), (p.x, p.y, p.z + 0.2), (0.6, 0.45, 0.4), FB.ang + rot)
ug.finish()


# ---------------------------------------------------------------- Kriska: rez fasade ugla
def prizma_ob(name, poly, z0, z1, mat):
    b = Builder(name, mat, bevel=0)
    prism(b, poly, z0, z1)
    ob = b.finish()
    ob.hide_render = True
    ob.display_type = "WIRE"
    return ob


ch_in = 3 + T * SQ2          # unutrasnja linija zakosenog zida: x + y = ch_in
SHELL = [(-3.0, -3.0), (XC, -3.0), (XC, T), (ch_in - T, T), (T, ch_in - T), (T, YC), (-3.0, YC)]
RC = ch_in - 0.1             # prostor pekare zalazi 5-10 cm u zid Kriske: bez komplanarnih lica za EXACT
RX, RY = 11.3, 8.7           # spoljna lica pregrade i zadnjeg zida enterijera (enterijer.py: X_PREG + 0.3, Y_ZAD + 0.3),
                             # da zidovi enterijera leze uz rez kuce, a ne iza njega
ROOM = [(T - 0.05, RC - T + 0.05), (RC - T + 0.05, T - 0.05), (RX, T - 0.05), (RX, RY), (T - 0.05, RY)]
ROOM_Z = (-0.05, Z1 - 0.35)
rez_k = prizma_ob("Rez_kriska", SHELL, -0.6, Z1, PRESEK)
rez_p = prizma_ob("Rez_pekara", ROOM, ROOM_Z[0], ROOM_Z[1], UNUTRA)


def u_kriski(p):
    if p.z >= Z1 or p.x >= XC or p.y >= YC:
        return False
    return not (p.x > T and p.y > T and p.x + p.y > ch_in)


class Acc:
    """Skuplja ostrva (otoke) mesha sa materijalima u novi mesh."""

    def __init__(self):
        self.v, self.f, self.fm, self.fs, self.mats = [], [], [], [], []

    def mi(self, m):
        if m not in self.mats:
            self.mats.append(m)
        return self.mats.index(m)

    def dodaj(self, faces, mats):
        idx = {}
        for fc in faces:
            ids = []
            for v in fc.verts:
                if v.index not in idx:
                    idx[v.index] = len(self.v)
                    self.v.append(tuple(v.co))
                ids.append(idx[v.index])
            self.f.append(ids)
            self.fm.append(self.mi(mats[fc.material_index] if fc.material_index < len(mats) else mats[0]))
            self.fs.append(fc.smooth)

    def dodaj_mesh(self, me):
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.index_update()
        self.dodaj(list(bm.faces), list(me.materials))
        bm.free()

    def mesh(self, name):
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        for m in self.mats:
            me.materials.append(m)
        for p, mi, sm in zip(me.polygons, self.fm, self.fs):
            p.material_index, p.use_smooth = mi, sm
        me.validate()
        return me


def otoci(bm):
    bm.faces.ensure_lookup_table()
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        seen.add(f.index)
        st, isl = [f], []
        while st:
            g = st.pop()
            isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        st.append(h)
        out.append(isl)
    return out


def boolean(me, ops):
    """ops: [(objekat, "INTERSECT"/"DIFFERENCE")], EXACT, presecene povrsine dobijaju materijal rezaca."""
    tmp = bpy.data.objects.new("_tmp_bool", me)
    scene.collection.objects.link(tmp)
    for ob, op in ops:
        md = tmp.modifiers.new(op, "BOOLEAN")
        md.operation, md.object, md.solver = op, ob, "EXACT"
        md.material_mode = "TRANSFER"
    dg = bpy.context.evaluated_depsgraph_get()
    out = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(me)
    return out


MASE = ("fasada", "prizemlje")


def podeli_ugao():
    """Svaki deo ugaone kuce (sa primenjenim modifikatorima) ide u Krisku, u kucu, ili se sece."""
    t = time.time()
    kr, kr_st = Acc(), Acc()
    n_cut = 0
    # mase (pune prizme) se seku u steku modifikatora: posle reza prozora, pre bevel-a (na gotovom
    # bevel-ovanom meshu EXACT ostavlja ostatke); Kriska dobija kopiju sa INTERSECT
    for key in MASE:
        ob = ug.obj[key]
        kop = ob.copy()
        scene.collection.objects.link(kop)
        for tgt, ops in ((ob, [(rez_k, "DIFFERENCE"), (rez_p, "DIFFERENCE")]), (kop, [(rez_k, "INTERSECT")])):
            for i, (c, op) in enumerate(ops):
                md = tgt.modifiers.new("Kriska_" + op, "BOOLEAN")
                md.operation, md.object, md.solver, md.material_mode = op, c, "EXACT", "TRANSFER"
                tgt.modifiers.move(len(tgt.modifiers) - 1, 1 + i)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(kop.evaluated_get(dg))
        kr.dodaj_mesh(me)
        bpy.data.meshes.remove(me)
        bpy.data.objects.remove(kop, do_unlink=True)
    dg = bpy.context.evaluated_depsgraph_get()
    for key, ob in list(ug.obj.items()):
        if key in CUTTERS or key == "sanduk":
            continue
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        mats = list(me.materials)
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.verts.index_update()
        kuca = Acc()
        dest_k = kr_st if key == "staklo" else kr
        for isl in otoci(bm):
            if key in MASE:
                kuca.dodaj(isl, mats)
                continue
            vs = {v for f in isl for v in f.verts}
            ins = [u_kriski(v.co) for v in vs]
            if all(ins):
                dest_k.dodaj(isl, mats)
                continue
            lo = Vector([min(v.co[i] for v in vs) for i in range(3)])
            hi = Vector([max(v.co[i] for v in vs) for i in range(3)])
            if not any(ins) and (lo.z >= Z1 or lo.x >= XC or lo.y >= YC or not u_kriski((lo + hi) / 2)):
                kuca.dodaj(isl, mats)
                continue
            one = Acc()                       # ostrvo prelazi rez: presek ide u Krisku, ostatak u kucu
            one.dodaj(isl, mats)
            m1 = one.mesh("_ostrvo")
            for acc, ops in ((dest_k, [(rez_k, "INTERSECT")]), (kuca, [(rez_k, "DIFFERENCE"), (rez_p, "DIFFERENCE")])):
                mo = boolean(m1.copy(), ops)
                acc.dodaj_mesh(mo)
                bpy.data.meshes.remove(mo)
            bpy.data.meshes.remove(m1)
            n_cut += 1
        bm.free()
        bpy.data.meshes.remove(me)
        old = ob.data
        ob.data = kuca.mesh(ob.name)
        ob.modifiers.clear()
        bpy.data.meshes.remove(old)
        if not ob.data.polygons:
            bpy.data.objects.remove(ob, do_unlink=True)
            del ug.obj[key]
    for key in CUTTERS:
        if key in ug.obj:
            bpy.data.objects.remove(ug.obj.pop(key), do_unlink=True)
    o = Vector((UG_C / 2, UG_C / 2, 0.0))           # ishodiste Kriske: dno sredine zakosenog ugla
    kob = bpy.data.objects.new("Kriska", kr.mesh("Kriska"))
    # fix A: mrvica je samo na krajevima reza (x = XC, y = YC, vrh Z1); unutrasnje lice Kriske (uz pekaru,
    # vidi se kroz izlog) je zid pekare, a ne kriska hleba
    me_k = kob.data
    if UNUTRA.name not in [m.name for m in me_k.materials]:
        me_k.materials.append(UNUTRA)
    i_pr = [m.name for m in me_k.materials].index(PRESEK.name)
    i_un = [m.name for m in me_k.materials].index(UNUTRA.name)
    n_un = 0
    for p in me_k.polygons:
        if p.material_index != i_pr:
            continue
        c, n = p.center, p.normal
        if ((abs(c.y - T) < 0.02 and n.y > 0.9) or (abs(c.x - T) < 0.02 and n.x > 0.9)
                or (abs(c.x + c.y - ch_in) < 0.03 and n.x > 0.6 and n.y > 0.6)):
            p.material_index = i_un
            n_un += 1
    sob = bpy.data.objects.new("Kriska_staklo", kr_st.mesh("Kriska_staklo"))
    for ob in (kob, sob):
        ob.data.transform(Matrix.Translation(-o))
        scene.collection.objects.link(ob)
    kob.location = o
    sob.parent = kob
    sob.visible_shadow = False                       # toplo svetlo izlazi na trotoar (kao u kitu)
    for lt in ug.tabla_svetla:                       # svetla nad tablama idu sa fasadom
        mw = lt.matrix_world.copy()
        lt.parent = kob
        lt.matrix_world = mw
    print(f"Kriska: {n_cut} ostrva preseceno, {n_un} unutrasnjih lica reza -> unutra, {time.time() - t:.1f} s")
    return kob, sob


kriska, kriska_staklo = podeli_ugao()
IZVUCI, SPUSTI = 4.5, 9.5
kriska["izvuci_smer"] = list(N_UG)          # Blender koordinate; u glTF (y gore): (x, z, -y)
kriska["izvuci_m"] = IZVUCI
kriska["spusti_m"] = SPUSTI
kriska["opis"] = "fr 1-40 izvlacenje ka ulici (pogl. 3), fr 40-70 spustanje kroz dasku (put za kameru u pogl. 4)"
kriska["wake"] = 0.0
for f, d in ((1, Vector()), (40, N_UG * IZVUCI), (70, N_UG * IZVUCI + Vector((0, 0, -SPUSTI)))):
    kriska.location = Vector((UG_C / 2, UG_C / 2, 0.0)) + d
    kriska.keyframe_insert("location", frame=f)
kriska.animation_data.action.name = "Kriska_izvlacenje"
scene.frame_start, scene.frame_end = 1, 70

otvor = bpy.data.objects.new("Pekara_otvor", None)      # prazan prostor za enterijer
otvor.empty_display_type = "CUBE"
otvor.location = ((T + RX) / 2, (T + RY) / 2, (ROOM_Z[0] + ROOM_Z[1]) / 2)
otvor.scale = ((RX - T) / 2, (RY - T) / 2, (ROOM_Z[1] - ROOM_Z[0]) / 2)
scene.collection.objects.link(otvor)
otvor["tlocrt"] = [c for p in ROOM for c in p]
otvor["z"] = list(ROOM_Z)
otvor["opis"] = ("unutrasnjost bez poda i bez namestaja (prazna, proverava bake_izvoz.py): x,y tlocrt (Blender m), "
                 "zakosen ugao uz vrata; zid Kriske je debeo T")
otvor["T"] = T
# privremeno svetlo u praznom prostoru, dok ne stigne enterijer (izlog svetli kroz staklo)
add_light("Pekara_unutra", "AREA", (5.2, 4.6, ROOM_Z[1] - 0.4), rot_dir=(0, 0, -1), shape="RECTANGLE",
          size=7.0, size_y=5.0, energy=700, color=(1.0, 0.6, 0.3))

# ---------------------------------------------------------------- susedi (isti kit, bez upaljenih prozora)
SUSEDI_A = [
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


def prizemlje(h, gfspec, gf):
    for it in gfspec:
        if it[0] == "haustor":
            h.haustor(0, it[1], h=min(3.4, gf - 0.9))
        elif it[0] == "prozor":
            h.prozor_prizemlja(0, it[1], z=min(1.2, gf - 2.6), h=min(2.2, gf - 1.6))
        else:
            h.izlog(0, it[1], it[2], it[0], z0=0.5, h=gf - 1.65)


for smer, niz, start in (("A", SUSEDI_A, UG_W), ("B", SUSEDI_B, UG_D)):
    pos = start
    for nm, w, nf, boja, nad, kb, gfspec in niz:
        gf = 4.1 if nf == 3 else 4.3
        fl = 3.25 if nf == 3 else 3.15
        h, ax = red_kuca(nm, pos, pos, w, DEPTH, smer, boja, gf=gf, fl=fl, nf=nf, nad=nad, krov_boja=kb)
        h.masa()
        h.prozori()
        h.krov_sattel(mansarde=ax[::2] if nf == 4 else (), dimnjaci=(0.28, 0.76))
        prizemlje(h, gfspec, gf)
        h.finish()
        kuce.append(h)
        pos += w
X_END, Y_END = UG_W + sum(s[1] for s in SUSEDI_A), UG_D + sum(s[1] for s in SUSEDI_B)

# ---------------------------------------------------------------- daska i ulice
FAR, NAS = -10.0, -13.0          # ivica trotoara preko puta, linija fasada preko puta
BX0 = BY0 = -19.5
BX1, BY1 = X_END + 2.0, Y_END + 2.0
RUB = 1.3
IX0, IY0, IX1, IY1 = BX0 + RUB, BY0 + RUB, BX1 - RUB, BY1 - RUB
CX, CY = (BX0 + BX1) / 2, (BY0 + BY1) / 2


class Niska(Kuca):
    """Kuca preko puta, presecena iznad prizemlja kao na maketi: gore je taman ravan krov (fix A).
    FOTO (krug 2): kadar 1 gleda u njihova dvorista, pa su bile crni blokovi. Sad su niske prizemne kuce
    (Vorstadthaus): svetliji malter, prozori i u dvoristu (poneki slabo upaljen), nizak dvovodni krov sa
    strehom, olukom i dimnjakom. U polusenci su, tamnije od pekare."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        if FOTO:   # ceo zid je "prizemlje": malter bez rustike, svetliji od rustike suseda
            self.M["prizemlje"] = mat_plaster(self.name + "_zid", tint(a[4], -0.1), tex="malter")[0]

    def izlog_slabo(self, e, s0, s1, z0=0.5, h=1.65):
        """Izlog kao "tamno" u kitu, ali staklo slabo toplo svetli (kafana koja jos nije otvorila)."""
        kit_b = self.b
        self.b = lambda k: kit_b("slabo" if k == "tamno" else k)
        self.izlog(e, s0, s1, "tamno", z0=z0, h=h)
        del self.b

    def nasenschild(self, s, z=2.05):
        """Tabla na konzoli, upravno na fasadu (vidi se iz ulice i odozgo kao crtica)."""
        fac = self.fac[0]
        fac.box(self.b("metal"), s, z + 0.62, 0.04, 0.9, 0.04, 0.45)
        fac.box(self.b("tabla_zel"), s, z, 0.06, 0.62, 0.55, 0.55)
        fac.box(self.b("zlato"), s, z - 0.03, 0.04, 0.68, 0.61, 0.55)

    def krov_foto(self, H):
        """Nizak dvovodni krov, sleme paralelno sa ulicom; nagib i dimnjak se smenjuju po kuci."""
        f, d, L = self.fac[0], self.fac[1].L, self.fac[0].L
        k = int(self.name[2:])
        st, kr, me = self.b("stuko"), self.b("krov"), self.b("metal")
        F = self.foot
        ring(st, offset_poly(F, [0.12] * len(F)), H - 0.28, H + 0.04, offset_poly(F, [-0.2] * len(F)))   # venac
        rh = d / 2 * (0.55, 0.68, 0.5, 0.62)[k % 4]
        R0 = H + 0.04
        z_e = R0 - 0.08
        f.extrude_s(self.b("kalkan"), 0.02, L - 0.02, [(0.0, R0 - 0.05), (-d / 2, R0 + rh - 0.1), (-d, R0 - 0.05)])
        for o_e in (0.42, -d - 0.42):                                       # ulicna i dvorisna ploca
            f.extrude_s(kr, 0.0, L, [(o_e, z_e), (-d / 2, R0 + rh + 0.1), (-d / 2, R0 + rh - 0.1), (o_e, z_e - 0.2)])
            sg = 1 if o_e > 0 else -1                                        # oluk ispod strehe
            f.extrude_s(me, 0.0, L, [(o_e - sg * 0.02, z_e - 0.36), (o_e + sg * 0.12, z_e - 0.36),
                                     (o_e + sg * 0.12, z_e - 0.22), (o_e - sg * 0.02, z_e - 0.22)])
        f.extrude_s(me, 0.0, L, [(-d / 2 + 0.12, R0 + rh + 0.06), (-d / 2 - 0.12, R0 + rh + 0.06), (-d / 2, R0 + rh + 0.2)])
        s_c = L * (0.3 if k % 2 else 0.68)                                  # dimnjak
        p = f.pt(s_c, -d / 2 - 0.45, 0)
        z1 = R0 + rh + 0.9
        wbox(self.b("dimnjak"), (p.x, p.y, (R0 + rh - 0.6 + z1) / 2), (0.55, 0.75, z1 - (R0 + rh - 0.6)), f.ang)
        wbox(self.b("dimnjak"), (p.x, p.y, z1 + 0.06), (0.7, 0.9, 0.12), f.ang)
        fb = self.fac[2]                                                     # olucna cev na dvorisnom uglu
        fb.box(me, fb.L - 0.25, 0.1, 0.1, 0.1, z_e - 0.4, 0.12)

    def prozori_dvor(self, H):
        """Dvorisna fasada (ivica 2, ka kameri u pogl. 1): prozori sa krstom, sambranom i klupicom."""
        fac, k = self.fac[2], int(self.name[2:])
        L = fac.L
        n = max(1, int((L - 1.2) / 2.3))
        z0, h, w = 0.95, min(1.5, H - 1.45), 0.95
        st, ok = self.b("stuko"), self.b("okvir")
        for i in range(n):
            s = 0.6 + (L - 1.2) * (i + 0.5) / n
            fac.box(self.b("cut_gf"), s, z0, w, 0.6, h, 0.0, jit=False)
            upaljen = (k + 2 * (self.name[1] == "Z")) % 3 == 1 and i == n // 2
            fac.box(self.b("upaljen" if upaljen else "tamno"), s, z0, w, 0.03, h, -0.16, jit=False)
            fac.box(ok, s, z0, 0.06, 0.05, h, -0.13)
            fac.box(ok, s, z0 + h * 0.62, w, 0.05, 0.06, -0.13)
            for sg in (-1, 1):
                fac.box(ok, s + sg * (w / 2 - 0.03), z0, 0.06, 0.05, h, -0.13)
                fac.box(st, s + sg * (w / 2 + 0.07), z0 - 0.02, 0.14, 0.07, h + 0.04, 0.03)
            fac.box(ok, s, z0, w, 0.05, 0.06, -0.13)
            fac.box(ok, s, z0 + h - 0.06, w, 0.05, 0.06, -0.13)
            fac.box(st, s, z0 - 0.1, w + 0.3, 0.16, 0.08, 0.06)                # klupica
            fac.box(st, s, z0 + h, w + 0.28, 0.08, 0.14, 0.03)                 # nadprozornik

    def niska(self, H, gfspec):
        F = self.foot
        prism(self.b("prizemlje"), F, 0.0, H)
        IN = offset_poly(F, [-0.35] * len(F))
        ring(self.b("sokla"), offset_poly(F, self.offs(0.06)), 0.0, 0.45, IN)
        # fix A: odozgo (pogl. 1, 6, 7) presek sa sobama i narandzastim rubom izgledao je kao nedovrsena parcela;
        # sad je to tamna mirna masa: ravan krov i nizak zidic, bez detalja, utapa se u maglu
        if FOTO:
            self.krov_foto(H)
            self.prozori_dvor(H)
        else:
            self.B["krov_n"] = Builder(self.name + "_krov_n", KROV_NASPRAM, 0.02, 1)
            prism(self.B["krov_n"], F, H - 0.02, H + 0.04)
            ring(self.B["krov_n"], F, H + 0.04, H + 0.2, offset_poly(F, [-0.22] * len(F)))
        self.haus_s = self.fac[0].L / 2
        for it in gfspec:
            e = it[-1]
            if it[0] == "haustor":
                self.haustor(e, it[1], h=2.5)
                self.haus_s = it[1]
            elif it[0] == "prozor":
                self.prozor_prizemlja(e, it[1], z=0.95, h=1.5)
            elif it[0] == "kafe":
                self.izlog_slabo(e, it[1], it[2])
            elif it[0] == "schild":
                self.nasenschild(it[1])
            else:
                self.izlog(e, it[1], it[2], it[0], z0=0.5, h=1.65)


NASPRAM_BOJE = ["#b9a27a", "#a98f80", "#9e9a90", "#c2a067", "#a7867c", "#8f8c84", "#b39b86"]
naspram = []


def red_naspram(pref, smer, start, kraj, sirine):
    pos, g = start, 0.02
    for i, w in enumerate(sirine):
        w = min(w, kraj - pos)
        if w < 3.0:
            break
        a, b = pos + g, pos + w - g
        if smer == "S":        # juzni red, fasada ka severu (y = NAS)
            foot = [(b, NAS), (a, NAS), (a, IY0), (b, IY0)]
        else:                  # zapadni red, fasada ka istoku (x = NAS)
            foot = [(NAS, a), (NAS, b), (IX0, b), (IX0, a)]
        L = b - a
        spec = [("haustor", L * 0.22, 0), ("kafe" if i % 2 == 0 else "tamno", L * 0.42, L - 0.6, 0)] if i % 3 == 0 else \
               [("roleta", 0.6, L * 0.55, 0), ("prozor", L * 0.75, 0), ("schild", L * 0.62, 0)] if i % 3 == 1 else \
               [("prozor", L * 0.2, 0), ("haustor", L * 0.5, 0), ("prozor", L * 0.8, 0), ("schild", L * 0.36, 0)]
        kw = {"krov_boja": CREP if (i + (smer == "Z")) % 3 == 0 else KROV} if FOTO else {}
        h = Niska(f"{pref}{i + 1}", foot, [0], {}, NASPRAM_BOJE[(i * 3 + (smer == "Z")) % len(NASPRAM_BOJE)], **kw)
        H = (2.9, 3.25, 2.95, 3.4, 3.05)[(i + 2 * (smer == "Z")) % 5]     # razlicite visine reza: red nije krut
        h.niska(H, spec)
        h.finish()
        naspram.append(h)
        pos += w


red_naspram("NS", "S", NAS, IX1, [9.0, 8.0, 10.0, 8.5, 9.0, 8.0, 9.0])
red_naspram("NZ", "Z", NAS, IY1, [8.5, 9.5, 8.0, 9.0, 8.0, 7.5, 9.0])
# ugao iza oba reda (x, y < NAS) ostaje mali trg sa drvetom

amb = {}


def ambijent(name, mat, bevel=0.03, seg=2):
    amb[name] = Builder(name, M[mat] if isinstance(mat, str) else mat, bevel=bevel, seg=seg)
    return amb[name]


wbox(ambijent("Daska_za_hleb", "daska", bevel=0.45, seg=6), (CX, CY, -0.95), (BX1 - BX0, BY1 - BY0, 1.1), jit=False)
wbox(ambijent("Ulica_kocka", "kocka", bevel=0.05), (CX, CY, -0.32), (IX1 - IX0, IY1 - IY0, 0.16), jit=False)
BLOK = [(UG_C, 0), (X_END, 0), (X_END, Y_END), (0, Y_END), (0, UG_C)]
b_ivic = ambijent("Ivicnjak", "ivicnjak", bevel=0.05)
b_trot = ambijent("Trotoar", "trotoar", bevel=0.02)
ring(b_ivic, offset_poly(BLOK, [3.0, 0.0, 0.0, 3.0, 3.0]), -0.24, -0.02, offset_poly(BLOK, [2.5, -0.5, -0.5, 2.5, 2.5]))
prism(b_trot, offset_poly(BLOK, [2.75, -0.1, -0.1, 2.75, 2.75]), -0.24, 0.0)
prism(b_trot, rect(IX0, IY0, IX1, FAR), -0.24, 0.0)                  # trotoari preko puta (ulica ~7 m)
prism(b_trot, rect(IX0, FAR, FAR, IY1), -0.24, 0.0)
prism(b_ivic, rect(FAR + 0.25, FAR, IX1, FAR + 0.25), -0.24, -0.02)
prism(b_ivic, rect(FAR, FAR, FAR + 0.25, IY1), -0.24, -0.02)
b_dv = ambijent("Dvoriste", "dvoriste", bevel=0.03)
prism(b_dv, rect(DEPTH - 0.2, DEPTH - 0.2, X_END - 0.05, Y_END - 0.05), 0.0, 0.07)
# sine: tramvaj ide juznom ulicom (pored izloga pekare), od ivice do ivice daske
SINE_Y, GAUGE = (-3.0 + FAR - 0.25) / 2, 1.435
b_sin = ambijent("Sine", "metal", bevel=0.01, seg=1)
for sg in (-1, 1):
    for dy in (-0.05, 0.05):
        wbox(b_sin, ((IX0 + IX1) / 2, SINE_Y + sg * GAUGE / 2 + dy, -0.225), (IX1 - IX0 - 0.1, 0.035, 0.035), jit=False)
for b in list(amb.values()):
    amb[b.name] = b.finish()


def u_jedan(name, builders, loc=None):
    """Vise Builder-a (po materijal) u jedan objekat sa vise materijala; loc: ishodiste objekta."""
    obs = [b.finish() for b in builders if len(b.bm.faces)]
    dg = bpy.context.evaluated_depsgraph_get()
    acc = Acc()
    for ob in obs:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        acc.dodaj_mesh(me)
        bpy.data.meshes.remove(me)
        bpy.data.objects.remove(ob, do_unlink=True)
    me = acc.mesh(name)
    o = Vector(loc) if loc is not None else Vector()
    me.transform(Matrix.Translation(-o))
    ob = bpy.data.objects.new(name, me)
    ob.location = o
    scene.collection.objects.link(ob)
    return ob


# --- ulicne lampe: jedan mesh, 8 instanci (glTF ih izvozi kao isti mesh)
bm_met = Builder("_lampa_met", M["metal"], bevel=0.01, seg=1)
bm_gl = Builder("_lampa_gl", M["lampa"], bevel=0)
lathe(bm_met, (0, 0, 0), [(0.0, 0), (0.16, 0), (0.16, 0.3), (0.09, 0.45), (0.06, 1.5), (0.045, 4.6), (0.0, 4.65)], seg=10)
wbox(bm_met, (0.55, 0, 4.55), (1.1, 0.06, 0.06), jit=False)
lathe(bm_met, (1.1, 0, 4.1), [(0.0, 0.42), (0.32, 0.25), (0.34, 0.2), (0.0, 0.2)], seg=12)
lathe(bm_gl, (1.1, 0, 4.1), [(0.0, 0.0), (0.18, 0.05), (0.28, 0.2), (0.0, 0.2)], seg=12)
lampa_tpl = u_jedan("Lampa", [bm_met, bm_gl])
LAMPE = [(17.5, -2.45, -90), (31.0, -2.45, -90), (-2.45, 17.0, 180), (-2.45, 30.0, 180),
         (8.0, FAR - 0.4, 90), (26.0, FAR - 0.4, 90), (FAR - 0.4, 8.0, 0), (FAR - 0.4, 25.0, 0)]
lampe, lampe_svetla = [], []
for i, (lx, ly, ang) in enumerate(LAMPE):
    ob = bpy.data.objects.new(f"Lampa_{i + 1}", lampa_tpl.data)
    ob.location = (lx, ly, 0.0)
    ob.rotation_euler = (0, 0, math.radians(ang))
    scene.collection.objects.link(ob)
    a = math.radians(ang)
    if FOTO:
        # Spot tik ispod stakla (svetlo nije zatvoreno u neprozirnoj kapi), mali radijus, 2700 K; stub blago nakrivljen
        ob.rotation_euler = (random.uniform(-0.008, 0.008), random.uniform(-0.008, 0.008), math.radians(ang))
        lt = add_light(f"Lampa_{i + 1}_svetlo", "SPOT", (lx + math.cos(a) * 1.1, ly + math.sin(a) * 1.1, 4.04),
                       energy=60, shadow_soft_size=0.04, spot_size=math.radians(130), spot_blend=0.6,
                       use_temperature=True, temperature=2700.0, color=(1.0, 1.0, 1.0))
    else:
        lt = add_light(f"Lampa_{i + 1}_svetlo", "POINT", (lx + math.cos(a) * 1.1, ly + math.sin(a) * 1.1, 4.2),
                       energy=35, color=(0.75, 0.85, 1.0), shadow_soft_size=0.15)
    lt.parent = ob
    lt.matrix_parent_inverse = ob.matrix_world.inverted()
    lampe.append(ob)
    lampe_svetla.append(lt)
bpy.data.objects.remove(lampa_tpl, do_unlink=True)

# --- tramvaj: dva clanka, crveno-beli princip, bez natpisa i logotipa; ishodiste na sinama, ide po x
TR = {
    "crveno": mat_simple("tram_crveno", "#a8261f", rough=0.45, coat=0.4),
    "belo": mat_plaster("tram_belo", "#ece3cf", var=0.03, bump=0.08, rough=0.55)[0],
    "krov": mat_plaster("tram_krov", "#6a6b68", var=0.06, bump=0.2)[0],
    "okno": mat_simple("tram_okno", "#2a2c2e", rough=0.2, emit="#e6ecf2", strength=1.4),
    "far": mat_simple("tram_far", "#fff4dc", rough=0.2, emit="#fff1d0", strength=6.0),
}
TRAM_X = 25.0
tb = {k: Builder("_tram_" + k, m, bevel=(0.12 if k in ("crveno", "belo") else 0.02), seg=3) for k, m in TR.items()}
tb["tamno"] = Builder("_tram_tamno", M["metal"], bevel=0.02, seg=1)
for (x0, x1) in ((-7.6, 0.6), (0.95, 7.6)):
    cx, L = (x0 + x1) / 2, x1 - x0
    wbox(tb["tamno"], (cx, 0, 0.27), (L - 0.6, 2.0, 0.34), jit=False)                    # podvozje
    wbox(tb["crveno"], (cx, 0, 0.95), (L, 2.3, 1.1), jit=False)                         # donji deo
    wbox(tb["belo"], (cx, 0, 1.56), (L + 0.01, 2.31, 0.14), jit=False)                  # beli pojas
    wbox(tb["okno"], (cx, 0, 2.13), (L - 0.06, 2.24, 1.02), jit=False)                  # osvetljena okna
    n = int(L / 1.3)
    for k in range(n + 1):                                                              # stubici
        px = x0 + 0.08 + k * (L - 0.16) / n
        for sg in (-1, 1):
            wbox(tb["belo"], (px, sg * 1.13, 2.13), (0.12, 0.06, 1.02), jit=False)
    wbox(tb["crveno"], (cx, 0, 2.78), (L, 2.3, 0.3), jit=False)                         # gornji deo
    wbox(tb["krov"], (cx, 0, 3.0), (L - 0.3, 2.0, 0.16), jit=False)
wbox(tb["tamno"], (0.78, 0, 1.75), (0.5, 2.1, 2.6), jit=False)                         # harmonika
for sx in (-7.62, 7.62):
    for sy in (-0.7, 0.7):
        wbox(tb["far"], (sx, sy, 0.75), (0.04, 0.22, 0.12), jit=False)
wbox(tb["tamno"], (-3.0, 0, 3.12), (1.2, 0.9, 0.06), jit=False)                        # pantograf
for sg in (-1, 1):
    wbox(tb["tamno"], (-3.0 + sg * 0.3, 0, 3.52), (0.05, 0.05, 0.8), jit=False)
wbox(tb["tamno"], (-3.0, 0, 3.94), (0.08, 1.6, 0.05), jit=False)
tram = u_jedan("Tramvaj", list(tb.values()))
tram.location = (TRAM_X, SINE_Y, -0.22)
tram["opis"] = "ishodiste na sredini sina; ide po x (juzna ulica), duzina ~15.6 m"

# --- figure: minijature bez lica, neke sa papirnom kesom
KESA = mat_plaster("kesa", "#b08a5a", var=0.08, bump=0.3)[0]
GLAVA = mat_plaster("glava", "#cdb594", var=0.05, bump=0.1)[0]
FIG = [  # (x, y, ugao smera, boja kaputa, kesa)
    (6.0, -1.7, 160, "#3d4a5c", True), (-1.6, 6.5, -70, "#5a3f33", True), (22.0, -1.4, 0, "#4d5440", False),
    (-1.5, 24.0, 90, "#6a5f55", False), (14.0, FAR - 1.4, 180, "#2f3540", True), (FAR - 1.5, 15.0, -90, "#7a6a50", False),
]
figure = []
for i, (fx, fy, fa, col, kesa) in enumerate(FIG):
    bk = Builder("_fig_k", mat_plaster(f"kaput_{i + 1}", col, var=0.05, bump=0.15)[0], bevel=0)
    bg = Builder("_fig_g", GLAVA, bevel=0)
    lathe(bk, (0, 0, 0), [(0.0, 0.0), (0.15, 0.0), (0.2, 0.85), (0.21, 1.3), (0.15, 1.45), (0.07, 1.5), (0.0, 1.5)], seg=10)
    bmesh.ops.create_uvsphere(bg.bm, u_segments=10, v_segments=7, radius=0.12, matrix=Matrix.Translation((0, 0, 1.62)))
    bl = [bk, bg]
    if kesa:
        bs = Builder("_fig_s", KESA, bevel=0.01, seg=1)
        wbox(bs, (0.0, 0.29, 0.72), (0.26, 0.14, 0.34), jit=False)
        bl.append(bs)
    ob = u_jedan(f"Figura_{i + 1}", bl)
    ob.location = (fx, fy, 0.0)
    tilt = 0.03 if FOTO else 0.0                    # FOTO: figure ne stoje savrseno uspravno (rucno zalepljene)
    ob.rotation_euler = (random.uniform(-tilt, tilt), random.uniform(-tilt, tilt), math.radians(fa))
    ob["kesa"] = kesa
    figure.append(ob)

# --- drvece: sundjeraste krosnje kao na maketi (dva u ulici, jedno u dvoristu)
drvece = []
for i, (tx, ty, r) in enumerate(((-11.5, 33.5, 1.5), (24.0, 22.0, 2.2))):
    bs, bk = Builder("_st", M["stablo"], bevel=0), Builder("_kr", M["krosnja"], bevel=0)
    lathe(bs, (tx, ty, 0.0), [(0.0, 0), (0.2, 0), (0.15, 1.2), (0.11, 3.2 * r / 2), (0.0, 3.3 * r / 2)], seg=8)
    for k in range(6):
        a = k * 2.1
        c = (tx + math.cos(a) * r * 0.45, ty + math.sin(a) * r * 0.45, 3.4 * r / 2 + r * 0.55 + random.uniform(-0.2, 0.4))
        ellipsoid(bk, c, (r * random.uniform(0.95, 1.2),) * 2 + (r * 0.95,), seg=(12, 8))
    drvece.append(u_jedan(f"Drvo_{i + 1}", [bs, bk], loc=(tx, ty, 0.0)))

# --- dim samo iz dimnjaka pekare
dim(dim_tops[0], 11)


def mat_magla(name):
    """Tanka prizemna magla: Volume Scatter, gustina opada sa visinom (Generated Z) i rastrgana sumom."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    vs = nt.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Color"].default_value = hexc("#cfc6bc")
    vs.inputs["Anisotropy"].default_value = 0.45            # svetlo izloga i lampi dobija oreol prema kameri
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sp.inputs["Vector"])
    vis = math_n(nt, "POWER", map_n(nt, sp.outputs["Z"], 1.0, 0.0), 2.0)
    nz = noise(nt, tc.outputs["Object"], 0.09, 3, 0.5)
    pr = map_n(nt, nz.outputs["Fac"], 0.35, 0.7, 0.15, 1.0)
    d = math_n(nt, "MULTIPLY", math_n(nt, "MULTIPLY", vis, pr), float(os.environ.get("KRUME_MAGLA", "0.07")))
    nt.links.new(d, vs.inputs["Density"])
    nt.links.new(vs.outputs["Volume"], nt.nodes["Material Output"].inputs["Volume"])
    return m


if FOTO:
    # magla samo nad ulicama (dve kutije, L oko bloka, bez preklapanja): ne ulazi u pekaru ni u blok, nema globalnog volumena
    MAGLA = mat_magla("magla")
    for nm, (x0, y0, x1, y1) in (("Magla_jug", (IX0, NAS, IX1, -0.3)), ("Magla_zapad", (NAS, -0.3, -0.3, IY1))):
        bmg = Builder(nm, MAGLA, bevel=0)
        prism(bmg, rect(x0, y0, x1, y1), -0.3, 2.6)
        mg = bmg.finish()
        mg.visible_shadow = False

# ---------------------------------------------------------------- svetlo i render (odeljci kita)
exec(kit_deo(SEC + "svetlo\n", SEC + "kamere\n"), globals())
exec(kit_deo(SEC + "render\n", SEC + "bake + GLB\n"), globals())

# prozori: atribut "_wake" po prozoru (udaljenost od vrata pekare, 0-1) i svojstvo "wake" po kuci.
# U renderu isti atribut pali prozore (prag), kao uniforma u shaderu sajta.
TAMNO = M["staklo_tamno"]


def prozori_ob():
    return [ob for ob in scene.objects if ob.type == "MESH" and TAMNO.name in [m.name for m in ob.data.materials if m]]


wins = {}
for ob in prozori_ob():
    me = ob.data
    ti = [i for i, m in enumerate(me.materials) if m == TAMNO]
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    mw = ob.matrix_world
    wins[ob.name] = []
    for isl in otoci(bm):
        if isl[0].material_index not in ti:
            continue
        vs = {v.index for f in isl for v in f.verts}
        c = sum((mw @ bm.verts[i].co for i in vs), Vector()) / len(vs)
        wins[ob.name].append((vs, c))
    bm.free()
DMAX = max((c - ORIGIN).length for lst in wins.values() for _, c in lst)
for name, lst in wins.items():
    me = bpy.data.objects[name].data
    at = me.attributes.get("_wake") or me.attributes.new("_wake", "FLOAT", "POINT")
    vals = [0.0] * len(me.vertices)
    ws = []
    for vs, c in lst:
        w = round((c - ORIGIN).length / DMAX, 4)
        ws.append(w)
        for i in vs:
            vals[i] = w
    at.data.foreach_set("value", vals)
    bpy.data.objects[name]["wake"] = round(sum(ws) / len(ws), 4) if ws else 0.0
    bpy.data.objects[name]["prozora"] = len(ws)

nt = TAMNO.node_tree
pb = nt.nodes["Principled BSDF"]
at_n = nt.nodes.new("ShaderNodeAttribute")
at_n.attribute_name = "_wake"
prag = nt.nodes.new("ShaderNodeValue")
prag.name = "prag"
prag.outputs[0].default_value = -1.0          # -1: svi ugaseni (noc)
lt_n = nt.nodes.new("ShaderNodeMath")
lt_n.operation = "LESS_THAN"
nt.links.new(at_n.outputs["Fac"], lt_n.inputs[0])
nt.links.new(prag.outputs[0], lt_n.inputs[1])
mul = nt.nodes.new("ShaderNodeMath")
mul.operation = "MULTIPLY"
mul.inputs[1].default_value = 2.2
nt.links.new(lt_n.outputs[0], mul.inputs[0])
nt.links.new(mul.outputs[0], pb.inputs["Emission Strength"])
pb.inputs["Emission Color"].default_value = hexc("#ffc27e")

# ---------------------------------------------------------------- put kamere, ciljevi, poglavlja
# Pogl_N: kadar poglavlja (tacka na krivoj); Cilj_N: gde kamera gleda. Svojstva na Pogl_N:
# udeo/udeo_kraj (mapa skrola), t (0-1 po duzini krive), lens (mm, senzor 36 mm po duzoj strani),
# shift_x/shift_y (pomak kadra kao u Blenderu, deo duze strane: + pomera kadar desno/gore, sadrzaj ide suprotno),
# tekst (strana za HTML na desktopu), tel_* (telefon 9:16: tel_cilj, tel_blize = deo rastojanja, tel_shift_y).
VP = Vector((-1.0, -1.15, 0.8)).normalized()
C1 = Vector((CX, CY, 2.0))
POGL = [
    dict(n=1, p=C1 + VP * 128, c=C1, lens=50, sx=-0.12, sy=0.02, udeo=(0.0, 0.09), tekst="L-dole",
         tel_cilj=(6.0, 5.5, 7.0), tel_blize=0.62, tel_sy=-0.1),
    dict(n=2, p=Vector((-12.0, 36.0, 31.0)), c=Vector((4.0, 4.0, 9.0)), lens=30, sx=-0.08, sy=0.0, udeo=(0.09, 0.25),
         tekst="D-sredina", tel_cilj=(4.0, 4.0, 12.0), tel_blize=1.0, tel_sy=-0.08),
    dict(n=3, p=Vector((15.0, -8.0, 2.0)), c=Vector((4.0, -1.0, 3.6)), lens=26, sx=-0.1, sy=0.0,
         udeo=(0.25, 0.42), tekst="L", tel_cilj=(2.5, -0.5, 3.8), tel_blize=1.0, tel_sy=-0.12),
    # fix A: tel_cilj je pomak cilja za ceo kadar 0,25-0,39 (i za presek na kraju), ne samo za ugao fasade
    # 4 i 5 (i stanica "Ofen") prepisani iz enterijer.blend (Stanica_4, Stanica_5, Kadar_pec, 27. 10.);
    # bake_izvoz.py ih pri pravljenju kamera.json uvek cita ponovo iz enterijer.blend
    dict(n=4, p=Vector((5.75, 0.55, 1.95)), c=Vector((6.25, 3.05, 1.0)), lens=30,
         sx=0.0, sy=0.0, udeo=(0.42, 0.60), tekst="L/D/L po stanici", tel_cilj=(6.1, 3.0, 1.0), tel_blize=1.0, tel_sy=-0.08),
    dict(n=5, p=Vector((3.0, 0.85, 1.6)), c=Vector((3.2, 3.6, 1.12)), lens=32, sx=0.0, sy=0.04, udeo=(0.60, 0.72),
         tekst="G-L", tel_cilj=(3.21, 3.55, 1.1), tel_blize=0.7, tel_sy=-0.1),
    dict(n=6, p=Vector((CX + 1, CY, 3.0)) + Vector((-0.8, -1.2, 0.85)).normalized() * 102, c=Vector((CX + 1, CY, 3.0)),
         lens=50, sx=-0.05, sy=-0.05, udeo=(0.72, 0.88), tekst="L-sredina; D-dole", tel_cilj=(5.0, 5.0, 7.0),
         tel_blize=0.6, tel_sy=-0.1),
    dict(n=7, p=Vector((CX, CY, 2.0)) + Vector((-0.9, -1.0, 1.3)).normalized() * 125, c=Vector((CX, CY, 2.0)), lens=50,
         sx=0.0, sy=0.0, udeo=(0.88, 1.0), tekst="S (forma)", tel_cilj=(6.0, 6.0, 6.0), tel_blize=0.65, tel_sy=-0.06),
]
P = {d["n"]: d["p"] for d in POGL}
# stanice poglavlja 4 posle prve (sto): korpe na polici, pa vrata peci; (ime, polozaj, cilj, lens)
STANICE_4 = [("Zeit", Vector((4.0, 5.0, 1.75)), Vector((4.0, 8.1, 1.35)), 28),
             ("Ofen", Vector((7.875, 2.65, 1.58)), Vector((8.8, 5.25, 1.09)), 30)]
VRATA_P = Vector((UG_C / 2, UG_C / 2, 0)) + N_UG * 2.3 + Vector((0, 0, 2.3))    # ispred vrata, pre ulaska
# medjutacke: let do zapada, klizanje nad mansardama B-reda, spustanje u ulicu, ispred vrata kad je Kriska spustena,
# stanice u pekari, pa nazad ispred izloga
# pogl. 2 (talas 3): let ide sirokim lukom nad zapadnom i juznom ulicom (ne tik uz fasadu ugla), da se vide
# ulica, lampe i tramvaj; isti brojevi su u bake_izvoz.py (KRIVA_POGL_2) za popravku krive u kvart.blend
PUT = [P[1], Vector((-62.0, -8.0, 50.0)), Vector((-22.0, 46.0, 30.0)), P[2], Vector((-30.0, 18.0, 25.0)),
       Vector((-28.0, -22.0, 15.0)), Vector((4.0, -21.0, 7.0)), P[3], P[3].lerp(VRATA_P, 0.5) + Vector((0, 0, 0.4)), VRATA_P,
       P[4], STANICE_4[0][1], STANICE_4[1][1], Vector((5.6, 0.6, 1.6)), P[5], Vector((6.0, -10.5, 7.5)),
       Vector((-4.0, -32.0, 24.0)), P[6], Vector((-75.0, -70.0, 85.0)), P[7]]
cu = bpy.data.curves.new("KameraPut", "CURVE")
cu.dimensions = "3D"
cu.resolution_u = 24
sp = cu.splines.new("BEZIER")
sp.bezier_points.add(len(PUT) - 1)
for bp, co in zip(sp.bezier_points, PUT):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = "AUTO"
put = bpy.data.objects.new("KameraPut", cu)
scene.collection.objects.link(put)
dg = bpy.context.evaluated_depsgraph_get()
pm = put.evaluated_get(dg).to_mesh()
pts = [v.co.copy() for v in pm.vertices]
put.evaluated_get(dg).to_mesh_clear()
cum = [0.0]
for a, b in zip(pts, pts[1:]):
    cum.append(cum[-1] + (b - a).length)
put["duzina_m"] = round(cum[-1], 2)
put["opis"] = "Bezier, AUTO rucke; Pogl_N leze na krivoj, t = udeo duzine krive"

pogl_obs, cilj_obs = [], []
for d in POGL:
    n = d["n"]
    k = min(range(len(pts)), key=lambda i: (pts[i] - d["p"]).length)
    pe = bpy.data.objects.new(f"Pogl_{n}", None)
    pe.empty_display_type = "SPHERE"
    pe.empty_display_size = 0.8
    pe.location = d["p"]
    pe["t"] = round(cum[k] / cum[-1], 4)
    pe["udeo"], pe["udeo_kraj"] = d["udeo"]
    pe["lens"] = d["lens"]
    pe["shift_x"], pe["shift_y"] = d["sx"], d["sy"]
    pe["tekst"] = d["tekst"]
    pe["tel_cilj"] = list(d["tel_cilj"])
    pe["tel_blize"] = d["tel_blize"]
    pe["tel_shift_y"] = d["tel_sy"]
    pe["tel_tekst"] = "dole (donja trecina)"
    ce = bpy.data.objects.new(f"Cilj_{n}", None)
    ce.empty_display_type = "PLAIN_AXES"
    ce.location = d["c"]
    for ob in (pe, ce):
        scene.collection.objects.link(ob)
    pogl_obs.append(pe)
    cilj_obs.append(ce)
for ime, p_, c_, ln in STANICE_4:                 # Pogl_4_Zeit, Cilj_4_Zeit, ...
    pe = bpy.data.objects.new(f"Pogl_4_{ime}", None)
    pe.empty_display_type = "SPHERE"
    pe.empty_display_size = 0.4
    pe.location = p_
    k = min(range(len(pts)), key=lambda i: (pts[i] - p_).length)
    pe["t"] = round(cum[k] / cum[-1], 4)
    pe["lens"] = ln
    ce = bpy.data.objects.new(f"Cilj_4_{ime}", None)
    ce.empty_display_type = "PLAIN_AXES"
    ce.location = c_
    for ob in (pe, ce):
        scene.collection.objects.link(ob)

cd = bpy.data.cameras.new("Kamera")
cd.clip_end = 600
kam = bpy.data.objects.new("Kamera", cd)
scene.collection.objects.link(kam)
scene.camera = kam

# ---------------------------------------------------------------- kolekcije
KOL = {}


def u_kol(ob, name):
    if name not in KOL:
        KOL[name] = bpy.data.collections.new(name)
        scene.collection.children.link(KOL[name])
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    KOL[name].objects.link(ob)


for ob in list(scene.objects):
    nm = ob.name
    if ob.type == "LIGHT":
        if ob.parent is None:
            u_kol(ob, "Svetla")
    elif nm.startswith(("Kriska", "Pekara_otvor")):
        u_kol(ob, "Kriska")
    elif nm.startswith("Rez_") or nm.endswith(("_cut_up", "_cut_gf")):
        u_kol(ob, "Rezaci")
    elif nm.startswith(("Ugao", "A1", "A2", "A3", "B1", "B2", "B3")):
        u_kol(ob, "Blok")
    elif nm.startswith(("NS", "NZ", "NU")):
        u_kol(ob, "Naspram")
    elif nm.startswith("Tramvaj"):
        u_kol(ob, "Tramvaj")
    elif nm.startswith("Lampa"):
        u_kol(ob, "Lampe")
    elif nm.startswith("Figura"):
        u_kol(ob, "Figure")
    elif nm.startswith("Drvo"):
        u_kol(ob, "Drvece")
    elif nm.startswith("Dim"):
        u_kol(ob, "Dim")
    elif nm.startswith(("KameraPut", "Pogl_", "Cilj_", "Kamera")):
        u_kol(ob, "Kamera")
    else:
        u_kol(ob, "Ulica")
for ob in list(scene.objects):          # svetla sa roditeljem (lampe, table) prate roditelja
    if ob.type == "LIGHT" and ob.parent is not None:
        u_kol(ob, ob.parent.users_collection[0].name)
KOL["Rezaci"].hide_render = True


# ---------------------------------------------------------------- trouglovi
def tris(obs):
    dg = bpy.context.evaluated_depsgraph_get()
    n = 0
    for ob in obs:
        if ob.type != "MESH":
            continue
        me = ob.evaluated_get(dg).to_mesh()
        me.calc_loop_triangles()
        n += len(me.loop_triangles)
        ob.evaluated_get(dg).to_mesh_clear()
    return n


vis = [o for o in scene.objects if o.type == "MESH" and not o.hide_render and o.users_collection[0].name != "Rezaci"]
TRIS = {
    "kvart ukupno": tris(vis),
    "ugaona kuca (bez Kriske)": tris([o for o in KOL["Blok"].objects if o.name.startswith("Ugao")]),
    "Kriska (+staklo)": tris([kriska, kriska_staklo]),
}
for c in ("Blok", "Naspram", "Ulica", "Tramvaj", "Lampe", "Figure", "Drvece", "Dim"):
    TRIS[c] = tris([o for o in KOL[c].objects if not o.hide_render])
print("TRIS", TRIS)
print(f"GRADNJA: {time.time() - T0:.1f} s")

scene.frame_set(1)
bpy.context.preferences.filepaths.save_version = 0      # bez kvart.blend1 pored fajla
if not WEB:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kvart.blend"))


# ---------------------------------------------------------------- renderi
def stanje(lampe_on, prag_v, tram_on, frame):
    for lt in lampe_svetla:
        lt.hide_render = not lampe_on
    M["lampa"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0 if lampe_on else 0.0
    prag.outputs[0].default_value = prag_v
    tram.hide_render = not tram_on
    scene.frame_set(frame)


def kadar(n, tel=False, fstop=None):
    d = POGL[n - 1]
    pe, ce = pogl_obs[n - 1], cilj_obs[n - 1]
    c = Vector(pe["tel_cilj"]) if tel else ce.location.copy()
    loc = c + (pe.location - ce.location) * (pe["tel_blize"] if tel else 1.0)
    kam.location = loc
    kam.rotation_euler = (c - loc).to_track_quat("-Z", "Y").to_euler()
    cd.lens = d["lens"]
    cd.sensor_fit = "AUTO"
    cd.shift_x = 0.0 if tel else pe["shift_x"]
    cd.shift_y = pe["tel_shift_y"] if tel else pe["shift_y"]
    cd.dof.use_dof = fstop is not None
    if fstop:
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = (Vector((UG_C / 2, UG_C / 2, 4.0)) - loc).length
    scene.render.resolution_x, scene.render.resolution_y = (900, 1600) if tel else (1600, 1000)


SHOTS = [
    ("1", "kvart-1440.png", lambda: (stanje(False, -1.0, False, 1), kadar(1, fstop=0.04))),
    ("916", "kvart-916.png", lambda: (stanje(False, -1.0, False, 1), kadar(1, tel=True, fstop=0.03))),
    ("3", "kvart-pogl-3.png", lambda: (stanje(True, -1.0, False, 40), kadar(3))),
    ("6", "kvart-pogl-6.png", lambda: (stanje(False, 0.5, True, 1), kadar(6, fstop=0.04))),
]
# probni kadrovi ostalih poglavlja (samo kad se traze, npr. "-- p2 p4"), sa KRUME_PREFIX van repoa
for n, fr, lamp in ((2, 1, True), (4, 70, True), (5, 1, True), (7, 1, False)):
    SHOTS.append((f"p{n}", f"kvart-pogl-{n}.png", lambda n=n, fr=fr, lamp=lamp: (stanje(lamp, -1.0, n == 2, fr), kadar(n))))
    SHOTS.append((f"t{n}", f"kvart-pogl-{n}-916.png", lambda n=n, fr=fr, lamp=lamp: (stanje(lamp, -1.0, n == 2, fr), kadar(n, tel=True))))
if "norender" not in ARGS and not WEB:
    for tag, fn, setup in SHOTS:
        if (ARGS and tag not in ARGS) or (not ARGS and tag[0] in "pt"):
            continue
        setup()
        scene.render.filepath = os.path.join(HERE, os.environ.get("KRUME_PREFIX", "") + fn)
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"RENDER {fn}: {time.time() - t:.1f} s")
    stanje(False, -1.0, True, 1)
    kadar(1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kvart.blend"))
