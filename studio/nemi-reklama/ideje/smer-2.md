## Soba u ekranu

**1. Ideja u jednoj rečenici:** Jedna uska, visoka voksel soba (oblika ekrana telefona) na svaki udarac menja rekvizite i svetlo, pa postaje kafić, studio, hotel i kancelarija, a na ekranu se reč po reč slaže rečenica sa sajta „Riechen, fühlen, sehen, hören.“ Šesto čulo je otkriće da je soba sve vreme bila u telefonu.

**2. Trenutak koji se pamti:** Posle sekunde tišine telefon zabruji, kamera se povuče unazad i vidi se da je mala soba sa sva četiri čula sve vreme stajala u ekranu voksel telefona: „Und der *sechste Sinn*.“

**3. Raspoloženje:** toplo · opipljivo · tiho. Voksel paleta od 8 boja: ink `#0b0b0c`, ink-2 `#121315`, bone `#efeae2`, bone-2 `#e4ddd2`, signal `#ff5a24` i 3 topla siva. U svakoj sceni je narandžast samo jedan predmet, nosilac čula (šoljica, prostirka, sunce u prozoru, lampa). Svetlo je jedan topao izvor kao u maloj radnji uveče, sa dubokim senkama i mutnom pozadinom (DOF). Ključne reči su u Instrument Serif kurzivu narandžaste, CTA u Geist-u, oznake u Geist Mono. Muzika je minimalni beat od 120 BPM (postojeći `beat.wav`, udarac na 15 kadrova), koji na „hören“ staje na jednu sekundu. Svaka zamena ima svoj zvuk.

**4. Tok (30 fps, 300 kadrova).** Tekst stoji u koloni x 80–900 px, y 220–1450 px, dakle ništa ispod 1536 px ni desno od 950 px. Gore levo je od kadra 0 do kraja sitan mono natpis „NEMI STUDIO“.

| s (kadrovi) | Slika · kamera · prelaz | Tekst na ekranu | Zvuk |
|---|---|---|---|
| 0–1 (0–29) | Makro: narandžasta šoljica na pultu, pikselna para se uvija ka sočivu, lik njuši. Kamera polako prilazi (push-in) sve do 4 s | „*Riechen*,“ pada iz 3D u kadru 0 · mono „01 · CAFÉ“ | kick + šištanje aparata |
| 1–2 (30–59) | **Rez na udarac:** ista soba, sada prostirka i teg. Lik se isteže | „Riechen,“ se smanji i ode gore (bone), krupno ulazi „*fühlen*,“ · „02 · STUDIO“ | kick + tup udarac tega |
| 2–3 (60–89) | Rez: krevet. Zavese se razmaknu (6 kadrova), u prozoru je narandžasto sunce. Lik zakloni oči | „*sehen*,“ · „03 · HOTEL“ | kick + kratak whoosh |
| 3–4 (90–119) | Rez: sto, sat, svetlo samo na lampi. Lik stavi ruku na uvo | „*hören*.“ Gore sada stoji cela rečenica · „04 · KANZLEI“ | muzika staje, čuje se samo „tik“ (90, 105) |
| 4–5,5 (120–164) | Soba zadrhti, pa se kamera povuče unazad: soba je ekran voksel telefona koji lebdi u mraku. Oko telefona su pikselne linije vibracije | „Und der“ (120) „*sechste Sinn*.“ (128) | „brrr“ (120, 135) + whoosh pri povlačenju |
| 5,5–7,5 (165–224) | Telefon miruje, a soba u njemu menja rekvizite na svaki udarac (sve četiri branše) | „Websites, die man“ (165) „*spürt*.“ (180, telefon opet zadrhti) | beat se vraća. Na 180 hit + „brrr“, tiho „tik“ na svaku zamenu |
| 7,5–9,5 (225–284) | Isti kadar. Soba se do kadra 284 vrati na kafić | „nemistudio.at“ (krupno) + mono „Erstgespräch · 30 Min. · kostenlos“ | hit na 225 |
| 9,5–10 (285–299) | Kamera uleti u ekran i stane tačno u kadar 0. CTA se raspadne u piksele | (nema) | obrnuti whoosh koji se završava kick-om kadra 0, pa sledi **petlja** |

Bez zvuka priču nosi tekst, a tišinu pokazuju „hören.“, sat i ruka na uvu. Vibraciju vide i oni bez zvuka, preko pikselnih linija. Za naslovnu sliku (cover) uzima se kadar 200: telefon sa sobom i slogan.

