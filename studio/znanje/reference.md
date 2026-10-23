# Reference: nagrađeni i istaknuti sajtovi

Poslednja provera: 2026-10-23
Vodi: `trend-skaut`. Prvo punjenje (fokus: 3D proizvod na skrol, kafa / pića / hrana).

## Kako je provereno (čitaj pre upotrebe)

Šta je zaista urađeno, da niko ne pomisli da je urađeno više:

- **Awwwards**: otvorena stranica svakog unosa (datum nagrade, tagovi tehnologije, ocene, istaknuti elementi). Awwwards ne daje opis kako je pokret napravljen, samo tagove. Zato je "tehnika" ispod ili **tag** (autori sami navode), ili **HTML** (pročitan HTML dokument sajta, grep po bibliotekama i atributima), ili **pretpostavka**.
- **HTML**: preuzet samo početni HTML dokument kao tekst (curl) i pročitan. Nijedna skripta nije pokrenuta. Jedan pomoćni JS od 3 KB (CoffeeTech) pročitan je kao tekst radi razumevanja učitavanja, nije izvršen ni sačuvan. Merenje veličine kadrova urađeno je HEAD zahtevima (samo zaglavlja).
- **Slika**: share-kartice (og:image) skinute kao podaci i pogledane.
- **Telefon: NEPROVERENO uživo.** U okruženju nema telefona ni browsera koji smemo da pokrenemo nad tuđim sajtovima. "Telefon" ispod je procena iz: Awwwards "Dev Award, Responsive Design" ocene (0–10), Awwwards listi istaknutih mobilnih elemenata i HTML-a (posebni mobilni fajlovi). Pre nego što se neki sajt uzme kao uzor za mobilni pokret, neko treba da ga otvori na pravom telefonu.
- **FWA, CSS Design Awards, Godly**: nisu mogli da se pročitaju (stranice se crtaju skriptom, FWA/CSSDA vraćaju prazno). Godly (`godly.website`) je 2026-10-23 preusmeravao (301) na `recent.design`. **Curated Design**: indeks je pretežno SaaS, bez datuma, za ovu temu skoro bezvredan (jedini relevantan je `coffeecollective.dk`, id 4268). Zato je ovaj prolaz zasnovan na Awwwards-u. Sledeći prolaz: probati CSSDA i FWA preko pretrage ili arhive.
- Oznake nagrada: **SOTD** = Site of the Day (jača), **HM** = Honorable Mention (slabija). Tipična SOTD ocena je 7,2–7,5, to je normalno.
- Pravilo 6 iz CLAUDE.md: uzima se princip, ne kopija. Ništa odavde se ne prepisuje (tekst, logo, fotografije, kod).

## A. 3D proizvod na skrol (najbliže našem kafa projektu)

