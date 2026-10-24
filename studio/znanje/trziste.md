# Tržište: segmenti, konkurencija, cene, pravila

Poslednja provera: 2026-10-24

Fajl vodi agent `trziste`. Do 24.10.2026 je u njemu samo jedan segment (kafa u Beču) i jedna tema (nepozvano obraćanje firmama). Ostali segmenti (kafići, sladoledžinice, restorani, lepota, fitnes, nekretnine, mali hoteli, radnje), konkurencija studija, pravila Impressum / DSGVO / pristupačnost / AI označavanje **još nisu istraženi**. Za webshop pravila (FAGG, Widerrufsbutton, Gewährleistungslabel, Grundpreis, PDV na kafu) vidi `studio/kafa-skrol/brief.md` (2026-10, WKO i RIS).

Oznake: stavka ima `(GGGG-MM, izvor)`. „procena" je moja procena. NEPROVERENO = nije potvrđeno u zvaničnom ili nezavisnom izvoru. Ovo nije pravni savet.

## Kafa u Beču: pržionice i prodavnice kafe (2026-10)

Uzorak: 25 kandidata (pržionice i prodavnice kafe sa sajtom ili sa tragom o sajtu), pregledano na telefonu 390 px, plus 10 isključenih. Lista i ocene po lokalu: `studio/prodaja/kafa-bec.md`. Uzorak potiče iz medijskih lista (Falter, 1000things, Falstaff), pa vrlo male pržionice koje nisu u medijima verovatno nedostaju.

