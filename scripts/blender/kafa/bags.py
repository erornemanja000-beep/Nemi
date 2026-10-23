"""Stojeće kese kafe KORN / KANNE (doypack sa ravnim dnom, zipper gore, mat papir) za staklene kartice u
sekciji SIP i za prodavnicu. Foto-studio verzija (23.10.2026).

Etikete su prave, od dizajnera (studio/kafa-skrol/dizajn/etiketa-{origin,flavor,roast}.png, 2048 x 3072,
specifikacija u etiketa.md): štampa na prednjoj strani 120 x 180 mm, UV po nedeformisanom obliku kese
(nabori papira ne krive natpis), sRGB, Cubic, EXTEND (ispod dna se nastavlja boja talasa, iznad papir).
Bokovi i leđa uzimaju ivicu slike (samo boja papira i talasa, bez teksta). Ventil Ø 16 mm na x=0, z=158 mm.
Mat papir sa sitnim vlaknima; reljef je blag, da natpis ostane oštar.

Svetlo je isti foto-studio kao šolja i mlin (common.photo_studio_lights, tamna HDRI okolina 0,15), a view
transform je Khronos PBR Neutral (storyboard 6: boje etikete ostaju verne; sekvence su na AgX-u).
  origin  papir #EEE5D5, talas #AD4731 (crveno-koralna),  3/4 sleva
  flavor  papir #E6D6BF, talas #3A9A96 (tirkiz),          skoro spreda
  roast   papir #EDB8A0, talas #D8826A (breskva),         3/4 zdesna

Pokretanje iz korena repoa (uslovi iz .claude/agents/blender-umetnik.md):
    unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \\
      -P scripts/blender/kafa/bags.py -- --out <folder> [--bag origin|flavor|roast|all] [--res 900] [--samples 128]

Izlaz: <folder>/kesa_<ime>.png (RGBA 4:5, npr. 900 x 1125; providna pozadina, senka sa shadow catcher-a).
"""
import argparse
import math
import pathlib
import sys
import time

sys.dont_write_bytecode = True      # bez __pycache__ u repou
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as C  # noqa: E402

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

REPO = HERE.parents[2]
LABELS = REPO / 'studio' / 'kafa-skrol' / 'dizajn'

W = 0.120        # širina prednje strane (m)
D = 0.075        # dubina dna (bočni nabor)
HB = 0.200       # visina tela do vara
SEAL = 0.016     # visina gornjeg vara
ZIP_Z = HB - 0.021
LABEL_Z = (0.010, 0.190)    # etiketa pokriva z 10-190 mm (etiketa.md, odeljak 2)
VALVE = (0.0, 0.158, 0.008)  # ventil: x, z, poluprečnik (m)

# boje iz etiketa.md (odeljak 3) i ugao pogleda po kesi (storyboard 6: 3/4 sleva / spreda / 3/4 zdesna)
DESIGNS = {
    'origin': {'paper': '#EEE5D5', 'turn': -24.0},
    'flavor': {'paper': '#E6D6BF', 'turn': 7.0},
    'roast': {'paper': '#EDB8A0', 'turn': 24.0},
}


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- model
def ring(t, z, n1=22, n2=8, n3=10):
    """Presek kese na visini t (0 dno, 1 var): pravougaonik sa zaobljenim uglovima koji se ka vrhu spljošti."""
    s = min(max((t - 0.40) / 0.60, 0.0), 1.0)
    b = max(0.0013, D / 2 * math.cos(math.pi / 2 * s) ** 1.15)
    a = W / 2 * (1 + 0.025 * smoothstep(0.55, 1.0, t))
    rc = min(0.0045, b * 0.9)
    bulge = 0.0065 * math.sin(math.pi * min(t, 1.0)) ** 0.8          # kesa puna zrna je „naduvana"
    q = []
    for i in range(n1):
        q.append(((a - rc) * i / n1, -b))
    for i in range(n2):
        ang = -math.pi / 2 + math.pi / 2 * i / n2
        q.append((a - rc + rc * math.cos(ang), -b + rc + rc * math.sin(ang)))
    for i in range(n3 + 1):
        q.append((a, -b + rc + (b - rc) * i / n3))
    loop = (q[:-1] + [(x, -y) for x, y in reversed(q)][:-1]
            + [(-x, -y) for x, y in q][:-1] + [(-x, y) for x, y in reversed(q)][:-1])
    out = []
    for x, y in loop:
        k = max(0.0, 1 - (x / a) ** 2)
        y = y - bulge * k if y < -1e-9 else (y + bulge * k if y > 1e-9 else y)
        out.append((x, y, z))
    return out


def label_uv(x, z, back):
    """UV etikete iz etiketa.md: u = (x + 0,060) / 0,120, v = (z - 0,010) / 0,180; leđa uzimaju levu ivicu
    slike (samo boja, bez natpisa u ogledalu)."""
    u = 0.0 if back else (x + W / 2) / W
    return u, (z - LABEL_Z[0]) / (LABEL_Z[1] - LABEL_Z[0])


