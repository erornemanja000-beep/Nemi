# Nemi Studio: novi sajt (nemistudio.at)

Pregled uživo: https://erornemanja000-beep.github.io/Nemi/nemistudio/
(`?intro=0` preskače uvodni film, `?intro=1` ga uvek pušta, `?lang=en` engleski)

## v4: čula („sajt u sajtu“, po principu referentnih reelova)
1. **Uvodni film** (33 s, DE/EN, 16:9 i 9:16): priča o tragovima.
   - „Seit es Menschen gibt, hinterlassen wir Spuren.“ Zatim šaka u pećini, znak u kamenu, ime na papiru, glas na radiju i lice na ekranu.
   - „Immer mit demselben Wunsch: gesehen zu werden.“, pa „Heute ist deine Spur deine Website.“, pa „Die meisten Websites schweigen.“
   - Kraj: „Hinterlass eine, die bleibt.“, zatim logo nemi.
   - Svaki red ima svoj efekat teksta: zamućenje, udarac, maska, dleto, pisaća mašina, radio-talas, glitch, razmicanje slova, nestajanje.
   - Slika „putuje kroz vreme“: oko je današnje i oštro; prošlost je u sepiji, sa ogrebotinama i treperenjem; do „gesehen zu werden“ slika postaje čista i u boji.
   - Oko je izoštreno AI uvećanjem (Real-ESRGAN x2).
2. **Početak**: zamućen laptop, „Websites, die man spürt.“ Skrol izoštri i uleti u ekran.
3. **Četiri sveta, svaki je jedno čulo.** Bez imena firmi i cena; u ekranu piše „Dein Café / Deine Kanzlei …“.
   - Kafić: miris i ukus (para, zrna, espreso, latte art, hleb, peciva). Slova se dižu kao para.
   - Kancelarija: osećaj u stomaku i sluh (pogled, potpis, razgovor, rukovanje, ugovor). Slova se „dekodiraju“.
   - Teretana: dodir i puls (zavoji, senka boksera, udarci, girja, znoj, dah). Ekran pulsira kao srce, a reči udaraju.
   - Hotel: vid i sluh (lan na prozoru, jezero, trava, bazen, terasa, zvezde). Slika se izoštrava kao objektiv.
4. Svaki svet je **film koji se skroluje** (WebGL): 6 poglavlja po 30 kadrova, kao na referentnim sajtovima.
   - Prelazi: svetlosni prelaz, pikseli, gorenje, zum kroz kadar, trake.
   - Kad staneš sa skrolovanjem, kamera se zaustavi na poglavlju.
5. **Zum nazad**: „Fünf Sinne. Und ein sechster.“
6. **Šesto čulo**: rečenica se dekodira iz šuma. „Nemi“ znači nem; dobar sajt govori bez reči.
7. Na kraju: usluge, postupak, FAQ, kontakt.

## Alati
- Uvodni film: `python3 tools/intro_film.py <klipovi> <slike> <izlaz.mp4> [--format reel] [--lang en] --music <mp3> --sr <AI-klipovi>`
- AI uvećanje kadrova: `python3 tools/upscale.py <model.pth> <in.mp4> <out.mp4> "0.9-1.35,2.3-3.45"` (Real-ESRGAN preko spandrel/PyTorch, na CPU-u oko 37 s po kadru)
- Kadrovi svetova: `python3 tools/world_frames.py <klipovi> public/w src/worlds.json`
- Ekrani uređaja: `python3 tools/portals.py <klipovi> <izlaz>`

## Materijal (sve besplatno)
- Video: Mixkit (Mixkit Stock Video Free License) i Coverr (Coverr License, bez obaveznog navođenja).
- Fotografije u uvodu: Unsplash (preuzimanja zabeležena preko Unsplash API-ja).
- Muzika u uvodu: Mixkit 543.

## Pokretanje
```
npm install
npm run dev
npm run build && python3 build_pages.py <gh-pages-folder>
```

## Otvoreno
- Impressum/Datenschutz: fale ime, adresa, UID i hosting (označeno narandžasto na stranicama).
- Formular otvara e-mail program (mailto); kad se zna hosting, može pravo slanje (npr. Netlify Forms).
- Sledeća čula/branše (zanat, zubar, frizer, restoran) po istom obrascu.
- `noindex` je uključen dok je ovo pregled.
