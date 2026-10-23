# Tekstovi: POUR / PLAY · Specialty Coffee (kafa-skrol)

Tekstopisac, 23.10.2026. Osnova: `brief.md`, `analiza-videa.md`. Engleski je podrazumevani jezik, nemački je drugi (DE/EN prekidač). U svakom polju je prvo EN, pa DE.

---

## Beleške za tim (srpski)

**Brend je privremen.** „POUR / PLAY" je radno ime iz videa. `analiza-videa.md` kaže da se ime iz videa ne kopira, pa ga programer stavlja u **jednu promenljivu** (`brand.name`), da zamena bude jedan red. Imena kafa „On Repeat" i „Pause" su igra reči sa „PLAY", ali rade i bez nje („Pause" je na DE i „Kaffeepause").

**Sve je izmišljeno i označeno kao demo:** brend, kafe, farme i kooperative, adresa, telefon, radno vreme, dani prženja i rok isporuke. Cene i pravila uzeti su iz briefa:
- cene kafa su u rasponima iz tabele „Tipične cene u Austriji";
- 1 kg je oko 10 % jeftiniji po kg, po uzoru na Jonas Reindl iz briefa;
- besplatna dostava od € 45 je predlog iz briefa;
- € 4,50 ispod praga je primer Coffee Pirates iz briefa;
- kuvalo € 169 je oslonjeno na Fellow Stagg € 170 iz briefa.

Imena farmi i kooperativa su izmišljena. **Pre objave** treba proveriti da ne postoji stvaran proizvođač sa istim imenom (to nisam proverio).

**Šta fali (`[FEHLT]`):**
- cene mlina i drippera (brief nema podatak, predlažem da `trziste` da raspon);
- pravilo za MHD;
- načini plaćanja;
- dostava van Austrije;
- EN tekst dugmeta „Vertrag widerrufen";
- sadržaj Impressuma i Datenschutza.

