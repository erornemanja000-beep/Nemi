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

---

# Dopune za izradu (talas 1)

Tekstopisac, 23.10.2026, zadatak Z3 iz `plan-izrade.md`. Postojeći tekst iznad se ne menja. Gde se dopuna i stari tekst razlikuju, piše šta važi.

## Beleške za tim (srpski)

**Osnova:**
- `brief.md`, `plan-izrade.md` (sa „Odlukama direktora posle plana"), `izvori.md`, `fotografije.md` i `scripts/blender/kafa/bags.py` (boje kesa);
- `mockup.html` (čip „Demo", dugme „+", datum na kartici);
- licence fontova: `sajt/src/assets/fonts/OFL-*.txt` i `KafaSkrol/node_modules/@fontsource-variable/archivo/LICENSE`.

Sve fotografije iz `KafaSkrol/public/media/photos/*-sm.webp` sam pogledao, pa alt tekstovi opisuju ono što se stvarno vidi na slikama.

**Redosled:** kao u ostatku fajla, prvo EN pa DE, jer je EN podrazumevani jezik sajta.

**Ime brenda** se ne piše u ovom odeljku. Gde treba, stoji `{brand}`, a ostale oznake su `{n}`, `{q}`, `{name}`, `{size}` i `{date}`.

**Šta sam primetio na fotografijama (za direktora i `recenzent`-a):**
- `onama-1` i `onama-2` ne prikazuju bubanj (kako piše u `izvori.md`), nego **sito za hlađenje**: okrugla posuda sa rupičastim dnom i mešalicom. U alt tekstu zato piše „cooling tray" / „Kühlsieb".
- `guide-2`: na displeju vage piše **330** (i tajmer 00:18), a recept kaže 288 g. Dripper ima **ravno dno** i talasasti filter, a naš proizvod je konus od 60°. Za simboličnu fotografiju to je sitnica, ali pažljiv gost može da primeti. Alt tekst ne pominje brojeve.
- `guide-1` prikazuje **cela zrna** na vagi, a korak 1 je „Mahlen". Fotografija i dalje odgovara koraku, jer se zrna mere pre mlevenja.
- Fotografije u O nama su stvarne pržionice (ONAMA-2 je po `fotografije.md` snimljena u Indoneziji), a tekst kaže „naša pržionica". To pokriva demo red ispod teksta. Ako direktor želi da bude strože, i tamo može da stoji „Symbolbild", isto kao u kontaktu.
- Alt SIP scene iz gornjeg dela fajla („…surrounded by three coffee cards") opisuje celu scenu. Poster (S64) prikazuje samo šolju, a kartice su HTML i čitač ih ionako čita. Za poster važi alt iz tabele ispod (B3).

**EUR-Lex:** nijedna stranica nije mogla da se otvori. Detalji su u odeljku 6, a obe formulacije ostaju **NEPROVERENE**.

---

## 1. Fotografije i mediji

### 1a. Alt tekstovi fotografija

Fotografije su iz „Odluka direktora posle plana", tačka 5. KONTAKT-1 je odbačen, pa fajl `kontakt-1` sadrži fotografiju KONTAKT-2. Pozadinske slike prodavnice su dekor i dobijaju `alt=""`. Njihov alt ispod važi samo ako se upotrebe kao sadržaj.

| Fajl | Gde | Alt (EN) | Alt (DE) |
|---|---|---|---|
| `shop-1` | prodavnica | A row of glass jars with clip lids, full of roasted coffee beans, on a dark background. Only the front jar is sharp. | Eine Reihe Gläser mit Bügelverschluss voller gerösteter Kaffeebohnen vor dunklem Hintergrund. Nur das vorderste ist scharf. |
| `shop-bg-1` | prodavnica, pozadina | `alt=""` (rezerva: A heap of roasted coffee beans on a cream background.) | `alt=""` (rezerva: Ein Häufchen gerösteter Kaffeebohnen auf cremefarbenem Grund.) |
| `shop-bg-2` | prodavnica, pozadina | `alt=""` (rezerva: Roasted coffee beans scattered on a cream surface, seen from above.) | `alt=""` (rezerva: Geröstete Kaffeebohnen, locker verstreut auf hellem Grund, von oben.) |
| `onama-1` | O nama | Freshly roasted beans in the round cooling tray of a roaster. A steel arm stirs them over the perforated floor. | Frisch geröstete Bohnen im runden Kühlsieb einer Röstmaschine. Ein Rührarm aus Stahl bewegt sie über den gelochten Boden. |
| `onama-2` | O nama | Close-up of roasted beans in a roaster's cooling tray, with a steel stirring arm passing through. | Nahaufnahme: geröstete Bohnen im Kühlsieb einer Röstmaschine, ein Rührarm aus Stahl zieht hindurch. |
| `guide-1` | Brew guide, korak 1 | Whole roasted beans in a white ceramic dosing cup on a black scale. A dark grinder stands next to it. | Ganze geröstete Bohnen in einem weißen Dosierbecher aus Keramik auf einer schwarzen Waage. Daneben steht eine dunkle Kaffeemühle. |
| `guide-2` | Brew guide, korak 2 | From above: a white dripper with a pleated paper filter on a digital scale, the wet grounds blooming. Next to it, a wooden scoop of ground coffee. | Von oben: ein weißer Handfilter mit gefaltetem Papierfilter auf einer digitalen Waage, das nasse Kaffeemehl quillt auf. Daneben ein Holzlöffel mit Kaffeemehl. |
| SIP poster | Brew guide, korak 3 | A ceramic cup with a dripping glaze. | Eine Keramiktasse mit herablaufender Glasur. |
| `kontakt-1` (izvor KONTAKT-2) | Kontakt | An empty café courtyard in Vienna after rain: white chairs and tables, a folded striped parasol, wet paving stones. | Ein leerer Gastgarten in einem Wiener Innenhof nach dem Regen: weiße Stühle und Tische, ein zusammengeklappter gestreifter Sonnenschirm, nasses Pflaster. |

- Za „Beč" na `kontakt-1` izvor je stranica fotografije na Pexels-u, kako piše u `izvori.md` i `fotografije.md`.
- „Gastgarten" je austrijska reč za baštu lokala. „Schanigarten" je samo bašta na trotoaru, pa ovde ne pristaje.
- Para (`steam-cup-a`, `steam-cup-b`) je dekor: `<video aria-hidden="true">`, bez alt teksta.

### 1b. Natpis „Symbolbild"

Plan navodi KONTAKT-1 i KONTAKT-2, ali na sajtu ostaje samo jedna fotografija (`kontakt-1`, izvor KONTAKT-2), pa natpis ide samo uz nju.

| Gde | EN | DE |
|---|---|---|
| čip na uglu fotografije | Illustrative photo | Symbolbild |
| `figcaption` ispod fotografije | Illustrative photo: a café courtyard in Vienna. Not our café. | Symbolbild: Gastgarten in einem Wiener Innenhof. Nicht unser Café. |

„Symbolic image" iz plana je doslovan prevod i na engleskom se retko koristi. Prirodnije je „Illustrative photo". Ako direktor želi da EN prati plan, rezerva je „Symbolic image".

### 1c. Kese (3 rendera)

Boje su iz `bags.py` i privremene su. Posle Z4 (etiketa) treba ih uskladiti, jer u alt tekstu mora da piše boja koja se stvarno vidi. Na etiketi po Z4 stoje brend, „Specialty Coffee · Wien", „250 g" i „Demo", bez imena kafe.

| Fajl | Alt (EN) | Alt (DE) |
|---|---|---|
| `kesa-origin` | Stand-up coffee bag, 250 g, cream with a coral-red label. | Stehende Kaffeepackung, 250 g, cremefarben mit korallenrotem Etikett. |
| `kesa-flavor` | Stand-up coffee bag, 250 g, beige with a turquoise wave and a blue stripe. | Stehende Kaffeepackung, 250 g, beige mit türkisfarbener Welle und blauem Streifen. |
| `kesa-roast` | Stand-up coffee bag, 250 g, peach-pink with salmon spots and a light arc. | Stehende Kaffeepackung, 250 g, pfirsichrosa mit lachsfarbenen Flecken und hellem Bogen. |

**Kako se koristi:**
- **SIP kartica i kartica u prodavnici:** `alt=""`, isto kao `aria-hidden` u `mockup.html`. Ime kafe već stoji u naslovu kartice, a pošto 6 kafa deli 3 kese, alt sa bojom bi samo ponavljao isto.
- **Modal proizvoda (velika slika):** EN „{name}, 250 g bag", DE „{name}, Packung à 250 g".
- **CSS kesa (rezerva):** `aria-hidden="true"`.

### 1d. Oprema (3 opciona Blender snimka)

Snimci još ne postoje. Alt tekst je napisan po opisu proizvoda i scenama, pa ga treba proveriti kad render stigne (materijal, boja, da li je bokal u kadru). CSS silueta kao rezerva je `aria-hidden="true"`.

| Fajl | Alt (EN) | Alt (DE) |
|---|---|---|
| `gear-grinder` | Electric burr grinder in stainless steel with a glass hopper. | Elektrische Kaffeemühle aus Edelstahl mit Bohnenbehälter aus Glas. |
| `gear-dripper` | Ceramic cone dripper on a glass carafe. | Kegelförmiger Handfilter aus Keramik auf einer Glaskanne. |
| `gear-kettle` | Electric gooseneck kettle with a long, thin spout, on its base. | Elektrischer Schwanenhals-Wasserkocher mit langem, dünnem Ausguss, auf dem Sockel. |

Ako snimak drippera prikazuje i bokal, kartica mora da kaže da li je bokal uključen u kupovinu. Toga nema ni u briefu ni u repou: `[FEHLT: Lieferumfang Dripper (Glaskanne ja/nein)]`.

---

## 2. Stranica Credits (`/credits`)

**Title (EN):** Credits & licenses   **Titel (DE):** Quellen & Lizenzen
**Subtitle (EN):** Who made the photos, video and fonts.
**Untertitel (DE):** Wer die Fotos, das Video und die Schriften gemacht hat.
**Text (EN):** Photos, video and fonts on this concept site come from free sources. The photo and video licenses don't ask for credit, but we give it anyway. The fonts are under the SIL Open Font License, and the license texts are linked below.
**Text (DE):** Fotos, Video und Schriften auf dieser Konzeptseite stammen aus freien Quellen. Für Fotos und Video verlangen die Lizenzen keine Nennung, wir nennen sie trotzdem. Die Schriften stehen unter der SIL Open Font License, die Lizenztexte findest du unten.
**Button:** EN: Back to the start · DE: Zurück zur Startseite

**Link u footeru:** EN „Credits" · DE „Quellen & Lizenzen".

**Nazivi kolona:**

| EN | DE |
|---|---|
| Photo | Foto |
| Author | Urheber |
| Source | Quelle |
| License | Lizenz |
| Used in (opciono) | Verwendet in (opciono) |

**Napomena iznad tabele:** EN „All photos are color-adjusted for this site, some are cropped." · DE „Alle Fotos sind für diese Seite farblich angepasst, manche zugeschnitten."

**Redovi** (autor, link i licenca prepisani iz `izvori.md`; link u koloni „Source" ide na stranicu fotografije):

| Fajl | Photo (EN) | Foto (DE) | Author / Urheber | Source / Quelle | License / Lizenz |
|---|---|---|---|---|---|
| `shop-1` | Coffee beans in glass jars · Shop | Kaffeebohnen in Gläsern · Shop | Clint Bustrillos | Unsplash | Unsplash License |
| `shop-bg-1` | Heap of coffee beans · Shop background | Häufchen Kaffeebohnen · Shop-Hintergrund | Cemrecan Yurtman | Unsplash | Unsplash License |
| `shop-bg-2` | Scattered coffee beans · Shop background | Verstreute Kaffeebohnen · Shop-Hintergrund | Mockup Graphics | Unsplash | Unsplash License |
| `onama-1` | Beans in a roaster's cooling tray · About | Bohnen im Kühlsieb · Über uns | Khanh Do | Unsplash | Unsplash License |
| `onama-2` | Stirring arm in roasted beans · About | Rührarm in gerösteten Bohnen · Über uns | Ichsan Chairul | Unsplash | Unsplash License |
| `guide-1` | Beans on a scale · Brew guide, step 1 | Bohnen auf der Waage · Zubereitung, Schritt 1 | User_Pascal | Unsplash | Unsplash License |
| `guide-2` | Dripper on a scale · Brew guide, step 2 | Handfilter auf der Waage · Zubereitung, Schritt 2 | Jason An | Unsplash | Unsplash License |
| `kontakt-1` | Café courtyard in Vienna (illustrative photo) · Visit | Gastgarten in Wien (Symbolbild) · Kontakt | Anna Holodna | Pexels | Pexels License |

**Red o snimku pare:**

| Polje | EN | DE |
|---|---|---|
| Photo / Foto | Steam over a cup (video, edited) · Pour, Sip | Dampf über einer Tasse (Video, bearbeitet) · Pour, Sip |
| Author / Urheber | Mixkit | Mixkit |
| Source / Quelle | Mixkit: „Demonstration video of a steaming cup of coffee" (originalni naslov, ne prevodi se) | isto |
| License / Lizenz | Mixkit Stock Video Free License | Mixkit Stock Video Free License |
| napomena | Cropped, background removed, looped, no sound. | Zugeschnitten, Hintergrund entfernt, als Endlosschleife, ohne Ton. |

Link: https://mixkit.co/free-stock-video/demonstration-video-of-a-steaming-cup-of-coffee-43935/ (licenca „Free", ne „Restricted", provereno 23.10.2026 po `izvori.md`).

**Red o fontovima:**
- EN: Fonts: Archivo, Fraunces and Figtree, under the SIL Open Font License, Version 1.1. © The Archivo Project Authors, The Fraunces Project Authors, The Figtree Project Authors.
- DE: Schriften: Archivo, Fraunces und Figtree, unter der SIL Open Font License, Version 1.1. © The Archivo Project Authors, The Fraunces Project Authors, The Figtree Project Authors.
- Linkovi: EN „License text: Archivo · Fraunces · Figtree" · DE „Lizenztext: Archivo · Fraunces · Figtree". Vode na `/licenses/OFL-Archivo.txt`, `/licenses/OFL-Fraunces.txt` i `/licenses/OFL-Figtree.txt`.
- Imena autora su iz prvog reda licenci u repou (`Copyright 2020 The Archivo Project Authors` i ostali).

**Red o 3D scenama:**
- EN: 3D scenes and coffee bags: our own renders, made in Blender.
- DE: 3D-Szenen und Packungen: eigene Renderings, gemacht mit Blender.

Dok važi `placeholder: true` u bilo kom `seq.json`, iza toga ide dodatak: EN „Until the final renders are in, you see placeholders." · DE „Bis die fertigen Renderings da sind, siehst du Platzhalter."

---

## 3. Pravne stranice (demo stub)

Ovo su podrazumevana rešenja iz otvorenog pitanja 8, bez izmišljenog sadržaja. Svaka stranica ima isti uvod i spisak naslova. Spiskovi su iz `[FEHLT]` liste u gornjem delu fajla i iz briefa.

Na stranici se ne prikazuje doslovno `[FEHLT]`, nego naslov sa čipom: EN „not in demo" · DE „nicht in der Demo". `[FEHLT]` ostaje samo u ovom fajlu, kao oznaka za klijenta.

**Zajedničko za svih šest stranica:**
- **Untertitel / Subtitle:** EN „Concept / demo — not a real shop." · DE „Konzept / Demo — kein echter Shop."
- **Text (EN):** In a real shop, this page holds the full legal text. We don't make up legal details, so here you only see what it would cover.
- **Text (DE):** Im echten Shop steht hier der vollständige Rechtstext. Rechtliche Angaben erfinden wir nicht. Hier siehst du nur, was dazugehört.
- **Naslov spiska:** EN „What goes here" · DE „Was hier hingehört"
- **Button:** EN: Back to the start · DE: Zurück zur Startseite

**Naslov kartice pregledača** (`document.title`, do 60 znakova):

| Ruta | EN | DE |
|---|---|---|
| `/impressum` | Imprint \| {brand} | Impressum \| {brand} |
| `/datenschutz` | Privacy policy \| {brand} | Datenschutz \| {brand} |
| `/agb` | Terms \| {brand} | AGB \| {brand} |
| `/versand` | Shipping & payment \| {brand} | Versand & Zahlung \| {brand} |
| `/widerruf` | Right of withdrawal \| {brand} | Widerrufsrecht \| {brand} |
| `/cookies` | Cookies \| {brand} | Cookies \| {brand} |
| `/credits` | Credits & licenses \| {brand} | Quellen & Lizenzen \| {brand} |

### Impressum
**Title (EN):** Imprint   **Titel (DE):** Impressum

| EN | DE | Oznaka |
|---|---|---|
| Company name (as registered) | Firma (laut Firmenbuch) | `[FEHLT]` |
| Address for service | Ladungsfähige Anschrift | `[FEHLT]` (demo adresa nije stvarna) |
| Email and phone | E-Mail und Telefon | `[FEHLT]` |
| Company register number and court | Firmenbuchnummer und Firmenbuchgericht | `[FEHLT]` |
| VAT ID (UID) | UID-Nummer | `[FEHLT]` |
| Supervisory authority | Aufsichtsbehörde | `[FEHLT]` |
| Chamber membership | Kammerzugehörigkeit | `[FEHLT]` |
| Applicable rules (Trade Regulation Act, GewO) | Anwendbare Rechtsvorschriften (GewO) | `[FEHLT]` |
| Disclosure under § 25 Media Act | Offenlegung nach § 25 MedienG | `[FEHLT]` (brief: NIJE POTVRĐENO) |
| Out-of-court dispute resolution | Außergerichtliche Streitbeilegung | `[FEHLT]` (bez linka na OS-platformu) |

### Datenschutz
**Title (EN):** Privacy policy   **Titel (DE):** Datenschutz
(podnaslov ispod naslova, ako dizajn ima mesta: DE „Datenschutzerklärung")

| EN | DE | Oznaka |
|---|---|---|
| Controller | Verantwortlicher | `[FEHLT]` |
| Purposes of processing | Zwecke der Verarbeitung | `[FEHLT]` |
| Cookies and local storage | Cookies und lokale Speicherung | vidi stranicu Cookies |
| Newsletter and withdrawing consent | Newsletter und Widerruf der Einwilligung | `[FEHLT]` |
| Your rights | Deine Rechte | `[FEHLT]` |
| Complaints to the Data Protection Authority | Beschwerde bei der Datenschutzbehörde | `[FEHLT]` |
| Hosting and server logs | Hosting und Server-Logs | `[FEHLT: Hosting (Netlify) und Server-Logs]` |

Netlify je iz repoa (`CLAUDE.md`). Šta Netlify beleži u logovima, to nisam proveravao, pa je i to `[FEHLT]`. Ovaj red nema u starom spisku i predlažem da se doda.

**Demo red (tačan danas, po planu):**
- EN: In this demo, forms don't send anything. Language and cart stay in your browser.
- DE: In dieser Demo senden Formulare nichts ab. Sprache und Warenkorb bleiben in deinem Browser.

### AGB
**Title (EN):** Terms   **Titel (DE):** AGB
**Untertitel / Subtitle:** EN „Terms and conditions" · DE „Allgemeine Geschäftsbedingungen". Na 390 px je dugačka reč samo u podnaslovu, uz `hyphens: auto` i `lang="de"`.

| EN | DE | Oznaka |
|---|---|---|
| Terms and conditions | Allgemeine Geschäftsbedingungen | `[FEHLT: AGB]` |
| How the contract is made: steps to your order | Wie der Vertrag zustande kommt: Schritte bis zur Bestellung | `[FEHLT]` (ECG § 9) |
| Whether the contract text is stored | Ob der Vertragstext gespeichert wird | `[FEHLT]` (ECG § 9) |
| Spotting and fixing input errors | Eingabefehler erkennen und korrigieren | `[FEHLT]` (ECG § 9) |
| Contract languages | Vertragssprachen | `[FEHLT]` (ECG § 9) |
| Subscription: term and cancellation | Abo: Laufzeit und Kündigung | `[FEHLT]` (brief: pravila za pretplatu NIJE POTVRĐENO) |

### Versand & Zahlung
**Title (EN):** Shipping & payment   **Titel (DE):** Versand & Zahlung

| EN | DE | Oznaka |
|---|---|---|
| Shipping in Austria | Versand in Österreich | tekst „Dostava" iz gornjeg dela fajla (demo) |
| Pickup at the café | Abholung im Café | isto (demo) |
| Payment methods | Zahlungsarten | `[FEHLT: Zahlungsarten]` |
| Shipping to Germany and the EU | Versand nach Deutschland & in die EU | `[FEHLT: Versand nach Deutschland & EU]` |

Po briefu (FAGG § 8 Abs 3), ograničenja isporuke i načini plaćanja moraju biti jasni najkasnije na početku porudžbine, pa ova dva reda ne smeju da ostanu prazna u pravom projektu.

### Widerrufsrecht
**Title (EN):** Right of withdrawal   **Titel (DE):** Widerrufsrecht

| EN | DE | Oznaka |
|---|---|---|
| Withdrawal information | Widerrufsbelehrung | `[FEHLT]` |
| Model withdrawal form (unchanged) | Muster-Widerrufsformular (unverändert) | `[FEHLT]` |
| Exceptions | Ausnahmen | `[FEHLT]` (brief: da li pržena kafa spada pod izuzetak § 18 FAGG, NIJE POTVRĐENO) |
| Withdraw online | Online widerrufen | demo blok ispod |

**Demo blok (cilj dugmeta „Vertrag widerrufen" iz footera):**
- EN: Demo: there's no contract here to withdraw from. In a real shop, you'd fill in your withdrawal here and send it.
- DE: Demo: Hier gibt es keinen Vertrag zum Widerrufen. Im echten Shop füllst du hier deinen Widerruf aus und schickst ihn ab.
- Dugme za potvrdu, onemogućeno: EN „Confirm withdrawal" · DE „Widerruf bestätigen" (oba **NEPROVERENO**, vidi 6).

### Cookies
**Title (EN):** Cookies   **Titel (DE):** Cookies
**Text (EN):** This demo doesn't use cookies. Your language and cart are saved only in your browser (localStorage) and are never sent to us. There are two entries: kafa-lang (language) and kafa-cart (cart). To remove them, clear this site's data in your browser.
**Text (DE):** Diese Demo verwendet keine Cookies. Sprache und Warenkorb werden nur in deinem Browser gespeichert (localStorage) und nicht an uns geschickt. Es sind zwei Einträge: kafa-lang (Sprache) und kafa-cart (Warenkorb). Löschen kannst du sie, indem du die Websitedaten dieser Seite in deinem Browser löschst.

| EN | DE | Oznaka |
|---|---|---|
| Cookie list and consent, if payment or other services are added | Cookie-Liste und Einwilligung, falls Zahlungs- oder andere Dienste dazukommen | `[FEHLT]` (samo za pravi shop) |

- Tekst odgovara planu (tačka 8: samo `kafa-lang` i `kafa-cart`, kolačića nema). Ako se ključevi promene, menja se i tekst. Proverava `bezbednost`.
- **Footer link:** stari tekst kaže „Cookie settings" / „Cookie-Einstellungen", ali podešavanja ne postoje. Predlog za Z11 je EN „Cookies" · DE „Cookies". Stari red iznad ne menjam, odluka je na direktoru.

### Mesto za Gewährleistungslabel (footer)

| Gde | EN | DE |
|---|---|---|
| natpis u obeleženom okviru | Placeholder: in a real shop, the official notice on the legal guarantee goes here, unchanged and in color. | Platzhalter: Im echten Shop steht hier der offizielle Hinweis zur gesetzlichen Gewährleistung, unverändert und in Farbe. |
| kratko (390 px) | Placeholder · Legal guarantee notice | Platzhalter · Gewährleistungshinweis |
| `aria-label` okvira | Placeholder for the legal guarantee notice | Platzhalter für den Gewährleistungshinweis |

Okvir ne pominje trajanje garancije niti bilo koji drugi sadržaj zvaničnog predloška. Odakle se predložak preuzima nisam proveravao (otvoreno pitanje 8).

---

## 4. Nedostajući natpisi

### Modal proizvoda i korpa

| Element | EN | DE |
|---|---|---|
| zatvori modal (dugme, `aria-label`) | Close details | Details schließen |
| zatvori korpu (`aria-label`) | Close cart | Warenkorb schließen |
| natpis „Količina" | Quantity | Menge |
| dugme − (`aria-label`) | Decrease quantity | Menge verringern |
| dugme + (`aria-label`) | Increase quantity | Menge erhöhen |
| ukloni (vidljivo) | Remove | Entfernen |
| ukloni (`aria-label`) | Remove {name}, {size}, from cart | {name}, {size}, aus dem Warenkorb entfernen |
| nazad iz modala (opciono) | Back to the shop | Zurück zum Shop |

### SIP kartica i kartica u prodavnici

| Element | EN | DE |
|---|---|---|
| čip | Demo | Demo |
| čip, tekst za čitač (`sr-only`) | Demo product, not for sale | Demo-Produkt, nicht erhältlich |
| dugme „+" (`aria-label`, iz `mockup.html`) | Add {name}, 250 g, to cart | {name}, 250 g, in den Warenkorb |

### Pretraga

| Element | EN | DE |
|---|---|---|
| broj rezultata, 1 | 1 result | 1 Ergebnis |
| broj rezultata, više | {n} results | {n} Ergebnisse |
| 0 rezultata | postojeći tekst „Nothing found for "{q}"." | postojeći tekst „Nichts gefunden für „{q}"." |

Broj se čita preko `aria-live="polite"`.

### Drugi skip link

| EN | DE | Vodi na |
|---|---|---|
| Skip to shop | Zum Shop springen | `#find-your-cup` |

### Demo napomena za „Start a subscription" i „Give as a gift"

| Element | EN | DE |
|---|---|---|
| red ispod oba dugmeta | Demo: nothing is ordered or paid here. | Demo: Hier wird nichts bestellt oder bezahlt. |
| toast posle „Start a subscription" | This is a demo, so no subscription was started. | Das ist eine Demo, es wurde kein Abo abgeschlossen. |
| toast posle „Give as a gift" | This is a demo, so no gift was ordered. | Das ist eine Demo, es wurde kein Geschenk bestellt. |

### `<noscript>`

Plugin pravi `<noscript>` na EN, a DE verzija je data u slučaju da zatreba.
- EN: Concept / demo — not a real shop. Turn on JavaScript to see the animation and the shop.
- DE: Konzept / Demo — kein echter Shop. Mit JavaScript siehst du die Animation und den Shop.

Alt GRIND postera u `<noscript>` je postojeći alt scene GRIND (EN).

### Format datuma

| Jezik | Izgled | Primer na kartici | `Intl` |
|---|---|---|---|
| EN | Oct 20, 2026 | Roasted on Oct 20, 2026 | `en-US`, `{ month: 'short', day: 'numeric', year: 'numeric', timeZone: 'Europe/Vienna' }` |
| DE | 20.10.2026 | Geröstet am 20.10.2026 | `de-AT`, `{ day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'Europe/Vienna' }` |

- EN ima ime meseca, jer bi „10/20/2026" ili „20/10/2026" gost mogao da pročita na dva načina. Uz US pravopis („flavor") ide US redosled.
- Ako se igde koristi pun naziv meseca na DE, `de-AT` daje „Jänner" umesto „Januar", i to je u redu za bečki sajt.

---

## 5. Grupe prženja za filter

**Potvrđeno:** Huila Pink Bourbon („Light-medium" / „Hell-mittel") se prikazuje i pod **Light / Hell** i pod **Medium / Mittel**, a na kartici ostaje natpis „Light-medium" / „Hell-mittel".

Provera brojeva iz Z9 po tabeli od 6 kafa:

| Filter | Kafe | Broj |
|---|---|---|
| Light | Guji, Nyeri, Huila | 3 |
| Medium | Huila, Tarrazú, Pause | 3 |
| Medium-dark | On Repeat | 1 |

`roastGroups` za Huilu je `['light', 'medium']`, a za ostale je po jedna grupa.

**Pomoćni tekst (opciono, ispod grupe Roast):**
- EN: Light-medium roasts show up under Light and Medium.
- DE: Hell-mittel geröstete Kaffees findest du unter Hell und unter Mittel.

---

## 6. Provera na EUR-Lex-u (23.10.2026)

**Rezultat: obe formulacije ostaju NEPROVERENE.**

Stranice EUR-Lex-a su otvarane preko `WebFetch` 23.10.2026 i svaki put su vratile prazan sadržaj. Verovatno je u pitanju provera „nisi bot" sa JavaScript-om. Probane stranice:
- HTML: `legal-content/EN/TXT/HTML/?uri=CELEX:32011L0083`;
- `TXT/?uri=CELEX:32011L0083`;
- PDF: `TXT/PDF/?uri=CELEX:32011L0083`;
- ELI 2023/2673: `eli/dir/2023/2673/oj/eng`;
- prečišćeni tekst 2011/83 na dan 27.09.2026, HTML i PDF.

Pretraga ograničena na `eur-lex.europa.eu` vratila je iste formulacije. Pošto je to sažetak malog modela, to je **trag, a ne citat**.

| Šta | EN (trag) | DE (trag) | Gde u propisu | Link | Status |
|---|---|---|---|---|---|
| dugme za porudžbinu | order with obligation to pay („or a corresponding unambiguous formulation") | zahlungspflichtig bestellen (brief, FAGG) | Direktiva 2011/83/EU, čl. 8(2), drugi podstav | [EUR-Lex 32011L0083](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32011L0083) | **NEPROVERENO** |
| funkcija za odustanak | withdraw from contract here | Vertrag widerrufen (isto i u FAGG § 13a, brief) | čl. 11a(1) Direktive 2011/83/EU, dodat Direktivom (EU) 2023/2673 | [EUR-Lex 2023/2673 EN](https://eur-lex.europa.eu/eli/dir/2023/2673/oj/eng), [DE](https://eur-lex.europa.eu/eli/dir/2023/2673/oj/deu) | **NEPROVERENO** |
| potvrda odustanka | confirm withdrawal | Widerruf bestätigen | čl. 11a(3) | isto, i [prečišćeni tekst 27.09.2026](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02011L0083-20260927) | **NEPROVERENO** |

**Ostali tragovi iz iste pretrage (nisu otvoreni):**
- Presuda SEU C-249/21 (Fuhrmann-2, 7.4.2022): reči iz čl. 8(2) su primer, a druge reči su dozvoljene ako već **sam natpis na dugmetu** jasno kaže da klik znači obavezu plaćanja ([EUR-Lex 62021CJ0249](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62021CJ0249)).
- Smernice Komisije (SL C 525/2021): „buy now", „pay now" i „confirm purchase" bi bili u redu, a „order now", „confirm" i „register" verovatno ne ([EUR-Lex SL C 525/2021](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ%3AC%3A2021%3A525%3AFULL)).
- Rok za prenošenje Direktive 2023/2673 je 19.12.2025, a primena od 19.6.2026 (EUR-Lex sažetak, trag). Brief za Austriju navodi Widerrufsbutton posle 30.9.2026 po RIS-u. Ta dva podatka se ne isključuju, ali vezu nisam proveravao.

**Šta važi do provere:**
- **Korpa (EN, onemogućeno dugme):** „Order with obligation to pay". To je doslovna formulacija iz direktive i najsigurniji izbor. Ima 28 znakova, pa staje u jedan red dugmeta u korpi na 390 px. Kraće „Buy now" je moguće po smernicama (trag), ali to bira klijent.
- **Footer (EN):** „Withdraw from contract here" (27 znakova). Ovim se popunjava `[FEHLT: EN-Text]` iz odeljka Footer, uz oznaku **NEPROVERENO**.
- **DE ostaje kao u briefu:** „Zahlungspflichtig bestellen" i „Vertrag widerrufen".

**Kako da se oznaka skine:** neko ko ima običan pregledač (korisnik ili direktor) otvori tri linka iz tabele, uporedi tekst i upiše datum. Posle toga u ovom odeljku i u beleškama na vrhu fajla „NEPROVERENO" postaje „provereno <datum>".
