# Priručnik: kako se prave „sajtovi od milion dolara“ (7 reelova, 10 sajtova)

Napravljeno 21.10.2026. Lično sam pregledao svaki frejm iz svih 7 reelova (ukupno ~3.000 frejmova).
Detaljne beleške frejm po frejm su u `my-notes.md`. Forenzičke analize (na engleskom) su u `wearebrand-analyses.md`.
Ovaj fajl je sažetak za rad: šta je svaki sajt, kako izgleda od početka do kraja, od čega je napravljen i kako ga mi pravimo.

---

## 0. Dve tehnike (sve što postoji svodi se na ovo)

### A) „AI film“ koji se skroluje (5 sajtova: Pear, Reposé, Larkhaven, Hartleigh & Vane, LITORALE)
1. **Slike ključnih kadrova (keyframes)**: AI slike (Nano Banana / Midjourney / Flux / Higgsfield), sve u ISTOM stilu (ista rečenica stila na kraju svakog prompta + ista referentna slika).
2. **Klipovi između kadrova**: AI video sa početnim i krajnjim kadrom (Kling, Veo, Seedance, Higgsfield). Kraj jednog klipa = početak sledećeg, pa nema reza.
3. **Seckanje u slike**: ffmpeg → 24–30 slika u sekundi, WebP/AVIF, 1920 px desktop + posebna mobilna verzija.
4. **Prikaz**: jedan `<canvas>` preko celog ekrana, „zalepljen“ (sticky) dok skroluješ kroz dugačku sekciju (300–3.000vh). Skrol → broj frejma → `drawImage`. Zato video ide napred/nazad tačno brzinom prsta i staje kad staneš.
5. **Sve ostalo je HTML preko canvasa**: naslovi, tekst, dugmad, meni, brojevi, HUD, tablice.
6. **Motor**: Lenis (mekani skrol) + GSAP ScrollTrigger (scrub + snap na poglavlja).

LITORALE autor na samom reelu piše: **„You used GPT-6 and Higgsfield API for a client's website“** → kod je pisao AI, slike i video su iz Higgsfield-a. To potvrđuje tehniku A.

### B) 3D u realnom vremenu (4 sajta: Ciao Energy, Zero, GQ×AP, Fighter Ready)
1. three.js / React Three Fiber scena (modeli GLB, teksture, svetla, HDRI).
2. Skrol pomera kameru po putanji (spline) i animira objekte; GSAP timeline.
3. Post-efekti: bloom (sjaj), magla, čestice prašine, vinjeta.
4. Tekst i UI su HTML preko canvasa.

**Kada šta:** A je realističnije i brže za izradu ako imaš kredite za AI video (ali teško za preuzimanje: stotine slika). B je oštro, interaktivno, lagano, može da se vrti u krug, ali traži 3D modele.

---

## 1. Pear (agencija za razvoj + SEO, plaća se procentom od zarade) — tehnika A

**Stil:** renesansno ulje na platnu (Bronzino, Alma-Tadema), Magrit nadrealizam, Da Vinčijevi crteži. Boje: kobalt plava (glavna), bledo siva, pergament, zlato, crvena (pojas), maslinasto zelena. Halftone tačkice kao zaštitni znak.
**UI stalno:** levo tanka vertikalna linija + logo kruške + meni od tačaka; gore desno crno „APPLY +“; tanke horizontalne linije; boja UI-a se menja (svetlo/tamno) po sceni.
**Font:** tanki serif (Tiempos/GT Sectra Light) + rukopisna reč + mono oznake u „pilulama“.

