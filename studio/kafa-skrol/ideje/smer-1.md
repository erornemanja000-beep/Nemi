## Kafa sa čašom vode

**U jednoj rečenici:** MARMOR ne prodaje bečku nostalgiju, nego bečki način serviranja: mermerni sto, srebrni poslužavnik i čašu izvorske vode, a na tome služi specialty kafu današnjice.

**Potpisni trenutak:** Kad se talas kafe povuče, šolja sleti na ovalni srebrni poslužavnik na mermernom stolu, a pored nje se spusti čaša vode sa kašičicom preko ivice, baš kako Beč služi kafu.

**Raspoloženje:** smireno · precizno · gostoljubivo · Marmor `#ECE8E1`, Ader `#B7B0A6`, Mokka `#1D1714`, Kirsche `#7B2620`, Espresso `#2A1A13`, Crema `#C98A4B`, Obers `#F7F3EC` · uski debeli grotesk + meki serif

**Priča skrola** (struktura iz `analiza-videa.md`, menja se samo sloj brenda):
1. **GRIND** na boji mermera. Gore levo je logo MARMOR, a meni ima 5 stavki: Kaffee · Rösterei · Shop · Über uns · Kontakt. Iza mlina polako klizi ogromna reč MOKKA, a uz nju stoji sitna fusnota kao u rečniku („Mok·ka, der: …").
2. Zrna i mleta kafa padaju preko granice sekcija u crvenu sekciju.
3. **POUR** (Kirsche): kuvalo sipa vodu i V60 kaplje. Iza njih prolazi QUELLWASSER, a fusnota kaže da voda od 1873. stiže iz Alpa.
4. Talas boje Crema preplavi ekran, a kroz njega se kao kroz sočivo nazire šolja.
5. **SIP** (Espresso): šolja stoji na srebrnom poslužavniku pored čaše vode, a iza je MELANGE. Tri staklene kartice slete oko šolje kao jelovnik. Dugme: „Finde deine Tasse".
6. Prodavnica je na boji mermera: kese sa ovalnim etiketama i filter Filter / Espresso.
7. Über uns izgleda kao novine na drvenom držaču (Zeitungshalter), u jednom uskom stupcu. Kontakt nosi naslov „Herr Ober, bitte!".
- **Telefon:** sekcije su jedna ispod druge, sa lakšim sekvencama. Ogromne reči postaju spora traka koja klizi, a kartice se prelaze prstom. Čaša u uglu radi isto kao na desktopu.
- **Reduced motion:** po jedan miran kadar za svako poglavlje (zrna u vazduhu, V60 koji kaplje, šolja na poslužavniku). Nema pina ni talasa, nego jasan rez preko trake boje Crema. Reči miruju, a čaša je puna i tekst se pojavljuje bez animacije.

**Video i mediji:** U Blenderu je već planirano: mlin, zrna, V60, kuvalo i šolja. Dodajemo ovalni srebrni poslužavnik, čašu vode sa kašičicom (jedan miran kadar i dva stanja vode, prazna i puna), tri kese sa našim etiketama (za kartice i prodavnicu) i mermernu ploču, napravljenu proceduralno u Blenderu, bez preuzimanja tekstura. AI nije obavezan. Od klijenta nemamo ništa jer je brend izmišljen.

**Tehnika i rizici:** Staklo i voda su u Cycles-u na CPU-u spori i puni šuma. Zato je čaša miran kadar, a dopuna je CSS maska između dva rendera, bez sekvence. Srebrnom poslužavniku treba dobro okruženje za odsjaj, pa koristimo proceduralno nebo u Blenderu. Tajmer neaktivnosti ne sme da prekida čitanje: bez zvuka, najviše 3 puta po poseti, poštuje reduced motion. Fontovi su varijabilni i svode se na podskup slova za ogromne reči. **Rizik brenda:** bečki Bieder & Maier (od 2017) već priča „tradicija + moderno", ali kroz bidermajer, ilustraciju i žirafu. Mi idemo kroz materijale (mermer, srebro, voda) i čist 3D, bez Sisi, lustera i Sacher torte.

**Zašto baš ovaj klijent:** Brend je izmišljen, ali je svaki detalj stvarna bečka činjenica:
- mermerni stolovi;
- kafa na srebrnom poslužavniku sa čašom vode i kašičicom (austria.info);
- kafedžije su čašom vode pokazivale kvalitet vode iz I. Wiener Hochquellenleitung, puštene 1873, a u početku je čaša služila za kašičicu (wien.info);
- Melange.

Specialty sloj (kafa je voće, voda je skoro cela šolja, važi poreklo) i kafanski sloj sreću se upravo u vodi. Zato je potpisni detalj čaša.

### Brend (obavezni dodaci)
- **Ime: MARMOR**, „Specialty Coffee · Wien".
  - Mermerni stolovi su znak bečke kafane (wien.info: „Marmor- und Zeitungstische").
  - Mleko u kafi se „marmoriert", kao kod Melange.
  - Na engleskom asocira na *murmur*, žamor kafane. Ima 6 slova i isto se čita na DE i EN.
  - Provera 23.10.2026: nema pržionice ni kafea „Marmor" u Beču (pretraga i liste Falstaff, wien.info, Falter).
  - Rizik: u pretrazi se meša sa klesarima, zato ide uvek uz podnaslov.
- **Rezervna imena:**
  - **SIEDER**, od „Kaffeesieder", starog bečkog naziva za vlasnike kafana. Nije zauzeto, ali se rimuje sa Bieder & Maier.
  - **PIKKOLO**: u bečkoj kafani je to konobar-šegrt, a u specialty svetu „piccolo" je napitak, pa ime spaja oba sveta. Rizik: u 18. becirku postoji kafe „Il Piccolo".
- **Pozadinske reči** (svaka ima fusnotu kao u rečniku, DE/EN):
  - GRIND → **MOKKA**: bečki naziv za crnu kafu („kleiner Mokka") i ime luke al-Mukha u Jemenu, odakle je kafa krenula u svet.
  - POUR → **QUELLWASSER**: alpska izvorska voda Beča od 1873. Zbog nje uz svaku bečku kafu ide čaša vode, a filter kafa je skoro sva od vode. Duga reč klizi preko ekrana dok teče mlaz.
  - SIP → **MELANGE**: bečki klasik (mokka, mleko, pena). Reč znači i „mešavina", pa se tako zove i kućna mešavina.
- **Naslovi poglavlja ostaju GRIND / POUR / SIP.**
  - Napred je jezik specialty sveta, a iza su bečke reči, pa se dva sloja brenda vide doslovno na ekranu.
  - Nemačke reči ne prolaze kao veliki naslovi: GENIESSEN ima 9 slova i lomi raspored, a GIEẞEN traži veliko ẞ koje mnogi fontovi nemaju.
  - Nemački ide u sitni natpis („Kapitel 1 · Mahlen") i u slogan **„Mahlen. Gießen. Genießen."**, koji stoji ispod logoa i na poleđini kese.
- **Paleta, zašto se razlikuje od videa:**
  - Marmor je hladniji i svetliji od krem boje iz videa, jer je to mermer, a ne pergament.
  - Kirsche menja terakotu: to je boja ploda kafe (specialty kaže da je kafa voće) i crvenog pliša kafanskih loža.
  - Espresso je tamniji od braon boje iz videa, da bi srebro, staklo i glazura zasijali.
  - Crema je boja talasa i cena.
  - Pozadinske reči su u bojama `#CFC8BD` (GRIND), `#5E1C18` (POUR) i `#4A3024` (SIP). Obers na Kirsche ima kontrast oko 8,9:1.
- **Fontovi** (OFL, lokalno):
  - **Archivo** (varijabilna širina): ExtraCondensed Black za naslove i logo, normalna širina za tekst i natpise.
  - **Fraunces** (osa SOFT) za pozadinske reči. Rezerva je Young Serif.
- **Kesa** (250 g):
  - Mat papir boje mermera sa jednom bledom žilom. Žila je na svakoj kesi drugačija, kao na pravom mermeru.
  - **Ovalna etiketa u obliku bečkog srebrnog poslužavnika.** Oval je osnovni oblik celog brenda: logo, pilule, kartice.
  - Ime kafe je u Fraunces-u, a poreklo, obrada i visina u sitnim verzalima.
  - Traka pri dnu pokazuje stepen prženja: Crema za svetlo, Kirsche za srednje, Mokka za espresso.
  - Datum prženja je upisan rukom, kao konobarski račun.
- **Proizvodi.** Za meru cena uzeta je Kaffeefabrik Wien: 250 g košta 10,60–14,90 € (provereno 23.10.2026). Mi smo malo iznad jer smo butik.
  1. **Melange**, kućna mešavina: Brasil Cerrado Mineiro (natural) + Kolumbija Huila (washed). Lešnik, mlečna čokolada, karamel. Srednje-tamno prženje, za espresso i mleko. **11,90 €**
  2. **Hambela**: Etiopija, Guji, Hambela Wamena; washed, heirloom, oko 2.000 m. Jasmin, bergamot, bela breskva. Svetlo prženje, za filter/V60. **14,50 €**
  3. **Pink Bourbon**: Kolumbija, Huila; washed. Hibiskus, mandarina, šećerna trska. Svetlo-srednje prženje, za filter i espresso. **15,90 €**
- **Potpisni detalj koji video nema: čaša vode koja se sama dopunjava.**
  - Umesto generičkog chat balona dole desno stoji mala čaša vode. Klik na nju otvara „Herr Ober?" (kontakt i pomoć).
  - Kad gost oko 25 s ne skroluje, voda se dolije i pojavi se jedan red teksta, npr. „Lassen Sie sich Zeit. Das Wasser geht aufs Haus."
  - Osnova je bečka kafana, gde se satima sedi uz jednu kafu. UNESCO kaže da se tu „troše vreme i prostor, a na računu je samo kafa" (navod sa wien.info).

**Inspiracija:**
- Reel Enkis Web Studio (18.10.2026): struktura, opisana u `analiza-videa.md`.
- Rye Island Roastery, https://www.awwwards.com/sites/rye-island-roastery (Awwwards HM, 26.03.2026): priča i prodavnica u jednom toku, proizvod predstavljen kroz poreklo.
- Kaffeefabrik, https://www.kaffeefabrik.at/ (pregledano 23.10.2026): jasna podela Filter/Espresso i cena po kg. Odatle je i mera za cene.
- Fluid Glass, https://www.awwwards.com/sites/fluid-glass (Exo Ape, Awwwards SOTD, 30.03.2026), druga branša, arhitektonsko staklo: materijal kao glavni junak i prelaz maskom na skrol. Taj princip koristimo za staklene kartice i čašu.
- Činjenice: https://www.wien.info/de/essen-trinken/cafes/wiener-kaffeehaus-fun-facts-433154 · https://www.austria.info/de/aktivitaeten/essen-und-trinken/kaffeehauskultur
- Konkurencija koju izbegavamo: Bieder & Maier, https://www.roastmarket.de/magazin/bieder-und-maier-roesterei-oesterreichische-kaffeetradition/ (30.07.2021).
