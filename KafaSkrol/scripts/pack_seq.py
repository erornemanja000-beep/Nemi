#!/usr/bin/env python3
"""Kafa skrol: pakovanje Blender rendera sekvence (PNG RGBA) u WebP nivoe d/m (opciono l) i seq.json (plan-izrade.md, Z21).

    python3 -I KafaSkrol/scripts/pack_seq.py sip   <folder sa kadar_NNNN.png> [--offset 0]  [--frames 1-64]
    python3 -I KafaSkrol/scripts/pack_seq.py grind <folder>                    [--offset 0]  [--frames 1-63:2]
    python3 -I KafaSkrol/scripts/pack_seq.py pour  <folder>                    [--offset 64] [--frames 65-191:2]

  scena      sip | grind | pour (id foldera u public/media/seq, sat, g_od/g_do, pun kadar, isecak, budzet, posteri)
  folder     Blender izlaz: kadar_NNNN.png (RGBA, ceo kadar, 1200 px za S). Ako PNG ne postoji, uzima se
             kadar_NNNN.webp (rezervne kopije u studio/kafa-skrol/renderi/). anchors.json u istom folderu se
             upisuje u seq.json (sidra u S); bez njega se uzimaju sidra iz starog seq.json ili podrazumevana.
  --offset   NNNN = G - offset (POUR: kadar_LLLL, L = G - 64, pa --offset 64; GRIND i SIP: 0)
  --frames   lista globalnih kadrova G: 1,3,5 | 1-64 | 1-63:2 (svaki drugi). Bez nje: svi kadrovi iz foldera.
  --out      izlaz; podrazumevano KafaSkrol/public/media/seq/<scena>. Stari sadrzaj (d/, m/, l/, posteri,
             seq.json) se brise TEK kad je novi komplet gotov (pise se u susedni privremeni folder, pa se menja).

Nivoi (Interfejs 4): d = 1200 px za S, m = 800 px za S (Lanczos u premultiplied alfi, bez povecavanja), l samo uz
--levels d,m,l i izvor od najmanje --l-px. Fajl k (od 1) nivoa prikazuje G = g_od + (k-1) * every; ime je
uvek 0001.webp, 0002.webp ... (redni broj u nivou, ne G).
  m   svaki drugi kadar pocev od g_od (neparni G: S1, S3, ... S63)
  d   svi kadrovi; ako su stigli samo neparni, d ide sa `every: 2` (isti oblik kao m). Kad stignu i parni,
      isti poziv sa novim spiskom pravi `every: 1` i preimenuje fajlove: ceo d se pise iznova.
Poziv za samo neparne kadrove (npr. POUR): --frames 65-191:2. Skripta sama nalazi `every` svakog nivoa i
javlja ako kadrovi nisu niz bez rupa.

Obrada pre kodiranja (sve se ispisuje u izvestaju):
  - meki prag alfe --alpha-floor (4/255): alfa pada za 4 i razvlaci se nazad na 255, pa sum u repu senke i
    sitne mrlje postaju 0 bez stepenice (stedi ~15 % bajtova);
  - --fade-right A,B (S): senka koja bi ostala odsecena na ivici isecka bledi do 0 (SIP: 0,80 -> 1,0). Skripta
    prijavi ako bi se time taknuo neproziran piksel (alfa >= 250);
  - upozorenje kad na ivici isecka (osim otvorenih ivica scene) ostane alfa > 6 (tvrda ivica na stranici).
WebP: lossy, method 6, alpha_quality 85 (136 nivoa alfe: korak senke na tamnoj pozadini <= 1 nivo po kanalu), kvalitet --q-d / --q-m;
isti kvalitet za sve kadrove nivoa (kvalitet koji skace od kadra do kadra titra na skrolu). Samo uz --q-min se
kvalitet kadra koji prelazi budzet spusta za 2 do te vrednosti.

--check DIR: za prvi, srednji i poslednji kadar i poster upisuje u DIR kompozite na #6E3A27 i #E6DDCE
(referenca | dekodirani WebP | razlika x8, uvecano) i ispisuje odstupanje na ivicama (oreol).

Cita samo nase fajlove. Pillow + numpy, bez cwebp i ffmpeg-a, bez mreze.
"""
import argparse
import concurrent.futures
import io
import json
import os
import pathlib
import re
import shutil
import statistics
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = pathlib.Path(__file__).resolve().parent
SEQ_ROOT = HERE.parent / 'public' / 'media' / 'seq'
VERSION = 'render-1'
UNITS = 'S (stranica kvadrata kadra), od gornjeg levog ugla punog kadra; steps i kafa_y u kadrovima sata'
LEVEL_PX = {'l': 1600, 'd': 1200, 'm': 800}
LEVEL_Q = {'l': 78, 'd': 82, 'm': 72}
ALPHA_Q = 85
SKIP_ANCHOR_KEYS = {'id', 'units', 'full', 'g_od', 'g_do', 'generator', 'fajl'}
DARK, LIGHT = (0x6E, 0x3A, 0x27), (0xE6, 0xDD, 0xCE)

