# Storyboard: Kafa skrol (GRIND → POUR → SIP) · 3D sekvence za skrol · desktop i telefon · ukupno ~8 ekrana skrola

Storyboard, 23.10.2026. Ovo nije knjiga snimanja za video, nego plan 3D sekvenci za skrol. Renderuje ih `blender-umetnik` (Blender 5.2 LTS, Cycles CPU, 4 jezgra). Kod piše `programer`/`animator`, a pakovanje radi `mediji`.

Osnova:
- `studio/kafa-skrol/analiza-videa.md`, kadrovi referentnog reela (pregledani lokalno, nisu u repou).
- `brief.md`, `ideje/smer-1..3.md`, `scripts/blender/common.py`.
- Sekvence u `freiraum-premium` (`premium.js`, `seq/*/seq.json`).
- `studio/znanje/ai-alati.md` (deo B, Blender za web).
- Postojeće skripte `scripts/blender/kafa/{grind,pour,sip}.py`. Razlike su u 13.

Oznake:
- **PROCENA**: moj račun, treba ga proveriti na prvom pravom kadru.
- **IZMERENO**: izmereno 23.10.2026 na fajlovima iz repoa.
- **NIJE POTVRĐENO**: nije provereno.

Smer brenda još nije izabran. Zato su boje sveta, glazure, etiketa i talasa **parametri**. Podrazumevane su boje iz videa (krem `#E6DDCE`, terakota `#915439`, tamnobraon `#6E3A27`). Geometrija, kamera, fizika i tajming ne zavise od smera, pa Blender može da počne odmah, sa neutralnim materijalima.

Pravila za AI klipove (5/10 s, `frames/…_16x9.png`) ovde ne važe, jer AI video nije u igri. Sve 3D je Blender. Tekst, logo, kartice, pozadinske reči i talas su kod.

---

## 0. Pregled (desktop, skrol u vh od vrha stranice)

| # | Od–do | Trajanje (skrol · kadrovi d/m) | Šta se vidi | Kamera | Prelaz | Zvuk | Izvor | Početni kadar → završni kadar |
|---|---|---|---|---|---|---|---|---|
| 1 | 0–200 vh | 200 vh · GRIND G1–G64 (64 / 32) | **GRIND** zakačen. Zrna padaju odozgo u stakleni levak, levak se puni, mlin se okreće 25° ka kameri, počinje mlevenje. | rig K, kadar GRIND, kamera miruje | — | nema | Blender `grind` + HTML (tekst, reč) | G1 (= poster) → G64 (mlaz mlevene kafe teče) |
| 2 | 200–300 vh | 100 vh · GRIND G65–G96 + POUR G65–G96 (32 + 32 / 16 + 16) | **Prelaz.** GRIND scena ide gore sa mlinom, a POUR ulazi odozdo. Mlaz mlevene kafe teče preko granice sekcija pravo u V60. | rig K, dva kadra jedan ispod drugog (razmak tačno 1 S) | **šav na granici sekcija** (vidi 2.) | nema | Blender `grind` i `pour`, isto vreme simulacije | G65 → G96 (otvor zatvoren na G88, rep mlaza pada) |
| 3 | 300–540 vh | 240 vh · POUR G97–G176 (80 / 40) | **POUR** zakačen. Poslednja mlevena kafa pada u filter. Kuvalo se nagne i sipa. Sledi bloom, pa para, kapanje i nivo kafe u bokalu raste. | rig K, kadar POUR, kamera miruje | — | nema | Blender `pour` + HTML | G97 → G176 (kuvalo se vratilo, drawdown) |
| 4 | 540–640 vh | 100 vh · POUR G177–G192 + SIP S1–S16 (16 + 16 / 8 + 8) | **Talas tečne kafe** se diže odozdo, preko POUR-a. Kroz njega se vidi šolja, pa se talas povlači gore. | — | **talas (kod)**, počinje sa linije nivoa kafe u bokalu | nema | kod (canvas/SVG) preko dve Blender sekvence | POUR G177 → SIP S16 |
| 5 | 640–790 vh | 150 vh · SIP S17–S64 (48 / 24) | **SIP** zakačen. Šolja (sletela tokom talasa) se smiri, a dižu se dva pramena pare. Staklene kartice (HTML) uleću i smeštaju se oko šolje. | isti objektiv i svetlo, bliža kamera, kamera miruje | — | nema | Blender `sip` + HTML kartice sa 3 rendera kesa | S17 → S64 (= poster) |
| 6 | od 790 vh | — | Prodavnica „Find your cup" na krem pozadini | — | običan skrol | nema | HTML + renderi kesa | — |

Ukupno **288 kadrova za desktop** (GRIND 96, POUR 128, SIP 64) i **144 za telefon** (svaki drugi kadar, isti render).

**Telefon:** ista struktura i isti procenti. Dužine su u svh: pin GRIND 150, prelaz 100, POUR 180, talas 80, SIP 100.

**Zvuk:** sajt je bez zvuka.

**Preskakanje:** priča traje oko 8 ekrana, pa zaglavlje treba da ima link „Zum Shop". To je isto pravilo kao „uvodni video mora moći da se preskoči".

---

## 1. Zajednička kamera, svet i svetlo (rig K)

GRIND i POUR imaju istu kameru (objektiv, udaljenost, visinu oka u odnosu na kadar), a POUR je tačno jedan kadar niže. SIP ima isti objektiv i svetlo, ali bližu kameru. Kamera se **ni u jednoj sekvenci ne pomera**: „pokret kamere" je sam skrol stranice. Tako je pravilo „jedan glavni pokret po klipu" ispunjeno samo od sebe, a pokreću se samo predmeti.