def build_bag():
    rings = [ring(0.0, 0.0), ring(0.0, 0.0012), ring(0.0, 0.0030)]
    rings[0] = [(x * 0.975, y * 0.95, z) for x, y, z in rings[0]]      # zaobljena ivica dna
    rings[1] = [(x * 0.993, y * 0.985, z) for x, y, z in rings[1]]
    weights = [0.1, 0.1, 0.1]
    n_body = 96
    for k in range(1, n_body + 1):
        t = k / n_body
        z = 0.0030 + (HB - 0.0030) * t
        rings.append(ring(t, z))
        # nabori: slabi gde je natpis (z 18-143 mm), jači pri vrhu gde se kesa spljošti
        weights.append(0.12 + 0.88 * smoothstep(0.72, 1.0, t))
    for z in (HB + 0.004, HB + 0.010, HB + SEAL):               # gornji var: ravna traka
        rings.append([(x * 1.004, y * 0.75, z) for x, y, _ in ring(1.0, z)])
        weights.append(0.35)

    m = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = []
    for k in range(len(rings) - 1):
        for i in range(m):
            faces.append((k * m + i, k * m + (i + 1) % m, (k + 1) * m + (i + 1) % m, (k + 1) * m + i))
    bot = len(verts)
    verts.append((0.0, 0.0, 0.0))
    for i in range(m):
        faces.append((bot, (i + 1) % m, i))
    top = len(verts)
    verts.append((0.0, 0.0, HB + SEAL))
    base = (len(rings) - 1) * m
    for i in range(m):
        faces.append((top, base + i, base + (i + 1) % m))

    me = bpy.data.meshes.new('Bag')
    me.from_pydata(verts, [], faces)
    me.update()
    # UV i maska prednje strane po NEdeformisanom obliku (pre nabora), pa se natpis ne krivi
    uv = me.uv_layers.new(name='UVMap')
    front = me.attributes.new('front', 'FLOAT', 'FACE')
    for p in me.polygons:
        back = p.normal.y > 0.30 or (p.center.y > 0.0 and abs(p.normal.x) < 0.8)
        front.data[p.index].value = 1.0 if (p.normal.y < -0.40 and p.center.z < HB - 0.002) else 0.0
        for li in p.loop_indices:
            x, _, z = verts[me.loops[li].vertex_index]
            uv.data[li].uv = label_uv(x, z, back)
    ob = bpy.data.objects.new('Bag', me)
    bpy.context.collection.objects.link(ob)
    C.smooth(ob)
    vg = ob.vertex_groups.new(name='wrinkle')
    for k, w in enumerate(weights):
        vg.add(list(range(k * m, (k + 1) * m)), w, 'REPLACE')
    for name, kind, size, strength in (('Folds', 'CLOUDS', 0.028, 0.0024), ('Crinkle', 'CLOUDS', 0.008, 0.0005)):
        tex = bpy.data.textures.new(name, kind)
        tex.noise_scale = size
        mod = ob.modifiers.new(name, 'DISPLACE')
        mod.texture, mod.texture_coords, mod.strength, mod.mid_level = tex, 'LOCAL', strength, 0.5
        mod.vertex_group = 'wrinkle'
    return ob


