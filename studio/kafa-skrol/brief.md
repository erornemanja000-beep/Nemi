# Brief: <brend> (izmišljena bečka pržionica specialty kafe)

Istraživač, 23.10.2026. Svi linkovi su otvoreni tog dana, osim gde piše drugačije.

Oznake:
- **NIJE POTVRĐENO**: nisam uspeo da potvrdim, ne koristiti kao činjenicu.
- **†**: tvrdnja je iz sažetka pretrage, stranicu nisam otvorio. Proveriti pre upotrebe.
- **IZRAČUNATO**: moj račun iz objavljenih cena, ne podatak sa sajta.
- Ništa ovde nije pravni savet. To je spisak šta sajt mora da pokrije, sa izvorima.

Baza znanja `studio/znanje/` je bila prazna (samo `README.md`), pa sam istraživao sve sam. Predlozi za bazu znanja su na kraju.

---

## Klijent (činjenice + izvori)

### Šta je klijent
Klijent ne postoji. To je koncept-maketa za portfolio, po uzoru na Vista Estates (`RealEstates/README.md`: "All listings, prices ... are made up. The brand is fictional").

| Stavka | Stanje | Izvor |
|---|---|---|
| Ime | `<brend>`, nije izabrano. Kreativci ga predlažu u `studio/kafa-skrol/ideje/`. | zadatak direktora |
| Šta je | izmišljena pržionica specialty kafe u Beču, sa kafićem i pogledom na pržionicu (pretpostavka koncepta) | zadatak direktora |
| Jezici | DE (osnovni) + EN | `CLAUDE.md`, zadatak direktora |
| Adresa, radno vreme, telefon, UID, firmenbuch | izmišljeno, nema stvarnih podataka. Za Impressum i footer treba izmišljen, ali verovatan niz podataka. | NIJE POTVRĐENO (ne postoji) |
| Struktura sajta | GRIND → POUR → SIP, pa prodavnica "Find your cup", o nama, kontakt | `studio/kafa-skrol/analiza-videa.md` |
| 3D sadržaj | mlin, dripper V60, gooseneck kuvalo, šolja, talas kafe, iz Blendera (Cycles, CPU) | `analiza-videa.md`, `.claude/agents/blender-umetnik.md` |

### Materijal koji već imamo u repou
- Za kafu nema nikakvih fotografija, logoa ni tekstova. `assets/` i `frames/` pripadaju DON'S Eisdiele.
- `studio/kafa-skrol/analiza-videa.md`: struktura, boje, tipografija, tehnika.
- `RealEstates/` (React + GSAP ScrollTrigger + Lenis + Three.js/R3F) ima gotove obrasce koje možemo da preuzmemo: pin sekcija od 420 vh, `useReducedMotion`, EN/DE prekidač (`src/i18n/`), modal proizvoda sa dubokim linkom (`#/property/<slug>`).
- `freiraum-premium/` ima skrol sa canvas sekvencama (prema `analiza-videa.md`).
- **Blender nije instaliran** u ovom okruženju (`which blender` ne vraća ništa), a `scripts/blender/` ne postoji. Okruženje ima 4 jezgra i 15 GB RAM-a. Treba proveriti ko i gde renderuje sekvence pre nego što se obeća broj kadrova.

### Pravila za online prodaju u Austriji (spisak šta sajt mora da ima)
Gde mockup prikazuje prodavnicu, mora da pokaže i ove elemente. Maketa nema stvarne porudžbine, pa se uz to stavlja vidljiva napomena "Konzept / Demo – keine echten Bestellungen" (moj predlog, ne zakonski zahtev).

