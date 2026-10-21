#!/usr/bin/env python3
"""Cuts the screen out of green-screen device shots for the "site in a site" zooms.

    python3 tools/portals.py <clips-dir> public/portals

For every portal: <name>.webp (photo with a transparent screen) and portals.json with the
screen's four corners in image pixels (tl, tr, br, bl) and the image size.
"""
import json
import os
import sys

import cv2
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# name: (mixkit id, time in s, shift) - shift rotates the corner order so "tl" is the screen's own
# top-left (a phone lying sideways on a table has its top edge on the left or right)
PORTALS = {
    'desk': ('48285', 11.8, 0),     # laptop on a dark desk: Nemi -> café
    'cafe': ('52076', 1.2, 0),      # laptop on a café table with a cup: café -> law firm
    'office': ('44737', 3.0, 0),    # monitor in an open office: law firm -> gym
    'tv': ('9584', 5.0, 0),         # TV in a warm room at night: gym -> hotel
    # phones for portrait screens
    'm-desk': ('100069', 2.6, 0),   # phone next to an espresso
    'm-cafe': ('42621', 6.5, 0),    # woman holding a phone over her notes
    'm-office': ('8839', 5.0, 0, (36, 120, 120)),   # hand holding a phone at a bright window
    'm-tv': ('100079', 8.5, 1),     # phone lying on a desk with books
}


def order(pts):
    """Clockwise (on screen) starting at the corner nearest the image's top-left."""
    pts = np.array(pts, dtype=np.float32)
    c = pts.mean(0)
    pts = pts[np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))]
    i = int(np.argmin(pts.sum(1)))
    return [pts[(i + k) % 4] for k in range(4)]  # tl, tr, br, bl


meta = {}
for name, (vid, t, shift, *lo) in PORTALS.items():
    cap = cv2.VideoCapture(os.path.join(SRC, vid + '.mp4'))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, img = cap.read()
    if not ok:
        sys.exit('cannot read ' + vid)
    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # green screen (also the pale mint one): hue 35..95, enough saturation
    mask = cv2.inRange(hsv, lo[0] if lo else (32, 45, 60), (98, 255, 255))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    screen = (lab == big).astype(np.uint8) * 255
    cnts, _ = cv2.findContours(screen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    eps = 0.02 * cv2.arcLength(hull, True)
    quad = cv2.approxPolyDP(hull, eps, True).reshape(-1, 2)
    if len(quad) != 4:
        rect = cv2.minAreaRect(hull)
        quad = cv2.boxPoints(rect)
    tl, tr, br, bl = (order(quad) * 2)[shift:shift + 4]
    # alpha: the screen polygon (slightly grown so no green fringe stays) is transparent
    alpha = np.full((h, w), 255, np.uint8)
    poly = np.array([tl, tr, br, bl], np.int32)
    cv2.fillPoly(alpha, [poly], 0)
    grow = cv2.dilate(255 - alpha, np.ones((5, 5), np.uint8))
    alpha = 255 - grow
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)
    # despill: pull remaining green out of the bezel edge
    b, g, r = cv2.split(img.astype(np.int16))
    g = np.minimum(g, np.maximum(r, b) + 12)
    img = cv2.merge([b, g, r]).clip(0, 255).astype(np.uint8)
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[..., 3] = alpha
    cv2.imwrite(os.path.join(OUT, name + '.webp'), rgba, [cv2.IMWRITE_WEBP_QUALITY, 82])
    meta[name] = {'w': w, 'h': h, 'quad': [[round(float(x), 1), round(float(y), 1)] for x, y in (tl, tr, br, bl)]}
    print(name, w, h, meta[name]['quad'])
    dbg = img.copy()
    cv2.polylines(dbg, [poly], True, (0, 0, 255), 3)
    cv2.circle(dbg, (int(tl[0]), int(tl[1])), 9, (255, 0, 255), -1)
    cv2.imwrite(os.path.join(OUT, '_dbg_' + name + '.jpg'), cv2.resize(dbg, (640, 360)))

json.dump(meta, open(os.path.join(OUT, 'portals.json'), 'w'), indent=1)
