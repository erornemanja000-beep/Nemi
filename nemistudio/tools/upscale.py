#!/usr/bin/env python3
"""AI upscale (Real-ESRGAN via spandrel) for the few shots that need macro detail.

    python3 tools/upscale.py <model.pth> <in.mp4> <out.mp4> <ranges> [--width 2560] [--test frame.jpg]

ranges: seconds, e.g. "0.9-1.35,2.3-3.45". Frames inside are upscaled with the model; all other frames are resized with Lanczos,
so the output keeps the timing of the source and the film renderer can seek it exactly like the original.
"""
import argparse
import subprocess
import sys
import time

import cv2
import numpy as np
import torch
from spandrel import ModelLoader

ap = argparse.ArgumentParser()
ap.add_argument('model')
ap.add_argument('src')
ap.add_argument('out')
ap.add_argument('ranges')
ap.add_argument('--width', type=int, default=2560)
ap.add_argument('--tile', type=int, default=384)
ap.add_argument('--test', default='')
args = ap.parse_args()

torch.set_num_threads(4)
model = ModelLoader().load_from_file(args.model).eval()
scale = model.scale

@torch.inference_mode()
def upscale(img):
    """BGR uint8 -> BGR uint8, tiled with overlap so memory stays small"""
    h, w = img.shape[:2]
    x = torch.from_numpy(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).permute(2, 0, 1).float().div(255)[None]
    out = torch.zeros(1, 3, h * scale, w * scale)
    wsum = torch.zeros(1, 1, h * scale, w * scale)
    T, O = args.tile, 16
    for y in range(0, h, T):
        for x0 in range(0, w, T):
            ya, yb = max(0, y - O), min(h, y + T + O)
            xa, xb = max(0, x0 - O), min(w, x0 + T + O)
            o = model(x[..., ya:yb, xa:xb]).clamp(0, 1)
            out[..., ya * scale:yb * scale, xa * scale:xb * scale] += o
            wsum[..., ya * scale:yb * scale, xa * scale:xb * scale] += 1
    out = (out / wsum)[0].permute(1, 2, 0).numpy()
    return cv2.cvtColor((out * 255).round().astype(np.uint8), cv2.COLOR_RGB2BGR)

cap = cv2.VideoCapture(args.src)
fps = cap.get(cv2.CAP_PROP_FPS) or 25
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
sw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
sh = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
W = args.width
H = round(sh * W / sw / 2) * 2

if args.test:
    cap.set(cv2.CAP_PROP_POS_MSEC, float(args.ranges.split('-')[0]) * 1000)
    ok, f = cap.read()
    t = time.time()
    u = upscale(f)
    print('model x%d, %.1fs per frame' % (scale, time.time() - t))
    cv2.imwrite(args.test, cv2.resize(u, (W, H), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    cv2.imwrite(args.test.replace('.jpg', '_lanczos.jpg'), cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4), [cv2.IMWRITE_JPEG_QUALITY, 92])
    sys.exit()

ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', args.out], stdin=subprocess.PIPE)
spans = [tuple(float(v) for v in r.split('-')) for r in args.ranges.split(',')]
todo = {i for a, b in spans for i in range(int(a * fps), int(b * fps) + 1)}
t = time.time()
done = 0
for i in range(n):
    ok, f = cap.read()
    if not ok:
        break
    if i in todo:
        f = cv2.resize(upscale(f), (W, H), interpolation=cv2.INTER_AREA)
        done += 1
        print(f'frame {i} ({done}/{len(todo)}) {(time.time() - t) / done:.1f}s/frame', file=sys.stderr)
    else:
        f = cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4)
    ff.stdin.write(f.tobytes())
ff.stdin.close()
ff.wait()
