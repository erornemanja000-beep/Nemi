# Brief: reklama za Nemi Studio (Instagram i TikTok, 10 s)

Izvor činjenica: nemistudio.at (pročitano 25. 10. 2026, tekst iz JS bundla i CSS-a) i ovaj repo.
Ništa van ovog spiska se ne tvrdi u reklami (bez izmišljenih brojeva klijenata, nagrada, cena).

## Zadatak
Video od 10 sekundi koji reklamira sajt nemistudio.at, za Instagram Reels i TikTok.
Mora da koristi sva tri programa koje korisnik uči: **MagicaVoxel** (voksel modeli i scene),
**Blender** (render, svetlo, pokret kamere) i **Pixelorama** (pikselni likovi, ikonice, animacija po kadrovima).
Tekst, prelaze, ritam i zvuk sklapa **Remotion** (`motion/`, React → MP4).

## Format
- 1080 × 1920 (9:16), 30 fps, 10 s = 300 kadrova
- Prva sekunda mora da zaustavi skrol; kraj treba da može da se vrti u krug (loop)
- Bezbedne zone: dole oko 20 % i desna ivica oko 12 % pokrivaju dugmad i opis na TikTok-u i Reels-u
- Mora da radi i bez zvuka (tekst nosi poruku), a sa zvukom svaki pokret ima svoj zvuk
- Korisnik je početnik u ova tri programa: modeli i animacije moraju da se naprave za nekoliko sati

## Brend (sa sajta)
- Ime: **Nemi Studio**, „Webdesign aus Österreich". Kontakt na sajtu: nemistudio7@gmail.com
- Slogan: „Websites, die man *spürt*." (EN: „Websites you can *feel*.")
- Priča imena: „Nemi heißt auf Serbisch ‚*stumm*'. Wir bauen Websites, die *ohne Worte* sprechen: mit Bild, Bewegung und Gefühl."
- Tema sajta: čula. „Riechen, fühlen, sehen, hören. Und der *sechste Sinn*." „Vier Branchen, vier Sinne."
  Primeri: „Ein *Duft*, der durch die ganze Straße zieht." „Ein *Blick*, für den man anreist." „Wasser, das man *hört*." „Hörst du die *Stille*?" „Gute Websites machen *Appetit*."
- Branše: Cafés/Bäckereien/Restaurants; Hotels/Pensionen/Ferienwohnungen; Kanzleien/Beratung/Praxen; Studios/Trainer/Vereine; „Für *alle*."
- Ton: obraća se sa „du", kratke rečenice, jedna reč u rečenici istaknuta kurzivom (serif).
- Boje: ink `#0b0b0c`, ink-2 `#121315`, bone `#efeae2`, bone-2 `#e4ddd2`, signal narandžasta `#ff5a24`
- Fontovi: Geist (sans), Instrument Serif (istaknute reči, kurziv), Geist Mono (sitne oznake)

## Ponuda (sme da se pomene)
- Prvi razgovor: 30 minuta, besplatno
- Ponuda sa fiksnom cenom, bez skrivenih troškova
- Sajt od nule, bez gotovog šablona („ohne Baukasten"); preko linka za pregled vidiš svaki napredak
- Prvo za telefon („zuerst für das Handy"); animacije poštuju smanjeno kretanje
- Prelazi, hover efekti, otkrivanje teksta i 3D; brz kod, osnove SEO-a
- Tekstovi na nemačkom, engleskom i drugim jezicima; fotografije, video i AI vizuali
- Domen, hosting, Google; isti kontakt i posle objavljivanja

## Reference za tehniku (princip, ne kopija)
Analiziran reel (Instagram, 15. 10. 2026): tekst ulazi reč po reč na udarac, ključna reč krupno u boji,
pikselni mozaik između scena, voksel sobe sa mutnom pozadinom, pikselni lik kao vodič, brojači, glitch.
Probni klip sa ovim tehnikama već postoji u `motion/` (`npx --no-install remotion render Probni`).

## Jezik reklame
Nemački (publika su lokali i firme u Austriji). Po želji i engleska verzija istog videa.