**Od početka do kraja (bez ijednog reza):**
1. Hero: levo plavo + naslov „Pear makes you appear.“; desno mladić u tunici izlazi iza zavese sa tačkicama.
2. Odsjaj zvezde na zavesi → beli dim prelazi ekran → mladić vuče zavesu.
3. Kamera ulazi u zavesu → tkanina postaje krem traka.
4. Traka postaje traka za kalemljenje → ruke u somotskim manžetnama kaleme granu kruške.
5. Kalem raste → krošnja puna krušaka → jedna sazri u zlatnu → ruka je bere („We build it.“, „We rank it.“).
6. Kamera pada kroz grane → lice se pojavi kroz lišće → portret mladića sa zlatnom kruškom; seče je („We share in what it earns.“).
7. Dve polovine → kamera ulazi u procep → plavi pravougaonik sa pikselizovanom („dither“) ivicom preplavi ekran.
8. Ravno plavo nebo sa crtanim oblacima od tačkica + tekst + lenjir sa brojačem desno; oblaci plove gore.
9. Odozdo vrh džinovske sive kruške (tačkice) → čovek na skeli je boji zlatom → kamera ide dole niz skelu → žena drži pergament.
10. Kamera ulazi u pergament → pojavi se sepija crtež (radnici guraju zlatnu krušku) → kamera ide gore u tlocrt → slika se smanji u ram levo; desno tekst o cenama koji se „razliva“ pa sklapa slovo po slovo.
11. Plava scena se diže odozdo sa talasastom pikselizovanom ivicom → žena orezuje drvo („We say no more often than yes.“ ulazi sa duplim tragom).
12. Kamera prati krušku koja pada → prsten duge oko nje → prolazi kroz krušku.
13. Pogled odozdo u krošnju: „Asked before *signing*“ (reč se crta), FAQ pitanja plove sleva nadesno povezana linijama.
14. Kamera ide kroz krošnju u nebo → oblaci se zatvaraju u prsten sa zvezdastim otvorom → prolaz kroz otvor.
15. Finale: čovek na mermernim stepenicama među oblacima pokazuje gore; zvezde se pale, crtaju se linije sazvežđa; pojavi se stakleni formular za prijavu.

**Zašto radi:** svaki prelaz je PREDMET koji postaje sledeći predmet (zavesa→traka→kalem→kruška→portret→procep→nebo). Kruška i crveni pojas drže priču. Tekst je mali i uvek na mirnom delu slike.
**Kako se pravi:** ~18 AI slika u stilu ulja, ~10 klipova (start→kraj). Halftone je deo slika; pikselizovane maske i zvezdice su shader/canvas preko; formular i tekst HTML.

---

## 2. CIAO Energy (energetsko piće, francuski) — tehnika B

**Stil:** tamni studio, sjajne 3D limenke, magenta/ljubičasti sjaj odozdo. Font: debeli italic kapitalke.
**UI stalno:** tanka bela linija napretka gore; FR/EN levo; logo u centru; MENU + belo dugme CONTACT desno.

**Od početka do kraja (stranica se vrti u krug):**
1. Vrteška od ~11 limenki u luku; aktivna u centru osvetljena, ostale tamne; hrom prsten sa logom iznad, crni postament ispod sa imenom ukusa; dole klizač u duginim bojama „SCROLLER POUR DÉCOUVRIR“. Vrti se brzo pa stane.
2. Prsten i bočne limenke odlaze, pozadina postane ljubičasta, kamera prilazi limenci; desno 4 ikonice.
3. „POMME RHUBARBE“ levo, ogromna limenka.
4. Limenka se okrene na poleđinu → na SAMOJ ETIKETI svetli roze traka preko reda o kom tekst levo priča; „loš“ sastojak precrtan. 4 puta: manje šećera, prirodne arome, kofein iz kafe, stevija. Naslovi se menjaju „glitch“ trakama.
5. Limenka se vrati napred i smanji → roze magla → iza nje ogroman „ZERO BULLSHIT“ slovo po slovo.
6. Tamne limenke uleću sa strane → 12 limenki u dijagonalnom redu.
7. FAQ (naslov sa 3–4 kasneće bleđe kopije ispod = „eho“) → newsletter → footer → magenta limenka izroni → nazad na početak.