# Po sceni (plan, Interfejs 3 i 4; budzet po kadru iz storyboard-a 8).
#   poster: ('set', G) = kadar G nivoa ako ga nivo ima, ('file', G) = poseban poster-<nivo>.webp (najblizi dostupan kadar)
#   open: ivice isecka koje su namerno otvorene (mlaz prelazi u susednu sekvencu)
SCENES = {
    'grind': dict(clock='G', g_od=1, g_do=96, full=(1, 1.25), crop=(0.22, 0, 0.56, 1.25), budget={'d': 75, 'm': 40},
                  poster={'d': ('set', 1), 'm': ('set', 1)}, open={'top', 'bottom'}, fade_right=None,
                  steps=[('pin', 1, 64), ('prelaz', 65, 96)], anchors={'osa_x': 0.5},
                  zoom=(0.30, 0.55, 0.40, 0.40)),
    'pour': dict(clock='G', g_od=65, g_do=192, full=(1, 1), crop=(0.26, 0, 0.72, 1), budget={'d': 80, 'm': 42},
                 poster={'d': ('file', 150), 'm': ('file', 150)}, open={'top'}, fade_right=None,
                 steps=[('prelaz', 65, 96), ('pin', 97, 176), ('talas', 177, 192)], anchors={'osa_x': 0.5},
                 zoom=(0.30, 0.30, 0.40, 0.40)),
    # SIP: render ima providnu senku koja ide udesno do ivice kadra (alfa do 218 na x = 0,84 S), pa isecak ide do
    # x = 1,0 S, a senka bledi 0,80 -> 1,0 S. Drska se zavrsava na 0,79 S.
    'sip': dict(clock='S', g_od=1, g_do=64, full=(1, 1), crop=(0.20, 0, 0.80, 0.86), budget={'d': 60, 'm': 28},
                poster={'d': ('set', 64), 'm': ('file', 64)}, open=set(), fade_right=(0.80, 1.0),
                steps=[('talas', 1, 16), ('pin', 17, 64)], anchors={'osa_x': 0.5, 'sto_y': 0.78},
                zoom=(0.55, 0.28, 0.45, 0.45)),
}


def die(msg):
    sys.exit(f'pack_seq: {msg}')


# ---------------------------------------------------------------- ulaz
def parse_frames(spec):
    out = set()
    for tok in spec.split(','):
        m = re.fullmatch(r'\s*(\d+)(?:-(\d+)(?::(\d+))?)?\s*', tok)
        if not m:
            die(f'--frames: ne razumem "{tok}" (primeri: 1,3,5 | 1-64 | 1-63:2)')
        a = int(m.group(1))
        b = int(m.group(2) or a)
        step = int(m.group(3) or 1)
        out.update(range(a, b + 1, step))
    return sorted(out)


def find_inputs(src, offset):
    """G -> putanja kadra (PNG ima prednost nad WebP rezervnom kopijom)."""
    found = {}
    for p in sorted(src.iterdir()):
        m = re.fullmatch(r'kadar_(\d+)\.(png|webp)', p.name)
        if not m:
            continue
        g = int(m.group(1)) + offset
        if g not in found or p.suffix == '.png':
            found[g] = p
    return found


