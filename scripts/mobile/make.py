#!/usr/bin/env python3
"""Pravi uspravne (9:16) snimke za telefon iz originala, po planovima kamere u scripts/mobile/plans/.

  python3 scripts/mobile/make.py film   -> sajt/src/assets/video/hero-m.mp4 (+ poster) i ispiše gde je logo
  python3 scripts/mobile/make.py gel    -> sajt/src/assets/video/sorten-m.mp4 (+ poster), petlja bez skoka
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
FIN = ROOT / 'video' / 'finalni'
OUT = ROOT / 'sajt' / 'src' / 'assets'
# Isto izoštravanje kao za široki film (vremena su na vremenskoj liniji celog filma)
FILM_VF = ("hqdn3d=1.2:1.0:3:3,cas=strength=0.55,unsharp=5:5:0.45:5:5:0,"
           "unsharp=7:7:0.6:5:5:0:enable='between(t,4.5,8)+between(t,15.5,23.8)+between(t,31.5,33.5)',"
           "eq=contrast=1.03:saturation=1.03")


def reframe(plan, out):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
        json.dump(plan, f)
    res = subprocess.check_output([sys.executable, '-I', str(HERE / 'reframe.py'), f.name, str(out)]).decode()
    return json.loads(res.strip().splitlines()[-1])


def film(crf):
    kf = json.load(open(HERE / 'plans' / 'film.json'))
    plan = {
        'fps': 30, 'size': [1080, 1920], 'crf': crf,
        # prvi deo je 4K original (0-10 s), zatim delovi 2 i 3 (1080p)
        'inputs': [{'path': str(FIN / '01_100811.mov')}, {'path': str(FIN / '02_q1.mov')}, {'path': str(FIN / '03_q2.mov')}],
        'keyframes': kf['keyframes'], 'post_vf': FILM_VF,
        'audio': str(OUT / 'video' / 'hero.mp4'),
        'logo': {'x': 567, 'y': 81, 'w': 825.6},   # don-badge.png preko loga u poslednjem kadru (px izvora)
    }
    out = OUT / 'video' / 'hero-m.mp4'
    info = reframe(plan, out)
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-frames:v', '1', '-vf', 'scale=720:-2',
                           '-q:v', '4', str(OUT / 'img' / 'hero-poster-m.jpg')])
    print(json.dumps(info), out.stat().st_size // 1024, 'KB')


def gel(crf):
    kf = json.load(open(HERE / 'plans' / 'gel.json'))
    tmp = pathlib.Path(tempfile.gettempdir()) / 'sorten-m-raw.mp4'
    reframe({'fps': 30, 'size': [720, 1280], 'crf': 12, 'inputs': [{'path': str(FIN / 'sladoled_w2.mov')}],
             'keyframes': kf['keyframes']}, tmp)
    out = OUT / 'video' / 'sorten-m.mp4'
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(tmp)]))
    # isto kao široka verzija: kraj se meko pretopi u početak (0,8 s), pa se petlja ne vidi
    off = dur - 0.8 - 0.8
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-filter_complex',
                           f"[0:v]split[a][b];[a]trim=start=0.8,setpts=PTS-STARTPTS[A];[b]trim=0:0.8,setpts=PTS-STARTPTS[B];"
                           f"[A][B]xfade=transition=fade:duration=0.8:offset={off:.3f},cas=strength=0.45,format=yuv420p[v]",
                           '-map', '[v]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high',
                           '-movflags', '+faststart', str(out)])
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-ss', '2', '-i', str(out), '-frames:v', '1', '-q:v', '4',
                           str(OUT / 'img' / 'sorten-poster-m.jpg')])
    print(out, out.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    what = sys.argv[1]
    crf = int(sys.argv[2]) if len(sys.argv) > 2 else (22 if what == 'film' else 24)
    {'film': film, 'gel': gel}[what](crf)
