# AI alati za slike i video, i Blender za web sekvence

Poslednja provera: 2026-10-23
Vodi: `trend-skaut`. Prvo punjenje. Deo A: AI alati (kratko). Deo B: Blender za web sekvence (za kafa skrol projekat, detaljno).

## Kako čitati

- Zvanična dokumentacija ima prvenstvo (CLAUDE.md). Tvrdnje iz reklame, press-releasa ili agregatora označene su **NEPROVERENO** ili je izvor naveden kao "agregator".
- **"Najbolji za fotorealističnu hranu, enterijer, proizvode" ne može da se potvrdi iz zvanične dokumentacije.** Nijedan proizvođač ne objavljuje takav rang. Jedini pošten dokaz je probni kadar na našem proizvodu (predlog testa na kraju dela A).
- Cene su cene proizvođača gde je navedeno, a cene preko Runway API liste su cene preprodavca (nisu cene proizvođača).
- Za kafa projekat AI je **sporedan**: pakovanja, etikete i logo moraju biti tačni, a AI generatori pogrešno pišu sitan tekst (naša analiza referentnog snimka, `studio/kafa-skrol/analiza-videa.md`: sav sitan tekst u tom snimku je izmišljena slovna masa). Pakovanja i proizvodi idu iz Blendera (deo B).

# DEO A: AI alati

## A1. Pregled

| Alat | Trajanje | Rezolucija | Početni i završni kadar | Cena | Status provere |
|---|---|---|---|---|---|
| **Gemini Omni Flash 1.1** (Google, Gemini API) | produženje 3–10 s, ukupno do 40 s; početna dužina nije navedena | 360p, 720p (podrazumevano), 1080p i 4K (obe upscale) | **da**, dva prikaza u ulazu | efektivno oko $0,10/s za 720p (Standard) | zvanična dokumentacija |
| **Veo 3.1** (Google, Gemini Enterprise Agent Platform, ranije Vertex) | 4, 6 ili 8 s | 720p, 1080p, 4K samo kod standardnog modela; 24 fps | **da** | nije na stranici modela | zvanična dokumentacija |
| **Nano Banana 2.1 / Pro** (Google, slike) | n/a | 1K, 2K, 4K | n/a | $0,0336 / $0,0504 / $0,113 po slici (2.1); Pro $0,134 (1K, 2K), $0,24 (4K) | zvanična dokumentacija i cenovnik |
| **GPT Image 2.5** (OpenAI, slike) | n/a | do 3840 px po ivici, ukupno 655.360 do 8.294.400 px | n/a | nije proverena | zvanična dokumentacija |
| **Kling 3.0** (Kuaishou) | 3–15 s | 720p (Standard), 1080p (Pro), 4K | početni i završni kadar (naš tok već koristi) | od $0,09 do $0,43 po sekundi preko Runway API-ja | agregator (zvanična dokumentacija se ne čita bez skripte) |
| **Kling 4.0** | tvrdi se 3–30 s | tvrdi se 720p, 1080p, 4K, 21:9 | tvrdi se do 10 ključnih kadrova | nije objavljena | **NEPROVERENO** (vidi A2) |
| **MiniMax Hailuo 2.3** | 6 ili 10 s (768P), 6 s (1080P) | 768P, 1080P | samo početni kadar u dokumentovanoj šemi | nije proverena | zvanična dokumentacija |
| **Luma Ray 3.2** | 5 ili 10 s | 360p do 1080p, HDR | **da** (10 s ne ide sa kadrovima) | nije proverena | zvanična dokumentacija |
| **Runway** (Gen-4.5, Aleph 2.0, agregator) | nije potvrđeno iz zvanične dokumentacije | nije potvrđeno | nije potvrđeno | Gen-4.5 $0,12/s, Gen-4 Turbo $0,05/s, Aleph 2.0 $0,28/s | cene zvanične, ostalo NEPROVERENO |

## A2. Alati

### Google: Gemini Omni Flash 1.1 i Veo 3.1 (video)
- **Trajanje i rezolucija.** Omni Flash (`gemini-omni-1.1-flash`): rezolucija 360p, 720p (podrazumevano), 1080p i 4K (obe upscale, `response_format.resolution`), odnos 16:9 ili 9:16. Produženje dodaje 3–10 s, ukupno do 40 s. Veo 3.1 (`veo-3.1-generate-001`, `veo-3.1-fast-generate-001`, GA od 2025-11-17; `veo-3.1-lite-generate-001`, Preview od 2026-04-02): 4, 6 ili 8 s, 24 fps, 720p/1080p ulaz, 4K izlaz samo kod standardnog modela. (2026-10, ai.google.dev + docs.cloud.google.com)
- **Početni i završni kadar.** Omni: dva prikaza u listi `input`, prompt opisuje prelaz. Veo: `image` + `lastFrame`, podržano u sva tri modela. (2026-10, ai.google.dev + docs.cloud.google.com)
- **Cena.** Omni Flash: Gemini cenovnik navodi efektivno oko $0,10 po sekundi za 720p (Standard). Veo: cena nije na stranici modela. Runway API navodi Veo 3.1 od $0,20/s i Fast od $0,10/s (cena preprodavca). (2026-10, ai.google.dev pricing + docs.dev.runwayml.com)
- **Komercijalno.** Uslovi Gemini API-ja: Google ne polaže pravo na vlasništvo nad sadržajem, ali može da generiše isto ili slično za druge, a odgovornost za upotrebu je na vama. Svi generisani snimci nose nevidljiv SynthID žig. (2026-10, ai.google.dev/gemini-api/terms + docs)
- **Saveti za promptove (zvanični).** Formula za Veo 3.1: `[Kinematografija] + [Subjekat] + [Radnja] + [Kontekst] + [Stil i ambijent]`. Za prelaz kadar-kadar: napraviti dve komplementarne slike (npr. isti prizor iz dva ugla) i u promptu opisati prelaz. Opisati šta treba da bude prisutno umesto negacije ("pusti predeo" umesto "bez zgrada"). Zvuk: govor u navodnicima, `SFX:`, `Ambient noise:`. Za Omni: negativni prompt nije parametar, piše se u tekstu. (2025-10, cloud.google.com blog "Ultimate prompting guide for Veo 3.1" + ai.google.dev)
- **Loše / ograničenja (iz dokumentacije).** Referisanje više videa nije podržano. Engleski je potpuno podržan, ostali jezici "mogu da rade". Veo može da blokira snimak zbog problema sa zvukom. U EU/UK/CH `personGeneration` dozvoljava samo odrasle. Omni: uređivanje i produženje otpremljenih snimaka nije dostupno u EEA, Švajcarskoj i UK; ne može da doda dijalog u već snimljen video; nema uređivanja glasa. Vodič za Veo nema savete za hranu i proizvode. Veo 3.1 u Vertex-u: region samo `us-central1`. (2026-10, ai.google.dev + docs.cloud.google.com)
- **Vreme.** Gemini API Veo 3.1 Preview modeli ugašeni su 2026-10-22. GA Veo 3.1 na Vertex-u: povlačenje "2026-11-17 ili kasnije". Preporuka: ne graditi na Veo 3.1, nego na Omni Flash. (2026-10, ai.google.dev + docs.cloud.google.com)