**Kako se pravi:** jedan 3D model limenke (GLB) + 12 tekstura etiketa + poleđina sa maskom redova; metal sa HDRI odsjajima; shader za pozadinu (gradijent, sjaj, magla); ~300 čestica prašine; GSAP timeline ~900vh. Na kraju `scrollTo(0)` za petlju.

---

## 3. Reposé Residence (luksuzna kula, Dubai) — tehnika A + klasičan editorijal

**Stil:** maglovit, topao, filmski AI render; zatim krem/mint stranice. Serif naslovi (red uspravan + red italic). Zeleno WhatsApp dugme stalno dole desno.

**Od početka do kraja:**
1. Hero: dron iznad oblaka (video u petlji), Dubai i Burdž Kalifa na horizontu; „Reposé / Residence“ levo.
2. Skrol: spuštanje kroz oblake → naselje u koncentričnim krugovima.
3. Crna kartica „READY / TO RISE.“ (veo se pojavi pa nestane).
4. AI time-lapse: gradilište sa kranovima u centru kruga → kula raste → gotova kula → nivo očiju u sumrak („WHY DUBAI?“ levo).
5. Kamera gleda kulu gore; „EXPLORE RESIDENCES“ + bela svetla traka preko sprata pod kursorom (biraš sprat).
6. Skok (vidljiv šav) na širi kadar ulice → dolly do ulaza → kroz staklena vrata → lobi (travertin, kamen, bela stolica) „WELCOME TO REPOSÉ“.
7. Pin se otpusti → krem stranica: „Step inside the everyday.“ + 4 kartice sa lučnim vrhom (sobe).
8. „Twelve ways to spend a day.“ + slika + lista; horizontalna galerija (joga, teretana, sauna, vrt) sa paralaksom.
9. Kartica bazena raste do celog ekrana → „Nothing to do. Everything to feel.“
10. Beli krug raste odozdo i prekrije ekran → „Less rush. More Reposé.“ → krovna terasa.

**Kako se pravi:** ~5 lančanih AI klipova (~800 frejmova) na sticky canvasu + HTML; donji deo običan sajt sa GSAP-om (maske luk/krug preko `clip-path`).

---

## 4. Zero (alternativa fakultetu) — tehnika B (WebGL) + AI teksture

**Stil:** mračna akademija × sci-fi; zelena tabla, crno-plavo, vatra žuto-narandžasta, mint tekst sa sjajem. Ukrašena serif slova + rukopisne reči.
**Jedna rečenica razvučena kroz ceo sajt**, reči se pojavljuju u različitim uglovima.

**Od početka do kraja:**
1. Makro novčanice preko celog ekrana; gipsana šaka u ovalu; toplo svetlo PRATI KURSOR.
2. Kamera se odmiče: lažna novčanica od 100 (Franklin sa kapom diplomca).
3. „University sells“ → novčanice lepršaju i GORE (užarene ivice, rupe rastu) → žar.
4. „Paper“ pod zelenim reflektorom.
5. Papiri lete ka kameri („but Companies“) → cepaju se u trake + kartice sa citatima („want Someone“) → let kroz trake („who can do the *Job*“).
6. „see the Disconnect“ → reč implodira u tačku → „and that's Why“ / „we had to Exist“.
7. Portal: segmentirani prstenovi rastu oko tačke → orb sa linijama → „TAP / HOLD“ (drži da uđeš).

**Kako se pravi:** ravni 3D „listovi“ sa AI teksturama novčanica; shader za gorenje (šum + užarena ivica); trake (instanced); prstenovi kao 3D lukovi; čestice; bloom. Jeftinija verzija: AI video za pozadinu, gorenje/tekst/portal u kodu.

---

## 5. GQ × Audemars Piguet (prototip izložbe sata) — tehnika B