| Parametar | Vrednost |
|---|---|
| Jedinice | metri, Z gore. Ravan ose je `y = 0` i u njoj leže otvor mlina, osa V60 i bokala. |
| Objektiv | 85 mm, senzor 36 mm, perspektiva (kao `common.camera`, lens 85) |
| Orijentacija | **horizontalna** (nagib 0°, rotacija 90°/0/0), gleda duž +Y. Vertikale ostaju paralelne, kao tilt-shift product shot. Ovo važi za GRIND i POUR jer imaju šav (vidi 2.). Sa nagibom od 10°, kakav je sada u `grind.py`/`pour.py`, razmera na šavu se ne poklapa: vertikalno 0,86 : 1, horizontalno 0,93 : 1 (IZMERENO računom projekcije). Kod horizontalne kamere sa pomakom je 1,000 : 1. |
| Udaljenost | 1,0625 m od ravni `y = 0`. Tada je kadar na toj ravni tačno **45 cm × 45 cm** (tan(FOV/2) = 18/85). |
| 1 S | stranica kvadrata kadra = 45 cm u svetu = 1600 px (desktop master) = 800 px (telefon). 3,56 px/mm na 1600. |
| Visina oka | 0,10 S (4,5 cm) iznad gornje ivice kadra. Kadriranje ide **pomakom objektiva** (shift_y −0,6 za kvadrat), ne naginjanjem. Tada se ivica levka vidi kao tanka elipsa (odnos visine i širine ~0,1), a ivica V60 kao punija (~0,23), kao u videu (~0,13 i ~0,24). |
| Pomak između scena | POUR kamera je **tačno 0,45 m (1 S) niže** od GRIND kamere, sa istim shift-om. Ravan `y = 0` se zato poklapa piksel na piksel na granici sekcija. |
| Udaljenost GRIND = POUR | Broj 1,0625 m je predlog. Bitno je da je **isti** u obe scene. Sada je GRIND 1,228 m (kadar 52 cm), a POUR 1,15 m (kadar 48,7 cm), pa bi mlaz na granici bio ~7 % krupniji iznad nego ispod. |
| SIP | Zasebna scena bez šava: isti objektiv (85 mm) i isto svetlo, ali kamera bliže (kadar ~24 cm, kao u `sip.py`: 0,56 m, 10° odozgo). Nagib je ovde dozvoljen. Promenu razmere sakriva talas. |
| fps i usporenje | GRIND i POUR imaju **isti fps i isto usporenje fizike**, jer mlaz prelazi iz jedne u drugu (skripte sada imaju 30 fps i `--usporenje 0.4`). Cilj: najbrže zrno ili mrvica pređe **≤ ~90 px po kadru na 1600**. Na 30 fps to je usporenje ≈ 0,3, jer 0,4 daje ~120 px. |
| Svetlo | `common.studio_lights` (ključno meko svetlo gore levo, popuna desno, kontra iza). **Rig svetla se pomera zajedno sa kamerom**, da svaki glavni predmet dobije isto svetlo. |
| Svet (odsjaji) | boja sveta = boja pozadine sekcije, jačina ~0,5: GRIND krem, POUR terakota, SIP tamnobraon. Inox i staklo tada „pripadaju" sekciji, kao kuvalo u videu. Boje dolaze iz izabranog smera. |
| Render | Cycles CPU, OIDN, adaptive sampling, `film_transparent` + `film_transparent_glass` (već u `common.render_settings`), PNG RGBA. Motion blur 0,5 kadra za GRIND i POUR. Caustics isključeni. Clamp indirect 1–3, a Filter Glossy 0,5–1. Persistent Data je uključen (`ai-alati.md` B4). Uzorci: predlažem 32 (neprozirno) i 48 (staklo/voda) uz OIDN (Albedo + Normal). Baza znanja polazi od 64 i 128. Odlučuje proba, a razlika u vremenu je u 9. |
| Senka | shadow catcher samo gde predmet stoji: pult u POUR-u (`z = 0`), sto u SIP-u. Mlin u GRIND-u lebdi, kao u videu, i nema podlogu. |
| Sidra za kod | Skripta upisuje u `seq.json` normalizovane koordinate tačaka (`bpy_extras.object_utils.world_to_camera_view`): `otvor`, `ivica_v60` (centar, rx, ry), `pult_y`, `kafa_y` po kadru za G177–G192, `sto_y` za SIP. Kod se ravna po njima, ne po procenama sa oka. |

### Koordinate (realna razmera; ako se svet skalira za fiziku, sve dužine se množe istim brojem)

| Šta | Gde |
|---|---|
| POUR kadar | `z` od −0,0225 do 0,4275; oko na 0,4725 |
| GRIND kadar | `z` od 0,4275 do 0,8775 (+ produžetak nadole do 0,315, vidi 2.); oko na 0,9225 |
| Otvor mlina | (0, 0, 0,500), u kadru GRIND na 0,84 S od vrha |
| Vrh levka | `z` 0,81 (0,15 S od vrha). Dno tela mlina na 0,49. Mlin je visok ~32 cm. |
| Ivica V60 | centar (0, 0, 0,216), u kadru POUR na 0,47 S. Prečnik ~11,5 cm. |
| Baza bokala (pult) | `z` 0 (0,95 S) |
| Kuvalo | ceo predmet u x +0,03…+0,20 i z 0,225…0,375 (0,12–0,45 S od vrha, do 0,94 S po širini). Vrh grlića pri sipanju na ~(+0,015, 0, 0,26). |
| Zrna na pultu | 4 zrna, x +0,07…+0,13, z 0 |
| Pad mlaza | od otvora do ivice V60 je 28,4 cm, do sloja kafe u filteru ~33 cm |
| SIP kadar | zasebna scena (`sip.py`): pod z 0, šolja u pravoj veličini (obod 9,8 cm), osa x = 0, kadar ~24 cm. Šolja stoji malo ispod sredine kadra, da para ima mesta. |

### Raspored na sajtu (isti princip na svakom ekranu)

```
            osa x = 0 (desktop ~58 % širine ekrana, telefon 50 %)
                    │
┌─ GRIND scena ─────┼──────────────────────────┐
│ tekst             │ ┌── GRIND platno ──────┐ │  platno počinje na vrhu scene
│                   │ │ zrna padaju odozgo   │ │
│                   │ │ levak 0,15 S         │ │
│                   │ │ otvor 0,84 S  ●      │ │
└───────────────────┼─┼──── šav 1,00 S ──────┼─┘  ← granica sekcija = donja ivica GRIND kvadrata
┌─ POUR scena ──────┼─┼── POUR platno ───────┼─┐  POUR platno je prislonjeno uz VRH svoje scene
│ (produžetak GRIND │ │ mlaz ulazi odozgo    │ │  (produžetak GRIND platna se seče na ovoj liniji)
│  platna se ovde   │ │ ivica V60 0,47 S ●   │ │
│  ne crta)         │ │ pult 0,95 S          │ │
└───────────────────┴─┴──────────────────────┴─┘
```

- **Desktop:** scena je 100vh, a kvadrat ima stranicu S = 100vh. Predmeti ostaju u x 0,08–0,92 S, jer su leva i desna ivica platna usred ekrana.
- **Telefon:** S = min(100vw, 62svh).
  - GRIND: tekst je gore, a platno je **prislonjeno uz dno** scene. Gornjih 12 % platna ima masku koja bledi, pa se zrna „pojavljuju" umesto da budu odsečena.
  - POUR: platno je **prislonjeno uz vrh** scene (ispod providnog zaglavlja), a tekst je ispod.
  - Kuvalo je zato najviše do 0,12 S od vrha, da ga zaglavlje ne pokrije.
- **Uslov za šav:** između GRIND i POUR scene nema razmaka ni paddinga. Razmak od otvora do V60 je tada uvek 0,63 S, na svakom ekranu.

---

## 2. Prelaz GRIND → POUR: kako se slaže (odluka)

| Opcija | Kako | Za | Protiv |
|---|---|---|---|
| A. Jedna duga sekvenca na fiksnom platnu | Jedno fiksno platno preko obe sekcije. Blender kamera se spušta (pedestal) od mlina do V60, a HTML sekcije klize ispod. | savršen kontinuitet | Pomeranje kamere u Blenderu mora da prati brzinu HTML skrola. Svaki kadar prelaza nosi i mlin i V60 (težak). POUR ne može da se učita posebno. Telefon (tekst između sekcija) ne može da koristi isti raspored. |
| B. Dve sekvence + traka „zrna u padu" na fiksnom platnu | GRIND i POUR su odvojeni, a uska traka sa mlazom (448×1280) je između njih. Mlin i V60 su holdout u traci. | delovi se renderuju i učitavaju odvojeno | Treći sloj i treći Player. Spoj traka/otvor i traka/V60 se vidi iz različitih uglova pa treba „čep" i fade. Na telefonu je razmak otvor–V60 drugačiji, pa treba druga traka. |
| **C. Dve sekvence sa zajedničkim vremenom i šavom na granici (preporuka)** | GRIND i POUR su iz **istog sveta i iste simulacije**, kamere su tačno 1 S jedna ispod druge. Mlaz u GRIND kadru ide od otvora do donje ivice, a u POUR kadru od gornje ivice do filtera. Tokom prelaza oba platna prikazuju **isti kadar simulacije**. | Nema trećeg sloja ni holdout trikova. Otvor i filter pokrivaju predmet tačno, jer je svaki deo mlaza renderovan svojom kamerom. Radi na desktopu i telefonu po istom pravilu. GRIND može da se odobri pre nego što je POUR gotov (fizika je zajednička). | Na šavu postoji mala paralaksa: mrvica 5 mm ispred ili iza ravni `y = 0` skoči vertikalno ~7 px na 1600 (≈ 5 CSS px na ekranu visine 1080), a na ±3 mm ~4 px (IZRAČUNATO). Uz motion blur od ~45 px i granicu boja sekcija to se teško vidi, ali mlaz mora biti tanak po dubini (±3–5 mm). Kod mora imati jedan zajednički sat za oba platna. |