### 1. More Nutrition, Iced Matcha Latte (case study)
- Link: https://more-nutrition.webflow.io/ (Awwwards: https://www.awwwards.com/sites/more-nutrition)
- Nagrada: SOTD 2025-11-03, uz Dev Award. Autori: FUTURE THREE®, Somefolk®, Eduard Bodak, tobias-anderssohn. (2025-11, Awwwards)
- Ocene: SOTD 7,39. Dev: Animations 8,20, **Responsive 8,00** (najviša u ovom uzorku). (2025-11, Awwwards)
- Šta je dobro: tegla proteinskog napitka je "naštimovana" na kosini, na polici, sa mekim prelivom boje u pozadini. Boja stranice prati ukus (#90b96d, #335c30). Oko proizvoda se na skrolu pojavljuju kartice sa činjenicama. Rukom crtani SVG potpisi i strelice sa blagim "wiggle" ponavljanjem daju toplinu. Logo je Lottie. Zasebni elementi u Awwwards listi: "3D Product Animation" i "3D Product Animation on Mobile", "Mobile Intro Animation". (2025-11, Awwwards)
- Tehnika (HTML, potvrđeno): sekcija sa `data-sequence-trigger` i "sticky" scenom, unutra `<canvas data-sequence-canvas>` koji učitava slike sa posebnog hosta; GSAP 3.15.0 sa ScrollTrigger, SplitText, CustomEase, DrawSVG, InertiaPlugin; Webflow. Znači: **unapred renderovana sekvenca slika na canvas-u, vezana za skrol**. To je tačno naša tehnika. (2026-10, HTML sajta)
- Telefon: posebno snimljena mobilna verzija pokreta (Awwwards je navodi odvojeno), Responsive 8,00. Uživo NEPROVERENO.
- Za kafa projekat: sticky scena + canvas + kartice sa činjenicama oko proizvoda; boja pozadine menja se po sekciji (mlin → kuvalo → pakovanje).

### 2. Vibe (koncept-prodavnica konzerviranog koktela)
- Link: https://vibebevvy.com/ (Awwwards: https://www.awwwards.com/sites/vibe)
- Nagrada: HM 2026-09-25. Autor: joelgobin. Napomena: **koncept-demo, nije stvaran brend**. Tagovi: 3D, Parallax, Transitions, Shopify. Istaknuto: "360° Product", "Mobile", "Loading Animation". (2026-09, Awwwards)
- Šta je dobro: **ogromna reč "Vibe Vibe" iza limenke, limenka u sredini preseca slova**. Reč je statična (ili sa sporijim parallax-om), proizvod se vrti uz skrol. Tipografija je debela, zaobljena serif. Paleta #DB98F9 / #FFF1E7 / tamna ljubičasta. (2026-10, share-kartica + Awwwards)
- Tehnika (HTML, potvrđeno u inline skripti): **150 kadrova** `vibe-can-seq-N.webp` na 2D canvasu. Skrol-progres sekcije se mapira na indeks kadra. Kadrovi se učitavaju u grupama po 10 kad se sekcija približi (do 2,5 visine ekrana ispred), pa se do učitavanja crta najbliži već učitan kadar. Canvas je 600×1500 CSS px, DPR ograničen na 2, kadrovi su renderovani u kutiji 1200×3000 pa smanjeni na 0,75× (supersampling) i **isečeni na limenku**, a pozicija se računa prema referentnoj kutiji. Sa `prefers-reduced-motion` učitava se samo prvi kadar. (2026-10, HTML sajta, inline skripta)
- Izmereno HEAD zahtevom (2026-10-23, 5 od 150 kadrova): **34–52 KB po kadru kao WebP** (preglednik sa `Accept: image/webp`), ukupno oko 6–7 MB. Isti URL bez `Accept` zaglavlja vraća PNG od 360–600 KB, što bi bilo oko 70 MB. Pouka: ugovorite formate eksplicitno, ne oslanjajte se na CDN pregovaranje. (2026-10, merenje)
- Telefon: "Mobile" je izdvojen kao istaknut element. Uživo NEPROVERENO.
- Za kafa projekat: najbolji uzor za tehniku i budžet. Princip: sečenje na proizvod + referentna kutija, učitavanje po blizini, najbliži kadar kao rezerva, reduced-motion = jedan kadar.

### 3. /zeroz brand site (Otsuka)
- Link: https://otsuka-air.jp/ (Awwwards: https://www.awwwards.com/sites/zeroz-brand-site)
- Nagrada: SOTD 2026-08-24, uz Dev Award. SHIFTBRAIN (+ minatosaori-3710, WongeunHeo). Klijent Otsuka Pharmaceutical. (2026-08, Awwwards)
- Ocene: SOTD 7,41. Dev: Animations 8,40, Responsive 7,60. (2026-08, Awwwards)
- Šta je dobro: pet numerisanih poglavlja, svako sa oznakom u zagradi, na primer "( About / Concept )" (urednički indeks). Naslov hero-a su krupne latinične reči ("Awaken / Energy, / Drive / Everything") iznad japanskog teksta. Poglavlja se "otvaraju" 3DCG scenama. Priča ide ka proizvodu, ne počinje njim. (2026-10, HTML + Awwwards)
- Tehnika (tag): **Three.js (WebGL) + Blender** (autori sami navode oba taga), plus Scrolling, Typography, Microinteractions. Sajt je napravljen u Astro-u. Pretpostavka: modeli i teksture su iz Blendera, scena u realnom vremenu. (2026-10, Awwwards + HTML)
- Telefon: HTML ima posebne `hero-mobile` slike za intervjue. Responsive 7,60. Uživo NEPROVERENO.
- Za kafa projekat: struktura poglavlja ("poglavlje = jedna radnja proizvoda") i brojevi 01–05 kao navigacija.

### 4. CIAO ENERGY (lansiranje linije pića)
- Link: https://www.ciaoenergy.com/ (Awwwards: https://www.awwwards.com/sites/ciao-energy-launch-website)
- Nagrada: SOTD 2026-07-30, uz Dev Award. Autor: Skaald. (2026-07, Awwwards)
- Ocene: SOTD 7,22. Dev: Animations 8,00, **Responsive 7,20** (najniža u uzorku, oprez na telefonu). (2026-07, Awwwards)
- Šta je dobro: interaktivni 3D objekat (limenka), zvučni dizajn, minimalistički identitet, beskonačni/ciklični hero ("Looping Site", "Hero with infinite scrolling"). Šest ukusa sa imenima razlomljenim na dva reda. Blokovi "pre/posle" (veštački aromi → prirodni, sintetički kofein → kofein iz zrna kafe) umesto praznih fraza. (2026-10, Awwwards + HTML)
- Tehnika (tag + HTML): **Webflow + Three.js + Blender**. U HTML-u: GSAP 3.15.0 sa ScrollTrigger i SplitText (Webflow CDN), Lenis, reference na WebGL i canvas. Znači realno-vremenski 3D, ne sekvenca slika. (2026-10, Awwwards + HTML)
- Telefon: najniža Responsive ocena u uzorku. Uživo NEPROVERENO.
- Za kafa projekat: "pre/posle" blokovi za sirovinu (npr. jedna sorta, jedna prerada) i ciklični hero.

### 5. SŌM (dnevni napitak za fokus)
- Link: https://www.drinksom.eu/ (Awwwards: https://www.awwwards.com/sites/som)
- Nagrada: SOTD 2026-04-04, uz Dev Award. Autor: .RAW. (2026-04, Awwwards)
- Ocene: SOTD 7,36. Dev: Animations 7,20, Responsive 7,00. (2026-04, Awwwards)
- Šta je dobro: "Product Details Scroll Experience" (detalji proizvoda se otkrivaju skrolom), 3D reakcija na miš, kontekstualni indikator stranice, odbrojavanje "Scroll down to explore". Paleta crvena #FF3A1F + bela. Veliki naslovi mešane veličine slova + sitne verzalne oznake sa velikim razmakom. Cena po danu (€4,49/dan) kao teksturalni detalj. (2026-10, Awwwards + HTML)
- Tehnika (tag): **WebGL + GSAP**, Vercel. Sajt je u Next.js-u. Realno-vremenski 3D (pretpostavka). (2026-10, Awwwards + HTML)
- Telefon: HTML ima posebne `hero-mobile-*` fajlove, duplirane blokove teksta sa drugim prelomima. Uživo NEPROVERENO.
- Za kafa projekat: otkrivanje karakteristika zrna (poreklo, visina, prerada) vezano za skrol proizvoda.

### 6. Santioni Spirits, "The Notturno Experience"
- Link: https://santionispirits.com/ (Awwwards: https://www.awwwards.com/sites/santioni-spirits)
- Nagrada: SOTD 2026-10-05, uz Dev Award. **Active Theory** + plan8. SOTD 8,09, najviša u uzorku. (2026-10, Awwwards)
- Ocene: Dev Animations **9,40** (najviša), Responsive **8,20**, Accessibility 6,60. (2026-10, Awwwards)
- Šta je dobro: stripski, ilustrovani ("mastilo") svet brenda umesto fotografije. Crno-bela paleta i visokokontrastni display serif sa preklapajućim slovima. Interakcije: "Pouring Beverage" (sipanje mišem), "Hand Animation", "Vortex", izbor ukusa, "Story Transition". (2026-10, share-kartica + Awwwards)
- Tehnika (tag): **WebGL, potpuno prilagođena**. HTML je samo ljuska od 32 KB. Pretpostavka: sopstveni engine. (2026-10, Awwwards + HTML)
- Telefon: Responsive 8,20 (dobra ocena za ovako težak sajt). Uživo NEPROVERENO.
- Za kafa projekat: sipanje kao "kontrola" (korisnik vodi kuvalo) i ilustrovani sekundarni sloj uz 3D. Budžet Active Theory-ja je van našeg dometa, ali ideja "sipanje = interakcija" nije.

### 7. CoffeeTech® (mašine za pržene kafe)
- Link: https://coffee-tech.com/ (Awwwards: https://www.awwwards.com/sites/coffeetech-r)
- Nagrada: SOTD 2026-07-16. Or Halevi + MAKETHECUT®. (2026-07, Awwwards)
- Ocene: SOTD 7,18. Dev: Animations 7,40, Responsive 7,60, WPO 7,20. (2026-07, Awwwards)
- Šta je dobro: **tamna podloga #0D0E13 + terakota #C8603D**, 3D hero i "360" prikaz, katalog sa filterima (Specialty / Commercial / Industrial Roasters), tri panela koja se šire (Coffee / Cocoa / Nuts), prelaz između stranica, brojčane oznake (01). Najbliža nama po temi (kafa), ali B2B (prženje, ne ispijanje). (2026-10, Awwwards + HTML)
- Tehnika (HTML): **Webflow + GSAP/ScrollTrigger/SplitText**. Slike su AVIF kadrovi izvezeni iz 3D renderera (nazivi tipa `…_0001_converted.avif`, `final_transparent_2_0001_…` sa alfa kanalom). Izmereno HEAD zahtevom: **6–71 KB po AVIF kadru** (jedan `transparent` kadar 71 KB). Da li je hero sekvenca na canvas-u, nije potvrđeno. (2026-10, HTML + merenje)
- Pažnja: pomoćna skripta sajta prepoznaje Lighthouse/PageSpeed i druge alate za merenje i tada služi lakšu verziju heroja. Njihova WPO ocena zato ne pokazuje stvarni doživljaj. **Ne kopirati tu praksu.** (2026-10, pročitano kao tekst, nije izvršeno)
- Telefon: Responsive 7,60. Uživo NEPROVERENO.
- Za kafa projekat: paleta (tamno + terakota), AVIF kadrovi sa alfom za proizvod.

### 8. Matcha Cartel
- Link: https://matcha-cartel.com/ (Awwwards: https://www.awwwards.com/sites/matcha-cartel)
- Nagrada: HM 2026-06-28. Surd Studio + WILDY RIFTIAN + Agnes Andreyana. (2026-06, Awwwards)
- Šta je dobro: koncept "matcha kao krijumčarena roba" (arhiva zaplenjene robe, preloader sa lozinkom, "cursor flashlight"). Istaknuti elementi: **"Matcha Pouring Scroll Video"** (sipanje vezano za skrol), "3D Products Section", "Matcha Obsession" (prelaz). Paleta #8CCC00 / #8796A1. (2026-10, Awwwards)
- Tehnika (tag): **Cinema 4D + Framer + Figma**. Pokret sipanja je verovatno video ili sekvenca unapred renderovana u C4D-u (pretpostavka). Sajt je Framer (HTML ljuska bez video taga, sve se crta skriptom). (2026-10, Awwwards + HTML)
- Telefon: NEPROVERENO (nema Dev Award ocene, HM).
- Za kafa projekat: scena sipanja (naše kuvalo) kao skrol-vođena sekvenca; narativ kao "svet" brenda.

### 8a. Koffiracha Hot Sauce (2025, malo starije, ali tehnika i tema su bliske)
- Link: https://koffiracha.com/ (studio Too Gallus)
- Nagrade: Gold, Interface Design, Scottish Design Awards 2025. Studio navodi i Awwwards Site of the Day i dve Online Design Awards. Awwwards stranica pod očekivanim imenom (`/sites/koffiracha-hot-sauce`) vraća 404, zato je **SOTD tvrdnja agencije NEPROVERENO**, a tačan mesec 2025. nije poznat. (2025, scottishdesignawards.com)
- Šta je dobro: ljuti sos sa kafom, više priče o brendu nego standardna prodavnica. Boca se "okreće i prevrće" uz skrol. (2025, scottishdesignawards.com)
- Tehnika: studio sam piše da su **3D render pretvorili u Lottie sekvencu vezanu za skrol** (scrubbable boca). Stek: Webflow dizajn izvezen u Shopify temu, Barba.js za prelaze stranica, GSAP. HTML potvrđuje Shopify + GSAP + Barba + Lottie i `<canvas>`. (2025, scottishdesignawards.com + HTML 2026-10)
- Telefon: NEPROVERENO.
- Za kafa projekat: drugi primer da "3D render → kadrovi vezani za skrol" prolazi kroz nagrade; Barba.js je opcija za prelaze između stranica kad se ne koristi View Transitions.

## B. Kafa i kafići, manje 3D, više struktura i ton

### 9. Sunbeam Bagels & Coffee
- Link: https://sunbeambagels.com/ (Awwwards: https://www.awwwards.com/sites/sunbeam-bagels-coffee)
- Nagrada: HM 2026-07-23. Drifting Creatives. (2026-07, Awwwards)
- Šta je dobro: razigran, "da iznenadi": **3D bagel pada u podnožju stranice** (podnožje kao završna scena), skriveni zvuci, rotirajući proizvod. Topla crveno-narandžasta paleta (#fa7e3b / #c3abc6), debeo serif naslov na fotografiji lokala (share-kartica). (2026-10, Awwwards + share-kartica)
- Tehnika (HTML): **Webflow + GSAP 3.15 + ScrollTrigger**, `<canvas id="bagel-canvas">` (biblioteka za fiziku nije identifikovana). (2026-10, HTML)
- Telefon: NEPROVERENO.
- Za kafa projekat: podnožje kao scena (zrna padaju u podnožju), zvuk samo na zahtev.

### 10. NewmixCoffee (Koreja, kafa u kesicama)
- Link: https://www.newmixcoffee.com/ (Awwwards: https://www.awwwards.com/sites/newmixcoffee)
- Nagrada: HM 2026-04-13. GrandeClip. (2026-04, Awwwards)
- Šta je dobro: stranica "Mix" gde korisnik "meša" kafu. Crno-bela paleta, marquee, plakati. Tagovi: **Three.js, React, Canvas API**. Sajt je Next.js. Ima odvojene `Footer_animation_desktop.mp4` i `…_mobile.mp4`. (2026-10, Awwwards + HTML)
- Tehnika: realno-vremenski Three.js za interakciju + video snimci za ambijent. (2026-10, tag + HTML)
- Telefon: odvojeni mobilni video fajlovi potvrđeni u HTML-u. Ponašanje uživo NEPROVERENO.

### 11. Best Bean Best Cup (Melburn, pržionica)
- Link: https://bestbeanbestcup.com.au (Awwwards: https://www.awwwards.com/sites/best-bean-best-cup)
- Nagrada: HM 2026-08-16. Nam Bui. Tagovi: **Blender, After Effects, Figma**, 3D. (2026-08, Awwwards)
- Šta je dobro: drzak crno-beli e-commerce, vijetnamsko nasleđe kao vizuelni identitet. Shopify tema sa GSAP/ScrollTrigger/Lottie. **Odvojeni `herobanner-desktop.mp4` i `herobanner-mobile.mp4`** (potvrđeno u HTML-u). (2026-10, Awwwards + HTML)
- Tehnika: Blender render → After Effects → video petlja kao hero. (2026-10, tagovi + HTML)
- Za kafa projekat: dokaz da pržionica sa Blender-om prolazi Awwwards, i odvojen mobilni hero video.

### 12. Seasats (robotika; samo kao tehnički uzor)
- Link: https://www.seasats.com/ (Awwwards: https://www.awwwards.com/sites/seasats)
- Nagrada: SOTD 2026-09-08, uz Dev Award. Raw Materials + Owls Department. Tagovi: **Cinema 4D**, 3D, Infinite Scroll. (2026-09, Awwwards)
- Ocene: Dev Animations 8,00, Responsive 7,40. (2026-09, Awwwards)
- Tehnika (HTML): Next.js; komponenta `AnimateFrames` sa `<canvas>` i "FlythroughPoints" okvirom, što je **sekvenca kadara iz 3D renderera na canvas-u**; ostale stranice koriste MP4. Lenis za skrol. (2026-10, HTML)
- Nije kafa. Služi kao dokaz da i SOTD sa renderom (C4D umesto Three.js) ide istim putem kao naš Blender.

### Ostali kafa sajtovi (struktura prodavnice i ton, bez 3D skrola)
Proverene samo Awwwards stranice, pokret nije gledan.
| Sajt | Nagrada | Šta uzeti | Izvor |
|---|---|---|---|
| Rye Island roastery, https://ryeisland.com/ | HM 2026-03-26 (CstudiosDigital) | puni ekran foto/video, specialty pržionica sa prodavnicom, Craft CMS | (2026-03, Awwwards) |
| Caffè Gilli, https://www.caffegilli.com/en | HM 2026-08-04 (thebrandingcrew) | filmski hero video, nasleđe (Firenca 1733), skrol kao priča; video + Vimeo | (2026-08, Awwwards + HTML) |
| Assembly Specialty Coffee, https://assemblycoffee.co.uk | HM 2025-10-20 (Alicia Blázquez) | čist, minimalan, #1A1A1A / #F5F6F1, jasna stranica proizvoda, Journal | (2025-10, Awwwards) |
| Little Amps Coffee, https://littleampscoffee.com | HM 2025-12-20 (Hello-World) | topla ilustracija, video blokovi, Shopify, #FFF9F2 / #FEBF6F | (2025-12, Awwwards) |

## Sažetak za brzu upotrebu

| Šta nam treba | Najbolji uzor |
|---|---|
| Sekvenca slika na canvas-u, budžet i učitavanje | Vibe (150 kadrova, merenja), More Nutrition (sticky + ScrollTrigger), Seasats, Koffiracha |
| Ogromna reč iza proizvoda | Vibe |
| Poglavlja i numeracija | /zeroz |
| Sipanje kao radnja | Matcha Cartel (skrol), Santioni (miš) |
| Paleta kafa (tamno + terakota) | CoffeeTech |
| Podnožje kao završna scena | Sunbeam |
| Odvojen mobilni hero | Best Bean Best Cup, NewmixCoffee, More Nutrition |

## Arhiva

- Coffee Collective (https://coffeecollective.dk/): HM 2025-09-26 (Dwarf, Shopify + Tailwind). Staro više od 12 meseci, 2026-10 premešteno. Mirna nordijska estetika (#FAF6ED / #4D4341), bez 3D skrola. Ima i unos u Curated (id 4268). (2025-09, Awwwards)
