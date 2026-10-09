import sys, math, random, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

F4, F5, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS, DUR = 1344, 768, 30, 8.0
N = int(FPS * DUR)

bg = Image.open(F4).convert('RGB')
end = Image.open(F5).convert('RGB')
e = np.asarray(end).astype(np.float32)

# letter mask from the finished photo (dark letters on light wall)
Y0, Y1, X0, X1 = 136, 242, 535, 860
lum = e[Y0:Y1, X0:X1].mean(2)
mask = (lum < 120).astype(np.float32)
mimg = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
mask = np.asarray(mimg).astype(np.float32) / 255

cols = (mask > 0.5).sum(0)
def split_x(a, b):
    seg = cols[a - X0:b - X0]
    return a + int(np.argmin(seg))
d_o = split_x(605, 630)
spans = [(545, d_o), (d_o, 693), (693, 756), (756, 788), (788, 852)]  # D O N ' S

letters = []
for (a, b) in spans:
    sub = np.zeros_like(mask)
    sub[:, a - X0:b - X0] = mask[:, a - X0:b - X0]
    ys, xs = np.nonzero(sub > 0.05)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    rgba[..., :3] = e[Y0 + y0:Y0 + y1, X0 + x0:X0 + x1].astype(np.uint8)
    rgba[..., 3] = (sub[y0:y1, x0:x1] * 255).astype(np.uint8)
    letters.append(dict(img=Image.fromarray(rgba, 'RGBA'), x=X0 + x0, y=Y0 + y0))

def clamp(t): return max(0.0, min(1.0, t))
def ease_out_back(t, s=1.9):
    t -= 1; return t * t * ((s + 1) * t + s) + 1
def ease_out_cubic(t): return 1 - (1 - t) ** 3
def bounce(t):
    if t < 1 / 2.75: return 7.5625 * t * t
    if t < 2 / 2.75: t -= 1.5 / 2.75; return 7.5625 * t * t + .75
    if t < 2.5 / 2.75: t -= 2.25 / 2.75; return 7.5625 * t * t + .9375
    t -= 2.625 / 2.75; return 7.5625 * t * t + .984375

# timing (seconds): start, duration
T = [(1.6, 0.6), (2.3, 0.8), (3.2, 0.7), (4.0, 0.6), (4.6, 0.6)]

def place(i, t):
    """return (image, dx, dy, alpha) for letter i at time t, or None"""
    L = letters[i]; img = L['img']; st, du = T[i]
    p = (t - st) / du
    if p < 0: return None
    p = clamp(p)
    if i == 0:   # D slides in from the left
        k = ease_out_back(p); return img, (1 - k) * -420, 0, clamp(p * 3)
    if i == 1:   # O rolls in from the right
        k = ease_out_cubic(p)
        dx = (1 - k) * 520
        ang = dx / (img.width / 2) * 180 / math.pi
        return img.rotate(ang, resample=Image.BICUBIC, expand=True), dx, 0, clamp(p * 3)
    if i == 2:   # N drops with a bounce
        return img, 0, (1 - bounce(p)) * -260, clamp(p * 4)
    if i == 3:   # apostrophe spins down like a leaf
        k = ease_out_cubic(p)
        ang = (1 - k) * 540
        return img.rotate(ang, resample=Image.BICUBIC, expand=True), math.sin(p * 9) * 18 * (1 - k), (1 - k) * -150, clamp(p * 3)
    if i == 4:   # S pops with overshoot
        s = max(0.01, ease_out_back(p, 2.6))
        im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BICUBIC)
        return im, 0, 0, clamp(p * 3)

random.seed(7)
# sparkles: rise from the storefront toward the sign
parts = []
for _ in range(170):
    t0 = random.uniform(0.0, 5.0)
    parts.append(dict(t0=t0, life=random.uniform(1.2, 2.4),
                      x=random.uniform(430, 900), y=random.uniform(330, 640),
                      tx=random.uniform(540, 860), ty=random.uniform(140, 240),
                      r=random.uniform(1.2, 3.2), gold=random.random() < 0.6))
