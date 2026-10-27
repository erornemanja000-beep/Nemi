# Reference: nagrađeni i vrhunski sajtovi

Poslednja provera: 2026-10-27

Napomena o proveri: stranice nagrada (Awwwards, FWA, CSSDA) vraćaju se kroz pretragu samo kao liste bez opisa, pa je ispod ono što se moglo potvrditi iz Awwwards članaka i iz sekundarnog pregleda (utsubo.com, agencijski blog, nije zvaničan izvor). Sajtovi nisu otvoreni u browseru (agent nema browser): **opis kamere i skrola je preuzet iz tih izvora, ne iz ličnog pregleda.** Ocenu na telefonu (390 px) niko nije proverio. Pre nego što se nešto uzme kao princip, `recenzent` ili `programer` neka otvori sajt kroz `playwright-cli`.

Pravilo: uzima se princip, ne kopija. Tekst, logo, modeli i fotografije se ne kopiraju.

## Hrana, piće, zanat

### La Revoltosa (španski sok, 70 godina stara marka)
- Link: https://larevoltosa.es/ (2026-07, izvor: Awwwards članak https://www.awwwards.com/la-revoltosa-rebooting-a-70-year-old-spanish-soda-brand-for-the-scroll-generation.html). Nagrada: iz članka se NE vidi, samo je studija slučaja. **NEPROVERENO** da li je SOTD.
- Stek: custom WordPress + Three.js + GSAP + Lenis, prvi WebGL projekat tima.
- Potpisni trenutak: 3D flaša od dva dela sa refrakcionim materijalom lomi naslov koji je iza nje (slova su prava geometrija u sceni, ne HTML). Na stranici pića svaki ukus ima svoju scenu vezanu za skrol, gde se menjaju model, ilustracija, pozadina i tekst zajedno.
- Telefon (izjava tima): smanjili broj poligona, ponovo koriste istu geometriju (menjaju samo etiketu/boju), učitan je samo aktivan model, ostali se oslobađaju iz memorije. Tim sam piše da je stabilnih 60 fps na svakom srednjem telefonu "skoro nemoguće". Postoji i prekidač na običnu mrežu proizvoda.
- Princip za Krume: jedna geometrija, više varijanti (4 hleba = jedan osnovni model + različite teksture); učitaj samo aktivnu scenu; ponudi običan prikaz kao rezervu.

### Oryzo by Lusion (oryzo.ai)
- Nagrada: Awwwards Site of the Month, april 2026, plus Developer Award (2026-04, izvor: utsubo.com pregled, sekundarni, **NEPROVERENO** na Awwwards stranici).
- Šta radi: 3D proizvod sa inercijskom kamerom i dubinom po Z osi na skrol, običan Three.js.
- Princip: kamera ne prati skrol 1:1, nego zaostaje i omekšava (inercija); proizvod je uvek glavni junak.

### Bunta Beer (buntabeer.com)
- Izvor: Awwwards element "3D product scroll animation" (autor Nikola Zahariev), https://www.awwwards.com/inspiration/3d-product-scroll-animation-bunta-beer. Nagrada i tehnika se na stranici ne navode, samo oznake product/scroll/3D. Samo trag, pregledati ručno.

### Sgrappa (hrana i piće, WebGL)
- Izvor: Awwwards element "Scroll with depth effect", https://www.awwwards.com/inspiration/sgrappa-scroll-with-depth-effect (oznake: food & drink, 3D, WebGL). Nagrada se ne navodi. Samo trag, pregledati ručno.

### Pekare bez 3D, za strukturu (Awwwards elementi)
- Sonoma Bakery (https://www.awwwards.com/inspiration/transition-sonoma-bakery) i UND NY (https://www.awwwards.com/inspiration/pastry-scroll-animation-und-ny), Haven Coffee + Kitchen. Nema 3D oznake. Služe samo kao trag za ton i raspored; nagrade se ne navode.
- Zaključak: **nije nađen nagrađen 3D sajt pekare/kafića iz 2025–2026.** Krume bi bio u retkoj niši. Rizik je što nema provereni uzor, prednost je što nema gomile istih.

## Opšti nagrađeni 3D/scroll sajtovi (za tehniku)

| Sajt | Nagrada | Šta radi | Izvor |
|---|---|---|---|
| Lando Norris | Awwwards Site of the Year 2025 (43 glasa; Users' Choice 596) | zvanično potvrđena pobeda; opis tehnike nije proveren | https://www.awwwards.com/annual-awards/winners (2026-10) |
| Messenger | Awwwards Developer Site of the Year 2025 | tehnika nije proverena | isto |
| Immersive Garden | Awwwards Agency of the Year 2025 | studio; za Cartier Watches & Wonders 2026: šest 3D "niša" sa GLSL, GSAP, Lenis i Web Audio muzikom | stranica nagrada; Cartier opis iz utsubo.com (sekundarno) |
| Explore Primland | Awwwards SOTD, 2026-02 | let kamere iznad stvarnog terena sa maglom, vezan za skrol | utsubo.com (sekundarno, **NEPROVERENO**) |
| Sleep Well Creative | Awwwards SOTD, 2026-01 | ilustrovana 3D scena vođena skrolom u Three.js | utsubo.com (sekundarno) |
| Hubtown (Unseen Studio) | Awwwards SOTD, 2026-06 | miš otkriva geometriju i svetlo u 3D hero sceni | utsubo.com (sekundarno) |
| IVRESS (Utsubo) | FWA Site of the Month, 2026-05 | WebGPURenderer sa WebGL rezervom, TSL shaderi za oba | utsubo.com, autor je sam studio, **NEPROVERENO** |

## Tutorijali koji pokazuju princip kamere (Codrops, zvanični tutorijal, ne nagrada)
- "Building a Scroll-Driven 3D Gallery Using a Blender Camera Path with Three.js and GSAP", 2026-07-07: putanja kamere se nacrta u Blenderu, izveze, u Three.js se rekonstruiše kriva, GSAP vodi kameru. Dve vrednosti: jedna se menja odmah na skrol, druga je omekšana (`quickTo`, ease `power3.out`) i kamera prati nju. Stranicu nije bilo moguće otvoriti (403), opis je iz rezultata pretrage. https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/
- "How to Build Cinematic 3D Scroll Experiences with GSAP", 2025-11-19: scrubovani ScrollTrigger timeline pomera kameru kroz niz pozicija. https://tympanus.net/codrops/2025/11/19/how-to-build-cinematic-3d-scroll-experiences-with-gsap/
- "More Than a Portfolio: Building a Scroll-Driven 3D World with Something to Say", 2026-04-28: Three.js + ScrollTrigger + Observer + SplitText. https://tympanus.net/codrops/2026/04/28/more-than-a-portfolio-building-a-scroll-driven-3d-world-with-something-to-say/

## Arhiva
(prazno)