**Preporuka: C.** B ostaje kao rezerva samo ako proba šava pokaže skok. Tada se preko šava (±8 % S) stavlja uska zakrpa iz srednje kamere.

### Šta C traži od Blendera
- Zajednički modul (npr. `scripts/blender/kafa/svet.py`) drži kameru, svetlo, fps, usporenje, emiter mlevene kafe (položaj, seed, brzina, vreme) i položaj V60 u istom koordinatnom sistemu. `grind.py` i `pour.py` ga uvoze.
  - Mlaz u oba renderovanja tada ima **iste čestice u istom trenutku**.
  - POUR kadar 1 je globalni G65, pa je vreme emitera u POUR-u pomereno za 64 kadra.
  - Moguće je i da jedna skripta ima argument `--kamera grind|pour`.
- **GRIND kadrovi su 1600×2000** (S × 1,25 S): gornji kvadrat je scena, a donjih 0,25 S je **produžetak** u kome se vidi samo mlaz.
  - Produžetak služi telefonu: na iOS-u, kad se traka sa adresom skupi, ispod zakačene scene od 100svh ostaje traka od oko 80–100 px (NIJE POTVRĐENO na iOS 26) i mlaz u njoj ne sme da bude odsečen.
  - Na desktopu je produžetak tokom pina ispod ekrana, pa se ne vidi.
  - Vrh kadra mora ostati isti kao kod kvadrata: shift se preračunava (~−0,58 za 1600×2000). Proveriti projekcijom tačke otvora.
- Mlaz je tanak po dubini, ±3–5 mm oko `y = 0`.

### Šta C traži od koda
- **Jedan sat `t` (globalni kadar G)** se izračunava iz skrola i ublažava **jednom**. Oba Player-a crtaju `G − g_od` svoje sekvence. `premium.js` sada ublažava svaki Player posebno, pa bi se tokom prelaza razišli.
- Ako kadar još nije učitan, oba platna uzimaju **isti najbliži G koji je učitan u obe sekvence**, ne svako svoj.
- GRIND platno (S × 1,25 S) se seče (`clip-path`) na gornjoj ivici POUR scene. Tako se produžetak nikad ne crta preko POUR platna.
- Kadrovi prelaza (G65–G96 iz obe sekvence) učitavaju se **celi** pre nego što GRIND dođe do 60 %.

---

## 3. Sekvenca GRIND

- **Šta je:** mlin od inoksa sa staklenim levkom. Zrna padaju odozgo, levak se puni, mlin se okreće ka kameri, a mlevena kafa izlazi iz otvora.
- **Kadrovi:** desktop 96 (G1–G96), telefon 48 (neparni G, isti render, smanjen).
- **Rezolucija:** pun kadar 1600×2000 (providna pozadina), isečak x 0,22–0,78 S (896×2000) kao PNG RGBA master. Desktop WebP se pravi na 1600 i 1200 skali, telefon na 800 (448×1000).
- **Skrol:** 0–300 vh. Pin traje 0–66,7 %, a prelaz 66,7–100 %.

| % skrola | Kadar G (d / m) | Šta se vidi | Šta je animirano |
|---|---|---|---|
| 0 % | G1 (1 / 1) | **= poster.** Mlin je okrenut −25° (vidi se dugme za mlevenje i profil), levak je pun ~45 %. Mlaz od 15–20 celih zrna pada odozgo, iz gornje ivice kadra, u levak. Iz otvora ne izlazi ništa. | — |
| 0–42 % | G1–G40 (1–40 / 1–20) | Zrna i dalje padaju i odskaču u levku, a gomila raste sa 45 na 80 %. **Mlin se okreće −25° → 0°** (ease in-out, oko ose kroz otvor), pa odsjaj klizi preko inoksa. Ako direktor više voli miran pogled 3/4 (sadašnji `--rot -25`), mlin stoji, a glavni pokret su samo zrna. Na kraju otvor gleda pravo u kameru, na x = 0. | rigid body zrna u padu i gornji sloj gomile; rotacija mlina (keyframes) |
| 42–50 % | G40–G48 | Dotok se proređuje: pada još ~10 zrna. Gomila se smiruje na 85 %. | rigid body |
| 50–58 % | G48–G56 | Počinje mlevenje. Gomila se u sredini lagano uvlači (levak), a na G52 iz otvora krene prva mlevena kafa. | spuštanje gomile (animacija), čestice |
| 58–67 % | G56–G64 (kraj pina) | Ujednačen mlaz mlevene kafe, 6–10 mm širok, ide od otvora ka dnu kadra i u produžetak. | čestice |
| 67–92 % | G65–G88 (prelaz) | Stranica ide gore, a mlin sa njom. Mlaz neprekinuto teče preko šava u POUR. Gomila se spušta sa 85 na 72 %. | čestice, gomila |
| 92–100 % | G88–G96 | Na G88 otvor prestaje. Rep mlaza se odvaja i pada: na G96 je ~6 cm ispod otvora, tik iznad šava, na samom vrhu ekrana. | čestice |

**Početni → završni kadar:** G1 (mlin −25°, levak 45 %, zrna u vazduhu) → G96 (mlin 0°, levak 72 %, rep mlaza tik iznad šava). G65–G96 su isti trenuci simulacije kao POUR 1–32.

**Šta je animirano i kako:**
- **Usporenje:** u realnom vremenu zrno na ulazu u levak pređe ~7–8 cm (≈ 270 px na 1600) po kadru, pa bi treperilo. Usporeno na ≤ ~90 px po kadru (na 30 fps, usporenje ≈ 0,3) i sa motion blurom od 0,5 kadra, zrno ostaje prepoznatljivo. Isto usporenje važi u POUR-u.
- **Okret mlina** ide oko vertikalne ose **kroz otvor**, kao u `grind.py`. Otvor tako ostaje na x = 0 pod svakim uglom, a mlaz sme da teče i tokom okreta.
- **Fizika zrna:**
  - rigid body (Bullet), samo za zrna u padu i gornji sloj gomile, ~250–400 tela;
  - telo gomile je statičan sloj instanci koji se podiže i spušta animacijom (lažiran nivo); 1000+ tela bi bilo sporo i nestabilno;
  - Blender priručnik (5.2) kaže da su mala tela nestabilna i da bi trebalo da imaju bar ~20 cm prečnika. Zato se fizika radi u **uvećanom svetu** (10–20×, `ai-alati.md` B5) sa proksi-zrnima (Convex Hull), pa se ispeče (Bake To Keyframes) i zameni detaljnim zrnom. Napomena: uvećanje od 16× uz pravu gravitaciju samo po sebi usporava za √16 = 4×, pa to treba uračunati u usporenje;
  - sudarač levka nije tanak mesh (Solidify ili debela ljuska), a substeps i solver iterations su povišeni.