# landing bursts
bursts = []
for i, (st, du) in enumerate(T):
    L = letters[i]
    cx, cy = L['x'] + L['img'].width / 2, L['y'] + L['img'].height / 2
    for _ in range(26):
        a = random.uniform(0, 2 * math.pi)
        bursts.append(dict(t0=st + du * 0.85, cx=cx, cy=cy, a=a, v=random.uniform(40, 120),
                           r=random.uniform(1.2, 2.8), gold=random.random() < 0.5))

GOLD, PINK = (255, 214, 140), (255, 190, 205)

def star(dr, x, y, r, col, a):
    c = col + (int(255 * a),)
    dr.ellipse([x - r, y - r, x + r, y + r], fill=c)
    if r > 2.2:
        dr.line([x - r * 3, y, x + r * 3, y], fill=col + (int(160 * a),), width=1)
        dr.line([x, y - r * 3, x, y + r * 3], fill=col + (int(160 * a),), width=1)

ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                       '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-vf', 'scale=1920:1080:flags=lanczos', '-c:v', 'libx264', '-crf', '17',
                       '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
                      stdin=subprocess.PIPE)

sweep_st, sweep_du = 5.5, 0.9
fade_st, fade_du = 6.6, 0.6

for f in range(N):
    t = f / FPS
    frame = bg.copy()
    # gentle warm-up of the shop light in the first 1.5s
    glow = clamp(t / 1.5)
    if glow > 0:
        lay = Image.new('RGB', (W, H), (255, 225, 215))
        frame = Image.blend(frame, Image.composite(lay, frame, Image.new('L', (W, H), 0)), 0)
        arr = np.asarray(frame).astype(np.float32)
        arr[255:640, 430:870] *= 1 + 0.06 * glow
        frame = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    # letters
    let_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for i in range(5):
        r = place(i, t)
        if r is None: continue
        im, dx, dy, a = r
        L = letters[i]
        cx = L['x'] + L['img'].width / 2 + dx
        cy = L['y'] + L['img'].height / 2 + dy
        if a < 1:
            al = np.asarray(im.getchannel('A')).astype(np.float32) * a
            im = im.copy(); im.putalpha(Image.fromarray(al.astype(np.uint8)))
        let_layer.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))

    # light sweep across the finished sign
    ps = (t - sweep_st) / sweep_du
    if 0 <= ps <= 1:
        arr = np.asarray(let_layer).astype(np.float32)
        xs = np.arange(W)[None, :]; ys = np.arange(H)[:, None]
        pos = X0 - 80 + ps * (X1 - X0 + 160)
        band = np.exp(-(((xs + (ys - 190) * 0.5) - pos) / 28.0) ** 2)
        arr[..., :3] += band[..., None] * 150 * (arr[..., 3:4] / 255)
        let_layer = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')

    frame = frame.convert('RGBA')
    frame.alpha_composite(let_layer)

    # sparkles
    sp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(sp)
    for p in parts:
        q = (t - p['t0']) / p['life']
        if not 0 <= q <= 1: continue
        k = ease_out_cubic(q)
        x = p['x'] + (p['tx'] - p['x']) * k + math.sin(q * 8 + p['x']) * 10
        y = p['y'] + (p['ty'] - p['y']) * k
        a = math.sin(q * math.pi) * (1 - clamp((t - 5.6) / 1.0))
        star(dr, x, y, p['r'], GOLD if p['gold'] else PINK, a)
    for b in bursts:
        q = (t - b['t0']) / 0.7
        if not 0 <= q <= 1: continue
        d = b['v'] * ease_out_cubic(q)
        star(dr, b['cx'] + math.cos(b['a']) * d, b['cy'] + math.sin(b['a']) * d, b['r'], GOLD if b['gold'] else PINK, 1 - q)
    glow_l = sp.filter(ImageFilter.GaussianBlur(4))
    frame.alpha_composite(glow_l); frame.alpha_composite(sp)
    frame = frame.convert('RGB')

    # finish on the exact original photo
    pf = clamp((t - fade_st) / fade_du)
    if pf > 0:
        frame = Image.blend(frame, end, ease_out_cubic(pf))

    ff.stdin.write(frame.tobytes())

ff.stdin.close(); ff.wait()
print('done', OUT)