**Stil:** bele sobe koje lebde u crnom; svaka sa zakrivljenim video zidom (zalazak, dim, Zemlja iz svemira).
1. Sat na crnom postolju ispred zida sa zalaskom; „+“ tačka za klik; titlovi intervjua dole; talasna linija zvuka sa poglavljima I–III.
2. Kamera odozgo → spušta se na nivo oka.
3. Klizi kroz crnu prazninu do sobe 2 (crno-beli dim, pera) → kruži oko sata.
4. Let do sobe 3 (luk Zemlje, ekrani sa rendgenom mehanizma i robotom).

**Kako se pravi:** 3D model sata (metal + HDRI), 3 sobe, video teksture, kamera po putanji, glas + titlovi + Web Audio talas.

---

## 6. Larkhaven Golf Club — tehnika A (~22 slike, ~20 klipova)

**Stil:** fotorealni dron, američki južnjački teren sa borovima i jezerima, zlatni sat → magenta zalazak; bez ljudi.
**UI stalno:** providna traka gore; DOLE STAKLENA PILULA SA CRVENIM DUGMETOM „Book a tee time“ (uvek vidljiva); desno oznake poglavlja; HUD i tablica rezultata u drugom delu.
**Font:** uski serif + JEDNA reč u italicu („Golf the way it *should* feel.“).

**Od početka do kraja:**
1. Klupska kuća, ružičasto nebo → kran preko krova → jezero („Lake *Larkin*“) → kafa na terasi → iza prvog tee-a.
2. Makro loptica na tee-u („Everything starts *here*.“) → drajver uleti → udarac → kamera leti sa lopticom niz fervej; brojke (brzina, ugao, visina, dužina) se broje, narandžasti luk se crta → „Three feet for *eagle*.“
3. Rez na drugi deo: FPV let dronom kroz rupe 2–6 bez prekida (preko vode i kamenog zida, kroz borovu šumu, preko bunkera, kroz maglu) sa HUD-om „ALT/SPD“ i tablicom.
4. Nebo postaje magenta → ostrvski grin u ružičastom jezeru → „Your tee time is *waiting*.“ + dugme → zelena sekcija sa datumima.

**Trik:** SNAP NA POGLAVLJA — kamera krene kad skroluješ i stane tačno kad je tekst pun. Šavovi između klipova sakriveni u kretanju (krov, tamno lišće, magla).

---

## 7. Hartleigh & Vane (kuhinje po meri, UK) — tehnika A (samo 4 slike, 3 klipa!)

**Stil:** tamni „tihi luksuz“, isti frontalni kadar sobe sve vreme. Zelene shaker kuhinje, beli mermer, mesing; dan → veče.
1. Prazna soba (sunce kroz prozor); „Scroll to fit the kitchen“.
2. Ormarići RASTU iz poda (prvo krajevi pa sredina), slavina iskoči, zidni ormarić se „odmota“ („Scribed to the wall“).
3. Mermerno ostrvo uklizi zdesna i stane ispod nape („One slab, folded“).
4. Lampe se spuste i upale, mermer se digne na zid, dan prelazi u veče („Warmed by degrees“).
5. Tekst pređe desno: „Supper at eight“ + dugme. Pin se otpusti → tamni editorijal (brojke, zanat, 5 dana, galerija, citat, kontakt).

**Najvažniji trik za izradu:** PRVO generiši GOTOVU kuhinju, pa UNAZAD briši elemente (isti kadar) → kamera je identična u svim kadrovima. Klipovi „static tripod, no camera movement“.

---

## 8. Fighter Ready (app za borilačke sportove) — tehnika B (izgled kao igrica)