### Google: Nano Banana 2.1 i Pro (slike)
- **Modeli i cena (Standard, po slici).** `gemini-nano-banana-2.1`: 1K $0,0336, 2K $0,0504, 4K $0,113. `gemini-3-pro-image`: 1K i 2K $0,134, 4K $0,24. `gemini-3.1-flash-image`: 0,5K $0,045, 1K $0,067, 2K $0,101, 4K $0,151. Batch je upola jeftiniji. (2026-10, ai.google.dev pricing)
- **Referentne slike:** do 14 u jednom zahtevu, ukupno (npr. Nano Banana 2.1: do 10 slika predmeta i 5 likova). Dokumentacija preporučuje višekratno uređivanje (nastavak razgovora) za doterivanje. (2026-10, ai.google.dev)
- **Loše / napomene:** razmišljanje (thinking) ne može da se isključi i model može da vrati do dve probne slike; veličina se piše velikim K ("2K"), malim se odbija; svaka slika nosi SynthID. Dokumentacija ne daje šablon za fotorealizam proizvoda. `gemini-2.5-flash-image` ugašen 2026-10-02. (2026-10, ai.google.dev)

### OpenAI: GPT Image 2.5 (slike)
- Modeli `gpt-image-2.5-sunburst` (preciznost uređivanja) i `gpt-image-2.5-flare` (brzo, svakodnevno). Veličine: preporučeno 1024×1024, 1536×1024, 1024×1536; proizvoljno uz stranice deljive sa 16, odnos 1:3 do 3:1, ivica do 3840 px, ukupno 655.360 do 8.294.400 px; iznad 2560×1440 je eksperimentalno. Kvalitet low do max. Providna pozadina: `background: "transparent"` uz PNG ili WebP. Potrebna je verifikacija organizacije. (2026-10, developers.openai.com)
- **Loše (zvanično):** tačan raspored i čitljivost teksta, doslednost brenda i likova kroz više slika, složeni rasporedi; složeni zahtevi do 2 minuta. Cena: **nije proverena** (nije se otvorila stranica sa cenama). (2026-10, developers.openai.com)

### Kling (3.0 u upotrebi, 4.0 pristiže)
- **Šta znamo da radi kod nas:** naši promptovi koriste Kling multi-shot sa početnom i završnom slikom (`video/prompt_gradnja_multishot.md`, `video/prompt_sorten.md`) i Kling O3 Video Edit (`video/prompt_radnja1.md`). (2026-10, repo)
- **Kling 3.0:** 3–15 s; Standard 720p, Pro 1080p, 4K; cene preko Runway API-ja od $0,09/s (Standard), od $0,12/s (Pro), $0,43/s (4K). Zvanična Kling dokumentacija i cenovnik ne mogu da se pročitaju bez skripte (stranice su SPA), pa su ovo podaci agregatora. (2026-10, docs.dev.runwayml.com)
- **Kling 4.0:** objava 2026-09-28. Kuaishou (preko saopštenja Bernama, 2026-10-19) tvrdi zvanično lansiranje 2026-10-15, do 30 s u jednom prolazu i do 10 ključnih kadrova. Agregator Creaa (2026-10-16), pozivajući se na Kling stranice, navodi 720p/1080p/4K, 21:9, stereo zvuk i **"Kling 4.0 API Coming Soon"**; HDR 10-bit označen kao "uskoro"; Flash varijanta nema početni/završni kadar i dostupna je ograničenoj grupi. Sve ovo je **NEPROVERENO** dok se ne potvrdi u Kling dokumentaciji ili u našem probnom klipu. Cena i komercijalni uslovi nisu objavljeni. (2026-10, Bernama + creaa.ai)
- **Komercijalno:** agregatori (Segmind, Atlas Cloud, PhotonPay) navode da besplatan nalog ima žig i nije za komercijalnu upotrebu, a plaćeni nalog skida žig. **NEPROVERENO** u Kling uslovima. Pre isporuke klijentu proveriti uslove naloga. (2026-10, agregatori)

