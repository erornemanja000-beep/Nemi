# Krume: bake i izvoz enterijera (poglavlja 3-5) u glTF za sajt (pekara/, three r186).
# Ulaz: enterijer.blend (iz enterijer.py). Izlaz:
#   pekara/public/models/enterijer.glb        tri albedo atlasa 2048 (WebP u GLB-u), Draco
#   pekara/public/models/enterijer-m.glb      isti atlasi za telefon (vidi ATLAS_M), Draco, najvise 1,3 MB
#   Atlasi (svaki je svoj materijal u GLB-u, svi na TEXCOORD_0 i dele jedan lightmap):
#     Enterijer        zidovi, pod, namestaj (glavni)
#     Enterijer_hleb   hlebovi, testo, korpe: junaci poglavlja 4 i 5, kamera im prilazi na desetak cm
#     Enterijer_pec    vrata peci, gvozdje, cepanice, lopata; Enterijer_zar (emisija) uzima isti atlas
#   pekara/public/textures/enterijer-noc-0.webp     nocni lightmap 2048 (drugi UV set "lightmap" = TEXCOORD_1)
#   pekara/public/textures/enterijer-noc-0-m.webp   isti lightmap 1024
#   studio/pekara/blender/bake/enterijer-noc-provera.png   kadar preseka sa primenjenim lightmap-om (kao na sajtu)
# Samo nocni lightmap: enterijer se vidi samo noću. Albedo (boja materijala, bez svetla) je u atlasu na UV 0,
# svetlo je u lightmap-u na UV 1. Na sajtu: boja = albedo * lightmap (bez tone mappinga), vidi format ispod.
#
# FORMAT (isti kao grad iz bake_izvoz.py, programer A, da motor ima jedan put):
#   albedo: baseColorTexture u GLB-u, UV "albedo" = TEXCOORD_0
#   lightmap: UV "lightmap" = TEXCOORD_1, fajl textures/enterijer-noc-0.webp (telefon: enterijer-noc-0-m.webp),
#     Non-Color WebP, flipY = false; kodiranje enc = (L / noc_max) ^ (1 / 4), pa je svetlo L = noc_max * texel ^ 4
#   gltf.scene.userData.krume = {noc_max, lightmap_gamma: 4, ...} (extras scene)
#   piksel = albedo * L (sirovo svetlo iz Cycles DIFFUSE bake-a, direktno + indirektno, bez boje)
#   Emisija (Zar, Lampa_sijalica): emissiveTexture/emissiveFactor + KHR_materials_emissive_strength, bez lightmap-a.
#
# Pokretanje:
#   Blender -b -P bake_enterijer.py                 (pun bake, izvoz, provera)
#   Blender -b -P bake_enterijer.py -- brzo         (malo uzoraka, za probu)
# Okruzenje: KRUME_BAKE_SAMPLES (podrazumevano 256). Veliki EXR iz bake/ se brisu na kraju (KRUME_CUVAJ=1 ih ostavlja).

import bpy, bmesh, math, os, sys, time
import numpy as np
from mathutils import Vector

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODELS = os.path.join(ROOT, "pekara", "public", "models")
TEX = os.path.join(ROOT, "pekara", "public", "textures")
BAKE = os.path.join(HERE, "bake")
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
BRZO = "brzo" in ARGS
SAMPLES = int(os.environ.get("KRUME_BAKE_SAMPLES", "48" if BRZO else "256"))
ATLAS, LM = 2048, 2048
ATLAS_M = {"glavni": 1024, "hleb": 2048, "pec": 1024}   # telefon: hleb ostaje 2048 (mak i so izbliza)
MB_M = 1.3e6                                             # granica za enterijer-m.glb (bajtova)
LM_GAMMA = 4.0                       # kao bake_izvoz.py: enc = (L / max) ^ (1 / LM_GAMMA)
EMISIJA = 1.8                        # = EMISSIVE_MAX u pekara/src/scene/renderer.js
for d in (MODELS, TEX, BAKE):
    os.makedirs(d, exist_ok=True)

# mere kao u enterijer.py (granice otvora iz kvart.blend)
X_OUT, Y_OUT, Z_TOP, Z_BOT = 11.3, 8.7, 8.1, -0.1
X_PREG, Y_ZAD, POD = 11.0, 8.4, 0.12

bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "enterijer.blend"))
scene = bpy.context.scene
vl = bpy.context.view_layer
scene.frame_set(1)                   # vrata peci zatvorena, testo i korpe u osnovnom obliku
C_ENT = bpy.data.collections["Enterijer"]
KOREN = bpy.data.objects["Enterijer_koren"]
for ob in bpy.data.objects:
    if ob.type == "MESH" and ob.data.shape_keys:
        for kb in ob.data.shape_keys.key_blocks[1:]:
            kb.value = 0.0
# za bake svetle samo svetla enterijera i nebo; pomocno (trotoar, stona lampa makete, rezaci) se gasi
for ob in bpy.data.objects:
    if ob.name not in C_ENT.all_objects:
        ob.hide_render = True

OBJS = [o for o in C_ENT.all_objects if o.type == "MESH"]


def grupa(n):
    """Kom albedo atlasu objekat pripada."""
    if n.startswith(("Hleb_", "Korpa", "Platno_vekne", "Izlog_hlebovi", "Vitrina_hlebovi")) or n == "Testo":
        return "hleb"
    if n in ("PecVrata", "Cepanice", "Zar", "Pec_gvozdje", "Pec_sarke", "Lopata"):
        return "pec"
    return "glavni"


GRUPE = ("glavni", "hleb", "pec")
STAKLO = [o for o in OBJS if o.name == "Vitrina_staklo"]
EMIT = {"Zar": "zar", "Lampa_sijalica": "sijalica"}
BAKE_OBJS = [o for o in OBJS if o not in STAKLO]
print("objekata za izvoz", len(OBJS))

# ---------------------------------------------------------------- 1. modifikatori u mesh, skrivena lica napolje
dg = bpy.context.evaluated_depsgraph_get()
for o in OBJS:
    if o.modifiers and not o.data.shape_keys:
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        old = o.data
        o.modifiers.clear()
        o.data = me
        me.name = o.name
        if old.users == 0:
            bpy.data.meshes.remove(old)


def skriveno(c, n):
    """Lica koja se nikad ne vide: uz kvart (spolja), ispod poda, ispod namestaja na podu, uz zidove."""
    return ((n.x > 0.98 and c.x > X_OUT - 0.01) or (n.y > 0.98 and c.y > Y_OUT - 0.01) or
            (n.z < -0.98 and c.z < Z_BOT + 0.01) or (n.z > 0.98 and c.z > Z_TOP - 0.01) or
            (n.z < -0.98 and abs(c.z - POD) < 0.004) or
            (n.y > 0.98 and abs(c.y - Y_ZAD) < 0.004) or (n.x > 0.98 and abs(c.x - X_PREG) < 0.004))


n_del = 0
for o in OBJS:
    if o.data.shape_keys:
        continue
    bm = bmesh.new()
    bm.from_mesh(o.data)
    mw = o.matrix_world
    rot = mw.to_3x3().normalized()
    dead = [f for f in bm.faces if skriveno(mw @ f.calc_center_median(), (rot @ f.normal).normalized())]
    n_del += len(dead)
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    # tanke trake iz boolean-a (pec): smart_project ih razvije u ostrvo bez povrsine, average_islands_scale
    # ga razvuce na stotine jedinica i pack_islands onda sabije sve ostalo u liniju
    bmesh.ops.dissolve_degenerate(bm, dist=1e-4, edges=bm.edges[:])
    sliv = [f for f in bm.faces if f.calc_area() < 1e-7]
    n_del += len(sliv)
    bmesh.ops.delete(bm, geom=sliv, context="FACES")
    bm.to_mesh(o.data)
    bm.free()
print("skrivenih lica obrisano", n_del)

