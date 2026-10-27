# Trendovi: dizajn, pokret, tehnika browsera, kratke vertikalne reklame

Poslednja provera: 2026-10-27
Vodi: `trend-skaut`. Prvo punjenje baze (nema prethodne provere).

## 0. Šta ova provera jeste i nije

- **Uzorak za trendove:** 13 stranica na Awwwards-u koje sam otvorio (Santioni Spirits, Bucks Sauce, Ciao Energy, Sunbeam Bagels & Coffee, Délice, Agrumea Farm, Son Daven, Tengile Malamala, ERA Residence, Realevate, Lama Lama, Floema, Butter), uz liste Site of the Day, Site of the Month i kategorija. Pojedinačni nalazi su u `reference.md`. (2026-10, awwwards.com)
- **Tehnologije i oznake** (GSAP, WebGL, Webflow, „Sound-Audio" itd.) su ono što autori sami upišu na Awwwards stranici. Nisu izmerene u kodu sajta. (2026-10, awwwards.com)
- **Sajtovi nisu renderovani.** Alat koji imam čita tekst bez izvršavanja JS-a, pa pokret i izgled na 390 px nisu viđeni. Za telefon koristim samo ocenu „Responsive Design" iz Awwwards Developer Award-a (ocena žirija, ne naša provera). Pre nego što se referenca uzme u dizajn, `tester` ili `recenzent` je otvara na 390 px. Napomena: `tools/playwright-cli/` ima samo `package.json`, nije instaliran; instalacija ide preko `bezbednost`.
- **CSS Design Awards, FWA i Godly** nisu čitljivi bez JS-a (prazan odgovor). CSSDA imam samo preko sažetaka pretrage, označeno u `reference.md`.
- **Curated Design:** pretrage „ice cream gelato", „cafe bakery restaurant" i „restaurant hero" nisu vratile ugostiteljske sajtove (vratili su Shop, Gelato (blockchain), galerije). Arhiva je jaka za SaaS i agencije, slaba za naše branše. (2026-10, curated.design)

## 1. Trendovi (potvrđeni na bar 3 dobra sajta)

Oznaka n/13 znači koliko od 13 otvorenih Awwwards stranica to navodi.

### T1. GSAP je standardni alat za pokret, a sad je i besplatan
- 8 od 13 navodi GSAP: ERA Residence, Son Daven, Lama Lama, Floema, Realevate, Bucks Sauce, Délice, Agrumea Farm (uz Lenis i Three.js). (2026-10, awwwards.com)
- GSAP je od 2025. besplatan i za komercijalnu upotrebu (vidi odeljak 3). (2025-05, gsap.com/standard-license)
- Za nas: Vista Estates je na istom alatu kao nagrađeni sajtovi. Za Freiraum i DON'S nema troška licence.

### T2. 3D/WebGL predmet kao glavni vizual, i u hrani i piću
- Ciao Energy (Three.js + Blender, interaktivni 3D predmet, SOTD 2026-07-30), Agrumea Farm (Three.js, HM 2026-10-01), Santioni Spirits (WebGL, SOTD 2026-10-05), Sunbeam Bagels & Coffee („3D", HM 2026-07-23). Van hrane: Floema, Son Daven, Lama Lama, Butter. (2026-10, awwwards.com)
- Cena: ovi sajtovi imaju ocenu pristupačnosti 6.6–7.0 (vidi T8).
- Za DON'S: voksel/Blender predmet (kornet, kugla) kao glavni lik ima ugled u nagrađenim sajtovima. Za Nemi reklamu: isti Blender model ide u video i na sajt.

### T3. Zvuk je deo doživljaja (ali samo na zahtev)
- Oznaka „Sound-Audio" nose Santioni Spirits, Ciao Energy i Sunbeam Bagels & Coffee („Music & Sound"). Sva tri su iz hrane i pića, jul–oktobar 2026. (2026-10, awwwards.com)
- Browser blokira zvuk bez radnje korisnika: „playback of any media that includes audio is generally blocked" dok korisnik nešto ne dodirne; video bez zvuka (ili sa utišanim zvukom) sme sam da krene. (2026-09, MDN Autoplay guide, izmenjeno 2026-09-10)
- Za nas: zvuk samo posle dodira na dugme „Ton an", uvek isključen na početku. Početna animacija DON'S-a mora da radi i bez zvuka.

### T4. Priča + veliki foto/video kadrovi u ugostiteljstvu i nekretninama
- Oznaka „Storytelling": ERA Residence, Son Daven, Tengile Malamala, Floema, Santioni Spirits. „Photo & Video" ili „Big Background Images": ERA Residence, Son Daven, Tengile Malamala, Délice. (2026-10, awwwards.com)
- Tengile Malamala sam opisuje sajt kao „quiet luxury through cinematic storytelling". (2026-10, awwwards.com/sites/tengile-malamala-collection)
- Za Freiraum i Vista: kadar i redosled kadrova nose utisak. Sadržaj (foto/video) je važniji od efekata.

### T5. Mikrointerakcije kao potpis
- Oznaka „Microinteractions": Bucks Sauce, Délice, Son Daven, Tengile Malamala, Realevate (5 od 13). (2026-10, awwwards.com)
- Za nas: male reakcije (dugme, ikona, kursor, brojač) jeftino daju utisak kvaliteta. Na telefonu nema hover-a, pa svaka mora da ima dodir/fokus ekvivalent.

### T6. Karakter brenda kroz ilustraciju, ikone i iznenađenje
- Santioni Spirits (strip-inspirisano iskustvo, ilustracija), Bucks Sauce (ikone, jaka ličnost), Sunbeam Bagels & Coffee („A website designed to surprise"). (2026-10, awwwards.com)
- Za DON'S: lik vilenjaka iz `video/prompt_gradnja_multishot.md` i roze-zelena paleta pripadaju istom pravcu (lik + ličnost), ne generičkom „sladoled" sajtu.

### T7. Pristupačnost je slaba tačka čak i nagrađenih (prilika za nas)
- Developer Award ocene 10 nagrađenih sajtova (Santioni, Tengile, ERA, Son Daven, Bucks Sauce, Ciao, Lama Lama, Realevate, Floema, Butter): pristupačnost prosek **6.86** (opseg 6.2–7.4), responsive prosek **7.52** (opseg 7.0–8.4), animacije prosek **8.06**. Prosek sam izračunao iz ocena na stranicama. (2026-10, awwwards.com)
- Najbolji responsive: Son Daven 8.40, Santioni Spirits 8.20. Najniža pristupačnost: Bucks Sauce 6.20. (2026-10, awwwards.com)
- Za nas: `prefers-reduced-motion`, kontrast i rad na 390 px su ono gde nagrađeni sajtovi gube poene. To je naša prednost i ne košta dodatni efekat.

## 2. Zapažanja (manje od 3 primera, nije trend)

- **Preloader sa brojačem procenata:** Son Daven („Loading the website … 0%") i ERA Residence (preloader). Oba su pobednici, ali za lokalni sajt to je zakašnjenje. Naš video-uvod mora da se može preskočiti i da prikaže sadržaj brzo. (2026-10, awwwards.com, tekst sajtova)
- **Prekidač dan/noć u hero-u** (ERA Residence) i **prevlačenje glavnog plana** („Drag to see more", ERA; „Drag to slide", Son Daven). Dobra ideja za Vista Estates, ali samo 2 primera. (2026-10, era-residence.com, sondaven.com)
- **Struktura nekretnine/hotel:** numerisana tri razloga, kartice tipova stanova, FAQ, modal za upit sa obećanjem odgovora u roku od jednog radnog dana (ERA Residence); isto FAQ i kartice jedinica (Son Daven). (2026-10, tekst sajtova)
- **Boja:** topla krem + skoro crna (Lama Lama `#F9F4EB`/`#1A1C1C`, Ciao Energy `#EEEEEE`/`#191917`) i zasićen topli akcenat (Délice `#DE2B2B` na `#F5DBCA`, Agrumea `#762530` + `#E94E1B`). Nemi paleta (`#efeae2`/`#0b0b0c`/`#ff5a24`) je u istom duhu. Po 2 primera, nije trend. (2026-10, awwwards.com)

## 3. Izbegavati / oprez

Nijedan obrazac nisam našao na 3+ sajta kao „već svuda", pa je ovo kratko i temelji se na dokazima, ne na utisku.

- **„Rotate your phone for better experience"** (Son Daven, 1 primer): prisiljava pejzaž. Protivi se našem pravilu 390 px. (2026-10, sondaven.com)
- **Dugi uvodi i logo animacije na početku vertikalne reklame:** TikTok savetuje „Skip long intros or logo animations". (2026, ads.tiktok.com guides/video-advertising-guide, bez datuma)
- **Težak WebGL bez rezerve:** sajtovi sa 3D/WebGL imaju pristupačnost 6.6–7.0 (T7). Svaki 3D mora da ima statičnu sliku kao rezervu i `prefers-reduced-motion`.
- **Zvuk koji kreće sam:** blokiran je u browserima (T3).
- **Animacije koje skrivaju sadržaj dok se JS ne učita:** sadržaj mora biti vidljiv u osnovnom CSS-u, a efekat dodat u `@supports` bloku (obrazac u odeljku 4).
- **Lenis stariji od 1.3.26** ne poštuje `prefers-reduced-motion` (vidi odeljak 5).

## 4. Tehnika browsera (stanje 2026-10-27)

Izvor podrške: web-platform-dx (api.webstatus.dev) i MDN browser-compat-data (bcd.developer.mozilla.org), oba čitana 2026-10-27. Napomena: MDN stranice ne prikazuju tabele podrške mom alatu, pa sam čitao podatke iz kojih se tabele prave.

| Mogućnost | Podrška | Baseline (webstatus 2026-10-27) | Sme kod nas? | Rezerva |
|---|---|---|---|---|
| **CSS scroll-driven animations** (`animation-timeline`, `scroll()`, `view()`, `animation-range`) | Chrome/Edge 115 (2023-07-18), Safari/iOS 26 (2025-09-15), Samsung Internet 23 (2023-10-18), **Firefox 159 (2026-10-27, uključeno po difoltu)** | webstatus još vodi „limited" jer Firefox nije upisan; MDN beleške izdanja Firefox 159 potvrđuju uključenje | **DA kao poboljšanje.** Firefox 159 je izašao danas, iOS/Safari ispod 26 nemaju podršku. | Sadržaj vidljiv bez efekta; efekat u `@supports (animation-timeline: view())` i `prefers-reduced-motion: no-preference`. Za skrol koji premotava `<video>` CSS ne može (to ostaje GSAP ScrollTrigger ili JS). |
| **View Transitions, isti dokument** (`document.startViewTransition`) | Chrome/Edge 111 (2023-03-07), Safari/iOS 18 (2024-09-16), Firefox 144 (2025-10-14) | **Baseline newly** od 2025-10-14 | **DA** (RealEstates React rute). | `if (!document.startViewTransition)` pa običan prelaz bez efekta. |
| **View Transitions, više dokumenata** (`@view-transition { navigation: auto }`, `pageswap`/`pagereveal`) | Chrome/Edge 126 (2024-06-11), Safari/iOS 18.2 (2024-12-11), **Firefox: ne** (bug 1860854) | „limited" | **DA za statične sajtove** (`sajt/`, `freiraum/`) kao čisto poboljšanje. | Browser bez podrške jednostavno učita novu stranicu. Ništa ne sme zavisiti od prelaza. |
| **`@starting-style`** | Chrome/Edge 117 (2023-09-12), Safari/iOS 17.5 (2024-05-13), Firefox 129 (2024-08-06) | **Baseline newly** od 2024-08-06 | **DA.** | U starijem browseru element se samo pojavi bez animacije ulaza. |
| **Anchor positioning** (`anchor-name`, `position-anchor`, `position-area`, `anchor()`) | `anchor-name`: Chrome/Edge 125 (2024-05-14), Safari/iOS 26 (2025-09-15), Firefox 147 (2026-01-13). `position-area`: Chrome/Edge 129 (2024-09-17), Safari 26, Firefox 147. | webstatus vodi celu grupu kao „limited"; podosobina `position_after_layout` ima Safari 27 (2026-09-14), Chrome 144, Firefox ne | **DA uz rezervu** (tooltip, meni, popover). | `@supports (anchor-name: --a)`; bez podrške običan `position: absolute` ispod okidača. |
| **Scroll-state queries** (`container-type: scroll-state`, `@container scroll-state(...)`) | Samo Chromium: Chrome/Edge 133 (2025-02-04), Samsung 29 (2025-10-25); **Firefox i Safari: ne** | „limited", MDN ga vodi kao eksperimentalan | **NE kao osnova.** Samo kao ukras (npr. senka zalepljenog zaglavlja). | Bez efekta ili IntersectionObserver. Nikad za funkciju. |

(2026-10, api.webstatus.dev i bcd.developer.mozilla.org; Firefox 159: developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/159)

Obrasci koje smemo koristiti (osnovni sadržaj je uvek vidljiv):

```css
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: view()) {
    .reveal { animation: reveal linear both; animation-timeline: view(); animation-range: entry 0% cover 30%; }
    @keyframes reveal { from { opacity: 0; translate: 0 2rem; } to { opacity: 1; translate: 0 0; } }
  }
}
@media (prefers-reduced-motion: no-preference) { @view-transition { navigation: auto; } }
```

Drugi obrazac (`@view-transition` unutar `@media`) je uobičajen obrazac, ali ga nisam potvrdio u specifikaciji u ovoj proveri: `tester` ga proba u Chrome-u i Safari-ju pre upotrebe.

Napomene:
- Pretpostavka agenta (nije izvor): CSS `animation-timeline` ne može da premotava `<video>` (nema CSS svojstva za vreme videa). Za „sajt koji se gradi dok skroluješ" ostaju GSAP ScrollTrigger ili sekvenca kadrova. Kako se `animation-timeline` ponaša uz Lenis na iOS-u: **NEPROVERENO**, testirati.
- Video na početnoj: `<video autoplay muted playsinline poster="...">`. `muted` dozvoljava autoplay, a `playsinline` je „required for autoplay in Safari". Ako autoplay ne uspe, prikazati poster i dugme (`NotAllowedError`). `navigator.getAutoplayPolicy("mediaelement")` vraća `allowed`, `allowed-muted` ili `disallowed`. (2026-09, MDN Autoplay guide, izmenjeno 2026-09-10)
- Pod posmatranje: `display: grid-lanes` (naslednik `masonry`, pominje ga Firefox 159; podrška u drugim browserima nije proverena). Firefox cross-document View Transitions (bug 1860854). Promena Baseline statusa za scroll-driven animations na webstatus.dev. (2026-10, MDN)

## 5. Biblioteke koje koristi RealEstates

| Biblioteka | Verzija danas | Licenca | RealEstates |
|---|---|---|---|
| **GSAP** (uključuje ScrollTrigger, SplitText…) | 3.15.0 (npm, 2026-10-27) | Standard „no charge" licenca, besplatna i komercijalno. Na snazi od 2025-04-30, poslednja izmena 2025-05-30 (Webflow). | `^3.15.0`, aktuelno |
| **Lenis** | 1.3.27 (npm, GitHub izdanje „15 Oct") | MIT | `^1.3.27`, aktuelno |

- **GSAP licenca:** komercijalna upotreba je pokrivena; dodaci koji su ranije bili samo za članove (npr. SplitText, MorphSVG) su uključeni; zabranjena je upotreba u alatima koji korisnicima daju vizuelni builder animacija bez koda i konkurišu Webflow-ovom builderu; kod koji generiše AI nije zabranjena upotreba. Webflow može da izmeni uslove objavom; ko ne prihvati, sme da koristi samo ranije verzije pod ranijim uslovima. Ni jedan naš projekat nije builder animacija. Preporuka agenta: u repo staviti kopiju teksta licence sa datumom. (2025-05, gsap.com/standard-license; 2026-10, gsap.com/pricing: „100% free for all users")
- **ScrollTrigger i ScrollSmoother** nisu pojedinačno imenovani u tekstu licence; spadaju pod „related plugins". SplitText i MorphSVG su imenovani izričito. (2025-05, gsap.com/standard-license)
- **Lenis beleške:** 1.3.26 (avgust) poštuje `prefers-reduced-motion: reduce`; 1.3.24 (jun) popravljeno označavanje teksta na iOS-u; 1.3.23 (april) popravljeno trzanje `syncTouch`. GitHub lista ne prikazuje godine; pretpostavljam 2026 jer je 1.3.27 trenutno poslednja na npm-u. (2026-10, github.com/darkroomengineering/lenis/releases)
- Za `tester` na RealEstates: Lenis sam štiti samo glatki skrol. GSAP animacije moraju same da provere `prefers-reduced-motion` (nisam otvarao kod RealEstates-a).

## 6. Kratke vertikalne reklame (za Nemi Studio, `studio/nemi-reklama/brief.md`)

**Granica:** nijedan zvanični izvor ne razlikuje reklame studija i agencija od ostalih. Ispod je opšte uputstvo platformi. Za pikselne i voksel stilove u reklamama nisam našao izvor, pa o tome ništa ne tvrdim.

**Prva sekunda / prve tri sekunde**
- „Grab attention in the first three seconds" i „Skip long intros or logo animations" (TikTok, vodič za male firme, bez datuma, © 2026). Otvoriti proizvodom u akciji, pitanjem, tvrdnjom ili iznenađenjem. (2026, ads.tiktok.com/business/en/guides/video-advertising-guide)
- „90% of ad recall impact is captured within the first six seconds" (TikTok, istraživanje iz 2020, TikTok sam objavljuje: samoprijavljeno). (2026, ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads)
- Reklame koje na ekranu prikazuju proizvod: „65% increase in brand affinity and 25% uplift in recall" (Lumen, 2021, samoprijavljeno od TikToka). Za nas: sajt (snimak ekrana) mora biti vidljiv u prvim sekundama. (isti izvor)

**Tekst bez zvuka i zvuk**
- Meta: „Over 75% of Reels views on Instagram are sound on" (samoprijavljeno). Znači da zvuk treba pravilno osmisliti, a ne preskočiti. (2024-11, developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/)
- TikTok: „TikTok is built for sound"; titlovi i tekst preko slike povećavaju vreme gledanja i pamćenje (Lumen 2021, samoprijavljeno); „use captions for clarity". (2026, ads.tiktok.com)
- Zaključak za brief: tekst mora da nosi poruku bez zvuka, ali zvuk je za većinu gledalaca uključen, pa svaki pokret zadržava svoj zvuk (kao što brief već kaže).

**Bezbedne zone (razlika od briefa)**
- Meta za Reels reklame: „roughly 14% of the top, 35% of the bottom, and 6% on each side" slobodno od teksta i loga; preporučeno 1440×2560, 9:16. (2026-10, facebook.com/business/ads-guide/update/image/instagram-reels, stranica za slikovne reklame)
- Izračun za 1080×1920: tekst i logo unutar x 65–1015 px, y 269–1248 px (gore 269, dole 672, strane 65). Brief pominje dole oko 20 % i desno oko 12 %. Meta traži znatno više dole (35 %). Desnih 12 % za TikTok dugmad nisam našao nigde u zvaničnom izvoru: **NEPROVERENO** (TikTok navodi „safe zones" bez mera).
- Preporuka agenta: koristiti Meta granice kao strožu donju granicu za sav tekst i logo.

**Dužina i kraj**
- TikTok za In-Feed reklame: „Up to 60 seconds, though 21–34 seconds performs best" (samoprijavljeno, bez datuma). Naših 10 s je znatno kraće; za organsku objavu to je u redu, ali reklamni format preporučuje duže. Odluka je direktorova. (2026, ads.tiktok.com guides)
- Jasan poziv na akciju na kraju; CTA kartice: „45% lift in recall and a 19% increase in likeability" (TikTok 2020, samoprijavljeno). (2026, ads.tiktok.com blog)
- Menjati kreativu na 2–4 nedelje (TikTok, bez datuma). (2026, ads.tiktok.com guides)
- Format: 9:16, 1080×1920 ili više. (2026, ads.tiktok.com guides)

**Petlja**
- TikTok vodiči ne pominju petlju. Instagram nigde ne navodi petlju kao signal rangiranja. Instagram kaže da najvažnije predikcije uključuju gledanje do kraja, deljenje i lajkove; vreme gledanja uključuje ponovljena puštanja, ali jedna pomoćna stranica kaže da broj puštanja ne uključuje ponavljanja (protivrečnost). Tvrdnja „petlja povećava domet" je **NEPROVERENO**; kao logika (gledanje do kraja, ponovno gledanje) razumna je, ali nema potvrde. (2025, about.instagram.com „Instagram Ranking Explained"; help.instagram.com/202865988324236; sažeci pretrage 2026-10)

## 7. Šta ovo znači po projektu

- **DON'S Eisdiele:** reference su u `reference.md` (Santioni, Bucks Sauce, Sunbeam, Délice, Ciao). Uvodni video: `muted playsinline`, poster, preskakanje, bez zvuka dok korisnik ne dotakne. Skrol-pokret: CSS scroll-driven uz `@supports`, a GSAP ScrollTrigger samo ako treba premotavanje videa.
- **Freiraum / Freiraum-premium:** Son Daven (responsive 8.40) i Tengile Malamala (pristupačnost 7.40) kao merilo. Cross-document View Transitions za prelaz među stranicama (čist dodatak).
- **Vista Estates:** biblioteke su aktuelne (GSAP 3.15.0, Lenis 1.3.27). Prekidač dan/noć i prevlačenje plana (ERA) su ideje, ne trend. View Transitions (isti dokument) za rute.
- **Nemi reklama:** vidi odeljak 6; bezbedne zone iz Meta izvora su strože nego u briefu.

## Arhiva

(prazno, prvo punjenje)