**Stil:** tamno plavo-crno, beton, narandžasto-crveni akcent, svetleća užad ringa, bloom, prašina, magla.
**UI stalno:** puna tamna traka sa 8 linkova (aktivan ima narandžastu podvlaku koja skače); levo traka napretka; tekst levo: „● ROUND 0X — IME“, ogroman uski debeli naslov sa tačkom, 1 rečenica, „READ MORE“.
1. Fasada, narandžasta staklena vrata, osvetljen FR znak; „SCROLL TO ENTER“.
2. Kamera prilazi, vrata se otvaraju, narandžasti bljesak → hodnik sa posterima („MATCHMAKING IS BROKEN.“).
3. Sala sa ringom, reflektori → kamera kruži oko ringa („EVERY MATCH, SAFELY.“).
4. Brz pan → dva boksera se spare (animacija u petlji) („THE RIGHT ROUNDS.“).
5. Džakovi pod narandžastim svetlom („GET FIGHTER READY.“) → zid profila sa okruglim lampama („ANYONE CAN START.“).
6. Tamni stub prebriše ekran → arena sa publikom i ringom pod trusom („FIRST SLOT TO FINAL BELL.“).

**Tekst uvek isto:** ulazi odozdo-levo (blur → oštro, slovo po slovo), stoji dok kamera ide, izlazi gore ispod menija.

---

## 9. LITORALE (arhitekte, grčka ostrva) — tehnika A (Higgsfield)

**Stil:** fotorealni dron; svetlo ide kroz ceo sajt od zlatnog sata do noći. Font: ŠIROKI debeli sans (Monument Extended) u kapitalkama + mono oznake.
1. Hero: brdo iznad tirkiznog zaliva; ogroman „LITORALE“ preko dna; zlatni zrak preleti travu.
2. „LITORALE“ nestaje → „VILLA AMMOS“ → TIME-LAPSE GRADNJE sa nepomičnom kamerom: plato → iskolčavanje → temelj → armatura → drveni skelet → zidovi → sprat → krov → bazen se napuni → drveće raste. Status i tekst se menjaju po fazi (FOUNDATION … COMPLETED).
3. Pretapanje → „VILLA SALINA“: dina, beli kikladski zidovi i stakleni paviljon izrastaju.
4. Pretapanje → „VILLA MELTEMI“: kanal sa palmama, čelik i staklo, bazen; na kraju DAN → SUMRAK u istom kadru, upale se svetla, pojavi se auto.
5. Pretapanje → „VILLA AUREA“ (plavi sat): kamera ide kroz staklena vrata, kroz dnevnu sobu sa lebdećim stepeništem, na terasu, preko bazena ka gradu.
6. Kamera se naginje u vodu → crno → MANIFEST se „dekodira“: tačke → izmešana slova → plavo-cijan eho kopije se skupe → čist tekst („We let the *coastline* finish the drawing we begin.“).
7. „FOUR VILLAS IN THE…“ + lista radova.

**Najvažniji trik:** hero JE prazna parcela prve vile, pa nema prelaza iz „naslovne“ u „sadržaj“. Prazan plac se pravi BRISANJEM kuće iz gotove slike (isti kadar).

---

## 10. Zajednički recept: zašto ovi sajtovi izgledaju kao milion dolara

1. **Jedan svet, jedna kamera, bez rezova.** Scene se menjaju kroz predmet (morf), prolazak kroz vrata/lišće/maglu, ili pretapanje u istom kadru.
2. **Skrol je daljinski za film.** Kamera se kreće, pa STANE dok čitaš (snap na poglavlja).
3. **Priča sa lukom:** prazno → izgrađeno; napolju → unutra; dan → noć; problem → rešenje → poziv.
4. **Malo teksta:** mala mono oznaka + veliki naslov sa JEDNOM reči u italicu + 1–2 rečenice koje opisuju TAČNO ono što vidiš u tom trenutku.
5. **Tekst u uglovima koji se smenjuju** (levo dole → desno dole), uvek na mirnom delu slike, sa blagim gradijentom ispod.
6. **UI uvek tu:** tanak meni, brojač poglavlja / traka napretka, glavno dugme (rezervacija/prijava) uvek vidljivo.
7. **Jedna paleta i jedan stil** kroz ceo sajt (ista rečenica stila u svakom AI promptu).
8. **Posle filma ide miran klasičan deo** (brojke, usluge, galerija, citat, kontakt) — da sajt bude i koristan, ne samo lep.

## 11. Katalog efekata → kako se prave u kodu