# ---------------------------------------------------------------- 2. UV: atlas (UVMap) i lightmap
# Tezine: koliko je objekat vazan u kadru (gustina teksela u odnosu na ostale u istom atlasu).
def tezina_atlas(n):
    g = grupa(n)
    if g == "hleb":
        if n.startswith("Hleb_") or n == "Testo":
            return 1.0
        if n in ("Korpa_testo_7", "Korpa_testo_8"):           # na stolu, uz testo
            return 0.5
        if n in ("Korpa_7", "Korpa_8"):
            return 0.35
        if n.startswith("Korpa_testo"):
            return 0.25
        if n.startswith("Korpa_prazna"):
            return 0.05
        if n.startswith("Korpa"):
            return 0.12
        if n == "Vitrina_hlebovi":                            # u telu pulta, jedva se vidi
            return 0.01
        return 0.15
    if g == "pec":
        return {"PecVrata": 1.0, "Cepanice": 0.8, "Zar": 0.6, "Pec_gvozdje": 0.4, "Pec_sarke": 0.5}.get(n, 0.3)
    if n.startswith(("Pult", "Sto_ploca")):
        return 3.0
    if n in ("Platno", "Pec_pod", "Brasno", "Alat", "Kasa", "Zdela"):
        return 1.6
    if n == "Pec":
        return 1.3
    if n.startswith("Magacin") or n in ("Zidovi", "Plafon"):
        return 0.3
    if n in ("Pod",):
        return 0.6
    if n == "Vitrina_staklo":
        return 0.05
    return 1.0


def tezina_lm(n):
    if n in ("Zar", "Lampa_sijalica", "Vitrina_staklo"):
        return 0.1
    if n in ("Testo",) or n.startswith("Hleb_"):
        return 25.0                     # junaci poglavlja 4 i 5, kamera im prilazi blizu (sitni su, malo kostaju)
    if n.startswith("Korpa_testo") or n in ("Zdela", "Brasno", "Alat", "Kasa", "PecVrata"):
        return 4.0                      # mala obla tela: bez dovoljno teksela se vide stepenici na rubovima ostrva
    if n.startswith(("Korpa", "Platno", "Izlog_hlebovi", "Vitrina_hlebovi", "Lampa")):
        return 2.0
    if n.startswith("Magacin"):
        return 0.6
    return 1.0


def uv_platno(o, layer):
    """Platno sa naborima: smart project ga iscepka na stotine ostrva (izgleda pocepano). Ovde je razvijeno
    rucno: u = x, v = put niz platno (preko daske pa niz prednju ivicu); gornja i donja strana su dva ostrva."""
    me = o.data
    mw = o.matrix_world
    rot = mw.to_3x3().normalized()
    uv = me.uv_layers[layer].uv
    for poly in me.polygons:
        n = rot @ poly.normal
        gore = n.z > 0.2 or n.y < -0.5
        for li in poly.loop_indices:
            c = mw @ me.vertices[me.loops[li].vertex_index].co
            uv[li].vector = (c.x, (8.4 - c.y) + (1.15 - c.z) + (0.0 if gore else 1.2))


RUCNO = {"Platno": uv_platno}


def uv_povrsina(objs, layer):
    """Zbir povrsina UV lica (udeo kvadrata 0-1)."""
    t = 0.0
    for o in objs:
        me = o.data
        uv = np.empty(len(me.loops) * 2, dtype=np.float64)
        me.uv_layers[layer].uv.foreach_get("vector", uv)
        uv = uv.reshape(-1, 2)
        for p in me.polygons:
            q = uv[p.loop_start:p.loop_start + p.loop_total]
            t += abs(np.dot(q[:, 0], np.roll(q[:, 1], -1)) - np.dot(q[:, 1], np.roll(q[:, 0], -1))) / 2
    return t


