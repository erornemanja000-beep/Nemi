"""Stojeće kese kafe (doypack sa ravnim dnom, zipper gore, mat papir) za staklene kartice u sekciji SIP.

Tri statična rendera, boje kao u referentnom videu. Etiketa je za sada samo obojene površine i pruge,
bez teksta i bez tekstura sa interneta; prave natpise daje dizajner (studio/kafa-skrol/dizajn/).
  origin  krem kesa, crveno-koralna etiketa
  flavor  bež kesa, tirkizni talas i plava pruga
  roast   breskva-roze kesa, lososove mrlje i svetli luk

Pokretanje iz korena repoa (uslovi iz .claude/agents/blender-umetnik.md):
    unshare -n /opt/blender/blender -b --factory-startup --offline-mode -Y --python-exit-code 1 -t 4 \
      -P scripts/blender/kafa/bags.py -- --out <folder> [--bag origin|flavor|roast|all] [--res 800] [--samples 32]

Izlaz: <folder>/kesa_<ime>.png (RGBA, providna pozadina, senka sa shadow catcher-a).
"""
import argparse
import math
import pathlib
import sys

sys.dont_write_bytecode = True      # bez __pycache__ u repou
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import common as C  # noqa: E402
from sip import Nodes, new_material, smoothstep  # noqa: E402  (pomoćne funkcije za čvorove)

import bpy  # noqa: E402

W = 0.120        # širina prednje strane (m)
D = 0.075        # dubina dna (bočni nabor)
HB = 0.200       # visina tela do vara
SEAL = 0.016     # visina gornjeg vara
ZIP_Z = HB - 0.021


def srgb(hex_color):
    """'#RRGGBB' -> linearne RGB vrednosti za shader."""
    h = hex_color.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


# palete iz kadrova videa (približno; konačne boje dolaze od dizajnera)
DESIGNS = {
    'origin': {'base': '#E8DDCB', 'label': '#C4513C', 'label_dark': '#963629', 'accent': '#E8DDCB'},
    'flavor': {'base': '#E6D6BF', 'teal': '#2B9AA2', 'blue': '#1E5C86', 'mint': '#8FCBC6'},
    'roast': {'base': '#EDB8A0', 'blob': '#D8826A', 'arc': '#F6ECE4', 'line': '#C46C56'},
}


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


def build_bag():
    rings = [ring(0.0, 0.0), ring(0.0, 0.0012), ring(0.0, 0.0030)]
    # dno: prvi prsten malo uvučen (zaobljena ivica dna)
    rings[0] = [(x * 0.975, y * 0.95, z) for x, y, z in rings[0]]
    rings[1] = [(x * 0.993, y * 0.985, z) for x, y, z in rings[1]]
    weights = [0.1, 0.1, 0.1]
    n_body = 72
    for k in range(1, n_body + 1):
        t = k / n_body
        z = 0.0030 + (HB - 0.0030) * t
        rings.append(ring(t, z))
        weights.append(0.25 + 0.75 * smoothstep(0.50, 1.0, t))
    for z in (HB + 0.004, HB + 0.010, HB + SEAL):               # gornji var: ravna traka
        r = [(x * 1.004, y * 0.75, z) for x, y, _ in ring(1.0, z)]
        rings.append(r)
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
    ob = bpy.data.objects.new('Bag', me)
    bpy.context.collection.objects.link(ob)
    C.smooth(ob)
    # nabori papira, jači pri vrhu gde se kesa spljošti
    vg = ob.vertex_groups.new(name='wrinkle')
    for k, w in enumerate(weights):
        vg.add(list(range(k * m, (k + 1) * m)), w, 'REPLACE')
    for name, kind, size, strength in (('Folds', 'CLOUDS', 0.028, 0.0026), ('Crinkle', 'CLOUDS', 0.008, 0.0006)):
        tex = bpy.data.textures.new(name, kind)
        tex.noise_scale = size
        mod = ob.modifiers.new(name, 'DISPLACE')
        mod.texture, mod.texture_coords, mod.strength, mod.mid_level = tex, 'LOCAL', strength, 0.5
        mod.vertex_group = 'wrinkle'
    return ob


