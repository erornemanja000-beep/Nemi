"""GRIND (kafa skrol-sajt, poglavlje 1): inox mlin sa staklenim levkom, foto-studio verzija (23.10.2026).

Zrna padaju odozgo (iz gornje ivice kadra) u stakleni levak i odskaču po gomili (rigid body), od G50 se
gomila u sredini lagano uvlači (mlevenje), a od G50 do G88 iz otvora mlina na x=0 curi mlevena kafa
(čestice) naniže, preko šava, u V60 iz scene POUR (pour.py renderuje iste čestice svojom kamerom).

Ova skripta drži i zajednički „svet“ GRIND/POUR (storyboard.md 1-2, rig K i šav opcija C), koji pour.py
uvozi (import grind): kamera, sat G, mlaz mlevene kafe, karta za transmisiju, svetlo. Zato je main() pod
`if __name__ == '__main__'`.

- Kamera: vodoravna, 85 mm, senzor 36 mm (HORIZONTAL), 1,0625 m od ravni y=0, kadar 45 cm (1 S);
  GRIND kadar je S x 1,25 S (z 0,8775 do 0,315), POUR je tačno 1 S niže; kadriranje ide shift_y-om.
- Sat: globalni kadar G (GRIND G1-G96, POUR G65-G192); u Blenderu je kadar scene G + G_OFF (sve > 0).
- Svetlo: common.photo_studio_lights (key prozor levo-gore-napred, dve trake pozadi, crna zastava desno),
  tamna HDRI okolina 0,15, ekspozicija 0, AgX Medium High Contrast. Rig ide sa kamerom (POUR = -1 S).
  Mlaz mlevene kafe ima svoje svetlo na istom mestu u obe scene (light linking), pa je na šavu isti.
- Staklo: film_transparent_glass=False + „karta“ u boji sekcije (vidljiva samo kroz staklo), boja je
  kalibrisana kroz AgX tako da render daje tačno boju iz tokens.css.
- Fizika zrna: Bullet u uvećanom svetu (x10, gravitacija x10), levak od kutija, 10 podkoraka, 20 iteracija;
  rezultat (položaj i rotacija svakog zrna po kadru) se kešira u cache/zrna_<otisak>.npz.

HDRI „Lebombo“ (Greg Zaal, Poly Haven, CC0 1.0, https://polyhaven.com/a/lebombo, md5
15daa3dc91907106756355aa0d2a3517) dolazi iz common.world_hdri / scripts/blender/assets (IZVORI.md).
Ostalo je proceduralno.

Pokretanje iz korena repoa:
  unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \\
    -P scripts/blender/kafa/grind.py -- --out <folder> [--kadrovi 1,48,84 | sve] [--res 1200] [--uzorci 64]
    [--poster] [--rot -25] [--fstop 5] [--bez-zamucenja] [--ponovo-fizika]

Izlaz: <out>/kadar_GGGG.png (RGBA, 1200 x 1500 na --res 1200), <out>/anchors.json (sidra u S), po želji
poster.png (= G1). Telefon: neparni kadrovi, umanjeni (bez novog rendera).
"""
import argparse
import json
import math
import pathlib
import random
import sys
import time

import bmesh
import bpy
import numpy as np
from bpy_extras import anim_utils
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import common as C  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / 'cache'          # u .gitignore

# ================================================================ zajednički svet GRIND/POUR (rig K)
S = 0.45                        # stranica kvadrata kadra u metrima (1 S)
CAM_DIST = 1.0625               # kamera -> ravan y=0
LENS = 85.0
EYE_ABOVE = 0.10 * S            # visina oka iznad gornje ivice kadra
GRIND_TOP = 0.8775              # gornja ivica GRIND kadra (z)
SEAM_Z = GRIND_TOP - S          # 0,4275: šav = donja ivica GRIND kvadrata = gornja ivica POUR kadra
GRIND_H = 1.25                  # GRIND kadar je S x 1,25 S (produžetak samo za mlaz)
FPS = 30
SLOW = 0.30                     # usporenje fizike (storyboard: <= ~90 px po kadru na 1600)
G_OFF = 100                     # kadar scene = G + G_OFF (Blender keš ne voli kadar 0 i negativne)
G_GRIND = (1, 96)
G_POUR = (65, 192)
FOCUS_Y = -0.015                # ravan oštrine (isto u obe scene, pa je mlaz na šavu jednako oštar)
FSTOP = 5.0
SHUTTER = 0.4                   # motion blur, deo kadra
SEED = 7
SPOUT_W = Vector((0.0, 0.0, 0.500))   # izlaz otvora mlina (mlevena kafa kreće odavde)
LIGHT_TARGET = Vector((0.01, 0.065, 0.63))  # centar svetla za GRIND; POUR je isti, 1 S niže
STREAM_G = (50, 88)             # mlevena kafa izlazi iz otvora od G50 do G88
STREAM_DIE_Z = 0.165            # čestice nestaju unutar filtera (ispod linije pogleda preko ivice V60)
BG_GRIND = '#E6DDCE'            # --pp-cream (tokens.css)
BG_POUR = '#915439'             # --pp-terracotta


def sf(g):
    """Globalni kadar G -> kadar scene."""
    return int(g) + G_OFF


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def render_setup(scene, res_x, res_y, samples, adaptive=0.02, motion_blur=True):
    """Foto render iz common + karta umesto providnog stakla, motion blur, fiksno seme (OIDN ne treperi
    na mirnim delovima kadra)."""
    C.photo_render_settings(scene, width=res_x, height=res_y, samples=samples, transparent=True,
                            adaptive=adaptive, fps=FPS)
    cy = scene.cycles
    cy.film_transparent_glass = False          # kroz staklo se vidi karta u boji sekcije
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 16
    cy.volume_bounces = 0
    cy.seed = SEED
    cy.use_animated_seed = False
    scene.render.use_motion_blur = motion_blur
    scene.render.motion_blur_shutter = SHUTTER
    scene.render.motion_blur_position = 'CENTER'


def rig_camera(scene, which, res, fstop=FSTOP):
    """Vodoravna kamera rig K; which = 'grind' (S x 1,25 S) ili 'pour' (S x S, 1 S niže)."""
    top = GRIND_TOP if which == 'grind' else SEAM_Z
    h = GRIND_H if which == 'grind' else 1.0
    eye = top + EYE_ABOVE
    cam = C.camera((0.0, -CAM_DIST, eye), (0.0, 0.0, eye), lens=LENS)
    cd = cam.data
    cd.sensor_fit = 'HORIZONTAL'      # 36 mm je uvek širina (i kad je kadar uspravan)
    cd.sensor_width = 36.0
    cd.shift_y = (top - h * S / 2 - eye) / S   # pomak je u jedinicama širine kadra (S)
    cd.clip_start, cd.clip_end = 0.05, 30.0
    scene.render.resolution_x = res
    scene.render.resolution_y = round(res * h)
    cd.dof.use_dof = True
    cd.dof.focus_distance = CAM_DIST + FOCUS_Y
    cd.dof.aperture_fstop = fstop
    cd.dof.aperture_blades = 7
    cd.dof.aperture_rotation = math.radians(12)
    return cam


def project(scene, cam, p, which):
    """Tačka sveta -> (x, y) u jedinicama S od gornjeg levog ugla punog kadra."""
    bpy.context.view_layer.update()
    v = world_to_camera_view(scene, cam, Vector(p))
    h = GRIND_H if which == 'grind' else 1.0
    return v.x, (1.0 - v.y) * h


# ---------------------------------------------------------------- karta (pozadina vidljiva samo kroz staklo)