### MiniMax Hailuo 2.3
- **Zvanična dokumentacija (platform.minimax.io):** modeli `MiniMax-Hailuo-2.3`, `-2.3-Fast`, `-02`. Trajanje 6 ili 10 s na 768P, samo 6 s na 1080P. `first_frame_image` je obavezan (JPG/PNG/WebP do 20 MB, kraća ivica preko 300 px, odnos 2:5 do 5:2). **Završni kadar nije u dokumentovanoj šemi** za ovu stranicu. (2026-10, platform.minimax.io)
- **Saveti za promptove (zvanični):** komande kamere u uglastim zagradama, 15 komandi (`[Push in]`, `[Pan left]`, `[Pedestal up]`, `[Static shot]` i druge), do 3 spojene u jednu zagradu (`[Pan left,Pedestal up]`), redosled komandi u tekstu daje redosled pokreta. Prompt najviše 2000 znakova. `prompt_optimizer` je podrazumevano uključen, isključiti za preciznu kontrolu. (2026-10, platform.minimax.io)
- **MiniMax H3** (Runway API lista: `h3_max`, 480p/768p, **prvi i poslednji kadar**, od $0,05/s): zvanična MiniMax dokumentacija za H3 nije pročitana, pa je ovo **NEPROVERENO**. Naš tok radi sa klipovima 1344×768 (NAPREDAK.md). (2026-10, docs.dev.runwayml.com)

### Luma Ray 3.2
- **Zvanično (docs.agents.lumalabs.ai):** trajanje 5 s (podrazumevano) ili 10 s; 10 s **ne** ide uz HDR, `start_frame` ni `end_frame`. Rezolucije 360p (nacrt), 540p, 720p (podrazumevano), 1080p. `start_frame` i `end_frame` su opcioni (oba, jedan ili nijedan). Više ključnih kadrova (`keyframes`) uklanja ograničenja pozicije i 10 s, ali se ne kombinuje sa `start_frame`/`end_frame`/`loop`. `loop` (neprekidna petlja) ne ide sa 10 s, HDR ni `end_frame`. HDR daje HDR MP4 (i EXR), samo 720p/1080p. Prompt 1–6000 znakova. Odnosi 9:16, 3:4, 1:1, 4:3, 16:9, 21:9. Slike do 50 MB i 8000 px. Izlazni linkovi važe 1 sat. (2026-10, docs.agents.lumalabs.ai)
- **Saveti (zvanični):** navesti subjekat, pokret, kretanje kamere, svetlo i tempo; što više kadrova se zakači, to je ishod bliži nameri. (2026-10, docs.agents.lumalabs.ai)
- **Loše / ograničenja:** produženje (`extend`) samo iz SDR generacije; interpolacija iz prethodne generacije plus drugog kadra još nije dostupna. Cena nije proverena. (2026-10, docs.agents.lumalabs.ai)

### Runway
- **Zvanično o pravima (help.runwayml.com, "Usage rights"):** sadržaj koji napravite je vaš, bez Runway ograničenja za nekomercijalnu upotrebu, na bilo kom paketu uključujući besplatan. Kreditiranje Runway-a nije obavezno. Besplatan paket stavlja žig, žig se skida od paketa Standard naviše. (2026-10, help.runwayml.com)
- **Cena (Runway API, po sekundi):** Gen-4.5 $0,12, Gen-4 Turbo $0,05, Aleph 2.0 (video-u-video, uređivanje) $0,28. Trajanje, rezolucija i završni kadar za Gen-4.5 **nisu potvrđeni iz zvanične dokumentacije** (agregatori navode 5, 8 ili 10 s i 720p), pa je to **NEPROVERENO**. (2026-10, docs.dev.runwayml.com)
- Runway API takođe prodaje druge modele po sekundi (Seedance 2.5 od $0,20, WAN 3.0 od $0,05, Kling 3.0, Veo 3.1, MiniMax H3, Gemini Omni Flash). To su cene preprodavca. (2026-10, docs.dev.runwayml.com)

### Seedance 2.5 i WAN 3.0
- Runway API lista: Seedance 2.5 do 30 s, 480p/720p/1080p, od $0,20/s, "draft" 480p koji se u roku od 7 dana može poboljšati na 1080p; WAN 3.0 2–30 s, 480p/720p/1080p, od $0,05/s. Početni i završni kadar za oba: **NEPROVERENO**. Zvanična ByteDance/BytePlus dokumentacija nije pročitana. Sekundarni izvori navode da je Seedance 2.5 objavljen 2026-07-31. (2026-10, docs.dev.runwayml.com + sekundarni izvori)

### Midjourney i FLUX
- **NEPROVERENO.** Midjourney dokumentacija vraća 403 (nije pročitana). BFL dokumentacija je u ovom prolazu dala samo naslovnu stranu ("FLUX.2 ostaje potpuno podržan"), bez podataka o rezoluciji, ceni ni licenci. Ne preporučuje se oslanjanje dok se ne pročita zvanična dokumentacija. (2026-10, docs.bfl.ai)

### Predlog probe za fotorealizam proizvoda (jer rang ne postoji)
Isti ulaz (naša referentna slika šolje ili pakovanja iz Blendera) u 2–3 alata, isti prompt, 3 pokušaja. Ocena po listi: oblik i proporcije predmeta ostaju?, etiketa čitljiva?, odsjaj i senka smisleni?, pokret kamere kakav je traženo? Ono što pogrešno napiše tekst na etiketi isključuje alat za pakovanja.

## A3. Pravo i označavanje (za `trziste`, nije pravni savet)
EU AI Act, član 50 (obaveze transparentnosti, označavanje sintetičkog sadržaja) primenjuje se od 2026-08-02. Za generativne sisteme već na tržištu pre tog datuma, obaveza označavanja iz čl. 50(2) odložena je do 2026-12-02. Sekundarni izvori (pravne kancelarije), **proveriti u EUR-Lex-u**. Naši Blender renderi nisu AI sadržaj, pa za njih ovo ne važi. Za AI snimke i slike pitanje je da li se označavaju kao sintetički, to treba da odluči `trziste`. (2026-08, Ropes & Gray, FEDIL)

---

# DEO B: Blender za web sekvence

Izvori: Blender Manual (izvor `.rst` fajlovi, grana `main` = 5.2 LTS), Release notes, blender.org, OpenImageDenoise, MDN, caniuse, Google WebP dokumentacija. Brojevi označeni "izmereno" su moja merenja na ovoj mašini (4 jezgra, 16 GB RAM-a) 2026-10-23 sa sintetičkom scenom, vidi B4.

