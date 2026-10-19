#!/usr/bin/env python3
"""Pull the best video + audio out of a saved Instagram page (.htm) and mux to MP4.

A page saved with "Save page as" keeps the DASH manifest of every reel it showed;
the signed CDN links in it stay valid for a few days.

    python3 -I dash_from_html.py FR1.htm outdir/

Writes outdir/<stem>_<n>.mp4 (VP9 + AAC, highest resolution) per video found.
"""
import base64
import html
import json
import os
import re
import subprocess
import sys
import urllib.request


def tag_of(url):
    m = re.search(r"efg=([^&]+)", url)
    if not m:
        return ""
    raw = m.group(1).replace("%3D", "=")
    try:
        return json.loads(base64.urlsafe_b64decode(raw + "==").decode())["vencode_tag"]
    except Exception:
        return ""


def representations(text):
    t = text.replace("\\u003C", "<").replace("\\/", "/").replace('\\"', '"')
    for m in re.finditer(r"<Representation([^>]*)>.*?<BaseURL>([^<]+)</BaseURL>", t):
        attrs, url = m.group(1), html.unescape(m.group(2)).replace("\\u0025", "%")
        bw = int(re.search(r'bandwidth="(\d+)"', attrs).group(1))
        kind = "audio" if 'mimeType="audio' in attrs else "video"
        yield {"kind": kind, "bw": bw, "url": url, "tag": tag_of(url)}


def group_key(tag):
    # "ig-xpvds.clips.c2-C3.dash_vp9-basic-gen2_1080p" -> "ig-xpvds.clips.c2-C3"
    return tag.rsplit(".", 1)[0] if "." in tag else tag


def fetch(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)


def main(src, outdir):
    os.makedirs(outdir, exist_ok=True)
    text = open(src, encoding="utf-8", errors="replace").read()
    groups = {}
    for rep in representations(text):
        groups.setdefault(group_key(rep["tag"]), []).append(rep)
    stem = os.path.splitext(os.path.basename(src))[0]
    for n, (key, reps) in enumerate(groups.items(), 1):
        video = max((r for r in reps if r["kind"] == "video"), key=lambda r: r["bw"], default=None)
        audio = max((r for r in reps if r["kind"] == "audio"), key=lambda r: r["bw"], default=None)
        if not video:
            continue
        v, a, out = (os.path.join(outdir, f"{stem}_{n}{s}") for s in ("_v.mp4", "_a.mp4", ".mp4"))
        fetch(video["url"], v)
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", v]
        if audio:
            fetch(audio["url"], a)
            cmd += ["-i", a]
        cmd += ["-c", "copy", out]
        subprocess.run(cmd, check=True)
        for tmp in (v, a):
            if os.path.exists(tmp):
                os.remove(tmp)
        print(out, key, video["tag"].rsplit("_", 1)[-1])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