def build_valve(bag):
    """Okrugao plastični ventil Ø 16 mm (ispupčen ~1 mm, sa sitnim rupicama), zalepljen za površinu kese:
    mesto i normala se nalaze ray cast-om na deformisanoj kesi."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bag.evaluated_get(dg)
    x, z, r = VALVE
    hit, loc, nor, _ = ev.ray_cast(Vector((x, -0.5, z)), Vector((0.0, 1.0, 0.0)))
    if not hit:
        loc, nor = Vector((x, -0.022, z)), Vector((0.0, -1.0, 0.0))
    prof = [(r * 1.02, -0.0004), (r, 0.0), (r * 0.97, 0.0004), (r * 0.85, 0.0008), (r * 0.55, 0.0010),
            (0.0, 0.00105)]      # od ivice ka osi: normale lathe-a gledaju napolje (od kese)
    v = C.lathe('Ventil', prof, segments=64)
    v.location = loc - nor * 0.0002
    v.rotation_euler = nor.to_track_quat('Z', 'Y').to_euler()
    m, nt, b, N = C.new_material('Ventil')
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    holes, _ = N.voronoi(N.vmath('MULTIPLY', P, (1.0, 1.0, 0.0)), 900.0, randomness=0.0)
    rr = N.vmath('LENGTH', N.vmath('MULTIPLY', P, (1.0, 1.0, 0.0)))
    hm = N.mul(N.ramp(holes, 0.16, 0.10), N.ramp(rr, 0.0034, 0.0028))       # rupice samo u sredini
    N.put(N.mix(hm, (0.80, 0.78, 0.74), (0.05, 0.05, 0.05)), b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.38
    b.inputs['Specular IOR Level'].default_value = 0.4
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(N.mul(hm, -0.00015), bump.inputs['Height'])
    N.put(bump.outputs['Normal'], b.inputs['Normal'])
    C.assign(v, m)
    return v


# ---------------------------------------------------------------- materijal
def mat_bag(name):
    """Mat papir kese: boja iz etikete (UV), var 12 % tamniji, rebrasti var i zipper u reljefu, sitna vlakna."""
    path = LABELS / f'etiketa-{name}.png'
    img = bpy.data.images.load(str(path), check_existing=True)
    img.colorspace_settings.name = 'sRGB'
    m, nt, bsdf, N = C.new_material(f'Kesa_{name}')
    tex = N.new('ShaderNodeTexImage', interpolation='Cubic', extension='EXTEND')
    tex.image = img
    uvn = N.new('ShaderNodeUVMap', uv_map='UVMap')
    N.put(uvn.outputs['UV'], tex.inputs['Vector'])
    tc = N.new('ShaderNodeTexCoord')
    P = tc.outputs['Object']
    _, _, z = N.sep(P)
    x, _, _ = N.sep(P)
    col = tex.outputs['Color']
    seal = N.ramp(z, HB - 0.001, HB + 0.002)
    col = N.mix(N.mul(seal, 0.12), col, (0.0, 0.0, 0.0))
    crimp = N.mul(N.math('SINE', N.mul(x, 2 * math.pi / 0.0011)),
                  N.mul(N.ramp(z, HB + 0.003, HB + 0.004), N.ramp(z, HB + 0.012, HB + 0.013, 1.0, 0.0)))
    zipper = N.add(N.ramp(N.math('ABSOLUTE', N.sub(z, ZIP_Z)), 0.0, 0.0013, 1.0, 0.0),
                   N.ramp(N.math('ABSOLUTE', N.sub(z, ZIP_Z - 0.0032)), 0.0, 0.0011, 1.0, 0.0))
    fiber = N.noise(P, 3500.0, detail=2)
    mottle = N.noise(P, 120.0, detail=3)
    col = N.mix(N.mul(N.sub(mottle, 0.5), 0.10), col, N.tint(col, (0.93, 0.93, 0.93)))   # papir nije savršen
    height = N.add(N.add(N.mul(crimp, 0.00012), N.mul(zipper, 0.00045)), N.mul(fiber, 0.000006))
    N.put(col, bsdf.inputs['Base Color'])
    N.put(N.math('MULTIPLY_ADD', fiber, 0.08, 0.64), bsdf.inputs['Roughness'])
    bsdf.inputs['Specular IOR Level'].default_value = 0.30
    bsdf.inputs['Sheen Weight'].default_value = 0.15
    bsdf.inputs['Sheen Roughness'].default_value = 0.5
    bump = N.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value = 1.0
    N.put(height, bump.inputs['Height'])
    N.put(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


# ---------------------------------------------------------------- scena
def main():
    ap = argparse.ArgumentParser(prog='bags.py')
    ap.add_argument('--out', required=True)
    ap.add_argument('--bag', default='all', choices=['origin', 'flavor', 'roast', 'all'])
    ap.add_argument('--res', type=int, default=900, help='širina u px; visina je 1,25 x (4:5)')
    ap.add_argument('--samples', type=int, default=128)
    ap.add_argument('--view', default='neutral', choices=['neutral', 'agx'])
    ap.add_argument('--exposure', type=float, default=-0.6)
    ap.add_argument('--key', type=float, default=55.0)
    ap.add_argument('--strip', type=float, default=2.5, help='trake pozadi (na papiru 10 W pere boju)')
    args = ap.parse_args(C.args())

    scene = C.reset()
    C.photo_render_settings(scene, width=args.res, height=round(args.res * 1.25), samples=args.samples,
                            transparent=True, exposure=args.exposure)
    if args.view == 'neutral':
        scene.view_settings.view_transform = 'Khronos PBR Neutral'
        scene.view_settings.look = 'None'
    C.world_hdri(scene, 0.15)
    bag = build_bag()
    valve = build_valve(bag)
    valve.parent = bag
    valve.matrix_parent_inverse = bag.matrix_world.inverted()
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0, 0.3, 0))
    floor = bpy.context.active_object
    floor.name = 'Senka'
    floor.is_shadow_catcher = True
    C.photo_studio_lights((0.0, 0.0, 0.105), [bag, valve], None, key=args.key, strip=args.strip, flags=True)
    elev, dist, target = math.radians(9.0), 0.80, (0.0, 0.0, 0.112)
    cam = C.camera((0.0, -dist * math.cos(elev), target[2] + dist * math.sin(elev)), target, lens=85)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = dist - 0.02
    cam.data.dof.aperture_fstop = 8.0

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in (DESIGNS if args.bag == 'all' else [args.bag]):
        C.assign(bag, mat_bag(name))
        bag.rotation_euler = (0.0, 0.0, math.radians(DESIGNS[name]['turn']))
        t, c = time.time(), time.process_time()
        scene.render.filepath = str(out / f'kesa_{name}.png')
        bpy.ops.render.render(write_still=True)
        print(f'KESA {name}: {time.time() - t:.1f} s zidno, {time.process_time() - c:.0f} CPU-s', flush=True)


if __name__ == '__main__':
    main()