- **Zrno:** proceduralni elipsoid 10 × 7,5 × 5,5 mm sa brazdom, u 4 varijante (±10 % veličine), materijal `common.mat_bean`, nijansa prženja iz smera.
- **Mlevena kafa:** čestice (bez sudara do filtera), nepravilne mrvice od 0,4–1,2 mm i grudvice od 2–3 mm. Boja je malo svetlija od zrna, hrapavost ~0,9. Na 1600 je to 2–10 px, a sa blurom izgleda kao mlaz peska.
- **Mlin:** lathe/screw profil, bez tuđeg brenda i logoa.
  - telo: valjak od brušenog inoksa (`mat_steel`, anizotropija) ~13 cm × 18 cm;
  - levak: stakleni (`mat_glass`) ~12 cm, blago konusan, sa tamnim gumenim prstenom na vrhu;
  - veliko dugme za finoću mlevenja napred levo, sa ugraviranim podeocima;
  - crni otvor od plastike napred dole, na x = 0.

**Procena rendera (PROCENA):**
- Formula: t ≈ 2 s + 11 s × (pikseli / 409 600) × (uzorci / 32) × k. Osnova je probni kadar od 13 s (640×640, 32 uzorka) koji je javio direktor.
- GRIND, 32 uzorka, k ≈ 1,3 (staklo sa zrnima iza njega). Produžetak je skoro prazan, pa je efektivno ×6,6 piksela.
- Vreme: **~96 s po kadru × 96 = ~2,6 h**. Bake fizike ~15–20 min.

---

## 4. Sekvenca POUR

- **Šta je:** gooseneck kuvalo gore desno sipa tanak mlaz u V60 sa papirnim filterom na staklenom bokalu. Ima pare, kapanja i nivoa kafe koji raste, a na pultu leže 4 zrna.
- **Kadrovi:** desktop 128 (G65–G192, lokalno 1–128), telefon 64 (neparni G).
- **Rezolucija:** pun kadar 1600×1600, isečak x 0,26–0,98 S (1152×1600) kao PNG RGBA master. Gornja ivica ostaje cela, zbog šava. Desktop WebP na 1600 i 1200 skali, telefon na 800.
- **Skrol:** 200–640 vh. Prelaz je 0–22,7 %, pin 22,7–77,3 %, a talas 77,3–100 %.

| % skrola | Kadar G (d / m) | Šta se vidi | Šta je animirano |
|---|---|---|---|
| 0 % | G65 (1 / 1) | Scena ulazi odozdo, pa se vidi samo vrh. V60 sa belim naboranim papirom (viri ~1,5 cm iznad ivice) stoji na staklenom bokalu. Kuvalo je gore desno, spremno (nagnuto 12°, bez vode). Bokal je prazan, a na pultu desno leže 4 zrna. Mlaz mlevene kafe ulazi odozgo u filter. | čestice |
| 0–23 % | G65–G96 (1–32 / 1–16) | **Prelaz.** U filteru raste kupa mlevene kafe, do ~2 cm. Mlaz je neprekinut sa GRIND kadrom iznad šava. | čestice gase se na sloju; kupa raste (scale/shape key po broju palih čestica) |
| 23–32 % | G97–G110 (33–46) | Pin počinje. Rep mlaza pada sa vrha ekrana (mlin je otišao, kao u videu), poslednje mrvice padnu na G110, a kupa se blago slegne. | čestice |
| 32–39 % | G110–G120 (46–56) | **Kuvalo se naginje 12° → 32°** (glavni pokret POUR-a). Iz grlića izlazi voda, a tanak mlaz (3–4 mm) u luku na G116 udara u sredinu kupe. | keyframes kuvala; mlaz je animirana kriva sa bevel-om |
| 39–49 % | G120–G136 (56–72) | **Bloom:** kafa tamni od sredine ka ivici, nadima se ~4 mm i pravi sitne mehuriće. Od G124 se dižu prvi pramenovi pare, a na G132 sa vrha V60 kapnu prve kapi. | maska vlage (šejder), displace, instance mehurića, para, kapi |
| 49–69 % | G136–G164 (72–100) | Ujednačeno sipanje (blago treperenje mlaza, opciono mali krug od 1,5 cm). Nivo u filteru raste do ~70 % kupe, sa svetlobraon penom na površini. Para je stalna i ide gore levo. Kapanje prelazi u tanak mlaz, a nivo u bokalu raste sa 0 na 30 %. | nivo tečnosti (ravan sa meniskusom, unutrašnjost bokala ispod nivoa), mlaz iz V60, para |
| 69–77 % | G164–G176 (100–112, kraj pina) | **Kuvalo se vraća 32° → 12°**, mlaz se tanji i na G170 prekida (rep pada). Počinje drawdown: nivo u filteru se spušta. | keyframes, mlaz, nivo |
| 77–100 % | G177–G192 (113–128) | Talas (kod) se diže odozdo. Drawdown se nastavlja, kapanje prelazi u retke kapi, a bokal je pun 30 → 38 %. Para se zadržava. `kafa_y` po kadru ide u `seq.json`, jer talas kreće sa te linije. | nivo, kapi, para |

**Početni → završni kadar:** G65 (prazan filter, mlaz ulazi odozgo, kuvalo spremno) → G192 (drawdown, bokal 38 %, para, retke kapi).

**Šta je animirano i kako:**
- **Mlaz vode:** nije fluid simulacija, nego kriva (parabola od grlića do površine) sa bevel-om od 1,5–2 mm, šumom po poluprečniku i položaju i materijalom vode (`mat_water`). Sa `film_transparent_glass` se vide samo odsjaj i blago izobličenje, pa po potrebi dodati blag sjaj da se mlaz vidi na terakoti.
- **Kafa u filteru i bokalu:** animirane površine (ravan sa meniskusom i penom), ne Mantaflow (`blender-umetnik.md`: prvo jeftin trik).
- **Para:** prvo 3–4 providne ravni okrenute ka kameri, sa animiranim šumom (jeftino). Volumen (Principled Volume sa 3D šumom) samo ako ravni izgledaju plosnato, jer na CPU-u utrostručava vreme.
- **Kapanje iz V60:** instance kapi na putanji, pa tanak cilindar sa šumom.
- **Kuvalo:** gooseneck od ~0,6 l, brušeni inox ili mat tamni čelik (iz smera), sa S-grlićem, ručkom desno i poklopcem sa dugmetom. Ceo mora biti u kadru (≥ 5 % od ivice). Ruka se ne modeluje.
- **V60:** providan sa spiralnim rebrima (kao u videu). Ako dva sloja stakla (V60 + bokal) daju šum, prelazi se na beli keramički (brže i čistije). Odluka posle probe.
- **Bokal:** staklo, ~600 ml, ručka desno, kljun levo.
- **Zrna na pultu:** 4 statična zrna sa kontaktnom senkom.
- Pult je **HTML traka**. Blender daje samo senku (shadow catcher na `z = 0`), a `pult_y` ide u `seq.json`.

**Procena rendera (PROCENA):**
- Sa ravnima za paru (48 uzoraka zbog stakla i vode, k ≈ 1,5): **~157 s po kadru × 128 = ~5,6 h**.
- Sa volumenom za paru (k ≈ 2,4): **~250 s × 128 = ~8,9 h**.
- Kadrovi G65–G96 se renderuju i ovde i u GRIND-u, jer su to dve kamere. To je uračunato.

---

## 5. Prelaz POUR → SIP: talas tečne kafe

**Preporuka: kod (canvas 2D ili SVG maska), ne Blender sekvenca.**

