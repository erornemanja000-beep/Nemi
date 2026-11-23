#!/usr/bin/env python3
"""Pravi uspravni TikTok/Shorts klip 1080×1920: gore pozadina (igrica/animacija), dole isečak streamera.

Primer:
  python3 clipper/split.py --dole ulaz/speed.mp4 --od 1:23 --do 2:10 \\
      --naslov "Speed prvi put vidi GTA 6" --titlovi ulaz/speed.en.vtt \\
      --autor "@IShowSpeed" --izlaz izlaz/speed_gta.mp4

Pozadina: --gore <video>, ili nasumično iz clipper/pozadine/*.mp4.
Brza provera rasporeda bez celog rendera: --slika 3 (pravi PNG kadra u 3. sekundi).
"""

from __future__ import annotations

import argparse
import random
import shutil
import tempfile
from pathlib import Path

from alati import (FONTOVI, KOREN, ass_tekst, ass_vreme, greska, hms, ima_zvuk, pokreni,
                   prelomi, probe, proveri_ffmpeg, trajanje, ucitaj_reci, vreme)

S, V = 1080, 1920          # ceo kadar
POLA = V // 2              # visina jedne polovine
FPS = 30

# TikTok pokriva gornjih ~200 px (Following / For You) i donjih ~400 px (opis, ime),
# a desno su dugmad. Naslov zato počinje na 250 px, a titlovi stoje na spoju polovina.
NASLOV_Y = 250
NASLOV_VELICINA = 88
NASLOV_RED = 100           # visina reda naslova u px
TITL_VELICINA = 86
ZUTA = "&H0000E6FF"        # ASS boja je &HAABBGGRR

ASS_ZAGLAVLJE = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {S}
PlayResY: {V}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Naslov,Inter Black,{NASLOV_VELICINA},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,7,3,8,50,50,{NASLOV_Y},1
Style: Titl,Inter Black,{TITL_VELICINA},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,8,3,5,40,40,0,1
Style: Autor,Inter Bold,34,&H20FFFFFF,&H20FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,8,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def grupisi(reci, max_reci=3, max_znakova=16, pauza=0.6):
    """Reči u kratke grupe (2–3 reči) koje se smenjuju na ekranu."""
    grupe, grupa = [], []
    for rec in reci:
        if grupa:
            tekst = " ".join(r[2] for r in grupa + [rec])
            prekid = (
                len(grupa) >= max_reci
                or len(tekst) > max_znakova
                or rec[0] - grupa[-1][1] > pauza
                or grupa[-1][2][-1:] in ".?!,"
            )
            if prekid:
                grupe.append(grupa)
                grupa = []
        grupa.append(rec)
    if grupa:
        grupe.append(grupa)
    return grupe


def napravi_ass(args, duzina: float, reci) -> str:
    redovi = [ASS_ZAGLAVLJE]
    kraj_svega = ass_vreme(duzina)

    if args.naslov:
        linije = prelomi(args.naslov.upper(), 18)
        do = ass_vreme(min(duzina, args.naslov_trajanje)) if args.naslov_trajanje else kraj_svega
        tekst = r"\N".join(ass_tekst(l) for l in linije)
        redovi.append(f"Dialogue: 2,0:00:00.00,{do},Naslov,,0,0,0,,"
                      r"{\fad(120,0)}" + tekst)
        autor_y = NASLOV_Y + len(linije) * NASLOV_RED + 18
    else:
        autor_y = NASLOV_Y

    if args.autor:
        redovi.append(f"Dialogue: 1,0:00:00.00,{kraj_svega},Autor,,0,0,{autor_y},,"
                      + ass_tekst(args.autor))

    for grupa in grupisi(reci):
        tekst_reci = [ass_tekst(r[2].upper() if not args.mala_slova else r[2]) for r in grupa]
        for i, (pocetak, _, _) in enumerate(grupa):
            kraj = grupa[i + 1][0] if i + 1 < len(grupa) else grupa[-1][1]
            if kraj <= pocetak:
                continue
            delovi = [
                ("{\\c" + ZUTA + "&}" + t + "{\\c&H00FFFFFF&}") if j == i else t
                for j, t in enumerate(tekst_reci)
            ]
            pop = r"{\fscx80\fscy80\t(0,90,\fscx100\fscy100)}" if i == 0 else ""
            redovi.append(
                f"Dialogue: 3,{ass_vreme(pocetak)},{ass_vreme(kraj)},Titl,,0,0,0,,"
                + r"{\an5\pos(" + f"{S // 2},{POLA}" + ")}" + pop + " ".join(delovi)
            )
    return "\n".join(redovi) + "\n"


