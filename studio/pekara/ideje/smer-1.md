## Dein Schnitt (ritual)

**U jednoj rečenici:** Skrol je jedna noćna smena od 04:00 do 07:00 i jedan neprekinut let kamere koji prati jedan isti komad testa od stola do vitrine, a posetilac mu sam napravi rez nožem pre nego što ode u peć.

**Potpisni trenutak:** Rez koji je posetilac sam povukao po testu pukne u peći, kora se rascveta duž njegove linije, a kamera kroz tu užarenu pukotinu izleti u radnju gde je već jutro.

**Raspoloženje:** tiho · toplo · zanatski · noć `#14110f`, kora `#7a4a24`, žar `#e8792b`, testo `#eadbc4`, brašno `#f6f1e7`, prozor pre zore `#3a4a5e` (jedina hladna boja) · široki groteskni naslov (Bricolage Grotesque, već je u `pekara/assets/fonts/`) + mirni serif za tekst (OFL, bira dizajner)

**Mapa skrola** (sat u uglu ide uz skrol; kamera ima inerciju, nikad ne skače 1:1 za točkićem)

| Vreme | Kamera | Šta se animira | Tekst (DE) |
|---|---|---|---|
| 04:00 Dunkel | Kreće iz potpunog mraka, polako se spušta kroz snop jedne lampe nad stolom | Brašno lebdi u snopu (čestice), peć tinja u dubini | Naslov je ispisan prstom u brašnu na stolu i otkriva se kako svetlo pređe preko njega: „Bevor Wien aufwacht, backen wir." |
| 04:20 Teig | Spušta se nisko, kruži oko kugle testa | Testo se mesi i preklapa (morph), puf brašna na svaki pregib | „Teig. Mit der Hand und mit Geduld." |
| 04:50 Zeit | Klizi bočno duž police sa korpama za narastanje | Testa u korpama narastaju jedno za drugim kao talas; zidni sat ubrzano vrti kazaljke; prozor iz crnog prelazi u tamnoplavo | „Zeit ist die Zutat, die man am Ende schmeckt." |
| 05:30 Schnitt | Staje iznad testa na lopati (pin, skrol pauzira) | **Interakcija** (vidi ispod) | „Jetzt du. Ein Schnitt." |
| 05:45 Ofen | Jaše na lopati u peć; vrata peći se otvore i narandžasta svetlost preplavi ekran | Testo raste ka kameri, boja ide iz testa u koru, rez se otvara | „Ofen. 250 Grad." |
| 06:15 Brot des Tages | Izleće kroz pukotinu i spušta se duž staklene vitrine | Kaisersemmel, Mohnwecken, Laugenbrezel, Roggenlaib, jedan po jedan u fokusu, para iznad toplih | ime, jedna rečenica, cena; hleb sa posetiočevim rezom stoji prvi u redu |
| 06:30 → 07:00 Aufsperren | Okreće se ka vratima radnje, vrata se otvore ka ulici | Svetlo iz plavog prelazi u toplo jutro, 3D se gasi u svetlu HTML stranu | „Wir sperren auf." Di–Sa 6:30–14:00 · „Dein Sackerl für morgen" (Vorbestellen; na papirnoj kesi piše ime iz forme) |

**Interakcija:** posetilac sam „zaseče" testo: mišem ili prstom povuče liniju po površini, pa ona ostane na hlebu do kraja sajta (otvori se u peći i stoji na hlebu u vitrini). Ako ne želi, tri dugmeta daju gotove rezove (Kreuz, Ähre, Einzelschnitt). Na telefonu je rez **vodoravni** prevlak unutar označenog okvira, pa se ne bije sa vertikalnim skrolom (`touch-action` samo na tom okviru).

**Telefon (390 px):** ista putanja, ali kamera je odmaknuta i ima širi FOV jer je kadar uspravan. Tekst je HTML preko scene, donja trećina ekrana. DPR najviše 1,5, bez post-procesa u punoj rezoluciji, vitrina bez prave transmisije (refleksija iz env mape). Hlebovi se učitavaju tek kad kamera priđe vitrini.
**prefers-reduced-motion:** bez Lenisa i bez leta kamere. Svako poglavlje je jedan statičan kadar renderovan u Blenderu iz iste scene (7 slika, uz sat), običan skrol, bez čestica. Rez se bira od tri gotova, a prikazuje se fotografija hleba sa tim rezom. Sav sadržaj (hlebovi, radno vreme, Vorbestellen) je i inače pravi HTML, pa radi i bez WebGL-a.

**3D modeli, materijali, shaderi**
- Enterijer kao jedan GLB (Meshopt, KTX2): sto za mešenje, police, 6–8 korpi za narastanje (jedna geometrija, instancirano), peć sa vratima (rig za otvaranje), lopata, vitrina, rešetka za hlađenje, zidni sat, ulazna vrata sa prozorom. Svetlo **zapečeno u Blenderu** (lightmap), uživo su samo sjaj peći i boja prozora.
- Testo: jedan mesh sa morph target-ima (3 faze mešenja, narastanje, pečeno). Shader: `uBake` 0→1 (testo → kora, šum za neravnu boju), maska reza iz canvas teksture koju crta posetilac (pomera temena i otkriva svetlu sredinu).
- 4 hleba (low-poly + normal mapa, učitavaju se na zahtev); posetiočev rez se kao maska nanosi i na njih.
- Kriva putanje kamere iz Blendera (tačke u JSON), GSAP ScrollTrigger vodi parametar, `quickTo` daje inerciju.
- Čestice brašna (Points + jednostavan shader), lažni volumetrijski snop (konus sa aditivnim gradijentom), para (sprite).
- Natpis u brašnu: decal sa maskom koja se otkriva svetlom. Papirna kesa (Sackerl) sa tekstom imena kao canvas tekstura.

**Težina:** L. Enterijer sa zapečenim svetlom i putanja kamere su poznat posao (M); rez koji crta posetilac, pa se otvara u peći, i let kroz pukotinu su ono što ovo diže na L.

**Najveći rizik:** da „pucanje" kore duž proizvoljne linije u shaderu izgleda gumeno umesto kao prava kora, a prolaz kamere kroz pukotinu kao greška u renderu. Rezerva: tri gotova reza sa pripremljenim morph target-ima u Blenderu, a prolaz kroz pukotinu kao blic narandžaste svetlosti preko celog ekrana (to je i brief-ov trenutak sa vratima peći). Drugi rizik: lightmap enterijera je težak za telefon, pa ga treba držati ispod 2 MB.

**Zašto baš ovaj klijent:** pekara prodaje ritual koji niko ne vidi jer se dešava dok grad spava. Rez na hlebu je pekarov potpis (svaki pekar ima svoj), a ovde ga dobija i gost, pa je „Dein Sackerl" sa njegovim imenom i rezom kraj iste priče.

**Inspiracija** (iz `studio/znanje/reference.md` i `trendovi.md`, 27. 10. 2026; sajtovi nisu otvarani u browseru)
- Codrops, putanja kamere iz Blendera + GSAP (2026-07): princip krive i dve vrednosti za inerciju.
- Oryzo / Lusion (SOTM 04/2026, NEPROVERENO): kamera koja zaostaje, proizvod je uvek junak.
- La Revoltosa (Awwwards članak, 2026-07): tekst kao deo scene, učitavanje samo aktivnog modela, običan prikaz kao rezerva.
- Druga branša: Explore Primland (SOTD 02/2026, NEPROVERENO), jedan neprekinut let umesto sekcija; Cartier / Immersive Garden (2026), satni mehanizam kao ritam, zvuk kao opcija (pucketanje kore, samo na klik).