def _srgb_to_lin(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def card_color(scene, hex_color):
    """Linearna emisija koja kroz AgX (view/look/ekspozicija scene) izlazi tačno kao hex_color.
    Kalibriše se renderom 8x8 ravni (par sekundi), rezultat se pamti u cache/karta_boje.json."""
    vs = scene.view_settings
    key = f'{hex_color}|{vs.view_transform}|{vs.look}|{vs.exposure:.3f}|{vs.gamma:.3f}|{bpy.app.version_string}'
    store = CACHE / 'karta_boje.json'
    data = json.loads(store.read_text()) if store.exists() else {}
    if key in data:
        return tuple(data[key])
    target = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    tl = [_srgb_to_lin(t) for t in target]
    tmp = bpy.data.scenes.new('Kalibracija')
    tmp.render.engine = 'CYCLES'
    tmp.cycles.device = 'CPU'
    tmp.cycles.samples = 1
    tmp.cycles.use_adaptive_sampling = False
    tmp.cycles.use_denoising = False
    tmp.cycles.filter_width = 0.01
    tmp.render.resolution_x = tmp.render.resolution_y = 8
    tmp.render.resolution_percentage = 100
    tmp.render.film_transparent = False
    tmp.view_settings.view_transform = vs.view_transform
    tmp.view_settings.look = vs.look
    tmp.view_settings.exposure = vs.exposure
    tmp.view_settings.gamma = vs.gamma
    tmp.display_settings.display_device = scene.display_settings.display_device
    tmp.render.image_settings.file_format = 'PNG'
    tmp.render.image_settings.color_mode = 'RGB'
    tmp.render.image_settings.color_depth = '8'
    cd = bpy.data.cameras.new('KalibCam')
    cd.type = 'ORTHO'
    cd.ortho_scale = 0.5
    co = bpy.data.objects.new('KalibCam', cd)
    tmp.collection.objects.link(co)
    tmp.camera = co
    co.location = (0, 0, 1)
    me = bpy.data.meshes.new('KalibPlane')
    me.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    po = bpy.data.objects.new('KalibPlane', me)
    tmp.collection.objects.link(po)
    m, nt, _, N = C.new_material('KalibEmisija')
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial':
            nt.nodes.remove(n)
    em = N.new('ShaderNodeEmission')
    nt.links.new(em.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    me.materials.append(m)
    c = list(tl)
    path = CACHE / 'kalibracija.png'
    CACHE.mkdir(parents=True, exist_ok=True)
    for _ in range(7):
        em.inputs['Color'].default_value = (*c, 1.0)
        tmp.render.filepath = str(path)
        bpy.ops.render.render(write_still=True, scene=tmp.name)
        img = bpy.data.images.load(str(path), check_existing=False)
        img.colorspace_settings.name = 'Non-Color'
        px = list(img.pixels[:4 * 8 * 8])
        meas = [sum(px[k::4]) / 64 for k in range(3)]
        bpy.data.images.remove(img)
        c = [ci * _srgb_to_lin(t) / max(_srgb_to_lin(mv), 1e-6) for ci, t, mv in zip(c, target, meas)]
    for ob in (co, po):
        bpy.data.objects.remove(ob)
    bpy.data.scenes.remove(tmp)
    path.unlink(missing_ok=True)
    data[key] = [round(v, 6) for v in c]
    store.write_text(json.dumps(data, indent=1))
    print(f'karta: {hex_color} -> linearno {tuple(round(v, 4) for v in c)} (izmereno {[round(255 * v) for v in meas]})')
    return tuple(c)


def transmission_card(scene, hex_color, center, radius=4.0):
    """Velika sfera u boji sekcije, vidljiva SAMO zracima prelamanja: kroz staklo i tečnost vidi se
    pozadina sajta, a staklo ostaje neprovidno u alfa kanalu (kafa u bokalu ne postaje providna)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=radius)
    me = bpy.data.meshes.new('Karta')
    bm.to_mesh(me)
    bm.free()
    ob = C.link(bpy.data.objects.new('Karta', me))
    ob.location = center
    m, nt, _, N = C.new_material('Karta')
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial':
            nt.nodes.remove(n)
    em = N.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*card_color(scene, hex_color), 1.0)
    nt.links.new(em.outputs[0], nt.nodes['Material Output'].inputs['Surface'])
    if hasattr(m, 'emission_sampling'):
        m.emission_sampling = 'NONE'
    elif hasattr(m.cycles, 'emission_sampling'):
        m.cycles.emission_sampling = 'NONE'
    C.assign(ob, m)
    C.ray_visibility(ob, camera=False, diffuse=False, glossy=False, transmission=True, scatter=False,
                     shadow=False)
    return ob


# ---------------------------------------------------------------- svetlo

def lights(scene, which, subjects, stream_objs, key=70.0, strip=6.0, refl=3.0, refl_subjects=None,
           stream_key=None, no_key=()):
    """Foto-studio iz common.py oko LIGHT_TARGET (POUR: 1 S niže) + blenda „Odsjaj“: velika bela ploča
    levo-napred, nisko, vidljiva samo u odsjaju predmeta (subjects): prednja strana inoksa dobija svetao
    meki odsjaj, a crna zastava desno tamnu traku (kontrast kao na product fotografiji).
    Mlevena kafa ne prima key ove scene, nego StreamKey na istom mestu u obe scene (između dva key-a),
    pa se mlaz na šavu ne menja."""
    dz = 0.0 if which == 'grind' else -S
    tgt = LIGHT_TARGET + Vector((0.0, 0.0, dz))
    ls = C.photo_studio_lights(tuple(tgt), subjects, None, key=key, strip=strip, flags=True)
    if refl > 0:
        only = bpy.data.collections.new('OdsjajPrima')
        for ob in (subjects if refl_subjects is None else refl_subjects):     # staklo ne (koprena)
            only.objects.link(ob)
        pos = tgt + 0.85 * C.direction(-138.0, 4.0)
        ro = C.area_light('Odsjaj', tuple(pos), tuple(tgt), (0.55, 0.75), refl, 6000)
        C.ray_visibility(ro, camera=False, diffuse=False, glossy=True, transmission=False, scatter=False)
        ro.light_linking.receiver_collection = only
        ls.append(ro)
    if not stream_objs and not no_key:
        return ls
    k = next(o for o in ls if o.name == 'Key')
    no_stream = bpy.data.collections.new('BezMlaza')       # key ne svetli mlaz (ni objekte iz no_key)
    for ob in list(stream_objs) + list(no_key):
        no_stream.objects.link(ob)
    for co in no_stream.collection_objects:
        co.light_linking.link_state = 'EXCLUDE'
    k.light_linking.receiver_collection = no_stream
    if not stream_objs:
        return ls
    only_stream = bpy.data.collections.new('SamoMlaz')
    for ob in stream_objs:
        only_stream.objects.link(ob)
    mid = LIGHT_TARGET + Vector((0.0, 0.0, -S / 2))
    kdir = C.direction(C.STUDIO['key_az'], C.STUDIO['key_el'])
    pos = mid + C.STUDIO['key_dist'] * kdir
    sk = C.area_light('StreamKey', tuple(pos), tuple(mid), C.STUDIO['key_size'],
                      key if stream_key is None else stream_key, C.STUDIO['key_kelvin'])
    sk.light_linking.receiver_collection = only_stream
    ls.append(sk)
    return ls


# ---------------------------------------------------------------- mlaz mlevene kafe (isti u GRIND i POUR)

def mat_grounds():
    """Mlevena kafa: mat, malo svetlija od zrna, svaka mrvica druge nijanse."""
    m, nt, b, N = C.new_material('MlevenaKafa')
    oi = N.new('ShaderNodeObjectInfo')
    col = N.mix(N.ramp(oi.outputs['Random'], 0.0, 1.0), (0.026, 0.013, 0.007), (0.075, 0.040, 0.021))
    N.put(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.85
    b.inputs['Specular IOR Level'].default_value = 0.3
    return m


def crumb_mesh(name, rng, size, subdiv=1, lumpy=0.35):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    s = (size * rng.uniform(0.8, 1.2), size * rng.uniform(0.6, 0.95), size * rng.uniform(0.45, 0.75))
    for vert in bm.verts:
        k = 1.0 + lumpy * rng.uniform(-1, 1)
        vert.co = (vert.co.x * s[0] * k, vert.co.y * s[1] * k, vert.co.z * s[2] * k)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def stream_fall_frames(z_die=STREAM_DIE_Z, v0=0.12):
    """Koliko kadrova čestica pada od otvora do z_die (za lifetime)."""
    h = SPOUT_W.z - z_die
    t = (-v0 + math.sqrt(v0 * v0 + 2 * 9.81 * h)) / 9.81
    return t / (SLOW / FPS)


def build_grounds(scene, rate=170, end_g=None):
    """Čestice mlevene kafe iz otvora mlina (Newton, seme fiksno). Isti poziv u grind.py i pour.py daje iste
    čestice u istom trenutku (šav, opcija C). Vraća (emiter, objekti mrvica za light linking)."""
    rng = random.Random(SEED * 31 + 5)
    shapes = bpy.data.collections.new('MlevenoOblici')        # nije u sceni, samo za instance
    mat = mat_grounds()
    crumbs = []
    for k in range(10):
        ob = bpy.data.objects.new(f'Mrvica{k}', crumb_mesh(f'Mrvica{k}', rng, rng.uniform(0.00035, 0.00075)))
        ob.data.materials.append(mat)
        shapes.objects.link(ob)
        crumbs.append(ob)
    ob = bpy.data.objects.new('Grudvica', crumb_mesh('Grudvica', rng, 0.0011, subdiv=2, lumpy=0.25))
    ob.data.materials.append(mat)
    shapes.objects.link(ob)
    crumbs.append(ob)
    for o in crumbs:
        for p in o.data.polygons:
            p.use_smooth = True

    # emiter: elipsa 9 x 4,4 mm (tanak mlaz po dubini zbog paralakse na šavu), normala nadole
    bm = bmesh.new()
    n = 24
    vs = [bm.verts.new((0.0045 * math.cos(2 * math.pi * i / n), 0.0022 * math.sin(2 * math.pi * i / n), 0.0))
          for i in range(n)]
    bm.faces.new(vs[::-1])                       # normala -Z
    me = bpy.data.meshes.new('MlazIzvor')
    bm.to_mesh(me)
    bm.free()
    em = C.link(bpy.data.objects.new('MlazIzvor', me))
    em.location = SPOUT_W - Vector((0.0, 0.0, 0.0008))
    em.show_instancer_for_render = False
    em.visible_shadow = False
    ps = em.modifiers.new('Mlaz', 'PARTICLE_SYSTEM').particle_system
    ps.seed = SEED
    st = ps.settings
    g0, g1 = STREAM_G
    st.frame_start, st.frame_end = sf(g0), sf(g1)
    st.count = int(rate * (g1 - g0))
    st.lifetime = stream_fall_frames()
    st.lifetime_random = 0.0
    st.emit_from = 'FACE'
    st.use_emit_random = True
    st.distribution = 'RAND'
    st.physics_type = 'NEWTON'
    st.normal_factor = 0.12                      # m/s nadole na izlazu
    st.factor_random = 0.010                     # mlaz se blago širi (±2-3 mm do V60)
    st.brownian_factor = 0.0
    st.drag_factor = 0.0
    st.time_tweak = SLOW * (1.0 / FPS) / 0.04    # čestice računaju 1 kadar = 0,04 s x time_tweak
    st.render_type = 'COLLECTION'
    st.instance_collection = shapes
    st.use_collection_pick_random = True
    st.particle_size = 1.0
    st.size_random = 0.45
    st.use_rotations = True
    st.rotation_mode = 'NONE'
    st.rotation_factor_random = 1.0
    st.phase_factor_random = 2.0
    st.angular_velocity_mode = 'RAND'
    st.angular_velocity_factor = 30.0
    pc = ps.point_cache
    pc.frame_start = sf(g0)
    pc.frame_end = sf(end_g if end_g else G_POUR[1])
    return em, crumbs


def bake_particles(scene):
    with bpy.context.temp_override(scene=scene):
        bpy.ops.ptcache.bake_all(bake=True)


# ---------------------------------------------------------------- zrna (geometrija i materijal, i za POUR)
BEAN = (0.0110, 0.0080, 0.0034, 0.0022)   # dužina, širina, ispupčena i ravna polu-debljina (m)
N_SHAPES = 12


def bean_shape(k):
    r = random.Random(1000 + 17 * k)
    return dict(L=BEAN[0] * r.uniform(0.90, 1.10), W=BEAN[1] * r.uniform(0.90, 1.08),
                tt=BEAN[2] * r.uniform(0.88, 1.12), tb=BEAN[3] * r.uniform(0.85, 1.15),
                bend=r.uniform(-0.0009, 0.0009), s_amp=r.uniform(0.00015, 0.00065), s_ph=r.uniform(-0.6, 0.6),
                asym=r.uniform(-0.12, 0.12), tip=r.uniform(0.85, 1.20), gd=r.uniform(0.0010, 0.0015),
                gw=r.uniform(0.00055, 0.00080), twist=r.uniform(-0.15, 0.15), lean=r.uniform(-0.25, 0.25))


def bean_bm(sh, u=64, v=24, groove=True, scale=1.0):
    """Zrno: elipsoid ispupčen gore (+Z), ravan dole sa S-urezom uzduž; atribut 'chaff' = ljuspica u urezu."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=1.0)
    lay = bm.verts.layers.float.new('chaff') if groove else None
    for vert in bm.verts:
        a, b, c = vert.co                      # c: osa polova = dužina zrna
        rr = math.hypot(a, b)
        if rr > 1e-6:
            k = rr ** sh['tip'] / rr           # zašiljeniji ili tupiji vrhovi
            a, b = a * k, b * k
        X = c * sh['L'] / 2
        Y = a * sh['W'] / 2 * (1 + sh['asym'] * c)
        if b >= 0:
            Z = b * sh['tt'] * (1 + sh['lean'] * a * 0.3)
            w = 0.0
        else:
            Z = -sh['tb'] * ((-b) ** 0.7)
            yc = sh['s_amp'] * math.sin(math.pi * c + sh['s_ph'])
            end = max(0.0, 1 - c ** 4)
            w = 0.0
            if groove:
                g = sh['gd'] * math.exp(-((Y - yc) / sh['gw']) ** 2) * end
                Z += g * min(1.0, -b * 1.6)
                w = math.exp(-((Y - yc) / (sh['gw'] * 0.75)) ** 2) * max(0.0, 1 - c ** 6) * min(1.0, -b * 2.0)
        Z += sh['bend'] * (c * c - 0.3)
        ca, sa = math.cos(sh['twist'] * c), math.sin(sh['twist'] * c)
        Y, Z = Y * ca - Z * sa, Y * sa + Z * ca
        vert.co = (X * scale, Y * scale, Z * scale)
        if lay is not None:
            vert[lay] = w
    return bm


def bean_meshes():
    """12 oblika zrna za render (sa urezom i ljuspicom) i isti oblici niske rezolucije za fiziku (x10)."""
    mat = mat_bean()
    render, proxy = [], []
    for k in range(N_SHAPES):
        sh = bean_shape(k)
        me = bpy.data.meshes.new(f'ZrnoOblik{k:02d}')
        bm = bean_bm(sh)
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(mat)
        render.append(me)
        pm = bpy.data.meshes.new(f'ZrnoFizika{k:02d}')
        bm = bean_bm(sh, u=10, v=6, groove=False, scale=PHYS_K)
        bm.to_mesh(pm)
        bm.free()
        proxy.append(pm)
    return render, proxy, mat


def mat_bean():
    """Prženo zrno (tamno, median ~#3A2216-#5A3A28 posle svetla): mrlje prženja, blag sjaj ulja, srebrna
    ljuspica (silverskin) u urezu, sitna tekstura; svako zrno malo druge nijanse."""
    m, nt, b, N = C.new_material('Zrno')
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    oi = N.new('ShaderNodeObjectInfo')
    rnd = oi.outputs['Random']
    base = N.mix(N.ramp(rnd, 0.0, 1.0), (0.020, 0.0095, 0.0048), (0.046, 0.023, 0.0115))
    mott = N.noise(P, 700.0, detail=3, rough=0.55)
    base = N.mix(N.ramp(mott, 0.35, 0.70), N.tint(base, (0.80, 0.78, 0.76)), N.tint(base, (1.18, 1.15, 1.10)))
    chaff = N.new('ShaderNodeAttribute', attribute_type='GEOMETRY', attribute_name='chaff').outputs['Fac']
    breakup = N.ramp(N.noise(P, 1400.0, detail=2), 0.30, 0.62)
    cm = N.mul(N.ramp(chaff, 0.25, 0.75), N.math('MULTIPLY_ADD', breakup, 0.8, 0.2))
    col = N.mix(cm, base, (0.27, 0.19, 0.11))
    N.put(col, b.inputs['Base Color'])
    N.put(N.mixf(cm, N.math('MULTIPLY_ADD', N.noise(P, 220.0, detail=2), 0.16, 0.34), 0.80), b.inputs['Roughness'])
    b.inputs['Specular IOR Level'].default_value = 0.5
    N.put(N.mixf(cm, 0.18, 0.0), b.inputs['Coat Weight'])
    b.inputs['Coat Roughness'].default_value = 0.28
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(N.add(N.noise(P, 2600.0, detail=1), N.mul(mott, 0.5)), 0.000012), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    return m


# ================================================================ mlin (lokalno: centar tela (0,0), pod z=0,
# prednja strana ka -Y); u svetu ga postavlja matrica M (okret oko ose otvora + pomak na SPOUT_W)
W, D = 0.155, 0.180          # telo: širina (x), dubina (y)
RC = 0.016                   # radijus vertikalnih ivica tela
Z_TOP = 0.165                # gornja površina tela
Z_OVER = 0.048               # donja ivica gornjeg dela (nadstrešnica iznad otvora)
RECESS = 0.058               # koliko je postolje uvučeno napred (niša ispod otvora)
SPOUT = (0.012, -D / 2 + 0.024)   # osa otvora (lokalno x, y)
SPOUT_Z = 0.036              # donja ivica crnog prstena otvora
DIAL = (-0.026, 0.098)       # točkić za mlevenje na prednjoj strani (x, z)
HOP_Z0, HOP_TOP = 0.192, 0.319    # stakleni levak
RIM_R = 0.0825               # unutrašnji radijus crnog prstena na vrhu (otvor za zrna)
HOP_IN = [(0.0362, 0.2000), (0.0362, 0.2045), (0.0388, 0.2095), (0.0832, 0.2572), (0.0848, 0.2620),
          (0.0852, 0.3185)]   # unutrašnjost levka (r, z) za fiziku
PHYS_K = 10.0                # uvećanje sveta za Bullet (Manual: mala tela su nestabilna)


def grinder_matrix(rot_deg):
    """Okret mlina oko vertikalne ose kroz otvor; otvor (izlaz) je tačno na SPOUT_W (x=0, y=0)."""
    th = math.radians(rot_deg)
    sx, sy = SPOUT
    rx, ry = sx * math.cos(th) - sy * math.sin(th), sx * math.sin(th) + sy * math.cos(th)
    return Matrix.Translation((-rx, -ry, SPOUT_W.z - SPOUT_Z)) @ Matrix.Rotation(th, 4, 'Z')


def mesh_object(name, bm, smooth=True, sharp_deg=None, collection=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = smooth
    if smooth and sharp_deg:
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    return ob


def bevel(ob, width=0.0004, angle=30.0, segments=2):
    """Bevel 0,3-0,5 mm na tvrdim ivicama (dijagnoza, tačka 10): odsjaj „uhvati“ ivicu kao na fotografiji."""
    m = ob.modifiers.new('Bevel', 'BEVEL')
    m.width, m.segments = width, segments
    m.limit_method = 'ANGLE'
    m.angle_limit = math.radians(angle)
    m.use_clamp_overlap = True
    m.harden_normals = False
    return ob


def lathe2(name, profile, segments=96, closed=False, sharp_deg=40, smooth=True):
    """Telo okretanja oko Z; profile je lista (r, z); closed=True spaja poslednju tačku sa prvom."""
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((r * ca, r * sa, z)) for r, z in profile])
    n = len(profile)
    for i in range(segments):
        A, B = rings[i], rings[(i + 1) % segments]
        for j in range(n if closed else n - 1):
            j2 = (j + 1) % n
            bm.faces.new((A[j], B[j], B[j2], A[j2]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7)
    return mesh_object(name, bm, smooth=smooth, sharp_deg=sharp_deg)


def rounded_box(name, x0, x1, y0, y1, z0, z1, rc, rt=0.001, rb=0.001, seg_c=12, seg_e=5):
    """Kvadar sa zaobljenim vertikalnim ivicama (rc) i zaobljenim gornjim/donjim ivicama (rt, rb)."""
    cx, cy, hx, hy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    prof = []   # (uvlačenje, z, normala_r, normala_z)
    for k in range(seg_e + 1):
        a = math.pi / 2 * k / seg_e
        prof.append((rb * (1 - math.sin(a)), z0 + rb * (1 - math.cos(a)), math.sin(a), -math.cos(a)))
    for k in range(seg_e + 1):
        a = math.pi / 2 * k / seg_e
        prof.append((rt * (1 - math.cos(a)), z1 - rt + rt * math.sin(a), math.cos(a), math.sin(a)))
    corners = [(1, 1, 0.0), (-1, 1, 90.0), (-1, -1, 180.0), (1, -1, 270.0)]
    bm = bmesh.new()
    rings, normals = [], []
    for inset, z, nr, nz in prof:
        ring = []
        rr = max(rc - inset, 1e-5)
        for sx, sy, a0 in corners:
            ccx, ccy = cx + sx * (hx - rc), cy + sy * (hy - rc)
            for k in range(seg_c + 1):
                a = math.radians(a0 + 90.0 * k / seg_c)
                ca, sa = math.cos(a), math.sin(a)
                ring.append(bm.verts.new((ccx + rr * ca, ccy + rr * sa, z)))
                normals.append(Vector((ca * nr, sa * nr, nz)).normalized())
        rings.append(ring)
    m = len(rings[0])
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(m):
            i2 = (i + 1) % m
            bm.faces.new((A[i], A[i2], B[i2], B[i]))
    bm.faces.new(rings[-1])
    bm.faces.new(list(reversed(rings[0])))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for poly in me.polygons:
        poly.use_smooth = True
    me.normals_split_custom_set_from_vertices(normals)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- materijali mlina

# otisci prstiju i mrlje (lokalne koordinate mlina): (centar, poluose) elipsoida na mestima koja se diraju
PRINTS = [((0.010, -0.0905, 0.128), (0.010, 0.006, 0.013)), ((0.040, -0.0905, 0.070), (0.011, 0.006, 0.015)),
          ((-0.062, -0.0905, 0.150), (0.009, 0.006, 0.012)), ((0.0775, -0.040, 0.120), (0.006, 0.012, 0.016)),
          ((0.0775, 0.010, 0.085), (0.006, 0.010, 0.013)), ((0.055, -0.007, 0.1885), (0.012, 0.008, 0.004))]


def mat_steel(name, rough=0.22, color=(0.62, 0.61, 0.59), aniso=0.65, spun=False, prints=True, smudge=1.0):
    """Brušeni inox: anizotropan (horizontalno brušenje = tangenta oko Z; spun = kružno oko ose dugmeta),
    fine linije brušenja u hrapavosti i bump-u, mrlje i otisci prstiju (hrapavije, manje anizotropno)."""
    m, nt, b, N = C.new_material(name)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Base Color'].default_value = (*color, 1.0)
    tan = N.new('ShaderNodeTangent', direction_type='RADIAL', axis='Z')
    N.put(tan.outputs['Tangent'], b.inputs['Tangent'])
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    if spun:
        r = N.vmath('LENGTH', N.vmath('MULTIPLY', P, (1.0, 1.0, 0.0)))
        streak = N.noise(N.xyz(N.mul(r, 2600.0), 0.0, 0.0), 1.0, detail=3)
    else:
        streak = N.noise(N.vmath('MULTIPLY', P, (35.0, 35.0, 2600.0)), 1.0, detail=3)
    sm = N.mul(N.ramp(N.noise(P, 16.0, detail=4, distortion=0.5), 0.60, 0.82), smudge)
    marks = sm
    if prints:                  # otisak = mrlja nepravilne ivice, a ne disk (na 1200 px šare se ne vide)
        grain = N.noise(P, 260.0, detail=2, distortion=0.8)
        for c, ax in PRINTS:
            q = N.vmath('DIVIDE', N.vmath('SUBTRACT', P, c), ax)
            d = N.add(N.vmath('LENGTH', q), N.mul(N.sub(grain, 0.5), 0.9))
            marks = N.math('MAXIMUM', marks, N.mul(N.ramp(d, 1.0, 0.45), 0.7))
    rgh = N.add(N.math('MULTIPLY_ADD', N.sub(streak, 0.5), 0.10, rough), N.mul(marks, 0.045))
    N.put(rgh, b.inputs['Roughness'])
    N.put(N.mul(N.math('MULTIPLY_ADD', marks, -0.20, 1.0), aniso), b.inputs['Anisotropic'])
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(streak, 0.0000025), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def mat_plastic(name, color=(0.012, 0.012, 0.012), rough=0.52, spec=0.32):
    m, nt, b, N = C.new_material(name)
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    b.inputs['Base Color'].default_value = (*color, 1.0)
    N.put(N.math('MULTIPLY_ADD', N.noise(P, 60.0, detail=3), 0.12, rough - 0.06), b.inputs['Roughness'])
    b.inputs['Specular IOR Level'].default_value = spec
    return m


def mat_glass(name, tint=(0.965, 0.980, 0.975), ior=1.5, shadow=0.90, smudge=0.06):
    """Staklo: za zrake senke delom providno (zrna u levku su osvetljena kao u videu, bez kaustika),
    sa retkim mrljama (hrapavije) da ne izgleda kao savršen CG."""
    m, nt, b, N = C.new_material(name)
    b.inputs['Base Color'].default_value = (*tint, 1.0)
    b.inputs['Transmission Weight'].default_value = 1.0
    b.inputs['IOR'].default_value = ior
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    N.put(N.mul(N.ramp(N.noise(P, 11.0, detail=3, distortion=0.4), 0.62, 0.80), smudge), b.inputs['Roughness'])
    out = nt.nodes['Material Output']
    lp = N.new('ShaderNodeLightPath')
    tr = N.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (shadow, shadow, shadow, 1.0)
    mix = N.new('ShaderNodeMixShader')
    N.put(lp.outputs['Is Shadow Ray'], mix.inputs['Fac'])
    nt.links.new(b.outputs['BSDF'], mix.inputs[1])
    nt.links.new(tr.outputs['BSDF'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m


def build_grinder(M):
    """Svi delovi mlina u lokalnim koordinatama, postavljeni matricom M. Vraća listu objekata."""
    steel = mat_steel('Inox')
    steel_pol = mat_steel('InoxPolirani', rough=0.13, aniso=0.45, prints=False, smudge=0.6)
    steel_spun = mat_steel('InoxTockic', rough=0.17, aniso=0.75, spun=True, prints=False, smudge=0.7)
    black = mat_plastic('CrnaPlastika')
    rubber = mat_plastic('Guma', color=(0.010, 0.010, 0.010), rough=0.70, spec=0.25)
    mark = mat_plastic('Oznake', color=(0.03, 0.03, 0.03), rough=0.55)
    glass = mat_glass('StakloLevka')
    objs = []

    def place(ob, mat, local=Matrix()):
        ob.matrix_world = M @ local
        C.assign(ob, mat)
        objs.append(ob)
        return ob

    body = rounded_box('Telo', -W / 2, W / 2, -D / 2, D / 2, Z_OVER, Z_TOP, RC, rt=0.0045, rb=0.0035)
    place(body, steel)
    base = rounded_box('Postolje', -W / 2 + 0.002, W / 2 - 0.002, -D / 2 + RECESS, D / 2 - 0.002,
                       0.0, Z_OVER + 0.004, RC - 0.002, rt=0.001, rb=0.003)
    place(base, steel)
    collar = lathe2('Kuciste', [(0.0, Z_TOP - 0.0005), (0.049, Z_TOP - 0.0005), (0.0502, Z_TOP + 0.001),
                                (0.0502, 0.1765), (0.0488, 0.1772), (0.0488, 0.1782), (0.0502, 0.1789),
                                (0.0502, 0.1885), (0.0490, 0.1900), (0.0, 0.1900)], segments=160)
    place(bevel(collar), steel_pol)
    gasket = lathe2('Zaptivka', [(0.0355, 0.1895), (0.0452, 0.1895), (0.0458, 0.1905), (0.0458, 0.1960),
                                 (0.0450, 0.1970), (0.0355, 0.1970)], segments=128, closed=True)
    place(gasket, rubber)
    hop = [(0.0400, HOP_Z0), (0.0400, 0.2040), (0.0425, 0.2085), (0.0870, 0.2560), (0.0885, 0.2620),
           (0.0890, HOP_TOP - 0.001), (0.0888, HOP_TOP), (0.0862, HOP_TOP), (0.0860, HOP_TOP - 0.001),
           (0.0855, 0.2625), (0.0842, 0.2575), (0.0397, 0.2098), (0.0370, 0.2050), (0.0370, HOP_Z0)]
    place(lathe2('Levak', hop, segments=192, closed=True, sharp_deg=50), glass)
    ring = [(0.0895, 0.312), (0.0925, 0.312), (0.0935, 0.3132), (0.0935, 0.3268), (0.0925, 0.328),
            (RIM_R + 0.001, 0.328), (RIM_R, 0.3268), (RIM_R, 0.3205), (RIM_R + 0.001, HOP_TOP + 0.0005),
            (0.0895, HOP_TOP + 0.0005)]
    place(bevel(lathe2('Poklopac', ring, segments=192, closed=True, sharp_deg=50)), black)

    dx, dz = DIAL
    dial_m = Matrix.Translation((dx, -D / 2 + 0.0005, dz)) @ Matrix.Rotation(math.radians(90), 4, 'X')
    bezel = lathe2('TockicPrsten', [(0.0300, -0.001), (0.0350, -0.001), (0.0350, 0.0022), (0.0342, 0.0031),
                                    (0.0300, 0.0031)], segments=160, closed=True, sharp_deg=50)
    place(bevel(bezel, 0.0003), steel_pol, dial_m)
    knob = lathe2('Tockic', [(0.0, 0.0), (0.0276, 0.0), (0.0276, 0.0026), (0.0290, 0.0040), (0.0290, 0.0250),
                             (0.0284, 0.0266), (0.0268, 0.0277), (0.0230, 0.0281), (0.0, 0.0276)],
                  segments=160, sharp_deg=50)
    place(bevel(knob, 0.0003), steel_spun, dial_m)
    for k in range(7):          # podeoci po gornjem luku prstena
        a = math.radians(40 + k * 100 / 6)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.0020, 0.0006, 0.0005), verts=bm.verts)
        tick = mesh_object(f'Podeok{k}', bm, smooth=False)
        loc = Matrix.Translation((0.0323 * math.cos(a), 0.0323 * math.sin(a), 0.0030)) @ Matrix.Rotation(a, 4, 'Z')
        place(tick, mark, dial_m @ loc)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.0055, 0.0009, 0.0006), verts=bm.verts)
    a = math.radians(120)
    ind = mesh_object('TockicOznaka', bm, smooth=False)
    place(ind, mark, dial_m @ Matrix.Translation((0.0215 * math.cos(a), 0.0215 * math.sin(a), 0.0280))
          @ Matrix.Rotation(a, 4, 'Z'))

    bm = bmesh.new()             # nareckano dugme gore levo
    n, r0, h = 72, 0.0155, 0.0135
    rings = []
    for z, kn, rr in ((Z_TOP - 0.001, True, r0), (Z_TOP + h - 0.0018, True, r0), (Z_TOP + h, False, r0 - 0.0016)):
        rg = []
        for i in range(n):
            a = 2 * math.pi * i / n
            r = rr - (0.0007 if (kn and i % 2) else 0.0)
            rg.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(rg)
    for j in range(2):
        for i in range(n):
            i2 = (i + 1) % n
            bm.faces.new((rings[j][i], rings[j][i2], rings[j + 1][i2], rings[j + 1][i]))
    bm.faces.new(rings[-1])
    knurl = mesh_object('DugmeGore', bm, sharp_deg=35)
    place(bevel(knurl, 0.0003), steel_pol, Matrix.Translation((-0.052, -0.045, 0.0)))
    tab = rounded_box('Jezicak', 0.030, 0.080, -0.013, -0.001, 0.1862, 0.1900, 0.0055, rt=0.0012, rb=0.0008,
                      seg_c=8, seg_e=3)
    place(tab, steel_pol)

    sx, sy = SPOUT              # otvor: crni prsten ispod nadstrešnice, šupalj (mlevena kafa izlazi iz njega)
    spout = lathe2('Otvor', [(0.0105, 0.0445), (0.0105, SPOUT_Z + 0.0012), (0.0118, SPOUT_Z),
                             (0.0185, SPOUT_Z), (0.0190, SPOUT_Z + 0.0008), (0.0190, Z_OVER + 0.0005),
                             (0.0, Z_OVER + 0.0005)], segments=96, sharp_deg=50)
    place(bevel(spout, 0.0003), black, Matrix.Translation((sx, sy, 0.0)))
    throat = lathe2('OtvorUnutra', [(0.0, 0.0446), (0.0105, 0.0446)], segments=48)
    place(throat, mat_plastic('OtvorTamno', color=(0.004, 0.003, 0.002), rough=0.9), Matrix.Translation((sx, sy, 0.0)))
    return objs


