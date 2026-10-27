## Ins Innere der Krume

**U jednoj rečenici:** Skrol je mikroskop: kamera počinje od zrna brašna od 0,1 mm, prolazi kroz testo, mehuriće i koru u peći i vraća se do hleba od 30 cm na pultu. Lenjir za razmeru u uglu stalno pokazuje gde smo, pa makro nikad ne postaje apstraktan.

**Potpisni trenutak:** Kamera je unutar jednog mehurića vazduha, u toploj pećini sa sjajnim zidovima, i u jednom neprekinutom povratnom zumu izlazi kroz zid. Tada se vidi da je ta pećina samo jedna rupica u preseku Roggenlaiba na dasci, a lenjir ide od 2 mm do 8 cm.

**Raspoloženje:** toplo · blisko · radoznalo. Paleta iz briefa: noć `#14110f`, kora `#7a4a24`, žar `#e8792b`, testo `#eadbc4`, brašno `#f6f1e7`, plus krume `#d9c29a`. Fontovi: Bricolage Grotesque (već je u projektu) za naslove i monospace sa OFL licencom za lenjir i brojeve (npr. IBM Plex Mono).

**Čitljivost i toplina:** (1) Lenjir za razmeru sa nemačkim natpisom, npr. „0,1 mm · ein Mehlkorn", „2 mm · eine Luftblase", „8 cm · ein Laib". (2) Svetlo je uvek jedno i toplo, bez hladnog plavog i bez neona. (3) Ispod svakog poglavlja je jedna kratka rečenica o zanatu, ne dekoracija. (4) Testo je mekano i providno, kao da svetlo ulazi u njega, a ne plastika.

**Priča skrola**
1. **Hero „Krume."** Presek Roggenlaiba izbliza, u mraku. Pod naslovom stoji „Das Beste ist innen." Na prvi skrol kamera klizi ka jednoj rupici i uranja u nju (prelaz kroz tamu).
2. **Mehl · 0,1 mm.** Zrna brašna lebde kao topla prašina u snopu svetla, a kamera polako prolazi između njih. Tekst: „Mehl, Wasser, Salz. Mehr nicht."
3. **Teig · 1 mm.** Kapi vode spajaju zrna, a vlakna glutena se istežu u mrežu kad se skroluje napred i vraćaju kad se skroluje nazad. Tekst: „Teig. Mit der Hand, mit Geduld."
4. **Zeit · 2 mm.** Mehurići rastu u testu dok skrol odmiče, a sat u lenjiru ide od 18:00 do 04:00 (veza sa idejom iz briefa). Ovde je interakcija (vidi ispod). Tekst: „Zeit. Der Sauerteig reift über Nacht."
5. **Ofen · 5 mm.** Kamera je na površini testa, boja posmeđi od ivice ka sredini (Maillard), a kora puca i u pukotinama sija žar. Uz to ide tihi zvuk pucketanja, samo ako ga gost uključi. Tekst: „Ofen. 250 Grad. Die Kruste singt."
6. **Potpisni povratni zum.** Iz mehurića nazad do celog hleba na dasci. Lenjir se vrti do 8 cm.
7. **Brot des Tages.** Četiri hleba, svaki prerezan na pola, i svaki pokazuje svoju sredinu: Kaisersemmel „Krume: luftig", Mohnwecken „fein", Laugenbrezel „dicht, glänzend", Roggenlaib „kräftig, grob". Na desktopu se menjaju na skrol, na telefonu na prevlačenje. Uvek je učitan samo aktivni model.
8. **07:00 · Wir sperren auf.** Kamera se još malo povlači, pa se vidi pult i papirno Sackerl sa imenom. Radno vreme (Di–Sa 6:30–14:00) i forma „Vorbestellen" su običan HTML preko scene, isti sadržaj kao sada.

**Interakcija: „Fingerprobe".** U poglavlju Zeit gost drži prst ili miš na testu. Testo se ugne i polako vraća, a tekst kaže: „Langsam zurück? Dann ist er bereit." To je prava pekarska proba testa, pa igra uči nešto o zanatu. Što duže drži, mehurići malo više narastu.

**Telefon (390 px):** Kadar je vertikalan, tekst je dole u traci, a lenjir gore. Zrna brašna su upola ređa, DPR je najviše 1,5, post-procesiranje je samo jedan lagani grain ili ništa. Fingerprobe radi na dugi pritisak, a skrol se ne blokira. Hlebovi se menjaju prevlačenjem, a mala dugmad 1–4 su rezerva.
**prefers-reduced-motion:** Kamera nije vezana za skrol i nema Lenisa. Svako poglavlje je jedan statičan kadar renderovan iz iste Blender scene (WebP), uz isti lenjir i tekst. Povratni zum se zamenjuje dvema slikama jedna pored druge, „2 mm" i „8 cm". Fingerprobe je statična slika sa rečenicom. Nema čestica ni grain-a. Hlebovi su obična mreža od četiri kartice.