| | Blender sekvenca | Kod |
|---|---|---|
| Veličina | Talas pokriva ceo ekran, pa treba render od ~2560×1440. Alfa je delimična svuda (gradijent, sjaj), a to WebP slabo pakuje: ~250–400 KB po kadru × 32 = **8–13 MB**. Telefonu treba poseban uspravni render (~3–4 MB). (PROCENA) | ~5–8 KB JS/CSS. Opciono jedna Blender tekstura sjaja od 2048×256 (~40 KB). |
| Oštrina | Raster se razvlači na 4K i ultrawide ekranima, a na 4:3 i 9:19,5 se seče ili deformiše. | Vektorska ivica i odsjaj su oštri na svakom DPR-u i svakoj razmeri ekrana. |
| Sadržaj iza | Blender ne vidi HTML. Kroz talas bi se videla samo boja, ne prava šolja i naslov SIP. | Kroz talas se vidi **živ** SIP sloj (šolja + HTML), zatamnjen i blago uvećan, kao sočivo u videu. |
| Vreme rendera | ~300 s po kadru (providna sjajna tečnost na 3,7 MPix) × 32 = **~2,7 h**, plus telefon ~40 min (PROCENA) | 0 |
| Boje | Nova boja brenda traži novi render. | CSS promenljive (Crema / Honig / Kirsche iz smera) |
| Rizik | — | Može da izgleda „ravno". Ublažava se slojevima ispod. |

**Kako izgleda (za `animator`-a), po procentu talasa (100 vh na desktopu):**
- **0 %:** tanka tamna linija se pojavi tačno na `kafa_y` (nivo kafe u bokalu, iz `seq.json`). Kafa iz bokala se „prelije" u ekran.
- **0–30 %:** gornja ivica talasa se diže preko bokala.
  - Ivica je zbir dve sinusoide: A1 ≈ 4 % vh, λ1 ≈ 1,2 vw; A2 ≈ 1,5 % vh, λ2 ≈ 0,45 vw.
  - Faza klizi bočno.
  - Iznad ivice je POUR, ispod nje SIP.
- **30–70 %:** traka tečnosti debljine 18–35 % vh, sa talasastom gornjom i donjom ivicom, prolazi sredinom ekrana.
  - Unutra se vidi SIP sloj sa `scale(1.04)` oko centra trake i ćilibarnim tonom (sepia/saturate).
  - Na desktopu opciono `feDisplacementMap` (scale ~12).
  - Ispod trake je čist SIP.
- **70–100 %:** traka izlazi na vrh ekrana i ostaje SIP. POUR scena se otkači i ide gore sporije od talasa (u videu V60 ode sa 0,45 na 0,2 vh).
- **Ivica talasa:**
  - tamni meniskus od 1,5 px;
  - ispod njega svetao odsjaj od 2 px (bela 50 %, blur 2 px, pomeren 3 px);
  - 3–5 sitnih odsjaja koji klize duž ivice.
- **Ispuna:** vertikalni gradijent od svetle ćilibarne do tamne kafe, providnost ~0,88.
- **Telefon:** bez displacement-a i backdrop-filter-a, samo gradijent i odsjaj.
- **Reduced motion:** nema talasa. Ostaje rez sa statičnom dekorativnom trakom boje talasa.
- **Tehnika:** SIP scena je zakačena ispod POUR scene tokom talasa (obe u istom kontejneru), a POUR se seče `clip-path`-om po ivici talasa.

---

## 6. Sekvenca SIP

- **Šta je:** keramička šolja sa curećom glazurom (tamno telo, krem glazura gore). Šolja se spusti na sto uz blag okret i smiri se, a dižu se dva pramena pare. Kartice proizvoda su HTML.
- **Kadrovi:** desktop 64 (S1–S64), telefon 32 (neparni S).
- **Rezolucija:** pun kadar 1600×1600, isečak oko šolje i pare po probi, PNG RGBA master. Desktop WebP na 1600 i 1200 skali, telefon na 800.
- **Skrol:** 540–790 vh. Talas je 0–40 %, a pin 40–100 %.

