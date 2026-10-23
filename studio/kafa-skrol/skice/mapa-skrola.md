# Mapa skrola: POUR / PLAY · Specialty Coffee (privremeno ime)

Uz `skica.html`, `skica-1440.png`, `skica-390.png`. Redosled i tempo su iz `../analiza-videa.md`.

Kako se čita:
- **vh** je visina ekrana (na telefonu `svh`). 100 vh = jedan ekran.
- **Pin sekcija** u CSS-u ima visinu `100 vh + pin skrol`. Tabela navodi pin skrol (koliko se skrola dok sekcija stoji zakačena), a u zagradi ukupnu visinu sekcije.
- Brojevi za tempo su predlog. Podešavaju se kad `animator` vidi pravu sekvencu.

## 1. Tempo: video → skrol

Video traje 8,06 s. Za prosečan korisnički skrol uzeto je oko 140 vh po sekundi videa, uz odstupanja da GRIND ostane kratak, POUR najduži, a SIP srednji.

| Deo | Video | Skrol (vh) | Odnos |
|---|---|---|---|
| 1 GRIND (pin) | 0,0–0,8 s | **120** | kratko |
| Prelaz 1 (bez pina) | 0,8–1,5 s | 100 | prirodni skrol jednog ekrana |
| 2 POUR (pin) | 1,5–4,4 s | **400** | najduže |
| Prelaz 2 (zadržavanje + skrol) | 4,4–5,8 s | 160 (60 + 100) | |
| 3 SIP (pin) | 5,8–7,2 s | **200** | srednje |
| Mirovanje (zvezdica) | 7,2–8,06 s | u SIP-u, bez dodatnog skrola | |
| **Ukupno priča** | | **980 vh** (oko 10 ekrana) | |

Kontrola: POUR je 3,3 puta duži od GRIND-a (u videu 3,6), a SIP 1,7 puta (u videu 1,75).

## 2. Tabela po sekcijama

Desktop je 1440×900, telefon 390×844. Visine običnih sekcija su izmerene u skici (sa napomenama), pa su okvirne.