**5. Materijal po programu (procena za početnika)**
- **MagicaVoxel, oko 1 h 45 min.** Soba 32 × 56 × 24, otvorena spreda, sa prozorom (30 min). Četiri kompleta od po 2–3 prosta predmeta: pult i šoljica; prostirka i teg; krevet i dve ploče zavesa; sto, lampa i sat (60 min). Telefon 40 × 80 × 4 sa otvorom tačno po meri sobe (15 min). Izvoz u OBJ.
- **Blender, oko 2 h, plus oko 30 min rendera bez nadzora.** Uvoz modela, sa materijalom na *Closest* da vokseli ostanu oštri (20 min). Četiri kolekcije čija se vidljivost u renderu ključa na markerima udaraca (25 min). Jedno toplo svetlo i jedno narandžasto, kojima se po čulu menjaju boja i jačina (30 min). Kamera sa 3 ključa (blizu → unazad → isto kao kadar 0), DOF i Noise modifikator za vibraciju (30 min). Sprajtovi iz Pixeloram-e kao ravni (*Image as Plane*, sekvenca, *Closest*), po jedan u svakoj kolekciji (15 min). Render u EEVEE-u, 1080 × 1920, PNG.
- **Pixelorama, oko 1 h 45 min.** Lik 16 × 24 px u 4 poze po 2 kadra (njuši, isteže se, zaklanja oči, sluša), plus 2 kadra mahanja (60 min). Para kao petlja od 6 kadrova (15 min). Četiri ikonice 24 × 24 (nos, šaka, oko, uvo) uz mono oznake (20 min). Linije vibracije u 3 kadra (10 min).
- **Remotion, oko 1 h 30 min (kod studija).** PNG sekvenca kao pozadina, a preko nje tekst reč po reč (postojeći `TekstURitmu`) i slaganje rečenice. Ikonice se skaliraju celim brojem, uz `pixelated`. Zvuk čine postojeći `beat`, `tick`, `hit` i `whoosh`, a nove „zisch“, „brumm“ i „thud“ pravimo ffmpeg-om u `sfx.sh`, bez preuzimanja sa interneta.
- **Ukupno: oko 7 h rada, plus render.**

**6. Rizik: šav petlje i pomak od jednog kadra.** Blender počinje od kadra 1, a Remotion od 0, pa rekviziti kasne za reč, a petlja „skoči“. Kako to izbeći: u Blenderu postaviti *Frame Start* 0 i *End* 299, a markere na svakih 15 kadrova. Poslednji ključ kamere je kopija prvog na kadru 300. Kafić je vidljiv od 285 do 299. U Remotion-u se sve računa iz `BEAT = 15`, a pre izvoza se petlja pregleda u studiju.

**Inspiracija (princip, ne kopija):** analizirani reel iz brief-a (15. 10. 2026): reč po reč na udarac, voksel soba sa DOF-om, pikselni vodič · Subway Singapur, maj 2026 ([marketing-interactive.com](https://www.marketing-interactive.com/subway-singapore-rolls-out-scent-sational-ooh-campaign), druga branša): svako čulo dobija svoj fizički nosač, kod nas jedan narandžasti predmet · IKEA „Room To Change“ ([lovethework.com](https://lovethework.com/work-awards/campaigns/room-to-change-1496734), 2021, starije, samo princip): ista soba sa malom promenom · Coca-Cola „Try Not to Hear This“ (David, 2019, [creativebloq.com](https://www.creativebloq.com/news/can-you-hear-these-coca-cola-print-ads), samo princip): slika koja pali drugo čulo · pikselna estetika u brendingu 2026 ([dubaimonsters.com](https://dubaimonsters.com/pixel-art-y2k-inspired-logos-nostalgic-vibes-in-2026-branding/), jan. 2026, mišljenje) · „63 % uspešnih reklama kaže poruku u prve 3 s“ ([bevycommerce.com](https://bevycommerce.com/insights/tiktok-ads-strategy-creative-best-practices-for-2026)), **NEPROVERENO**, prenosi se TikTok podatak.

**Za proveru:** brief ne kaže koje čulo ide uz koju branšu (ovde: Café–riechen, Studio–fühlen, Hotel–sehen, Kanzlei–hören). Uporediti sa sajtom. Ako se razlikuje, menjaju se samo oznake i redosled rekvizita. Nemački CTA proverava `tekstopisac`.
