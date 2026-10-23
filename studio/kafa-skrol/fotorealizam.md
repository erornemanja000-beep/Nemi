# Plan: fotorealizam bez troška (zaključak sastanka tima, 23.10.2026)

Učesnici:
- `recenzent`: dijagnoza, `dijagnoza-3d.md`;
- `istrazivac` ×2: `stock-video.md` i `fotografije.md`;
- `trend-skaut`: `studio/znanje/ai-alati.md`, deo C;
- `bezbednost`: `studio/znanje/izvori-i-licence.md`;
- `blender-umetnik`: dokaz na šolji.

## Realna granica

- **Besplatno i bez GPU-a** stiže se do oko **3,5 od 5**, gde je 5 „ne razlikuje se od referentnog AI videa".
  - Najbolje prolaze predmeti: keramika, inox i staklo (3,5–4).
  - Slabije prolaze tečnost i zrna u letu (3).
  - Para je najbolja kao pravi snimak (4).
- **AI video je jedini put do 5/5.** Postoje dve mogućnosti:
  - Artlist, posle obnove kredita 9.11.;
  - **Google Flow na korisnikovom nalogu:** 50 besplatnih kredita dnevno, a klip 720p od 4 s košta 7 kredita. Prompt piše `prompt-video`, a korisnik generiše.
  - Besplatni nivoi Hailuo, Pika i Kling ne smeju na sajt klijenta.

## Odluka po kadru

| Kadar | Rešenje | Ocena | CPU render (procena) |
|---|---|---|---|
| GRIND | Blender: foto-studio svetlo (dijagnoza, tačka 1), inox sa mapom otisaka, bevel, DOF, motion blur na zrnima | 3,5 | 1,6–7 h |
| prelaz zrna | Blender, ista simulacija i šav kao u `storyboard.md` (opcija C) | 3 | u GRIND/POUR |
| POUR | Blender: V60, bokal, kuvalo, mlaz (karta za transmisiju, Volume Absorption) + **pravi snimak pare na crnom** preko `mix-blend-mode: screen` | 3,5 (para 4) | 5–10 h |
| talas | kod (SVG/WebGL maska), bez rendera | 3–3,5 | 0 |
| SIP | Blender šolja (dokaz 3/5: ispraviti glazuru u sivo-zelenu „ovsenu" sa smeđim pegama, ispeći proceduralne mape, kamera ~13–22°) + pravi snimak pare | 3,5–4 | 2,5–5 h |
| kese | Blender sa pravom etiketom iz dizajna (bez AI teksta) | 3,5–4 | ~10 min po kesi |
| prodavnica, O nama, Brew guide, Kontakt | prave fotografije sa licencom iz `fotografije.md` (Unsplash/Pexels, ručno preuzete) | 5 | 0 |
| ceo sajt | CSS svetlosni gradijent pozadine, traka stola, zrno filma 3–5 % (`overlay`) | — | 0 |

## Pravila izrade

- **Svetlo i kamera:** sve scene prelaze na isti foto-studio raspored iz `sip.py`, koji se seli u `scripts/blender/common.py`: `photo_studio_lights`, `area_light`, `flag`, `world_hdri`, `mat_surface`.
- **Render:** jedna po jedna sekvenca, nikad paralelno, a vreme se planira u CPU-sekundama.
  - Nepomični delovi kadra renderuju se jednom kao „ploča", a po kadru samo region koji se menja.
  - Prvo idu 3 probna kadra po sceni, pa tek onda cela sekvenca.
- **Stock i fotografije:**
  - preuzima samo `mediji`, po `studio/znanje/izvori-i-licence.md`;
  - sirovi fajlovi idu u `studio/kafa-skrol/izvori/` (ne objavljuje se), a manifest u `studio/kafa-skrol/izvori.md`;
  - za Mixkit se licenca proverava na stranici svakog klipa, jer samo *Free* sme na sajt.
- **Ako korisnik izabere Google Flow:**
  - `prompt-video` piše promptove po storyboard-u, a za početni kadar koristi naš Blender render;
  - klipove obrađuje `mediji`;
  - pre upotrebe se proverava da li AI Act čl. 50 traži oznaku na sajtu.
