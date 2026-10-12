# Kinematic Shot: demo sajt (beleška)

Demo sajt za (izmišljeni) filmski studio iz Beograda: reklame, spotovi, brend filmovi,
dokumentarci i kolor grejding. Sajt se „pušta” skrolovanjem kao film.

## Ideja
**Sajt je kamera.** Preko celog ekrana stoji tražilo (uglovi kadra, REC lampica, sat za
Beograd). Skrol je reprodukcija filma: dole levo piše trenutna scena, u sredini je montažna
traka sa oznakama scena (klik skače na scenu), a desno teče tajmkod (24 fps).

Tipografija koristi širinu fonta Archivo kao anamorfni objektiv: naslovi se „razvlače”
iz uskog u širok, kao kad se anamorfni snimak raspakuje u postprodukciji.

## Scene (redom)
| Scena | Šta se dešava |
|---|---|
| Uvod | Filmski „leader” odbrojava 3-2-1, blic, pa se otvaraju crne trake (letterbox) |
| SC.01 Opening | Montaža 4 kadra sa Ken Burns pokretom, podaci o kadru se menjaju, rotirajuće reči „We shoot …”, dugmad za format kadra (2.39 / 1.85 / 16:9 / 9:16) |
| SC.02 Manifesto | Tekst „ulazi u fokus” reč po reč dok se skroluje (rack focus) + skala fokusa objektiva; brojevi 24 / 2.39 / 180 / 3200 se vrte kao brojač |
| SC.03 Push in | Mali kadar raste do celog ekrana, „Every frame / is a decision.” se razmiče; dugme za showreel |
| Traka | Velike reči usluga klize, brže i u smeru skrola |
| SC.04 Selected work | Filmska traka sa perforacijom ide vodoravno; brojač 01/06; klik pušta mini reel projekta |
| SC.05 Shot list | Usluge kao lista kadrova; na hover slika prati kursor |
| SC.06 The grade | Klizač „pre/posle” (LOG prema gotovom grejdu) + 3 izgleda (KS-01/02/03) |
| SC.07 Script to screen | Proces kao montažni timeline (V1/V2/A1/A2), glava reprodukcije ide sa skrolom |
| SC.08 On set | Titlovi sa seta se smenjuju („Quiet on set…”, „Mark it.”), klapa klapne, broj take-a raste |
| SC.09 Final cut | Kontakt, kopiranje mejla, forma „brief” |
| SC.10 End credits | Odjavna špica (i zasluge za fotografije), veliki logo, dugme „Rewind” |

Tekstovi koji se smenjuju: rotirajuće reči u heroju, scenarističke oznake kadra
(„Sc. 12 · Ext. city street · Night”), titlovi sa seta, koraci procesa, naziv scene u donjoj traci.

## Priča koja ide sama (narator i „Play the film”)
- **Narator (V.O.)**: gore na sredini ekrana. U heroju svaki od 4 kadra ima svoju rečenicu
  (`data-line` na `<figure class="shot">`), a svaka scena ima svoju (`data-vo` na `<section>`).
  Priča: *Every film starts in the dark → … → Thank you for watching.*
- **Play the film**: dugme u heroju i u donjoj traci. Prvo se ispričaju 4 rečenice uvoda, pa se
  sajt sam skroluje (oko 150 px u sekundi) i na svakoj sceni zastane da se pročita narator.
  Prekida se skrolom, dodirom ili tasterom. Brzina: `speed` u objektu `auto`.
- **Međunatpisi** na početku i kraju filmske trake („Six stories, told in light.” /
  „Your story could be the seventh.”) i oznake kadrova u showreelu.

## Boje i fontovi
| Token | Boja | Uloga |
|---|---|---|
| `--black` | `#0A0D0E` | crna projekcione sale (senke ka tirkiznoj) |
| `--shadow` | `#121819` | paneli, forma, timeline |
| `--film` | `#17120F` | podloga filmske trake |
| `--light` | `#EFE7DA` | svetlo projektora, tekst |
| `--dim` | `#8E918A` | sporedni tekst |
| `--tungsten` | `#F3A34B` | akcenat (3200K, volfram svetlo) |
| `--rec` | `#FF4433` | samo REC lampica |

Fontovi (Google Fonts, skinuti lokalno u `src/assets/fonts`, licenca OFL):
**Archivo** (naslovi i tekst, širina 62–125 %), **Cormorant** italic (akcenti),
**Fragment Mono** (HUD, tajmkod, oznake).