**Video i mediji:** Sve je 3D uživo, osim statičnih rezervnih kadrova iz Blendera. AI video ne treba. Postojeće fotografije sa Unsplash-a mogu da posluže kao referenca boje za teksture kore. Zvuk pucketanja je besplatan (Codex ga traži u `promptovi/codex.md`).

**Šta treba napraviti (Blender → GLB, Three.js WebGL)**
- *Zrna brašna:* jedan izobličen ikosfer kao instanced mesh (oko 2.000 komada na desktopu, oko 800 na telefonu).
- *Vlakna glutena:* 30–60 cevi na krivama, istezanje kroz vertex shader.
- *Površina testa:* gusta ravan sa vertex shaderom za ugib i oprugu (Fingerprobe) i lažnim svetlom koje ulazi u testo (wrap lighting i boja po debljini).
- *Pećina mehurića:* glavni asset. U Blenderu se pravi kao Voronoi ili metaball koji se oduzme od kocke, sa remesh-om, pa se ispeku normal i AO mape. Unutra je jedno toplo svetlo i sjaj vlažnih zidova (fresnel).
- *Mehurići koji rastu:* sfere sa fresnel shaderom, veličina vezana za skrol.
- *Kora:* ravan sa displacement mapom, a maska pukotina se otvara po pragu, sa emisivnim žarom u pukotinama i jednim uniformom za smeđu boju.
- *Hlebovi:* 4 GLB modela, svaki prerezan, sa ispečenom teksturom preseka (Meshopt, KTX2, 1024 px na telefonu). Uz to Roggenlaib na dasci i Sackerl.
- *Kamera:* putanja nacrtana u Blenderu, sa inercijom (`quickTo`).

**Tehnika i rizici:** Težina je **L**. Najveći rizik je prelaz između razmera, jer jedan neprekinut svet od 0,1 mm do 30 cm nije izvodljiv u browseru. Rešenje je trik iz „Powers of Ten": svaka razmera je posebna scena, a promena se sakrije kad kamera prođe kroz tamnu poru ili zid mehurića. Učitava se samo sledeća scena. Jedini pravi neprekinut zum je potpisni (mehurić → presek), a izvodi se kao jedan model sa dve razmere detalja. Drugi rizik je da pećina izgleda kao sunđer ili kamen. To se proverava rano: prvo jedan render iz Blendera, pa tek onda kod. Treći rizik: Fingerprobe ne sme da ukrade skrol na telefonu (zato dugi pritisak i `touch-action`).

**Zašto baš ovaj klijent:** Ime „Krume" doslovno znači ono u šta ulazimo. Smer pokazuje ono što pekara prodaje, a na fotografiji se ne vidi: vreme i vazduh u hlebu. Poglavlja su ista kao u briefu (Teig, Zeit, Ofen), samo gledana iznutra.

**Inspiracija**
- Charles i Ray Eames, „Powers of Ten" (film, 1977): neprekinut zum sa oznakom razmere na ekranu. Odatle je preuzet lenjir kao sidro, a ne izgled. Stariji izvor, namerno van branše.
- Awwwards elementi sa oznakama zoom/scale, samo kao trag, datum i nagrada nisu provereni: https://www.awwwards.com/inspiration/zoom-in-egeon, https://www.awwwards.com/inspiration/zoom-scroll-intro-telescope
- La Revoltosa (2026-07, Awwwards studija slučaja): učitava se samo aktivni model i postoji običan prikaz kao rezerva. https://www.awwwards.com/la-revoltosa-rebooting-a-70-year-old-spanish-soda-brand-for-the-scroll-generation.html
- Oryzo / Lusion (SOTM 2026-04, NEPROVERENO) i Codrops 2026-07-07: kamera sa inercijom po putanji iz Blendera. https://tympanus.net/codrops/2026/07/07/building-a-scroll-driven-3d-gallery-using-a-blender-camera-path-with-three-js-and-gsap/
- Codrops, metaballs kao kapi (2025-06), za izgled mehurića: https://tympanus.net/codrops/2025/06/09/how-to-create-interactive-droplet-like-metaballs-with-three-js-and-glsl/
- Napomena: nijedan od ovih sajtova nije otvoren u browseru. Nagrađen makro-sajt hrane iz 2025–2026 nije nađen.