# ---------------------------------------------------------------- materijal
def mat_bag(bag, name):
    pal = {k: srgb(v) for k, v in DESIGNS[name].items()}
    m, nt, bsdf, N = new_material(f'Bag_{name}')
    tc = N.new('ShaderNodeTexCoord', object=bag)
    P = tc.outputs['Object']
    x, _, z = N.sep(P)
    _, ny, _ = N.sep(tc.outputs['Normal'])
    front = N.mul(N.ramp(ny, -0.45, -0.70), N.ramp(z, HB - 0.004, HB - 0.012))   # štampa samo spreda, ispod vara

    def box(cx, cz, hx, hz, rad):
        dx = N.math('MAXIMUM', N.sub(N.math('ABSOLUTE', N.sub(x, cx)), hx - rad), 0.0)
        dz = N.math('MAXIMUM', N.sub(N.math('ABSOLUTE', N.sub(z, cz)), hz - rad), 0.0)
        return N.sub(N.vmath('LENGTH', N.xyz(dx, dz, 0.0)), rad)

    def circle(cx, cz, rad):
        return N.sub(N.vmath('LENGTH', N.xyz(N.sub(x, cx), N.sub(z, cz), 0.0)), rad)

    def fill(dist):
        return N.mul(N.ramp(dist, -0.00025, 0.00025, 1.0, 0.0), front)

    def band(lo, hi, var=z):
        return N.mul(N.mul(N.ramp(var, lo - 0.0002, lo + 0.0002), N.ramp(var, hi - 0.0002, hi + 0.0002, 1.0, 0.0)), front)

    col = pal['base']
    relief = 0.0
    if name == 'origin':
        lab = box(0.0, 0.098, 0.047, 0.054, 0.007)
        col = N.mix(fill(lab), col, pal['label'])
        col = N.mix(band(0.060, 0.066), col, pal['label_dark'])
        col = N.mix(band(0.070, 0.0715), col, pal['label_dark'])
        col = N.mix(fill(circle(0.0, 0.124, 0.011)), col, pal['accent'])       # mesto za znak
        col = N.mix(band(0.163, 0.1655), col, pal['label'])
        relief = N.mul(N.ramp(lab, -0.0003, 0.0, 1.0, 0.0), 0.00012)          # nalepljena etiketa
    elif name == 'flavor':
        wave_top = N.math('MULTIPLY_ADD', N.math('SINE', N.math('MULTIPLY_ADD', x, 42.0, 0.6)), 0.010, 0.128)
        diag = N.math('MULTIPLY_ADD', x, 0.42, 0.083)
        teal = N.mul(N.ramp(N.sub(z, wave_top), -0.00025, 0.00025, 1.0, 0.0), N.ramp(N.sub(z, diag), -0.00025, 0.00025))
        col = N.mix(N.mul(teal, front), col, pal['teal'])
        blue = N.mul(N.ramp(N.sub(z, diag), -0.00025, 0.00025),
                     N.ramp(N.sub(z, N.add(diag, 0.016)), -0.00025, 0.00025, 1.0, 0.0))
        col = N.mix(N.mul(N.mul(blue, N.ramp(x, -0.020, -0.012)), front), col, pal['blue'])
        mint = N.mul(N.ramp(N.sub(z, N.sub(diag, 0.012)), -0.0002, 0.0002),
                     N.ramp(N.sub(z, N.sub(diag, 0.008)), -0.0002, 0.0002, 1.0, 0.0))
        col = N.mix(N.mul(mint, front), col, pal['mint'])
        col = N.mix(band(0.160, 0.1625), col, pal['teal'])
    elif name == 'roast':
        col = N.mix(fill(circle(0.022, 0.100, 0.046)), col, pal['blob'])
        arc = N.math('ABSOLUTE', N.sub(N.vmath('LENGTH', N.xyz(N.add(x, 0.060), N.sub(z, 0.020), 0.0)), 0.092))
        col = N.mix(fill(N.sub(arc, 0.0075)), col, pal['arc'])
        col = N.mix(fill(circle(-0.030, 0.150, 0.012)), col, pal['blob'])
        col = N.mix(band(0.163, 0.1655), col, pal['line'])
        col = N.mix(band(0.040, 0.0415), col, pal['line'])

    # var i zipper: malo tamniji papir, rebrasti var, dva ispupčenja zippera
    seal = N.ramp(z, HB - 0.001, HB + 0.002)
    col = N.mix(N.mul(seal, 0.12), col, (0.0, 0.0, 0.0))
    crimp = N.mul(N.math('SINE', N.mul(x, 2 * math.pi / 0.0011)),
                  N.mul(N.ramp(z, HB + 0.003, HB + 0.004), N.ramp(z, HB + 0.012, HB + 0.013, 1.0, 0.0)))
    zipper = N.add(N.ramp(N.math('ABSOLUTE', N.sub(z, ZIP_Z)), 0.0, 0.0013, 1.0, 0.0),
                   N.ramp(N.math('ABSOLUTE', N.sub(z, ZIP_Z - 0.0032)), 0.0, 0.0011, 1.0, 0.0))
    fiber = N.noise(P, 3500.0, detail=2)
    height = N.add(N.add(N.mul(crimp, 0.00012), N.mul(zipper, 0.00045)), N.mul(fiber, 0.000012))
    if not isinstance(relief, float):
        height = N.add(height, relief)

    N.put(col, bsdf.inputs['Base Color'])
    N.put(N.math('MULTIPLY_ADD', fiber, 0.10, 0.58), bsdf.inputs['Roughness'])
    bsdf.inputs['Specular IOR Level'].default_value = 0.32
    bsdf.inputs['Sheen Weight'].default_value = 0.2
    bsdf.inputs['Sheen Roughness'].default_value = 0.45
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
    ap.add_argument('--res', type=int, default=800)
    ap.add_argument('--samples', type=int, default=48)
    ap.add_argument('--exposure', type=float, default=-2.1)
    ap.add_argument('--turn', type=float, default=-24.0, help='blago iskošen pogled (° oko Z)')
    args = ap.parse_args(C.args())

    scene = C.reset()
    C.render_settings(scene, width=args.res, height=args.res, samples=args.samples, transparent=True)
    scene.view_settings.exposure = args.exposure
    C.world(scene)
    C.studio_lights()
    C.shadow_catcher()
    bag = build_bag()
    bag.rotation_euler = (0.0, 0.0, math.radians(args.turn))
    elev, dist, target = math.radians(9.0), 0.74, (0.0, 0.0, 0.106)
    C.camera((0.0, -dist * math.cos(elev), target[2] + dist * math.sin(elev)), target, lens=85)

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name in (DESIGNS if args.bag == 'all' else [args.bag]):
        C.assign(bag, mat_bag(bag, name))
        scene.render.filepath = str(out / f'kesa_{name}.png')
        bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    main()