## B1. Verzija i hardver
- **Aktuelna stabilna: Blender 5.2.3 LTS, objavljen 2026-10-22** (blender.org/download). 5.2 LTS je izašao 2026-07-14, podrška do jula 2028. Prethodni LTS 4.5 podržan do jula 2027. 5.3 je u beta, 5.4 u alfa fazi. Instalirana verzija u `/opt/blender` je 5.2.3 LTS (izmereno: `--version`). Preporuka: fiksirati 5.2 LTS za ceo projekat. (2026-10, blender.org + developer.blender.org)
- **Zahtevi** (blender.org): minimum 4 jezgra sa SSE4.2 (preporuka 8 jezgara), 8 GB RAM-a (preporuka 32 GB), za GPU 2 GB VRAM-a sa OpenGL 4.3 ili Vulkan 1.3. (2026-10, blender.org/download/requirements)
- **Upozorenje o zastarelosti (izmereno, 5.2.3):** `Material.use_nodes` i `World.use_nodes` su "expected to be removed in Blender 6.0". Radi u 5.2, ali ne pisati nove skripte oslanjajući se na to bez napomene (`scripts/blender/common.py` koristi `w.use_nodes = True`). (2026-10, izmereno)

## B2. Cycles ili EEVEE bez GPU-a (headless)
- **Zvanično: EEVEE renderuje samo na GPU-u i nema plan za CPU (softverski) render.** "Headless" nije podržan na Windows serverima bez ekrana. CPU je i dalje potreban za pripremu geometrije. (2026-10, Blender Manual, EEVEE "Limitations", odeljak Hardware and GPU Requirements)
- Zaključak: na mašini bez GPU-a (naše okruženje: 4 CPU jezgra) koristi se **Cycles na CPU-u**. Zajednica (devtalk.blender.org) navodi da EEVEE preko Xvfb-a radi, ali vrlo sporo (kadar od 2 s trajao je 50 s, i to na instanci sa GPU-om); da li bi Mesa llvmpipe radio, tema ne potvrđuje, a Manual to ne podržava. Ne planirati. (2026-10, Manual + devtalk.blender.org)
- Šta se gubi: Cycles je fizički tačniji ("Cycles će uvek dati fizički tačnije rendere", Manual), lomi svetlo kroz staklo i tečnost bez trikova. Cena: sporije (B4).
- **Izmereno (2026-10-23, Blender 5.2.3, ova mašina bez GPU-a):** pokušaj renderovanja sa `scene.render.engine = 'BLENDER_EEVEE'` u pozadinskom režimu (`-b`) staje na grešci `Couldn't open libEGL.so.1: cannot open shared object file` i ne daje sliku. U 5.2.3 je jedini ugrađeni identifikator EEVEE motora `BLENDER_EEVEE` (stariji nazivi tipa `BLENDER_EEVEE_NEXT` iz verzija 4.2 do 4.5 ne važe, to poslednje je iz mog znanja i nije proveravano). Znači: ovde je Cycles jedini put. (2026-10, izmereno)

## B3. Komanda za render bez ekrana (Manual, Command Line)
Pokretanje se radi isključivo preko sigurnog obrasca iz `.claude/agents/blender-umetnik.md` (`unshare -n … --factory-startup --offline-mode -Y …`). Argumenti koji su bitni za render (Manual, "Command Line Arguments" i "Rendering"):
- `-b` bez korisničkog sučelja. `-E CYCLES` motor. `-o /putanja/kadar_####` izlaz (broj `#` je broj cifara). `-F PNG` format. `-s 1 -e 120` raspon kadrova. **`-a` ili `-f 10` uvek na kraj** ("Arguments are executed in the order they are given"). `-t 0` svi procesori, `-t 4` četiri niti. `-j 2` preskače svaki drugi kadar (nacrt). `--cycles-device CPU` bira uređaj. `--` kraj opcija, ostatak ide skripti (`sys.argv`). `--python-expr` izvršava izraz. (2026-10, Blender Manual)

## B4. Podešavanja za brz CPU render (polazne vrednosti)

**Brojevi su polazne tačke, ne gotovi recepti.** Manual za većinu ne daje podrazumevane vrednosti. Konačnu vrednost određuje probni kadar (pravilo iz `blender-umetnik.md`: 3 probna kadra pre cele sekvence). Kolona "Izvor" kaže da li je tvrdnja iz Manual-a ili je moje iskustvo.