def napravi_uv(layer, tezina, margin, objs=None):
    """objs: objekti koji se pakuju zajedno u isti 0-1 kvadrat (jedan atlas)."""
    objs = objs or OBJS
    for o in OBJS:
        o.data.uv_layers.active = o.data.uv_layers[layer]
    bpy.ops.object.select_all(action="DESELECT")
    auto = [o for o in objs if o.name not in RUCNO]
    bpy.ops.object.select_all(action="DESELECT")
    for o in auto:
        o.select_set(True)
    vl.objects.active = auto[0]
    scene.tool_settings.use_uv_select_sync = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action="SELECT")
    # 62 stepena: sa 66 u Blenderu 5.2 pack_islands posle ne radi nista (ostrva ostanu sitna u uglu)
    bpy.ops.uv.smart_project(angle_limit=math.radians(62), island_margin=0.0, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objs:
        if o.name in RUCNO:
            RUCNO[o.name](o, layer)
            o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.average_islands_scale()
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in objs:
        w = math.sqrt(tezina(o.name))
        uv = o.data.uv_layers[layer].uv
        a = np.empty(len(uv) * 2, dtype=np.float32)
        uv.foreach_get("vector", a)
        uv.foreach_set("vector", a * w)
    # pack_islands u Blenderu 5.x ponekad ne uradi nista (ostrva ostanu sitna u uglu, zavisi od geometrije):
    # posle pakovanja se meri obuhvat, pa se po potrebi ponavlja sa drugim podesavanjima.
    for kw in (dict(rotate=True, shape_method="CONCAVE"), dict(rotate=True, shape_method="CONVEX"),
               dict(rotate=False, shape_method="CONCAVE"), dict(rotate=True, shape_method="AABB")):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.pack_islands(scale=True, margin_method="FRACTION", margin=margin, **kw)
        bpy.ops.object.mode_set(mode="OBJECT")
        pok = uv_povrsina(objs, layer)
        print(f"pack {layer} ({len(objs)} obj, {kw}): pokriveno {pok:.2f}")
        if pok > 0.3:
            break
    else:
        raise RuntimeError(f"pack_islands nije spakovao {layer}")


for o in OBJS:
    me = o.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="albedo")
    me.uv_layers.new(name="lightmap")
def pokrivenost(layer, objs=None, ime=""):
    """Udeo UV kvadrata pod ostrvima i gustina teksela (px/m na 2048) za nekoliko objekata."""
    uk, gus = 0.0, {}
    for o in objs or OBJS:
        me = o.data
        uv = np.empty(len(me.loops) * 2, dtype=np.float64)
        me.uv_layers[layer].uv.foreach_get("vector", uv)
        uv = uv.reshape(-1, 2)
        a2 = 0.0
        for p in me.polygons:
            q = uv[p.loop_start:p.loop_start + p.loop_total]
            a2 += abs(np.dot(q[:, 0], np.roll(q[:, 1], -1)) - np.dot(q[:, 1], np.roll(q[:, 0], -1))) / 2
        uk += a2
        if o.name in ("Pod", "Testo", "Zidovi", "Hleb_1", "Hleb_2", "Pult_ploca", "PecVrata", "Cepanice", "Zar", "Korpa_testo_7"):
            a3 = sum(p.area for p in me.polygons)
            gus[o.name] = round(math.sqrt(a2 / a3) * 2048) if a3 else 0
    print(f"UV {layer} {ime}: pokriveno {uk:.2f}, px/m (2048) {gus}")


t = time.time()
GOBJ = {g: [o for o in OBJS if grupa(o.name) == g] for g in GRUPE}
for g in GRUPE:
    napravi_uv("albedo", tezina_atlas, 0.002, GOBJ[g])
napravi_uv("lightmap", tezina_lm, 0.003)
for o in OBJS:
    o.data.uv_layers["albedo"].active = True
    o.data.uv_layers["albedo"].active_render = True
print(f"UV gotovo: {time.time() - t:.1f} s")
for g in GRUPE:
    pokrivenost("albedo", GOBJ[g], g)
pokrivenost("lightmap")
if "samo_uv" in ARGS:
    sys.exit(0)

# ---------------------------------------------------------------- 3. Cycles za bake
scene.render.engine = "CYCLES"
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
cy.use_adaptive_sampling = False
cy.use_denoising = False
cy.max_bounces = 6
cy.sample_clamp_indirect = 4.0
# Margina bake-a mora biti manja od pola razmaka ostrva: Blender je pise po objektu i prepisuje
# susedna ostrva drugih objekata (crne mrlje). Razmak: atlas 0,002 * 2048 = 4 px, lightmap 0,003 * 2048 = 6 px.
scene.render.bake.margin = 2
scene.render.bake.margin_type = "EXTEND"


def novi_img(name, size, float_buf=False, colorspace="sRGB"):
    old = bpy.data.images.get(name)
    if old:
        bpy.data.images.remove(old)
    img = bpy.data.images.new(name, size, size, alpha=False, float_buffer=float_buf)
    img.colorspace_settings.name = colorspace
    return img


