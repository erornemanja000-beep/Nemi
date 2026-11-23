#!/usr/bin/env python3
"""Transkript sa vremenom svake reči (faster-whisper), za titlove u split.py.

Pokreće se iz venv-a (vidi BEZBEDNOST.md). Zvuk dekodira ffmpeg, a Whisper dobija gotov niz uzoraka:
zakucani faster-whisper 1.2.1 zove av.open(..., metadata_errors=...), a zakucani av 19 tu opciju više nema.

Primer:
  python clipper/transkript.py clipper/ulaz/klip.mp4            # pravi clipper/ulaz/klip.reci.json
  python clipper/transkript.py klip.mp4 --od 5 --do 15 --jezik en

Izlaz je lista reči [{"p": početak, "k": kraj, "r": "reč"}] u vremenu izvornog videa; split.py ga čita
preko --titlovi klip.reci.json.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent
MODEL = KOREN / "modeli" / "faster-whisper-large-v3-turbo"
SR = 16000


def ucitaj_zvuk(video: Path, od: float, do: float | None):
    import numpy as np

    komanda = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{od:.3f}"]
    if do is not None:
        komanda += ["-t", f"{do - od:.3f}"]
    komanda += ["-i", str(video), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    r = subprocess.run(komanda, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"GREŠKA: ffmpeg ne može da pročita zvuk: {r.stderr.decode(errors='replace')[-500:]}")
    return np.frombuffer(r.stdout, dtype=np.float32)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--od", type=float, default=0.0)
    p.add_argument("--do", dest="do_", type=float)
    p.add_argument("--jezik", default="en")
    p.add_argument("--izlaz", help="podrazumevano <video>.reci.json")
    args = p.parse_args()

    # bez poziva ka Hugging Face-u (model je već preuzet i heš proveren)
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    if not (MODEL / "model.bin").exists():
        sys.exit(f"GREŠKA: nema modela u {MODEL} (preuzimanje je opisano u BEZBEDNOST.md, deo 7).")

    from faster_whisper import WhisperModel

    video = Path(args.video).resolve()
    zvuk = ucitaj_zvuk(video, args.od, args.do_)
    model = WhisperModel(str(MODEL), device="cpu", compute_type="int8")
    segmenti, _ = model.transcribe(zvuk, language=args.jezik, word_timestamps=True, vad_filter=True)

    reci = []
    for s in segmenti:
        print(f"[{s.start + args.od:7.2f}–{s.end + args.od:7.2f}] {s.text.strip()}")
        for w in s.words or []:
            rec = w.word.strip()
            if rec:
                reci.append({"p": round(w.start + args.od, 3), "k": round(w.end + args.od, 3), "r": rec})

    izlaz = Path(args.izlaz) if args.izlaz else video.with_suffix(".reci.json")
    izlaz.write_text(json.dumps(reci, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{len(reci)} reči → {izlaz}")


if __name__ == "__main__":
    main()
