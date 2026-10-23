# Stock video: besplatni, legalni snimci za Kafa skrol

Istraživač, 23.10.2026. Sve stranice su otvorene tog dana. Ništa nije preuzeto, osim sličica (thumbnails) za pregled, i one su samo u privremenom folderu, ne u repou.

Oznake:
- **NIJE POTVRĐENO**: nisam uspeo da potvrdim, ne koristiti kao činjenicu.
- **PROCENA**: moj zaključak, ne podatak sa sajta.
- Ocena 1–5 meri koliko se klip uklapa u naš izgled (krem `#E6DDCE` / terakota `#915439` / tamnobraon `#6E3A27`, predmet u desnoj polovini, čista pozadina, statična kamera):
  5 = skoro bez obrade; 4 = treba kadriranje, korekcija boje ili preklapanje; 3 = samo kao umetnuti prozor ili uz jaku obradu; 2 = slabo; 1 = ne.
- Ocenjivao sam po 4 pregledna kadra (početak do kraja klipa) i po tekstu stranice. Kamera je „statična" samo ako su sva 4 kadra istog kadriranja.

---

## 0. Sažetak

**Stock video ne može sam da reprodukuje referentni video, ali pokriva tri od šest kadrova.**

| Kadar | Stock pokriva? | Najbolji kandidat |
|---|---|---|
| 1. Mlin melje (inox + stakleni levak) | **Ne.** Nema čistog snimka bez ruku i tuđih logotipa. | (rezerva) Pexels 40206487, ocena 3 |
| 2. Zrna padaju kroz vazduh | **Delimično.** Postoji snimak na crnoj pozadini (izdvaja se jednostavno). | Pexels 32896425, ocena 4 |
| 3. Kuvalo sipa u V60 | **Da, uz korekciju boje.** | Mixkit 816 (tamno) ili Pexels 4794521 (svetlo), ocena 4 |
| 4. Talas / splash kafe za prelaz | **Ne.** Nema talasa koji plavi ekran, samo makro tečnost. | kod (talas iz storyboarda); makro samo kao tekstura |
| 5. Šolja sa parom | **Da.** | Mixkit 43935, ocena 5 |
| 6. Pakovanja kafe | **Samo fotografije** (prazne kese, za nalepnicu); video ne. | Pexels foto 12039675 / Unsplash luNZR9Mcys4 |

Tri velika problema (detalji u odeljku 5):
1. **Kontinuitet**: mlaz koji neprekinuto teče iz mlina u V60 preko granice sekcija traži isti svet i isto svetlo. Dva različita stock klipa to ne mogu.
2. **Izdvajanje pozadine**: čisto se izdvajaju samo klipovi na crnoj ili beloj pozadini (K2, deo K3). Klipovi sa zamućenom pozadinom (kafić, drvo, osoba) traže rotoskopiju.
3. **Svetlo i boja** se razlikuju od klipa do klipa, pa treba jedna zajednička korekcija boje.

**Preporuka:** hibrid. Stock za šolju (K5), pour-over kao dekorativni prozor (K3) i zrna na crnom (K2). Blender (već planiran u `storyboard.md`) za mlin, V60 sa mlazom koji prelazi granicu sekcija i kese.

Nemi Studio je već koristio Mixkit (Mixkit Stock Video Free License) i Coverr (Coverr License, bez obaveznog navođenja), prema `NAPREDAK.md` na grani `origin/claude/nice-mendel-xsfnrl`. Ista pravila važe ovde.

---

## 1. Licence (tačan naziv, šta dozvoljava, šta zabranjuje)

