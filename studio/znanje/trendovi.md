# Trendovi: 3D sajtovi na skrol

Poslednja provera: 2026-10-27

Pouzdanost: zvanični izvori (web.dev, GitHub izdanja three.js, Awwwards, Codrops) su navedeni uz stavku. Blogovi i agencijski pregledi (utsubo, svilenkovic, hontran, digitalstrategyforce) su samo trag i označeni su kao takvi. Brojevi iz blogova nisu merenja.

## Trendovi (ponavljaju se na više dobrih sajtova)

1. **Skrol je kamera (scrollytelling).** Skrol vodi kameru ili scenu kroz poglavlja, svako poglavlje ima svoj trenutak. La Revoltosa (poglavlje po ukusu), Explore Primland (let iznad terena), Sleep Well, Cartier (šest niša), Oryzo (dubina po Z). (2026-07, Awwwards; 2026-01..06, utsubo.com sekundarno)
2. **Putanja kamere iz Blendera.** Putanja se nacrta u Blenderu i izveze, u Three.js se rekonstruiše kriva, GSAP vodi kameru. (2026-07, Codrops) Za nas pogodno, Blender imamo.
3. **Kamera sa inercijom.** Dve vrednosti: ciljna (menja se odmah na skrol) i omekšana koja je prati (`gsap.quickTo`, `power3.out`). Daje osećaj teške filmske kamere umesto trzaja. (2026-07, Codrops; 2026-04, utsubo za Oryzo)
4. **Tekst kao deo scene.** Naslov je geometrija u 3D, pa ga proizvod lomi ili izobličava (La Revoltosa). (2026-07, Awwwards)
5. **Materijali koji se vide: refrakcija, transmisija.** Staklo, tečnost, lom svetla kao potpisni trenutak. (2026-07, Awwwards)
6. **Jedna scena, više varijanti.** Ista geometrija, menja se tekstura/boja, aktivan je samo jedan model. (2026-07, Awwwards, La Revoltosa)
7. **Rezervni običan prikaz.** Prekidač između scroll doživljaja i klasične mreže. (2026-07, Awwwards, La Revoltosa)
8. **Zvuk kao deo doživljaja** (Web Audio), npr. Cartier. (2026, utsubo sekundarno, jedan primer, još nije trend)

Dominacija Three.js: blog tvrdi da je 29 od 47 SOTD u Q1 2026 koristilo Three.js, **NEPROVERENO** (hontran.dev, bez metodologije).

## Tehnika, stanje podrške

| Tehnika | Stanje | Izvor | Sme li |
|---|---|---|---|
| WebGPU | Chrome/Edge 113 (desktop), Android Chrome 121 (Android 12+, Qualcomm/ARM). Firefox 141 Windows, 145 macOS ARM64 (Tahoe 26), Linux/Android/Intel Mac u toku. Safari 26 (macOS/iOS/iPadOS 26). | web.dev, 2025-11-25 | Samo sa WebGL rezervom. Na iPhone-ima ispod iOS 26 i većini Androida nema. Za Krume ostati na WebGLRenderer, WebGPU nije potreban. |
| three.js WebGPURenderer + TSL | Aktivno se razvija. r186 (24. 9. 2026): `DirectRenderPipeline`, `compileComputeAsync()`, `dispose()` je sada asinhron. r184 (16. 4.): `compileAsync()` stvarno ne blokira, kompajliranje TSL oko 3x brže. r185 (1. 7.). | GitHub izdanja three.js, 2026-10 | Ne za ovaj projekat (RealEstates je na ^0.186, ali WebGL). Pažnja: asinhroni `dispose()` u r186. |
| Gaussian splatting | Spark (World Labs, MIT, za three.js r180+, strimovani LOD). three.js r186 dobio izvorni splat renderer za WebGPU, **u razvoju, NEPROVERENO da je stabilan**. Rule of thumb: oko 500 hiljada splatova mobilno, 2,5 miliona desktop (36kr.com, nije zvanično). | sparkjs.dev, radiancefields.com, 2026 | Ne za Krume: hleb se ne skenira, a rizik na telefonu je velik. Pratiti. |
| Scroll-driven CSS animacije | nisu proveravane u ovom prolazu | | proveriti MDN/caniuse pre upotrebe |
| View Transitions | nisu proveravane u ovom prolazu | | proveriti pre upotrebe |

## Performanse na telefonu

Zvaničnih brojeva za scroll-3D sajtove nije nađeno. Ono što stoji potvrđeno samo kao praktičan konsenzus iz više blogova i foruma (rezerva: nisu merenja):
- **DPR ograničiti**: `renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5))` na telefonu, 2 na desktopu. Forum three.js: 40 fps na iOS-u sa punim DPR na jednostavnoj sceni (discourse.threejs.org, tema o niskom fps-u na iOS-u).
- **Post-procesiranje u pola rezolucije** označeno kao najveća jedinačna ušteda (digitalstrategyforce.com, blog).
- **Kompresija**: Meshopt za geometriju (brže dekodiranje, dobro za mnogo malih mesh-eva) ili Draco (manji fajl), KTX2/Basis za teksture, 512–1024 px na telefonu. Veličine ušteda se razlikuju po izvorima, ne citirati brojeve.
- **Pauza kad nije u vidu**: `IntersectionObserver` zaustavlja render petlju.
- **Učitaj samo aktivnu scenu** i oslobodi ostale (`dispose`). Primer: La Revoltosa (2026-07, Awwwards). Tim sam kaže da stabilnih 60 fps na svakom srednjem telefonu nije realno.
- Testirati na pravom telefonu, ne samo u emulatoru.

## prefers-reduced-motion

Zvaničan primer nije nađen kod nagrađenih sajtova. Predlog za naš kod (ne činjenica iz istraživanja): ne vezivati kameru za skrol, prikazati nekoliko statičnih kadrova (po poglavlju jedan), isključiti čestice i grain, zadržati običan skrol bez Lenisa.

## Izbegavati

- **Izlizano**: čist "proizvod se vrti u mraku" bez priče; kamera koja se trza 1:1 sa točkićem miša; teška bloom svetlost preko svega.
- **Rizično**: stalno učitavanje velikih modela pre prvog prikaza (nema spoljne potvrde, ali tim La Revoltosa je zato učitavao samo aktivni model); sajt koji se oslanja na WebGPU; splat skenovi na telefonu.
- **Napomena**: lista "izašlo iz mode" nije potvrđena nezavisnim izvorom, ovo su zaključci iz praktičnih saveta. Dopuniti kad se pregledaju sajtovi u browseru.

## Pozicioniranje: šta ovo znači za Krume

- Nije nađen nagrađen 3D sajt pekare 2025–2026, pa nema provere da ta kombinacija deluje. Pratiti tek posle izrade na pravom telefonu.
- Princip "skrol = vreme" (04:00 do 07:00) se poklapa sa trendom 1 i 3.

## Arhiva
(prazno)