def filter_dole(args) -> str:
    f = []
    if args.isecak:
        try:
            x, y, w, h = (float(v) for v in args.isecak.split(":"))
        except ValueError:
            greska("--isecak se piše kao x:y:sirina:visina u delovima kadra, npr. 0.7:0.05:0.28:0.3")
        f.append(f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y}")
    if args.kadar == "ceo":
        osnova = ",".join(f) + "," if f else ""
        return (
            f"[0:v]{osnova}split[d1][d2];"
            f"[d1]scale={S}:{POLA}:force_original_aspect_ratio=increase,crop={S}:{POLA},"
            f"boxblur=24:2,eq=brightness=-0.12[dz];"
            f"[d2]scale={S}:{POLA}:force_original_aspect_ratio=decrease[dp];"
            f"[dz][dp]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={FPS}[dole]"
        )
    f.append(f"scale={S}:{POLA}:force_original_aspect_ratio=increase")
    f.append(f"crop={S}:{POLA}:(iw-ow)*{args.fokus}:(ih-oh)*{args.fokus_y}")
    f.append(f"setsar=1,fps={FPS}")
    return "[0:v]" + ",".join(f) + "[dole]"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dole", required=True, help="video streamera (izvor)")
    p.add_argument("--gore", help="pozadina; bez ovoga se uzima nasumično iz clipper/pozadine/")
    p.add_argument("--od", default="0", help="početak u izvoru (83, 1:23, 0:01:23.5)")
    p.add_argument("--do", dest="do_", help="kraj u izvoru")
    p.add_argument("--trajanje", help="umesto --do: koliko sekundi")
    p.add_argument("--naslov", help="udica na vrhu klipa (piše se velikim slovima)")
    p.add_argument("--naslov-trajanje", type=float, help="koliko sekundi se vidi naslov (podrazumevano ceo klip)")
    p.add_argument("--autor", help="ko je u klipu, npr. @IShowSpeed")
    p.add_argument("--titlovi", help="SRT ili VTT (npr. YouTube automatski titlovi), u vremenu izvora")
    p.add_argument("--mala-slova", action="store_true", help="titlovi kako su napisani, ne velikim slovima")
    p.add_argument("--kadar", choices=["iseci", "ceo"], default="iseci",
                   help="iseci = popuni polovinu (seče strane), ceo = ceo kadar na zamućenoj pozadini")
    p.add_argument("--fokus", type=float, default=0.5, help="vodoravno 0 (levo) … 1 (desno) kod sečenja")
    p.add_argument("--fokus-y", type=float, default=0.5, help="uspravno 0 (gore) … 1 (dole) kod sečenja")
    p.add_argument("--isecak", help="deo izvora x:y:sirina:visina (0–1), npr. samo kamera streamera")
    p.add_argument("--zamena", action="store_true", help="streamer gore, pozadina dole")
    p.add_argument("--gore-od", help="odakle počinje pozadina (podrazumevano nasumično)")
    p.add_argument("--traka", action="store_true", help="tanka traka napretka na spoju polovina")
    p.add_argument("--seed", type=int, help="za ponovljiv izbor pozadine i njenog početka")
    p.add_argument("--slika", type=float, help="umesto videa napravi PNG kadra u ovoj sekundi klipa")
    p.add_argument("--izlaz", required=True, help="izlazni .mp4 (ili .png uz --slika)")
    args = p.parse_args()

    proveri_ffmpeg()
    rng = random.Random(args.seed)

    dole = Path(args.dole).resolve()
    if not dole.exists():
        greska(f"ne postoji: {dole}")
    info = probe(dole)
    duzina_izvora = trajanje(info)

    od = vreme(args.od)
    if args.do_:
        do = vreme(args.do_)
    elif args.trajanje:
        do = od + vreme(args.trajanje)
    else:
        do = duzina_izvora
    do = min(do, duzina_izvora) if duzina_izvora else do
    duzina = do - od
    if duzina <= 0.5:
        greska(f"isečak je prekratak ({od:.1f}–{do:.1f} s; video traje {duzina_izvora:.1f} s)")

    # pozadina
    if args.gore:
        gore = Path(args.gore).resolve()
        if not gore.exists():
            greska(f"ne postoji: {gore}")
    else:
        kandidati = sorted((KOREN / "pozadine").glob("*.mp4"))
        gore = rng.choice(kandidati) if kandidati else None
    if gore:
        duzina_gore = trajanje(probe(gore))
        if args.gore_od is not None:
            gore_od = vreme(args.gore_od)
        else:
            gore_od = rng.uniform(0, max(0.0, duzina_gore - duzina)) if duzina_gore > duzina else 0.0
        ulaz_gore = ["-stream_loop", "-1", "-ss", f"{gore_od:.3f}", "-i", str(gore)]
    else:
        print("Napomena: nema pozadine u clipper/pozadine/, koristim pokretne prelive.")
        ulaz_gore = ["-f", "lavfi", "-i", f"gradients=s={S}x{POLA}:r={FPS}:speed=0.015:n=6:seed={rng.randint(0, 9999)}"]

    reci = []
    if args.titlovi:
        sve = ucitaj_reci(Path(args.titlovi))
        reci = [(p - od, k - od, r) for p, k, r in sve if p >= od - 0.05 and p < do]
        if not reci:
            print("Napomena: u titlovima nema reči u izabranom delu (proveri --od/--do).")

    izlaz = Path(args.izlaz).resolve()
    izlaz.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="clipper_") as tmp:
        tmp = Path(tmp)
        # ffmpeg radi u privremenom folderu, pa se u filteru koriste kratke relativne putanje
        # (inače Windows putanje sa dvotačkom kvare filter).
        (tmp / "fontovi").mkdir()
        for font in [*FONTOVI.glob("*.otf"), *FONTOVI.glob("*.ttf")]:
            shutil.copy(font, tmp / "fontovi" / font.name)
        (tmp / "t.ass").write_text(napravi_ass(args, duzina, reci), encoding="utf-8")

        gore_filter = (f"[1:v]scale={S}:{POLA}:force_original_aspect_ratio=increase,"
                       f"crop={S}:{POLA},setsar=1,fps={FPS}[gore]")
        gornji, donji = ("[dole]", "[gore]") if args.zamena else ("[gore]", "[dole]")
        delovi = [filter_dole(args), gore_filter,
                  f"{gornji}{donji}vstack=inputs=2:shortest=1[st]"]
        posle = "[st]"
        if args.traka:
            delovi.append(f"color=c=0xFFE600:s={S}x8:r={FPS}[bar]")
            delovi.append(f"[st][bar]overlay=x='-W+W*t/{duzina:.3f}':y={POLA - 4}:eval=frame:shortest=1[sb]")
            posle = "[sb]"
        delovi.append(f"{posle}ass=t.ass:fontsdir=fontovi,format=yuv420p[v]")

        komanda = ["ffmpeg", "-hide_banner", "-y",
                   "-ss", f"{od:.3f}", "-t", f"{duzina:.3f}", "-i", str(dole), *ulaz_gore]
        if args.slika is not None:
            pass  # samo slika, bez zvuka
        elif ima_zvuk(info):
            delovi.append("[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
        else:
            komanda += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
            delovi.append("[2:a]anull[a]")
        komanda += ["-filter_complex", ";".join(delovi)]

        if args.slika is not None:
            komanda += ["-map", "[v]", "-ss", f"{args.slika:.3f}", "-frames:v", "1", str(izlaz)]
        else:
            komanda += ["-map", "[v]", "-map", "[a]", "-t", f"{duzina:.3f}",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
                        "-pix_fmt", "yuv420p", "-r", str(FPS),
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(izlaz)]
        pokreni(komanda, cwd=tmp)

    print(f"Gotovo: {izlaz}  ({hms(duzina)}, izvor {hms(od)}–{hms(do)}"
          + (f", pozadina {gore.name}" if gore else "") + ")")
    if args.slika is None and duzina <= 60:
        print("Napomena: klip traje do 60 s. Za rast je to dobro, ali TikTok Creator Rewards plaća samo videe duže od 1 minuta.")


if __name__ == "__main__":
    main()