| Izvor | Licenca | Dozvoljeno | Zabranjeno / obaveza | Izvor teksta |
|---|---|---|---|---|
| **Pexels** (`PX`) | Free Stock Photo & Video License | Besplatno, komercijalno, bez navođenja autora, izmene dozvoljene | Prodaja neizmenjenih kopija (posteri, otisci). Sugerisanje da ljudi ili brendovi preporučuju naš proizvod. Prikaz prepoznatljivih ljudi u lošem ili uvredljivom svetlu. Preprodaja na drugim stock ili wallpaper platformama. Upotreba kao deo žiga, znaka, naziva firme. AI trening se ne pominje. | [pexels.com/license](https://www.pexels.com/license/) |
| **Pixabay** (`PB`) | Pixabay Content License | Besplatno, bez navođenja, izmene dozvoljene | Prodaja ili deljenje neizmenjenog sadržaja samostalno. Prepoznatljivi žigovi, logotipi i brendovi se ne smeju komercijalno koristiti uz robu i usluge. Prepoznatljive osobe se ne smeju koristiti nemoralno, nezakonito ni obmanjujuće. Upotreba kao deo žiga ili naziva firme. Autor može imati dodatna prava (provera je na korisniku). Pixabay ima i AI-generisan sadržaj (tag „Ai Generated"). | [pixabay.com/service/license-summary](https://pixabay.com/service/license-summary/) |
| **Mixkit** (`MK`) | **Mixkit Stock Video Free License** (komercijalno i nekomercijalno) i **Mixkit Restricted License** (samo lična upotreba). **Licenca je po klipu.** | Free: YouTube, društvene mreže, reklame, komercijalni projekti, bez navođenja (preporučuje se). Pravo da se preuzme, kopira, menja, deli. | Free: ograničenja iz Terms § 9: prodaja neizmenjenih kopija (štampa na šolji nije dovoljna izmena), kršenje Acceptable Use Policy, masovno preuzimanje skriptom ili botom. Komponente (ljudi, brendovi) mogu biti neodobrene od trećih strana, pa je provera na korisniku. **Restricted: samo lična upotreba, ne može na sajt klijenta ni u portfolio.** | [mixkit.co/license/modal/videoFree/](https://mixkit.co/license/modal/videoFree/) i [mixkit.co/terms](https://mixkit.co/terms/) |
| **Coverr** (`CV`) | Free Stock Video Footage License | Komercijalno i nekomercijalno, bez navođenja (poželjno) | Preprodaja i ponuda u okviru usluga koje se bave videom. Pravljenje konkurentne usluge. **AI trening.** Logotipi, žigovi i brendovi iz snimka. Nema model-release za prepoznatljive osobe. Na Coverr-u ima i **Coverr+ (premium, `isPremium=true`)** i **AI-generisanih** klipova (`isAiGenerated=true`), a oni nisu besplatni stock. | [coverr.co/license](https://coverr.co/license) |
| **Videezy** (`VZ`) | Videezy Standard License (besplatno) / Videezy Pro License (plaća se) | Standard: besplatno i za komercijalnu upotrebu, **ali uz obavezno navođenje** (na webu link „Stock Video by Videezy" na stranici). Bez navođenja samo uz kupovinu. | Pro klipovi (npr. 6785, 46614, 46617, 46620, 6779) su plaćeni. Rezolucija, fps i trajanje se ne vide na stranici klipa. | modal licence klipa, npr. `videezy.com/resources/47157/license_info_modal` |
| **Vecteezy** | Free License (video) | Besplatno, neograničena upotreba online | **Navođenje je obavezno.** Budžet produkcije do 1.000 USD. Zabranjene su sličice (stills) izvučene iz videa osim za promociju produkcije. Zabranjeno gomilanje klipova „za kasnije". Zabranjena samostalna distribucija. | [vecteezy.com/licensing-agreement](https://www.vecteezy.com/licensing-agreement) |
| **Videvo** | — | — | `videvo.net/license` vraća 301 na `freepik.com/license`, a ta stranica mi je vratila 403. Šta važi danas: **NIJE POTVRĐENO.** Sporedni izvori govore o Videvo Attribution License i CC BY 3.0 (obavezno navođenje). | pretraga, sekundarni izvori |

**Odluka o izvorima:** Pexels, Pixabay i Mixkit (samo klipovi sa „Stock Video Free License") su prvi izbor. Coverr samo kad je `isPremium=false` i `isAiGenerated=false`. Videezy samo ako direktor prihvata vidljivo navođenje. Vecteezy i Videvo se ne koriste (navođenje, budžetski limit, nejasna licenca).

**Mixkit zamka, nađena u ovom istraživanju:** više najboljih klipova zrna koja padaju su pod **Restricted License** i ne smeju na sajt. Provereno na stranici svakog klipa (rečenica „…for personal use only, under the Mixkit Restricted License"):
`25296` (zrna padaju na tamnoj pozadini), `16358`, `15200`, `38390`, `38397`, `15953`, `9501`, `17846`, `9417`, `25295`, `16335` (zrna), `7852` (voda u smeđu tečnost), `30812` (mleko u kafu), `44956` (šolja sa parom, zlatna), `7983` i `8402` (sipanje kafe), `28984` (mlevenje), `28428`, `28806`, `21036`, `24474`, `24363`, `44955`.
**Pre upotrebe svakog Mixkit klipa proveri rečenicu o licenci na njegovoj stranici.**

---

## 2. Kandidati po kadru

Skraćenice: **Pozadina** = boja uzorkovana sa gornjeg dela preglednog kadra (približno, video ima svoje svetlo). **Ljudi/ruke/logo** se odnosi na 4 pregledana kadra.

### K1. Mlin melje, stakleni levak (GRIND)

| # | Kandidat | Lic. | Rez. · fps · trajanje | Pozadina | Kamera | Ljudi / ruke / logo | Ocena i napomena |
|---|---|---|---|---|---|---|---|
| 1 | [Pexels 40206487](https://www.pexels.com/video/automatic-coffee-grinder-pouring-fresh-espresso-40206487/), Automatic Coffee Grinder Pouring Fresh Espresso (Rajat Sahu, 12.10.2026) | PX | 3840×2160 · 50 · 0:22 | bež, zamućena, nije jednobojna (krem-topla) | **NIJE POTVRĐENO**: kadar 0 (providan levak na narebrenom crnom telu) i kadrovi 4–12 (cev iz koje curi mleveno) imaju različito kadriranje, pa je pomak ili rez | ruke se ne vide; logo **NIJE POTVRĐENO** | **3.** Najbliže „mlin melje bez ruku". Mat crni mlin, ne inox. Mleveno curi u metalnu čašu. |
| 2 | [Pexels 4369686](https://www.pexels.com/video/close-up-of-coffee-beans-in-a-bean-hopper-4369686/), Close Up of Coffee Beans in a Bean Hopper (Ketut Subiyanto, 2020) | PX | 3840×2160 · 25 · 0:08 | svetlosiva, hladna, zamućena | statična | osoba zamućena u pozadini desno (opis stranice); ruku nema; logo se ne vidi | **3.** Veliki providan levak sa zrnima na hromiranoj bazi sa skalom, kao naš mlin. Zrna miruju, ne pada ništa. |
| 3 | [Mixkit 4985](https://mixkit.co/free-stock-video/coffee-beans-falling-into-a-coffee-pot-4985/), Coffee beans falling into a coffee pot | MK Free | 1920×1080 · 24 · 0:17 | breskva/krem, zamućena | statična | nema | **2.** Zrna padaju u stakleni sud mlina sa nožem (nije burr), makro odozgo, predmet izlazi iz kadra. |
| 4 | [Pexels 37633453](https://www.pexels.com/video/modern-coffee-grinder-in-action-37633453/), Modern Coffee Grinder in Action (Buğra, 17.5.2026) | PX | 2160×3840 (uspravno) · 30 · 0:17 | tamnoplava / čelik | statična | ruke se ne vide; portafilter | **2.** Mleveno pada u portafilter. Plavi ton, vertikalan. Isti set: [37554012](https://www.pexels.com/video/professional-espresso-grinder-dispensing-coffee-37554012/). |
| 5 | [Coverr Coffee Grinding Process](https://coverr.co/videos/coffee-grinding-process-xtltnwkvvw) | CV | 3840×2160 · 24 · 0:18,5 | kuhinjski zid, kablovi, razdelnik struje | statična | **ploča sa logotipom na mlinu**, ruka sa portafiltrom | **1.** Primer šta ne koristiti. |

Odbačeno: Pexels 2849951 (tetovirana ruka), 28889083 / 28889087 (kafić, ruka na kraju), 19428460 (nož mlina, makro).

### K2. Zrna padaju kroz vazduh (jednobojna pozadina)

| # | Kandidat | Lic. | Rez. · fps · trajanje | Pozadina | Kamera | Ljudi / ruke / logo | Ocena i napomena |
|---|---|---|---|---|---|---|---|
| 1 | [Pexels 32896425](https://www.pexels.com/video/coffee-beans-falling-in-dark-ambience-32896425/), Coffee Beans Falling in Dark Ambience (Evgenij Mikhailov, 6.7.2025) | PX | 3840×2160 · 59,94 · 0:20 | **crna, ravna** (`#111010`), dole tamna podloga | statična | nema | **4.** Slow motion: retka zrna padaju na gomilu u dnu kadra. Izdvaja se luma ključem ili `screen` mešanjem. Gomila je u donjoj trećini (može da se odseče ili ostane kao postolje). Pregled: `images.pexels.com/videos/32896425/pictures/preview-0.jpg` |
| 2 | [Pexels 3756153](https://www.pexels.com/video/scooping-from-a-bag-of-coffee-beans-3756153/), Scooping from a Bag of Coffee Beans (cottonbro studio, 2020) | PX | 4096×2160 · 50 (na stranici; u nazivu fajla 25, **NIJE POTVRĐENO**) · 0:05 | **krem, platno** (`#B4A999` gore), nabori | statična | **ruka sa zlatnom kašikom** prvih ~2 s | **3.** Jedina krem pozadina. Zrna se sipaju u platnenu kesu. Prvih 2 s se mora iseći zbog ruke. Kratak. |
| 3 | [Mixkit 42943](https://mixkit.co/free-stock-video/many-coffee-beans-on-a-black-background-42943/), Many coffee beans on a black background | MK Free | 4096×2160 · 24 · 0:07 | crna gore | statična | nema | **3.** Gomila zrna u prvom planu, zlatnosmeđa, par zrna pada odozgo. Kratak. |
| 4 | [Pexels 19428464](https://www.pexels.com/video/a-coffee-bean-falling-from-the-table-19428464/), A coffee bean falling from the table (Kelly, 2023) | PX | 1920×1080 · 23,98 · 1:00 | tamna sivosmeđa (`#2A2529`), glatka, ali sa stolom i horizontom | **NIJE POTVRĐENO** | nema | **3.** Pojedinačna zrna skaču po stolu, slow motion. Dugačak klip. |
| 5 | [Pexels 30143569](https://www.pexels.com/video/slow-motion-roasted-coffee-beans-falling-30143569/), Slow Motion Roasted Coffee Beans Falling (2025) | PX | 1920×1080 · 29,97 · 0:30 | topla smeđa bokeh (zamućena zrna) | statična | nema | **3.** Zrna padaju i odskaču. Pozadina nije ravna, ne može se izdvojiti. Dobra kao uramljen prozor. |
| 6 | [Pixabay 44802](https://pixabay.com/videos/coffee-beans-falling-close-up-seed-44802/), Coffee, Beans, Falling (ShikiRyu, 2020) | PB | 1920×1080 · fps **NIJE POTVRĐENO** · 0:12 (iz liste) | crna gore | NIJE POTVRĐENO | nema | **3.** Tamna zrna sa sjajem na crnoj pozadini. |
| 7 | [Mixkit 100247](https://mixkit.co/free-stock-video/sack-of-coffee-beans-overflowing-100247/) / [100255](https://mixkit.co/free-stock-video/burlap-sack-overflowing-with-coffee-beans-100255/) | MK Free | 4096×2160 · 24 · 0:32 / 0:19 | tamnoplavosiva teksturisana „škriljac" | statična | nema; 100255 ima ručni mlin i kašiku (bez vidljivog brenda, **NIJE POTVRĐENO** za pun kadar) | **2.** Zrna padaju u džak. Pozadina nije jednobojna ni u našoj paleti. |

Odbačeno: svi Mixkit klipovi „zrna padaju" pod Restricted licencom (vidi 1.).

### K3. Kuvalo sipa u V60 / pour-over (statična kamera, mirna pozadina)

| # | Kandidat | Lic. | Rez. · fps · trajanje | Pozadina | Kamera | Ljudi / ruke / logo | Ocena i napomena |
|---|---|---|---|---|---|---|---|
| 1 | [Mixkit 816](https://mixkit.co/free-stock-video/water-poured-into-a-coffee-filter-816/), Water poured into a coffee filter | MK Free | 1920×1080 (stranica piše „1080x720" za HD, očigledna greška) · 24 · 0:24 | **tamna smeđa, mirna** (`#29221C`), zamućena | statična | nema; nema čitljivog teksta u 4 kadra | **4.** V60 sa belim papirnim filterom, **čelično gooseneck kuvalo gore desno** (kao u našem rasporedu), bloom i tanak mlaz, slow motion. Dripper zauzima veliki deo kadra, a bokal je odsečen. Pregled: `assets.mixkit.co/videos/816/816-thumb-720-0.jpg` |
| 2 | [Pexels 4794521](https://www.pexels.com/video/pouring-hot-water-on-a-cup-with-filter-4794521/), Pouring Hot Water On A Cup With Filter (cottonbro studio, 2020) | PX | 4096×2160 · 25 · 0:32 | **svetla, skoro bela** (`#C2C2C1`), glatka | statična | nema ruku; čelično kuvalo gore levo | **4.** Crveni keramički V60 sa belim filterom. Bela pozadina se uklanja `multiply` mešanjem na krem. Crvena je bliska terakoti. Kuvalo je levo (može da se okrene horizontalno). |
| 3 | [Mixkit 88004](https://mixkit.co/free-stock-video/v60-pour-over-coffee-88004/), V60 pour over coffee | MK Free | 1920×1080 · **60** · 0:14 | **osoba** (plavosiva majica, tetovirana podlaktica desno), zamućena | statična | torzo bez lica | **3.** Providan V60 na staklenom bokalu, čelično kuvalo gore levo. 60 fps je najbolje za skrol. Pozadina je telo, ne može se izdvojiti. Isti set: [88005](https://mixkit.co/free-stock-video/person-making-a-v60-pour-over-coffee-from-above-88005/) (odozgo, ruka vidljiva). |
| 4 | [Mixkit 100257](https://mixkit.co/free-stock-video/pouring-coffee-into-a-drip-filter-on-wooden-table-100257/) / [100258](https://mixkit.co/free-stock-video/pouring-water-in-wooden-coffee-dripper-100258/) | MK Free | 4096×2160 · 24 · 0:23 / 0:20 | tamnoplavosiva zid, drveni pult, šolja, mlin, cimet | statična | nema | **3.** Chemex (ne V60) sa drvenom kragnom, **crno gooseneck kuvalo gore desno**. Ceo mizanscen (pult, šolja, mlin) je deo kadra, pa se ne može izdvojiti. Vertikalna verzija: [100345](https://mixkit.co/free-stock-video/pouring-water-over-coffee-grounds-in-filter-brewer-100345/) (1080×1920). |
| 5 | [Pexels 5564283](https://www.pexels.com/video/pour-over-coffee-in-making-5564283/), Pour Over Coffee in Making (Phillip Dillow, 2020) | PX | 1920×1080 · 23,98 · 0:36 | tamni granit | statična | nema ruku | **3.** Metalni filter, čelično kuvalo sleva, para, bloom. Isti set: 5540805, 5540807. |
| 6 | [Pexels 2849953](https://www.pexels.com/video/pouring-hot-water-on-a-portable-filter-cup-filled-with-ground-coffee-2849953/) | PX | NIJE POTVRĐENO | topla zamućena bašta | NIJE POTVRĐENO | ruka na kuvalu | **2.** |

Odbačeno: Pixabay 47245 (torba sa štampanim natpisom i ruka u kadru), Pexels 4391960 (osoba u kecelji).

### K4. Kafa se sipa / talas u slow motion (za prelaz)

Nema snimka u kome kafa plavi kadar. Svi kandidati su makro sipanja ili površine.

| # | Kandidat | Lic. | Rez. · fps · trajanje | Pozadina | Kamera | Ljudi / ruke / logo | Ocena i napomena |
|---|---|---|---|---|---|---|---|
| 1 | [Mixkit 236](https://mixkit.co/free-stock-video/filling-a-white-cup-of-coffee-236/), Filling a white cup of coffee | MK Free | 4096×2160 · 24 · 0:20 | tamna ljubičastosmeđa, zamućena | statična | nema | **3.** Mlaz u penastu kafu, slow motion. |
| 2 | [Pexels 855391](https://www.pexels.com/video/pouring-of-coffee-855391/), Pouring Of Coffee (2017) | PX | 3840×2160 · 25 · 0:09 | smeđemaslinasta, zamućena | statična | nema | **3.** Porcelan sa zlatnom ivicom, lepa površina. |
| 3 | [Pexels 4210979](https://www.pexels.com/video/coffee-drip-4210979/), Coffee Drip (Kaboompics, 2020) | PX | **1280×720** · 25 · 0:26 | topla ćilibarna keramika | statična | nema | **3.** Boja je tačna za naš „ćilibarni" talas, ali samo 720p. |
| 4 | [Mixkit 209](https://mixkit.co/free-stock-video/cup-full-of-coffee-209/), Cup full of coffee | MK Free | 4096×2160 · 24 · 0:18 | tamna ljubičastosmeđa | statična | nema | **2.** Mirna površina sa mehurićima. |
| 5 | [Pixabay 44244](https://pixabay.com/videos/coffee-drop-slow-motion-surface-44244/), Coffee, Drop, Slow, Motion, Surface | PB | 1920×1080 · fps **NIJE POTVRĐENO** · 0:17 (iz liste) | **bela, ravna** (`#CEC7C9`) | NIJE POTVRĐENO | nema | **2.** Talasići na crnoj kafi u beloj šolji. Izdvaja se `multiply`om. |
| 6 | Pixabay [316901](https://pixabay.com/videos/coffee-espresso-foam-vortex-detail-316901/) (4096×2304 · 24) i [341493](https://pixabay.com/videos/coffee-milk-drop-swirl-liquid-341493/) (7680×4284 · 30) | PB | trajanje **NIJE POTVRĐENO** | makro odozgo | NIJE POTVRĐENO | nema | **3.** Vrtlog kafe i mleka. Tagovi sadrže „Generated" i „Galaxy", pa je moguće da su **AI-generisani** (**NIJE POTVRĐENO**). Po licenci su besplatni, ali nisu „pravi" snimak. |
| 7 | Coverr [rxlz8tctij](https://coverr.co/videos/super-slow-motion-of-milk-poured-into-coffee-rxlz8tctij) / [j3txuozzn2](https://coverr.co/videos/milk-poured-into-coffee-j3txuozzn2) | CV | 3840×2160 · 24 · 0:28,6 / 0:35 | tečnost do ivica | statična | nema | **2.** Makro mleka u kafi. Može kao tekstura trake talasa. |

### K5. Keramička šolja sa kafom i parom, statična kamera

| # | Kandidat | Lic. | Rez. · fps · trajanje | Pozadina | Kamera | Ljudi / ruke / logo | Ocena i napomena |
|---|---|---|---|---|---|---|---|
| 1 | [Mixkit 43935](https://mixkit.co/free-stock-video/demonstration-video-of-a-steaming-cup-of-coffee-43935/), Demonstration video of a steaming cup of coffee | MK Free | **4096×2160** (i 1920×1080) · 24 · 0:10 | **tamnosmeđa, ravna** (`#442B25`), „brown background" po opisu | statična | nema; šolja bez logotipa | **5.** Tamna keramička šolja sa tankom parom na tanjiriću, zrna kafe, kriška limuna i cimet. Odgovara tamnobraon sekciji. Šolja je u sredini kadra, pa treba pomeriti udesno (kadriranje ili `object-position`). Pregled: `assets.mixkit.co/videos/43935/43935-thumb-720-0.jpg` |
| 2 | [Mixkit 43940](https://mixkit.co/free-stock-video/one-coffee-cup-in-a-sea-of-coffee-beans-43940/), One coffee cup in a sea of coffee beans | MK Free | 4096×2160 · 24 · 0:06 | tamnosmeđa (`#3D2822`) | statična | nema | **4.** Isti set, širi kadar, šolja manja. Kratak. |
| 3 | [Pexels 855414](https://www.pexels.com/video/cup-of-coffee-on-top-of-coffee-beans-855414/), Cup Of Coffee On Top Of Coffee Beans (Pixabay, 2017) | PX | 1920×1080 · 25 · 0:11 | **terakota bokeh** (`#9E5D47`, skoro naša `#915439`) | statična | nema | **4.** Bela šolja sa parom na zrnima, **u desnoj polovini kadra**. Boja pozadine odgovara POUR sekciji. Samo 1080p. Pregled: `images.pexels.com/videos/855414/free-video-855414.jpg` |
| 4 | [Pexels 9534789](https://www.pexels.com/video/a-cup-of-coffee-on-a-black-background-9534789/), A cup of coffee on a black background (max laurell, 2021) | PX | 3840×2160 · 23,98 · 0:21 | **crna** (`#000000`), ravna | šolja se **vrti** na postolju | nema | **3.** Tamna kamenina na crnom, lako se izdvaja, ali tamni predmet na tamnom ima slab kontrast (treba svetla ivica). Para se ne vidi. |
| 5 | [Pexels 7247786](https://www.pexels.com/video/close-up-view-of-coffee-dropping-on-a-mug-7247786/) | PX | 1920×1080 · 23,98 · 0:34 | tamna sivozelena (`#1B2022`) | statična | nema | **3.** Staklena šolja crne kafe, bez pare, hladan ton. |
| 6 | [Mixkit 808](https://mixkit.co/free-stock-video/steaming-mug-808/), Steaming mug | MK Free | 1920×1080 · 24 · 0:11 | tamna zamućena prostorija | statična („Static Shot") | nema | **3.** Siva šolja sa kašikom, svetlo sa strane. Hladan ton. |
| 7 | [Pixabay 329141](https://pixabay.com/videos/coffee-pouring-steam-cup-329141/), Coffee, Pouring, Steam (Solarselle77, 21.1.2026) | PB | 3872×2160 · 30 · 0:10 (iz liste) | tamnosmeđi gradijent | NIJE POTVRĐENO | nema | **3.** Izgled je odličan (narandžasta šolja, para, mlaz), ali kuvalo i mlaz izgledaju **AI-generisano** (**NIJE POTVRĐENO**). |

### K6. Pakovanja kafe (kese)

**Video: nema upotrebljivog.** Pexels 36964003 (uspravno, 1080×1920 · 30 · 0:08, 7.4.2026) ima kutiju sa okruglim logotipom na drvenom stolu (logo = ne koristiti, ocena 1). Pexels 32166344 su desetine tuđih brendova (ne koristiti).

**Fotografije (prazne kese, osnova za našu nalepnicu):**

| # | Kandidat | Lic. | Rezolucija | Pozadina | Napomena | Ocena |
|---|---|---|---|---|---|---|
| 1 | [Pexels foto 12039675](https://www.pexels.com/photo/paper-bag-on-white-background-12039675/), Paper Bag on White background (mockupbee, 2022) | PX | 3000×2000 | neutralna siva, ravna | Prazna kraft kesa, mockup. Nalepnica se postavlja perspektivnom izmenom. | **4** |
| 2 | [Pexels foto 12024976](https://www.pexels.com/photo/two-stand-up-zipper-pouch-on-white-surface-12024976/), Two Stand Up Zipper Pouch (Mr. Mockup, 2022) | PX | 3811×2531 | svetlosiva, ravna | Dve bele kese sa zipperom. | **4** |
| 3 | [Unsplash luNZR9Mcys4](https://unsplash.com/photos/brown-paper-pouch-on-white-luNZR9Mcys4), brown paper pouch (Vitalii Abakumov, 1.10.2026) | Unsplash License | veličina **NIJE POTVRĐENO** (traži se `w=3000`) | bela | Kraft kesa odozgo (flat lay). Unsplash License: besplatno, bez navođenja, ne sme prodaja bez značajne izmene i ne sme konkurentska zbirka. | **4** |
| 4 | [Pexels foto 29795391](https://www.pexels.com/photo/minimalist-coffee-packaging-display-on-wooden-table-29795391/) (Daniel & Hannah Snipes, 2024) | PX | 3405×5184 | topla drvena, bokeh | Kraft kesa sa belom etiketom na stolu. Topla boja odgovara terakoti. | **4** |
| 5 | [Pexels foto 29795387](https://www.pexels.com/photo/artisan-coffee-bag-and-mug-on-wooden-table-29795387/) | PX | 5184×3456 | drvo, jako svetlo | Kesa i šolja. | 3 |

Napomena: Unsplash `l1NDBXZlt4E` (srebrna folija) je **Unsplash+ (plaća se)**, ne koristiti. Fotografije 29795384 i 29795390 imaju ruke i haljinu, ne koristiti.
**PROCENA:** za kartice proizvoda je bolji render iz Blendera (`bags.py`, ~20 min za tri kese, već u `storyboard.md`), jer su tri kese iste geometrije i svetla kao sekvence. Stock fotografije služe kao referenca za papir i svetlo.

---

## 3. Najbolji kandidat po kadru

| Kadar | Prvi izbor | Rezerva | Zašto / šta se radi |
|---|---|---|---|
| K1 mlin | **nema (ocena ≥ 4)**; za prozor: Pexels 4369686 | Pexels 40206487 | Nema čistog mlina bez ruku i tuđeg logotipa. Preporuka: Blender. |
| K2 zrna u vazduhu | **Pexels 32896425** (4) | Pexels 3756153 (3, krem, iseći prvih 2 s) | Crna ravna pozadina, 60 fps, 4K. `screen` mešanje na tamnobraon ili luma ključ. Pad je redak, pa se po potrebi petlja. |
| K3 pour-over | **Mixkit 816** (4, tamna sekcija) | Pexels 4794521 (4, svetla sekcija, `multiply`) | Kuvalo gore desno kao u našem rasporedu. Mixkit 88004 daje 60 fps, ali je u pozadini osoba. |
| K4 talas | **kod (bez stocka)** | makro kao tekstura: Pexels 4210979 ili Mixkit 236 | Nema talasa koji plavi ekran. Talas iz `storyboard.md` (SVG/canvas) i dalje važi. |
| K5 šolja | **Mixkit 43935** (5) | Pexels 855414 (4, terakota, šolja desno) | Pozadina je već u paleti. Pomeriti šolju udesno, uskladiti zrna sa ostalim klipovima. |
| K6 kese | **foto: Pexels 12039675 + 12024976** (4), Unsplash luNZR9Mcys4 (4) | Blender `bags.py` | Prazne kese bez brenda. Nalepnica iz `dizajn/`. Video nema. |

**Kombinacija koja ima smisla (PROCENA):**
- GRIND: Blender (mlin) + sloj zrna iz K2 samo kao dekor (zrna se na `screen`u spuste iz vrha ekrana).
- POUR: Blender za V60 sa mlazom koji prelazi granicu. Mixkit 816 samo ako se odustane od neprekinutog mlaza i POUR postane „prozor" sa pour-over snimkom.
- SIP: Mixkit 43935 (`screen`/`lighten` ne treba, pozadina je u paleti).

---

## 4. Kako se izdvaja pozadina i priprema za skrol (PROCENA, nije testirano u ovom okruženju)

| Tip pozadine | Klipovi | Postupak |
|---|---|---|
| **Crna, ravna** | Pexels 32896425, Pixabay 44802, Mixkit 42943, Pexels 9534789 | CSS `mix-blend-mode: screen` ili `lighten` na tamnoj sekciji, ili `ffmpeg lumakey` u providan WebP kadar. Tamni delovi predmeta (tamna šolja) postaju poluprovidni, pa treba svetla ivica. |
| **Bela, ravna** | Pexels 4794521, Pixabay 44244 | `mix-blend-mode: multiply` na krem pozadini (belo nestaje). Senke ostaju, što je poželjno. |
| **Zamućena scena** | Mixkit 816, 88004, 100257, Pexels 855414, 5564283 | Ne može se izdvojiti ključem. Opcije: ostaviti pozadinu i uklopiti je bojom sekcije (korekcija boje + maska sa mekom ivicom), ili rotoskopija (alat izvan okvira, prvo `bezbednost`). |

**Skrol:** `video.currentTime` se trza ako klip nema ključni kadar na svakom kadru (PROCENA). Naš postojeći postupak (izvezeni WebP kadrovi, platno, `seq.json`, kao u `freiraum-premium`) rešava to i omogućava alfa. Budžet je u `storyboard.md` odeljak 8 (cilj ≤ 70–80 KB po kadru na 1200 px). Radi `mediji`, jedan po jedan klip, sa ručno preuzetim fajlom.

---

## 5. Rizici

1. **Različito svetlo i boja između klipova.**
   - Klipovi se razlikuju po temperaturi (88004 hladan, 855414 topao, 816 neutralan, 7247786 hladan), dubinskoj oštrini, zrnu, rezoluciji (720p–4K) i fps (24, 25, 30, 50, 60).
   - Bez zajedničke korekcije boje izgleda kao kolaž.
   - Mere: jedan zajednički LUT / gradacija za sve klipove u `ffmpeg`-u (krive, balans boja), isti odnos stranica i isto zrno, odabir klipova istog „raspoloženja" (tamno, toplo, zamućena pozadina). Najsigurnije: klipovi u okvirima (prozor sa zaobljenim ivicama) umesto predmeta koji lebde.
2. **Kontinuitet prelaza.**
   - Neprekinut mlaz iz mlina u V60 preko granice sekcija (opcija C u `storyboard.md`) traži isti svet, isto svetlo i istu simulaciju. Dva stock klipa to ne mogu.
   - Prelaz POUR → SIP pokriva kodni talas, pa tu razlika u svetlu manje smeta.
   - GRIND → POUR sa stock klipovima ostaje samo čist rez ili preklop (npr. zrna iz K2 padaju preko šava kao poseban sloj, ali ne ulaze u pravi V60).
3. **Izdvajanje pozadine.** Samo klipovi na crnoj ili beloj pozadini (K2, deo K3, K5 sa Pexels 9534789) se izdvajaju čisto. Svi ostali najbolji (816, 43935, 855414) imaju pozadinu koja je deo kadra. Pozadina Mixkit 43935 je već braon, pa je rešenje da sekcija dobije njenu boju, ne da se izdvaja.
4. **Položaj predmeta.** Većina klipova drži predmet u sredini ili levo, a mi hoćemo desnu polovinu. Kadriranje (crop) smanjuje efektivnu rezoluciju: 1080p isečak od polovine kadra je ~960 px širine. Okretanje horizontalno je moguće samo ako nema čitljivog teksta (u 43935, 816 i 855414 se ne vidi tekst u 4 pregledana kadra).
5. **Licence.**
   - Mixkit je po klipu Free ili Restricted (vidi 1.), a pretraga ih meša. Videezy traži vidljivo navođenje i ima Pro (plaćene) klipove. Coverr ima premium i AI klipove. Pixabay meša AI-generisan sadržaj.
   - Ljudi i brendovi: nijedan izvor ne garantuje model-release, pa se uzimaju samo kadrovi bez prepoznatljivih lica i bez čitljivih logotipa.
   - Preporuka: čuvati zapis za svaki korišćen klip (URL, datum, licenca, autor) u jednom fajlu (npr. `<sajt>/assets/LICENCE.md`).
6. **Originalnost.** Isti besplatni klipovi se koriste na mnogim sajtovima (PROCENA, broj nisam proveravao). To je dizajnerski, ne pravni rizik, ali smanjuje „vau" efekat portfolio makete.
7. **Preuzimanje.** Pexels i Pixabay stranice vraćaju Cloudflare proveru (403) na `curl`. Mixkit Terms zabranjuju masovno preuzimanje skriptama ili botovima. Preuzimanje klip po klip radi čovek u pregledaču ili `mediji` posle odobrenja, i čuva fajlove lokalno (hotlink se ne koristi).
8. **Dužina i kvalitet za skrol.** Mnogi klipovi su kratki (K2: 5–7 s) ili 1080p. Za 288 kadrova iz `storyboard.md` jedan klip daje samo 100–300 kadrova, a skrol od 100 vh traži oko 32–80 kadrova. Dovoljno je, ali ne za 240 vh pina bez ponavljanja.

---

## 6. Šta nije potvrđeno / šta nisam radio

- Ne znam da li Pexels 40206487 ima pomak kamere ili rez (kadrovi se razlikuju), ni da li se na mlinu vidi logo.
- fps za Pexels 3756153 (50 na stranici, 25 u nazivu fajla).
- Trajanje i fps za Pixabay klipove (stranica ih ne navodi, trajanje je iz liste rezultata). Rezolucija, fps i trajanje za Videezy (stranica ih ne prikazuje).
- Da li su Pixabay 329141, 316901, 341493 AI-generisani.
- Šta danas važi za Videvo / Freepik (403). Nisam tražio kandidate na Vecteezy-ju (licenca ih isključuje).
- Da li klip ima logotip ili čitljiv tekst u delovima koje nisam pregledao (gledao sam 4 kadra po klipu).
- Alfa video (WebM VP9 / HEVC alfa) i `mix-blend-mode` rezultati nisu testirani.
- Pexels API (potreban besplatan ključ) nisam koristio.

## 7. Pitanja za direktora

1. Prihvata li se hibrid (Blender za K1, deo K3 i K6; stock za K2 i K5)? Ili se traži čist stock, pa se K1 i neprekinuti mlaz izbacuju iz koncepta?
2. Je li dozvoljeno vidljivo navođenje (Videezy Standard)? Ako nije, Videezy otpada.
3. Treba li nastaviti sa ručnim pregledom prvog izbora (43935, 816, 32896425) u punoj rezoluciji pre odluke? To traži preuzimanje (`mediji`).

## 8. Predlog za bazu znanja (`studio/znanje/`)

Predlažem novi fajl `stock-izvori.md` (vodi `trend-skaut`), sa ovim stvarima koje važe za sve projekte:
- tabela licenci iz odeljka 1;
- **Mixkit je po klipu Free ili Restricted** (provera rečenice na stranici klipa);
- Videezy: Standard traži navođenje, a Pro se plaća;
- Coverr: polja `isPremium` i `isAiGenerated` u JSON-u stranice;
- tehnički trikovi za pregled bez preuzimanja videa: Mixkit sličice `assets.mixkit.co/videos/<id>/<id>-thumb-720-0..3.jpg`, Pexels `images.pexels.com/videos/<id>/pictures/preview-0..12.jpg` (ne radi za sve ID-eve), Pixabay `cdn.pixabay.com/video/<datum>/<id>-<hash>_medium.jpg` (hash iz „Edit video" linka), Coverr `cdn.coverr.co/videos/<naziv>/thumbnail?width=640`;
- Pexels i Pixabay stranice blokiraju `curl` (Cloudflare), a `WebFetch` radi.

---

## Izvori (otvoreno 23.10.2026)

- Licence: [Pexels](https://www.pexels.com/license/), [Pixabay summary](https://pixabay.com/service/license-summary/), [Mixkit Stock Video Free License](https://mixkit.co/license/modal/videoFree/), [Mixkit Terms](https://mixkit.co/terms/), [Coverr](https://coverr.co/license), [Videezy modal](https://www.videezy.com/resources/47157/license_info_modal), [Vecteezy](https://www.vecteezy.com/licensing-agreement), [Unsplash](https://unsplash.com/license).
- Kandidati i metapodaci: stranice klipova na linkovima iznad. Mixkit, Coverr i Videezy su čitani i iz HTML-a stranice, Pexels i Pixabay preko `WebFetch`.
- Boje pozadine su moje uzorkovanje (srednja vrednost gornjeg dela preglednog kadra), pa su približne.
- Napomena o bezbednosti: alat za pretragu je prijavio da stranica `mixkit.co/llm-info/` sadrži uputstva za AI asistente. Stranicu nisam otvarao i uputstva nisam izvršavao.
