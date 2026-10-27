## Ein Fenster brennt
**U jednoj rečenici:** Neubau u 04:00 je minijatura na dasci za hleb: ceo blok spava u sivoplavom mraku, svetli samo jedan topao prozor u prizemlju ugaone zgrade, i skrol nas vodi od krovova do tog prozora i dalje unutra, dok se nebo menja od noći do 07:00.

**Potpisni trenutak:** Fasada ugaone zgrade se odvoji kao kriška od vekne, a ispod „kore" grada stoji topla, živa pekara. Zato se zove *Krume*: grad je kora, a pekara sredina.

**Raspoloženje:** tiho · ručno pravljeno · toplo iznutra · noć `#14110f`, kamen `#2b2a28`, krov `#3b4048` (jedina hladna nota, ugasi se do zore), kora `#7a4a24`, žar `#e8792b`, testo `#eadbc4`, jutro `#f6f1e7` · Bricolage Grotesque (već je u `pekara/assets/fonts`) za naslove, uski mono za sat (OFL, self-host)

**Mapa skrola**
1. **04:00, Das Grätzl.** Kamera je visoko, pod uglom kao kod makete (lažni tilt-shift). Blok sa tri gründerzeit kuće i jednom ugaonom kućom stoji na dasci u praznini. Sve je tamno, samo dim iz dimnjaka pekare i jedan narandžasti prozor. Naslov: „Bevor Wien aufwacht, backen wir." Sat u uglu: 04:00.
2. **04:30, Über die Dächer.** Kamera klizi preko mansardi, badža i dimnjaka po putanji iz Blendera, sa inercijom. Dole prolazi prvi, prazan i osvetljen tramvaj, a ulične lampe trepere. Tekst: „Noch fährt keiner. Außer uns."
3. **05:00, Der Anschnitt (potpis).** Kamera se spusti do ulice, ispred toplog prozora. Fasada i prvi sprat se izvuku napred kao kriška, a na preseku se vidi cigla sa teksturom mrvice. Unutra je pekara u preseku, kao kućica za lutke.
4. **05:15, Teig. Zeit. Ofen.** Kamera ide od stanice do stanice unutar preseka. Na stolu se testo mesi (morph), korpe čekaju da testo naraste (skala), a na kraju se otvore vrata peći i narandžasta svetlost preplavi kadar. Taj trenutak iz briefa ovde ostaje kao eho. Ispod su tri kratka teksta sa sajta.
5. **06:00, Brot des Tages.** Kamera se vrati iza izloga. Na polici su četiri hleba (Kaisersemmel, Mohnwecken, Laugenbrezel, Roggenlaib), a na skrol svaki izađe napred sa imenom i cenom. Nebo iza bloka počinje da sivi.
6. **06:30–07:00, Das Grätzl wacht auf.** Kamera se diže nazad na pogled cele makete. Od pekare kreće talas svetla: prozori se pale jedan po jedan, sve dalje od radnje, kao da se miris širi kroz ulice. Lampe se gase, krovovi se zagreju, a sitne figure sa kesama idu ka vratima. Prikazuje se „Wir sperren auf.", Di–Sa 6:30–14:00 i „Neubau, 1070 Wien".
7. **Vorbestellen i kraj.** Maketa je dnevna i mirna, iza HTML forme „Dein Sackerl für morgen". U futeru nebo opet padne u veče i ponovo svetli samo jedan prozor: „Bis morgen früh."

**Interakcija:** „Dreh das Grätzl". Vodoravnim povlačenjem (miš ili prst) maketa se okreće na dasci najviše ±25°, sa inercijom, kao torta na postolju, pa se vrati u osu kad se pusti. Uspravni skrol ostaje skrol. Dodatno: tap na topli prozor u bilo kom trenutku pusti kratak puf brašna i zvuk zvona na vratima (Web Audio, samo posle prvog klika, podrazumevano isključen).

**Telefon (390 px):** Kompozicija je napravljena oko ugaone kuće, koja je uspravna, pa staje u portret bez sečenja. Kamera je bliže, a sporedne kuće se gube u magli. DPR je najviše 1,5, bez DOF-a, a tilt-shift je jeftin gradijent zamućenja u jednom pasu. Unutrašnjost pekare se učitava tek u poglavlju 2. Tekst je u HTML-u ispod kadra, ne u 3D-u.

