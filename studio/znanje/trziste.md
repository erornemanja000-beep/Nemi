# Tržište: segmenti, konkurencija, cene, pravila

Poslednja provera: 2026-10-27
Vodi: `trziste`. Prvo punjenje. Ovo nije pravni savet; za klijenta uvek proveriti kod WKO-a ili pravnika.

**Kako čitati stavke.** `(GGGG-MM, izvor)`: mesec izdanja izvora; ako strana nema datum, piše „bez datuma" i uzet je mesec provere. „Procena" je moja, bez izvora. Brojevi tipa „x od 14" su prebrojani na mom uzorku, a njihovo uopštavanje na tržište je procena.

**Granice ovog punjenja (važno za pouzdanost).**
- Uzorak sajtova: 14 gastro sajtova (6 sladoledžinica, 8 kafića/pekara/restorana) i 1 pansion. Uzeti su sa liste bečkog turističkog zavoda (wien.info), dakle iznad proseka. Lokali bez sajta i sa lošim sajtom nisu u uzorku, pa su pravi nedostaci verovatno veći nego ovde.
- Alat čita samo tekst stranice. Kolačić-baner, video i izgled na telefonu se iz teksta ne mogu pouzdano proveriti. Gde piše „nije vidljivo", to ne znači da ne postoji.
- RIS (tekst zakona) nije bio dostupan (HTTP 503 u više pokušaja). Pravila ispod su iz WKO-a, ministarstava, USP-a i službenih EU strana; tekst ECG/MedienG/UGB treba proveriti na RIS-u pri sledećem punjenju.
- Nije pokriveno: lepota i wellness, fitnes, nekretnine, radnje (vidi „Praznine").

---

## 1. Veličina i sastav tržišta (Beč)

- Fachgruppe Gastronomie Wien, stanje 31. 12. 2024: 6.397 aktivnih članova (7.120 sa mirujućim, 10,2 % mirujućih). Po vrstama (aktivni): restorani 2.144; „freie Gewerbe" (izdavanje hrane i pića) 1.461; barovi/diskoteke 623; imbisi/Jausenstationen 615; bufei 384; Gasthäuser 364; catering/lieferküche 297; kantine 150; **Eissalons 101 (126 sa mirujućim, 19,8 % mirujućih)**; Würstel/Kebab 101. (2024-12, wko.at/wien/tourismus-freizeitwirtschaft/gastronomie/jahresstatistik-2024.pdf)
- U toj tabeli nema posebne stavke za kafiće. WKO Wien na strani Gastronomie pominje „ca. 8.000" članova cele sekcije (nedatirano; iz isečka pretrage, strana nije otvorena). (2026-10, wko.at/wien/tourismus-freizeitwirtschaft/gastronomie/start-w)
- Zaključak za studio (procena): bečkih sladoledžinica ima oko stotinu, pa je to ulazna referenca, a ne tržište od kog studio živi. Veći deo posla je u restoranima, kafićima, pekarama i lokalima sa više filijala.
- Lista sladoledžinica na wien.info: 36 lokacija, 17 brendova; 8 brendova ima po 2 ili više lokacija (zajedno 27 lokacija, najviše Veganista 9, Eis-Greißler 4). Prebrojao ja sa liste. (2026-10, wien.info/de/essen-trinken/cafes/eissalons-345022) Posledica (procena): mnogi lokali su male mreže, pa sajt treba da ume „Standorte" sa radnim vremenom po lokaciji. DON'S je jedna lokacija.
- Statistik Austria: 92 % firmi ima sajt, 68,1 % koristi društvene mreže, ali anketa obuhvata samo firme sa 10 i više zaposlenih, pa **ne važi za mikro-lokale**; razlaganje za gastronomiju nisam uspeo da pročitam. (2025-12, statistik.at, IKT-Einsatz in Unternehmen 2025, iz isečka pretrage)
- Udeo lokala koji imaju samo Instagram: **nije izmeren** (nema zvaničnog broja za mikro-firme).

---

## 2. Segmenti: obrasci na pregledanim sajtovima

### 2.1 Sladoledžinice (najdetaljnije, DON'S je sledeći)

Uzorak: 6 sajtova (1020, 1030, 1040/1080, 1080/1120, 1100, 1200 + Klosterneuburg). Po kvartovima se razlika ne vidi (premali uzorak). (2026-10, ručni pregled: schelato.at, leones.at, vidoni.wien, zuckero.at, tichy-eissalon.at, leonardelli-eis.at)

| Pitanje | Nalaz |
|---|---|
| Jezik | 6 od 6 samo nemački, nijedan nema prekidač za engleski |
| Sorte/cene | cene kao HTML tekst vidljive na 1 od 6 (Leones, sa kodovima alergena); samo PDF na 1 (Tichy: „Eiskarte 2026.pdf"); bez cena na 2 (Schelato, Vidoni); 2 imaju meni na podstrani koju nisam otvarao |
| Radno vreme | sezonski prekid vidljiv na 4 od 6 (zatvoreno do marta 2027); Tichy ima prazno radno vreme „-- Uhr -- Uhr" i „Winterpause" do 12. 3. 2027 |
| Online | 1 ima prodavnicu, torte po porudžbini i poklon-bonove (Zuckero); 1 ima dostavu preko spoljne platforme (Leonardelli); 1 prodaje bonove samo u radnji (Schelato); rezervacije nigde (nije potrebno) |
| Impressum/Datenschutz | linkovi u podnožju na 6 od 6 |
| Kolačić-baner | potvrđen samo na 1 (Schelato: Google Analytics, Google Ads, Meta); na ostalima se iz teksta ne može proveriti |
| Tehnika | WordPress 3 (jedan sa Elementor-om), verovatno Drupal 1, verovatno ručni/statički HTML 1, nepoznato 1 (zaključeno iz putanja u tekstu) |
| Video | 0 od 6 ima video na početnoj (jedan samo link na YouTube) |
| Greške | zamenski tekstovi „--", prazne slike, tipografske greške, duplirana navigacija, duge liste ukusa koje se na telefonu teško skeniraju, slike bez alt teksta |
| Izgled | 3–4 od 5 (procena, samo iz teksta) |

Šta najčešće fali (procena iz uzorka): engleski, meni sa cenama kao tekst (ne PDF), tačno sezonsko radno vreme, jasan prelaz sezone, video/pokret, sređena podešavanja privatnosti.

Za DON'S konkretno (iz repoa): sajt je već dvojezičan (DE/EN), ima meni sa kodovima alergena, Datenschutz stranu, lokalne fontove i Google Maps samo kao link bez ugrađene mape. To je iznad većine pregledanih sajtova.

Vreme prodaje (procena): sezonski lokali zatvaraju sajt i radnju do marta; zima je vreme da im se nudi nov sajt, sa objavom pre otvaranja.

### 2.2 Kafići, kafeterije, pekare, restorani

Uzorak: 8 sajtova (1010, 1020 ×2, 1040/1060, 1060, 1070 ×2, 1200). (2026-10, ručni pregled: balthasar.at, kaffemik.at, kaffeefabrik.at, wienerroesthaus.at, ulrichwien.at, petitjeudi.at, labstelle.at, drechsler-wien.at)

| Pitanje | Nalaz |
|---|---|
| Jezik | pun engleski na 3 od 8 (Kaffemik, Ulrich, Labstelle); delimično 1; samo nemački 4 |
| Meni sa cenama | HTML tekst 1 od 8 (Labstelle); samo PDF 2 (Ulrich, Drechsler); nema menija kafića sa cenama u pročitanom tekstu 5 od 8 (tri od njih imaju prodavnicu zrna sa cenama) |
| Rezervacija | online 4 od 8 (Ulrich, Drechsler: alat bez imena u tekstu; Labstelle: sopstvena strana; Petit Jeudi: TheFork); Balthasar piše da ne prima rezervacije |
| Prodavnica/bonovi | Shopify prodavnica sa bonovima i pretplatom 2 (Kaffemik, Kaffeefabrik), spoljna prodavnica zrna 1, bonovi/prodavnica na poddomenu 1 |
| Impressum/Datenschutz | bez Datenschutz linka u pročitanom podnožju 2 (Kaffeefabrik; Petit Jeudi samo „Rechtliche Hinweise" sa tekstom o Google Analytics bez vidljivog banera); Ulrich ima spojen link; Drechsler ima engleski naziv linka |
| Kolačić-baner | potvrđen na 1 (Ulrich), ali sa neprikazanim šablonom u tekstu banera (`{vendor_count}`, `{title}`) |
| Tehnika | WordPress 3, Shopify 2, Wix 1, nepoznato 2 |
| Video | 0 od 8 |
| Greške | „Widget wurde nicht geladen" (Rösthaus), „Wird geladen" u korpi (Kaffemik), isti alt tekst „tsw-bit-more-1" na 4 slike (Drechsler), nedosledan naziv lokala, dupla navigacija |
| Instagram | kod 2 od 8 je jedina društvena mreža na sajtu (Balthasar, Kaffeefabrik), ali oba imaju i pravi sajt; niko u uzorku nije samo Instagram |
| Izgled | 3–4 od 5 (procena) |

Šta fali (procena iz uzorka): meni kao tekst sa cenama i alergenima, engleski, rezervacija povezana sa postojećim alatom, ispravno podešavanje privatnosti i linkova, video/pokret.

### 2.3 Mali hoteli, pansioni, apartmani

- Raspodela rezervacija u Austriji (referentna godina 2025): online platforme 25,9 % (EU prosek 29,9 %), direktna prodaja 59,9 %; Booking Holdings ima 73,9 % tržišta platformi u Austriji. (2026-09, wko.at/tourismus-freizeitwirtschaft/hotellerie/hotrec-european-hotel-distribution-study, HOTREC studija)
- Provizija Booking.com 12–20 %, otkazivanje 19,0 % kod platforme prema 9,1 % kod sajta hotela, direktne rezervacije oko 68,7 % (druga metodologija od HOTREC-a, zato se brojke ne poklapaju): sve iz novinskih izveštaja (Ö1, tageskarte.io), izvorna ÖHV studija nije nađena. (bez datuma, iz isečka pretrage; tretirati kao NEPROVERENO)
- Uzorak sajtova: samo 1 pansion (Pension Wild): DE/EN, strana „Buchen" i „Anfragen", Real Cookie Banner, WordPress, bez izjave o pristupačnosti, cene nisu vidljive u tekstu. (2026-10, ručni pregled) Dva dalja pokušaja su propala (pretraga vratila samo agregatore). **Uzorak je premali za zaključak o obrascima.**
- Pravilo koje važi (vidi 5.3): većina pansiona je Kleinstunternehmen i izuzeta je iz BaFG za usluge; hotel sa 10 i više zaposlenih i online rezervacijom nije.

### 2.4 Kanzleien, Praxen

- Nije uzorkovano (pretrage za ordinacije i kancelarije nisu vratile sajtove). Zapisana su samo pravila:
- Lekari: § 53 ÄrzteG zabranjuje nesaobraznu, neistinitu informaciju i ono što šteti ugledu staleža; direktiva „Arzt und Öffentlichkeit" (2003) zabranjuje ponovljeno, naglašeno, reklamno isticanje imena; imena i slike pacijenata samo uz saglasnost. Lekar koji vodi sajt je Medieninhaber po MedienG. Ärztekammer Wien savetuje posebnu Datenschutzerklärung, jer izuzetak iz ÄrzteG ne važi za sajtove. (2018-05, aekwien.at, „Arzt und Homepage", i RIS Ärztegesetz, fassung 2026-10-11, oba iz isečka pretrage; stariji izvor, proveriti aktuelnu direktivu)
- Kancelarije (advokati, poreski savetnici): pravila oglašavanja po staleškim propisima **nisu istražena**.
- BaFG: sajt koji samo informiše nije obuhvaćen (WKO), a B2B ponuda takođe ne. Vidi 5.3.

### 2.5 Lepota/wellness, fitnes, nekretnine, radnje

Nisu istraženi u ovom punjenju. Jedini podatak: primer Herold-a, frizer u Beču sa 5 strana, rezervacijom termina i SEO-om, oko 1.900 € (2026-01, herold.at/ratgeber/website-erstellen/website-kosten-oesterreich, prodavac).

---

## 3. Konkurencija: agencije i frilenseri (javne cene)

Samo ponude sa javnim cenama. Nivo portfolija nije ocenjivan (reference nisu otvarane). Cene su „ab" i često neto; gde nije rečeno, piše „nije navedeno".

| Ponuda (domen) | Paketi i cene | Šta je uključeno / dodatno | Datum |
|---|---|---|---|
| hmtech.at (Beč) | Starter 990 € neto (do 5 strana, 2–3 ned.), Business 1.890 € (do 10 strana, Maps, kolačić-baner), Premium 3.490 € (neograničeno, shop ili blog, GA, 3 meseca podrške) | domen i hosting od 80 €/god. odvojeno; mesečno održavanje bez cene; rezervacija i video se ne pominju | bez datuma (2026-10) |
| webseitefix.at (gastro, Burgenland/Beč/NÖ) | GASTRO BASIS 1.900 €, GASTRO VOLL 2.900 € (bez PDV-a jer Kleinunternehmer) | Basis: sajt, Impressum, Datenschutz, galerija, rezervacija sa planom stolova, meni koji vlasnik menja sa telefona, porudžbine bez provizije. Voll: karta vina, DE/EN/HU, newsletter, bonovi, događaji. Bez mesečne takse; održavanje opciono 119 €/god.; domen i hosting oko 60–90 €/god. odvojeno. Bez pomena pristupačnosti, fotografije, videa | bez datuma (2026-10) |
| murix.at | OnePager od 690 €, Komplett od 1.490 € | gastro: HTML meni (ne PDF), rezervacija, fotke; hosting, održavanje i video se ne pominju | bez datuma (2026-10) |
| studiohills.at (Beč, Ottakring) | 790 € Einstieg, 1.490 € Business, 2.490 € Premium, 3.490 € Complete | svi: individualni dizajn, DSGVO, mobilno. Betreuung 49 €/mes. (hosting, SSL, dnevni backup, podrška); Google Ads 499 €/mes. + budžet; SEO setup 399 €; Google Business profil 249 €; lokalni SEO 89 €/mes. Foto/video/društvene mreže ne pominju | bez datuma (2026-10) |
| Herold (herold.at) | firmin sajt od 65,80 €/mes. (5–10 strana); Premium od 3.200 €+; DIY od 8,90 €/mes. | održavanje i hosting „meist 10–50 €/mes."; primeri: frizer 1.900 €, instalater 2.700 €, shop od 7.500 € (prodavac proizvoda) | 2026-01 |
| frilenser u Austriji (PDF cenovnik) | „Einfache Website" 1–3 strane 500 € privatno / 1.500 € firma; „Umfangreiche" 5–8 strana sa jednostavnim animacijama 1.500 € / 3.000 €; „Sehr umfangreiche" 10–15 strana 3.500 € / 6.000 € | pomoć oko domena i hostinga; bez održavanja | 2025-09 (emanueldevelopment.lima-city.at, pricelist 2025) |
| web-design.wien, internetservice.wien, naluma.at, webgaudi.at | od 699 €, od 890 € (Professional 1.990 €), od 799 €, restorani od 1.500 € sa rezervacijom i digitalnim menijem | iz isečaka pretrage, strane nisu otvorene; internetservice.wien navodi različite iznose na svojim stranama | 2026-10, NEPROVERENO |

Zaključci o konkurenciji:
- Javne cene lokalnih pružalaca kreću se od 690 € do 3.490 €, sa gastro paketima sa rezervacijom na 1.490–2.900 €. Skoro svi uključuju DSGVO i Impressum.
- Na 4 otvorene ponude (hmtech, webseitefix, murix, Studio Hills) **nijedna ne pominje video/Reels**; pristupačnost izričito ne pominje webseitefix, a na ostale tri nisam gledao tu stavku. Uzorak je mali; to je trag, ne dokaz.
- Premium agencije sa animacijama (Webflow i slično) postoje i u Beču, ali javnih cena nisu našle (isečak pretrage, bez otvaranja).
- Studio sa „sajtom od nule, prvo za telefon, animacije, video" nije u konkurenciji sa paketima od 690–1.490 €, nego sa gornjim delom raspona.

### 3.1 Video za društvene mreže (Reels/TikTok)

| Izvor | Cena | Šta |
|---|---|---|
| Filmska produkcija iz Beča (genesisfilms.at) | jedan Reel/TikTok 800–3.000 €; paket snimanja (5–10 klipova) 3.000–8.000 €; mesečno od 2.500 € | neto/bruto nije navedeno; tekst prodavca (2026-07) |
| Agencija iz Beča (goldenwing.at) | jedan Reel 300–800 €; 4–8 videa mesečno 1.500–3.500 € | koncept, snimanje, montaža; bez datuma; neto/bruto nije navedeno |
| Social Media Nanny (Austrija) | 4 Reels iz vaših fotografija od 360 € neto (oko 90 € po komadu, moj račun); snimanje na licu mesta od 4 Reels od 1.200 € neto (oko 300 € po komadu, moj račun), bez puta | muzika, tekst, efekti; na licu mesta i skripta, titlovi; bez datuma |
| Herold, upravljanje društvenim mrežama | „Small" od 250 €/mes. (objave za Facebook i Instagram, Reels se ne pominju); agencije često 800–1.200 € minimum; opšti raspon 800–1.500 €+ mesečno | bez budžeta za reklame; foto-snimanje „meist extra"; (2026-06) |

Gastro-specifične cene za Reels nisu nađene. Cifra „oko 1.200 €/god. prosečni marketing budžet restorana" iz jednog vodiča za pravljenje Reels-a (pozivanje na „DEHOGA Branchenreport 2026") nije potvrđena; ne koristiti. (2026-10, isečak pretrage)

---

## 4. Cene: raspon po tipu projekta

Sve su javne „ab" cene prodavaca, osim gde piše „procena". Neto/bruto često nije navedeno.

| Tip projekta | Javni raspon | Izvori |
|---|---|---|
| Jedna strana / početni sajt | 690–1.500 € | murix 690 € (OnePager), web-design.wien 699 €, Studio Hills 790 €, hmtech 990 € (do 5 strana), frilenser 1.500 € (firma, 1–3 strane) |
| Sajt sa menijem i rezervacijom | 1.490–2.900 € (tipično oko 1.900 €) | murix 1.490 €, Studio Hills Business 1.490 €, webseitefix 1.900–2.900 €, Herold primer frizera 1.900 €, webgaudi od 1.500 € |
| Premium skrol-sajt sa videom | **nema javnih cena u Beču.** Najbliže: Premium paketi 2.490–3.490 € (bez skrola i videa u opisu), Herold Premium od 3.200 €+, frilenser 3.500–6.000 €, shop od 7.500 € | (2026-10, strane iz gornje tabele). **Procena za studio: 4.500–7.500 € neto**, nizak nivo sigurnosti |
| Mesečno održavanje | 10–50 €/mes. (Herold), 49 €/mes. sa hostingom, SSL i backup-om (Studio Hills), oko 10 €/mes. (webseitefix 119 €/god.); hosting i domen od 60–90 €/god. odvojeno | (2026-01 i 2026-10, strane iz gornje tabele). **Procena za studio: 39–59 €/mes.** |
| Kratki video | 90–800 € po Reel-u u paketu ili pojedinačno, 800–3.000 € za pojedinačnu produkciju | vidi 3.1 |

Alati za rezervaciju koje klijent već plaća (da sajt ne dupliramo): DISH Professional Reservation 49 €/mes. na 12 meseci, 74 € na 3, 79 € bez ugovora, plus 199 € jednokratno, sve bez PDV-a (iz isečka francuske verzije strane, nije otvoreno); resmio u Nemačkoj Basic 0 €, Premium 69,90 €, Ultimate 129,90 €/mes. (strana za poređenje, datum nepoznat, NEPROVERENO); aleno bez javne cene. (2026-10, dish.co i treća strana)

Smisao za studio: rezervacija se skoro uvek ugrađuje iz postojećeg alata, a ne piše ispočetka, što drži cenu sajta niže od očekivanog.

WKO ne daje referentne satnice za web (honorarne smernice u oblasti reklame su opozvane zbog kartelskog prava; strana WK Wien je iz 2018). (2018-07, wko.at/wien/information-consulting/werbung-marktkommunikation/kalkulation-und-honorar)

---

## 5. Pravila i obaveze

Samo službeni izvori. Za konkretnog klijenta: provera kod WKO-a ili pravnika.

### 5.1 Impressum

- **ECG § 5 (važi za svaku komercijalnu stranicu):** ime/firma; geografska adresa sedišta; kontakt sa e-mailom, a prema OGH-u e-mail sam nije dovoljan, treba još jedan kanal (telefon ili web forma); Firmenbuchnummer i sud ako postoje; nadležni nadzorni organ; komora/udruženje i naziv zanimanja sa upućivanjem na propise; UID ako postoji. Cene čitke, za potrošače sa PDV-om (PrAG). AGB moraju moći da se sačuvaju i odštampaju. Važi i za profile na društvenim mrežama (XING, Facebook, X) i aplikacije. (2024-11, wko.at/internetrecht/informationspflichten-nach-dem-e-commerce-gesetz--dem-unte)
- **UGB § 14:** firma kako je upisana; ako se firma jednog upisanog preduzetnika razlikuje od građanskog imena, navesti i građansko ime. Isti izvor.
- **GewO § 63:** za obrtnike koji nisu u Firmenbuch-u; ime (prezime i bar jedno ime ispisano). WKO strana ne opisuje sadržaj odredbe, samo ime. Isti izvor.
- **MedienG:** važi za sve sajtove, privatne i komercijalne. Mali sajtovi: ime vlasnika medija, predmet poslovanja, prebivalište/sedište (§ 25 Abs. 5); veliki sajtovi sa sadržajem koji oblikuje mišljenje i Blattlinie traže više (§ 25 Abs. 2–4). WKO preporučuje da se Impressum objavi direktno na sajtu, ne samo kao link. (2025-08, wko.at/oe/internetrecht/das-korrekte-website-impressum-*.pdf; WKO navodi § 25 za sajtove i newsletter; § 24 se pominje uz newsletter, pa se brojevi članova proveravaju na RIS-u)
- **Posledica za „Instagram-only" lokale:** Impressum je obavezan i na profilu (WKO, vidi ECG iznad).

### 5.2 DSGVO i kolačići

- **Google Fonts:** WKO savetuje preuzimanje i lokalno hostovanje; provera: u izvornom kodu tražiti `fonts.googleapis.com` i `fonts.gstatic.com`. Talas opomena iz leta 2022 (190 € po sajtu); prvostepena presuda LG für ZRS Wien od 30. 12. 2025: sistematske opomene radi zarade su zloupotreba prava, DSGVO nema opšti preventivni zahtev, šteta traži stvaran gubitak; presuda nije pravosnažna. LG München (20. 1. 2022) dosudio 100 €. (2026-01, wko.at/datenschutz/abmahnungen-google-fonts, Stand 13. 1. 2026)
- **Kolačići (TKG 2021 § 165 Abs. 3):** za sve što nije tehnički neophodno treba saglasnost pre postavljanja; nema unapred štriklirane kućice; odbijanje mora biti isto lako kao prihvatanje, dugme za odbijanje ne sme biti manje vidljivo; prvi sloj navodi ko obrađuje, svrhe, pravni osnov i povlačenje; pristup sajtu se ne sme uskratiti zbog odbijanja. Tehnički neophodni (korpa, prijava, jezik, stanje saglasnosti bez ID-a) ne traže saglasnost. (bez datuma, dsb.gv.at/faqs/datenschutz-cookies)
- **Analitika i ugrađeni sadržaj:** alati za analizu i praćenje traže saglasnost; analiza log-fajlova za doseg se tretira kao legitimni interes; spoljni video, mape i objave sa društvenih mreža traže saglasnost, WKO preporučuje rešenje sa dva klika (Shariff, Embetty); Datenschutzerklärung mora imati sopstveni link, ne sme biti samo u Impressum-u ili AGB-u. (2026-10, wko.at/dsgvo4kmu/datenschutz-webseiten-cookies, datum strane 9. 10. 2026)
- **Forme:** WKO strana ne daje posebna pravila za kontakt forme, samo opšta načela (svrha, ograničeno čuvanje, mere bezbednosti po čl. 32 DSGVO). Datenschutzerklärung mora da pokrije i forme. (2026-10, isti izvor)
- Posledica za studio (procena): sajt bez analitike i bez spoljnih ugradnji ne traži baner; to je prednost za male lokale. Ako klijent hoće GA, Meta pixel, mape ili video, ide baner i dvoklik.

### 5.3 Pristupačnost (BaFG, od 28. 6. 2025)

- BaFG (BGBl. I Nr. 76/2023) primenjuje EU direktivu 2019/882 (European Accessibility Act); važi za usluge i proizvode stavljene na tržište ili pružene posle 28. 6. 2025. (2025-07, Leitlinien für Kleinstunternehmen, sozialministerium.gv.at, Stand 10. 7. 2025)
- **Obuhvaćeno:** sajtovi preko kojih potrošači mogu da zaključe ugovor, webshopovi, online rezervacije (WKO: „generell alle Online-Termin-Buchungs-Tools", i spoljni servisi za rezervaciju računaju se kao deo sajta). **Nije obuhvaćeno:** prezentacioni sajtovi bez prodaje, blogovi, sajtovi sa samo e-mailom u Impressum-u, B2B ponuda, oglasi za posao. (2026-01, wko.at/ce-kennzeichnung-normen/faqs-webinar-barrierefreiheitsgesetz, Stand 28. 1. 2026; 2025-11, wko.at/tourismus-freizeitwirtschaft/das-barrierefreiheitsgesetz-fuer-tourismus-und-freizeitbetriebe)
- **Izuzetak za mikropreduzeća (§ 6 Abs. 1):** firme sa manje od 10 zaposlenih i godišnjim prometom ili bilansom do 2 miliona €. Izuzetak važi za **usluge**, ne za proizvode. Ministarstvo ima primer: pekara sa 5 zaposlenih koja prodaje torte na sajtu je izuzeta (Beispiel 3). Prelazak praga vraća obavezu (sajt ili alat za rezervaciju se tada prilagođava). (2025-07, Leitlinien, sozialministerium.gv.at; 2026-01, WKO FAQ)
- USP navodi izuzetak za Kleinstunternehmen bez razlikovanja usluga i proizvoda. (2025-07, usp.gv.at/themen/betrieb-und-umwelt/nachhaltigkeit/BaFG.html, Stand 16. 7. 2025) Tumačenje ministarstva je preciznije; za sajtove ishod je isti.
- **I dalje važi BGStG** (Bundes-Behindertengleichstellungsgesetz): barijera je diskriminacija, osim ako je uklanjanje nezakonito ili neprimereno opterećenje; kazne nisu krivične, nego građanske posledice. (2025-07, Leitlinien; 2026-01, WKO FAQ)
- Ko mora (zaključak iz izvora): hotel, restoran, ordinacija ili prodavnica sa 10 i više zaposlenih (ili preko 2 miliona € prometa i bilansa) koja prima rezervacije ili prodaje potrošačima preko sajta. Tada: Barrierefreiheitserklärung (preporuka WKO: sopstveno dugme), usklađenost sa EN 301 549, WKO preporučuje WCAG 2.2 AA; dokumentacija izuzeća 5 godina. Kazna do 80.000 €, prvo poziv na ispravku („Beraten vor strafen"), niže kazne za KMU. (2025-11 i 2026-01, WKO strane iznad)
- Dokumentacija: mikropreduzeća za usluge ne moraju da dokumentuju procenu, ali na zahtev Sozialministeriumservice-a dostavljaju činjenice. (2026-01, WKO FAQ)
- Ostalo: sadržaj objavljen pre 28. 6. 2025 (video, PDF, arhiva) pod uslovom da je nepromenjen ne mora da se prilagođava; ugovori pre tog datuma do isteka, najviše 5 godina. (2026-01, WKO FAQ)

### 5.4 Označavanje AI sadržaja (EU AI Act, član 50)

- **Od kada:** pravila transparentnosti iz člana 50 počinju da važe **2. 8. 2026**. (2026-08, commission.europa.eu/news-and-media/news/safer-and-more-transparent-ai-2026-08-02_en; ai-act-service-desk.ec.europa.eu, timeline)
- **Digital Omnibus:** Uredba (EU) 2026/1744 od 8. 7. 2026 (Službeni list 24. 7. 2026) pomera visoko-rizična pravila (Annex III na 2. 12. 2027, Annex I na 2. 8. 2028), a **ne član 50**. Za generatore koji su na tržištu pre 2. 8. 2026 rok za mašinski čitljivo označavanje (čl. 50 st. 2) je 2. 12. 2026. To je obaveza **provajdera** alata (npr. generatora slika/videa), ne vlasnika sajta. (2026-10, ai-act-service-desk.ec.europa.eu, timeline; naslov uredbe iz EUR-Lex isečka, tekst nije otvoren)
- **Obaveze korisnika (deployer), čl. 50 st. 4:** ko u profesionalnoj delatnosti koristi AI sistem koji pravi ili menja sliku, zvuk ili video (deepfake) mora da navede da je sadržaj veštački napravljen ili izmenjen. Deepfake je (čl. 3 st. 60) AI sadržaj koji **liči na postojeće osobe, predmete, mesta, organizacije ili događaje i može pogrešno delovati kao autentičan**. Izuzetak: očigledno umetničko, kreativno, satirično ili fikciono delo, tada je dovoljno označavanje koje ne smeta prikazu. AI tekst objavljen radi informisanja javnosti o pitanjima od javnog interesa mora se označiti, osim uz ljudsku proveru i urednički nadzor. Čl. 50 st. 1: korisnik mora znati da razgovara sa AI sistemom (chatbot, avatar), osim kad je očigledno. Informacija mora biti jasna, najkasnije pri prvom susretu, i pristupačna. (2026-10, ai-act-service-desk.ec.europa.eu/en/ai-act/article-50 i /article-3)
- **Kazne i nadzor:** do 15 miliona € ili 3 % svetskog prometa za firme, srazmerno za MSP; nadzor nacionalni organi tržišnog nadzora. EU je napravila skup ikona za označavanje. Kodeks prakse (dobrovoljan) objavljen 10. 6. 2026; Smernice za član 50 objavljene (22. 7. 2026 na listi Komisije). (2026-08, commission.europa.eu, vidi iznad; kodeks i smernice iz isečaka pretrage, strane digital-strategy.ec.europa.eu su vratile 403, nisam ih pročitao)
- **Šta to znači za sajt klijenta (procena, tumačenje, ne zvaničan stav):**
  - AI slika jela, sobe, lokala, osobe ili događaja koja izgleda kao fotografija i bila bi shvaćena kao autentična: verovatno deepfake po definiciji, treba označiti (ili ne koristiti za prikaz stvarnog lokala).
  - Očigledno stilizovan ili izmišljen vizual (voksel, piksel, ilustracija, nadrealna scena): verovatno izuzetak za umetnička dela ili ne liči na stvarno, ali granicu određuju Smernice koje nisam pročitao.
  - AI video u Reels-u: označiti i alatom platforme i na sajtu.
  - Chatbot na sajtu: jasno reći da je AI.
  - Za hotele i restorane: AI slike ne koristiti kao prikaz stvarnih soba i jela (zavaravanje potrošača; UWG nije istraživan).
  - Pre ugovora sa klijentom: ko je „deployer" (studio ili klijent) zapisati u ugovoru.

### 5.5 Alergeni (meni na sajtu)

- Meni treba alergene sa kodovima A–R po Codex preporuci (A gluten, B rakovi, C jaja, D riba, E kikiriki, F soja, G mleko, H orašasti plodovi, L celer, M slačica, N susam, O sulfiti, P lupin, R mekušci) ili kratkim nazivima uz legendu; za Eissalon WKO izričito preporučuje pisani oblik (meni ili oglas); elektronski oblik je dozvoljen dodatno; informacija mora da počiva na pisanoj dokumentaciji i u lokalu mora biti obučena osoba. (bez datuma, wko.at/tourismus-freizeitwirtschaft/gastronomie/allergenkennzeichnung-bei-lebensmitteln i usp.gv.at/themen/brancheninformationen/gastronomie-und-tourismus/allergenkennzeichnung.html; iz isečka pretrage)

---

## 6. Prilike za studio

Sve cene u ovom odeljku su **procena** osim kad je uz njih naveden izvor.

1. **Mali gastro lokali (sladoledžinice, kafići, pekare), jednokratni sajt „Lokal".** Polazi od praznina iz 2.1 i 2.2: nemački samo, meni kao PDF ili bez cena, sezonsko radno vreme, bez videa, podešavanja privatnosti. Paket: sajt od nule, prvo za telefon, DE/EN, HTML meni sa alergenima, radno vreme po lokaciji i sezoni, lokalni fontovi, bez analitike (bez banera), 2-klik mapa. Cena: **od 1.900 do 2.400 € neto** (tržište: gastro paketi 1.490–2.900 €, vidi 4). Održavanje 39–59 €/mes. (sidro: 49 € Studio Hills).
2. **„Lokal + Reels".** Sajt + 4 Reels iz postojećih fotografija ili sa snimanja. Sidra: 4 Reels na licu mesta od 1.200 € neto i iz fotografija od 360 € neto (Social Media Nanny), 4–8 videa mesečno 1.500–3.500 € (Goldenwing). Cena paketa: **od 3.100 do 3.600 € neto**. Na 4 otvorena cenovnika sajtova (vidi 3) niko ne pominje video, što je razlikovanje, ali uzorak je mali.
3. **Premium skrol-sajt sa videom za restorane, hotele i veće lokale.** Javnih cena u Beču nema. Procena: **4.500–7.500 € neto** (sidra: Premium 3.200–3.490 €, frilenser 3.500–6.000 €, shop od 7.500 €). Nizak nivo sigurnosti.
4. **Pansioni i mali hoteli.** Argument: direktna prodaja je 59,9 % rezervacija u Austriji, a Booking ima 73,9 % tržišta platformi (HOTREC 2026, vidi 2.3). Paket sa direktnom rezervacijom preko postojećeg alata i videom: 2.400–4.500 € (procena). Uzorak je 1 sajt, nizak nivo sigurnosti.
5. **Kanzleien i Praxen.** Sajt koji samo informiše nije u opsegu BaFG; mali sajt je manji rizik i jasne granice oglašavanja (lekari). Cena 1.900–3.200 € (procena). Nije uzorkovano, nizak nivo sigurnosti.
6. **Pristupačnost kao ugrađen kvalitet.** Većina ciljnih klijenata je izuzeta iz BaFG, ali BGStG važi i WKO preporučuje WCAG 2.2 AA. Među otvorenim cenovnicima pristupačnost izričito ne pominje webseitefix (ostale nisam proveravao za tu stavku). Uključiti je u cenu kao standard kvaliteta, ne prodavati je kao pravnu obavezu.
7. **Vreme.** Sladoledžinice su zatvorene do marta 2027 (Tichy 12. 3. 2027). Procena: ponuda u novembru–januaru, objava početkom marta.

---

## 7. Praznine i šta osvežiti sledeći put

- Lepota/wellness, fitnes, nekretnine, radnje: nepokriveno.
- Kanzleien/Praxen, pansioni, Ferienwohnungen: uzorak nula ili jedan sajt; pravila oglašavanja advokata i poreskih savetnika nisu istražena.
- Udeo lokala samo sa Instagram-om: nije izmeren (mogući način: ručno proći lokale na Google Maps u 3 kvarta bez linka na sajt).
- Tekst zakona na RIS-u (ECG § 5, MedienG § 24/25, UGB § 14, BaFG § 6) i pun tekst Smernica za član 50 i kodeksa prakse: nisam mogao da otvorim (503 i 403).
- Konkurencija: nivo portfolija nije ocenjen; premium agencije bez cena; nije proveren Impressum/Datenschutz na sajtovima konkurenata.
- Cene Reels-a specifične za gastronomiju: nema javnih podataka.
- Rok za osvežavanje: pravila svakog meseca do 2. 12. 2026 (AI Act rok za označavanje); cene i konkurencija kvartalno; uzorak sajtova polugodišnje.
