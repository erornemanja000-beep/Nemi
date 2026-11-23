#!/usr/bin/env python3
"""Nalazi najživlje trenutke u dugom videu (reakcija, stream, intro) po zvuku.

Meri glasnoću na svakih 0,1 s (EBU R128, ffmpeg). Vrisak, smeh i galama su skokovi iznad
uobičajenog govora. Oko svakog skoka predlaže isečak: veći deo pre skoka (uvod), manji posle
(reakcija), a početak i kraj pomera na najtišu tačku u blizini da ne seče usred reči.

Primer:
  python3 clipper/momenti.py ulaz/speed_reakcija.mp4 --duzina 45 --broj 8
  python3 clipper/momenti.py ulaz/speed.mp4 --napravi izlaz/speed --autor "@IShowSpeed" --titlovi ulaz/speed.en.vtt

Ovo je prvi filter. Konačan izbor (i naslov) radi čovek ili Claude iz transkripta.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from alati import KOREN, greska, hms, probe, proveri_ffmpeg, trajanje, ima_zvuk

KORAK = 0.1  # sekundi između merenja


def izmeri(video: Path) -> list[float]:
    """Momentalna glasnoća (LUFS) na svakih 0,1 s."""
    with tempfile.TemporaryDirectory(prefix="momenti_") as tmp:
        log = Path(tmp) / "m.txt"
        r = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
             "-af", "aresample=16000,aformat=channel_layouts=mono,asetnsamples=n=1600,"
                    "ebur128=metadata=1,ametadata=mode=print:key=lavfi.r128.M:file=m.txt",
             "-f", "null", "-"],
            cwd=tmp, capture_output=True, text=True,
        )
        if r.returncode != 0 or not log.exists():
            print(r.stderr[-2000:], file=sys.stderr)
            greska("merenje zvuka nije uspelo")
        vrednosti = []
        for red in log.read_text().splitlines():
            if red.startswith("lavfi.r128.M="):
                v = float(red.split("=", 1)[1])
                vrednosti.append(max(v, -70.0))
    return vrednosti


def percentil(niz: list[float], p: float) -> float:
    s = sorted(niz)
    return s[min(len(s) - 1, max(0, int(p / 100 * len(s))))]


def ugladi(niz: list[float], prozor: int) -> list[float]:
    """Klizni prosek (prozor u broju merenja)."""
    out, zbir, pola = [], 0.0, prozor // 2
    pref = [0.0]
    for v in niz:
        zbir += v
        pref.append(zbir)
    for i in range(len(niz)):
        a, b = max(0, i - pola), min(len(niz), i + pola + 1)
        out.append((pref[b] - pref[a]) / (b - a))
    return out


def najtisa_tacka(m: list[float], centar: float, raspon: float) -> float:
    a = max(0, int((centar - raspon) / KORAK))
    b = min(len(m) - 1, int((centar + raspon) / KORAK))
    if b <= a:
        return centar
    i = min(range(a, b + 1), key=lambda j: m[j])
    return i * KORAK


def nadji(m: list[float], ukupno: float, duzina: float, broj: int, pre: float) -> list[dict]:
    if not m:
        return []
    glatko = ugladi(m, 10)            # 1 s
    govor = percentil(m, 50)          # uobičajen nivo
    prag = percentil(glatko, 92)
    glasno = percentil(m, 90)

    # vrhovi: lokalni maksimumi iznad praga
    vrhovi = []
    for i in range(1, len(glatko) - 1):
        if glatko[i] >= prag and glatko[i] >= glatko[i - 1] and glatko[i] > glatko[i + 1]:
            vrhovi.append(i)

    kandidati = []
    for i in vrhovi:
        t = i * KORAK
        od = max(0.0, t - duzina * pre)
        do = min(ukupno, od + duzina)
        od = max(0.0, do - duzina)
        a, b = int(od / KORAK), int(do / KORAK)
        prozor = m[a:b] or [govor]
        gustina = sum(1 for v in prozor if v >= glasno) / len(prozor)
        skok = glatko[i] - govor
        ocena = skok + 25 * gustina
        kandidati.append({"vrh": t, "od": od, "do": do, "ocena": ocena, "skok": skok, "gustina": gustina})

    kandidati.sort(key=lambda k: k["ocena"], reverse=True)
    izabrani: list[dict] = []
    for k in kandidati:
        if all(k["do"] <= z["od"] or k["od"] >= z["do"] for z in izabrani):
            izabrani.append(k)
        if len(izabrani) >= broj:
            break

    for k in izabrani:
        k["od"] = najtisa_tacka(m, k["od"], 2.0)
        k["do"] = min(ukupno, najtisa_tacka(m, k["do"], 2.0))
    izabrani.sort(key=lambda k: k["od"])
    return izabrani


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--duzina", type=float, default=45, help="željena dužina klipa u sekundama (podrazumevano 45)")
    p.add_argument("--broj", type=int, default=8, help="koliko trenutaka (podrazumevano 8)")
    p.add_argument("--pre", type=float, default=0.65, help="koliki deo klipa ide pre vrhunca (0–1)")
    p.add_argument("--json", help="sačuvaj trenutke u JSON")
    p.add_argument("--napravi", metavar="FOLDER", help="odmah napravi klipove u ovaj folder")
    p.add_argument("--autor", help="prosleđuje se split.py")
    p.add_argument("--titlovi", help="prosleđuje se split.py")
    p.add_argument("--gore", help="prosleđuje se split.py")
    args = p.parse_args()

    proveri_ffmpeg()
    video = Path(args.video).resolve()
    if not video.exists():
        greska(f"ne postoji: {video}")
    info = probe(video)
    if not ima_zvuk(info):
        greska("video nema zvuk, pa nema po čemu da se meri")
    ukupno = trajanje(info)
    if ukupno < args.duzina:
        greska(f"video ({ukupno:.0f} s) je kraći od željenog klipa ({args.duzina:.0f} s)")

    print(f"Merim zvuk: {video.name} ({hms(ukupno)}) …")
    m = izmeri(video)
    trenuci = nadji(m, ukupno, args.duzina, args.broj, args.pre)
    if not trenuci:
        greska("nisam našao nijedan izražen trenutak")

    print(f"\n{'#':>2}  {'od':>8}  {'do':>8}  {'vrhunac':>8}  {'ocena':>5}")
    for n, k in enumerate(trenuci, 1):
        print(f"{n:>2}  {hms(k['od']):>8}  {hms(k['do']):>8}  {hms(k['vrh']):>8}  {k['ocena']:5.1f}")

    if args.json:
        Path(args.json).write_text(json.dumps(
            [{**k, "od_hms": hms(k["od"]), "do_hms": hms(k["do"])} for k in trenuci],
            indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nSačuvano: {args.json}")

    split = KOREN / "split.py"
    dodatno = []
    for ime in ("autor", "titlovi", "gore"):
        if getattr(args, ime):
            dodatno += [f"--{ime}", getattr(args, ime)]

    if not args.napravi:
        print("\nKomande za klipove (dopiši --naslov):")
        for n, k in enumerate(trenuci, 1):
            delovi = [f"python3 {split}", f'--dole "{video}"', f'--od {k["od"]:.1f}', f'--do {k["do"]:.1f}',
                      *(f'"{d}"' if " " in d else d for d in dodatno), f"--izlaz izlaz/{video.stem}_{n:02d}.mp4"]
            print(" ".join(delovi))
        return

    folder = Path(args.napravi)
    folder.mkdir(parents=True, exist_ok=True)
    for n, k in enumerate(trenuci, 1):
        izlaz = folder / f"{video.stem}_{n:02d}.mp4"
        print(f"\n[{n}/{len(trenuci)}] {hms(k['od'])}–{hms(k['do'])} → {izlaz}")
        r = subprocess.run([sys.executable, str(split), "--dole", str(video),
                            "--od", f"{k['od']:.2f}", "--do", f"{k['do']:.2f}",
                            "--seed", str(n), *dodatno, "--izlaz", str(izlaz)])
        if r.returncode != 0:
            greska(f"klip {n} nije uspeo")


if __name__ == "__main__":
    main()
