# Nemi Studio: novi sajt (nemistudio.at)

Pregled uživo: https://erornemanja000-beep.github.io/Nemi/nemistudio/
(`?intro=0` preskače uvodni film, `?intro=1` ga uvek pušta, `?lang=en` engleski; dugme „Intro ansehen“ na početku, u meniju i u futeru ga pušta ponovo)

## v4: čula („sajt u sajtu“, po principu referentnih reelova)
1. **Uvodni film** (25 s, DE/EN, 16:9 i 9:16): priča o tragovima. Svaka scena počinje na udarac muzike.
   - Oko se otvori sa zenicom tačno u centru kadra; kamera kreće od prvog kadra i bez reza, sve brže, uleti u zenicu.
   - „Seit es Menschen gibt, hinterlassen wir Spuren.“ Zatim šaka u pećini, znak u kamenu, ime na papiru, glas na radiju i lice na ekranu.
   - „Immer mit demselben Wunsch: gesehen zu werden.“, pa „Heute ist deine Spur deine Website.“, pa „Die meisten Websites schweigen.“
   - Kraj: „Hinterlass eine, die bleibt.“, zatim logo nemi.
   - Svaki red ima svoj efekat teksta: zamućenje, udarac, maska, dleto, pisaća mašina, radio-talas, glitch, razmicanje slova, nestajanje.
   - Slika „putuje kroz vreme“: oko je današnje i oštro; prošlost je u sepiji, sa ogrebotinama i treperenjem; do „gesehen zu werden“ slika postaje čista i u boji.
   - Tri glavna kadra su izoštrena AI uvećanjem (Real-ESRGAN x2, 2560 px): oko na početku, ekran u oku i lice sa naočarima.
   - Verzija 9:16 za Instagram ima posebno kadriranje kad je motiv van centra (šaka, oko).
2. **Početak**: zamućen laptop, „Websites, die man spürt.“ Skrol izoštri i uleti u ekran.
3. **Četiri sveta, svaki je jedno čulo.** Bez imena firmi i cena; u ekranu piše „Dein Café / Deine Kanzlei …“.
   - Kafić: miris i ukus (para, zrna, espreso, latte art, hleb, peciva). Slova se dižu kao para.
   - Kancelarija: osećaj u stomaku i sluh (pogled, potpis, razgovor, rukovanje, ugovor). Slova se „dekodiraju“.
   - Teretana: dodir i puls (zavoji, senka boksera, udarci, girja, znoj, dah). Ekran pulsira kao srce, a reči udaraju.
   - Hotel: vid i sluh (lan na prozoru, jezero, trava, bazen, terasa, zvezde). Slika se izoštrava kao objektiv.
4. Svaki svet je **film koji se skroluje** (WebGL): 6 poglavlja po 40 kadrova, kao na referentnim sajtovima.
   - Brzi snimci su skraćeni ili zamenjeni (bokser: usporeni snimak 40966, rukovanje: 46755) da skrol bude gladak.
   - Prelazi: svetlosni prelaz, pikseli, gorenje, zum kroz kadar, trake.
5. **Zum nazad**: „Das war kein Film. Das waren Websites.“
6. **Šesto čulo**: rečenica se dekodira iz šuma. „Nemi“ znači nem; dobar sajt govori bez reči.
7. Na kraju: usluge, postupak, FAQ, kontakt.
8. **Futer**: veliko „nemi“; tačka iznad „i“ se pretvori u narandžastog leptira i odleti, „i“ se istopi (ponavlja se pri svakom dolasku do dna).

Ključne reči u tekstu su istaknute (`*reč*` u content.js/worlds.js): kurziv, narandžasto u uvodnim pasusima, u svetovima u boji tog sveta.
Svetli dnevni snimci u kancelariji (žena, rukovanje, ugovor, potpis) dobili su tamniji filmski kolor (`GRADE` u tools/world_frames.py); poslednji kadar teretane je nova borkinja u crveno-plavom svetlu (40988).

## Zamena starog sajta na nemistudio.at (Cloudflare)
Stari sajt („Nemi’s“) je na Cloudflare-u (domen nemistudio.at i www idu preko Cloudflare-a). Novi sajt je spreman za produkciju
(bez noindex, canonical https://nemistudio.at/, og.jpg, robots.txt, sitemap.xml).

**Ručno (dashboard, jednom):** Workers & Pages → Create → Pages → Connect to Git → repo erornemanja000-beep/Nemi,
production branch `gh-pages`, framework None, build command prazno, output `nemistudio` → Save and Deploy.
Zatim u starom projektu Custom domains: ukloniti nemistudio.at i www; u novom: dodati nemistudio.at i www.
Posle toga svaki `build_pages.py` + push na gh-pages ide automatski na nemistudio.at.

**Preko API-ja (ako postoji env `CLOUDFLARE_API_TOKEN`: Pages Edit, Workers Scripts Edit, Zone DNS Edit + Zone Read za nemistudio.at):**
1. `curl -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" https://api.cloudflare.com/client/v4/user/tokens/verify`
2. ID naloga: `GET /accounts`; ID zone: `GET /zones?name=nemistudio.at`
3. Gde je stari sajt: `GET /accounts/{acc}/pages/projects` (polje domains) ili `GET /accounts/{acc}/workers/domains`
4. Novi projekat i deploy: `cd nemistudio && npm run build && CLOUDFLARE_ACCOUNT_ID={acc} npx wrangler pages project create nemistudio-site --production-branch main`
   pa `npx wrangler pages deploy dist --project-name nemistudio-site --branch main`
5. Domeni: `DELETE /accounts/{acc}/pages/projects/{stari}/domains/nemistudio.at` (i www),
   `POST /accounts/{acc}/pages/projects/nemistudio-site/domains` sa `{"name":"nemistudio.at"}` (i www)
6. DNS u zoni: CNAME `nemistudio.at` i `www` → `nemistudio-site.pages.dev` (proxied); stare zapise ka starom sajtu izmeniti (`PATCH /zones/{zone}/dns_records/{id}`)
7. Provera: `curl -sI https://nemistudio.at` i da index.html sadrži „Websites, die man spürt“.

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