**1. Impressum** (ECG § 5, UGB § 14), [WKO, stanje 07.11.2024](https://www.wko.at/internetrecht/informationspflichten-nach-dem-e-commerce-gesetz--dem-unte)
- Ime ili firma (kako je upisana), ladungsfähige adresa, e-mail **i** još jedan kontakt. Za webshop FAGG traži telefon i e-mail.
- Firmenbuchnummer i sud, UID (ako postoje), nadležni organ, komora, GewO kao primenljivi propis.
- Impressum na samom sajtu, ne samo link na tuđu stranicu.
- Mediengesetz § 25 (Offenlegung) važi za (neke) sajtove i za newsletter. Šta tačno treba navesti, WKO ne navodi na toj stranici: **NIJE POTVRĐENO**.

**2. Informacije pre ugovora** (FAGG § 4 i § 8), [WKO, stanje 02.07.2026](https://www.wko.at/service/wirtschaftsrecht-gewerberecht/Spezielle_Informationspflichten_im_Fernabsatz_B2C_im_Detail.html), [RIS FAGG, fassung 23.10.2026](https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20008847)
- Bitne osobine robe, identitet i kontakt trgovca.
- **Ukupna cena sa svim porezima, troškovima dostave i dodacima.** Ako se ne može izračunati unapred, mora da piše kako se računa. Neispravno prikazani troškovi dostave potrošač ne plaća.
- Uslovi plaćanja, isporuke i rok isporuke. Ograničenja isporuke i način plaćanja moraju biti jasni najkasnije na početku porudžbine (§ 8 Abs 3).
- Dugme za porudžbinu: "zahlungspflichtig bestellen" ili jednako jasno. Samo "bestellen" ili "weiter" ne važi.
- Potvrda ugovora na trajnom nosaču (e-mail) najkasnije uz isporuku.
- Streitbeilegung: navesti da li se dobrovoljno učestvuje u vansudskom postupku. **EU OS-platforma je ukinuta 20.6.2025**, pa se ne linkuje (isti WKO izvor).
- Instrukcije po ECG § 9: koraci do ugovora, da li se tekst ugovora čuva, ispravljanje grešaka u unosu, jezici (WKO, stranica iz prve pretrage, nije otvorena †).

**3. Novo od jeseni 2026** ([WKO, stanje 31.08.2026](https://www.wko.at/internetrecht/informationspflichten-webshops))
- Ugovori sklopljeni posle 26.9.2026: nove informacije po FAGG. **Widerrufsbutton** posle 30.9.2026 (§ 13a FAGG, tekst dugmeta "Vertrag widerrufen", vidi RIS iznad).
- **Gewährleistungslabel** (§ 4 Z 12): istaknuto obaveštenje o zakonskoj garanciji od 2 godine, npr. u footeru, u boji, bez izmena, **na svim jezicima sajta** (dakle DE i EN), i u e-mailu posle porudžbine.
- Informacija o ekološkim opcijama dostave, ako postoje (obaveze da ih nudimo nema).
- **Garantielabel** samo ako proizvođač daje besplatnu garanciju dužu od 2 godine (relevantno samo za opremu, npr. mlin). Podaci o popravljivosti opreme samo ako ih proizvođač da.
- **Sukob izvora:** WKO stranica "Rücktrittsrecht im Online-Shop" (stanje 30.06.2026) kaže da zakonodavni postupak za Widerrufsbutton u Austriji nije završen. Novija WKO stranica (31.08.2026) i RIS (fassung 23.10.2026, sadrži § 13a) kažu suprotno. Uzimam RIS kao merodavan. Kojom novelom i od kog datuma tačno: RIS stranica to ne pridružuje (nisam pročitao poslednjih 30.000 znakova), **NIJE POTVRĐENO**.

**4. Widerrufsrecht** ([WKO, stanje 30.06.2026](https://www.wko.at/internetrecht/ruecktrittsrecht-bei-warenkauf-im-internet), [FAGG § 18 na RIS](https://www.ris.bka.gv.at/eli/bgbl/i/2014/33/P18/NOR40162344))
- 14 dana bez navođenja razloga. Rok počinje kad kupac (ili njegov imenovani treći, ne prevoznik) preuzme robu.
- Muster-Widerrufsformular se daje **nepromenjen**. Povraćaj novca najkasnije 14 dana po prijemu izjave, istim sredstvom.
- Izuzeci iz § 18 Abs 1: Z 4 "Waren, die schnell verderben können oder deren Verfallsdatum schnell überschritten würde"; Z 5 zapečaćena roba, ako je iz zdravstvenih ili higijenskih razloga nije moguće vratiti **i** pečat je skinut posle isporuke.
- **Da li pržena kafa u zrnu spada pod Z 4 ili Z 5: NIJE POTVRĐENO.** Nijedan izvor ne govori o kafi, a pržena kafa ima rok trajanja od više meseci. Ne pretpostavljati izuzetak. Pitanje za pravnika (vidi dole). RIS verzija § 18 koju sam otvorio je stara (19.07.2022), ali tekst Z 4 i Z 5 potvrđuje i aktuelna fassung 23.10.2026.

**5. Cene** ([WKO, stanje 25.04.2025](https://www.wko.at/noe/e-commerce/faq-5), PrAG §§ 10a ff)
- **Grundpreis (cena po kg)** uz ukupnu cenu, vidljiv "na prvi pogled" uz nju. Važi i za webshop. Izuzeci: roba ispod 20 g/ml, kombinovane ponude, već jednak 1 kg.
- Cena sa PDV-om. **Kafa je u Austriji na 20 % PDV-a** ([Österreichischer Kaffee- und Tee-Verband, 21.9.2026](https://www.wko.at/oe/industrie/nahrungs-genussmittelindustrie/pa-21.9.2026---ktv_tag-des-kaffees.pdf), PDF, strana 1). Snižena stopa od 4,9 % od 1.7.2026 se na kafu ne odnosi ([WKO, stanje 24.06.2026](https://www.wko.at/steuern/ermaessigte-umsatzsteuer-saetze)). Oprema (mlin, dripper): podrazumevanih 20 %, **NIJE POTVRĐENO**.
- Od 30.12.2025 postoje minimalne veličine slova za prikaz cena, i za digitalne (Grundpreis oko 3,5 mm) †. Za webshop proveriti.

**6. Hrana: oznake** (LMIV, WKO †)
- LMIV važi i za prodaju na daljinu. Obavezne informacije moraju biti vidljive pre kupovine, **osim MHD, koji mora biti dostupan najkasnije pri isporuci**. Naziv, sastojci, alergeni, neto količina, MHD, firma i adresa. Austrijska Loskennzeichnungsverordnung dodaje broj lota †.
- Šta tačno važi za pržena zrna (npr. da li sastojci za jednosastojni proizvod): **NIJE POTVRĐENO**, nijedan izvor o kafi.
- Ako se na pakovanju navodi bio, kod kontrolne ustanove (primer formata: `AT-BIO-401` kod Coffee Pirates, `AT-BIO-402` kod Caffè a Casa). Izmišljeni brend ne sme da tvrdi Bio, Fairtrade i slično bez stvarne sertifikacije, pa se u makete stavljaju samo opisne tvrdnje ili jasna oznaka "Demo".

**7. DSGVO i newsletter** ([WKO, Einwilligung Newsletter](https://www.wko.at/internetrecht/zustimmungserklaerung-newsletter-tkg-dsgvo) †)
- Newsletter: prethodna saglasnost (§ 174 TKG 2021), aktivno štiklirano polje, **posebno** od AGB i kupovine, napomena da se saglasnost može opozvati, mogućnost dokaza. Double-opt-in nije obavezan, ali je preporučen. Potvrdni mejl neutralan.
- Preporuka WKO: kao obavezno polje samo e-mail. Datenschutzerklärung je potrebna. Kolačići i web-analitika: videti [WKO checklist](https://www.wko.at/internetrecht/checkliste-cookies-webanalyse-webshop) †. Predlog za maketu: samo neophodni kolačići, bez analitike. Fontovi lokalno (već u analizi).

**8. Ostalo**
- AGB nije zakonski obavezan, ali se preporučuje (WKO NÖ †).
- **Pristupačnost:** BaFG važi za webshopove od 28.6.2025. Izuzetak za mikro-preduzeća (manje od 10 zaposlenih i do 2 mil. € prometa ili bilansa) postoji, ali WKO kaže da važi samo za pružaoce usluga. Za klijenta koji je izmišljen cilj je WCAG 2.1 AA ionako ([WKO †](https://www.wko.at/internetrecht/barrierefreiheitsgesetz-e-commerce)).
- **EUDR (zakon o šumama i uvozu):** kafa je u Aneksu I. Primena od 30.12.2026 (velika preduzeća) i 30.6.2027 (mikro i mala). Obaveza je na prvom uvozniku, ne na sajtu ([IHK izvori †](https://www.ihk.de/karlsruhe/fachthemen/international/aktuelles/eudr-6823924)). Relevantno samo ako tekst tvrdi da brend sam uvozi zeleno zrno.
- **Pretplata:** pravila o trajanju i otkazu u FAGG nisam proverio, **NIJE POTVRĐENO**. UI mora jasno da pokaže učestalost, cenu i otkazivanje pre plaćanja.

---

## Ponuda

### Šta stvarno prodaje specialty pržionica u Beču
Zasnovano na šest sajtova (tabela u Konkurenciji) i na [Falter, 08.12.2025](https://www.falter.at/best-of-vienna/artikel/20251208/liebe-in-der-tasse): većina kafića prodaje zrna za kuću, lokalno ili online.

| Kategorija | Šta je tipično | Primer sa cenom |
|---|---|---|
| Single origin | 4–10 kafa u ponudi, rotira se | kaffemik HUEHUE (Gvatemala, washed) €16 / €64 po kg |
| Blend | kućni blend, često za espresso | Jonas Reindl Misty Mountain €15 (250 g), €54 (1 kg) |
| Espresso i filter | sajt deli kafe po pripremi | Jonas Reindl: "Espresso" i "Filter" kolekcije |
| Decaf | jedna kafa | Jonas Reindl Jimma Chamomilla (Etiopija) €20 (250 g), €80 (1 kg) |
| Kapsule | retko | Jonas Reindl Misty Mountain Capsules €10 (količina nije navedena) |
| Probierset / paketi | sample set, "favoriti" | GOTA Sample Set €29, Barista Favorites €59 |
| Pretplata | mesečna, dva tempa, poklon | kaffemik Release-Abo €40 mesečno (dve nove kafe), GOTA od €16 mesečno / €148 za 12 meseci |
| Oprema | ručni mlin, kuvalo, dripper, filteri | Fellow Stagg Pour-Over Kettle €170 (Jonas Reindl), kaffemik set sa ručnim mlinom, vagom i bokalom €195 |
| Knjiga, merch, vaučeri | česti | kaffemik Coffee Brew Book €24; vaučeri od €5 (kafić) i od €10 (GOTA) |
| Kursevi | cupping, latte art, filter | kaffemik cupping €29, Latte Art Basics €85, Home Espresso Workshop €290; Caffè a Casa Cupping Workshop 21.11.2026 |
| Wholesale / kancelarije | stranica B2B, često bez detalja | Jonas Reindl, kaffemik, GOTA, Coffee Pirates, Caffè a Casa (Geschäftskunden), Nomi (Büro / Gastronomie) |

Izvori: [jonasreindl.at](https://www.jonasreindl.at/collections/all), [kaffemik.at](https://www.kaffemik.at/), [gota.coffee](https://gota.coffee/), [caffeacasa.com](https://caffeacasa.com/), [nomi.coffee](https://nomi.coffee/), [coffeepirates.at](https://coffeepirates.at), svi 23.10.2026.

Veza sa našim 3D predmetima (predlog, nije činjenica): GRIND = mlin i zrna (kategorija "ganze Bohne" + izbor mlevenja), POUR = dripper i gooseneck (oprema, recepti), SIP = šolja (kafe, "Find your cup").

### Podaci na pakovanju i kartici proizvoda
Definicija: kafa od 80 ili više poena na SCA cupping skali je specialty ([ICO, 2025](https://ico.org/documents/cy2024-25/fgsc-3-r1e-definitions-specialty-coffee.pdf) †). SCA danas gleda i "spoljne" atribute, poreklo i obradu ([SCA](https://sca.coffee/what-is-specialty-coffee) †).

Šta stvarno stoji na stranicama proizvoda koje sam otvorio:

| Polje | kaffemik HUEHUE | Caffè a Casa Brazil Fazenda Dutra | Coffee Pirates Ethiopia Keramo |
|---|---|---|---|
| Zemlja i region | Gvatemala, Huehuetenango, San Antonio | Brazil, Matas de Minas, Araponga | nije prikazano |
| Proizvođač ili farma | Primavera Sisterhood ("Multiple Farms"), uvoznik Primavera Coffee | Fazenda Dutra, porodična od 1950-ih | nije prikazano |
| Visina | 1550 do 1650 m | 1000 do 1300 m | nije prikazano |
| Sorta | Caturra, Catuai | Yellow Bourbon, Red Catuí | nije prikazano |
| Obrada | washed | all natural | nije prikazano |
| Note ukusa | tamna čokolada, orašasto | gorka čokolada, karamel, orašasto, smeđi šećer | nije prikazano |
| Pakovanja | 250 g, 1000 g | 250, 500, 1000 g | cena €17,90, veličina samo u tabeli potrošnje (250 g) |
| Mlevenje | 7 opcija (zrno, espresso, moka, AeroPress, V60, filter mašina, French press) | 6 opcija | nije prikazano |
| Grundpreis | €64/kg | nije prikazano | polje postoji, prazno |
| Datum prženja | nije prikazan | nije prikazan | nije prikazan |
| MHD | nije prikazan | nije prikazan | nije prikazan |
| Posebno | cena proizvođaču €9,8/kg i trošak prženja €11,9/kg, lotovi od 84–85 poena | oznaka bio `AT-BIO-402`, ikone "Am besten geeignet für" | tabela potrošnje i odnos 1:16 |

Izvori: [kaffemik](https://www.kaffemik.at/products/huehue), [Caffè a Casa](https://caffeacasa.com/collections/best-sellers/products/kaffee-brazil-fazenda-dutra-bio), [Coffee Pirates](https://coffeepirates.at/products/ethiopia-keramo), 23.10.2026. Alat za čitanje stranica daje sažetak, pa "nije prikazano" znači da to nisam našao u preuzetom tekstu, ne da sigurno ne postoji.

Zaključak: **nijedna od tri stranice ne prikazuje datum prženja ni MHD**, a to je ono što specialty kupac traži i što zakon traži najkasnije pri isporuci. Mi to možemo da pokažemo na svakoj kartici.

### Tipične cene u Austriji (23.10.2026, sve sa PDV-om)
| Segment | 250 g | Po kg (Grundpreis) | Primeri |
|---|---|---|---|
| ulaz (kućni blend, bio blend) | €11,90–15 | oko €48–60 IZRAČUNATO | Coffee Pirates Pirates Blend BIO od €11,90; Caffè a Casa najprodavanije od €11,90; Jonas Reindl Misty Mountain €15 |
| standard single origin | €16–22 | €64–88 | kaffemik €16; GOTA od €14 (veličina nije navedena); Jonas Reindl Four Winds €22 |
| premium i mikro-lot | €19,90–29 | €80–116+ IZRAČUNATO | Coffee Pirates Pink Bourbon €19,90, Rumudamo €24,90; Jonas Reindl Lychee Rosé €29 |
| decaf | €20 | €80 | Jonas Reindl Jimma Chamomilla |
| 1 kg | €54–145 | – | Jonas Reindl: €54 (Misty Mountain), €79 (Four Winds), €145 (Lychee Rosé) |

Napomene:
- Jonas Reindl: 1 kg košta oko 10 % manje po kg od četiri vreće od 250 g (€54 prema €60, €79 prema €88). Kod Lychee Rosé je 1 kg skuplji po kg (€145 prema €116) IZRAČUNATO, što odgovara pakovanju od 200 g, a ne 250 g. Isto važi za kaffemik Ivan Junqueira Ribeiro (€14, €70/kg, oko 200 g). **Veličina nije potvrđena.**
- Besplatna dostava u Austriji od €35 (Coffee Pirates, ispod toga €4,50, minimalna porudžbina €20), €39 (Nomi), €50 (kaffemik), €60 (Caffè a Casa). Za Nemačku €70–75, za EU €70–120.
- Predlog za koncept (nije činjenica): cene u rasponu iznad, jedan premium lot oko €25–29 sa jasnom napomenom "demo", i prag besplatne dostave oko €45.

### Pretplata
- kaffemik: Release-Abo €40 mesečno (dve nove kafe), "Abonniere und spare" -10 % na bilo koju kafu, poklon pretplata 3/6/12 meseci od €114.
- Caffè a Casa: Roaster's Pick (menja se mesečno), omiljena kafa, kancelarijska pretplata. Učestalost mesečno, na dve nedelje ili nedeljno, otkazivanje ili preskakanje uvek.
- GOTA: mesečno od €16, 12 meseci €148.
- Tim Wendelboe (Oslo): poklon pretplata sa izborom espresso ili filter, 1–3 vreće mesečno, 3–12 meseci ([timwendelboe.no](https://www.timwendelboe.no/)).
- Coffee Collective (Kopenhagen): rotacija, mikro-lotovi, pauziranje i otkazivanje ([coffeecollective.dk](https://coffeecollective.dk/)).

---

## Brend (boje, fontovi, ton)

Koncept je dat u `analiza-videa.md`. Ovde samo ono što je provereno ili što utiče na dizajn.

**Boje (uzorci iz AI videa, približne):** krem `#E6DDCE`, tekst i tamno dugme `#2B2316`, terakota (Pour) `#915439`, tamnobraon (Sip) `#6E3A27`.

**Kontrast (WCAG 2.x, izračunato mojom skriptom 23.10.2026):**

| Tekst na pozadini | Odnos | Prolazi AA za običan tekst (4,5) |
|---|---|---|
| `#2B2316` na kremu `#E6DDCE` | 11,51 | da |
| krem na tamnobraon `#6E3A27` | 6,79 | da |
| krem `#E6DDCE` na terakoti `#915439` | **4,42** | **ne**, za malo slovo |
| `#2B2316` na terakoti `#915439` | **2,61** | **ne** |
| bela `#FFFFFF` na terakoti `#915439` | 5,95 | da |

Posledica: u POUR poglavlju običan tekst mora biti svetliji od `#E6DDCE` (npr. bela ili svetlija krem) ili se terakota malo zatamni. Veliki naslovi (od 24 px) prolaze i sa 4,42 (prag 3), ali tekst kartica i dugmeta ne. Pozadinske reči u 15–20 % razlici od pozadine su dekor i ne smeju nositi informaciju.

**Fontovi (iz analize):** uzak debeo grotesk velikim slovima za naslove poglavlja, mekani dekorativni serif iz 70-ih za pozadinske reči, razmaknuta velika slova za male natpise. Lokalno, ne preko CDN-a. Izbor konkretnih familija je posao dizajnera.

**Ton (iz konkurencije, predlog):**
- Obraćanje u Beču nije ujednačeno: kaffemik "du" i mešavina DE/EN, Caffè a Casa "Sie" i rodno inkluzivno ("KundInnen"), Nomi toplo sa "wir", GOTA i Coffee Pirates šaljivo ("The Coffee You Want, Not The Coffee You Need!", "Break the silence on lackluster coffee"), Sey i Onyx smireno i zanatski.
- Predlog: DE sa "du", kratke rečenice, stručni izrazi (washed, natural, masl) uz objašnjenje jednom. EN paralelno, bez doslovnog prevoda.
- Izbegavati: pirate, running-club, "wellness" ton (već zauzeto) i tvrdnje koje ne možemo da dokažemo ("beste Kaffee Wiens").

---

## Publika

**Činjenice:**
- Oko **86 %** stanovnika Austrije redovno pije kafu, prosečno **162 l po glavi godišnje**. Kafa i čaj imaju 20 % PDV-a, najviši stepen ([ÖKTV, saopštenje 21.9.2026](https://www.wko.at/oe/industrie/nahrungs-genussmittelindustrie/pa-21.9.2026---ktv_tag-des-kaffees.pdf)). Starija cifra od 162 l postoji već 2020. godine u [Hogapage](https://www.hogapage.de/nachrichten/beverage/kaffee-tee/oesterreicher-bei-kaffee-qualitaetsbewusst-und-genussaffin/), bez navedenog izvora, pa je moguće da je zastarela.
- Prema Tchibo Kaffee-Fakten 2026 (navedeno u istom saopštenju ÖKTV): **94,2 %** Gen Z kupuje kafu "za usput", a **78,6 %** se u kafeu sastaje na važnim razgovorima (iz rečenice nije jasno koja se generacija misli). To su podaci iz Tchibove ankete, ne iz nezavisne studije.
- Bečka kafana je upisana u austrijski nacionalni inventar nematerijalne baštine 2011. kao društvena praksa. Opis: mermerni stolovi, Thonet stolice, niše, stalci za novine, "a place in which time and space are consumed, but only the coffee is listed on the bill" ([UNESCO Austrija](https://www.unesco.at/en/culture/intangible-cultural-heritage/inventory/element/viennese-coffee-house-culture)).
- Specialty scena (izvor: [Falter, 08.12.2025](https://www.falter.at/best-of-vienna/artikel/20251208/liebe-in-der-tasse), [1000things, ažurirano 04.03.2026](https://www.1000thingsmagazine.com/de/a/54289/spezialitaetenkaffee-wien/)):
  - ručno prženje, direct trade, rotacija kafa, prženje u lokalu, kursevi i cupping, prodaja zrna i opreme;
  - kupci: komšije iz Grätzla, kućni baristi, turisti, kancelarijski radnici;
  - održivost, fair trade i bio su "središnji" u sceni (1000things). Alt Wien navodi oko 60 % sertifikovanih sorti, bio od 2005;
  - Kaffeegreissler je u nekadašnjem Naber espresso baru sa zaštićenim enterijerom iz 1950-ih, spoj starog i novog (Falter).
- Datumi početka: Jonas Reindl prži od 2014 ([Double Skinny Macchiato, 13.4.2026](https://www.doubleskinnymacchiato.com/2026/04/best-specialty-coffee-shops-vienna-austria-guide.html)), Coffee Pirates od 2012, GOTA od 2015, Café Franze od 2016, J. Hornig u Beču od 2017 (1000things).

**Šta ih zanima (zaključak, ne istraživanje):** poreklo i prozirnost cena, kako da skuvaju kod kuće, održivost. Dokaz je posredan: sve što konkurencija ističe je upravo to (kaffemik cena proizvođaču, Coffee Pirates Direct Trade i Fairly Paid, Coffee Collective Transparency Report, Wendelboe stranice farmi). **Anketu specialty kupaca u Beču nisam našao: NIJE POTVRĐENO.**

**Veza kafane i specialty scene:** Falter ne poredi izričito, a 1000things ne obrađuje odnos. Most koji se vidi u izvorima je prostor (Kaffeegreissler), vreme koje se troši na kafu (UNESCO opis) i "Grätzl-Austauschplatz". Za koncept: mesto ritualu, ne samo proizvodu. To je predlog kreativcima, ne činjenica o tržištu.

**Segmenti za dizajn (predlog):**
1. Kućni baristi koji kupuju zrna i opremu (GRIND i POUR poglavlja).
2. Radoznali kupci "Find your cup" (ukus, ne poreklo).
3. Poklon kupci i pretplatnici.
4. Turisti u Beču koji čitaju EN.
5. B2B (kancelarije, gastronomija): jedan link, bez posebnog sadržaja.

---

## Reference (link → šta uzimamo)

Nisam našao nagrađen scroll-3D sajt pržionice koji bih mogao da potvrdim. Curated Design ima samo jednu pržionicu (Coffee Collective), a Awwwards pretraga je dala samo NewmixCoffee (Honorable Mention). Scroll obrazac zato dolazi iz videa i iz `RealEstates/`, a ove reference daju strukturu prodavnice, podatke i ton. `studio/znanje/reference.md` još ne postoji, pa nema dupliranja. **Proveriti na kraju** da trend-skaut nije dodao iste sajtove.

| # | Sajt | Šta uzimamo | Šta ne uzimamo |
|---|---|---|---|
| 1 | [Coffee Collective, Kopenhagen](https://coffeecollective.dk/) (Curated id 4268, [stranica](https://curated.design/sites/s/4268/)) | Redosled početne: jedna istaknuta kafa sa notama → karusel kafa → pretplata → oprema → B2B → newsletter → mreža lokala. **Transparency** kao stavka glavnog menija. EN/DA prekidač iznad zaglavlja. Traka sa uslovima dostave. | Kartice bez porekla i nota, prazne oznake "Sale price" i "Unit price" (primer šta ne raditi). |
| 2 | [Tim Wendelboe, Oslo](https://www.timwendelboe.no/) | **Farms** kao glavna stavka: posebna stranica po farmi (osam). Izveštaji o transparentnosti pod "Responsibility". Poklon pretplata kao konfigurator (espresso ili filter, 1–3 vreće, 3–12 meseci). Mirna mreža proizvoda: ime, cena, jedinična cena. | Tekst, fotografije, brend. |
| 3 | [Sey Coffee, Njujork](https://www.seycoffee.com/) | Jedan dugačak skrol sa uredničkim ritmom, jedna istaknuta kafa (zemlja, mesto, note), velike fotografije preko cele širine, tekst o partnerstvu umesto prodajnog jezika. Ton događaja: "sniff, slurp and discuss". | Nema mreže ni cena na početnoj. Mi moramo da pokažemo prodavnicu. |
| 4 | [Onyx Coffee Lab, SAD](https://onyxcoffeelab.com/) | Smenjivanje punih sekcija sa jednom porukom i jednim dugmetom. Široko razmaknuti naslovi velikim slovima. **Producer Spotlight** (farma, visina, obrada). "Subscribe & Save" objašnjen kao "tracked, cupped, published". Mega-meni sa promo pločicama. | Njihove boje i pozadinske kremove (mi imamo svoju paletu), chat widget, četiri sestrinska brenda u zaglavlju. |
| 5 | [NewmixCoffee, Seul](https://www.newmixcoffee.com/) ([Awwwards, Honorable Mention 13.4.2026](https://www.awwwards.com/sites/newmixcoffee), Three.js, React, Canvas) | Samo ideja: jedna ruku-na-predmet interakcija u hero-u ("Drag to mix") i pet jezika. Slab uzor, jer je mala nagrada. | Sve ostalo. U tekstu stranice nisam našao ni 3D ni rezervu bez WebGL-a. Imena slika strelica karusela ("desktop_left") nagoveštavaju da kontrole nisu za telefon, **NIJE POTVRĐENO**. |

Napomena o tehnici: nijedan od ovih sajtova ne koristi pin i sekvence kao mi. Nijedan nije proveren na telefonu. Tehničke obrasce (pin, sekvence, reduced motion) treba uzimati iz `RealEstates/` i videa.

---

## Konkurencija

Aktivni su danas: svih šest sajtova je odgovorilo sa HTTP 200 23.10.2026, a navode ih [Falter](https://www.falter.at/lokalfuehrer/die-besten-cafes-fuer-specialty-coffee) (06.07.2026), Falter (08.12.2025), 1000things (04.03.2026) i Double Skinny Macchiato (13.04.2026). Caffè a Casa najavljuje radionicu za 21.11.2026. Imena i brojevi iz tuđih sajtova, bez fotografija i teksta.

**Mobilni kvalitet: NIJE POTVRĐENO.** PageSpeed API je vratio grešku zbog dnevne kvote, a pravi telefon nemam. Proverio sam samo HTML: svih šest ima `viewport` meta oznaku. Pet je na Shopify-ju (`cdn.shopify.com`), Jonas Reindl na WooCommerce-u. To znači da su sve standardne prodavnice sa responzivnom osnovom, a ne da su dobre na telefonu.

| Lokal (kraj) | Online shop | Pretplata | Kursevi | Kafić | Wholesale | Jezik | Cena 250 g | Besplatna dostava AT |
|---|---|---|---|---|---|---|---|---|
| [Jonas Reindl](https://www.jonasreindl.at/), 4 kafića (1070, 1080, 1090, 1030) | da | u meniju, bez detalja | nije pomenuto | da | da | EN (nešto DE) | €15–29 | nije navedeno |
| [kaffemik](https://www.kaffemik.at/), 1070 | da | da, €40 / -10 % | da (€29–290) | da | B2B stranica | DE + EN | €16 | od €50 |
| [Nomi / Kaffeemodul](https://nomi.coffee/) | da | nije pomenuto | nije pomenuto | Kaffeemodul (lokal, prema vodiču; sajt ga ne opisuje) | Büro/Gastro | samo DE | od €13 | od €39 |
| [Caffè a Casa](https://caffeacasa.com/), 1010, 1090, pržionica u Klosterneuburgu | da | da, više tempa | da (cupping, filter) | da | Geschäftskunden | samo DE | od €11,90 | od €60 |
| [Coffee Pirates](https://coffeepirates.at), 1090 | da | da | nije pomenuto | da | da | EN + DE | od €11,90 | od €35 |
| [GOTA](https://gota.coffee/), 1150 | da | da | da (SCA) | da | da | EN (nešto DE) | od €14 | nije navedeno |

Ostali pomenuti u vodičima, sajt nisam otvarao: Kaffeegreissler (1040), Wildkaffee (1050, otvoren aprila 2026, pržionica u Nemačkoj), Balthasar (1020), POC (1080), Alt Wien Kaffee (1040, pržionica u 1230), Café Franze (1180), J. Hornig (1070), Caffè Couture (1010). Izvori: [Falter 06.07.2026](https://www.falter.at/lokalfuehrer/die-besten-cafes-fuer-specialty-coffee), 1000things 04.03.2026.

### Šta rade dobro, a šta loše (samo ono što sam video u tekstu stranica)
- **Jonas Reindl:** jasna podela Espresso/Filter, decaf, 1 kg, oprema, vaučeri, "Brew Guides" u meniju. Prži u malim serijama do 10 kg. Loše: nema cene dostave ni uslova na stranici, bez nota ukusa na listi, sajt na engleskom iako je bečki.
- **kaffemik:** najbolja prozirnost (cena proizvođaču €9,8/kg, trošak prženja €11,9/kg), Grundpreis, preuzimanje u kafiću u roku 24 h, 14 dana povraćaja navedeno na stranici proizvoda. Loše: kartice bez sorte, veličine i datuma prženja, prazna sekcija "Rezepte" i oba pakovanja prikazana kao rasprodata na jednoj stranici.
- **Caffè a Casa:** najpotpuniji podaci o kafi (farma, visina, sorta, obrada), šest opcija mlevenja, jasna učestalost pretplate. Loše: samo DE, bez Grundpreisa i MHD na stranici koju sam otvorio, kontradiktoran status zaliha ("nicht verfügbar" uz "-187 auf Lager").
- **Coffee Pirates:** bio sertifikat sa brojem, tabela potrošnje (1–4 šolje nedeljno = 1 vreća mesečno), odnos 1:16, jasna tabela dostave. Loše: na stranici Keramo nema porekla ni nota, a polje Grundpreis je prazno.
- **GOTA:** širok svet (kafić, kursevi, vaučeri, merch, doručak, Running Club), selektor od 27 zemalja. Loše: previše stavki u meniju, bez uslova dostave i napomene o PDV-u na stranici.
- **Nomi:** kratak i čist, toplo. Loše: bez nota, veličina pakovanja nije navedena, samo DE.

### Gde možemo da budemo bolji (realno)
1. Nijedan nema skrol-priču. Svi su standardne prodavnice (Shopify × 5, WooCommerce × 1).
2. Rupe u podacima: datum prženja i MHD nigde, Grundpreis na dve od tri otvorene stranice nedostaje ili je prazan.
3. Prazne ili kontradiktorne stavke (prazna jedinična cena, "-187 na lageru", prazni recepti): naša prodavnica to ne sme da ima, čak ni u maketi.
4. Povezivanje sadržaja sa kupovinom: kod nikoga recept nije vezan za proizvod, a naše POUR poglavlje to prirodno nudi.
5. Jezik: samo dva od šest (kaffemik, Coffee Pirates) imaju DE i EN prekidač.
6. U preuzetom tekstu nijedan ne pominje bečku kafanu. Provereno samo na početnoj, **NIJE POTVRĐENO** za podstranice.

---

## Šta nedostaje / pitanja za klijenta

(Klijent ne postoji, pa pitanja idu direktoru, kreativcima i korisniku.)

1. **Ime brenda i logo.** Do izbora se u svemu piše `<brend>`. Fotografija, logoa i teksta nema.
2. **Da li je maketa samo vizuelna ili i funkcionalna?** Prodavnica sa korpom je lako: lokalni JSON i modal kao u `RealEstates`. Pravi checkout, nalog i newsletter traže backend (Netlify funkcije kao u `freiraum/`). Ključevi samo u Netlify env promenljivama (`CLAUDE.md`).
3. **Koliko stvarnih pravnih elemenata stavljamo na sajt?** Predlog: Impressum, Datenschutz, Widerruf i Gewährleistungslabel kao izmišljene, ali potpune stranice, sa napomenom "Konzept / Demo". To je i deo portfolija.
4. **Proizvodi i cene** su izmišljeni. Treba odlučiti: koliko kafa (predlog 6–8), da li imamo blend, decaf, set, opremu (mlin, dripper, kuvalo, šolja kao proizvodi?) i vrednosti za "Origin, Flavor, Roast" iz kartica u SIP poglavlju. Imena farmi i kooperativa izmisliti, ne preuzimati stvarna sa konkurentskih sajtova.
5. **Pravnik, kad bi brend bio stvaran:** (a) važi li Widerrufsrecht-izuzetak § 18 Z 4/5 za pržena zrna, (b) pravila otkazivanja pretplate, (c) šta tačno MedienG § 25 traži za sajt i newsletter, (d) PDV na opremu, (e) LMIV oznake za kafu u zrnu.
6. **Blender:** nije instaliran, pa treba dogovoriti ko renderuje (CPU, Cycles) i koliki je budžet kadrova. Analiza predviđa tri sekvence (mlin, dripper, šolja), talas i telefon sa manje kadrova.
7. **Mobilni test konkurencije.** Treba pregledati šest sajtova na telefonu (390 px) kad `tester` ili korisnik mogu. Moja provera je samo HTML.
8. **Fotografije i kafić.** Predlog je da fizičke fotografije izbegnemo i sve radimo iz Blendera i CSS-a. Ako treba fotografija lokala ili kafića, `prompt-slike` i `mediji` je prave. Ja ne preuzimam ništa sa tuđih sajtova.

---

## Šta koncept mora da ima da bi delovao kao pravi brend (5)

1. **Potpun podatak o svakoj kafi:** zemlja, region, farma ili kooperativa, visina, sorta, obrada, note, espresso ili filter, **datum prženja i MHD**, cena i **Grundpreis po kg**, pakovanja 250 g i 1 kg. Konkurencija ima rupe baš tu.
2. **Prozirnost porekla i cene:** stranica o farmi/kooperativi po kafi i cifra "cena proizvođaču" (kaffemik €9,8/kg, Wendelboe Farms). Izmišljeno, ali dosledno i označeno kao demo.
3. **Prodavnica koja radi po austrijskim pravilima:** cene sa PDV-om i Grundpreis, dostava sa pragom (oko €35–60), "zahlungspflichtig bestellen", Impressum, Widerruf sa "Vertrag widerrufen", Gewährleistungslabel na DE i EN, DSGVO newsletter sa posebnom kućicom. Plus DE/EN prekidač.
4. **Ponuda koja prati tri poglavlja:** "Find your cup" (Origin, Flavor, Roast), izbor mlevenja po metodi (6–7 opcija), pretplata sa poklon varijantom, Probierset, oprema (mlin, dripper, kuvalo), vaučer.
5. **Prisustvo u Beču i ritual:** adresa, radno vreme i kafić sa pogledom na pržionicu, cupping i kurs (referentna cena €29), B2B link, ton koji priča o kafani i vremenu uz kafu. Uz to **telefon, reduced motion i kontrast**: krem na terakoti ima 4,42:1 (ispod 4,5), pa tekst u POUR poglavlju mora biti svetliji.

---

## Predlozi za bazu znanja (`studio/znanje/`)

- `trziste.md`: bečki specialty segment (tabela konkurenata i cena iznad), pravila online prodaje (spisak iznad: FAGG novine od 27.9. i 1.10.2026, Widerrufsbutton, Gewährleistungslabel, ukinuta OS-platforma 20.6.2025, Grundpreis, BaFG). **Važi za svakog klijenta sa webshopom.**
- `trendovi.md` i `reference.md`: Coffee Collective, Wendelboe, Sey i Onyx kao uzori za "prozirnost i podatke o proizvodu". Za scroll-3D nema potvrđene pržionice, pa trend-skaut treba da traži uzore van branše (3D proizvod na skrol sa nagradom).
- Beleška o alatima: PageSpeed Insights API je odgovorio na 429 (dnevna kvota), pa za mobilnu proveru treba lokalni test ili ključ.
- Beleška o metodi: WebFetch vraća sažetak koji pravi mali model, pa se cene, veličine pakovanja i datumi sa tuđih sajtova moraju proveriti ručno pre nego što uđu u bazu znanja. Mesta gde sam sumnjao označena su u ovom briefu.