def principled(m):
    if not m.use_nodes:
        return None
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def izlaz(nt):
    outs = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"]
    for n in outs:
        if n.is_active_output:
            return n
    return outs[0]


def bake_select(objs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]


# ---------------------------------------------------------------- 4. albedo atlas (EMIT bake boje materijala)
orig = {o.name: [s.material for s in o.material_slots] for o in OBJS}
alb = {}
IMG = {g: novi_img("enterijer_" + ("atlas" if g == "glavni" else g), ATLAS) for g in GRUPE}
img_atlas = IMG["glavni"]
for o in BAKE_OBJS:
    g = grupa(o.name)
    for s in o.material_slots:
        m = s.material
        if m is None or (m.name, g) in alb:
            continue
        a = m.copy()
        a.name = m.name + "__albedo_" + g
        nt = a.node_tree
        p = principled(a)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Strength"].default_value = 1.0
        if p is None:
            em.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
        else:
            sock = p.inputs["Emission Color"] if o.name in EMIT else p.inputs["Base Color"]
            if sock.is_linked:
                nt.links.new(sock.links[0].from_socket, em.inputs["Color"])
            else:
                em.inputs["Color"].default_value = sock.default_value
        nt.links.new(em.outputs["Emission"], izlaz(nt).inputs["Surface"])
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = IMG[g]
        nt.nodes.active = tx
        alb[(m.name, g)] = a
for o in BAKE_OBJS:
    for s in o.material_slots:
        if s.material:
            s.material = alb[(s.material.name, grupa(o.name))]
bake_select(BAKE_OBJS)
cy.samples = 4 if BRZO else 32                   # antialiasing teksela (mak, godovi) i sum Bevel cvora gvozdja
t = time.time()
bpy.ops.object.bake(type="EMIT", uv_layer="albedo", margin=2, use_clear=True, target="IMAGE_TEXTURES")
print(f"BAKE atlasi {ATLAS}: {time.time() - t:.1f} s")
for g, img in IMG.items():
    img.filepath_raw = os.path.join(BAKE, f"enterijer-{'atlas' if g == 'glavni' else g}.png")
    img.file_format = "PNG"
    img.save()
for o in BAKE_OBJS:
    for s, m in zip(o.material_slots, orig[o.name]):
        s.material = m

# ---------------------------------------------------------------- 5. nocni lightmap (DIFFUSE: direktno + indirektno, bez boje)
img_lm = novi_img("enterijer_lm", LM, float_buf=True, colorspace="Linear Rec.709")
LM_OBJS = [o for o in BAKE_OBJS if o.name not in EMIT]
lm_nodes = []
for m in {m for o in LM_OBJS for m in orig[o.name] if m}:
    nt = m.node_tree
    tx = nt.nodes.new("ShaderNodeTexImage")
    tx.image = img_lm
    nt.nodes.active = tx
    lm_nodes.append((nt, tx))
# DIFFUSE prolaz vidi samo difuzni deo: metal, subsurface i providnost bi ostali crni ili tamniji u lightmap-u.
# Za bake su privremeno nula (albedo ih vec nosi), posle se vraca.
vrati = []
for m in {m for o in LM_OBJS for m in orig[o.name] if m}:
    p = principled(m)
    if p is None:
        continue
    for k in ("Metallic", "Subsurface Weight", "Transmission Weight"):
        if not p.inputs[k].is_linked and p.inputs[k].default_value:
            vrati.append((p.inputs[k], p.inputs[k].default_value))
            p.inputs[k].default_value = 0.0
bake_select(LM_OBJS)
cy.samples = SAMPLES
t = time.time()
bpy.ops.object.bake(type="DIFFUSE", pass_filter={"DIRECT", "INDIRECT"}, uv_layer="lightmap", margin=3,
                    use_clear=True, target="IMAGE_TEXTURES")
print(f"BAKE lightmap {LM} ({SAMPLES} uzoraka): {time.time() - t:.1f} s")
for nt, tx in lm_nodes:
    nt.nodes.remove(tx)
for sock, v in vrati:
    sock.default_value = v
img_lm.filepath_raw = os.path.join(BAKE, "enterijer-noc-sirov.exr")
img_lm.file_format = "OPEN_EXR"
img_lm.save()