| Podešavanje | Polazno | Izvor |
|---|---|---|
| Motor / uređaj | Cycles, CPU | Manual (EEVEE samo GPU) |
| Max samples (render) | 64 za neprozirne predmete (ili maks. 128 uz prag 0,02), više samo za staklo i tečnost posle probnog kadra | merenje B4a (32 do 64 + OIDN je dovoljno za scenu bez stakla) |
| Noise Threshold | 0,02 | Manual: "tipične vrednosti od 0,1 do 0,001"; merenje B4a (adaptivno je radilo posle 64 uzorka) |
| Min samples | 0 (automatski). Ako tanak mlaz kafe treperi, 16–32 | Manual (0 = automatski) |
| Denoise | OpenImageDenoise, Passes **Albedo + Normal**; za probe Balanced + prefilter Fast (oko +10 CPU-s po kadru), za finalne kadrove High + Accurate (oko +25 CPU-s, 47,7 dB naspram 46,8 dB) | Manual: OIDN "obično daje najviši kvalitet", Albedo "najmanje preporučeno"; merenje B4a |
| Denoise na GPU-u | isključeno (nema GPU-a) | Manual |
| Animated seed | probati oba, odlučiti na probnom nizu | Manual preporučuje uključeno za animaciju; **OIDN ne garantuje stabilnost kroz vreme** (OIDN README: RT filter "nije vremenski stabilan") |
| Bounces | total 6, diffuse 2, glossy 3, transmission 4 (6–8 samo za staklo i tečnost), volume 0 (1–2 za paru) | Manual: više odbijanja = više šuma, staklo traži najviše |
| Clamp | Indirect 1–3, Direct 0 | Manual: "često je korisno stegnuti samo indirektno" |
| Filter Glossy | 0,5–1 | Manual (zamućuje oštre odsjaje, na račun tačnosti) |
| Caustics | isključeni (reflective i refractive) | Manual |
| Light Tree | uključeno | Manual (smanjuje šum kod više svetala) |
| Fast GI Approximation | isključeno za junaka sekvence | Manual ("brza alternativa, smanjen kvalitet") |
| Boje materijala | najviše 0,8 | Manual ("držite maksimalnu vrednost 0,8 ili manje, pojačajte svetla") |
| Film → Transparent | uključeno (pozadina dolazi sa sajta) | Manual |
| Film → Transparent Glass | uključeno samo za staklo; **proveriti kafu u staklu**: može da postane providna preko pozadine | Manual + moje upozorenje |
| Senka na providnoj pozadini | ravan sa **Shadow Catcher** (`Object → Visibility`) + Shadow Catcher prolaz | Manual |
| Pixel filter | Blackman-Harris (podrazumevano) | Manual |
| View transform | **Khronos PBR Neutral** za pakovanja (cilj mu je da boje sa etikete ostanu verne), AgX za dramatičnu sliku | Manual (PBR Neutral "namenjen fotografiji proizvoda"); Filmic je zastareo (zamenjen AgX-om) |
| Persistent Data | uključeno za animaciju | Manual |
| Niti | automatski (ili fiksno da ostane CPU za rad) | Manual |
| Izlaz | PNG RGBA 8-bit kao međufajl, pa kodiranje u WebP | vidi B7 |

- Blender sam može da snimi **WebP** (8-bit, alfa) i **AVIF** (8, 10, 12-bit, alfa), ali bez podešavanja osim kvaliteta. Za nadzor nad kvalitetom bolji je PNG pa `cwebp`/ffmpeg (naš `scripts/freiraum/frames.py` koristi ffmpeg `libwebp`). (2026-10, Blender Manual, Image Formats)
- **Procena vremena (formula):** ukupno = broj kadrova × sekunde po kadru. Trošak po kadru raste linearno sa brojem piksela, a sa brojem uzoraka do tačke gde adaptivno uzorkovanje počne da prekida piksele (B4a). Prvo izmeriti 3 kadra (početak, sredina, najteži), pa množiti, i računati u CPU-sekundama (B4a).

### B4a. Izmereno na ovoj mašini (2026-10-23, Blender 5.2.3, 4 CPU niti, bez GPU-a)
Scena je moja sintetička "kafa" (šolja sa premazom, 400 zrna sa premazom, kesa, dva area svetla, providna pozadina, Shadow Catcher ravan), nije naša stvarna scena i nema stakla ni tečnosti. Brojevi su **red veličine**, ne obećanje. Skripte su u privremenom folderu, ne u repou.

**Mašinu dele drugi procesi.** U isto vreme su radili drugi Blender procesi (druga odeljenja), pa je zidno vreme za isto podešavanje variralo do 3× (iskorišćenost CPU-a 31 do 93 %). **CPU-sekunde su stabilne (±5 %)**, zato planirati u CPU-sekundama i deliti brojem slobodnih jezgara (4 kad nema drugih Blender procesa). Render sekvence je serijski posao, ne puštati ga uporedo sa tuđim renderima.

| 720×1280, Albedo + Normal | CPU-sekundi po kadru | PSNR prema referenci (512 uzoraka + OIDN) |
|---|---|---|
| 16 uzoraka + OIDN (Balanced, prefilter Fast) | 59 | 43,6 dB |
| 32 uzorka + OIDN (Balanced / Fast) | 110 | 45,4 dB |
| 64 uzorka + OIDN (Balanced / Fast) | 217–219 | 46,8 dB |
| 64 uzorka + OIDN (High / Accurate) | 233–235 | 47,7 dB |
| 64 uzorka + OIDN (Fast / bez prefiltra) | 219–226 | 46,0 dB |
| 64 uzorka, bez denoisera | 209 | 41,0 dB |
| 128 maks. uzoraka + OIDN (Balanced / Fast) | 281 | 48,1 dB |
| 128 maks. uzoraka, bez denoisera | nije mereno (zidno 83 s) | 43,0 dB |
| 512 uzoraka + OIDN, bez adaptivnog (referenca) | nije mereno (zidno 467 s) | |

- Svi redovi: Noise Threshold 0,02. Razlika od reference ispod 1,7/255 po pikselu već pri 16 uzoraka; **32 do 64 uzorka sa denoiserom je dovoljno za ovakvu scenu**. Denoiser vredi više od udvostručavanja uzoraka: 64 uzorka bez njega je gore (2,27/255) od 16 sa njim (1,68/255).
- **Adaptivno uzorkovanje (0,02) je radilo posao tek posle 64 uzorka:** do 64 trošak je skoro linearan (oko 3,4 CPU-s po uzorku), a 128 maks. uzoraka je koštalo samo 28 % više od 64. Izbor je "maks. 128, prag 0,02" ili fiksnih 64.
- **Denoise nije usko grlo na 64 uzorka:** dodaje oko 10 CPU-s (Balanced / Fast) do oko 25 CPU-s (High / Accurate) po kadru. Same za sebe (1 uzorak, zidno): bez denoisera 2,2–2,6 s, High + Accurate (Albedo + Normal) 14,9 s, High + Accurate (samo Albedo) 8,1 s, Balanced + Fast 5,8 s, Fast + bez prefiltra 4,6 s.
- **Po pikselima linearno:** 1080×1920 (2,07 MP) na 64 uzorka je 486 CPU-s (oko 235 CPU-s po megapikselu). Zato je isečak oko proizvoda (B7) najjeftinija ušteda.
- **Procena za naš projekat** (račun iz 235 CPU-s po MP na 64 uzorka, prava scena može biti jeftinija ili skuplja; zidno vreme na 4 slobodna jezgra):