| % skrola | Kadar S (d / m) | Šta se vidi | Šta je animirano |
|---|---|---|---|
| 0 % | S1 | Šolja lebdi ~4,5 cm iznad stola (`sip.py --drop 0.045`), a ručka je zaokrenuta ~28° unazad od konačnog ugla. U šolji je kafa sa tankim prstenom kreme. Senka na stolu je meka i bleda. Nema pare. Vidi se kroz talas. | — |
| 0–35 % | S1–S14 (1–14 / 1–7) | **Ulazak:** šolja se spušta i okreće (ease-out), a senka se skuplja i tamni. Odsjaj klizi preko glazure. Šolja sleti na S14, dok talas prolazi gornjom trećinom ekrana. To je i potpisni trenutak smera 1 („šolja sleti kad se talas povuče"). | spuštanje i okret (keyframes) |
| 35–57 % | S14–S30 | Malo smirivanje bez odskoka. Ručka je desno, ~8° ka kameri (`HANDLE_ANGLE = -8`), pa se vidi otvor ručke. Od S20 se dižu dva tanka pramena pare. HTML kartice uleću (kod, 45–80 %). | poslednji stepeni okreta, para |
| 57–100 % | S30–S64 | Šolja miruje, para se diže. Kartice su na mestu, zvezdica treperi (SVG). Poslednji kadar je **poster**. | para |

**Početni → završni kadar:** S1 (šolja u vazduhu, ručka iza, kroz talas) → S64 (šolja na stolu, ručka desno, para, = poster).

**Šolja (proceduralno):**
- **Oblik:**
  - u pravoj veličini, ~9,8 cm visine (obod u `sip.py`) i ~8,5 cm prečnika;
  - blago trbušast valjak, najširi na ~30 % visine;
  - zaobljena ivica, zid od 5 mm;
  - nogica blago uvučena, bez glazure;
  - ručka u obliku „uha" desno, spojena na 25 % i 80 % visine.
- **Telo:** tamna kamenina (podrazumevano ~`#3B2A22`), mat (hrapavost ~0,7), sa sitnim pegama (svetle i tamne tačke) i blagim prstenovima sa vitla (bump).
- **Glazura:**
  - krem/ovas (podrazumevano ~`#D8CCB4`), sjajna (hrapavost ~0,2, coat);
  - pokriva gornjih 35–40 % spolja i celu unutrašnjost;
  - 8–12 nejednakih curenja do 45–60 % visine, sa zaobljenim i zadebljanim krajevima (displace);
  - na ivici se glazura tanji i otkriva braon glinu (smeđa linija na obodu, kao u videu);
  - na prelazu ka telu je smeđi oreol, a po površini sitne rupice i mrlje (šum).
- **Kafa u šolji:** tamna, sjajna, 1 cm ispod oboda, sa prstenom kreme.
- **Para:** dve providne ravni sa šumom. Ako izgleda lažno, izbacuje se, jer šolja i bez nje stoji.
- **Varijante po smeru:** smer 1 krem glazura (podrazumevano); smer 2 seladon `#8FA394`; smer 3 crvena glazura `#A3122A` na belom telu. Menja se samo materijal.
- **Sto:** HTML traka, a Blender daje kontaktnu senku (shadow catcher). `sto_y` ide u `seq.json`.

**Procena rendera (PROCENA):** 32 uzorka, k ≈ 1,1 (šolja zauzima veći deo kadra nego predmeti u GRIND-u i POUR-u): **~78 s po kadru × 64 = ~1,4 h**.

### Tri statična rendera kesa za kartice (Origin / Flavor / Roast)

Kartice su HTML (staklo je `backdrop-filter`, a rotacija je CSS 3D). Unutra je ravna slika kese, koja se okreće zajedno sa karticom. Isti renderi služe i prodavnici.

- **Model (jedan za sve tri):**
  - kesa od 250 g sa ravnim dnom, ~13 × 20 × 7,5 cm. `bags.py` pravi stojeću kesu (doypack) sa zipperom, i to je u redu. Box pouch sa bočnim naborima je alternativa ako dizajn traži „kutijast" oblik;
  - vrh zavaren sa nazubljenim šavom (ili zipper);
  - okrugli ventil od 16 mm gore na sredini prednje strane;
  - mat papir (kraft ili premazan), sa sitnim gužvanjem (šum, displace).
- **Etiketa:** tekstura sa prednje strane, PNG 2048×3072 iz SVG-a koji daje `dizajner` (`studio/kafa-skrol/dizajn/`). **Nikad AI tekst.** Do izbora smera stoji etiketa „&lt;brend&gt;" sa poljima.
- **Kamera i svetlo:** isti objektiv (85 mm) i isti rig svetla kao sekvence, providna pozadina, kontaktna senka (shadow catcher).
- **View transform:** Khronos PBR Neutral, da boje etikete ostanu verne (`ai-alati.md` B4). Sekvence ostaju na AgX-u. Na kartici je to razlika koja se ne vidi, a etiketa je tačna.

| Render | Ugao | Boja kese (podrazumevano iz videa, posle iz smera) | Šta etiketa ističe |
|---|---|---|---|
| `kesa_origin` | 3/4 sleva (yaw −25°), uspravno | terakota/glina | zemlja, region, visina, farma |
| `kesa_flavor` | spreda (yaw 0°), nagnuta 3° unazad | tirkiz/žalfija | note ukusa (čipovi) |
| `kesa_roast` | 3/4 zdesna (yaw +25°), nagnuta 8° | roze/krem | skala prženja (traka) |

- **Master:** 1200×1500 (4:5), 256 uzoraka.
- **Za web:**
  - kartica 600×750 (~45 KB);
  - telefon 400×500 (~22 KB);
  - prodavnica 900×1125 (~80 KB).
- **Procena:** ~6,5 min po kesi, **~20 min za sve tri**.

---

## 7. Posteri (telefon, reduced motion, prvi ekran)

| Poster | Kadar | Šta | Render |
|---|---|---|---|
| `grind/poster` | **G1** | zrna u vazduhu, levak 45 %, mlin −25°. Isti fajl je i kadar 0001, pa nema skoka kad platno zameni sliku. | 1600×2000, 256 uzoraka, ~13 min |
| `pour/poster` | G150 (sredina sipanja) | mlaz, bloom i pena, para, kapanje, bokal ~20 %, zrna na pultu | 1600², 256 uzoraka, ~14 min |
| `sip/poster` | **S64** | šolja u konačnom uglu sa parom. Isti fajl je i poslednji kadar. | 1600², 256 uzoraka, ~10 min |

Talas nema poster (u reduced motion je to rez).

- **Reduced motion:** nema pina ni sekvenci, svako poglavlje dobija svoj poster kao `<img>`, a kartice su statična mreža.
- **`Save-Data`:** samo posteri.
- **Prvi ekran:**
  - Platno se ne računa kao LCP element (web.dev), pa je prvi ekran `<img fetchpriority="high">` sa GRIND posterom;
  - platno ga zamenjuje kad se učita prvi deo kadrova.

---

## 8. Budžet fajlova (WebP) i učitavanje

**Osnova:**
- IZMERENO: sekvence u `freiraum-premium` (720 px, RGBA, ~36 % pokrivenosti) imaju prosečno 40 KB po kadru.
- IZMERENO: isti kadrovi uvećani na 1600 i spakovani sa q70 imaju 91–165 KB, na 1200 64–115 KB, a na 800 (q66) 36–68 KB.
- Pravi Blender kadrovi su oštriji od uvećanih, ali su posle OIDN-a čisti od šuma. Brojevi ispod su ciljevi. `mediji` ih proverava na prvih 10 pravih kadrova.
- Baza znanja (`ai-alati.md` B7) preporučuje do 60 KB po kadru na desktopu i do 40 KB na telefonu, a to je izvedeno iz setova od 720–1280 px.
  - Telefon ovde to ispunjava.
  - Desktop na 1600 px sa inoksom i staklom ne može. Zato je **1200 podrazumevani desktop nivo** (~70–80 KB po kadru), a 1600 se šalje samo kad je S × min(DPR, 2) > 1250 (Retina, 1440p i veći ekrani).
- **Isečak oko predmeta** (`ai-alati.md` B7, kao Vibe): kadar se renderuje (border + crop) i pakuje samo u okviru koji pokriva predmet u svim kadrovima, plus 4 % margine. `seq.json` nosi pomak (`x0`, `y0`), pa platno crta isečak na pravom mestu u kvadratu.
  - Predlog okvira: GRIND x 0,22–0,78 S × ceo 1,25 S (896×2000); POUR x 0,26–0,98 S × ceo S (1152×1600); SIP po probi.
  - **Gornja ivica POUR-a i donja ivica GRIND-a se ne seku**, zbog šava.
  - Prazni pikseli i u Cycles-u i u WebP-u koštaju malo, pa isečak najviše štedi **memoriju dekodiranih kadrova** (GRIND 7,2 MB umesto 12,8 MB po kadru) i nešto vremena rendera. Bajtovi padnu tek ~10 % (PROCENA).

| | Kadrovi d / m | Cilj po kadru 1600 / 800 | Desktop 1600 (veliki ekrani) | **Desktop 1200 (podrazumevano)** | Telefon 800 |
|---|---|---|---|---|---|
| GRIND (1600×2000 / 800×1000) | 96 / 48 | ≤ 105 / ≤ 40 KB | 10,1 MB | ~7,1 MB | 1,9 MB |
| POUR | 128 / 64 | ≤ 115 / ≤ 42 KB | 14,7 MB | ~10,3 MB | 2,7 MB |
| SIP | 64 / 32 | ≤ 80 / ≤ 28 KB | 5,1 MB | ~3,6 MB | 0,9 MB |
| Posteri (POUR, SIP; GRIND poster je kadar 1) | 2 | ~170 / 60 KB | 0,35 MB | 0,25 MB | 0,12 MB |
| Kese (kartica + prodavnica) | 3 × 2 | — | 0,38 MB | 0,38 MB | 0,19 MB |
| **Ukupno ako se pregleda sve** | 288 / 144 | | **≈ 30 MB** | **≈ 21 MB** | **≈ 5,8 MB** |

**Podešavanja za `mediji`:**
- Polazna vrednost je q 62–70, `alpha_quality` 90, method 6, Lanczos za smanjivanje. Telefon se pravi iz 1600 mastera (svaki drugi kadar), bez novog rendera.
- Ako cilj nije ispunjen: prvo q do 60, pa tek onda manje kadrova (svaki četvrti iz POUR pina ispada).
- Proveriti oreole na pari i staklu (alfa ivice na tamnoj pozadini).

**Prvi ekran:**
- Desktop: HTML, CSS, JS i fontovi (~150 KB) + GRIND kadar 1 / poster (q 80: ~95 KB na 1200, ~140 KB na 1600) = **~250–300 KB do LCP-a**.
- Telefon: ~150 KB + ~50 KB.
- Cilj je LCP ≤ 2,5 s (web.dev „good").

**Delovi (posle `load` događaja, 6 zahteva paralelno, kao `premium.js` `loadSeq`):**
1. GRIND: svaki 6. kadar (16 kadrova, ~1,7 MB desktop / 8 kadrova, ~0,3 MB telefon), pa svaki 2., pa ostali.
2. Kad GRIND pređe 30 %: **POUR 1–32 celi** (kadrovi prelaza, potrebni za šav), pa POUR svaki 6.
3. Ulazak u POUR pin: ostatak POUR-a, pa SIP svaki 6.
4. Kad POUR pređe 60 %: ostatak SIP-a i slike kesa (`loading="lazy"` za prodavnicu).

---

## 9. Ukupno vreme rendera (PROCENA, 4 jezgra)

| Posao | Vreme |
|---|---|
| Probe: 3 kadra po sceni, 640² sa 32 uzorka + 1 pun kadar za merenje + kompozit šava | ~40 min (+ ponavljanja) |
| Bake fizike (zrna + čestice) | ~20–30 min |
| GRIND 96 × ~96 s | ~2,6 h |
| POUR 128 × ~157 s (para od ravni) / × ~250 s (volumen) | ~5,6 h / ~8,9 h |
| SIP 64 × ~78 s | ~1,4 h |
| Posteri 3 × 256 uzoraka | ~35–40 min |
| Kese 3 × 256 uzoraka | ~20 min |
| **Ukupno (32/48 uzoraka + OIDN, moj predlog)** | **≈ 11,5 h** (para od ravni) / **≈ 15 h** (volumen) |
| Za poređenje: uzorci iz baze znanja (64 neprozirno, 128 staklo/voda) | GRIND ~5,1 h + POUR ~14,7 h + SIP ~2,7 h + ostalo ~2 h ≈ **24,5 h** |

- Renderuje se jedan po jedan kadar, jer Cycles već koristi sva 4 jezgra.
- Duge rendere treba pustiti preko noći, u pozadini, tek posle odobrenih proba.
- Ako treba brže: GRIND i SIP na 24 uzorka (−25 %) ili master na 1200 umesto 1600 (≈ −45 %). Druga opcija gubi oštrinu na Retina ekranima.
- Formula računa sve piksele kadra. Prazni pikseli (providna pozadina) su u Cycles-u jeftini, pa je stvarno vreme verovatno niže, naročito sa isečkom (border render). Prvi pun kadar po sceni daje pravi broj.

---

## 10. Kadrovi koje treba napraviti

Probe ostaju u privremenom folderu `blender-umetnik`-a, a ne u repou.

| Kadar | Zašto |
|---|---|
| `grind` G1, G40, G84 (640², 32 uzorka) | početak / mlin na 0° / mlaz u prelazu |
| `pour` G84, G150, G192 | mlaz ulazi u filter / sredina sipanja / drawdown |
| `sip` S1, S32, S64 | početni ugao / smirivanje / poster |
| **Kompozit šava**: GRIND G84 (1600×2000) iznad POUR G84 (1600²), pomeren tačno 1600 px | provera paralakse i kontinuiteta mlaza, pregleda ga `recenzent` |
| 1 pun kadar po sceni (1600) | merenje vremena; preračunati tabelu iz 9. |
| `kesa_origin` sa privremenom etiketom (600×750) | provera papira i ventila pre prave etikete |

Gotovo ide preko `mediji`-ja, posle odobrenja direktora. Folder sajta još nije izabran:

```
<sajt>/assets/seq/grind/{d,m}/0001.webp …   seq.json   (poster = d/0001.webp i m/0001.webp)
<sajt>/assets/seq/pour/{d,m}/0001.webp …    poster.webp  seq.json
<sajt>/assets/seq/sip/{d,m}/0001.webp …     poster.webp  seq.json
<sajt>/assets/img/kesa-{origin,flavor,roast}-{600,400,900}.webp
(opciono) <sajt>/assets/img/talas-sjaj.webp   2048×256
```

`seq.json` (proširenje formata iz `freiraum-premium`):
- polja `count`, `w`, `h`, `fps` (isti kao u Blenderu, sada 30);
- `g_od` / `g_do` (globalni kadrovi simulacije);
- `koraci` (prelaz / pin / talas);
- sidra iz 1. (`otvor`, `ivica_v60`, `pult_y`, `kafa_y[]`, `sto_y`, `osa_x` = 0,5);
- pomak isečka `x0`, `y0` i puna veličina kadra `W`, `H` (sidra su u koordinatama punog kadra).

---

## 11. Rizici

1. **Šav na granici GRIND/POUR.**
   - Paralaksa zrna van ravni `y = 0`.
   - Dva Player-a sa posebnim ublažavanjem se razilaze.
   - Različiti „najbliži učitani" kadrovi.
   - Rešenje: tanak mlaz (±3–5 mm), jedan sat, zajednički fallback kadar, prelaz se učitava unapred i kompozit se proverava. Rezerva je zakrpa preko šava (opcija B).
2. **Bullet i sitna tela.** Priručnik 5.2 kaže da su mala tela nestabilna (idealno ≥ 20 cm) i da mesh oblici nemaju debljinu. Rešenje: uvećan svet (10–20×) sa proksi-zrnima, debeo sudarač levka, viši substeps, gomila lažirana instancama. Nazive API opcija proveriti u 5.2.
3. **Mlin se okreće dok su zrna u levku.** Kinematički levak gura tela. Ako proba pravi probleme, rotacija se završava pre nego što gornji sloj padne, ili mlin stoji na 0°.
4. **Pomeraj po kadru.** Pri realnoj brzini zrna trepere. Zato je fizika usporena (≈ 0,3 na 30 fps), a motion blur je 0,5 kadra. Proveriti da zrno ne pređe više od ~90 px po kadru na 1600.
5. **Staklo i para na CPU-u.**
   - Dva sloja stakla (V60 + bokal) i voda daju šum i svetle tačke. Rešenje: 48 uzoraka, clamp, a po potrebi keramički V60.
   - Para kao volumen utrostručava vreme.
   - Alfa ivice pare u WebP-u mogu dati oreol na tamnoj pozadini.
6. **Memorija dekodiranih kadrova.** Kadar 1600×1600 RGBA zauzima ~10 MB u memoriji (GRIND 1600×2000 ~13 MB), pa 288 kadrova može da zauzme do ~3,2 GB ako ih pregledač sve drži. Na telefonu je to 144 × ~2,6–3,2 MB ≈ 0,4 GB. Predlog: dekodiran samo prozor od ±24 kadra oko trenutnog (`createImageBitmap` / `close()`). `tester` proverava na iPhone Safari-ju.
7. **Budžet.** 30 MB na desktopu je gornja granica. Ako probe daju više, ide se redom iz 8.: prvo q, pa broj kadrova. Podrazumevani nivo 1200 daje ≈ 21 MB.
8. **Raspored.**
   - Šav traži da GRIND i POUR scene budu jedna uz drugu (bez razmaka), GRIND platno od vrha scene, a POUR platno uz vrh svoje scene.
   - Tekst ne sme preko ose mlaza.
   - Na telefonu zaglavlje ne sme da pokrije kuvalo, zato je kuvalo najviše do 0,12 S od vrha.
   - Traka sa adresom na iOS-u se rešava produžetkom GRIND kadra (NIJE POTVRĐENO na iOS 26).
9. **Oštrina na telefonu.** 800 px na 100vw (390 CSS px) pri DPR 3 znači uvećanje ~1,46×. Ako `tester` nađe da je mutno, `mediji` pravi 960 px iz istih mastera (+~40 % bajtova), bez novog rendera.
10. **Smer brenda nije izabran.** Boje sveta (odsjaji), glazura, kese i talas čekaju izbor. Geometrija, fizika i tajming ne čekaju. Etikete kesa čekaju `dizajner`-a.
11. **Vreme.** Ukupno je ~11,5–15 h rendera na 4 jezgra (~24 h sa uzorcima iz baze znanja). Svaka izmena posle punog rendera košta sate, pa se probe odobravaju pre punog rendera.
12. **Kafa u staklu postaje providna.**
    - Sa `film_transparent_glass` zrak koji prođe kroz staklo **i kroz kafu** (`mat_coffee_liquid` ima Transmission 0,85) i ne udari ni u šta postaje providan. Kafa u bokalu bi tada dobila boju sajta umesto tamne boje (upozorenje i u `ai-alati.md` B4).
    - Rešenje: kafa bez transmisije ili sa volumenskom apsorpcijom. Proveriti na probi POUR G150.
13. **Treperenje između kadrova.**
    - OIDN nije vremenski stabilan (`ai-alati.md` B4, OIDN README), a skrol pokazuje kadrove napred i nazad.
    - Proveriti 10 uzastopnih kadrova sa i bez animated seed-a, posebno staklo levka sa zrnima i paru.
14. **Postojeće skripte su po drugom dogovoru** (vidi 13.): nagnuta kamera, različite udaljenosti, odvojene simulacije. Šav (opcija C) bez tih izmena ne radi.

## 12. Odluke za direktora / korisnika

1. **Šta izlazi iz mlina: mlevena kafa (preporuka) ili cela zrna kao u videu.** Specialty kupac odmah vidi da cela zrna ne idu u V60. Mlevena kafa je tačna, ali na telefonu je to tanji „pesak" (2–5 px). Cela zrna se bolje čitaju, ali su pogrešna.
2. **Prelaz: opcija C (preporuka)** ili B.
3. **Para:** ravni (brže) ili volumen (+3,3 h). Odlučuje se posle probe POUR G150.
4. **V60:** providan kao u videu ili beli keramički (brži, manje šuma). Odlučuje se posle probe.
5. **Nivoi za desktop:** 1200 kao podrazumevani i 1600 samo za velike i Retina ekrane (preporuka, ≈ 21 MB naspram ≈ 30 MB), ili samo 1600.
6. **Talas: kod (preporuka).**
7. **Izmene u `grind.py` i `pour.py`** (13.) idu pre punog rendera. Bez njih ostaje samo opcija B (zakrpa preko šava).

---

## 13. Usklađivanje sa postojećim skriptama (`scripts/blender/kafa/`, stanje 23.10.2026)

Skripte su nastale paralelno sa ovim storyboardom. Ono što se slaže ostaje, a ostalo menja `blender-umetnik`.

| Tema | Sada u skriptama | Storyboard traži | Zašto |
|---|---|---|---|
| Kamera GRIND/POUR | 85 mm, 10° odozgo, GRIND 1,228 m (kadar 52 cm), POUR 1,15 m (48,7 cm) | 85 mm, **horizontalno + shift_y**, **ista** udaljenost u obe scene, POUR tačno 1 S niže | Šav: sa nagibom 10° razmera na granici je 0,86 (vert.) i 0,93 (horiz.), a sa različitim udaljenostima mlaz menja veličinu za ~7 %. |
| Koordinate | svaka scena ima pod na z = 0 | Zajednički sistem (modul `svet.py`): otvor 0,84 S od vrha GRIND kadra, ivica V60 0,47 S od vrha POUR kadra, pad ~0,63 S | da se mlaz iz GRIND-a nastavi u POUR na istom mestu |
| Mlaz mlevene kafe | čestice u `grind.py`, POUR prima „zrna iz GRIND" | **iste čestice** (emiter, seed, vreme) renderovane iz obe kamere; POUR kadar 1 = G65 | šav C |
| Okret mlina | statičan `--rot -25`, osa kroz otvor | osa kroz otvor ostaje. Predlog je animacija −25° → 0° (G1–G40), ili ostaje statično po odluci direktora. | glavni pokret GRIND-a |
| fps / usporenje | 30 fps, `--usporenje 0.4` | isto u GRIND i POUR; ≤ ~90 px po kadru na 1600 (≈ 0,3) | treperenje zrna |
| Broj kadrova | GRIND 90, POUR 120, SIP 90 | GRIND 96, POUR 128 (G65–G192), SIP 64 | zajednički sat i pola za telefon (neparni G) |
| GRIND kadar | kvadrat | 1600×2000 (produžetak 0,25 S nadole, samo mlaz) | iOS traka i šav |
| SIP | 0,56 m, 10°, spuštanje 4,5 cm + okret 28°, drška −8° | **ostaje tako** (nema šava). Samo da broj kadrova i poster prate tabelu iz 6. | — |
| Kese | `bags.py` (u izradi): doypack, 3 boje kao u videu, etiketa bez teksta, `--turn -24`, 800 px, 48 uzoraka | Isti model. Etiketa je tekstura iz dizajna kad bude gotova. PBR Neutral. Master 1200×1500 sa 256 uzoraka. Uglovi po kesi: −25° / 0° / +25°. | kartice i prodavnica |
| Kamera (napomena) | `pour.py` već ima izbor `nagib` (10°, „dogovor iz zadatka") i `rigk` (iz ovog storyboarda) | **Direktor bira.** Šav C traži `rigk` i u `grind.py`. | — |

---

## Izvori (otvoreno 23.10.2026)

- [Blender 5.2 LTS, release notes](https://developer.blender.org/docs/release_notes/5.2/) i [Physics](https://developer.blender.org/docs/release_notes/5.2/physics/): nova fizika u Geometry Nodes (XPBD) je za kosu i tkaninu i označena je kao eksperimentalna. Stranica ne pominje promene u klasičnom rigid body-ju ni Mantaflow-u, pa nisu provereni. Izdanje je od 14.7.2026, sa podrškom do jula 2028 (sažetak pretrage, [gamefromscratch](https://gamefromscratch.com/blender-5-2-lts-released/) †).
- [Blender 5.2 Cycles release notes](https://developer.blender.org/docs/release_notes/5.2/cycles/): nema promena u CPU renderu, OIDN-u, volumenu, shadow catcher-u i providnom staklu, ali ima Texture Cache i manju potrošnju memorije pri sinhronizaciji.
- [Blender 5.2 Manual, Rigid Body: Tips](https://docs.blender.org/manual/en/latest/physics/rigid_body/tips.html): mala tela su „currently unstable", idealno ≥ 20 cm. Mesh oblici „do not really have any thickness", pa ih izbegavati za mala i brza tela. Više koraka i solver iteracija daju veću stabilnost.
- [web.dev, Largest Contentful Paint](https://web.dev/articles/lcp) (ažurirano 4.9.2025): kandidati su `<img>`, `<image>` u SVG-u, `<video>`, `background-image` i blokovi teksta, a `<canvas>` nije među njima. „Good" je ≤ 2,5 s.
- **IZMERENO** u repou: `freiraum-premium/src/assets/seq/*` (veličine, pokrivenost alfom) i probno pakovanje uvećanih kadrova na 1600/1200/800 (privremeni folder).
- Vreme probnog kadra (13 s, 640², 32 uzorka) je dao direktor. Nisam ga merio, pa sve procene vremena zavise od njega.
- `studio/znanje/ai-alati.md` (trend-skaut, 23.10.2026), deo B: Blender za web sekvence. Odatle su:
  - polazna podešavanja Cycles-a (B4) i upozorenje o kafi u staklu;
  - OIDN koji nije vremenski stabilan;
  - fizika u uvećanoj sceni sa proksi-zrnima (B5);
  - talas kao CSS/SVG maska (B6);
  - budžet po kadru, isečak oko predmeta i klizni prozor za memoriju (B7).
  Gde se moj predlog razlikuje (uzorci, KB po kadru na desktopu), to je napisano uz broj. Ostatak baze (`trendovi.md`, `reference.md`) nije menjao ništa u ovom planu.
- Napomena o metodi: baza znanja se pojavila dok sam pisao, pa sam pretražio web pre nego što sam je video. Pretrage o Blenderu 5.2 i rigid body-ju se zato delimično preklapaju sa B1 i B5.