def denoise(img):
    """OIDN iz kompozitora na praznoj sceni (Workbench, bez objekata): Image -> Denoise -> izlaz."""
    sc = bpy.data.scenes.new("Denoise")
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = img.size
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    sc.sequencer_colorspace_settings.name = "Linear Rec.709"
    ng = bpy.data.node_groups.new("Denoise_lm", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    ni = ng.nodes.new("CompositorNodeImage")
    ni.image = img
    dn = ng.nodes.new("CompositorNodeDenoise")
    for k in ("HDR",):
        if k in dn.inputs:
            dn.inputs[k].default_value = True
    out = ng.nodes.new("NodeGroupOutput")
    ng.links.new(ni.outputs["Image"], dn.inputs["Image"])
    ng.links.new(dn.outputs["Image"], out.inputs[0])
    sc.compositing_node_group = ng
    path = os.path.join(BAKE, "enterijer-noc-denoise.exr")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True, scene=sc.name)
    res = bpy.data.images.load(path, check_existing=False)
    res.colorspace_settings.name = "Linear Rec.709"
    a = np.empty(res.size[0] * res.size[1] * 4, dtype=np.float32)
    res.pixels.foreach_get(a)
    bpy.data.images.remove(res)
    bpy.data.scenes.remove(sc)
    return a.reshape(img.size[1], img.size[0], 4)


raw = np.empty(LM * LM * 4, dtype=np.float32)
img_lm.pixels.foreach_get(raw)
raw = raw.reshape(LM, LM, 4)
try:
    t = time.time()
    lm = denoise(img_lm)
    print(f"denoise: {time.time() - t:.1f} s")
    if not np.isfinite(lm).all() or lm[..., :3].max() <= 0:
        raise RuntimeError("denoise je vratio prazno")
except Exception as e:
    print("Denoise nije uspeo, ide sirov lightmap:", e)
    lm = raw


def snimi_webp(arr, path, q):
    """arr: (H, W, 3) vec kodirano 0-1; upis bez konverzije boje (Non-Color), kao upisi_webp u bake_izvoz.py."""
    h, w = arr.shape[:2]
    out = np.ones((h, w, 4), dtype=np.float32)
    out[..., :3] = arr
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    img.pixels.foreach_set(out.ravel())
    img.file_format = "WEBP"
    img.save(filepath=path, quality=q)
    bpy.data.images.remove(img)
    return os.path.getsize(path)