| Kadar | Megapiksela | Po kadru | 100 kadrova | Tri poglavlja |
|---|---|---|---|---|
| 900×1200 (isečak oko proizvoda) | 1,08 | oko 65 s | oko 1,8 h | oko 5,4 h |
| 1600×1600 | 2,56 | oko 150 s | oko 4,2 h | oko 12,5 h |

  Telefon set se pravi **smanjivanjem istog rendera**, ne novim renderom. Ako rade i tuđi Blender procesi, računati 2 do 3× duže.
- **Nije mereno:** treperenje između susednih kadrova (OIDN to ne garantuje, vidi tabelu iznad), staklo i tečnost (traže više uzoraka i odbijanja), Mantaflow bake.
- Senka na providnoj pozadini (Shadow Catcher): u mom probnom kadru velika ravan daje crnu RGB senku sa alfa 0,08 do 0,46, čak i daleko od predmeta (33 % piksela je poluprovidno). Zato **mali disk ispod predmeta** ili ublažiti ivice radijalno, ne veliku ravan preko celog kadra. (2026-10, izmereno)

## B5. Fizika zrna (Rigid Body)
- **Šta Manual kaže:** Rigid body simulira kretanje čvrstih tela (menja položaj i orijentaciju, ne oblik). Aktivna tela se simuliraju, pasivna miruju. Samo mesh objekti. Za stabilnost: **izbegavati male objekte ("trenutno su nestabilni"), po mogućstvu najmanje 20 cm u prečniku**; izbegavati mesh oblike sudara za mala i brza tela (trouglovi nemaju debljinu); povećati broj koraka u sekundi i broj iteracija rešavača; margina sudara može da se poveća da mesh dobije "debljinu"; kad skaliranje nije potrebno, primeniti ga (`Ctrl-A`). **"Bake To Keyframes"** pretvara dinamiku u obične ključne kadrove. (2026-10, Blender Manual, Rigid Body, Tips)
- **Zrno kafe je oko 1 cm, a Manual traži 20 cm. To je glavni rizik.** Preporuka (iskustvo, **nije u Manual-u**, ali provereno u mom testu ispod): simulirati u uvećanoj sceni (10× uvećano, gravitacija pomnožena istim brojem, `scene.gravity = (0, 0, -98.1)`) sa **proksi-zrnima** (200–400 niskopoligonskih zrna, oblik Convex Hull), pa pečenjem (`Bake To Keyframes`) i zamenom proksija detaljnim zrnom (instance). Mlin, levak i dripper su pasivna tela (oblik Box ili Convex Hull, ne Mesh). Zrna puštati u talasima (uključivanje dinamike po ključnom kadru).
- **Pogodak koji često poremeti test:** `Object → Apply → Scale` mora bez lokacije (`transform_apply(location=False, rotation=False, scale=True)`), inače se ishodište objekta vraća u koordinatni početak, geometrija ostaje pomerena i Bullet za Box i Sphere oblike kolizije koristi pogrešno mesto (u mom prvom pokušaju su sva 250 zrna propala kroz pod). (2026-10, izmereno)
- **Izmereno (2026-10-23, 250 zrna veličine 1,1 × 0,76 × 0,54 cm, levak od 4 kosa zida, 120 kadrova, 2 CPU niti pod opterećenjem):**

| Postavka | Vreme simulacije | Propalo kroz pod | Preliveno van levka |
|---|---|---|---|
| prava razmera, 10 podkoraka, 10 iteracija | 62 s | 10 | 69 |
| 10× uvećano, 10 podkoraka, 10 iteracija | 23–24 s | 7 | 42–48 |
| 20× uvećano, 10 podkoraka, 10 iteracija | 18 s | 12 | 51 |
| **10× uvećano, 30 podkoraka, 20 iteracija** | **128 s** | **0** | **1** |
| 10× uvećano, 30 podkoraka, 20 iteracija, pod debljine 5 cm, razmak spawna 1,2 cm | 93 s | 0 | 8 |

  Zaključak: **uvećanje razmere ubrza simulaciju 2,5 do 3,4×, ali stabilnost daje tek veći broj koraka u sekundi i iteracija rešavača** (kako i Manual kaže). Svejedno je simulacija zanemarljiva prema renderu (minuti naspram sati). Posle baka obavezno proveriti i ukloniti zrna koja su pobegla. Test je na jednoj sceni i nije opšti recept.
- **Veliki broj zrna (hiljade):** Geometry Nodes **Simulation zone** (Manual: rezultat jednog kadra utiče na sledeći; keš automatski tokom reprodukcije; "bake to disk" za render farmu, kadrovi mogu da se renderuju bez redosleda; navedeni primer: simulacije zasnovane na sferama uz čvor Index of Nearest). Zrno kao sfera je gruba aproksimacija, ali za gomilu je dovoljno. (2026-10, Blender Manual, Simulation Zone)
- **Mlevenje:** ne simulirati. Zrna nestaju u mlinu, a mleveno kafa raste kao gomila (promena oblika / pomeranje temena + instance sitnih delova). (Preporuka, iskustvo.)