| Efekat | Gde | Kako |
|---|---|---|
| Video ide sa skrolom | A sajtovi | sticky canvas + ScrollTrigger `scrub` → `frame = round(p*(N-1))` → `drawImage` (cover) |
| Kamera staje kod teksta | Larkhaven | ScrollTrigger `snap` na labele timeline-a |
| Pretapanje dve scene | LITORALE, Reposé | nacrtaj oba frejma, drugi sa `globalAlpha` 0→1 preko ~3% skrola |
| Pikselizovana („dither“) ivica | Pear | WebGL shader: prag šuma/Bayer matrice koji raste |
| Krug/luk otkrivanje | Reposé | `clip-path: circle(0%→150% at 50% 100%)` |
| Naslov blur → oštro | svi | GSAP: `opacity 0, y 40, filter blur(12px)` → 0, SplitText po slovima/redovima |
| Glitch trake | Ciao | 6 kopija naslova, svaka `clip-path: inset()` jedna traka, pomeraj ±20px, 0.1 s |
| Eho kopije naslova | Ciao, Pear | 3–4 kopije sa opacity 1/.4/.2/.1, svaka prati skrol drugim kašnjenjem |
| Dekodiranje teksta | LITORALE | tačka → nasumična slova 4–6 tikova → pravo slovo; eho ±0.3em cijan, jačina = brzina skrola |
| Reč se crta rukom | Pear, Zero | SVG putanja, `stroke-dashoffset` animacija |
| Brojke se broje | Larkhaven, H&V | GSAP tween na broj, `textContent` |
| Svetlo prati kursor | Zero | radijalni gradijent / point light na poziciji miša sa lerp |
| Gorenje papira | Zero | shader: `n = fbm(uv)`, `discard n<p`, užarena ivica `smoothstep(p, p+.04, n)` |
| Sjaj, prašina, magla | Fighter, Ciao | three.js UnrealBloom, Points (~2.000), FogExp2 |
| Uvek vidljivo dugme | Larkhaven, Pear | `position: fixed` staklena pilula (`backdrop-filter: blur`) |
| Traka napretka / brojač | Fighter, LITORALE, Ciao | `scaleY/scaleX` = progres skrola; „01 / 04“ |

## 12. Proizvodnja AI slika i videa (tehnika A), korak po korak

1. **Art direkcija:** jedna rečenica stila (svetlo, paleta, sočivo, „no people“, 16:9) + jedna referentna slika. Ista za SVE.
2. **Lista kadrova:** za svako poglavlje 1 kadar; za svaki prelaz zamisli predmet koji spaja dve scene.
3. **Gotovo stanje prvo:** ako se nešto gradi (kuća, kuhinja, sajt), generiši ZAVRŠEN kadar, pa unazad briši delove (edit sa istim kadrom).
4. **Klipovi:** start → kraj, 5–8 s; za zaključanu kameru napiši „static tripod, no camera movement“; za let „FPV drone“. Više pokušaja, uzmi najstabilniji.
5. **Spajanje:** poslednji frejm klipa = prvi frejm sledećeg; šavove sakrij u pokretu (lišće, magla, tama, vrata).
6. **Izvoz:** `ffmpeg -i clip.mp4 -vf "fps=24,scale=1920:-2" -c:v libwebp -quality 70 f_%04d.webp` + mobilna verzija (1080×1350 ili 9:16). Prvo poglavlje učitaj odmah, ostala u pozadini.
7. **Front:** sticky canvas + Lenis + GSAP; tekst/UI kao HTML; `prefers-reduced-motion` → statične slike.

**Cena (Artlist, 21.10.):** slika ~160 kredita, klip 5 s ~500–750 kredita. Sajt kao Hartleigh: 4 slike + 3 klipa ≈ 2.900 kredita. Sajt kao LITORALE/Larkhaven: 10–20 slika + 7–20 klipova ≈ 6.000–17.000 kredita (bez ponavljanja).
