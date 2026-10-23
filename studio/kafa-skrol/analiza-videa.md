# Analiza videa: skrol-sajt za kafu („Grind → Pour → Sip")

Izvor: Instagram reel naloga Enkis Web Studio (enkywebstudio), objavljen 18.10.2026.
- Trajanje: 8,06 s, 213 kadrova (26,4 fps), 1080×1920.
- Na snimku je laptop na drvenom stolu, a na ekranu se skroluje sajt kafe brenda „POUR / PLAY · Specialty Coffee".
- Pregledan je svaki drugi kadar, a prelazi kadar po kadar. Kadrovi su sačuvani samo lokalno, ne u repou, jer je to tuđ snimak.

## Ključni nalaz: sajt ne postoji, video je AI

- Sav sitan tekst na ekranu je izmišljena slovna masa. Primeri su meni („SECEKTION"), dugme („OLAS NICPT") i pozadinske reči („Lon…", „Peu…are", „Fro…her") koje menjaju oblik od kadra do kadra.
- Kamera i laptop se pomeraju, a odsjaji su generisani. Ceo snimak je napravio AI video generator. To je **koncept**, a ne pravi sajt koji bi mogao da se kopira.
- Za nas to znači sledeće: pravimo **pravi** sajt po istom principu, sa našim brendom, našim tekstom i 3D sadržajem iz Blendera.
- Ime „POUR / PLAY", njihove reči i raspored kartica ne kopiramo, po pravilu iz `CLAUDE.md`: uzima se princip, ne kopija.

## Struktura sajta (redom)

| Vreme | Šta se vidi | Šta je tehnički |
|---|---|---|
| 0,00–0,80 s | **Poglavlje 1 · GRIND** (hero). Krem pozadina. Levo: „Section 1", veliki naslov GRIND, kratak tekst, tamno dugme u obliku pilule. Desno: mlin za kafu (inox + stakleni levak), zrna padaju odozgo u levak, mleta kafa curi iz otvora. Iza mlina ogromna pozadinska reč u braon boji, u dekorativnom serif fontu, koja se pomera polako. Strelice levo i desno za karusel. | zakačena (pin) sekcija; 3D sekvenca slika sa providnom pozadinom; reč je HTML tekst sa parallax-om |
| 0,80–1,50 s | **Prelaz GRIND → POUR.** Stranica ide nagore, mlin izlazi gore, a mleta kafa i zrna **nastavljaju da padaju preko granice sekcija** i upadaju u dripper u sledećoj sekciji. Braon sekcija ulazi odozdo. | neprekinut predmet između dve sekcije: sekvenca je prekrivena preko obe sekcije (fixed canvas), a granica sekcija klizi ispod nje |
| 1,50–4,40 s | **Poglavlje 2 · POUR.** Terakota pozadina. Gooseneck kuvalo gore desno sipa tanak mlaz vode u V60 dripper sa papirnim filterom na staklenom bokalu. Para se diže, kafa kaplje i nivo u bokalu raste. Iza drippera je ogromna tamnobraon reč, a pored bokala par zrna. | 3D sekvenca (mlaz, para, nivo tečnosti) vezana za skrol |
| 4,40–5,80 s | **Prelaz POUR → SIP:** talas tečne kafe. Sjajna ćilibarna površina tečnosti se diže odozdo i preplavi ekran. Kroz nju se vidi šolja (tečnost radi kao sočivo), pa se talas povlači i ostaje treća sekcija. | maska talasa (SVG/canvas sa gradijentom i sjajem) ili renderovan talas iz Blendera, preko granice sekcija |
| 5,80–7,20 s | **Poglavlje 3 · SIP.** Tamnobraon pozadina, keramička šolja sa curećom glazurom u sredini. Uleću **staklene kartice proizvoda** (Origin, Flavor, Roast) sa pakovanjima kafe i cenama. Rotiraju se u 3D i smeštaju oko šolje. Levo naslov SIP, tekst i dugme „Find your cup". Ispod su tačkice karusela. | šolja iz Blendera; kartice su prave HTML kartice (klik vodi na proizvod) sa CSS 3D transformacijama i staklenim efektom |
| 7,20–8,06 s | Sve stoji, a mala zvezdica treperi. Ispod se nazire sledeća sekcija „Find your cup" (prodavnica) na krem pozadini. | — |

**Uvek vidljivo:**
- logo levo („BREND / IME" + mali podnaslov);
- 5 stavki menija u sredini;
- dugme-pilula desno, pretraga i korpa sa brojem;
- okrugli chat balon dole desno.

## Boje (uzorci iz kadrova; video ima svoje svetlo, pa su približne)

| Uloga | Boja |
|---|---|
| krem pozadina (Grind, prodavnica) | `#E6DDCE` |
| tekst / tamno dugme | `#2B2316` |
| terakota pozadina (Pour) | `#915439` |
| tamnobraon pozadina (Sip) | `#6E3A27` |
| pozadinske reči | tamnije ili svetlije od pozadine za oko 15–20 % |

## Tipografija

- Naslovi poglavlja (GRIND, POUR, SIP) su u debelom, uskom grotesku, velikim slovima.
- Pozadinske reči su u dekorativnom serifu sa „mekim" oblicima (stil 70-ih).
- Mali natpisi („Section 1") su razmaknuta velika slova.

## Šta pravimo i čime

| Deo | Alat |
|---|---|
| mlin + zrna (fizika), dripper + kuvalo + mlaz + para + nivo kafe, šolja | **Blender** (Cycles, CPU), sekvence sa providnom pozadinom → WebP |
| pozadinske reči, tekstovi, meni, kartice, prodavnica | HTML/CSS, fontovi lokalno |
| skrol, pin, prelaz zrna, talas tečnosti | JS (canvas sekvence, kao u Freiraum Premium; ili GSAP kao u RealEstates) |
| telefon | lakša sekvenca (manje kadrova i rezolucija); sekcije jedna ispod druge |
| reduced motion | jedan statičan kadar po poglavlju, bez pina |