L = np.maximum(lm[..., :3], 0.0)
lum = L.max(axis=2)
NOC_MAX = float(np.percentile(lum[lum > 1e-5], 99.7))
enc = np.power(np.clip(L / NOC_MAX, 0, 1), 1 / LM_GAMMA)
enc_m = enc.reshape(LM // 2, 2, LM // 2, 2, 3).mean(axis=(1, 3))
for stari in ("enterijer-noc.webp", "enterijer-noc-m.webp"):          # stara imena iz prve probe
    if os.path.exists(os.path.join(TEX, stari)):
        os.remove(os.path.join(TEX, stari))
v1 = snimi_webp(enc, os.path.join(TEX, "enterijer-noc-0.webp"), 88)
v2 = snimi_webp(enc_m, os.path.join(TEX, "enterijer-noc-0-m.webp"), 85)
print("LIGHTMAP noc_max %.4f p50 %.4f; webp %d KB / %d KB" % (NOC_MAX, np.percentile(lum[lum > 1e-5], 50), v1 // 1024, v2 // 1024))

# ---------------------------------------------------------------- 6. materijali za izvoz (jedan atlas za sve)
def mat_izvoz(name, img, emit=None, color_emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    p.inputs["Roughness"].default_value = 1.0
    p.inputs["Specular IOR Level"].default_value = 0.0
    if img is not None:
        uvn = nt.nodes.new("ShaderNodeUVMap")
        uvn.uv_map = "albedo"
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = img
        nt.links.new(uvn.outputs["UV"], tx.inputs["Vector"])
        nt.links.new(tx.outputs["Color"], p.inputs["Base Color"])
        if emit:
            nt.links.new(tx.outputs["Color"], p.inputs["Emission Color"])
    if color_emit:
        p.inputs["Base Color"].default_value = color_emit
        p.inputs["Emission Color"].default_value = color_emit
    if emit:
        p.inputs["Emission Strength"].default_value = emit
    return m, p


for img in IMG.values():
    img.colorspace_settings.name = "sRGB"
M_MAIN, _ = mat_izvoz("Enterijer", IMG["glavni"])
M_HLEB, _ = mat_izvoz("Enterijer_hleb", IMG["hleb"])
M_PEC, _ = mat_izvoz("Enterijer_pec", IMG["pec"])
M_ZAR, _ = mat_izvoz("Enterijer_zar", IMG["pec"], emit=EMISIJA)
M_GRUPA = {"glavni": M_MAIN, "hleb": M_HLEB, "pec": M_PEC}
MAT_IMG = {M_MAIN: IMG["glavni"], M_HLEB: IMG["hleb"], M_PEC: IMG["pec"], M_ZAR: IMG["pec"]}
M_SIJ, _ = mat_izvoz("Enterijer_sijalica", None, emit=EMISIJA, color_emit=(1.0, 0.8, 0.55, 1.0))
M_ST, p_st = mat_izvoz("Enterijer_staklo", None)
# Na sajtu je staklo neosvetljeno (boja * alfa se samo doda): svetlo staklo je u noci sivi zid ispred vitrine.
# Zato tamna boja i mala alfa (world.js trenutno boju menja svojom, ENT_STAKLO; alfa ostaje odavde).
p_st.inputs["Base Color"].default_value = (0.03, 0.035, 0.04, 1)
p_st.inputs["Alpha"].default_value = 0.08
p_st.inputs["Roughness"].default_value = 0.1
try:
    M_ST.surface_render_method = "BLENDED"
except Exception:
    M_ST.blend_method = "BLEND"
for o in OBJS:
    me = o.data
    me.materials.clear()
    me.materials.append({"Zar": M_ZAR, "Lampa_sijalica": M_SIJ}.get(o.name, M_ST if o in STAKLO else M_GRUPA[grupa(o.name)]))
    for p_ in me.polygons:
        p_.material_index = 0
    for a in [a for a in me.attributes if a.name in ("boja", "drvo")]:      # vec su u atlasu
        me.attributes.remove(a)
scene["krume"] = {"lightmap_uv": "TEXCOORD_1 (Blender UV 'lightmap')", "albedo_uv": "TEXCOORD_0 (Blender UV 'albedo')",
                  "lightmap_gamma": LM_GAMMA, "noc_max": round(NOC_MAX, 4),
                  "fajlovi": "textures/enterijer-noc-0.webp, telefon: enterijer-noc-0-m.webp",
                  "emisija": "Zar, Lampa_sijalica: emissive, bez lightmap-a"}

# ---------------------------------------------------------------- 7. izvoz GLB (2048 i 1024)
ops_props = {p.identifier for p in bpy.ops.export_scene.gltf.get_rna_type().properties}


def izvoz(path, q=82):
    bpy.ops.object.select_all(action="DESELECT")
    KOREN.select_set(True)
    for o in OBJS:
        o.select_set(True)
    vl.objects.active = KOREN
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_extras=True, export_yup=True,
              export_apply=False, export_texcoords=True, export_normals=True, export_tangents=False,
              export_materials="EXPORT", export_image_format="WEBP", export_image_quality=q,
              export_cameras=False, export_lights=False, export_animations=False, export_morph=True,
              export_morph_normal=True, export_skins=False, export_vertex_color="NONE",
              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
              export_draco_position_quantization=14, export_draco_normal_quantization=10,
              export_draco_texcoord_quantization=12)
    kw = {k: v for k, v in kw.items() if k in ops_props or k == "filepath"}
    bpy.ops.export_scene.gltf(**kw)
    return os.path.getsize(path)


sz = izvoz(os.path.join(MODELS, "enterijer.glb"))
print(f"GLB enterijer.glb: {sz / 1024:.0f} KB")
IMG_M = {}
for g, img in IMG.items():
    if ATLAS_M[g] == ATLAS:
        IMG_M[g] = img
        continue
    im = img.copy()
    im.name = img.name + "_m"
    im.scale(ATLAS_M[g], ATLAS_M[g])
    IMG_M[g] = im
for m, g in ((M_MAIN, "glavni"), (M_HLEB, "hleb"), (M_PEC, "pec"), (M_ZAR, "pec")):
    for n in m.node_tree.nodes:
        if n.type == "TEX_IMAGE":
            n.image = IMG_M[g]
sz_m = izvoz(os.path.join(MODELS, "enterijer-m.glb"), q=76)
print(f"GLB enterijer-m.glb: {sz_m / 1024:.0f} KB (granica {MB_M / 1024:.0f} KB)")
if sz_m > MB_M:
    print("UPOZORENJE: enterijer-m.glb je preko granice, smanji ATLAS_M")

dg = bpy.context.evaluated_depsgraph_get()
tri = 0
for o in OBJS:
    me = o.evaluated_get(dg).to_mesh()
    me.calc_loop_triangles()
    tri += len(me.loop_triangles)
    o.evaluated_get(dg).to_mesh_clear()
print("TROUGLOVA u izvozu", tri)

# ---------------------------------------------------------------- 8. provera: atlas * lightmap, bez tone mappinga (kao na sajtu)
img_prov = bpy.data.images.load(os.path.join(TEX, "enterijer-noc-0.webp"), check_existing=False)
img_prov.colorspace_settings.name = "Non-Color"
for m, emit in ((M_MAIN, False), (M_HLEB, False), (M_PEC, False), (M_ZAR, True)):
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type == "TEX_IMAGE":
            n.image = MAT_IMG[m]
    tx = [n for n in nt.nodes if n.type == "TEX_IMAGE"][0]
    em = nt.nodes.new("ShaderNodeEmission")
    if emit:
        nt.links.new(tx.outputs["Color"], em.inputs["Color"])
        em.inputs["Strength"].default_value = EMISIJA
    else:
        uvl = nt.nodes.new("ShaderNodeUVMap")
        uvl.uv_map = "lightmap"
        tl = nt.nodes.new("ShaderNodeTexImage")
        tl.image = img_prov
        tl.interpolation = "Linear"
        nt.links.new(uvl.outputs["UV"], tl.inputs["Vector"])
        gm = nt.nodes.new("ShaderNodeGamma")
        gm.inputs["Gamma"].default_value = LM_GAMMA
        nt.links.new(tl.outputs["Color"], gm.inputs["Color"])
        mul = nt.nodes.new("ShaderNodeMix")
        mul.data_type, mul.blend_type = "RGBA", "MULTIPLY"
        sock = {s.identifier: s for s in mul.inputs}
        sock["Factor_Float"].default_value = 1.0
        nt.links.new(tx.outputs["Color"], sock["A_Color"])
        nt.links.new(gm.outputs["Color"], sock["B_Color"])
        nt.links.new([s for s in mul.outputs if s.identifier == "Result_Color"][0], em.inputs["Color"])
        em.inputs["Strength"].default_value = NOC_MAX
    nt.links.new(em.outputs["Emission"], izlaz(nt).inputs["Surface"])
for ob in bpy.data.objects:
    if ob.type == "LIGHT":
        ob.hide_render = True
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
cy.samples = 24
cy.max_bounces = 0
cy.use_denoising = False
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.view_settings.exposure = 0.0
scene.compositing_node_group = None
scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for cam_name, path in (("Kadar_presek", os.path.join(BAKE, "enterijer-noc-provera.png")),
                       ("Stanica_4_kam", os.path.join(BAKE, "enterijer-noc-provera-st4.png")),
                       ("Stanica_5_kam", os.path.join(BAKE, "enterijer-noc-provera-st5.png"))):
    if cam_name not in bpy.data.objects:
        continue
    scene.camera = bpy.data.objects[cam_name]
    bpy.data.objects[cam_name].data.dof.use_dof = False
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BAKE, "enterijer-bake.blend"), compress=True)
b1 = os.path.join(BAKE, "enterijer-bake.blend1")
if os.path.exists(b1):
    os.remove(b1)
if os.environ.get("KRUME_CUVAJ") != "1":                 # sirovi EXR (desetine MB) ne ostaju u repou
    for f in os.listdir(BAKE):
        if f.startswith("enterijer") and f.endswith(".exr"):
            os.remove(os.path.join(BAKE, f))
print(f"GOTOVO za {time.time() - T0:.0f} s")