**prefers-reduced-motion (i bez WebGL-a):** Nema kamere vezane za skrol ni Lenisa. Svako poglavlje je jedna statična slika renderovana iz iste Blender scene (7 kadrova u WebP-u, 16:9 i 9:16): noć, krovovi, presek, peć, izlog, budno jutro i veče. Slike se menjaju običnim skrolom, bez pomeranja. Sat i svi tekstovi ostaju, a interakcija i čestice se isključuju.

**3D modeli, materijali, shaderi (Blender → GLB, Meshopt, KTX2)**
- Modularni kit fasade: prozor sa šambranom, venac, gauba, dimnjak i mansardni krov. Od njega se slažu 4 kuće (princip bečkog grinderzajta, bez prave zgrade).
- Ugaona kuća sa radnjom: fasada kao poseban mesh-kriška sa presekom (cigla i mrvica) i animacijom izvlačenja u GLB-u.
- Unutrašnjost: peć sa vratima, sto, testo (2 shape keys), korpe, polica, četiri hleba (low-poly, bake normala sa high-poly).
- Ulica: kocka, trotoar, 6–8 lampi (instancirane), generički tramvaj, 5–6 sitnih figura sa jednostavnim hodom, papirna kesa i daska-postolje.
- Bake svetla u Blenderu: noćni i dnevni lightmap, između kojih shader meša po vremenu skrola.
- Shader prozora: svaki prozor u vertex boji nosi „vreme buđenja" (udaljenost od pekare), pa jedna uniforma pali talas. To je jedan draw call, ne stotinu svetala.
- Nebo kao gradijent shader (noć → zora → jutro → veče), magla u boji neba, dim i brašno kao `Points` (par stotina), lažni tilt-shift kao jedan pas u pola rezolucije.
- Putanja kamere iz Blendera kao kriva, GSAP ScrollTrigger + `quickTo` inercija + Lenis.

**Težina: L.** Kod je srednje težak, a veći deo posla je Blender: kit, bake i presek.
**Najveći rizik:** da maketa izgleda kao generički low-poly paket iz prodavnice, a ne kao ručno pravljen Beč. Zato su proporcije gründerzeit fasade, bake svetla i tekstura „maketa od kartona i gipsa" presudni, a recenzent treba da vidi render jedne kuće pre nego što se gradi ceo blok. Drugi rizik je telefon (grad i enterijer u jednoj sceni), pa se pravi podela na dva GLB-a i učitava se samo aktivni deo.

**Zašto baš ovaj klijent:** Ime *Krume* doslovno znači sredinu hleba ispod kore, pa presek grada kao vekne izrasta iz imena, a ne iz efekta. Pekari su jedini budni u gradu u 4 ujutru, i taj jedan prozor je istina zanata. Pekara se ne gubi, jer je ona jedini topao izvor u celoj sceni (pravilo iz briefa) i odatle kreće svako svetlo.

**Inspiracija (princip, ne kopija):**
- Windland, Codrops case study (mini grad u Three.js, različit post-pas za dan i noć radi brzine; datum nije potvrđen): https://tympanus.net/codrops/hub/tag/city
- aldervale, noćni grad sa kamerom na ScrollTrigger-u (samo pogledati, ništa ne preuzimati): https://github.com/ojja/aldervale
- Codrops, Blender putanja kamere + GSAP, 2026-07: https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/
- Oryzo (inercijska kamera) i La Revoltosa (samo aktivna scena, rezervni prikaz), iz `studio/znanje/reference.md`.
- Druga branša: Kaiser Permanente „Moving All to One", brend film od ručno pravljenih minijatura, Creative Circle 2026 (toplina makete): https://www.creativecircle.co.uk/2026winners/moving-all-to-one/a90ae631-6a6c-406e-8179-2c9fb5c918df. Arhitektonski presek-modeli (Schnittmodell) kao princip za „kriška otkriva unutrašnjost".
- Nije nađen nagrađen sajt-diorama 2025–2026 (pretraga Awwwards i Codrops, 2026-10-27), pa je pristup svež, ali bez proverenog uzora.