1. **Podela prema kvalitetu sajta (procena):** 10 od 25 ima slab sajt ili vidljiv problem (A), 5 srednje (B), 10 vrhunski (C). Najjači sajtovi su kod najpoznatijih specialty imena (kaffemik, Coffee Pirates, Süssmund, Rauwolf, Caffè a Casa). (2026-10, moj pregled 24.10.2026)
2. **Platforme (među 25):** 9 Shopify, 6 WooCommerce, 7 ostalo (Wix, Jimdo, Shopware, JTL-Shop, vlastiti CMS siteswift, Webflow, jedna nepoznata), 3 posebna slučaja (sajt u radu, samo Instagram, shop na tuđem domenu). (2026-10, moj pregled; platforma po tragovima u kodu i `generator` meta oznaci)
3. **Webshop:** 22 od 25 imaju put do online kupovine. Bez shopa: Café Franze (sajt u radu), Café Fokus (samo Instagram, NEPROVERENO), BEANDEPENDENT (jedna stranica). (2026-10, moj pregled)
4. **Jezici:** samo 5 od 23 pregledana sajta ima DE/EN prekidač. 14 su samo DE, 3 samo EN, 1 mešano. (2026-10, moj pregled linkova i `hreflang` na početnoj; prekidače koji se prave JavaScript-om može da promaši)
5. **Težina početne na telefonu:** 4 od 23 šalju preko 9 MB (Cottage Roasters 17,0 MB, od toga 16,4 MB dva MP4-a; taste it 13,8; Alt Wien 12,0, od toga 11,6 MB JPEG; Hawelka 9,8, od toga 8,8 MB PNG). Ostali su do 6,6 MB. Zbir `Content-Length`, donja granica. (2026-10, moj pregled 24.10.2026) Naš KORN / KANNE koncept: 1,9 MB pri otvaranju i 6,0 MB posle skrolovanja do dna u istom testu. (2026-10, moje merenje)
6. **Vidljivi problemi na telefonu (kod 6 od 25 kandidata):** kutija „Zustimmung erforderlich … Matomo" na vrhu (Mocca Brasil), dugmad dijaloga za kolačiće van ekrana (Cottage Roasters), pokvarena slika u naslovu dijaloga (Balthasar), traka „Bestellungen nur auf Rechnung" na shopu (Fürth Kaffee), sajt u režimu održavanja (Café Franze), preko 12 MB slika (Alt Wien). (2026-10, moj pregled)
7. **Skrol-priča:** na prvim ekranima nijednog od pregledanih sajtova nisam video skrol sa 3D ili sekvencom kadrova. Cottage Roasters koristi video u zaglavlju. Pregledan je samo prvi ekran i navigacija, NEPROVERENO za dublje strane. (2026-10, moj pregled; isto kaže `studio/kafa-skrol/brief.md`, 2026-10)
8. **Shop tuđeg brenda:** Balthasar (kafe-bar) preusmerava „SHOP" na stranicu Wildkaffee GmbH (Shopify, 194 proizvoda). Znači da neki bečki lokali prodaju zrna kroz shop proizvođača, a ne svoj. (2026-10, moj pregled)
9. **Cene zrna, jedan primer sa sajta:** Mocca Brasil (pržionica „seit 1927") 250 g od 7,95 € do 10,98 €, uz „inkl. 20 % MwSt.". To je ispod specialty raspona iz briefa (11,90–29 €). (2026-10, [brasil.at](https://www.brasil.at/site/shop), 24.10.2026)
10. **Pržionica nije uvek u Beču:** Kaffeefabrik prži u Burgenlandu (wien.info, datum stranice nepoznat), Caffè a Casa u Klosterneuburgu (2026-03, 1000things), Die Rösterin je firma iz Stockeraua sa tezgom u 1210 (2026-10, Impressum sajta i Falter), a Wildkaffee u Bavarskoj (2026-10, Falter). Tvrdnju „bečka pržionica" proveriti pre nego što uđe u tekst klijenta.

## Pravila: nepozvano obraćanje firmama (TKG 2021 § 174), 2026-10

Izvori: WKO i Ministarstvo (BMWKMS). Tekst na RIS-u ([TKG 2021 § 174](https://www.ris.bka.gv.at/eli/bgbl/i/2021/190/P174/NOR40238632)) nisam mogao da otvorim (anti-bot provera, HTTP 503), pa citat potiče iz WKO-a.

1. **Poziv radi reklame traži prethodni pristanak.** „Anrufe zu Werbezwecken ohne vorherige Einwilligung des Teilnehmers sind unzulässig." Važi i za prvi kontakt sa potencijalnim klijentom. Javno objavljen telefon nije pristanak. (2026-08, [WKO](https://www.wko.at/information-consulting/werbung-marktkommunikation/werbung-per-telefon-fax-e-mail-sms-was-ist-erlaubt), stranica sa datumom 15.08.2026)
2. **E-mail i SMS radi direktne reklame traže prethodni pristanak.** Izuzetak je samo e-mail sopstvenim kupcima za slične proizvode, uz mogućnost odbijanja pri prikupljanju podataka. Granica „više od 50 primalaca" je ukinuta 2018. (2026-08, WKO isti izvor)
3. **Važi i za firme.** Ministarstvo: pravilo važi i za privredni i za neprivredni sektor. Stranica nema datum. (2026-10, [BMWKMS](https://www.bmwkms.gv.at/en/topics/telecom-and-postal-services/telecommunications-law-and-policy/Unsolicited-messages.html))
4. **Kazna:** upravni prekršaj, nadležan je Fernmeldebüro. Visinu u otvorenim izvorima nisam našao. (2026-10, BMWKMS)
5. **Lični dolazak u lokal:** WKO i BMWKMS stranice govore samo o pozivu, faksu, e-mailu i SMS-u. Pravilo o poseti nisam našao, UWG nisam proveravao: NEPROVERENO, ne dozvola. Za sigurnost pitati WKO ili pravnika. (2026-10, WKO i BMWKMS)
6. **Kontakt forma firme:** nijedan izvor to ne rešava izričito. Tretirati kao e-mail (procena).

## Cene sajtova u Austriji (slaba pouzdanost, 2026-10)

Nema nezavisne statistike. Sve je iz blogova i oglasa agencija, većinom nemačkih:
- Shop kod frilensera 3.000–8.000 €, individualni shop kod agencije 5.000–20.000 € (2026-10, [experte.de](https://www.experte.de/online-shop/onlineshop-kosten), Nemačka).
- Mesečni paketi za jednostavan sajt u Beču 29–100 € neto: One-Page 29 €, više stranica 49 € (Social Bunny), „Rundum-Sorglos" od 97 € (Webigo). Hosting, SSL i podrška uključeni po navodu agencija. (2026-10, [meinbezirk.at](https://www.meinbezirk.at/leopoldstadt/c-regionauten-community/warum-wiens-kleinbetriebe-online-unsichtbar-sind_a8961897) i sajtovi agencija, reklama)
- Održavanje oko 100–200 €/mesec za Shopify i 100–400 € za WooCommerce (2026-10, [ostend.digital](https://ostend.digital/shopify-shop-erstellen-lassen-kosten-ablauf/), agencijski blog).
- Premium skrol-sajt sa 3D i video sekvencama: **nema izvora**. Moja procena za pilot sa prvim klijentom: oko 3.000–5.000 € jednokratno plus 50–100 € mesečno održavanje. Nizak nivo sigurnosti.

## Prilike (procena, nizak do srednji nivo sigurnosti)

- **Segment:** nezavisne pržionice i prodavnice kafe u Beču sa slabim ili zastarelim sajtom (A lista u `studio/prodaja/kafa-bec.md`: Comet / Fürth, Cottage Roasters, Mocca Brasil, Alt Wien, Wiener Rösthaus, Balthasar, Café Franze).
- **Paket:** skrol-priča + shop sa pretplatom, DE/EN, lagane slike (ispod 10 MB na telefonu), cena po kg i datum prženja na kartici.
- **Cena:** vidi iznad (procena).
- **Šta ne važi:** uzorak je mali (25) i dolazi iz medija, a vlasnik često ne mora da hoće skrol-priču. Prva poseta treba da potvrdi interes, ne da ga pretpostavi.

## Šta ostaje da se istraži

Ostali segmenti, konkurencija studija (paketi i cene agencija u Beču), pravila: Impressum, DSGVO (forme, fontovi, analitika), pristupačnost (EAA / BaFG), AI označavanje. Za webshop obaveze vidi `studio/kafa-skrol/brief.md`.
