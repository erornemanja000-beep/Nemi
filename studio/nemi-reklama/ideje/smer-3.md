## Würfel für Würfel

**U jednoj rečenici:** Pikselni majstor čekićem razbije sivi šablon-telefon, raščisti ga do prazne ploče i za četiri sekunde sagradi pravi Nemi sajt kocku po kocku. Poslednja kocka koju postavi je narandžasto dugme sa pozivom na razgovor.

**Trenutak koji se pamti:** Prva kocka koju majstor uhvati je narandžasta. Nosi je kroz celu gradnju, na kraju je zakuca u ekran kao dugme, i na taj „klak" se upali ceo sajt.

**Raspoloženje:** zanatski · razigrano · precizno.
Boje: prostor ink `#0b0b0c`, ploča ink-2 `#121315`, sajt bone `#efeae2` / bone-2 `#e4ddd2`. Narandžasta `#ff5a24` je samo na šlemu majstora, na reči u kurzivu i na poslednjoj kocki. Šablon je namerno mrtvo siv (`#8c8c8c`, `#c9c9c9`), van brenda.
Svetlo ide u tri koraka: prvo ravno, kancelarijsko odozgo. Zatim mrak i jedan topli spot na praznoj ploči („Null"). Na kraju ekran sajta svetli sam (emisija) i obasjava majstora.
Muzika i zvuk: 120 BPM, udarac na svakih 15 kadrova (kao u `motion/`). Gradnju prati niz „tok" zvukova koji se ubrzava u rafal, a „klak" dugmeta je drop. „Tok" i „klak" se snime telefonom: drvena kocka udari o sto, tri snimka. Ostalo se pravi ffmpeg-om, kao postojeći `sfx/`. Bez zvuka poruku nose natpisi.

**Tok (30 fps, k = kadar).** Tekst je levo poravnat, na x 72–900 i y 200–1500 px. Telefon je ~70 px levo od centra, a dugme je na y ≈ 1050.

| s | Slika i kamera | Tekst na ekranu | Prelaz i zvuk |
|---|---|---|---|
| 0–0,5 | Ogroman pikselni čekić se povlači od kamere i otkriva sivi šablon-telefon. Iza njega su u izmaglici još dve iste kopije. Kamera miruje na 120 mm, slika deluje ravno. Majstor je levo, u zamahu. | „Noch ein *Baukasten*?" (sivo) | kraj prelaza iz prethodnog kruga, whoosh se gasi |
| 0,5–1 | k15: udarac. Sive kocke prsnu ka kameri i padnu na ploču. Kamera se trese 6 kadrova. | natpis se raspadne u piksele (glitch) | hit, krckanje, zveckanje kocki |
| 1–2,5 | Kamera se odmiče i diže, žižna daljina ide sa 120 na 50 mm, pa ravna slika dobija dubinu. Ruševina tone u ploču i svetla se gase. Ostaje spot. Majstor doskoči na red teksta, a k60 mu u ruke padne narandžasta kocka. | „Wir bauen von *Null*." („Null" narandžasto) | whoosh, klik prekidača, prvi „tok" |
| 2,5–6,5 | Telefon raste odozdo naviše: okvir, ekran red po red, reljef hero slike (brdo i sunce u bone tonovima), trake teksta. Prvo pada jedna kocka na udarac, zatim rafal. Kamera kruži 30° i staje spreda. Majstor stoji na tekstu i pokazuje gde koja kocka pada. | Geist Mono gore levo: „WÜRFEL 0001", pa sve do stvarnog broja kocki u modelu. Od k120: „ZUERST FÜR DAS HANDY" | „tok-tok-tok" se ubrzava u rafal |
| 6,5 | k185–195: majstor skoči i zakuca kocku. Pikselni oblačak prašine sakrije zamenu 2D kocke 3D dugmetom. Ekran se upali, hero se pomeri u slojevima, trake uklize. Kamera se primakne za 3 %. | — | KLAK i bas drop, ulazi ceo bit |
| 6,5–8 | Sajt je živ, kamera miruje. | „Websites, die man *spürt*." (reč po reč) | udarac na svaku reč |
| 8–9,5 | k270: pikselni kursor pritisne dugme i ono utone za jednu kocku. Majstor stoji na redu sa CTA i pokazuje na dugme. | „30 Min. Erstgespräch." / „*Kostenlos*." / **nemistudio.at** | klik |
| 9,5–10 | Majstor se okrene ka gledaocu i zamahne. Čekić raste dok ne pokrije ceo kadar. Rez na sledeći krug pada ispod čekića. | — | whoosh raste, a udarac stiže na k15 sledećeg kruga |