| Sekcija | Visina (vh) | Pin | Šta se animira | Sa reduced motion | Šta se menja na telefonu |
|---|---|---|---|---|---|
| **1 Header** (fiksan) | 72 px (telefon 56 px), van toka | fiksan (`position: fixed`), ne pin | ništa obavezno. Predlog: aktivna stavka menija prati poglavlje (scroll-spy), tanka linija ispod posle prvih 20 px skrola | isto, bez prelaza | logo (2 reda) + korpa sa brojem + hamburger. Pretraga, DE/EN i „Shop now“ idu u panel hamburgera. „Shop now“ je i dalje u hero-u (dugme „Shop beans“) |
| **2 Poglavlje 1 GRIND** | **220** (100 + 120 pin) | **da, 120 vh skrola** | 0–40 %: zrna padaju odozgo u levak. 40–100 %: mlin radi, mleta kafa curi iz otvora. Pozadinska reč „Longberry“ klizi vodoravno (parallax, oko 10 % širine). Strelice (desno aktivna, levo isključena) i tačkice (1/3) su navigacija po poglavljima, skaču na sledeće | bez pina (sekcija 100 vh), jedan statičan kadar (zrna u levku, malo mlevene kafe). Reč miruje. Strelica radi kao običan link | bez pina, `100 svh`. Redosled: Section 1, GRIND, tekst, dugme, pa mlin ispod. Dugme je iznad 844 px. Strelice sakrivene. Sekvenca ima manje kadrova i vezana je za položaj sekcije u ekranu |
| **3 Prelaz 1** GRIND → POUR | **100** | ne (prirodni skrol), ali fixed canvas preko obe sekcije | zrna i mleta kafa iz otvora mlina **padaju preko granice sekcija** i upadaju u dripper. Mlin izlazi nagore, a POUR (srednji ton) ulazi odozdo. Isti x za otvor mlina i dripper | nema canvasa. Tvrd rez po granici sekcija. Zrna su statična slika u dripperu u POUR kadru | nema fixed canvasa. Zrna padaju jednom (oko 0,8 s) kad POUR uđe u ekran, bez preklapanja dve sekcije |
| **4 Poglavlje 2 POUR** | **500** (100 + 400 pin) | **da, 400 vh skrola** | kuvalo gore desno se naginje, mlaz, para (opacity), kafa kaplje, nivo u bokalu 0 → 100 %. Par zrna pored bokala. Pozadinska reč „Percolate“ iza drippera, isti parallax. Strelice i tačkice (2/3). Najduže poglavlje | bez pina, jedan kadar (V60 sa kapljicom, bokal do pola), bez pare. Reč miruje | bez pina, oko 115 svh. Tekst gore, animacija ispod. Strelice sakrivene. Manje kadrova |
| **5 Prelaz 2** POUR → SIP | **160** (60 zadržavanje + 100 skrol) | prvih 60 vh POUR stoji zakačen | talas tečne kafe (sjajna ćilibarna površina) se diže odozdo i preplavi ekran. Kroz tečnost se vidi šolja (sočivo). Zatim se talas povlači, a SIP ulazi. Jedan fixed sloj (SVG/canvas maska ili render iz Blendera) preko obe sekcije | nema talasa. Tvrd rez, a granica je statična talasasta ivica (jedna SVG linija) | nema fixed sloja. Isti talas kao CSS/SVG traka koja klizi preko granice za oko 60 svh |
| **6 Poglavlje 3 SIP** | **300** (100 + 200 pin) | **da, 200 vh skrola** | 0–35 %: glazura curi niz šolju. 20–80 %: kartice Origin, Flavor, Roast uleću jedna za drugom (3D rotacija, staklo) i staju oko šolje. Poslednjih 20 %: sve stoji. Pozadinska reč „Frother“ iza šolje (najslabiji kontrast od tri). Strelica levo vodi nazad, desna je isključena, tačkice (3/3). Zvezdica treperi (jedina animacija koja nije vezana za skrol, petlja oko 2 s) | bez pina. Kartice su već na mestu, a zvezdica miruje. Tačkice i klik na karticu rade | bez pina, oko 120 svh. Šolja gore, ispod nje kartice u horizontalnoj traci (scroll-snap), a tri tačkice ispod prate traku kartica (ne poglavlja). Reč „Frother“ se ne prikazuje. Ulet kartica zamenjen običnim pojavljivanjem |
| **7 Prodavnica „Find your cup“** (naslov, filteri Origin / Flavor / Roast, izbor mlevenja sa 5 opcija, 6 kafa + 3 komada opreme, traka sa dostavom) | oko 280 (telefon oko 310) | ne | kartice se pojavljuju pri ulasku (fade + pomeraj 16 px, razmak 60 ms). Filtriranje: fade mreže. Nema 3D | bez pojavljivanja i fade-a, filter odmah menja mrežu | 2 kolone. Filteri Origin / Flavor / Roast su horizontalne trake sa prstom. Kartica je kraća: bez nota, datuma prženja i izbora veličine (idu na stranicu proizvoda), a Grundpreis ostaje uz cenu. Oprema je traka sa 3 kartice |
| **8 Pretplata / Probierset** (jedan red) | oko 50 (telefon oko 90) | ne | fade-in pri ulasku | bez animacije | dve kartice jedna ispod druge |
| **9a About** | oko 70 | ne | slika blago klizi (parallax do 40 px), tekst fade-in | bez parallax-a | slika iznad teksta, bez parallax-a |
| **9b Brew guide** | oko 75 (telefon oko 135) | ne | 3 koraka se pojavljuju redom (60 ms razmak) | bez animacije | koraci jedan ispod drugog |
| **10 Contact** | oko 70 | ne | nema | isto | tekst i radno vreme, pa mapa. Mapa je slika, ne iframe |
| **11 Footer** | oko 45 (telefon oko 105) | ne | nema | isto | kolone u dve, logo preko cele širine |
| **Chat balon** | 60 px (telefon 50 px), van toka | fiksan dole desno | pojavljuje se posle 3 s (opacity). Bez zvuka, bez automatskog otvaranja | pojavljuje se odmah | 12 px od ivica. Zadnje dugme na stranici ima 72 px razmaka ispod, da ga balon ne pokrije |

## 3. Prelazi (za animatora)

- **Prelaz 1:** jedan fixed canvas (`z-index` iznad obe sekcije, `pointer-events: none`). Dok je GRIND u pinu, canvas crta mlin. Od početka prelaza 1 crta samo zrna i mlevenu kafu i nastavlja sekvencu u POUR. Na granici sekcija nema reza, jer je canvas isti. Otvor mlina i dripper moraju imati isti x u skici (oko 69 % širine na desktopu).
- **Prelaz 2:** talas je zaseban fixed sloj. Šolja se vidi kroz tečnost, pa sloj mora imati providan prozor ili se šolja crta u istom canvasu ispod mase tečnosti.
- Canvas ne sme da pokrije tekst i dugmad koji su u tom trenutku vidljivi: tekst ostaje HTML iznad ili ispod, uvek klikabilan.