## Fajlovi
- `src/index.html` – ceo sajt (HTML, CSS i JS u jednom fajlu, kao kod DON'S sajta)
- `src/assets/img/` – fotografije (WebP), `src/assets/fonts/` – fontovi, `src/assets/favicon.svg`
- `vendor/` – GSAP 3.13 + ScrollTrigger i Lenis 1.3 (za `dist/`, bez CDN-a)
- `build.py` – pravi `dist/` za hosting (`python3 kinematic/build.py`)
- `images.json` – koje Unsplash slike su gde i ko ih je snimio

## Kako se menja
- Tekstovi: direktno u `src/index.html` (sve je obično HTML).
- Rotirajuće reči u heroju: traži `'stories', 'light', 'motion'` u skripti.
- Titlovi sa seta: funkcija `buildOnSet`, niz `script`.
- Projekti: blok `<section class="work">`, svaki `<article class="frame">`.
- Forma: u `dist/` šalje na Netlify Forms (atribut `data-netlify`); u pregledu
  kaže da demo još nije povezan sa sandučetom.

## Fotografije (Unsplash)
19 fotografija, 19 autora, sve besplatne (Unsplash licenca). Spisak je u `images.json`.

| Mesto | Šta je na slici | Autor |
|---|---|---|
| `reel-1` | A wet city street at night, streetlights reflected in the asphalt | [Hiroya Nakashima](https://unsplash.com/photos/wet-city-street-at-night-with-glowing-streetlights-XcGNCdEP8Fw) |
| `reel-2` | An empty road running between dark hills at dusk | [Tim Foster](https://unsplash.com/photos/gray-concrete-road-during-nighttime-moJmTRR7E8U) |
| `reel-3` | A person in an orange jacket walking a foggy forest path | [Adlene Amiti](https://unsplash.com/photos/person-walking-on-a-foggy-forest-path-OOKwKlYirR8) |
| `reel-4` | A lighthouse lit against a teal twilight sky | [Kellen Riggin](https://unsplash.com/photos/lighthouse-illuminated-against-a-dark-twilight-sky-2SEER_RNB7w) |
| `push` | A man walking toward streetlights in the fog | [Markus Gjengaar](https://unsplash.com/photos/man-standing-in-concrete-road-during-night-time-NxeLSQ6uQVs) |
| `set` | A film crew in silhouette in front of a glowing orange LED wall | [Gordon Cowie](https://unsplash.com/photos/silhouette-of-people-holding-umbrella-4SYDbxHG0t8) |
| `grade` | Two people on a rooftop above a city street at dusk | [Sasha Samusevych](https://unsplash.com/photos/a-couple-of-people-sitting-on-top-of-a-roof-NwKrH1-4aBw) |
| `work-1` | A man in silhouette under falling rain, lit from behind | [Frederik Højfeldt Nielsen](https://unsplash.com/photos/silhouette-of-man-standing-during-nighttime-v0KFkaO6qwk) |
| `work-2` | A car with its headlights on, driving a winding road at sunset | [Gabe Pierce](https://unsplash.com/photos/black-car-on-road-during-sunset-txze3pN-RDM) |
| `work-3` | Three workers raking salt pans by hand | [Dibakar Roy](https://unsplash.com/photos/a-group-of-people-walking-across-a-dirt-field-pPuojOoHHak) |
| `work-4` | A woman lit by a row of bare bulbs | [Ilya Pavlov](https://unsplash.com/photos/woman-standing-beside-lights-xE87C_OvVO4) |
| `work-5` | A hiker below a sunlit peak that rises above the clouds | [Patrik László](https://unsplash.com/photos/a-person-standing-on-top-of-a-grass-covered-hill-iBSh3hrL8f8) |
| `work-6` | A dancer in a white dress, blurred by a long exposure on stage | [Ahmad Odeh](https://unsplash.com/photos/woman-in-white-dress-dancing-on-stage-zhNuTzUJ_p8) |
| `craft-1` | Two crew members at a rigged cinema camera on a tungsten-lit set | [Oleg Brovchenko](https://unsplash.com/photos/a-couple-of-people-standing-in-front-of-a-camera-t5xk1J6zaH8) |
| `craft-2` | A guitarist in silhouette at the microphone in stage haze | [Felipe Portella](https://unsplash.com/photos/man-holding-electric-guitar-h6gTtqBZUxc) |
| `craft-3` | Four friends walking a coastal road at golden hour | [Michael Henry](https://unsplash.com/photos/four-men-and-women-walking-on-roadway-near-body-of-water-8TNbGM3iu9o) |
| `craft-4` | An elderly woman smiling in warm window light | [Misak Aghababyan](https://unsplash.com/photos/an-old-woman-is-smiling-for-the-camera-LWzV0KPxwaA) |
| `craft-5` | An aerial view of an autumn forest meeting the sea | [Hans](https://unsplash.com/photos/a-tree-next-to-a-body-of-water-AeRh-NGBVak) |
| `craft-6` | An editor at a glowing monitor in a dark room | [Nubelson Fernandes](https://unsplash.com/photos/person-editing-video-in-dark-workspace-ZdOsQiwp0Ss) |

`dist/` ih učitava direktno sa Unsplasha (sa `srcset`-om, telefon skida manju verziju).
Kad mreža ovog okruženja dozvoli `images.unsplash.com`, slike mogu i lokalno:
`python3 kinematic/fetch_images.py && python3 kinematic/build.py`.

## Objavljivanje
- Pregled na Claude-u (privremene, umanjene slike): https://claude.ai/artifact/398N6MrQosRCT65FR1GzHr
- Pravi sajt: Netlify → Add new site → Import an existing project → GitHub → repo `Nemi`,
  grana `claude/sweet-edison-jx8jjl`, **Base directory: `kinematic`** (ostalo čita iz
  `kinematic/netlify.toml`). DON'S sajt ostaje na svom Netlify sajtu, ovo je poseban sajt.
- Ili Netlify Drop: prevuci folder `kinematic/dist` na app.netlify.com/drop.

## Šta je demo sadržaj
Imena projekata, opisi, ime režisera na klapi, adresa `hello@kinematicshot.com`
i linkovi ka mrežama su primeri. Fotografije su sa Unsplasha (besplatna licenca),
autori su navedeni u odjavnoj špici i u `images.json`.