**Materijal po programu (početnik, ukupno ~6,5 h, plus ~10 min rendera):**
- **MagicaVoxel (~1,5 h):** paleta sa 5 boja brenda i 2 sive. `sablon.vox`: telefon 36×72, sive trake i slika sa X. `nemi.vox`: kopija šablona, prebojena, sa reljefom hero slike dubokim 2–3 kocke i praznim mestom za dugme. `dugme.vox`: narandžasta kocka 6×6×6. `ploca.vox`: ploča 64×64 sa linijama.
- **Blender (~2–2,5 h):** Skriptu piše `programer`, a korisnik je samo pokrene. Skripta čita .vox direktno (format je javan) i pravi oblak tačaka sa atributom „start". Geometry Nodes zatim stavi kocku na svaku tačku. Tako nema hiljade objekata ni ručnih keyframe-ova. Skripta pravi i prskanje šablona, tonjenje ruševine, redosled gradnje, pad dugmeta i njegov pritisak. Ručno se podešavaju tri svetla sa promenom jačine, kamera u 4 položaja (trešenje preko Noise modifikatora) i emisija ekrana. Kopije šablona su linked duplicate. Render: EEVEE, 1080×1920, PNG sekvenca, prvo probni render na 25 %.
- **Pixelorama (~1,5 h):** majstor 24×32 px (ink, bone, narandžasti šlem). Animacije: zamah 3 kadra (isti na početku i na kraju), stajanje sa kockom 2, skok i zakucavanje 3, pokazivanje 2. Uz to čekić za prelaz (32×16), kursor (2 kadra) i oblačak prašine (4 kadra).
- **Remotion (~1,5 h):** koristi postojeće `TekstURitmu`, `Glitch`, `Brojac` i `Zvuk`. Novo su: komponenta za sprajt (PNG kadrovi uvećani ×8 bez zamućenja), tema u bojama brenda, lokalni fontovi Geist i Instrument Serif, sloj sa bezbednim zonama za proveru i EN verzija preko propsa.

**Rizik: 2D majstor promaši 3D dugme.** Lik i dugme nastaju u različitim programima, pa majstor može da skoči pored rupe. Rešenje: kamera miruje od k180 do kraja. Blender skripta upiše tačnu poziciju dugmeta na ekranu u mali JSON, a Remotion postavi skok tačno tamo. Oblačak prašine (3 kadra) sakrije zamenu.

**Zašto baš Nemi:** Od cele ponude, samo se tvrdnja „sajt od nule, bez šablona" može doslovno pokazati slikom. Narandžasta je njihova signalna boja, a sajt koji nastaje je u njihovom stilu (tamno i bone).

**Inspiracija (preuzet princip):** [LEGO FOOH, Madrid, 1. 1. 2026](https://fooh.com/library/4573-lego-blocks-cover-building-facade-fooh-ad/): poznat predmet se pred očima pretvara u kocke, a poruka dolazi tek posle toga. [Wix Harmony, Super Bowl LX teaser, 29. 1. 2026](https://www.ispot.tv/ad/gZj2/wix-harmony-super-bowl-2026-teaser-the-new-way-to-create-song-by-candi-staton): AI pravi „custom template", a mi pokazujemo suprotno. Nijedna marka se u reklami ne imenuje. [Squarespace „Unavailable", 8. 2. 2026](https://www.squarespace.com/press-releases/2026/2/4/squarespace-and-emma-stone-confront-the-stakes-of-domain-ownership-in-super-bowl-lx-campaign): razbijanje alata kao slika koja zaustavlja skrol. Druga branša: [Videobolt, trendovi 2026](https://blog.videobolt.net/post/top-motion-graphics-trends-2026) (blog prodavca šablona, dakle mišljenje, ne podatak): taktilno i hibrid 2D/3D, pa kod nas pikselni lik stoji na slovima, a svet je od voksela. Tehnika: reel iz brief-a (15. 10. 2026) i `motion/` Probni, [pojavljivanje instanci u Geometry Nodes](https://www.blendernation.com/2021/07/16/geometry-nodes-tutorial-grid-instance-appear-animation/) i naš DON'S (`scripts/gradnja`, ceo scenario u jednom fajlu).
