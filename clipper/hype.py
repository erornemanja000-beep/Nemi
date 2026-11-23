#!/usr/bin/env python3
"""Klip 1080×1920 u tri dela: gore igra, u sredini kamera streamera, dole naš „Hype" pojas.

Hype pojas pravi Remotion (motion/, kompozicija HypeTraka): naš AI snimak noćne vožnje i brzinomer
čija kazaljka prati jačinu glasa streamera, kadar po kadar. Titlovi stoje na spoju igre i kamere.

Primer (Speed na Twitch-u: kamera levo, chat gore desno, njegovi titlovi dole u sredini):
  python3 clipper/hype.py --izvor clipper/ulaz/twitch/speed.mp4 --od 18 --do 27 \\
      --igra 405:90:1290:860 --kamera 2:464:384:238 \\
      --voznja clipper/ulaz/artlist/voznja_neon.mp4 \\
      --naslov "Speed's first ever robbery in GTA 6" --autor "@IShowSpeed" \\
      --titlovi clipper/ulaz/twitch/speed.reci.json --izlaz clipper/izlaz/speed_pljacka.mp4

--igra i --kamera su pravougaonici u pikselima izvora: x:y:sirina:visina.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from alati import (FONTOVI, greska, hms, ima_zvuk, pokreni, probe, proveri_ffmpeg, trajanje,
                   ucitaj_reci, vreme)
from split import S, FPS, napravi_ass

KOREN = Path(__file__).resolve().parent
MOTION = KOREN.parent / "motion"
H_IGRA, H_KAMERA, H_HYPE = 720, 668, 532   # zbir 1920
SR = 16000


def pravougaonik(tekst: str) -> tuple[int, int, int, int]:
    try:
        x, y, w, h = (int(float(v)) for v in tekst.split(":"))
    except ValueError:
        greska(f"pravougaonik se piše x:y:sirina:visina, dobio sam {tekst}")
    return x, y, w, h


def kriva_glasa(izvor: Path, od: float, duzina: float) -> list[float]:
    """Jačina glasa po kadru (0–1): brz uspon, sporiji pad, kao kazaljka pravog brzinomera."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{od:.3f}", "-t", f"{duzina:.3f}",
                        "-i", str(izvor), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        greska("ne mogu da pročitam zvuk izvora")
    zvuk = np.frombuffer(r.stdout, dtype=np.float32)
    po_kadru = SR // FPS
    n = int(round(duzina * FPS))
    db = []
    for i in range(n):
        deo = zvuk[i * po_kadru:(i + 1) * po_kadru]
        rms = float(np.sqrt(np.mean(deo ** 2))) if deo.size else 0.0
        db.append(20 * np.log10(rms + 1e-9))
    # skala prema samom klipu: tiho (10. percentil) = 0, najglasnije (98. percentil) = 1
    nisko, visoko = np.percentile(db, 10), np.percentile(db, 98)
    raspon = max(visoko - nisko, 6.0)
    vrednosti, h = [], 0.0
    for d in db:
        cilj = min(1.0, max(0.0, (d - nisko) / raspon)) ** 1.4
        h += (cilj - h) * (0.55 if cilj > h else 0.12)
        vrednosti.append(round(h, 4))
    return vrednosti


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--izvor", required=True)
    p.add_argument("--od", default="0")
    p.add_argument("--do", dest="do_", required=True)
    p.add_argument("--igra", required=True, help="x:y:sirina:visina igre u izvoru (bez kamere, chata i titlova)")
    p.add_argument("--kamera", required=True, help="x:y:sirina:visina kamere streamera u izvoru")
    p.add_argument("--voznja", required=True, help="naš snimak za donji pojas (AI vožnja)")
    p.add_argument("--naslov")
    p.add_argument("--naslov-trajanje", type=float)
    p.add_argument("--autor")
    p.add_argument("--titlovi", help="SRT, VTT ili .reci.json iz transkript.py (vreme izvora)")
    p.add_argument("--mala-slova", action="store_true")
    p.add_argument("--bez-cenzure", dest="cenzura", action="store_false")
    p.add_argument("--oznaka", default="HYPE")
    p.add_argument("--izlaz", required=True)
    args = p.parse_args()

    proveri_ffmpeg()
    if not shutil.which("npx"):
        greska("nema npx (Node.js), a Hype pojas se renderuje u Remotion-u")
    izvor = Path(args.izvor).resolve()
    info = probe(izvor)
    if not ima_zvuk(info):
        greska("izvor nema zvuk, a brzinomer prati glas")
    od, do = vreme(args.od), min(vreme(args.do_), trajanje(info))
    duzina = do - od
    if duzina <= 0.5:
        greska("isečak je prekratak")

    reci = []
    if args.titlovi:
        reci = [(a - od, b - od, r) for a, b, r in ucitaj_reci(Path(args.titlovi)) if od - 0.05 <= a < do]

    izlaz = Path(args.izlaz).resolve()
    izlaz.parent.mkdir(parents=True, exist_ok=True)
    gx, gy, gw, gh = pravougaonik(args.igra)
    kx, ky, kw, kh = pravougaonik(args.kamera)

    with tempfile.TemporaryDirectory(prefix="hype_") as tmp:
        tmp = Path(tmp)

        # 1) Hype pojas u Remotion-u
        javno = MOTION / "public" / "clipper"
        javno.mkdir(parents=True, exist_ok=True)
        shutil.copy(Path(args.voznja).resolve(), javno / "voznja.mp4")
        shutil.copy(FONTOVI / "Inter-Black.otf", javno / "Inter-Black.otf")
        props = tmp / "props.json"
        props.write_text(json.dumps({"vrednosti": kriva_glasa(izvor, od, duzina),
                                     "video": "clipper/voznja.mp4", "oznaka": args.oznaka}))
        traka = tmp / "traka.mp4"
        r = subprocess.run(["npx", "--no-install", "remotion", "render", "HypeTraka", str(traka),
                            f"--props={props}", "--muted", "--crf=16", "--log=error"],
                           cwd=MOTION, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:])
            greska("Remotion nije napravio Hype pojas")

        # 2) titlovi i naslov
        (tmp / "fontovi").mkdir()
        for font in FONTOVI.glob("*.otf"):
            shutil.copy(font, tmp / "fontovi" / font.name)
        (tmp / "t.ass").write_text(napravi_ass(args, duzina, reci, titl_y=H_IGRA), encoding="utf-8")

        # 3) spajanje: igra / kamera / pojas, tanke neonske linije na spojevima
        f = [
            "[0:v]split=2[i0][k0]",
            f"[i0]crop={gw}:{gh}:{gx}:{gy},scale={S}:{H_IGRA}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={S}:{H_IGRA},setsar=1,fps={FPS}[igra]",
            f"[k0]crop={kw}:{kh}:{kx}:{ky},scale={S}:{H_KAMERA}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={S}:{H_KAMERA},unsharp=5:5:0.7,setsar=1,fps={FPS}[kam]",
            f"[1:v]scale={S}:{H_HYPE},setsar=1,fps={FPS}[hype]",
            "[igra][kam][hype]vstack=inputs=3:shortest=1,"
            f"drawbox=x=0:y={H_IGRA - 3}:w={S}:h=6:color=0xFF2BD6@0.9:t=fill,"
            f"drawbox=x=0:y={H_IGRA + H_KAMERA - 3}:w={S}:h=6:color=0x00E5FF@0.9:t=fill,"
            "ass=t.ass:fontsdir=fontovi,format=yuv420p[v]",
            "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
        ]
        pokreni(["ffmpeg", "-hide_banner", "-y", "-ss", f"{od:.3f}", "-t", f"{duzina:.3f}", "-i", str(izvor),
                 "-i", str(traka), "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]",
                 "-t", f"{duzina:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(izlaz)], cwd=tmp)

    print(f"Gotovo: {izlaz}  ({hms(duzina)}, izvor {hms(od)}–{hms(do)})")


if __name__ == "__main__":
    main()