def pick_every(frames, g_od, g_do, strides):
    """Najmanji `every` iz `strides` za koji kadrovi g_od, g_od+every, ... stizu do kraja bez rupe.
    Vraca (every, kadrovi, opis) ili (None, [], opis rupa) kad nijedan ne staje."""
    have = set(frames)
    why = []
    for every in strides:
        seq = []
        g = g_od
        while g in have:
            seq.append(g)
            g += every
        if seq and seq[-1] > g_do - every:
            return every, seq, ''
        why.append(f'every {every}: niz staje na G{seq[-1] if seq else g_od}, fali G{g} (kraj je G{g_do})')
    return None, [], '; '.join(why)


# ---------------------------------------------------------------- obrada kadra
def load_rgba(path):
    return np.array(Image.open(path).convert('RGBA'))


def fade_zone_x(w_px, s_px, a0, a1):
    x = (np.arange(w_px) + 0.5) / s_px
    t = np.clip((x - a0) / (a1 - a0), 0.0, 1.0)
    return 1.0 - t * t * (3.0 - 2.0 * t), x


def prepare(arr, s_px, opts):
    """Alfa: bledenje desne senke i pod suma. RGB (neprozirna boja) se ne dira. Vraca (rgba, upozorenja)."""
    warn = []
    al = arr[..., 3].astype(np.float32)
    if opts['fade_right']:
        a0, a1 = opts['fade_right']
        k, x = fade_zone_x(arr.shape[1], s_px, a0, a1)
        zone = x > a0
        if (arr[..., 3][:, zone] >= 250).any():
            warn.append(f'neproziran piksel (alfa >= 250) u zoni bledenja x > {a0} S')
        al = al * k[None, :]
    f = float(opts['alpha_floor'])
    if f > 0:      # meki prag: alfa pada za f i razvlaci se nazad na 255, pa na repu senke nema stepenice
        al = np.maximum(al - f, 0.0) * (255.0 / (255.0 - f))
    al = np.rint(al).astype(np.uint8)
    out = arr.copy()
    out[..., 3] = al
    out[..., :3][al == 0] = 0
    return out, warn


def resample(rgba, box, size):
    """Lanczos u premultiplied alfi (float), zatim nazad u pravu alfu. Bez premultiply-a RGB ispod alfa=0 curi u ivice."""
    f = rgba.astype(np.float32) / 255.0
    a = f[..., 3]
    chans = [f[..., 0] * a, f[..., 1] * a, f[..., 2] * a, a]
    res = []
    for c in chans:
        r = Image.fromarray(np.ascontiguousarray(c)).resize(size, Image.LANCZOS, box=box)
        res.append(np.asarray(r, dtype=np.float32))
    a2 = np.clip(res[3], 0.0, 1.0)
    out = np.zeros((size[1], size[0], 4), np.uint8)
    safe = np.where(a2 > 1e-4, a2, 1.0)
    for i in range(3):
        out[..., i] = np.rint(np.clip(res[i] / safe, 0.0, 1.0) * 255.0).astype(np.uint8)
    out[..., 3] = np.rint(a2 * 255.0).astype(np.uint8)
    return out


def make_frame(path, level_px, geo, opts):
    """Ceo kadar -> prepared isecak na nivou `level_px`. geo = dict(full=(W,H), crop=(x0,y0,w,h))."""
    arr = load_rgba(path)
    fw, fh = geo['full']
    s_px = arr.shape[1] / fw
    if abs(arr.shape[0] / fh - s_px) > 0.51:
        die(f'{path.name}: {arr.shape[1]}x{arr.shape[0]} ne odgovara punom kadru {fw} x {fh} S')
    if level_px > s_px + 1e-6:
        die(f'{path.name}: izvor ima {s_px:g} px za S, nivo trazi {level_px} (bez povecavanja)')
    rgba, warn = prepare(arr, s_px, opts)
    x0, y0, w, h = geo['crop']
    size = (round(w * level_px), round(h * level_px))
    box = (x0 * s_px, y0 * s_px, (x0 + w) * s_px, (y0 + h) * s_px)
    if abs(level_px - s_px) < 1e-6:
        bx = [round(v) for v in box]
        out = rgba[bx[1]:bx[3], bx[0]:bx[2]]
        if (out.shape[1], out.shape[0]) != size:
            die(f'isecak {out.shape[1]}x{out.shape[0]} umesto {size[0]}x{size[1]}')
    else:
        out = resample(rgba, box, size)
        out[..., 3][out[..., 3] <= 1] = 0      # Lanczos zvonjenje u providnom delu
        out[..., :3][out[..., 3] == 0] = 0
    return np.ascontiguousarray(out), warn