# ================================================================ fizika zrna (uvećan svet, keš)

def r_hopper(z):
    """Unutrašnji poluprečnik levka na visini z (lokalno)."""
    for (r0, z0), (r1, z1) in zip(HOP_IN, HOP_IN[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return HOP_IN[0][0] if z < HOP_IN[0][1] else HOP_IN[-1][0]


def physics_plan(a):
    """Deterministički plan: punjenje (rešetka u levku, pada pre G1) i mlaz odozgo (red na „traci“).
    Vraća listu (oblik, start (x, y, z) lokalno u m, rot0, kadar puštanja u G ili None)."""
    rng = random.Random(a.seed)
    plan = []
    sp = 0.0125                     # razmak rešetke (zrno 11 mm)
    z, layer = 0.214, 0
    while len(plan) < a.punjenje:
        rmax = min(0.074, r_hopper(z) - 0.0080)    # zrno (pola dužine 5,5 mm) ne sme u zid na startu
        off = (layer % 2) * sp / 2
        nx = int(rmax / sp) + 1
        for ix in range(-nx, nx + 1):
            for iy in range(-nx, nx + 1):
                x = ix * sp + off + rng.uniform(-0.002, 0.002)
                y = iy * sp * 0.866 + rng.uniform(-0.002, 0.002)
                if x * x + y * y < rmax * rmax and len(plan) < a.punjenje:
                    rot = (rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3))
                    plan.append((len(plan) % N_SHAPES, (x, y, z + rng.uniform(-0.002, 0.002)), rot, None))
        z += sp * 0.9
        layer += 1
    # mlaz odozgo: G-20..G40 punom brzinom, G40..G48 se proređuje
    times = []
    t = -20.0
    while t < 48.0:
        rate = a.tok if t < 40 else a.tok * (48 - t) / 8
        if rate <= 0.05:
            break
        times.append(t)
        t += 1.0 / rate
    vq = a.traka * SLOW / FPS        # m po kadru na „traci“ iznad kadra
    z_rel = 0.950 - (SPOUT_W.z - SPOUT_Z)  # puštanje na z=0,95 u svetu (iznad gornje ivice kadra)
    placed = []
    for t in times:
        for _ in range(200):
            rr = 0.024 * math.sqrt(rng.random())
            ang = rng.uniform(0, 2 * math.pi)
            x, y = rr * math.cos(ang), rr * math.sin(ang)
            jz = rng.uniform(0.0, 0.010)
            qz = vq * t + jz
            if all((x - px) ** 2 + (y - py) ** 2 + (qz - pz) ** 2 > 0.0135 ** 2
                   for pz, px, py in placed[-80:] if abs(qz - pz) < 0.0135):
                break
        placed.append((qz, x, y))
        rot = (rng.uniform(0, 6.3), rng.uniform(0, 6.3), rng.uniform(0, 6.3))
        plan.append((len(plan) % N_SHAPES, (x, y, z_rel + jz), rot, t))
    return plan


def _box(name, center, size, rot3, coll):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.matrix_world = Matrix.Translation(center) @ rot3.to_4x4()
    return ob


def _staves(prefix, prof, n, thick, coll, ext_top=0.0):
    """Zid okretanja od kutija (Box oblik ima debljinu, za razliku od mesh sudara)."""
    obs = []
    K = PHYS_K
    for j in range(len(prof) - 1):
        (r0, z0), (r1, z1) = prof[j], prof[j + 1]
        if j == len(prof) - 2:
            z1 += ext_top
        L = math.hypot(r1 - r0, z1 - z0)
        tilt = math.atan2(r1 - r0, z1 - z0)
        rm = (r0 + r1) / 2
        wdt = 2 * math.pi * (rm + thick) / n * 1.15
        nr, nz = math.cos(tilt), -math.sin(tilt)
        c_r, c_z = rm + nr * thick / 2, (z0 + z1) / 2 + nz * thick / 2
        for i in range(n):
            ang = 2 * math.pi * (i + 0.5 * (j % 2)) / n
            rot = Matrix.Rotation(ang, 3, 'Z') @ Matrix.Rotation(tilt, 3, 'Y')
            obs.append(_box(f'{prefix}{j}_{i}', Vector((c_r * math.cos(ang), c_r * math.sin(ang), c_z)) * K,
                            Vector((thick, wdt, L * 1.02)) * K, rot, coll))
    return obs


def _rb_add(scene, objs, kind):
    vl = scene.view_layers[0]
    for o in vl.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.rigidbody.objects_add(type=kind)


def simulate_beans(a, proxy_meshes):
    """Bullet simulacija u uvećanom svetu (lokalne koordinate levka x10) u istoj sceni, pa se sve fizičko
    briše. Vraća (oblik[n], položaj[n, F, 3] i kvaternion[n, F, 4] lokalno u m, kadrovi scene[F])."""
    sc = bpy.context.scene
    K = PHYS_K
    plan = physics_plan(a)
    f0, f1 = sf(-45), sf(G_GRIND[1] + 1)
    sc.frame_start, sc.frame_end = f0, f1
    old_g = tuple(sc.gravity)
    sc.gravity = (0.0, 0.0, -9.81 * K)
    coll = bpy.data.collections.new('Fizika')
    sc.collection.children.link(coll)
    walls = _staves('Levak', HOP_IN, 40, 0.008, coll, ext_top=0.03)
    walls += _staves('Grlo', [(0.0362, 0.085), (0.0362, 0.2000)], 24, 0.008, coll)
    bpy.ops.rigidbody.world_add()
    rbw = sc.rigidbody_world
    rbw.substeps_per_frame = a.podkoraci
    rbw.solver_iterations = 20
    rbw.use_split_impulse = True
    rbw.time_scale = SLOW
    rbw.point_cache.frame_start, rbw.point_cache.frame_end = f0, f1
    _rb_add(sc, walls, 'PASSIVE')
    for w in walls:
        w.rigid_body.collision_shape = 'BOX'
        w.rigid_body.friction, w.rigid_body.restitution = 0.5, 0.1
    # klip u grlu: od G50 se spušta (mlevenje), pa gomila u sredini tone; grlo je u neprovidnom kućištu
    piston = _box('Klip', Vector((0, 0, 0.2000 - 0.005)) * K, Vector((0.07, 0.07, 0.01)) * K, Matrix.Identity(3), coll)
    _rb_add(sc, [piston], 'PASSIVE')
    piston.rigid_body.collision_shape = 'BOX'
    piston.rigid_body.kinematic = True
    for g in range(50, G_GRIND[1] + 2):
        piston.location.z = (0.2000 - 0.005 - a.odvod * smoothstep(50, 96, g)) * K
        piston.keyframe_insert('location', index=2, frame=sf(g))

    beans, rel_frames = [], []
    vq = a.traka * SLOW / FPS
    for idx, (shape, (x, y, z), rot, t_rel) in enumerate(plan):
        ob = bpy.data.objects.new(f'ZF{idx:04d}', proxy_meshes[shape])
        coll.objects.link(ob)
        ob.rotation_euler = rot
        if t_rel is None:
            ob.location = Vector((x, y, z)) * K
            rel_frames.append(None)
        else:
            rel = max(int(math.floor(t_rel)), -44)
            frac = t_rel - rel
            z_at = z + vq * frac
            rr = random.Random(idx)
            w = Vector(tuple(rr.uniform(-1, 1) for _ in range(3))) * (10 * SLOW / FPS)
            ob.location = Vector((x, y, z_at + vq * (rel + 45))) * K
            ob.keyframe_insert('location', frame=f0)
            ob.keyframe_insert('rotation_euler', frame=f0)
            ob.location = Vector((x, y, z_at)) * K
            ob.rotation_euler = Vector(rot) + w * (rel + 45)
            ob.keyframe_insert('location', frame=sf(rel))
            ob.keyframe_insert('rotation_euler', frame=sf(rel))
            rel_frames.append(rel)
        beans.append(ob)
    _rb_add(sc, beans, 'ACTIVE')
    for ob, rel in zip(beans, rel_frames):
        rb = ob.rigid_body
        rb.collision_shape = 'CONVEX_HULL'
        rb.mass = 0.05
        rb.friction = 0.6
        rb.restitution = 0.15
        rb.use_margin = True
        rb.collision_margin = 0.0004 * K
        rb.linear_damping = 0.05
        rb.angular_damping = 0.3
        if rel is not None:
            rb.kinematic = True
            ob.keyframe_insert('rigid_body.kinematic', frame=f0)
            ob.keyframe_insert('rigid_body.kinematic', frame=sf(rel))
            rb.kinematic = False
            ob.keyframe_insert('rigid_body.kinematic', frame=sf(rel) + 1)
    t0 = time.time()
    with bpy.context.temp_override(scene=sc):
        bpy.ops.ptcache.bake_all(bake=True)
    print(f'GRIND fizika: {len(beans)} zrna, {f1 - f0 + 1} kadrova, bake {time.time() - t0:.0f} s', flush=True)
    frames = list(range(sf(G_GRIND[0]) - 1, sf(G_GRIND[1]) + 2))
    pos = np.zeros((len(beans), len(frames), 3), np.float32)
    quat = np.zeros((len(beans), len(frames), 4), np.float32)
    for fi, f in enumerate(frames):
        sc.frame_set(f)
        for bi, ob in enumerate(beans):
            mw = ob.matrix_world
            pos[bi, fi] = mw.translation / K
            quat[bi, fi] = mw.to_quaternion()
    # očisti fiziku (render ide bez Bullet-a: zrna dobijaju ključne kadrove iz keša)
    bpy.ops.rigidbody.world_remove()
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob)
    bpy.data.collections.remove(coll)
    sc.gravity = old_g
    rel = np.array([-999 if r is None else r for r in rel_frames], np.int32)
    return np.array([p[0] for p in plan], np.int32), pos, quat, np.array(frames, np.int32), rel