**Format za programera:**
- Cene: DE `€ 17,90` (austrijski zapis, € ispred, zarez; kaffemik piše „€64,00/kg"), EN `€17.90`. Grundpreis uvek u istom redu kao cena: DE `€ 71,60/kg`, EN `€71.60/kg`. Kod pakovanja od 1 kg Grundpreis nije obavezan (brief, izuzetak), ali ne smeta.
- Uz svaku cenu ide „inkl. MwSt., zzgl. Versand" / „incl. VAT, plus shipping". Kaffemik piše „Inkl. Steuern", a „USt." je takođe ispravno u Austriji.
- Nelomljivi razmak (`&nbsp;`) ide u „18 g", „93 °C", „250 g", „10 %", „€ 13,50" i „1.950 m".
- Visina: DE `1.950–2.200 m`, EN `1,950–2,200 m`. Vreme `3:00` je isto na oba jezika.
- Naslove i natpise ne pisati velikim slovima u HTML-u, nego preko CSS `text-transform: uppercase` i uz `lang="de"`/`lang="en"` na `<html>`. Tako „Aufgießen" postaje „AUFGIESSEN" bez ručnog ß → SS.
- Pozadinske reči i talas su dekor: `aria-hidden="true"`, bez informacija (brief, kontrast).
- H1: „GRIND" sam nije dobar H1 za pretragu. Predlog je skriven H1 (vizuelno sakriven, čitač ga čita):
  - EN: „POUR / PLAY – specialty coffee roastery in Vienna"
  - DE: „POUR / PLAY – Kaffeerösterei für Specialty Coffee in Wien"

  Poglavlja su H2.

**Ton:** DE sa „du", kratko. Austrijski izrazi su samo tamo gde prirodno stoje:
- „Sessel" (u Austriji obična stolica) u naslovu O nama;
- „Marille" umesto „Aprikose" u notama ukusa;
- „Mokkakanne" (koristi je bečki kaffemik);
- „um € 12,15" (austrijski predlog uz cenu);
- „Sonn- und Feiertag".

Bez superlativa i bez tvrdnji koje ne možemo da dokažemo (Bio, Fairtrade, „najbolja kafa"). EN je pisan paralelno, ne kao doslovan prevod. Pravopis je US („flavor"), jer u videu na kartici piše „Flavor".

**Istraživanje (23.10.2026).** Pretrage su vratile sažetke malog modela, pa su to tragovi, ne citati.

| Šta sam tražio | Reči koje koriste prvi rezultati | Izvor |
|---|---|---|
| „Kaffeebohnen kaufen Wien Rösterei Specialty Coffee online" | „Specialty Coffee in Wien", „eigene Rösterei", „Mahlgrade", „250-, 500- oder 1.000-Gramm" | [Falter](https://www.falter.at/lokalfuehrer/die-besten-cafes-fuer-specialty-coffee), [1000things](https://www.1000thingsmagazine.com/de/a/54289/spezialitaetenkaffee-wien/) |
| „specialty coffee roastery Vienna buy beans online" | „specialty coffee", „roastery", „single origin", „blends", „online shop" | [Vienna Würstelstand](https://viennawurstelstand.com/guide/delivering-specialty-coffee-vienna/) |
| „Filterkaffee Bohnen online kaufen Österreich versandkostenfrei ab" | „Handfilter, Chemex und Filtermaschine", „ganze Bohnen", „Probierpakete", „Kostenloser Versand ab" | [roastmarket.de](https://www.roastmarket.de/kaffee/filterkaffee.html) |
| „Kaffee Abo Österreich Specialty frisch geröstet" | „Kaffee-Abo", „jederzeit kündbar", „Pausieren oder Überspringen", „2, 4 oder 6 Wochen" | [happycoffee.org](https://www.happycoffee.org/kaffee-abo/) |
| stranica proizvoda bečke pržionice (otvorena) | Mahlgrad: „Ganze Bohne", „Espresso / Siebträger", „Mokkakanne", „AeroPress", „Handfilter / V60", „Filtermaschine", „French Press"; „Grundpreis €64,00/kg"; „Inkl. Steuern. Versand wird beim Checkout berechnet" | [kaffemik HUEHUE](https://www.kaffemik.at/products/huehue) |
| „Schwanenhals Wasserkocher Handfilter 93 Grad" | „Schwanenhals", program „Handbrew" na 93 °C, opseg 90–96 °C | [Graef](https://www.graef.de/en/p/4001627003944) (uputstvo proizvođača) |
| „Harar Longberry" | izduženo zrno iz Harara; izvori se ne slažu da li je to klasa po veličini ili naziv za sortu | [Coffee Review, glossary H](https://www.coffeereview.com/coffee-glossary/h/), [Sweet Maria's](https://library.sweetmarias.com/what-ever-happened-to-ethiopian-harar-coffee/) |
| „pour over percolation vs immersion" | pour-over = perkolacija (voda jednom prolazi kroz kafu), French press = imerzija | [19grams Kaffeelexikon](https://19grams.coffee/en/blogs/kaffeelexikon/immersion-vs-percolation), [Coffee Parts](https://know.coffeeparts.com.au/glossary/immersion-vs-percolation) |
| „Röstergasse Wien" (provera demo adrese) | nema pogodaka, slične su Rögergasse (1090) i Rötzergasse (1170) | pretraga; zvanični registar ulica Beča **NEPROVERENO** |

Zaključak za SEO: u DE se traže „Kaffeerösterei Wien", „Specialty Coffee", „Kaffeebohnen", „frisch geröstet", „Handfilter", „Kaffee-Abo" i „Probierset", a u EN „specialty coffee", „roastery Vienna" i „coffee beans". Te reči su ubačene u naslove, podnaslove i meta opise.

**Pravna napomena:**
- Formulacije dugmadi „Zahlungspflichtig bestellen" i „Vertrag widerrufen" su iz briefa (FAGG).
- EN formulacije pišem po sećanju na tekst direktiva, pa su **NEPROVERENE** dok se ne potvrde na EUR-Lex-u:
  - „order with obligation to pay", Direktiva 2011/83/EU, čl. 8(2);
  - „withdraw from contract here", Direktiva (EU) 2023/2673.
- Gewährleistungslabel se ne piše sam, nego se ubacuje zvanični predložak, nepromenjen, na DE i EN.

---

## SEO

**Title (EN):** Specialty Coffee Roastery in Vienna | POUR / PLAY (49 znakova)
**Titel (DE):** Kaffeerösterei Wien · Specialty Coffee | POUR / PLAY (52 znaka)

**Meta description (EN):** Specialty coffee roasted in Vienna: whole bean or ground for espresso, filter and moka pot. Brew guide, subscription, tasting set. Concept demo. (144 znaka)
**Meta description (DE):** Specialty Coffee, frisch geröstet in Wien: ganze Bohne oder gemahlen für Espresso, Filter und Mokkakanne. Zubereitung, Abo, Probierset. Konzept-Demo. (149 znakova)

„Concept demo" / „Konzept-Demo" je namerno u opisu, da niko iz pretrage ne pomisli da je prodavnica stvarna.

---

## Header

**Logo:** POUR / PLAY
**Podnaslov logoa (EN):** Specialty Coffee · Vienna   **(DE):** Specialty Coffee · Wien
**aria-label logoa (EN):** POUR / PLAY, home   **(DE):** POUR / PLAY, Startseite

**Meni, 5 stavki:**

| # | EN | DE | Vodi na |
|---|---|---|---|
| 1 | Coffee | Kaffee | prodavnica, filter „Kaffee" |
| 2 | Subscription | Abo | pretplata |
| 3 | Brew guide | Zubereitung | brew guide |
| 4 | About | Über uns | o nama |
| 5 | Visit | Kontakt | kontakt i kafić |

**Button (EN):** Shop now   **(DE):** Zum Shop

**aria natpisi:**

| Element | EN | DE |
|---|---|---|
| pretraga (dugme) | Open search | Suche öffnen |
| polje pretrage, placeholder | Search coffee, origin or gear | Kaffee, Herkunft oder Zubehör suchen |
| pretraga bez rezultata | Nothing found for "{q}". | Nichts gefunden für „{q}". |
| korpa | Cart, {n} items (1: Cart, 1 item) | Warenkorb, {n} Artikel |
| chat balon | Open chat | Chat öffnen |
| tooltip chat balona | Questions? Ask us. | Fragen? Schreib uns. |
| meni na telefonu | Open menu / Close menu | Menü öffnen / Menü schließen |
| jezik | Language: English. Switch to Deutsch | Sprache: Deutsch. Zu English wechseln |
| preskoči na sadržaj | Skip to content | Zum Inhalt springen |

**Chat panel (demo):**
- EN: Hi! This chat is a demo. Write to hallo@pourplay.example or come by the café.
- DE: Hallo! Dieser Chat ist eine Demo. Schreib an hallo@pourplay.example oder komm im Café vorbei.

---

## Poglavlje 1 · GRIND

**Title (EN):** GRIND   **Titel (DE):** GRIND
**Subtitle / Untertitel:** EN: Section 1 · DE: Kapitel 1 · Mahlen
**Text (EN):** It all starts with a whole bean. We roast twice a week in Vienna and grind to order: for espresso, filter, French press or moka pot. Or keep it whole and grind it fresh at home. (177 znakova)
**Text (DE):** Alles beginnt mit der ganzen Bohne. Wir rösten zweimal pro Woche in Wien und mahlen erst, wenn du bestellst: für Siebträger, Filter, French Press oder Mokkakanne. Oder du mahlst selbst, frisch zu Hause. (202 znaka)
**Button:** EN: Shop beans · DE: Bohnen kaufen
**Alt / aria-label scene (EN):** Coffee grinder of steel and glass. Beans fall into the hopper, ground coffee runs out below.
**Alt / aria-label scene (DE):** Kaffeemühle aus Stahl und Glas. Bohnen fallen in den Trichter, unten rieselt gemahlener Kaffee heraus.

## Poglavlje 2 · POUR

**Title (EN):** POUR   **Titel (DE):** POUR
**Subtitle / Untertitel:** EN: Section 2 · DE: Kapitel 2 · Aufgießen
**Text (EN):** Pour-over takes its time: 18 g of coffee, water at 93 °C, three minutes. Let it bloom, pour in slow circles, then wait for the last drop. Our guide walks you through it. (169 znakova)
**Text (DE):** Filterkaffee braucht Zeit: 18 g Kaffee, Wasser mit 93 °C, drei Minuten. Erst aufquellen lassen, dann in ruhigen Kreisen gießen und auf den letzten Tropfen warten. Die Anleitung zeigt jeden Schritt. (197 znakova)
**Button:** EN: Brew guide · DE: Zur Anleitung
**Alt / aria-label scene (EN):** A gooseneck kettle pours water into a ceramic dripper on a glass carafe. Steam rises, coffee drips.
**Alt / aria-label scene (DE):** Ein Schwanenhals-Wasserkocher gießt Wasser in einen Keramik-Handfilter auf einer Glaskanne. Dampf steigt auf, Kaffee tropft.

## Poglavlje 3 · SIP

**Title (EN):** SIP   **Titel (DE):** SIP
**Subtitle / Untertitel:** EN: Section 3 · DE: Kapitel 3 · Genießen (rezerva: „Trinken")
**Text (EN):** Fruity, chocolaty or somewhere in between? Find your cup by origin, flavor or roast: from a floral Ethiopian to our house espresso. Every bag shows its roast date. (163 znaka)
**Text (DE):** Fruchtig, schokoladig oder irgendwo dazwischen? Finde deine Tasse nach Herkunft, Geschmack oder Röstung: vom blumigen Äthiopier bis zum Haus-Espresso. Auf jeder Packung steht das Röstdatum. (189 znakova)
**Button:** EN: Find your cup · DE: Finde deine Tasse
**Alt / aria-label scene (EN):** Ceramic cup with a dripping glaze, surrounded by three coffee cards.
**Alt / aria-label scene (DE):** Keramiktasse mit herablaufender Glasur, umgeben von drei Kaffeekarten.

**Kontrole karusela (sva tri poglavlja):**

| Element | EN | DE |
|---|---|---|
| strelica levo | Previous section | Vorheriges Kapitel |
| strelica desno | Next section | Nächstes Kapitel |
| tačkica | Go to section {n} of 3 | Zu Kapitel {n} von 3 |
| telefon, kartice | Swipe for more | Wischen für mehr |

---

## Tri ogromne pozadinske reči

Iste su na EN i DE, jer su dekor kao i GRIND / POUR / SIP. Pišu se kao u videu, prvo slovo veliko, ostala mala.

| Poglavlje | U videu | Naša reč | Slova | Značenje (jedna rečenica) |
|---|---|---|---|---|
| GRIND | „Lon…" | **Longberry** | 9 | Longberry je krupno, izduženo zrno arabike iz Harara u istočnoj Etiopiji. Izvori se ne slažu da li je to klasa po veličini ili naziv za stare lokalne sorte, pa na sajtu kažemo samo „dugo zrno iz Harara" ([Coffee Review](https://www.coffeereview.com/coffee-glossary/h/), [Sweet Maria's](https://library.sweetmarias.com/what-ever-happened-to-ethiopian-harar-coffee/)). |
| POUR | „Peu…are" | **Percolate** | 9 | Perkolacija je ekstrakcija u kojoj voda jednom protekne kroz sloj mlevene kafe, a upravo to radi dripper, za razliku od imerzije u French pressu ([19grams](https://19grams.coffee/en/blogs/kaffeelexikon/immersion-vs-percolation), [Coffee Parts](https://know.coffeeparts.com.au/glossary/immersion-vs-percolation)). |
| SIP | „Fro…her" | **Frother** | 7 | Frother je penilica za mleko, koja pravi penu za bečku Melange ili cappuccino, poslednji korak pre gutljaja kod kafe sa mlekom. Veza sa sajtom: On Repeat je „made for a flat white or a Melange". |

Oblik: „Pe…ate" kod Percolate liči na „Peu…are", a „Fro…her" se kod Frother poklapa slovo po slovo.

**Rezerve:**
- POUR: **Peaberry** (8 slova), okruglo zrno, jedno u plodu. Oblik je dobar, ali je smisao „zrno", a ne „voda".
- SIP: **Finish** (6 slova), ukus koji ostaje posle gutljaja. Smisao je jači, ali je reč kraća i ne liči na video.

**Fusnota uz reč (opciono, ako dizajner hoće sitan natpis kao u rečniku):**

| Reč | EN | DE |
|---|---|---|
| Longberry | a long bean from Harar, Ethiopia | lange Bohne aus Harar, Äthiopien |
| Percolate | water runs through the coffee, once | das Wasser läuft einmal durch den Kaffee |
| Frother | makes the foam for your Melange | macht den Schaum für deine Melange |

---

## SIP: staklene kartice (Origin / Flavor / Roast)

Svaka kartica je link na proizvod u prodavnici. Grundpreis stoji u istom redu kao cena.

| | Kartica 1 | Kartica 2 | Kartica 3 |
|---|---|---|---|
| **Natpis (EN / DE)** | Origin / Herkunft | Flavor / Geschmack | Roast / Röstung |
| **Podnatpis (EN)** | Where it grows | What you taste | How dark we go |
| **Podnatpis (DE)** | Wo er wächst | Was du schmeckst | Wie dunkel wir rösten |
| **Kafa** | Guji | Huila Pink Bourbon (telefon: „Pink Bourbon") | On Repeat |
| **Red (EN)** | Ethiopia · 1,950–2,200 m | Colombia · Limited lot | House blend · Medium-dark |
| **Red (DE)** | Äthiopien · 1.950–2.200 m | Kolumbien · Limitiertes Lot | Hausmischung · Mittel-dunkel |
| **Note (EN)** | Jasmine · Bergamot · White peach | Hibiscus · Pink grapefruit · Panela | Milk chocolate · Hazelnut · Caramel |
| **Note (DE)** | Jasmin · Bergamotte · Weißer Pfirsich | Hibiskus · Rosa Grapefruit · Panela | Milchschokolade · Haselnuss · Karamell |
| **Cena (EN)** | €17.90 · 250 g · €71.60/kg | €26.00 · 250 g · €104.00/kg | €13.50 · 250 g · €54.00/kg |
| **Cena (DE)** | € 17,90 · 250 g · € 71,60/kg | € 26,00 · 250 g · € 104,00/kg | € 13,50 · 250 g · € 54,00/kg |
| **Dugme (EN / DE)** | View / Ansehen | View / Ansehen | View / Ansehen |

**aria-label kartice:** EN „Guji, Ethiopia, €17.90 for 250 g. View coffee", DE „Guji, Äthiopien, € 17,90 für 250 g. Kaffee ansehen" (isto i za druge dve).

---

## Prodavnica „Find your cup"

**Title (EN):** Find your cup   **Titel (DE):** Finde deine Tasse
(varijanta B: EN „Six coffees, one for you" / DE „Sechs Kaffees, einer für dich")
**Subtitle (EN):** Roasted in Vienna every Tuesday and Friday. Whole bean or ground the way you brew.
**Untertitel (DE):** Geröstet in Wien, jeden Dienstag und Freitag. Ganze Bohne oder gemahlen, so wie du zubereitest.
**Text (EN):** Not sure where to start? Four filter coffees side by side in the tasting set.
**Text (DE):** Du weißt nicht, wo du anfangen sollst? Im Probierset stehen vier Filterkaffees nebeneinander.
**Button:** EN: Try the tasting set · DE: Zum Probierset

### Filteri

| Grupa (EN / DE) | Opcije EN | Opcije DE |
|---|---|---|
| Brew / Zubereitung | All · Espresso · Filter | Alle · Espresso · Filter |
| Flavor / Geschmack | Fruity & floral · Chocolate & nuts | Fruchtig & blumig · Schokoladig & nussig |
| Roast / Röstung | Light · Medium · Medium-dark | Hell · Mittel · Mittel-dunkel |
| Type / Kategorie | Coffee · Decaf · Equipment · Sets | Kaffee · Entkoffeiniert · Zubehör · Sets |
| Sort / Sortieren | Newest roast · Price: low to high · Price: high to low | Neueste Röstung · Preis aufsteigend · Preis absteigend |

**Ostalo:**

| Element | EN | DE |
|---|---|---|
| broj rezultata | {n} products | {n} Produkte |
| reset | Reset filters | Filter zurücksetzen |
| prazno | No coffee matches these filters. | Kein Kaffee passt zu diesen Filtern. |

Kojoj grupi ukusa pripada koja kafa:
- Fruity & floral: Guji, Nyeri, Huila Pink Bourbon, Tarrazú Honey.
- Chocolate & nuts: On Repeat, Pause, Tarrazú Honey (zbog badema).

### Natpisi na kartici proizvoda

| Polje | EN | DE |
|---|---|---|
| poreklo | Origin | Herkunft |
| obrada | Process | Aufbereitung |
| sorta | Variety | Varietät |
| visina | Altitude | Höhe |
| note | Tasting notes | Geschmack |
| za šta | Best for | Ideal für |
| prženje | Roast | Röstung |
| farma | Farm / co-op (fictional) | Farm / Kooperative (fiktiv) |
| datum prženja | Roasted on | Geröstet am |
| MHD | Best before | Mindestens haltbar bis |
| veličina | Size | Größe |
| mlevenje | Grind | Mahlgrad |
| napomena uz cenu | incl. VAT, plus shipping | inkl. MwSt., zzgl. Versand |
| dugme | Add to cart | In den Warenkorb |

- **Datum prženja (demo):** poslednji dan prženja pre posete (utorak ili petak). Može da se računa u JS-u, a kao fiksna vrednost: 20.10.2026.
- **MHD:** `[FEHLT: MHD-Regel, z. B. Röstdatum + X Monate]`. Brief kaže da MHD mora da bude dostupan najkasnije pri isporuci.

### 6 kafa

| # | Ime | Poreklo (EN / DE) | Obrada (EN / DE) | Sorta · visina | Note (EN) | Note (DE) | Za (EN / DE) | Prženje (EN / DE) | 250 g | 1 kg |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **On Repeat** · House blend / Hausmischung | Brazil, Cerrado Mineiro 60 % + Colombia, Huila 40 % / Brasilien, Cerrado Mineiro 60 % + Kolumbien, Huila 40 % | Natural + washed / Natural + gewaschen | blend | Milk chocolate · Hazelnut · Caramel | Milchschokolade · Haselnuss · Karamell | Espresso | Medium-dark / Mittel-dunkel | € 13,50 (€ 54,00/kg) | € 48,90 |
| 2 | **Guji** | Ethiopia, Oromia, Guji / Äthiopien, Oromia, Guji | Washed / Gewaschen | Heirloom (local varieties / lokale Varietäten) · 1.950–2.200 m | Jasmine · Bergamot · White peach | Jasmin · Bergamotte · Weißer Pfirsich | Filter | Light / Hell | € 17,90 (€ 71,60/kg) | € 64,90 |
| 3 | **Nyeri** | Kenya, Nyeri / Kenia, Nyeri | Washed / Gewaschen | SL28, SL34 · 1.700–1.900 m | Blackcurrant · Blood orange · Cane sugar | Schwarze Johannisbeere · Blutorange · Rohrzucker | Filter | Light / Hell | € 19,50 (€ 78,00/kg) | € 69,90 |
| 4 | **Huila Pink Bourbon** · Limited lot / Limitiertes Lot | Colombia, Huila / Kolumbien, Huila | Washed / Gewaschen | Pink Bourbon · 1.750–1.850 m | Hibiscus · Pink grapefruit · Panela | Hibiskus · Rosa Grapefruit · Panela (Vollrohrzucker) | Filter & espresso / Filter & Espresso | Light-medium / Hell-mittel | € 26,00 (€ 104,00/kg) | € 93,90 |
| 5 | **Tarrazú Honey** | Costa Rica, Tarrazú | Honey | Caturra, Catuaí · 1.600–1.800 m | Apricot · Honey · Almond | Marille · Honig · Mandel | Espresso & filter / Espresso & Filter | Medium / Mittel | € 18,50 (€ 74,00/kg) | € 66,90 |
| 6 | **Pause** · Decaf / Entkoffeiniert | Colombia, Caldas / Kolumbien, Caldas | Sugarcane decaf / Zuckerrohr-Methode | Castillo, Caturra · 1.400–1.700 m | Date · Milk chocolate · Hazelnut | Dattel · Milchschokolade · Haselnuss | Espresso & filter / Espresso & Filter | Medium / Mittel | € 19,00 (€ 76,00/kg) | € 68,90 |

EN cene u istom redosledu: €13.50 (€54.00/kg) / €48.90 · €17.90 (€71.60/kg) / €64.90 · €19.50 (€78.00/kg) / €69.90 · €26.00 (€104.00/kg) / €93.90 · €18.50 (€74.00/kg) / €66.90 · €19.00 (€76.00/kg) / €68.90.

„Marille" (a ne „Aprikose") je austrijska reč za kajsiju i prirodno stoji u bečkom shopu. Nisam je proverio u rečniku u ovoj sesiji, ali je opštepoznata.

**Farme i kooperative (fiktivne, pre objave proveriti):**
- Guji: Tesfa Hills Cooperative;
- Nyeri: Kiburu Factory;
- Huila: Finca Tres Quebradas;
- Tarrazú: Beneficio Cerro Azulejo;
- Pause: Kooperative Alto Caldas.

On Repeat nema jednu farmu.

**Kratak opis na kartici (EN / DE):**
1. **On Repeat.** EN: Our everyday espresso. Sweet and round, made for a flat white or a Melange. DE: Unser Espresso für jeden Tag. Süß und rund, gemacht für Flat White und Melange.
2. **Guji.** EN: Floral and light, almost like tea with fruit. Our pick for the pour-over recipe. DE: Blumig und leicht, fast wie Tee mit Frucht. Unser Tipp für das Handfilter-Rezept.
3. **Nyeri.** EN: Juicy, with a clear acidity. For anyone who likes their coffee lively. DE: Saftig, mit klarer Säure. Für alle, die es lebendig mögen.
4. **Huila Pink Bourbon.** EN: A rare variety with a floral, tart finish. Small lot, while it lasts. DE: Seltene Varietät mit blumig-herbem Abgang. Kleines Lot, solange es reicht.
5. **Tarrazú Honey.** EN: Some of the fruit stays on the bean while it dries. That makes it sweet, as espresso and as filter. DE: Beim Trocknen bleibt etwas Fruchtfleisch an der Bohne. Das macht ihn süß, als Espresso und als Filter.
6. **Pause.** EN: Decaffeinated with the sugarcane method. Sweet and mellow, for the cup after 6 pm. DE: Entkoffeiniert mit der Zuckerrohr-Methode. Süß und mild, für die Tasse nach 18 Uhr.

### 3 komada opreme

| # | Ime (EN / DE) | Tekst (EN) | Tekst (DE) | Cena |
|---|---|---|---|---|
| 1 | Burr Grinder / Kaffeemühle | Electric, stainless steel, glass hopper. Grinds from espresso fine to French press coarse. | Elektrisch, Edelstahl, Bohnenbehälter aus Glas. Mahlt von fein für Espresso bis grob für French Press. | `[FEHLT: Preis Mühle]` |
| 2 | Ceramic Dripper / Handfilter aus Keramik | Cone with a 60° angle, for 1–2 cups. Fits size 02 paper filters. | Kegelform mit 60°-Winkel, für 1–2 Tassen. Passt für Papierfilter Größe 02. | `[FEHLT: Preis Dripper]` |
| 3 | Gooseneck Kettle / Schwanenhals-Wasserkocher | Electric, set to the degree. Holds 93 °C while you pour. | Elektrisch, gradgenau einstellbar. Hält 93 °C, während du gießt. | € 169,00 / €169.00 |

- Ime „V60" ne koristim za naš proizvod, jer je to naziv proizvoda firme Hario (zaštićen znak, **NEPROVERENO** u registru). Opisno („dripper like a V60") može u brew guide-u, ako zatreba.
- PDV na opremu je 20 % kao podrazumevana stopa, što je po briefu **NIJE POTVRĐENO**.
- Garantielabel ne stavljamo, jer nema garancije proizvođača duže od 2 godine.

### Izbor mlevenja

**Natpis:** EN: Grind · DE: Mahlgrad

| EN | DE |
|---|---|
| Whole bean | Ganze Bohne |
| Espresso | Espresso / Siebträger |
| Filter | Filter (Handfilter & Maschine) |
| French press | French Press |
| Moka pot | Mokkakanne |

**Pomoćni tekst:**
- EN: Whole beans keep their aroma longest. We grind on the day we ship.
- DE: Ganze Bohnen halten das Aroma am längsten. Gemahlen wird am Versandtag.

**Veličina:** 250 g · 1 kg

### Dostava

**Title (EN):** Shipping & pickup   **Titel (DE):** Versand & Abholung
**Text (EN):** Free shipping within Austria from €45, otherwise €4.50. We roast on Tuesdays and Fridays and ship within one working day. Delivery in Austria takes 2–4 working days. Or pick up your order free of charge at the café in 1070 Vienna. All prices incl. VAT.
**Text (DE):** Innerhalb Österreichs versandkostenfrei ab € 45, sonst € 4,50. Wir rösten dienstags und freitags und versenden innerhalb eines Werktags. Die Lieferung in Österreich dauert 2–4 Werktage. Oder du holst deine Bestellung gratis im Café in 1070 Wien ab. Alle Preise inkl. MwSt.
**Plaćanje:** `[FEHLT: Zahlungsarten]`
**Van Austrije:** `[FEHLT: Versand nach Deutschland & EU]`
**Button:** EN: Shipping & payment · DE: Versand & Zahlung (link na stranicu)

**Traka nad prodavnicom (kratko):** EN: Free shipping in Austria from €45 · DE: Versandkostenfrei in Österreich ab € 45

### Korpa (demo)

| Element | EN | DE |
|---|---|---|
| naslov | Your cart | Dein Warenkorb |
| prazna | Your cart is empty. | Dein Warenkorb ist leer. |
| međuzbir | Subtotal | Zwischensumme |
| dostava | Shipping | Versand |
| do besplatne dostave | €{x} to free shipping | Noch € {x} bis zum Gratisversand |
| ukupno | Total incl. VAT | Gesamt inkl. MwSt. |
| dugme (onemogućeno) | Order with obligation to pay (NEPROVERENO, vidi beleške) | Zahlungspflichtig bestellen |
| natpis ispod dugmeta | Demo: no real orders. | Demo: keine echten Bestellungen. |
| toast posle „Add to cart" | Added to cart. This is a demo, so nothing will be ordered. | Im Warenkorb. Das ist eine Demo, es wird nichts bestellt. |

---

## Pretplata

**Title (EN):** Never run out of beans   **Titel (DE):** Nie mehr ohne Bohnen
(varijanta B: EN „Coffee that comes to you" / DE „Kaffee, der zu dir kommt")
**Subtitle (EN):** Fresh from the roastery, every 2 or 4 weeks.
**Untertitel (DE):** Frisch aus der Rösterei, alle 2 oder 4 Wochen.

**Opcija 1, EN „Your coffee" / DE „Dein Kaffee":**
- EN: Pick any coffee and grind, 1 to 3 bags of 250 g, every 2 or 4 weeks. You save 10 % on every delivery. For example, On Repeat for €12.15 instead of €13.50 (€48.60/kg).
- DE: Wähle Kaffee und Mahlgrad, 1 bis 3 Packungen à 250 g, alle 2 oder 4 Wochen. Du sparst 10 % bei jeder Lieferung. Zum Beispiel On Repeat um € 12,15 statt € 13,50 (€ 48,60/kg).

**Opcija 2, EN „Surprise me" / DE „Überrasch mich":**
- EN: Every 4 weeks we send two different coffees we're excited about, 2 × 250 g, with a card on how to brew them. €38.00 per delivery (€76.00/kg), plus €4.50 shipping.
- DE: Alle 4 Wochen schicken wir dir zwei verschiedene Kaffees, die uns gerade begeistern, 2 × 250 g, mit einer Karte zur Zubereitung. € 38,00 pro Lieferung (€ 76,00/kg), zzgl. € 4,50 Versand.

**Uslovi:**
- EN: Pause, skip or cancel before any delivery. You'll see price and rhythm again before you pay.
- DE: Pausieren, überspringen oder kündigen geht vor jeder Lieferung. Preis und Rhythmus siehst du vor dem Bezahlen noch einmal.
- Pravila otkaza po FAGG brief označava kao **NIJE POTVRĐENO**, pa ovo proverava klijent.

**Poklon:**
- EN: As a gift: 3, 6 or 12 deliveries of Surprise me, paid once, ends by itself. 3 deliveries €127.50, 6 deliveries €255.00, 12 deliveries €510.00, shipping included in the price.
- DE: Als Geschenk: 3, 6 oder 12 Lieferungen „Überrasch mich", einmal bezahlt, endet von selbst. 3 Lieferungen € 127,50, 6 Lieferungen € 255,00, 12 Lieferungen € 510,00, Versand im Preis enthalten.
- Račun: (€ 38,00 + € 4,50) × broj isporuka. „Versand im Preis enthalten" ovde samo znači da je dostava već uračunata, ne da je besplatna.

**Button:** EN: Start a subscription · DE: Abo starten   |   EN: Give as a gift · DE: Verschenken

## Probierset

**Title (EN):** Not sure yet? Try four.   **Titel (DE):** Noch unsicher? Probier vier.
**Subtitle (EN):** Tasting set: 4 × 100 g filter coffee
**Untertitel (DE):** Probierset: 4 × 100 g Filterkaffee
**Text (EN):** Guji, Nyeri, Huila Pink Bourbon and Tarrazú Honey side by side, with a card for your notes. Brew them one after another and you'll know what you like. €29.00 (€72.50/kg), incl. VAT, plus shipping.
**Text (DE):** Guji, Nyeri, Huila Pink Bourbon und Tarrazú Honey nebeneinander, mit einer Karte für deine Notizen. Brüh sie nacheinander, dann weißt du, was dir schmeckt. € 29,00 (€ 72,50/kg), inkl. MwSt., zzgl. Versand.
**Button:** EN: Add tasting set · DE: Probierset in den Warenkorb

Cena je oslonjena na GOTA Sample Set € 29 iz briefa. Kafe iz seta pojedinačno vrede oko € 32,80 za 400 g, IZRAČUNATO.

---

## O nama

**Title (EN):** A roastery with chairs   **Titel (DE):** Eine Rösterei mit Sesseln
(varijanta B: EN „Roasted behind the counter" / DE „Geröstet hinter der Theke")
**Subtitle (EN):** Small roastery, café up front.
**Untertitel (DE):** Kleine Rösterei, vorne ein Café.
**Text (EN):** POUR / PLAY is a small roastery with a café in Vienna's 7th district. Our roaster sits right behind the counter, so you can watch the beans turn brown while your coffee cools. In Vienna you stay as long as your cup lasts, often longer. We're fine with that. On every bag you'll find the farm, the altitude, the process and the day we roasted it.
**Text (DE):** POUR / PLAY ist eine kleine Rösterei mit Café im 7. Bezirk. Die Röstmaschine steht gleich hinter der Theke: Du siehst, wie die Bohnen braun werden, während dein Kaffee abkühlt. In Wien bleibt man sitzen, solange die Tasse reicht, oft länger. Uns ist das recht. Auf jeder Packung stehen Farm, Höhe, Aufbereitung und der Tag, an dem wir geröstet haben.
**Demo red (EN):** Concept: the brand, café and farms are made up.
**Demo red (DE):** Konzept: Marke, Café und Farmen sind erfunden.
**Button:** EN: Visit the café · DE: Zum Café

„Sessel" je u Austriji obična stolica, pa naslov zvuči bečki. Na nemačkom iz Nemačke bi zvučao kao „fotelja", što takođe nije loše.

---

## Brew guide

**Title (EN):** Three steps, three minutes   **Titel (DE):** Drei Schritte, drei Minuten
(telefon: EN „3 steps, 3 minutes" / DE „3 Schritte, 3 Minuten")
**Subtitle (EN):** Pour-over for one big cup: 18 g coffee, 288 g water (1:16), 93 °C.
**Untertitel (DE):** Handfilter für eine große Tasse: 18 g Kaffee, 288 g Wasser (1:16), 93 °C.
**Treba ti (EN):** Dripper, paper filter, scale, kettle, timer.
**Du brauchst (DE):** Handfilter, Papierfilter, Waage, Wasserkocher, Timer.

| Korak | EN | DE |
|---|---|---|
| **1 · Grind / Mahlen** | Grind 18 g of coffee medium-fine, about like table salt. Rinse the paper filter with hot water and pour that water away. | 18 g Kaffee mittelfein mahlen, etwa wie Speisesalz. Den Papierfilter mit heißem Wasser ausspülen und das Wasser weggießen. |
| **2 · Pour / Aufgießen** | Start the timer. Pour 50 g of water at 93 °C and let it bloom for 45 seconds. Then pour slowly in circles until the scale shows 288 g. | Timer starten. 50 g Wasser mit 93 °C aufgießen und 45 Sekunden aufquellen lassen. Dann langsam in Kreisen gießen, bis die Waage 288 g zeigt. |
| **3 · Sip / Genießen** | Let it drip through. At about 3:00 it's done. Swirl the carafe once and pour. | Durchlaufen lassen. Nach etwa 3:00 ist er fertig. Kanne einmal schwenken und einschenken. |

**Savet (EN):** Too sour? Grind finer. Too bitter? Grind coarser.
**Tipp (DE):** Zu sauer? Feiner mahlen. Zu bitter? Gröber mahlen.
**Preporuka (EN):** Works well with Guji, Nyeri and Tarrazú Honey.
**Empfehlung (DE):** Passt gut zu Guji, Nyeri und Tarrazú Honey.
**Button:** EN: Shop filter coffee · DE: Filterkaffee ansehen

Izvori:
- Odnos 1:16 je iz briefa (Coffee Pirates), a 18 × 16 = 288 g.
- 93 °C je u opsegu 90–96 °C iz uputstva proizvođača kuvala ([Graef](https://www.graef.de/en/p/4001627003944)). To je proizvođač, ne nezavisan izvor, ali opseg se ovde samo koristi kao recept.
- Bloom 50 g / 45 s je uobičajen recept, a ne činjenica koju treba citirati.

---

## Kontakt

**Title (EN):** Come by   **Titel (DE):** Komm vorbei
(varijanta B: EN „Coffee at the roastery" / DE „Kaffee in der Rösterei")
**Subtitle (EN):** Café, beans to go and cupping in 1070 Vienna.
**Untertitel (DE):** Café, Bohnen zum Mitnehmen und Cupping in 1070 Wien.

**Adresa:** Röstergasse 18, 1070 Wien
- EN: (Demo address, this street doesn't exist.)
- DE: (Demo-Adresse, diese Straße gibt es nicht.)
- Pretraga nije našla „Röstergasse" u Beču, ali zvanični registar ulica nisam proverio.

**Café (EN):** Mon–Fri 8:00–18:00 · Sat 9:00–17:00 · Sun & public holidays closed
**Café (DE):** Mo–Fr 8–18 Uhr · Sa 9–17 Uhr · Sonn- und Feiertag geschlossen

**Prženje:**
- EN: We roast on Tuesdays and Fridays. Come by in the morning and watch.
- DE: Wir rösten dienstags und freitags. Komm am Vormittag vorbei und schau zu.

**Cupping:**
- EN: First Saturday of the month, 10:00, €29 per person. Book by email.
- DE: Jeden ersten Samstag im Monat, 10 Uhr, € 29 pro Person. Anmeldung per Mail.
- Cena je po uzoru na kaffemik cupping € 29 iz briefa.

**E-mail:** hallo@pourplay.example (domen `.example` je rezervisan, pa poruka ne stiže nikome)
**Telefon:** +43 1 000 00 00 (Demo)
**Za firme:**
- EN: For offices and restaurants: wholesale@pourplay.example
- DE: Für Büros und Gastro: wholesale@pourplay.example

**Button:** EN: Write to us · DE: Schreib uns (mailto)

Sve ovde (adresa, radno vreme, dani prženja, termin cupping-a, telefon) je izmišljeno za demo.

---

## Footer

**Kolone:**

| Kolona (EN / DE) | Linkovi EN | Linkovi DE |
|---|---|---|
| Shop / Shop | Coffee · Equipment · Subscription · Tasting set | Kaffee · Zubehör · Abo · Probierset |
| POUR / PLAY | About · Brew guide · Café & contact · Wholesale | Über uns · Zubereitung · Café & Kontakt · Für Büros & Gastro |
| Legal / Rechtliches | Imprint · Privacy policy · Terms · Shipping & payment · Right of withdrawal · Cookie settings | Impressum · Datenschutz · AGB · Versand & Zahlung · Widerrufsrecht · Cookie-Einstellungen |

**Dugme za opoziv ugovora:**
- DE: Vertrag widerrufen (tekst iz briefa, § 13a FAGG)
- EN: `[FEHLT: EN-Text]`. Predlog je „Withdraw from contract here" (Direktiva (EU) 2023/2673), **NEPROVERENO**.

**Gewährleistungslabel:** `[Zvanični predložak, nepromenjen, u boji, DE i EN. Ne formulišemo sami.]`

**Newsletter:**
**Title (EN):** New coffees, once a month   **Titel (DE):** Neue Kaffees, einmal im Monat
**Polje:** EN: Email · DE: E-Mail (jedino obavezno polje)
**Kućica, nije unapred štiklirana (EN):** Yes, I'd like to get the newsletter. I can unsubscribe at any time. More in the privacy policy.
**Kućica, nije unapred štiklirana (DE):** Ja, ich möchte den Newsletter bekommen. Ich kann mich jederzeit abmelden. Mehr dazu im Datenschutz.
**Button:** EN: Sign up · DE: Anmelden
**Demo red:** EN: Demo: nothing is sent. · DE: Demo: Es wird nichts verschickt.

Pravila iz briefa: posebna kućica, odvojeno od kupovine, uz napomenu o opozivu. Tekst saglasnosti proverava klijent.

**Napomena o demou (stalno vidljiva, u footeru i u traci nad prodavnicom):**
- DE: Konzept / Demo — kein echter Shop. Marke, Kaffees, Farmen, Adresse und Preise sind erfunden.
- EN: Concept / demo — not a real shop. Brand, coffees, farms, address and prices are made up.

**Copyright:** © 2026 POUR / PLAY (Konzept / Concept)
**Prekidač jezika:** DE · EN

---

## Impressum i Datenschutz: šta fali (ne pišem, proverava klijent)

**Impressum** (spisak iz briefa: ECG § 5, UGB § 14, FAGG):
- `[FEHLT]` firma kako je upisana;
- `[FEHLT]` ladungsfähige adresa (demo adresa iz Kontakta nije stvarna);
- `[FEHLT]` e-mail i telefon (za webshop oba);
- `[FEHLT]` Firmenbuchnummer i sud;
- `[FEHLT]` UID;
- `[FEHLT]` nadležni organ;
- `[FEHLT]` komora;
- `[FEHLT]` GewO kao primenljivi propis;
- `[FEHLT]` Offenlegung po MedienG § 25 (šta tačno, brief: **NIJE POTVRĐENO**);
- `[FEHLT]` izjava o vansudskom rešavanju sporova (bez linka na OS-platformu, ukinuta je 20.6.2025).

**Datenschutz:**
- `[FEHLT]` rukovalac;
- `[FEHLT]` svrhe obrade;
- `[FEHLT]` kolačići (predlog iz briefa: samo neophodni, bez analitike);
- `[FEHLT]` newsletter i opoziv saglasnosti;
- `[FEHLT]` prava korisnika;
- `[FEHLT]` Datenschutzbehörde.

**Ostalo:**
- `[FEHLT]` AGB;
- `[FEHLT]` Widerrufsbelehrung i Muster-Widerrufsformular (nepromenjen);
- `[FEHLT]` informacije po ECG § 9 (koraci do ugovora, ispravka grešaka, jezici).

Za maketu bi svaka stranica mogla da počne redom „Konzept / Demo — kein echter Shop". Sadržaj ne izmišljam.

---

## Telefon (390 px): kraće verzije

| Gde | Dugo | Kratko |
|---|---|---|
| kartica 2 u SIP-u | Huila Pink Bourbon | Pink Bourbon |
| brew guide | Three steps, three minutes / Drei Schritte, drei Minuten | 3 steps, 3 minutes / 3 Schritte, 3 Minuten |
| probierset | Not sure yet? Try four. / Noch unsicher? Probier vier. | Try four. / Probier vier. |
| footer, B2B | Für Büros & Gastro | Für Firmen |
| meni | 5 stavki | ide u meni na dugme („Menu" / „Menü"), „Shop now" ostaje vidljiv |
| pozadinske reči | Longberry, Percolate (9 slova) | smeju da izađu van ekrana, jer su dekor; ne prelamati ih u dva reda |

Tekstovi poglavlja (do 202 znaka) staju u 5–6 redova na 390 px pri 16 px. Ako dizajner smanji prostor pored predmeta, DE tekst GRIND može bez poslednje rečenice („Oder du mahlst selbst, frisch zu Hause."), pa ima 162 znaka.