## 4. Kadrovi sekvenci (predlog, treba potvrda od `blender-umetnik` i `mediji`)

U Blenderu se renderuje samo ono što je na skrol sekvenci. Između susednih kadrova se radi crossfade, pa broj ne mora da prati svaki piksel skrola. Blender u ovom okruženju nije instaliran (brief), pa je budžet otvoren.

| Sekvenca | Desktop (kadrova) | Telefon (kadrova) |
|---|---|---|
| GRIND (mlin + zrna) | 60 | 24 |
| Prelaz 1 (zrna preko granice) | 40 | 0 (CSS padanje) |
| POUR (kuvalo, V60, para, nivo) | 120 | 48 |
| Prelaz 2 (talas) | 0 (SVG/CSS) ili 48 iz Blendera | 0 (SVG/CSS) |
| SIP (šolja + glazura) | 72 | 30 |

- Svako poglavlje učitava svoje kadrove tek kad je sledeće na vidiku (lazy). Prvi kadar poglavlja je i poster za reduced motion i za slučaj da JS ne radi.
- Telefon: uža sekvenca (oko 640 px), ista slika za 2x ekrane.

## 5. Pravila koja važe svuda

- **Reduced motion** (`prefers-reduced-motion: reduce`): nema pina, nema fixed canvasa, nema talasa, nema parallax-a, nema treperenja. Svako poglavlje je običan blok od 100 vh sa jednim statičnim kadrom (poster). Sav tekst je vidljiv od početka. Strelice, tačkice, filter i klik na karticu rade, ali odmah, bez prelaza.
- **Telefon:** prelomna tačka oko 900 px. Visine u `svh`, ne `vh`, zbog trake adrese. Nema pina na telefonu: pin plus fixed canvas je najskuplja kombinacija i na telefonu trese stranicu. Prvi ekran: header, Section 1, GRIND, tekst i dugme su iznad 844 px (provereno u skici).
- **Bez WebGL-a i bez JS-a:** poster kadar + tekst + dugmad.
- **Pristupačnost:** strelice i tačkice su pravi `button`-i sa `aria-label`. H1 je skriven (naziv sajta), a GRIND, POUR i SIP su h2. Animacija ne nosi informaciju koje nema u tekstu.
- **Zakon (prodavnica):** Grundpreis je uz svaku cenu kafe, i na karticama u SIP-u. Datum prženja i rok trajanja su na kartici u prodavnici. Napomena „Konzept / Demo“ je u naslovu prodavnice i u footeru.

## 6. Otvoreno

1. Šta rade strelice i tačkice. U skici su navigacija po tri poglavlja na desktopu (isto kao u `tekstovi.md`: „Previous section“, „Go to section n of 3“), a na telefonu ih nema, osim tačkica ispod kartica u SIP-u. Alternativa je da menjaju mlevenje ili kafu u animaciji. Analiza videa pominje strelice samo u GRIND-u, a tačkice samo u SIP-u, pa su ovde prošireni na sva tri poglavlja radi doslednosti.
2. DE/EN prekidač je dodat u header (nije u videu). Ako header ostaje čist kao u videu, ide u footer i u panel hamburgera.
3. Pozadinske reči su iz `tekstovi.md` (Longberry, Percolate, Frother). Analiza videa za SIP ne pominje reč, pa je ona ovde najtiša i može da otpadne.
4. Korpa, checkout (dugme „zahlungspflichtig bestellen“) i stranice proizvoda nisu u ovoj skici.
5. Meni: skica prati spisak iz zadatka (Shop, Coffees, Brew guide, About, Contact). `tekstovi.md` ima drugačiju petoricu (Coffee, Subscription, Brew guide, About, Visit). Treba odluka.
6. Filteri u skici su Origin / Flavor / Roast. `tekstovi.md` ima Brew (Espresso / Filter), Flavor, Roast i Type (Coffee, Decaf, Equipment, Sets), bez Origin-a.
7. Iz `tekstovi.md` ostaju `[FEHLT]`: cena mlina i drippera, pravilo za MHD (na kartici piše „Best before [MHD]“), način plaćanja, dostava van Austrije.
