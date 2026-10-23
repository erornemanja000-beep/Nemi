# Fotografije: kafa-skrol (besplatne i legalne, 23.10.2026)

Istraživač, 23.10.2026. Osnova: `analiza-videa.md`, `tekstovi.md`, `skice/mapa-skrola.md`. Pinterest i slične stranice nisu korišćene.

Ovde su samo **linkovi i podaci**. Nijedan pun fajl nije preuzet. Za pregled sam gledao sličice od 360 px (za nekoliko spornih, do 1000 px) u privremenom folderu, ne u repou, i čitao metapodatke sa CDN-a.

## Kako je rađeno i šta je potvrđeno

- **Unsplash alat (MCP) nije bio dostupan u ovoj sesiji.** Iako ga opis servera pominje, nijedna njegova funkcija nije bila izložena. Zato sam koristio javne stranice Unsplash-a, Pexels-a i Pixabay-a i zvaničnu dokumentaciju. Nijedno API preuzimanje nije pokrenuto, pa nema šta da se prijavi.
- **Autor, datum, lokacija, tagovi i licenca** su pročitani sa stranice svake fotografije u tabelama, a CDN adresa slike je poređena sa stranicom. Rezultati pretrage su dati kao trag, a ne kao dokaz, jer sažetak malog modela ume da pogreši (isto upozorenje kao u `tekstovi.md`).
- **Rezolucija (Unsplash):** `images.unsplash.com/<foto>?fm=json` vraća `PixelWidth` i `PixelHeight` i orijentaciju (ispravljeno kad je slika rotirana). To su dimenzije originala po CDN-u.
- **Dominantne boje (Unsplash):** `?palette=json` sa istog CDN-a, bez preuzimanja slike. **Pexels** nema taj servis, pa su boje izračunate iz sličice od 360 px (približno). Dimenzije Pexels fotografija su sa njihovih stranica.
- **Pozadina:** ocena „ujednačena" znači da je standardna devijacija boje na ivici sličice mala (sd ≤ 25, računato iz sličice). To je pomoć, a ne garancija da će cutout biti bez ručnog posla.
- **Uklapanje u paletu:** ΔE (CIE76) između najbliže dominantne boje i cilja: krem `#E6DDCE`, terakota `#915439`, tamnobraon `#6E3A27`. ΔE ispod 10 je praktično ista boja, 10–20 bliska, preko 20 daleka. Ocena „dobro/loše" je moje tumačenje.
- **Skala ocena (1–5):** 5 je može direktno (cutout ili ugradnja) ili je skoro tačan uzor, čisto, bez brenda i ljudi, visoka rezolucija, boje u paleti. 4 je vrlo dobar uzor ili atmosfera uz mala ograničenja. 3 je upotrebljivo uz obradu ili samo kao uzor. 2 je slabo (brend, ljudi, pogrešan stil). 1 je ne koristiti.

## Licence (zvanični izvori, pročitano 23.10.2026)

| Izvor | Šta sme | Šta ne sme / šta licenca ne pokriva | Izvor |
|---|---|---|---|
| **Unsplash** | Sve slike „can be downloaded and used for free", komercijalno i nekomercijalno. Dozvola nije potrebna, **navođenje autora nije obavezno** (preporučuje se). | „Images cannot be sold without significant modification." Zabranjeno je sastavljanje slika sa Unsplash-a radi sličnog ili konkurentskog servisa. **Ne pokriva** zaštitne znakove, logoe i brendove na slici, prepoznatljive ljude i umetnička dela na slici. Unsplash ne može da proveri model release i „cannot make any guarantees about the scope of permitted uses". Odgovornost za prava trećih je na korisniku. | [unsplash.com/license](https://unsplash.com/license), [Releases and Trademarks](https://help.unsplash.com/en/articles/2612329-releases-and-trademarks) |
| **Pexels** | „All photos and videos on Pexels are free to use", izmene dozvoljene, navođenje nije obavezno. | Prepoznatljive osobe ne smeju da budu prikazane u lošem svetlu. Ne koristiti kao deo zaštitnog znaka, imena firme ili usluge. Ne sugerisati da ljudi ili brendovi sa slike preporučuju proizvod. Ne prodavati nepromenjene kopije. | [pexels.com/license](https://www.pexels.com/license/) |
| **Pixabay** | Besplatno, bez obaveznog navođenja, izmene dozvoljene. | Ne prodavati ni deliti sadržaj samostalno. Ako sadržaj ima prepoznatljiv zaštitni znak, logo ili brend, ne sme za komercijalnu upotrebu. Prepoznatljivi ljudi: ne koristiti nezakonito ni na uvredljiv način. „It is your responsibility to check whether you require the consent of a third party." Stranica ne pominje model release ni AI sadržaj, pa je to **NIJE POTVRĐENO**. | [pixabay.com/service/license-summary](https://pixabay.com/service/license-summary/) |

Ako sajt ima komercijalnu nameru (maketa za buduće klijente), ista pravila važe. Zato je u tabelama posebno označeno sve što ima **vidljiv brend** ili **prepoznatljivu osobu**.

---

# A. Predmeti: cutout ili uzor za 3D

## A1. Mlin (inox, stakleni levak)