## B6. Tečnost, para i prelaz "talas"
- **Mantaflow (ugrađeno, Fluid):** radi se Domain (granice simulacije) + Flow (izvor) + Effector (prepreke), dodeli se materijal domenu, sačuva se fajl i **peče se keš**. Manual: "veliki domeni traže veće rezolucije i duže pečenje", "držati usku zonu tanku, čestice unutar tečnosti troše računar", OpenVDB keš smanjuje veličinu keša, "Bake All" može da se pauzira i nastavi. Parametri: Resolution Divisions, Time Scale, CFL, Timesteps Min/Max. Gas (para, dim) je deo istog sistema. (2026-10, Blender Manual, Fluid)
- **Kada Mantaflow:** samo ako jeftin trik ne izgleda dobro, i samo u malom domenu (oblast šolje), ne cela scena. Tanak mlaz iz kuvala traži visoku rezoluciju (iskustvo), pa je pečenje dugo na 4 CPU jezgra. (Pravilo iz `blender-umetnik.md` isto.)
- **Jeftin trik za mlaz (iskustvo; čvor Trim Curve potvrđen u Manual-u):** kriva od vrha kuvala do šolje + **Trim Curve** (Manual: skraćuje splajn od početka i kraja, Start/End kao faktor ili dužina) sa animiranim "End" od 0 do 1 + **Curve to Mesh** sa kružnim profilom (poluprečnik se sužava, šum daje talasanje) + materijal (tamna kafa, malo prozračnosti). Nivo u šolji: ravan koja se diže uz ključne kadrove + animirani talasi (šum) i prsten talasa kod udara. Mehurići "bloom-a": instance sfera (rasporedi tačke po površini) sa animiranom veličinom. Petlja kapljica: Simulation zone (gore).
- **Para (iskustvo):** volumenski šum animiran kroz četvrtu dimenziju šuma, ili Mantaflow gas ako je kadar blizu. Ili providne ravni sa šumom (pravilo iz `blender-umetnik.md`).
- **Prelaz "talas kafe preplavi ekran":** ne simulirati u 3D-u preko celog ekrana. Opcije (mišljenje, vidi `trendovi.md`): (1) CSS/SVG maska sa `clip-path` i SVG filterom za "tečan rub", (2) kratka providna sekvenca renderovana u Blenderu u pola rezolucije (30–40 kadrova) i razvučena preko ekrana, (3) WebGL shader. Opcija 1 je najjeftinija za telefon.

## B7. Pakovanje za web
**Referentne tačke koje imamo (izmereno):**
- **Naš `freiraum`:** 80 kadrova po sekvenci, desktop set 720×1280, **prosečno 52–58 KB po kadru** (ukupno 4,2–4,7 MB), telefon set 540×960, **36–40 KB** (ukupno 2,9–3,2 MB), lossy WebP (VP8), prag telefona 860 px, `seq.json` sa `count, fps, w, h`. Skripte: `scripts/freiraum/frames.py` (ffmpeg `libwebp`, desktop kvalitet 55, telefon 52) i `day_seq.py` (WebP sa providnom pozadinom, kvalitet 70 i 66). (2026-10, repo, izmereno)
- **Vibe (HM 2026-09):** 150 kadrova, **34–52 KB po kadru** kao WebP, ukupno oko 6–7 MB, isečeni na proizvod, canvas 600×1500 CSS px, DPR najviše 2. (2026-10, merenje, vidi `reference.md`)
- **CoffeeTech (SOTD 2026-07):** AVIF kadrovi iz rendera, **6–71 KB**. (2026-10, merenje)

**Format.**
- **WebP je podrazumevani za sekvencu.** Podrška 97,08 % (caniuse, 2026-09); lossy WebP može i sa alfa kanalom, "tipično oko 3 puta manji od PNG-a" (Google); u proseku 25–35 % manji od JPEG-a; najveća dimenzija 16.383 px; lossy WebP čuva boju u 8-bit YUV 4:2:0 (MDN), pa sitan tekst na etiketi i obojene ivice mogu da omekšaju. (2026-09, caniuse + MDN + developers.google.com/speed/webp)
- **AVIF za mirne slike** (poster, hero fotografija): podrška 96,33 %, MDN kaže medijana 50 % manji od JPEG-a, ali **nema progresivno prikazivanje**. iOS Safari 16.0 podržava samo mirne slike (bez noise synthesis), Safari 16.4 pun. **Brzina dekodiranja AVIF-a na telefonu: izvori se ne slažu, NEPROVERENO**, izmeriti na ciljnom telefonu pre nego što se sekvenca prebaci na AVIF. (2026-09, caniuse + MDN)
- **Izmereno (2026-10-23, jedan RGBA kadar 720×1280 iz moje probne scene, PNG 763 KB):** WebP lossy sa alfa kanalom bez gubitaka 82–92 KB (kvalitet 50–80, 41–44 dB prema PNG-u). Sa `alpha_quality 80` 67–73 KB (alfa se razlikuje najviše za 1/255), dakle alfa bez gubitaka košta oko 17–20 KB po kadru. Blender direktno: WEBP kvalitet 80 je 92 KB, 60 je 86 KB. **AVIF iz Blendera: kvalitet 60 je 26 KB, ali alfa kanal odstupa do 31/255 (kvalitet 45: do 48/255)**, pa se ivice providnosti kvare. Scena ima velike glatke površine, pa su veličine manje nego za fotografije. U našem repou su fotografski kadrovi 720×1280 bez alfa 52–58 KB. Zaključak: za providne sekvence WebP + `alpha_quality` oko 80; AVIF samo ako se alfa proveri na ivicama. (2026-10, izmereno)
- Uvek `<picture>` sa rezervom (AVIF → WebP → JPEG/PNG) za mirne slike (MDN). Za kadrove sekvence format se bira eksplicitno (ime fajla `.webp`), ne pregovaranjem na CDN-u (Vibe: 34–52 KB WebP naspram 360–600 KB PNG za isti URL).

**Kodiranje (polazne vrednosti, proveriti okom na etiketi i ivicama):**
- `cwebp`: `-q` 70–80 (podrazumevano 75), `-m 6` (sporije, manje), **`-sharp_yuv`** (oštrija RGB→YUV konverzija, važna za tekst i ivice; sporije), `-alpha_q` 80–100 (podrazumevano 100 = bez gubitka alfa kanala; u mom testu je 80 dao oko 20 % manji kadar uz grešku alfe do 1/255, ali ivice ipak proveriti), `-exact` isključeno (podrazumevano, bolje se kompresuje). ffmpeg `libwebp` (kao u `frames.py`) je prihvatljiv. (2026-10, developers.google.com/speed/webp/docs/cwebp)
- Testirati **ivice na svetloj i tamnoj pozadini** (halo od providnosti).
- Alati `cwebp`, `avifenc`, libvips i slični su spoljašnji programi: ako ih nema u okruženju, preuzimanje i instalacija idu preko `bezbednost`. U okruženju postoje ffmpeg i Pillow 12.3. To je u redu za naše sopstvene Blender renderove; za tuđe slike i snimke važe pravila iz `studio/znanje/izvori-i-licence.md` (izolovan ffmpeg, venv sa Pillow 13.0.0).

