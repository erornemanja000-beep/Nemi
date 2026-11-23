"""Zajedničke funkcije za clipper: vreme, ffprobe, pokretanje ffmpeg-a, titlovi."""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent
FONTOVI = KOREN / "fontovi"


def greska(poruka: str) -> None:
    print(f"GREŠKA: {poruka}", file=sys.stderr)
    sys.exit(1)


def proveri_ffmpeg() -> None:
    for alat in ("ffmpeg", "ffprobe"):
        if not shutil.which(alat):
            greska(f"{alat} nije instaliran ili nije u PATH-u.")


def vreme(tekst: str | float | int) -> float:
    """'83', '1:23', '01:01:23.5' ili '1:23,5' -> sekunde."""
    if isinstance(tekst, (int, float)):
        return float(tekst)
    delovi = tekst.strip().replace(",", ".").split(":")
    if not 1 <= len(delovi) <= 3:
        raise ValueError(f"loše vreme: {tekst}")
    sekunde = 0.0
    for deo in delovi:
        sekunde = sekunde * 60 + float(deo)
    return sekunde


def hms(sekunde: float) -> str:
    """Sekunde -> 'M:SS' ili 'H:MM:SS' (za ispis i komande)."""
    sekunde = max(0.0, sekunde)
    s = int(round(sekunde))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def probe(putanja: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(putanja)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        greska(f"ffprobe ne može da pročita {putanja}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def trajanje(info: dict) -> float:
    return float(info.get("format", {}).get("duration") or 0)


def ima_zvuk(info: dict) -> bool:
    return any(s.get("codec_type") == "audio" for s in info.get("streams", []))


def pokreni(komanda: list[str], cwd: Path | None = None) -> None:
    r = subprocess.run(komanda, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(" ".join(komanda), file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr)
        greska("ffmpeg nije uspeo (gore je kraj njegovog izveštaja).")


# ---------------------------------------------------------------- titlovi

_VTT_VREME = re.compile(
    r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})\s*-->\s*(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})"
)
_OZNAKA_VREMENA = re.compile(r"<(\d+:)?\d{1,2}:\d{2}[.,]\d{3}>")


def _sek(h, m, s, ms) -> float:
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _ocisti(tekst: str) -> str:
    tekst = re.sub(r"<[^>]+>", "", tekst)
    tekst = html.unescape(tekst)
    return re.sub(r"\s+", " ", tekst).strip()


def ucitaj_reci(putanja: Path) -> list[tuple[float, float, str]]:
    """Učita SRT/VTT i vrati listu reči (početak, kraj, reč) u vremenu izvornog videa.

    YouTube automatski titlovi (VTT) imaju vreme za svaku reč u oznakama <00:00:01.230>;
    tada se koriste prava vremena. Kod običnih titlova vreme rečenice se deli na reči
    srazmerno dužini reči.
    """
    tekst = putanja.read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")

    # Kju počinje redom sa vremenom i traje do potpuno praznog reda. YouTube u kjuu ima
    # red sa jednim razmakom, pa se ne sme deliti na "redovima sa samo belinom".
    kjuovi: list[tuple[float, float, list[str]]] = []
    tekuci: list[str] | None = None
    for red in tekst.split("\n"):
        m = _VTT_VREME.search(red)
        if m:
            g = m.groups()
            tekuci = []
            kjuovi.append((_sek(*g[:4]), _sek(*g[4:]), tekuci))
        elif red == "":
            tekuci = None
        elif tekuci is not None:
            tekuci.append(red)

    ima_oznake = any(_OZNAKA_VREMENA.search(r) for _, _, rr in kjuovi for r in rr)
    reci: list[tuple[float, float, str]] = []

    if ima_oznake:
        # Uzimamo samo redove sa oznakama vremena: to su nove reči. Ostali redovi u
        # YouTube titlovima samo ponavljaju prethodni red.
        for pocetak, kraj, redovi in kjuovi:
            for red in redovi:
                if not _OZNAKA_VREMENA.search(red):
                    continue
                delovi = re.split(r"(<(?:\d+:)?\d{1,2}:\d{2}[.,]\d{3}>)", red)
                t = pocetak
                for deo in delovi:
                    mo = re.fullmatch(r"<(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})>", deo)
                    if mo:
                        t = _sek(*mo.groups())
                        continue
                    for rec in _ocisti(deo).split():
                        reci.append((t, kraj, rec))
        # kraj reči = početak sledeće (ali najviše 1,2 s)
        for i in range(len(reci)):
            p, k, r = reci[i]
            sledeci = reci[i + 1][0] if i + 1 < len(reci) else k
            reci[i] = (p, max(p + 0.08, min(sledeci, p + 1.2, k if k > p else p + 1.2)), r)
        return reci

    prethodni = ""
    for pocetak, kraj, redovi in kjuovi:
        recenica = _ocisti(" ".join(redovi))
        if not recenica or recenica == prethodni:
            continue
        prethodni = recenica
        delovi = recenica.split()
        ukupno = sum(len(d) + 1 for d in delovi)
        t = pocetak
        for d in delovi:
            dt = (kraj - pocetak) * (len(d) + 1) / ukupno
            reci.append((t, t + dt, d))
            t += dt
    return reci


def ass_tekst(tekst: str) -> str:
    """Tekst za ASS: bez vitičastih zagrada i obrnutih kosih crta."""
    return tekst.replace("\\", "/").replace("{", "(").replace("}", ")")


def prelomi(tekst: str, max_znakova: int) -> list[str]:
    redovi, red = [], ""
    for rec in tekst.split():
        if red and len(red) + 1 + len(rec) > max_znakova:
            redovi.append(red)
            red = rec
        else:
            red = f"{red} {rec}".strip()
    if red:
        redovi.append(red)
    return redovi


def ass_vreme(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"