def edge_alpha(img):
    a = img[..., 3]
    return {'top': int(a[0].max()), 'bottom': int(a[-1].max()), 'left': int(a[:, 0].max()), 'right': int(a[:, -1].max())}


def encode(img, q, aq):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, 'WEBP', quality=q, alpha_quality=aq, method=6)
    return buf.getvalue()


# ---------------------------------------------------------------- provera oreola
def composite(img, bg):
    f = img.astype(np.float32)
    a = f[..., 3:4] / 255.0
    return f[..., :3] * a + np.array(bg, np.float32) * (1.0 - a)


def halo_check(ref, data, label, outdir, zoom, geo):
    """ref = niz koji je ulazio u koder, data = WebP bajtovi. Vraca tekst izvestaja; slike u outdir."""
    dec = np.array(Image.open(io.BytesIO(data)).convert('RGBA'))
    al = ref[..., 3]
    opaque = np.array(Image.fromarray(((al >= 251) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    near = np.array(Image.fromarray(((al >= 251) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17))) > 0
    edge = opaque & (al < 255)                       # ivica predmeta: do 3 px od neprozirnog dela
    shadow = (al >= 9) & (al <= 250) & ~near         # senka: dalje od predmeta
    lines = []
    for name, bg in (('dark', DARK), ('light', LIGHT)):
        cr, cd = composite(ref, bg), composite(dec, bg)
        d = np.abs(cr - cd).max(axis=2)
        parts = []
        for tag, m in (('ivica', edge), ('senka', shadow)):
            v = d[m]
            parts.append(f'{tag} ({int(m.sum())} px) srednje {v.mean():.2f}, 99,9 % {np.percentile(v, 99.9):.1f}, max {v.max():.0f}, piksela > 2: {int((v > 2).sum())}')
        lines.append(f'    {label} na {name}: ' + '; '.join(parts) + f'; ceo kadar max {d.max():.0f}')
        h, w = ref.shape[:2]
        zx0, zy0, zw, zh = zoom
        fw, fh = geo['full']
        x0, y0 = geo['crop'][0], geo['crop'][1]
        px = w / geo['crop'][2]                      # px za S nivoa
        bx0, by0 = int((zx0 - x0) * px), int((zy0 - y0) * px)
        bx1, by1 = min(w, bx0 + int(zw * px)), min(h, by0 + int(zh * px))
        bx0, by0 = max(0, bx0), max(0, by0)
        sl = (slice(by0, by1), slice(bx0, bx1))
        panels = [cr[sl], cd[sl], np.clip(d[sl] * 8, 0, 255)[..., None].repeat(3, axis=2)]
        strip = np.concatenate([np.clip(p, 0, 255).astype(np.uint8) for p in panels], axis=1)
        im = Image.fromarray(strip)
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        im.save(outdir / f'halo_{label}_{name}.png')
        Image.fromarray(np.clip(cd, 0, 255).astype(np.uint8)).save(outdir / f'full_{label}_{name}.jpg', quality=90)
    return '\n'.join(lines)


# ---------------------------------------------------------------- radnik (proces)
def work(job):
    path = pathlib.Path(job['path'])
    img, warn = make_frame(path, job['px'], job['geo'], job['opts'])
    q = job['q']
    data = encode(img, q, job['aq'])
    while len(data) > job['budget'] * 1024 and q - 2 >= job['q_min']:
        q -= 2
        data = encode(img, q, job['aq'])
    pathlib.Path(job['dest']).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(job['dest']).write_bytes(data)
    res = dict(g=job['g'], level=job['level'], dest=job['dest'], bytes=len(data), q=q, warn=warn, edges=edge_alpha(img),
               size=(img.shape[1], img.shape[0]))
    if job.get('check'):
        res['halo'] = halo_check(img, data, job['check']['label'], pathlib.Path(job['check']['dir']), job['zoom'], job['geo'])
    return res


# ---------------------------------------------------------------- anchors i seq.json
def read_anchors(src, out, spec, explicit):
    path = pathlib.Path(explicit) if explicit else src / 'anchors.json'
    if path.is_file():
        data = json.loads(path.read_text(encoding='utf-8'))
        fw, fh = spec['full']
        if 'full' in data and (data['full'].get('W') != fw or data['full'].get('H') != fh):
            die(f'{path}: full {data["full"]} nije {fw} x {fh} kao u scenariju')
        return {k: v for k, v in data.items() if k not in SKIP_ANCHOR_KEYS}, f'{path}'
    old = out / 'seq.json'
    if old.is_file():
        try:
            data = json.loads(old.read_text(encoding='utf-8'))
            if isinstance(data.get('anchors'), dict):
                return data['anchors'], f'stari {old} (NEMA anchors.json u izvoru)'
        except ValueError:
            pass
    return dict(spec['anchors']), 'podrazumevana sidra iz skripte (NEMA anchors.json)'


def build_manifest(scene, spec, geo, sets, posters, anchors, version, packinfo):
    x0, y0, w, h = geo['crop']
    return {
        'id': scene, 'version': version, 'placeholder': False, 'clock': spec['clock'],
        'g_od': spec['g_od'], 'g_do': spec['g_do'], 'fps': 30,
        'full': {'W': geo['full'][0], 'H': geo['full'][1]},
        'crop': {'x0': x0, 'y0': y0, 'w': w, 'h': h},
        'sets': sets, 'poster': posters,
        'steps': [{'name': n, 'from': a, 'to': b} for n, a, b in spec['steps']],
        'anchors': anchors,
        'units': UNITS,
        'generator': 'KafaSkrol/scripts/pack_seq.py',
        'pack': packinfo,
    }


def swap_into_place(tmp, out, force):
    ours = {'d', 'm', 'l', 'seq.json'}
    if out.exists():
        extra = [p.name for p in out.iterdir() if p.name not in ours and p.suffix != '.webp']
        if extra and not force:
            die(f'{out}: ima i druge fajlove ({", ".join(extra)}); ne brisem bez --force')
        shutil.rmtree(out)
    tmp.rename(out)


# ---------------------------------------------------------------- glavno
def main():
    ap = argparse.ArgumentParser(prog='pack_seq.py', description=__doc__.split('\n')[0])
    ap.add_argument('scene', choices=sorted(SCENES))
    ap.add_argument('src', help='folder sa kadar_NNNN.png (i anchors.json)')
    ap.add_argument('--offset', type=int, default=0, help='NNNN = G - offset (POUR: 64)')
    ap.add_argument('--frames', help='lista G: 1,3,5 | 1-64 | 1-63:2')
    ap.add_argument('--out', help='izlaz (podrazumevano public/media/seq/<scena>)')
    ap.add_argument('--levels', default='d,m', help='d,m ili d,m,l')
    ap.add_argument('--l-px', type=int, default=LEVEL_PX['l'])
    ap.add_argument('--crop', help='x0,y0,w,h u S (preglasava scenu)')
    ap.add_argument('--anchors', help='anchors.json (podrazumevano <src>/anchors.json)')
    ap.add_argument('--version', default=VERSION)
    ap.add_argument('--q-d', type=int, default=LEVEL_Q['d'])
    ap.add_argument('--q-m', type=int, default=LEVEL_Q['m'])
    ap.add_argument('--q-l', type=int, default=LEVEL_Q['l'])
    ap.add_argument('--q-min', type=int, default=None,
                    help='spusti kvalitet kadra do ove vrednosti kad prelazi budzet (podrazumevano ne: isti q za sve kadrove)')
    ap.add_argument('--alpha-quality', type=int, default=ALPHA_Q)
    ap.add_argument('--alpha-floor', type=int, default=4, help='meki prag alfe (alfa -= f, pa nazad na 255); 0 = bez')
    ap.add_argument('--fade-right', help='A,B (S) ili none; preglasava scenu')
    ap.add_argument('--budget-d', type=float)
    ap.add_argument('--budget-m', type=float)
    ap.add_argument('--budget-l', type=float, default=120.0)
    ap.add_argument('--check', help='folder za provere oreola (kompoziti na tamnoj i svetloj pozadini)')
    ap.add_argument('--jobs', type=int, default=max(1, min(4, os.cpu_count() or 1)))
    ap.add_argument('--force', action='store_true', help='brisi i folder sa tudjim fajlovima')
    args = ap.parse_args()

    spec = SCENES[args.scene]
    src = pathlib.Path(args.src)
    if not src.is_dir():
        die(f'{src}: nije folder')
    out = pathlib.Path(args.out) if args.out else SEQ_ROOT / args.scene
    levels = [v.strip() for v in args.levels.split(',') if v.strip()]
    if any(v not in LEVEL_PX for v in levels) or 'd' not in levels or 'm' not in levels:
        die('--levels mora da ima d i m (i opciono l)')
    px = dict(LEVEL_PX, l=args.l_px)
    qs = {'l': args.q_l, 'd': args.q_d, 'm': args.q_m}
    budget = {'l': args.budget_l, 'd': args.budget_d or spec['budget']['d'], 'm': args.budget_m or spec['budget']['m']}
    crop = tuple(float(v) for v in args.crop.split(',')) if args.crop else spec['crop']
    if len(crop) != 4:
        die('--crop traži x0,y0,w,h')
    geo = {'full': spec['full'], 'crop': crop}
    fade = spec['fade_right']
    if args.fade_right:
        fade = None if args.fade_right == 'none' else tuple(float(v) for v in args.fade_right.split(','))
    opts = {'fade_right': fade, 'alpha_floor': args.alpha_floor}

    inputs = find_inputs(src, args.offset)
    avail = sorted(g for g in inputs if spec['g_od'] <= g <= spec['g_do'])
    if args.frames:
        want = parse_frames(args.frames)
        missing = [g for g in want if g not in inputs]
        if missing:
            die(f'nema kadrova u {src} za G: {missing[:12]}{" ..." if len(missing) > 12 else ""} (offset {args.offset})')
        avail = [g for g in want if spec['g_od'] <= g <= spec['g_do']]
    if not avail:
        die(f'nema kadrova G {spec["g_od"]}-{spec["g_do"]} u {src} (offset {args.offset}: kadar_NNNN, NNNN = G - {args.offset})')

    # koji kadrovi idu u koji nivo
    plan = {}
    for lv in levels:
        strides = (2,) if lv == 'm' else (1, 2)
        every, frames, why = pick_every(avail, spec['g_od'], spec['g_do'], strides)
        if not frames:
            die(f'nivo {lv}: kadrovi nisu niz bez rupa od G{spec["g_od"]} do G{spec["g_do"]} ({why}). '
                f'Kad render jos traje, spakuj kad stigne ceo niz (svi, ili samo svaki drugi uz --frames {spec["g_od"]}-{spec["g_do"]}:2).')
        plan[lv] = (every, frames)
    anchors, anchors_src = read_anchors(src, out, spec, args.anchors)

    # privremeni folder pored izlaza (isti fajl-sistem, pa je zamena jedan rename)
    tmp = out.parent / f'.{out.name}.pack-tmp'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    check_dir = pathlib.Path(args.check) if args.check else None
    if check_dir:
        check_dir.mkdir(parents=True, exist_ok=True)
    zoom = spec['zoom']

    try:
        jobs = []
        posters = {}
        sets = {}
        for lv in levels:
            every, frames = plan[lv]
            w_px, h_px = round(crop[2] * px[lv]), round(crop[3] * px[lv])
            sets[lv] = {'px': px[lv], 'w': w_px, 'h': h_px, 'count': len(frames), 'every': every}
            mid = frames[len(frames) // 2]
            for k, g in enumerate(frames, 1):
                job = dict(path=str(inputs[g]), g=g, level=lv, px=px[lv], geo=geo, opts=opts, q=qs[lv], q_min=args.q_min if args.q_min is not None else qs[lv],
                           aq=args.alpha_quality, budget=budget[lv], dest=str(tmp / lv / f'{k:04d}.webp'), zoom=zoom)
                if check_dir and g in (frames[0], mid, frames[-1]):
                    job['check'] = {'dir': str(check_dir), 'label': f'{lv}_G{g:03d}'}
                jobs.append(job)
            # poster
            kind, pg = spec['poster'][lv]
            have = set(frames)
            if kind == 'set' and pg in have:
                posters[lv] = f'{lv}/{frames.index(pg) + 1:04d}.webp'
            else:
                near = min(avail, key=lambda g: (abs(g - pg), g))
                if near != pg:
                    print(f'poster {lv}: G{pg} nije u izvoru, uzimam G{near}')
                posters[lv] = f'poster-{lv}.webp'
                pjob = dict(path=str(inputs[near]), g=near, level=lv, px=px[lv], geo=geo, opts=opts, q=qs[lv],
                            q_min=args.q_min if args.q_min is not None else qs[lv], aq=args.alpha_quality, budget=budget[lv] * 1.4,
                            dest=str(tmp / f'poster-{lv}.webp'), zoom=zoom, poster=True)
                if check_dir:
                    pjob['check'] = {'dir': str(check_dir), 'label': f'{lv}_poster_G{near:03d}'}
                jobs.append(pjob)

        total = len(jobs)
        print(f'{args.scene}: {total} fajlova ({", ".join(f"{lv} {plan[lv][1][0]}-{plan[lv][1][-1]} every {plan[lv][0]}, {len(plan[lv][1])} kadrova" for lv in levels)}), '
              f'isecak {crop}, bledenje desno {fade}, sidra: {anchors_src}', flush=True)
        results = []
        if args.jobs > 1:
            with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as ex:
                for i, r in enumerate(ex.map(work, jobs, chunksize=2), 1):
                    results.append(r)
                    if i % 16 == 0 or i == total:
                        print(f'  {i}/{total}', flush=True)
        else:
            for i, j in enumerate(jobs, 1):
                results.append(work(j))
        manifest = build_manifest(args.scene, spec, geo, sets, posters, anchors, args.version,
                                  {'q': {lv: qs[lv] for lv in levels}, 'alpha_quality': args.alpha_quality,
                                   'alpha_floor': args.alpha_floor, 'fade_right': list(fade) if fade else None})
        (tmp / 'seq.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        swap_into_place(tmp, out, args.force)
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)

    report(args, spec, results, plan, budget, sets, posters, out, opts)


def report(args, spec, results, plan, budget, sets, posters, out, opts):
    print(f'\nIZVESTAJ {args.scene} -> {out}')
    warns = sorted({w for r in results for w in r['warn']})
    for lv in plan:
        rs = [r for r in results if r['level'] == lv and not r['dest'].endswith(f'poster-{lv}.webp')]
        kb = [r['bytes'] / 1024 for r in rs]
        s = sets[lv]
        over = [f'G{r["g"]} {r["bytes"] / 1024:.1f} KB (q{r["q"]})' for r in rs if r['bytes'] / 1024 > budget[lv]]
        lowq = sorted({r['q'] for r in rs})
        print(f'  {lv}: {len(rs)} kadrova {s["w"]}x{s["h"]} (px {s["px"]}, every {s["every"]}), KB po kadru: '
              f'min {min(kb):.1f}, srednje {statistics.mean(kb):.1f}, max {max(kb):.1f}, ukupno {sum(kb) / 1024:.2f} MB; '
              f'budzet {budget[lv]:g} KB; q {lowq if len(lowq) > 1 else lowq[0]}')
        if over:
            print(f'     iznad budzeta (kvalitet je isti za sve kadrove; spusti --alpha-quality ili --q-*): {"; ".join(over)}')
    for r in sorted(results, key=lambda r: (r['level'], r['g'])):
        if r['dest'].endswith('.webp') and '/poster-' in r['dest'].replace('\\', '/'):
            print(f'  poster {r["level"]}: G{r["g"]} {r["size"][0]}x{r["size"][1]} {r["bytes"] / 1024:.1f} KB')
    print(f'  posteri u seq.json: {posters}')
    open_edges = spec['open']
    worst = {}
    for r in results:
        for side, v in r['edges'].items():
            if side not in open_edges:
                worst[side] = max(worst.get(side, 0), v)
    bad = {s: v for s, v in worst.items() if v > 6}
    print(f'  alfa na zatvorenim ivicama isecka (max po strani): {worst or "nema"}'
          + (f'  UPOZORENJE: tvrda ivica {bad}' if bad else ''))
    for w in warns:
        print(f'  UPOZORENJE: {w}')
    for r in results:
        if r.get('halo'):
            print(r['halo'])


if __name__ == '__main__':
    main()