**Nije nađena nijedna besplatna fotografija inox burr mlina sa staklenim levkom na čistoj pozadini** (Unsplash 10 stranica pretrage, Pexels 2, Pixabay 1). Pexels i Pixabay vraćaju skoro isključivo vintage ručne mlinove sa drvenom kutijom. Ispod su najbliži uzori za oblik i materijal, ne za cutout.

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| MLIN-1 | [Person milling coffee](https://unsplash.com/photos/person-milling-coffee-vrgJNOSj4Eo) | Nathan Dumlao, Unsplash (2017) | 4480×6720 | zamućen enterijer kafića, nije čista | `#d9dee1` `#b6b9b9` `#99a09f` `#796449` `#5d6253` | srednje: telo bakarno-braon (terakota ΔE 20), pozadina hladno siva | **4** | Stakleni levak sa zrnima koja **padaju odozgo**, tačno scena GRIND. Samo uzor: u kadru su ruke i ivica glave osobe. |
| MLIN-2 | [Mazzer grinder with roasted beans](https://unsplash.com/photos/mazzer-coffee-grinder-with-roasted-beans-gi9aryl6O9Y) | Ahmet Yüksek, Unsplash (2026-09-10) | 5226×7835 | bokeh pržionice | `#e6e6e6` `#b4c1c4` `#988576` `#74817e` `#522f19` | zrna ΔE 10 od tamnobraon, ostalo neutralno | 3 | Providan levak sa metalnim prstenom, najčistiji oblik levka. **Vidljiv logo „Mazzer"**: samo uzor. |
| MLIN-3 | [Automatic coffee grinder (Sam Riz)](https://unsplash.com/photos/a-coffee-maker-sitting-on-top-of-a-wooden-table-K5qTQSFGss4) | Sam Riz, Unsplash (2025-02-19) | 3980×5971 | tamna drvena podloga, zamućeno | `#d4cac2` `#9c8b84` `#856a59` `#6a5b54` `#4f3d41` | inox i smeđa podloga, dobro za materijal | 3 | Inox cilindar sa providnom čašom ispod: najbolji uzor za **inox materijal**. Na telu vidljiv natpis „Unique Life". |
| MLIN-4 | [Grinder filled with beans (wibowo)](https://unsplash.com/photos/a-coffee-grinder-filled-with-lots-of-coffee-beans-7Z9nFXhsKGM) | wisnu dwi wibowo, Unsplash (2023, Indonezija) | 3376×6000 | tamna, narandžast bokeh | `#fefefe` `#d8cacd` `#af928c` `#8a311c` `#522712` | zrna ΔE 10 od tamnobraon, bokeh blizu terakote (ΔE 18) | 3 | Makro: zrna iza stakla i odsjaj. Uzor za staklo i zrna, ne za oblik celog mlina. |

## A2. Gooseneck kuvalo

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| KUVALO-1 | [Grey stainless steel electric kettle](https://unsplash.com/photos/grey-stainless-steel-electric-kettle-mGlfn5uQH80) | Battlecreek Coffee Roasters, Unsplash (2019) | 5472×3648 | **jednobojna svetlosiva, ujednačena** (`#bfbfb7`, sd 17) | `#0f1416` `#6c6957` `#aeada5` `#c7beb5` `#d1c9bd` | pozadina blizu krema (ΔE 7), predmet neutralan | **4** | Inox gooseneck na postolju sa vagom, ravan ugao: najbliže „predmet na čistoj podlozi". Kabl i vaga ispod, senka ostaje pri cutout-u. |
| KUVALO-2 | [Stainless steel gooseneck kettle on a wooden board](https://unsplash.com/photos/a-stainless-steel-gooseneck-kettle-on-a-wooden-board-bd3Z3Bq9M4c) | Lera Ginzburg, Unsplash (2026-01-17) | 7274×4850 | kuhinjski enterijer, nije čista | `#f8fcf8` `#c8b9a7` `#97a6a7` `#897557` `#4f656c` | drvo i inox, srednje | 4 | Klasičan oblik sa tankim grlom i odsjajem inoxa u visokoj rezoluciji. Uzor za materijal. |

## A3. V60 dripper sa filterom na staklenom bokalu

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| DRIPPER-1 | [White Cup on Glass Sauce Bottle (V60 on server)](https://www.pexels.com/photo/white-cup-on-glass-sauce-bottle-2616169/) | Anna Tukhfatullina (myfoodie), Pexels (2019) | 3045×3806 | svetla bela kuhinja, cigla | `#e8eae9` `#d1cfc5` `#84726b` `#e3e3db` (iz sličice) | **krem ΔE 5**, kafa u crveno-braon tonu | **4** | Bela keramika, papirni filter i stakleni server, svetlo kao za naš krem sloj. Kuvalo iza. Na serveru su Hario oznake („01"). Naslov i opis na stranici se ne poklapaju (naslov kaže "sauce bottle"), slika je ispravna. |
| DRIPPER-2 | [Pour over coffee on a weighing scale](https://www.pexels.com/photo/pour-over-coffee-on-a-weighing-scale-8742029/) | Adrian Vocalan, Pexels (2021) | 2906×3874 | tamna plavosiva (`#383f4f`) | `#212123` `#4f5f7b` `#5f6f8c` (iz sličice) | po boji slabo (hladno plavo), po obliku odlično | 4 (kao uzor) | Najčistiji profil bele V60 i staklenog bokala sa odsjajima. Za sajt bi trebalo prebojiti. |
| DRIPPER-3 | [Clear glass coffee pot (pour over)](https://unsplash.com/photos/clear-glass-coffee-pot-on-brown-wooden-table-BrfShtTVC6I) | Wes Walker, Unsplash (2021) | 5977×8965 | bela cigla, drveni sto | `#dbdfe5` `#759ba9` `#996611` `#888787` `#738238` | toplo-neutralno, dobro | 4 | Para se diže iznad drippera: uzor za POUR (para i kapi). |
| DRIPPER-4 | [White ceramic mug and clear glass container (dripper on server, on a scale)](https://unsplash.com/photos/white-ceramic-mug-and-clear-glass-container-Gr0LeI6M7ho) | Julien Labelle, Unsplash (2019) | 3516×5273 | **svetlosiva ujednačena** (sd 12), tag „white background" | `#1e2728` `#564339` `#8d8b86` `#ababa5` `#c3b8a8` | neutralno | 4 | Bela keramika i staklo na čistoj podlozi, ali vaga je iste svetlosive pa cutout traži ručnu masku. |
| DRIPPER-5 | [Clear glass pitcher (blue V60)](https://unsplash.com/photos/clear-glass-pitcher-on-brown-wooden-table-zmGAqVOQAk8) | Luke Porter, Unsplash (2021) | 3825×4781 | tamna pozadina sa kuvalom | `#e2e6e5` `#d6d3cb` `#71a7c7` `#9a8572` `#78451c` | plava glazura odskače, ostalo toplo | 3 | Kompletan set (dripper, server, vaga, kuvalo). Plavo ne ide uz paletu. |

## A4. Šolja sa curećom glazurom (tamno telo, krem glazura)

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| SOLJA-1 | [An Artisan Mug](https://www.pexels.com/photo/an-artisan-mug-12544793/) | Naveen Kumar, Pexels (snimljeno 2020, objavljeno 2022) | 5568×3712 | **crna, ujednačena** (`#030302`, sd 9), odraz na podlozi | `#716155` (telo), crna (iz sličice) | telo braon (terakota ΔE 25), glazura bela, ne krem | **5** | **Najbliži uzor traženoj šolji:** tamnosmeđe telo sa teksturom drveta i bela glazura koja **curi sa ivice**. Crna pozadina se lako izdvaja (luma ključ). Glazuru u Blenderu pomeriti u krem. |
| SOLJA-2 | [Brown ceramic mug on floral textile](https://unsplash.com/photos/brown-ceramic-mug-on-white-and-blue-floral-textile-rIFGXNX-8fI) | Susan Holt Simpson, Unsplash (2020) | 3072×4608 | svetla plavosiva sa cvetnim stolnjakom (`#a4b6b5`) | `#1a0b06` `#4c352a` `#847b6a` `#6691a6` `#c27d3f` | šolje u tamnom braonu i ćilibaru (dobro), pozadina ne | 4 | Četiri naslagane šolje sa **ćilibarno-krem glazurom koja se sliva preko ruba**, retro 70-ih (isti duh kao pozadinske reči). Pozadina nije čista. |
| SOLJA-3 | [Brown and black ceramic cup](https://www.pexels.com/photo/brown-and-black-ceramic-cup-7009698/) | Luis Ruiz, Pexels (2021) | 4000×6000 | zamućena topla bež | `#a48872` `#534333` `#7b6c5d` `#9c7052` (iz sličice) | terakota ΔE 13, tamnobraon ΔE 19 | 3 | Krem glazura sa rđastim potezima i tamnom trakom. Nema curenja, a kadar seče šolju. |
| SOLJA-4 | [Handcrafted cup, brown and cream glaze](https://unsplash.com/photos/handcrafted-ceramic-cup-with-unique-brown-and-cream-glaze-RJM_n4A5Ocw) | Adam Rasheed, Unsplash (2026-06-25) | 2560×3200 | drvena podloga, zamućeno zelenilo | `#e9dfd3` `#c5956a` `#ad744c` `#997658` `#885a38` | **odlično: krem ΔE 2, terakota ΔE 8** | 3 | Boje su baš naše (krem gore, terakota dole), ali je tumbler bez ručke i bez curenja. Uzor za gradijent glazure i boje. |
| SOLJA-5 | [Handmade cup and saucer, black glaze](https://unsplash.com/photos/handmade-ceramic-cup-and-saucer-gE9NCV_Rths) | Max Tcvetkov, Unsplash (2026-08-22) | 7888×4437 | svetla krem, vintage mlinovi iza | `#060708` `#311611` `#55231a` `#a24e31` `#d0523c` | terakota ΔE 12, ali obrnut odnos (tamna glazura, glina dole) | 3 | Obrnut od tražene (crna glazura preko gline). Dobar kao uzor za sjaj glazure i tanjirić. |

## A5. Kese kafe (stand-up pouch)

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| KESA-1 | [Brown paper bag on a white table](https://unsplash.com/photos/a-brown-paper-bag-sitting-on-top-of-a-white-table-wizWrRZJXSg) | With Mahdy, Unsplash (2023-09-20) | 5906×3937 | bela podloga i kraft zid (`#e6d6c4`), jedna meka senka | `#5d3a1d` `#b98457` `#dac0ae` `#e7b17a` `#f1bd8a` | **odlično: pozadina skoro naš krem, kraft blizu terakote** | **5** | **Prazna kraft kesa** sa ravnim dnom i preklopljenom trakom za otvaranje na vrhu. Jedini natpis je sitan generički "TAP PULL TAB TO OPEN" na traci, bez brenda (provereno na prikazu od 900 px). Etiketu pravimo sami. Najbolji uzor za oblik i materijal. |
| KESA-2 | [Brown coffee beans inside white sack](https://unsplash.com/photos/brown-coffee-beans-inside-white-sack-7QlJ79Cj43w) | Nadia Valko, Unsplash (2019) | 3000×3750 | svetlosiva (`#dcddd8`, sd 23) | `#060806` `#64432d` `#867975` `#a7a8a7` `#c49b73` | zrna ΔE 10 od tamnobraon | 4 | Otvorena bela folija sa zrnima, bez brenda. Uzor za zrna u kesi i materijal folije. |
| KESA-3 | [Paper bag with scattered roasted coffee beans](https://www.pexels.com/photo/paper-bag-with-scattered-roasted-coffee-beans-14545422/) | Engin Akyurt, Pexels (snimljeno 2022-11-05) | 9453×7090 | **čisto bela** (`#fdfdfc`, sd 12) | `#a7754a` `#ead3be` + bela (iz sličice) | kraft ΔE 15 od terakote | 4 | Kesa **sa prosutim zrnima na čistoj beloj**: cutout je lak. Nije stand-up pouch nego položena papirna vreća. |
| KESA-4 | [A bag of coffee beans (top view)](https://www.pexels.com/photo/a-bag-of-coffee-beans-7657837/) | Cup of Couple, Pexels (2021) | 5464×8192 | bela (`#f6f7f8`, sd 5) | `#a38c84` + bela (iz sličice) | zrna smeđa, ostalo belo | 3 | Pogled odozgo na belu kesu sa zrnima, ne vidi se oblik pouch-a. |

## A6. Zrna (cutout, padanje)

Dodatak uz stavku iz zadatka: zrna su u videu glavni element prelaza GRIND → POUR.

| ID | Foto | Autor / izvor | Rez. | Pozadina | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| ZRNA-1 | [Brown coffee beans on white surface](https://unsplash.com/photos/brown-coffee-beans-on-white-surface-m7ijvnNGaV0) | Mockup Graphics, Unsplash (2020) | 4499×4499 | **čisto bela** (`#fefefe`, sd 1) | `#080503` `#56291a` `#774838` `#9f673a` `#c79273` | **zrna ΔE 7 od tamnobraon** | **5** | Gomila zrna odozgo na čistoj beloj: najlakši cutout. Za rasutu teksturu ili 2D zrna uz 3D mlin. |
| ZRNA-2 | [Pile of coffee beans on a white background](https://unsplash.com/photos/a-pile-of-coffee-beans-on-a-white-background-G4RS0NGIS8I) | Cemrecan Yurtman, Unsplash (2025-01-14) | 4160×6240 | krem breskvasta (`#e8dacc`, skoro tačno naš krem) | `#0c0b08` `#382e24` `#67432b` `#875d44` `#c37a4d` | **pozadina = naš krem, zrna ΔE 8** | 4 | Pozadina već odgovara krem sloju (GRIND). Senka ispod zrna. |
| ZRNA-3 | [Coffee beans falling into the air](https://unsplash.com/photos/a-pile-of-coffee-beans-falling-into-the-air-m3csqBPnMFw) | Maria Klichik, Unsplash (2024-06-03) | 3626×4532 | tamna, makro | `#cd9c60` `#777b84` `#4f362d` `#393635` `#1b2329` | tamno, topli odsjaj | 4 | Zrna u padu u makro kadru: uzor za pokret, svetlo i dubinsku oštrinu padanja. Nije cutout. |

---

# B. Atmosfera za sekcije ispod 3D dela

Boje ovde ne mora da budu u paleti 1:1, jer se preko slika stavlja tamnobraon ili krem sloj, ali bi trebalo da budu topli.

## B1. Prodavnica (zrna, kese, oprema)

Prvi pregled je pokazao da je većina polica sa kesama **brendirana** (provereno u većem prikazu), pa su ocene ispod niže nego što bi se očekivalo.

| ID | Foto | Autor / izvor | Rez. | Pozadina / kadar | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| SHOP-1 | [Glass jar filled with coffee beans](https://unsplash.com/photos/clear-glass-jar-filled-with-coffee-bean-lot-XgVHdER_fG4) | Clint Bustrillos, Unsplash (2019) | 3706×4632 | niz staklenih tegli sa zrnima, tamna pozadina, toplo svetlo | `#f4f3f1` `#cebdac` `#97a7a5` `#787469` `#564839` | tamno-braon, krem svetlo (ΔE 10), pogodno za tamnobraon sloj | **4** | **Bez brenda i bez ljudi** (proveren prikaz od 1000 px). Zrna u staklu: ista tema kao stakleni levak. Za prodavnicu kao atmosfera, ne kao slika proizvoda. |
| SHOP-2 | [A shelf filled with lots of white bags](https://unsplash.com/photos/a-shelf-filled-with-lots-of-white-bags-oJr2vE_h0_E) | Zachary Delorenzo, Unsplash (2021, Denver) | 3860×5790 | bele kese sa štipaljkama na drvenim policama, puzavica | `#e9e1dc` `#cbc2be` `#b7b9b5` `#91725f` `#5e6359` | krem ΔE 5, ali hladno-zeleno | 3 | Gornje dve trećine kadra su bez natpisa. **Donji deo ima limenke sa etiketama za čaj** ("BAO ZHONG", "MOONLIGHT JASMINE"): iseći. Zelenilo odskače od palete. |
| SHOP-3 | [Brown paper bags with white labels](https://unsplash.com/photos/brown-paper-bags-with-white-labels-stacked-together-7I0rU4R1OA8) | Monaz Nazary, Unsplash (2026-06-05) | 4016×6016 | gomila kraft kesa sa belim etiketama, jako sunce | `#100804` `#633a1c` `#9e836a` `#d3a373` `#e6b888` | **kraft = terakota/tamnobraon (ΔE 7–15)** | 3 | Boje su savršene, ali **etikete su na persijskom pismu** (naslov izgleda kao "هفته محیط زیست", moje čitanje, **NIJE POTVRĐENO**) i imaju sitan logo. Za bečku prodavnicu pogrešan jezik: samo kao tekstura ili uz retuš etiketa. Opis fotografa ne odgovara slici (piše "silverskin"). |
| SHOP-4 | [Bags of coffee beans on shelves](https://unsplash.com/photos/bags-of-coffee-beans-on-shelves-qvRafRg5S2k) | Haberdoedas, Unsplash (2025-10-12) | 6305×8407 | tamne police sa kraft kesama | `#dadae4` `#c1a37c` `#977a55` `#796547` `#383a51` | kraft odlično, ali kadar je taman | 2 | **Jasno vidljiv brend "BOOT, Branders uit Baarn 1973"**, holandski tekst na etiketama i cene u € ("Panamaria € 11,25"). Ne koristiti. |

## B2. O nama (pržionica, prženje)

Fotografije sa ljudima pri radu: nađene su samo takve gde se **ne vidi lice**. Čak i tada Unsplash ne garantuje model release, pa su ocene niže.

| ID | Foto | Autor / izvor | Rez. | Pozadina / kadar | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| ONAMA-1 | [Freshly roasted beans in a roaster](https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-QrrFbQp085M) | Khanh Do, Unsplash (2026-04-28) | 3483×5214 | bubanj sa zrnima odozgo, **bez ljudi** | `#ffcc01` `#d1e1da` `#cc9151` `#aa774d` `#714d2e` | terakota ΔE 13, tamnobraon ΔE 11 | **4** | Jaki topli tonovi. Žuti ram uz ivicu se može iseći. |
| ONAMA-2 | [Roaster machine (Umbra Coffee, Makassar)](https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-machine-iwcZmTKFo0w) | Ichsan Chairul, Unsplash (2026-03-10) | 5338×3559 | mešalica i zrna, **bez ljudi**, široki kadar | `#fefefe` `#c79d74` `#969289` `#766553` `#522d16` | tamnobraon ΔE 10 | **4** | Horizontalan, pogodan za baner. Fotografija je snimljena u stvarnoj pržionici (Indonezija), bez čitljivog brenda. |
| ONAMA-3 | [Coffee roasting in Playa del Carmen](https://unsplash.com/photos/coffee-roasting-in-playa-del-carmen-YC6RVdoTtIk) | Tim Mossholder, Unsplash (2020) | 6771×4515 | ruke sa metalnom lopaticom u bubnju | `#fcf8f0` `#d4a675` `#af9994` `#683b29` `#473628` | tamnobraon ΔE 4 | 3 | „Ljudi pri radu", ali samo ruke. Snimljeno u stvarnom kafiću (Cafe Kaawa, po metapodacima). |
| ONAMA-4 | [Beans being roasted (Indianapolis)](https://unsplash.com/photos/a-close-up-of-a-machine-making-coffee-beans-_7CVm353m7A) | Scott Soltys-Curry, Unsplash (2023) | 2615×3269 | hlađenje zrna u bubnju, toplo svetlo | `#fffffe` `#ca7525` `#a8a8a8` `#746557` `#554436` | tamnobraon ΔE 19 | 3 | Najmanja rezolucija u grupi. |

## B3. Brew guide (3 koraka pour-over)

Koraci iz `tekstovi.md`: 1 Grind / Mahlen, 2 Pour / Aufgießen, 3 Sip / Genießen.

| ID | Foto | Autor / izvor | Rez. | Pozadina / kadar | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| GUIDE-1 | [Coffee beans are being weighed on a digital scale](https://unsplash.com/photos/coffee-beans-are-being-weighed-on-a-digital-scale-dZAb0Km1ELY) | User_Pascal, Unsplash (2025-07-21) | 5602×3735 | drveni sto, vaga, crno kuvalo, zelenilo | `#080808` `#51382a` `#8e5231` `#ac734f` `#cbc797` | **terakota ΔE 4** | **4** | Korak 1 (merenje 18 g). Topao kadar. |
| GUIDE-2 | [A cup of coffee sitting on top of a scale (dripper with grounds, from above)](https://unsplash.com/photos/a-cup-of-coffee-sitting-on-top-of-a-scale-S9QYhiZ0tFE) | Jason An, Unsplash (2023) | 5993×3994 | pogled odozgo, neutralna toplosiva | `#e3e2e4` `#c4b5aa` `#a99789` `#8f7b6d` `#6c4a31` | tamnobraon ΔE 11 | **4** | Korak 2 (sipanje). Odozgo je lak za masku ili kružni kadar. |
| GUIDE-3 | [Person about to pour coffee powder in brewer](https://unsplash.com/photos/person-about-to-pour-coffee-powder-in-coffee-brewer-f01uTP4gX2c) | Najib Kalil, Unsplash (2018, Los Angeles) | 3840×5760 | ruka sipa mlevenu kafu u Chemex | `#f2d4d0` `#b16c5b` `#94867a` `#857059` `#516a50` | terakota ΔE 12, zelenilo odskače | 3 | Korak 1. Chemex, ne V60. Vidi se ruka sa tetovažom. |
| (korak 2 i 3) | vidi GUIDE-2, DRIPPER-1, DRIPPER-3 | | | | | | | Za korak 3 (Sip) nema dobre besplatne fotografije u paleti. **Preporuka: naša 3D šolja iz SIP poglavlja** ili SOLJA-1/SOLJA-2. |

## B4. Kontakt (bečki kafić, enterijer)

Jedini pravi bečki kafe-enterijer nađen među besplatnim izvorima je KONTAKT-1. Spoljašnjosti su dodatak.

| ID | Foto | Autor / izvor | Rez. | Pozadina / kadar | Dominantne boje | Uklapanje u paletu | Ocena | Napomena |
|---|---|---|---|---|---|---|---|---|
| KONTAKT-1 | [Elegant cafe interior with tables and chairs](https://unsplash.com/photos/elegant-cafe-interior-with-tables-and-chairs-yjE0w4YRYCI) | Sára Sedlmajerová, Unsplash (2025-12-06), **lokacija Beč** | 4000×6000 | enterijer: mermerni stolovi, savijene drvene stolice, tamno drvo, luster, novine | `#f1ede3` `#cfc8b9` `#b29767` `#926b52` `#6d6558` | **krem ΔE 6, terakota ΔE 14** | **4** | Pravi bečki Kaffeehaus (tagovi: marble table, newspapers, dark wood). Na zidu je slika u ramu (autorsko delo koje licenca ne pokriva), a lokal je verovatno stvaran (ime nije navedeno). Označiti kao „Symbolbild" u kontaktu, jer je naša adresa izmišljena. |
| KONTAKT-2 | [View of an empty cafe patio](https://www.pexels.com/photo/view-of-an-empty-cafe-patio-16862543/) | Anna Holodna, Pexels (2023), **Beč** | 2456×3661 | prazna bašta, prugast suncobran, **bez ljudi** | `#5b5749` `#a39c92` `#2b2c22` (iz sličice) | hladno zeleno-sivo, treba tople gradacije | 4 | Spoljašnjost kafića u Beču, mirna. Manja rezolucija od ostalih. |
| KONTAKT-3 | [Illuminated cafe exterior at night](https://unsplash.com/photos/illuminated-cafe-exterior-with-outdoor-tables-at-night-92emRwuQhoo) | Florian Schindler, Unsplash (2026-07-09), **Beč** | 8192×5464 | fasada noću, svetleći natpis „CAFE" | `#cee1d2` `#ac9163` `#6e502b` `#38424e` `#362614` | topli ćilibar, taman | 3 | Stvaran lokal sa natpisom. Taman, pa traži posvetljavanje. |
| KONTAKT-4 | [Karlsplatz store window](https://unsplash.com/photos/karlsplatz-store-window-N3nP9AQllcw) | Quentin Schulz, Unsplash (2018), **Beč** | 3681×2761 | lučni prozor sa zlatnim slovima „KARLSPLATZ" | `#fdf591` `#97938b` `#84776e` `#506853` `#46362d` | zeleno-zlatno, daleko od palete (ΔE 21+) | 3 | Bečki secesioni duh („Old school cafe"), ali ima **natpis lokacije i reklamu za pivo (zaštićen znak)**. Samo kao uzor. |
| KONTAKT-5 | [People talking inside a restaurant, arched window](https://unsplash.com/photos/people-talking-inside-a-restaurant-seen-through-an-arched-window-R5gqaRydhDM) | Florian Schindler, Unsplash (2026-07-09), **Beč** | 2769×4153 | lučni prozor, ljudi unutra | `#cce0de` `#c69f61` `#93754e` `#71522c` `#584731` | topli ćilibar | 2 | Vide se osobe unutra: ne koristiti (prepoznatljivi ljudi). |
| KONTAKT-6 | [Modern coffee shop interior, curved counter](https://unsplash.com/photos/modern-coffee-shop-interior-with-curved-counter-ZZxmc66SjfM) | Keghan Crossland, Unsplash (2019) | 3024×4032 | svetao enterijer, lučni prozori, tabla sa menijem | `#19160f` `#52504b` `#87563e` `#abaaa9` `#c5b8ab` | krem ΔE 7, terakota ΔE 7 | 3 | Boje su odlične, ali **lokacija nije navedena (NIJE POTVRĐENO da je Beč)**. Rezerva ako KONTAKT-1 otpadne. |

---

# Odbačeno (da se ne traži ponovo)

| Foto | Razlog |
|---|---|
| [Battlecreek pouch](https://unsplash.com/photos/battercreek-coffee-pack-rsnzc-8dVs0) (Battlecreek Coffee Roasters) | Čist kadar, ali **vidljiv brend** na kesi |
| Blue Bottle kesa ([Unsplash "white plastic pack"](https://unsplash.com/photos/white-plastic-pack-on-brown-wooden-table-OnvwNl5iRcY)), Boarding Pass, Cultivate, Homniom, Wood Burl, Blank Street, [zlatne kese "0566"](https://unsplash.com/photos/golden-bags-displayed-neatly-on-curved-shelves-pAj9ibNKLwI) (Declan Sun, Šangaj) | Vidljivi logoi tuđih brendova, licenca ih ne pokriva |
| [Niche Zero grinder](https://unsplash.com/photos/a-white-coffee-grinder-stands-ready-to-use-UgkYx9CswJE) (Kevin Dowling) | Logo „Niche", bela, nije inox |
| Crna kuvala ([Aritao](https://unsplash.com/photos/black-kettle-on-brown-wooden-table-GkDw-QcomAw), [Esch-Laurent](https://unsplash.com/photos/a-coffee-maker-on-a-table-tVeVHHWCfHM)) | Oblikom liče na Fellow Stagg (brend na slici **NIJE POTVRĐEN**), crno, ne uklapa se u paletu |
| Vintage ručni mlinovi (Pexels 13427987, Pixabay više desetina) | Drvena kutija i ručica, pogrešan stil za inox mlin |
| Pexels 15126445, 29689924 (Beč, Kaffee Konditorei) | Ljudi u kadru, vidljivi natpisi i logoi |
| Pexels 10966812 (Café Museum) | Vidljiv natpis na šolji (stvaran lokal) |
| Sve što je „Unsplash+" ili iStock | Plaćeno, besplatna licenca ne važi |

# Preporuka

**Fotografije ne zamenjuju render.** Ono što nađeno služi kao uzor za oblik, materijal i svetlo za Blender i kao atmosfera ispod 3D dela. Mlin, kuvalo i dripper ostaju u Blenderu, kako piše u `analiza-videa.md`.

| Namena | Prvi izbor | Rezerva |
|---|---|---|
| Cutout zrna | ZRNA-1 (5) | ZRNA-2 (4, pozadina već krem) |
| Cutout / uzor kese | KESA-1 (5, uzor) + KESA-3 (4, cutout kese sa zrnima) | KESA-2 (4, otvorena folija) |
| Šolja sa glazurom | SOLJA-1 (5, glazura koja curi) + SOLJA-2 (4, retro oblik) + SOLJA-4 (boje) | SOLJA-3 |
| Mlin | **nema čiste fotografije**: MLIN-1 (levak i zrna u padu) + MLIN-2 (inox i staklo) + MLIN-3 (inox telo) | MLIN-4 |
| Kuvalo | KUVALO-1 (čisto) + KUVALO-2 (materijal) | |
| Dripper | DRIPPER-1 (svetlo, krem) + DRIPPER-3 (para) + DRIPPER-4 (čista podloga) | DRIPPER-2 |
| Prodavnica | SHOP-1 (tegle sa zrnima) + SHOP-2 (iseći gornji deo) | SHOP-3 samo uz retuš etiketa |
| O nama | ONAMA-1 + ONAMA-2 (bez ljudi) | ONAMA-3 (ruke) |
| Brew guide | GUIDE-1 (korak 1), GUIDE-2 (korak 2); korak 3 iz naše 3D šolje | GUIDE-3 |
| Kontakt | KONTAKT-1 (enterijer) + KONTAKT-2 (spoljašnjost) | KONTAKT-6 |

Ukupno prvi izbor je 22 fotografije (18 Unsplash, 4 Pexels: KESA-3, SOLJA-1, DRIPPER-1, KONTAKT-2).

## Uslovi za `mediji` (preuzimanje)

1. **Praćenje preuzimanja (Unsplash).** Zvanična dokumentacija ([API guidelines](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines), [API docs](https://unsplash.com/documentation)) kaže da se pri svakom preuzimanju fotografije preko API-ja mora poslati `GET /photos/:id/download` na adresu `photo.links.download_location`. **Ako `mediji` koristi Unsplash MCP alat ili API, taj poziv je obavezan za svaku preuzetu fotografiju.** Ja nisam imao alat, pa nijedan nije pokrenut.
2. **Ista smernica traži i hotlink** (`photo.urls`) i navođenje autora sa linkom na profil i `?utm_source=<app>&utm_medium=referral`. Hotlink protivreči statičnom sajtu koji sam služi slike (Netlify objavljuje `dist`, vidi `CLAUDE.md`). **Otvoreno pitanje za direktora:** ili se slike preuzimaju ručno sa stranice fotografije (dugme „Download", licenca to dozvoljava bez API-ja), ili se prihvata API pravilo. Da li dugme beleži preuzimanje i kako Unsplash tumači API smernice za ručno preuzimanje: **NIJE POTVRĐENO**.
3. **Ne zaobilaziti proveru „nisi bot".** `unsplash.com` odbija goli `curl` stranicom „Making sure you're not a bot!" (HTTP 401). Pokušaj je prekinut i nije zaobiđen. CDN `images.unsplash.com` odgovara bez provere.
4. **Preuzimati samo potrebnu širinu.** CDN prima `?w=2400&q=85&fm=jpg` (Unsplash) i `?auto=compress&w=2400` (Pexels). Pun original treba samo za cutout (ZRNA-1, SOLJA-1, KESA-1, KESA-3).
5. **Pre upotrebe u punoj rezoluciji proveriti** sitan tekst i logoe (posebno SHOP-2, SHOP-3, KESA-1), prepoznatljive osobe (MLIN-1, ONAMA-3, GUIDE-3, KONTAKT-1) i znake AI generisanja kod objava iz 2026. (nijedan izvor ne označava AI poreklo, ali ni ne garantuje da ga nema).
6. **Navođenje autora** nije obavezno ni na Unsplash-u ni na Pexels-u (osim ako se koristi Unsplash API, vidi tačku 2). Preporuka: stranica „Credits" ili red u footeru uz napomenu Konzept / Demo, a ova tabela je evidencija.
7. **Kontakt-fotografije su stvarni lokali** u Beču, a adresa na sajtu je izmišljena. Uz njih ide oznaka „Symbolbild" / „Symbolfoto", da se ne stvori utisak da je to naš kafić.
8. **Pexels i Pixabay nemaju** obavezu praćenja preuzimanja koju sam našao u pročitanim stranicama licence. Njihova API pravila nisam čitao: **NIJE POTVRĐENO**.

## Šta nije nađeno / otvoreno

- Inox burr mlin sa staklenim levkom na čistoj pozadini: nema.
- Gooseneck kuvalo koje sipa tanak mlaz na čistoj pozadini: nema (KUVALO-1 stoji, bez vode).
- Stand-up pouch (kesa koja stoji) bez brenda sa ravnim dnom: KESA-1 je tačno to, ali **nije potvrđeno** da traka na vrhu radi kao rajsferšlus, a etiketa ne postoji (pravimo je sami).
- Krem glazura na **tamnom** telu koja curi: SOLJA-1 ima belu glazuru na braon telu, SOLJA-2 ima ćilibarno-krem. Obe traže prebojavanje u krem.
- Bečka pržionica sa ljudima pri radu bez problema oko saglasnosti: nema. Ostaje foto sa rukama (ONAMA-3) ili sopstveni snimak, kako predlaže `ideje/smer-2.md`.
- Korak 3 brew guide-a (Sip): nema dobre besplatne fotografije u paleti.

## Predlog za bazu znanja (`studio/znanje/`)

Ovo važi šire od jednog projekta, pa predlažem `trend-skaut`-u ili `trziste`-u novi fajl (npr. `foto-izvori.md`):
- Pravila licenci za Unsplash, Pexels i Pixabay (tabela gore), uključujući ono što licenca **ne** pokriva (brend, prepoznatljivi ljudi, umetnička dela).
- Metod bez preuzimanja: `images.unsplash.com/<foto>?fm=json` (dimenzije), `?palette=json&colors=6` (dominantne boje), `?w=360&fm=jpg` (sličica) rade bez API ključa.
- Unsplash stranice (ne CDN) blokiraju `curl`, a `WebFetch` ih čita. Sažetak koji `WebFetch` vraća je trag, jer ne vidi slike i može da pogreši par adresa i opisa. Zato svaka adresa mora da se proveri gledanjem sličice.


## Dodatak: CDN adrese za `mediji`

Samo za preuzimanje onoga što se stvarno koristi (vidi uslove iznad). Adrese Unsplash fotografija poređene su sa stranicom fotografije (sve osim KONTAKT-4, gde je adresa uzeta iz pretrage i potvrđena pregledom slike). Pexels adrese imaju predvidiv oblik `images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg` i potvrđene su pregledom slike.

| ID | Izvor | Adresa (bez parametara) | Parametri za potrebnu širinu |
|---|---|---|---|
| MLIN-1 | Unsplash | `https://images.unsplash.com/photo-1496282808562-d01e97fac01c` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| MLIN-2 | Unsplash | `https://images.unsplash.com/photo-1789009547716-bd710193c25d` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| MLIN-3 | Unsplash | `https://images.unsplash.com/photo-1739991892154-8ce8fbae2f88` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| MLIN-4 | Unsplash | `https://images.unsplash.com/photo-1701256407483-4331e8c3e6e0` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KUVALO-1 | Unsplash | `https://images.unsplash.com/photo-1559761340-1e6a341f0b51` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KUVALO-2 | Unsplash | `https://images.unsplash.com/photo-1768674150917-55b1ddf46a02` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| DRIPPER-1 | Pexels | `https://images.pexels.com/photos/2616169/pexels-photo-2616169.jpeg` | `?auto=compress&w=2400` |
| DRIPPER-2 | Pexels | `https://images.pexels.com/photos/8742029/pexels-photo-8742029.jpeg` | `?auto=compress&w=2400` |
| DRIPPER-3 | Unsplash | `https://images.unsplash.com/photo-1610874150308-a1e6f8c905d9` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| DRIPPER-4 | Unsplash | `https://images.unsplash.com/photo-1547852703-dbf36c84f766` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| DRIPPER-5 | Unsplash | `https://images.unsplash.com/photo-1620051524363-5ce1bca4ec98` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SOLJA-1 | Pexels | `https://images.pexels.com/photos/12544793/pexels-photo-12544793.jpeg` | `?auto=compress&w=2400` |
| SOLJA-2 | Unsplash | `https://images.unsplash.com/photo-1588614688492-65b7e720b334` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SOLJA-3 | Pexels | `https://images.pexels.com/photos/7009698/pexels-photo-7009698.jpeg` | `?auto=compress&w=2400` |
| SOLJA-4 | Unsplash | `https://images.unsplash.com/photo-1782351112349-a0b0806aa0ef` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SOLJA-5 | Unsplash | `https://images.unsplash.com/photo-1787379027026-932df7eab620` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KESA-1 | Unsplash | `https://images.unsplash.com/photo-1695245503558-5cdb37f49092` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KESA-2 | Unsplash | `https://images.unsplash.com/photo-1562051036-e0eea191d42f` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KESA-3 | Pexels | `https://images.pexels.com/photos/14545422/pexels-photo-14545422.jpeg` | `?auto=compress&w=2400` |
| KESA-4 | Pexels | `https://images.pexels.com/photos/7657837/pexels-photo-7657837.jpeg` | `?auto=compress&w=2400` |
| ZRNA-1 | Unsplash | `https://images.unsplash.com/photo-1587049016823-69ef9d68bd44` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ZRNA-2 | Unsplash | `https://images.unsplash.com/photo-1736813133035-6baf4762fd3d` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ZRNA-3 | Unsplash | `https://images.unsplash.com/photo-1717380046829-10602f1ff9ab` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SHOP-1 | Unsplash | `https://images.unsplash.com/photo-1550608751-d38ee4dd799a` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SHOP-2 | Unsplash | `https://images.unsplash.com/photo-1635304901720-898524afa099` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| SHOP-3 | Unsplash | `https://images.unsplash.com/photo-1780660231448-7f0aa4d236e9` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ONAMA-1 | Unsplash | `https://images.unsplash.com/photo-1777383504831-d0f3c6e0486e` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ONAMA-2 | Unsplash | `https://images.unsplash.com/photo-1773118360501-00f979fd9322` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ONAMA-3 | Unsplash | `https://images.unsplash.com/photo-1607681034540-2c46cc71896d` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| ONAMA-4 | Unsplash | `https://images.unsplash.com/photo-1680381615265-6cce996f6e4f` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| GUIDE-1 | Unsplash | `https://images.unsplash.com/photo-1753091122032-ddfb454849cc` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| GUIDE-2 | Unsplash | `https://images.unsplash.com/photo-1676600475896-dbf8ddd44f1d` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| GUIDE-3 | Unsplash | `https://images.unsplash.com/photo-1522825180917-a355ef45e880` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KONTAKT-1 | Unsplash | `https://images.unsplash.com/photo-1765045038226-43d7cd5cfd29` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KONTAKT-2 | Pexels | `https://images.pexels.com/photos/16862543/pexels-photo-16862543.jpeg` | `?auto=compress&w=2400` |
| KONTAKT-3 | Unsplash | `https://images.unsplash.com/photo-1783584732212-f3228740c739` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KONTAKT-4 | Unsplash | `https://images.unsplash.com/photo-1544038314-3a8986f60123` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KONTAKT-5 | Unsplash | `https://images.unsplash.com/photo-1783584731229-88a994486ad3` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
| KONTAKT-6 | Unsplash | `https://images.unsplash.com/photo-1567880905822-56f8e06fe630` | `?w=2400&q=85&fm=jpg` (širina po potrebi) |