def beans_cached(a, proxy_meshes):
    key = C.source_key(physics_plan, r_hopper, simulate_beans, _staves, bean_shape, bean_bm,
                       (a.seed, a.punjenje, a.tok, a.traka, a.odvod, a.podkoraci, PHYS_K, SLOW, G_OFF, HOP_IN))
    path = CACHE / f'zrna_{key}.npz'
    if path.exists() and not a.ponovo_fizika:
        d = np.load(path)
        print(f'GRIND fizika iz keša {path.name}', flush=True)
        return d['shape'], d['pos'], d['quat'], d['frames'], d['rel']
    for old in CACHE.glob('zrna_*.npz'):
        old.unlink()
    res = simulate_beans(a, proxy_meshes)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, shape=res[0], pos=res[1], quat=res[2], frames=res[3], rel=res[4])
    return res


def _fcurves(ob, path, frames, values, interp='LINEAR'):
    """Ključni kadrovi iz niza (values[F, k]) preko channelbag API-ja (Blender 5: slotted actions)."""
    ad = ob.animation_data or ob.animation_data_create()
    if ad.action is None:
        act = bpy.data.actions.new(ob.name)
        ad.action = act
        ad.action_slot = act.slots.new(id_type='OBJECT', name=ob.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(ad.action, ad.action_slot)
    values = np.asarray(values, np.float32).reshape(len(frames), -1)
    ip = {'CONSTANT': 0, 'LINEAR': 1}[interp]
    for i in range(values.shape[1]):
        fc = cb.fcurves.new(path, index=i)
        kp = fc.keyframe_points
        kp.add(len(frames))
        co = np.empty(2 * len(frames), np.float32)
        co[0::2], co[1::2] = frames, values[:, i]
        kp.foreach_set('co', co)
        kp.foreach_set('interpolation', [ip] * len(frames))
        fc.update()


def place_beans(shape, pos, quat, frames, rel, M, render_meshes):
    """Render zrna u svetu (M @ lokalno); zrna koja se ne pomeraju u G1-G96 nemaju animaciju."""
    coll = bpy.data.collections.new('Zrna')
    bpy.context.scene.collection.children.link(coll)
    Mq = M.to_quaternion()
    Mt = np.array(M, np.float64)
    wpos = (pos.astype(np.float64) @ Mt[:3, :3].T) + Mt[:3, 3]
    objs, moving, hidden = [], 0, 0
    for i in range(len(shape)):
        q = quat[i].astype(np.float64)
        wq = np.empty_like(q)
        for fi in range(len(frames)):                # svet = M.rot @ lokalno
            wq[fi] = tuple(Mq @ Quaternion(q[fi]))
        for fi in range(1, len(frames)):             # bez skoka znaka (q i -q su ista rotacija)
            if np.dot(wq[fi], wq[fi - 1]) < 0:
                wq[fi] = -wq[fi]
        lp = pos[i]
        r = np.hypot(lp[:, 0], lp[:, 1])
        escaped = bool(np.any((r > 0.094) & (lp[:, 2] < 0.33)) or np.any(lp[:, 2] < 0.08))
        ob = bpy.data.objects.new(f'Zrno{i:04d}', render_meshes[shape[i]])
        coll.objects.link(ob)
        ob.rotation_mode = 'QUATERNION'
        ob.location = tuple(wpos[i, 0])
        ob.rotation_quaternion = tuple(wq[0])
        if escaped:
            ob.hide_render = True
            hidden += 1
            continue
        dp = np.abs(wpos[i] - wpos[i, 0]).max()
        dq = 1.0 - np.abs(wq @ wq[0]).min()
        if dp > 2e-5 or dq > 1e-6:
            _fcurves(ob, 'location', frames, wpos[i])
            _fcurves(ob, 'rotation_quaternion', frames, wq)
            moving += 1
        if rel[i] > -999 and sf(rel[i]) > frames[0]:   # zrno iz mlaza: skriveno dok je na „traci“
            vis = (np.array(frames) < sf(rel[i])).astype(np.float32)
            _fcurves(ob, 'hide_render', frames, vis, interp='CONSTANT')
        objs.append(ob)
    print(f'GRIND zrna: {len(objs)} u renderu, {moving} animirano, {hidden} pobeglo (sakriveno)', flush=True)
    return objs


# ================================================================ scena

def parse():
    p = argparse.ArgumentParser(prog='grind.py')
    p.add_argument('--out', required=True, help='folder za kadar_GGGG.png i anchors.json')
    p.add_argument('--kadrovi', default='sve', help='"sve" ili lista G, npr. 1,48,84')
    p.add_argument('--res', type=int, default=1200, help='širina kadra u px (visina = 1,25 x)')
    p.add_argument('--uzorci', type=int, default=64)
    p.add_argument('--adaptive', type=float, default=0.02)
    p.add_argument('--rot', type=float, default=-25.0, help='okret mlina oko otvora (stepeni)')
    p.add_argument('--fstop', type=float, default=FSTOP)
    p.add_argument('--key', type=float, default=70.0)
    p.add_argument('--strip', type=float, default=6.0)
    p.add_argument('--punjenje', type=int, default=1450, help='zrna u levku pre G1')
    p.add_argument('--tok', type=float, default=4.0, help='zrna po kadru u mlazu odozgo')
    p.add_argument('--traka', type=float, default=0.6, help='brzina zrna pri puštanju, m/s (stvarno vreme)')
    p.add_argument('--odvod', type=float, default=0.06, help='koliko se klip u grlu spusti G50-G96 (m)')
    p.add_argument('--mleveno', type=int, default=600, help='čestica mlevene kafe po kadru')
    p.add_argument('--odsjaj', type=float, default=3.0, help='blenda levo-napred (samo odsjaj), W')
    p.add_argument('--podkoraci', type=int, default=10)
    p.add_argument('--seed', type=int, default=SEED)
    p.add_argument('--poster', action='store_true', help='poster.png = G1')
    p.add_argument('--bez-zamucenja', dest='bez_zamucenja', action='store_true', help='bez motion blur-a')
    p.add_argument('--ponovo-fizika', dest='ponovo_fizika', action='store_true')
    p.add_argument('--bez-rendera', dest='bez_rendera', action='store_true')
    return p.parse_args(C.args())


def build(a):
    sc = C.reset()
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    render_meshes, proxy_meshes, _ = bean_meshes()
    shape, pos, quat, frames, rel = beans_cached(a, proxy_meshes)
    for pm in proxy_meshes:
        bpy.data.meshes.remove(pm)

    render_setup(sc, a.res, round(a.res * GRIND_H), a.uzorci, a.adaptive, motion_blur=not a.bez_zamucenja)
    sc.frame_start, sc.frame_end = sf(G_GRIND[0]), sf(G_GRIND[1])
    C.world_hdri(sc, 0.15)
    cam = rig_camera(sc, 'grind', a.res, a.fstop)
    transmission_card(sc, BG_GRIND, LIGHT_TARGET)

    M = grinder_matrix(a.rot)
    parts = build_grinder(M)
    beans = place_beans(shape, pos, quat, frames, rel, M, render_meshes)
    em, crumbs = build_grounds(sc, a.mleveno, end_g=G_GRIND[1] + 1)
    metal = [o for o in parts if o.active_material and o.active_material.name.startswith('Inox')]
    lights(sc, 'grind', parts, crumbs, key=a.key, strip=a.strip, refl=a.odsjaj, refl_subjects=metal)
    # (trake i blenda samo na mlin: na zrnima bi ih isprale u sivo)
    bake_particles(sc)
    return sc, cam, M


def write_anchors(out, data):
    (pathlib.Path(out) / 'anchors.json').write_text(json.dumps(data, indent=1, ensure_ascii=False))


def frame_list(spec, g_range):
    if spec == 'sve':
        return list(range(g_range[0], g_range[1] + 1))
    return [int(x) for x in spec.split(',') if x.strip()]


def main():
    a = parse()
    t0 = time.time()
    sc, cam, M = build(a)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sc.frame_set(sf(1))
    ox, oy = project(sc, cam, SPOUT_W, 'grind')
    write_anchors(out, {'id': 'grind', 'units': 'S od gornjeg levog ugla punog kadra (W 1, H 1,25)',
                        'full': {'W': 1, 'H': GRIND_H}, 'osa_x': round(project(sc, cam, (0, 0, 0.6), 'grind')[0], 4),
                        'otvor': {'x': round(ox, 4), 'y': round(oy, 4)}, 'g_od': G_GRIND[0], 'g_do': G_GRIND[1],
                        'generator': 'scripts/blender/kafa/grind.py'})
    print(f'GRIND scena {time.time() - t0:.0f} s; otvor u kadru ({ox:.4f}, {oy:.4f}) S', flush=True)
    if a.bez_rendera:
        return
    for g in frame_list(a.kadrovi, G_GRIND):
        t1, c1 = time.time(), time.process_time()
        sc.frame_set(sf(g))
        sc.render.filepath = str(out / f'kadar_{g:04d}.png')
        bpy.ops.render.render(write_still=True)
        cpu = time.process_time() - c1
        print(f'GRIND kadar G{g}: {time.time() - t1:.1f} s zidno, {cpu:.0f} CPU-s (~{cpu / 4:.0f} s na 4 slobodna jezgra)',
              flush=True)
    if a.poster:
        p1 = out / 'kadar_0001.png'
        if not p1.exists():
            sc.frame_set(sf(1))
            sc.render.filepath = str(p1)
            bpy.ops.render.render(write_still=True)
        (out / 'poster.png').write_bytes(p1.read_bytes())


if __name__ == '__main__':
    main()