**Dimenzije i broj kadrova.**
- Renderovati **uski isečak oko proizvoda**, ne ceo ekran (Vibe: isečeno na limenku + referentna kutija). Broj piksela pada 3–5×, a to je i vreme renderovanja.
- Prikazna veličina u CSS pikselima × `min(DPR, 2)` = potrebna širina. Desktop set: duža strana 1280–1600 px. Telefon set: duža strana do 960 px (naš postojeći 540×960). Moguće renderovati 1,33× pa smanjiti na 0,75× (Vibe: supersampling radi oštrijih ivica).
- Broj kadrova: **60–90 po poglavlju** za 1–2 visine ekrana skrola, 120 samo za brzu radnju (padanje zrna). Naš `Player` glatko pomera indeks ka cilju, pa niži broj kadrova ne deluje kao "trzanje" (`cur += (target - cur) × 0,22`). (2026-10, repo + Vibe)
- Budžet (preporuka izvedena iz naših i Vibe merenja): **do 40 KB po kadru na telefonu, do 60 KB na desktopu; do 3,5 MB po sekvenci na telefonu**. Pun RGBA kadar 720×1280 iz moje probne scene je 67–92 KB (gore), pa se budžet drži samo isečkom oko proizvoda i smanjenom rezolucijom telefon seta; ceo sajt pre prve sekvence do oko 2 MB; svaka sekvenca se učitava tek kad se približi (Vibe: do 2,5 visine ekrana ranije; mi u `freiraum` prvo svaki 6. kadar, pa popunjavamo).

**Memorija na telefonu (račun, nije izvor).** Dekodiran kadar zauzima širina × visina × 4 bajta: 720×1280 = oko 3,5 MB, 80 kadrova odjednom = oko 280 MB. Zato držati dekodirane samo kadrove oko trenutnog položaja (klizni prozor) ili osloniti se na to da ih browser odbaci. iOS Safari ograničava ukupnu memoriju canvas-a (WebKit upozorenje "Total canvas memory use exceeds the maximum limit (384 MB)", granica zavisi od uređaja i verzije, **tačna vrednost NEPROVERENA**), zato jedan canvas po sekvenci i bez novih canvas-a po kadru. (2026-10, WebKit Bugzilla 195325, 190280)

**Rezervna ponašanja.** `prefers-reduced-motion`: jedan statičan kadar po poglavlju (Vibe učitava samo kadar 0, naš `Player` skače direktno na cilj). Bez JavaScript-a ili sporo: `poster` slika (`poster.png` iz `blender-umetnik.md`). Canvas `aria-hidden`, a sadržaj (naslov, cena) običan tekst u HTML-u.

**Alternativa: video vezan za skrol.** Matcha Cartel ima "Matcha Pouring Scroll Video" (Awwwards element, mehanizam nepotvrđen). Video je mnogo manji od niza slika, ali pomeranje `currentTime` je neujednačeno, naročito na iOS-u, i traži video kodiran sa svakim kadrom kao ključnim (ffmpeg `-g 1`). WebCodecs `VideoDecoder` daje tačan kadar (Chrome 94, Firefox 130, Safari 16.4), ali traži biblioteku za razdvajanje MP4, koju mora da odobri `bezbednost`. Preporuka: ostati na WebP sekvencama dok se ne pokaže da su prevelike. (2026-10, MDN browser-compat-data + Awwwards)

**Keš.** Imena sa heš-om i dugačak `Cache-Control` (`public, max-age=31536000, immutable`) u `netlify.toml` za folder sekvenci (preporuka, iskustvo; Netlify objavljuje `dist`).

## B8. Šta ovo znači za kafa projekat
- Tok `Blender (Cycles CPU) → PNG RGBA → WebP (d + m) → canvas sa sticky/pin scenom` je isti tok kao More Nutrition, Vibe, Seasats i Koffiracha, ali sa merljivim budžetom (B7).
- Jedan canvas koji prelazi preko granice sekcija (zrna padaju iz GRIND u POUR) je naša odluka iz `analiza-videa.md`; reč iza proizvoda je običan HTML tekst iza canvas-a (kao Vibe).
- **Najveći rizik je vreme renderovanja na 4 CPU jezgra** (B4 merenja): odrediti broj kadrova i rezoluciju po stvarnoj sceni, ne po brojevima iz ovog dokumenta.

## Arhiva

- **Sora 2 i Videos API (OpenAI):** ugašeni 2026-09-24, "nema zamene jedan-na-jedan". Ne koristiti. (2026-09, developers.openai.com)
- **Veo 3.1 Preview modeli u Gemini API-ju** (`veo-3.1-generate-preview`, `-fast-`, `-lite-`): ugašeni 2026-10-22. Veo 3 (`veo-3.0-*`): zastareo. Migracija: Gemini Omni Flash ili GA Veo 3.1 na Vertex-u. (2026-10, ai.google.dev)
- **`gemini-2.5-flash-image`:** ugašen 2026-10-02, zamena Nano Banana 2 Lite. (2026-10, ai.google.dev)
- **Filmic** (Blender): zastareo, zamenjen AgX-om (a za proizvode postoji Khronos PBR Neutral). (2026-10, Blender Manual)
- **Blender 4.2 LTS:** podrška istekla jula 2026. (2026-10, blender.org)
- **Luma Ray 2 / `ray-flash-2`** (stariji API na docs.lumalabs.ai): zamenjen Ray 3.2 na docs.agents.lumalabs.ai. (2026-10, docs.lumalabs.ai)
