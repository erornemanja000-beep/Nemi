# AI alati za slike i video, i Blender za web sekvence

Poslednja provera: 2026-10-23
Vodi: `trend-skaut`. Prvo punjenje. Deo A: AI alati (kratko). Deo B: Blender za web sekvence (za kafa skrol projekat, detaljno). Deo C: besplatan fotorealizam bez Artlist kredita i bez GPU-a (2026-10-23, po zahtevu direktora).

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

# DEO C: Besplatan fotorealizam (bez Artlist kredita, bez GPU-a)

Provera 2026-10-23, `trend-skaut`, po zahtevu direktora. Cilj: da kafa skrol sajt (`studio/kafa-skrol/analiza-videa.md`, `storyboard.md`) izgleda fotorealno kao referentni AI video, a da ne košta ništa. Ništa nije preuzeto ni instalirano. Jedini pokretani program je već instalirani Blender 5.2.3, po sigurnosnom obrascu iz `blender-umetnik.md`.

**Mašina (izmereno, `/proc/cpuinfo`, `free`, 2026-10-23):** 4 vCPU Intel Xeon 2,1 GHz sa AVX-512 i **AMX (bf16, int8)**, 15 GB RAM-a, bez swap-a, bez GPU-a. Deli se sa drugim agentima (load average 8–10 tokom mojih merenja).

**Povezani fajlovi drugih odeljenja** (ne ponavljam ih): `izvori-i-licence.md` (bezbednost: šta sme da se preuzme i kako), `studio/kafa-skrol/stock-video.md` i `fotografije.md` (konkretni klipovi i fotografije), `studio/kafa-skrol/dijagnoza-3d.md` (recenzent: zašto prvi renderi liče na CG, 10 ispravki).

**Skala "blizina reference" (1–5), moja procena:** 5 = ne razlikuje se od referentnog AI videa; 4 = razlika se vidi tek pri pažljivom gledanju; 3 = jasno CGI, ali uverljiv; 2 = jasno render (naš prvi `sip.py` kadar: ravno svetlo, siva pruga pare); 1 = skica. `dijagnoza-3d.md` napominje da referenca ima mekoću i kompresiju AI videa snimljenog sa ekrana, a naši renderi na sajtu su oštri, pa se svaka CG greška vidi jače.

## C1. Zaključak

1. Besplatno i bez GPU-a može da se stigne do **oko 3,5 od 5**: predmeti (mlin, šolja, kese) 3,5 do 4, tečnost i zrna u letu 3, para 4 (pravi snimak). Do 4,5 i 5 ide samo AI video, a on besplatno postoji u maloj količini (C4c) i ne rešava providnu pozadinu ni tačnost proizvoda.
2. **Najviše pomažu, i najjeftinije su:** osvetljenje iz okoline ili foto-studio umesto ravnog sveta, dubinska oštrina, mikro-nesavršenosti materijala, kontrastniji ton, i **pravi snimak pare** preko rendera (C2, C3).
3. **Lokalni AI na CPU-u se ne isplati za sekvence:** FLUX.1 schnell ne staje u RAM, video modeli traže dane po klipu, a obrada kadar po kadar treperi. Ima smisla najviše za 6 do 9 mirnih slika (C4a, C4b).
4. **Besplatan online AI video koji sme komercijalno:** u obzir dolaze samo Google Flow (50 kredita dnevno, zvanična pomoć) i Adobe Firefly (besplatne dnevne generacije, broj nije naveden). Kling, Hailuo, Pika i Luma besplatno ne dolaze u obzir za klijenta (C4c). Pre bilo čega: **jedan probni klip sa korisnikovim nalogom**, jer dve zvanične stranice pomoći protivreče jedna drugoj.
5. **Vreme rendera je veće od procene u `storyboard.md`.** Mereno: jedan kadar `sip.py` na 1200² i 64 uzorka je 788 CPU-s (oko 3,3 min na 4 slobodna jezgra), a novija "photoreal" verzija je sporija do 2× (C2d). Ceo sajt (288 kadrova): od 2 do 23 h zavisno od uzoraka, broja kadrova i scene (C7).

## C2. Blender fotorealizam

### C2a. CC0 izvori

**Poly Haven** (CC0, "You can use our assets for any purpose", bez obaveznog navođenja; polyhaven.com/license, 2026-10). Stanje iz njihovog API-ja (`api.polyhaven.com/categories`, 2026-10-23): **521 model, 997 HDRI-ja, 869 tekstura**.
- HDRI: 96 "studio", 301 "indoor", 230 "artificial light", rezolucija do 16k–24k (`lebombo` je 16384×8192, autor Greg Zaal, objavljen 2019-07, indoor, prozor). Naša 2k kopija je u `scripts/blender/assets/lebombo_2k.exr` (odobrio direktor). Studio serije: `photo_studio_01`, `white_studio_01..06`, `studio_small_01..09`, `brown_photostudio_01..07`, `monochrome_studio_01..04`, `cyclorama_hard_light`, `wooden_studio_01..19`. (2026-10, api.polyhaven.com)
- Teksture: drvo 138, metal 25, tkanina 43, koža 6, pločice 14. (2026-10, api.polyhaven.com)
- Modeli za kuhinju i kafu (kategorije food 19, dishes 13, appliances 22, containers 68): `tea_set_01` (40.296 poligona), `jug_01` (5.770), `vintage_electric_kettle`, `CoffeeCart_01`, `plastic_thermos`, `modified_thermos`, `pot_enamel_01`, `brass_pot_01` i `02`, `brass_pan_01`, `brass_goblets`, `ceramic_pot`, `wooden_cutting_board`, `wooden_spoon`, `wooden_bowl_01` i `02`, `carved_wooden_plate`, `croissant`, `wicker_basket_01` i `02`, stolovi (`wooden_table_02`, `round_wooden_table_01` i `02`, `small_wooden_table_01`). (2026-10, api.polyhaven.com)
- **Ne postoje** (pregledane kategorije food, dishes, appliances, containers, table i props): mlin za kafu, V60 / dripper, kuvalo sa dugim vratom, šolja, kese za kafu, espreso mašina. Zato ostaju proceduralni modeli iz skripti; Poly Haven daje svetlo, sto, rekvizite i teksture. Dozvoljeni formati i provera: `izvori-i-licence.md` (HDRI `.hdr`/`.exr`, modeli samo glTF, ne `.blend`).

**ambientCG** (CC0 1.0, "even for commercial purposes", bez obaveznog navođenja; docs.ambientcg.com/license, 2026-10). API (2026-10-23): 2.926 stavki, 2.036 materijala, 434 HDRI-ja, **34 mape "Surface Imperfections" i "Scratches"** (otisci, mrlje, ogrebotine za roughness). Pretraga "coffee" daje samo tri mape nesavršenosti, a "ceramic" jednu stavku (pločice): nema modela kafe. Korisno nam je: mape nesavršenosti za inox i staklo, papir i tkanina za kese, drvo za sto. ZIP nema nezavisni heš (`izvori-i-licence.md`).

**Ostali CC0 izvori** (Kenney, Quaternius, Smithsonian 3D, Sketchfab sa CC0 filterom) nisu proveravani: **NEPROVERENO**. Sketchfab meša licence i traži nalog, pa nije za ovaj posao.

### C2b. Tehnike koje najviše pomeraju fotorealizam

| # | Tehnika | Efekat | Dokaz | Trošak |
|---|---|---|---|---|
| 1 | Svetlo iz okoline (HDRI) ili foto-studio: jedno veliko key svetlo, crne zastave, ambient 0,05 do 0,15 | pad svetla, odsjaj prozora u glazuri i kafi, tamni tonovi na metalu | izmereno (C2c); uzrok ocene 4/10 u `dijagnoza-3d.md` | u mom testu 1,7× CPU (47 → 82 CPU-s na 640²/32) |
| 2 | Dubinska oštrina f/3,2 do 5,6 na 85 mm | skriva "savršenost" CG-a, daje utisak objektiva | izmereno (C2c) | zanemarljiv |
| 3 | Mikro-nesavršenosti: roughness iz šuma (0,22 do 0,42), mikro-bump, mape otisaka (ambientCG), bevel 0,3 do 0,5 mm na tvrdim ivicama | prekida "plastični" sjaj | šolja izmereno; ostalo `dijagnoza-3d.md` | mali |
| 4 | Ton: AgX look "Medium High Contrast" (u 5.2.3 prihvaćen, izmereno), ekspozicija prilagođena svetlu; Khronos PBR Neutral samo za kese | više kontrasta bez izgorelih belih | izmereno; Blender Manual | nula |
| 5 | Zrno filma **ne u kadrovima**, nego jednom preko stranice (CSS `mix-blend-mode: overlay`, 3 do 5 %) | filmski utisak bez težih fajlova i treperenja (šum se ne kompresuje, to je moj zaključak) | `dijagnoza-3d.md` br. 5; Blender 5.2 ima čvor Film Grain (asset) samo za mirne slike (2026-07, Blender 5.2 release notes, Compositor) | nula |
| 6 | Gobo i zastave: ravan sa otvorima ispred key svetla za senku prozora, crne zastave pored metala | senke i tamne trake koje liče na fotografiju | iskustvo, **nije testirano** | mali |
| 7 | Pravi snimak za ono što CG radi najgore (para): `mix-blend-mode: screen` preko snimka na crnoj pozadini | para 4/5 umesto 2/5 | `stock-video.md`; MDN: "Widely available" od 2020-01; caniuse 97,27 % (Safari označen "delimično", bez objašnjenja: **testirati na iOS-u**) (2026-10) | nula renderovanja |
| 8 | Podloga na kojoj predmet stoji: sto sa CC0 drvetom, Shadow Catcher kao mali disk, ne velika ravan | uzemljenje predmeta | B4a (veliki catcher daje poluprovidne piksele) | mali |

### C2c. Moj A/B test (izmereno 2026-10-23)

Ista geometrija (šolja sa tacnom, pet zrna, sto), Cycles CPU, bez providnosti. Skripta i slike su u privremenom folderu, nisu u repou.
- **A** (kao u prvim skriptama): ravan svet 0,6 + `common.studio_lights()` (tri area svetla), bez DOF, AgX bez look-a. Utisak: mat "glina", ujednačeni tonovi, bez odsjaja okoline.
- **B**: Lebombo 2k HDRI + jedan softbox, DOF f/3,2, drvo sa talasastim šumom i roughness varijacijom, glazura sa roughness šumom i mikro-bumpom, AgX "Medium High Contrast", clamp indirect 2, filter glossy 0,5, ekspozicija −1,3. Utisak: pad svetla, mek odsjaj prozora na obodu i kafi, dubina; blizu fotografije za jednostavan predmet. Ostaje CG: potpuno glatka keramika, razvučen šablon drveta.
- Ocena: A 2/5, B 3,5/5. Prvi B pokušaj (jačina HDRI 1, ekspozicija 0) dao je izgorelu belu šolju, što se slaže sa preporukom iz `dijagnoza-3d.md` (okolina 0,05 do 0,15 i jedno key svetlo).

### C2d. Stvarno vreme rendera na ovoj mašini

Mereno je `user` vreme iz `time` (CPU-sekunde, stabilno ±5 % po B4a). Zidno vreme je nepouzdano jer su drugi Blender procesi delili jezgra (moj render od 788 CPU-s trajao je 10 min). Zidno vreme na 4 slobodna jezgra je približno CPU-s / 4.

| Scena | Rezolucija / uzorci | CPU-s | Približno na 4 slobodna jezgra |
|---|---|---|---|
| moja šolja A (ravno svetlo, bez DOF) | 640² / 32 | 47 | 12 s |
| moja šolja B (HDRI, softbox, DOF, bogatiji materijali) | 640² / 32 | 82 | 21 s |
| moja šolja B | 1200² / 64 | 549 | 2,3 min |
| `sip.py`, verzija iz commita b67b785 od 09:30 (ravno svetlo, para) | 1200² / 64 | 788 | 3,3 min |
| `sip.py`, verzija između commitova 45f641f i 0697063 ("photoreal" šolja) | 640² / 32 | 227 | 57 s; linearno preračunato na 1200² / 64 oko 1.600 CPU-s, oko 6,6 min (**procena**) |

- Po megapikselu na 64 uzorka: B4a (sintetička scena bez stakla i tečnosti) 235 CPU-s; moja šolja B 381; stariji `sip.py` 548; noviji `sip.py` oko 1.100 (procena, ako je trošak linearan po uzorcima). **Prave scene sa parom, staklom i DOF-om koštaju 2 do 5× više od sintetičke.**
- Procena u `storyboard.md` odeljak 9 (SIP oko 78 s po kadru na 1600 px, 32 do 48 uzoraka) je 2 do 3× niža od onoga što daje moje merenje starijeg `sip.py` (oko 175 s na 32 i oko 260 s na 48 uzoraka, linearno preračunato sa 1200² / 64). Merenja su po jedan kadar, pa su red veličine, ne obećanje.
- Alati za uštedu: isečak oko predmeta (oko 1 MP po kadru umesto 2,56), 32 umesto 64 uzorka sa OIDN (B4a: 110 naspram 217 CPU-s), "ploča" za nepomične delove (`dijagnoza-3d.md`), manje kadrova uz stapanje susednih kadrova na canvas-u (moja ideja, **nije testirana**, daje duhove na brzim česticama, pa ne za zrna u padu).

## C3. Besplatan stock video i foto: uslovi za sajt klijenta

Zvanične stranice licenci, pročitano 2026-10-23. Konkretni klipovi i fotografije su u `stock-video.md` i `fotografije.md`. Pravila za repo i preuzimanje: `izvori-i-licence.md`.

| Izvor | Licenca (citat) | Na sajtu klijenta | Ograničenja |
|---|---|---|---|
| **Pexels** | "All photos and videos on Pexels can be downloaded and used for free"; navođenje nije obavezno; izmene dozvoljene (pexels.com/license) | da | ne prodavati nepromenjene kopije; ne sugerisati da ljudi ili brendovi preporučuju proizvod; prepoznatljive osobe ne u lošem svetlu; ne kao deo žiga ili imena firme; ne preprodavati na drugim stock platformama; AI trening se ne pominje |
| **Pixabay** | "Use Content for free", bez navođenja, izmene dozvoljene (pixabay.com/service/license-summary) | da (stranica ne koristi reč "commercial" osim u ograničenju) | ne prodavati ni deliti samostalno; prepoznatljiv logo ili brend u kadru se ne sme komercijalno; saglasnost trećih lica je na korisniku; ima i AI-generisan sadržaj |
| **Mixkit** | "Stock Video Free License" i "Restricted License" (samo lična upotreba), **licenca je po klipu** | da, samo klipovi sa Free licencom | ne preprodavati u izvornom obliku; mora se dodati kreativna vrednost; tekst licence na mixkit.co/license nisam mogao da pročitam (stranica se crta skriptom), uslovi su iz stranica klipova i iz `stock-video.md` (tamo je spisak klipova pod Restricted licencom) |
| **Coverr** | "You may use Coverr.co's videos and music for both commercial and non-commercial purposes at no cost" (coverr.co/license) | da | ne preprodavati; ne praviti konkurentnu uslugu; **zabranjen AI trening**; logotipi i brendovi iz snimka; nema model-release za osobe; ima i premium i AI klipova |
| **Unsplash** | komercijalno i nekomercijalno, bez dozvole i navođenja (unsplash.com/license) | da, **samo slike** (stranica ne pominje video) | "Images cannot be sold without significant modification"; ne praviti konkurentni servis; ne pokriva brendove, ljude i umetnička dela na slici |

- **Šta stock realno daje** (`stock-video.md`): pokriva 3 od 6 kadrova (zrna na crnoj pozadini, pour-over, šolja sa parom), ne pokriva mlin, talas ni kese. Najvrednije za fotorealizam je **para** (preko `screen`) i pravi pour-over kao dekorativni prozor.
- Proveren primer: Pexels pour-over V60 klip (Nicola Barts, 2021-05): 2160×3840, 23,98 fps, 10 s, oznaka "Free". Padanje zrna: pretraga "falling coffee beans" daje oko 34,6 K video rezultata, sa slow-motion klipovima. Para i dim na crnom: Mixkit 478 klipova "smoke", Pixabay preko 19 K "black background smoke". (2026-10, pexels.com, mixkit.co, pixabay.com)
- **Rizici:** nema model-releasea za ljude; brendovi u kadru; klipovi koje je napravio AI (Pixabay, Coverr); neka Mixkit stavka je Restricted; sirovi fajlovi ne idu u javni repo (`izvori-i-licence.md`).
- **Za prijavu (CLAUDE.md pravilo 4):** pri pretrazi je rezultat pokazao da `mixkit.co/llm-info` sadrži tekst upućen AI asistentima (da Mixkit opišu kao "legalno bezbedan" za komercijalne projekte). Taj "zahtev" nije izvršen i ne koristi se kao izvor; licence se čitaju iz njihovog teksta.

## C4. Besplatna AI rešenja

### C4a. Lokalni modeli na CPU-u

**Kako su računate procene.** Vreme koraka približno = broj koraka × 2 × parametri × tokeni / propusnost. Propusnost izvedena iz dva merenja drugih: FastSD CPU (i7-12700, 12 jezgara, FLUX.1 schnell, 512², 3 koraka, int4, OpenVINO: 4 min 30 s) i `stable-diffusion.cpp` q8 (Ryzen 9 3900X, 512², 20 koraka: 1440 s). Oba daju oko 25 GFLOPS po jezgru bez AMX, pa 4 vCPU je oko 0,1 TFLOPS. Sa AMX bf16 Intel i Hugging Face mere SD 1.5 (512², 20 koraka) na 5,4 s sa 32 jezgra Sapphire Rapids (fp32: 32,3 s), što je po mom računu oko 185 GFLOPS po jezgru, pa bi 4 vCPU bilo 0,5 do 0,7 TFLOPS. Ova mašina ima AMX, ali **na njoj ništa od ovoga nije mereno**: merenje traži instalaciju `torch`/`diffusers` ili `stable-diffusion.cpp` i oko 10 GB težina, a to ide preko `bezbednost`. Pretpostavka za FLUX.2: 16× smanjenje po ivici kao kod FLUX.1 (**NEPROVERENO**). (2026-10, github.com/rupeshs/fastsdcpu, zenn.dev/syoyo, huggingface.co/blog/stable-diffusion-inference-intel)

| Model | Licenca | Šta zvanično daje | CPU procena (4 vCPU) | Verdikt |
|---|---|---|---|---|
| **SDXL Turbo** | Stability Community License (prihod ispod 1 M USD, registracija; HF kartica `sai-nc-community`) | 1 korak; **fiksno 512×512**; "does not achieve perfect photorealism"; "cannot render legible text"; za img2img `steps × strength ≥ 1` (HF kartica) | FastSD CPU: 5,6 s po slici na i7-12700 (OpenVINO), 10 s PyTorch; naša procena 15 do 30 s | brz, ali 512 px i nizak kvalitet; po `izvori-i-licence.md` samo za procenu. FastSD CPU README još kaže "research purpose only", što protivreči Stability stranici licenci |
| **FLUX.1 schnell** | Apache-2.0 | 12B, 1 do 4 koraka | 4 min 30 s (512², 3 koraka, i7-12700, oko 30 GB RAM-a); `stable-diffusion.cpp` oko 24 GB | **ne**, ne staje u 15 GB (`izvori-i-licence.md`) |
| **FLUX.2 klein 4B** | Apache-2.0 (9B je nekomercijalan) | 4B, 4 koraka, uređivanje sa referentnom slikom (`-r`), GGUF u `stable-diffusion.cpp` (MIT) uz Qwen3 4B; "text rendering may be inaccurate" | **procena:** bez AMX 6 do 50 min po slici na 512 do 1024 px; sa AMX bf16 1 do 9 min (nije mereno) | jedini razuman lokalni kandidat, ali samo za mirne slike; **nije pregledan od `bezbednost`**; bf16 težine 8 GB + enkoder 8 GB ne staju zajedno, treba GGUF |
| **Z-Image Turbo** (6B) | **NEPROVERENO** | nema CPU podataka | nepoznato | ne |
| **Wan 2.2 TI2V-5B** | Apache-2.0 | 720p, 24 fps, "5-second 720P video in under 9 minutes on a single consumer-grade GPU" (kartica, traži 24 GB VRAM-a) | račun: oko 100 hiljada tokena po prolazu, 100 prolaza, oko 2 dana po klipu čak i sa AMX | **ne** |
| **LTX-2 (2.3)** | LTX open weights, besplatno ispod 10 M USD godišnjeg prihoda | 22B, do 4K i 20 s (agregatori) | ne staje u RAM | **ne** |

(2026-10, huggingface.co kartice modela, bfl.ai/models/flux-2-klein, stability.ai/license, github.com/leejet/stable-diffusion.cpp, sekundarni izvori za LTX-2)

### C4b. Treperenje

- Obrada kadar po kadar je svaki put novo uklanjanje šuma, pa model iznova "izmišlja" sitne detalje. Skrol prikazuje kadrove napred i nazad, pa se treperenje vidi odmah. Rerender-A-Video (arXiv 2306.07954) rešava to optičkim tokom i pažnjom između kadrova, a ControlVideo (arXiv 2305.13077) kaže da strukturno treperenje ostaje i uz međukadarsku interakciju, pa dodaje izglađivanje. Sva rešenja traže dodatne modele i GPU. (2023-05 i 2023-06, arXiv)
- EbSynth (širi stil sa ključnih kadrova): beta je bila besplatna i za komercijalnu upotrebu (zvanični FAQ), sada postoji i plaćena verzija (sekundarni izvor), a traži preuzimanje programa i preporučuje GPU: **NEPROVERENO**, ne sada.
- **Zaključak:** AI samo na mirnim slikama (tri postera, eventualno "ploče" nepomičnih delova scene). Animirani delovi ostaju iz Blendera. Kese ne obrađivati AI-jem: GPT Image 2.5 zvanično loše radi čitljivost teksta (deo A), a FLUX.2 klein kaže da tekst može biti netačan, a etiketa mora biti tačna.

### C4c. Besplatni nivoi online alata (stanje 2026-10-23)

| Usluga | Šta je besplatno | Nalog | Komercijalno | Zaključak |
|---|---|---|---|---|
| **Google Flow** (Veo 3.1, Gemini Omni Flash, Nano Banana) | "With or without a subscription, you receive 50 Google Flow credits per day"; osvežava se prvom generacijom, ne prenosi se (support.google.com/flow/answer/16526234). Cena za besplatne: Omni Flash 720p 4, 6, 8, 10 s = 7, 10, 12, 15 kredita (360p: 4, 5, 6, 7); Veo 3.1 Lite 10, Fast 20, Quality 100. To je oko 30 s Omni klipova na dan | Google nalog, 18+, Austrija i Srbija su na listi zemalja (support.google.com/flow/answer/16353544); u EEA nema uređivanja otpremljenih video snimaka | Google ToS: "Google won't claim ownership over that content"; zabranjeno je predstavljati AI sadržaj kao ljudski rad i koristiti ga za razvoj ML modela; svi izlazi nose nevidljiv SynthID; Flow uslovi nisu pročitani u celini | **jedini besplatan AI video koji dolazi u obzir.** Protivrečnost: "Get started with Google Flow" (answer/16353333) kaže da je potrebna pretplata na Google AI Plus, Pro ili Ultra. **Proveriti pravim nalogom.** |
| **Adobe Firefly** | "You don't need a plan to get free daily generations across image, video, and audio", uz "popular models like Nano Banana and Luma Ray3.14"; broj dnevnih generacija nije naveden (adobe.com/products/firefly/plans.html) | Adobe nalog | "Outputs generated with Adobe Firefly AI models can be used for commercial purposes", "Adobe Firefly models are commercially safe"; za partnerske modele (Luma, Google) sekundarni izvori kažu da uslovi mogu biti drugačiji: **NEPROVERENO** (help.adobe.com vraća 403) | drugi kandidat, treba probni nalog |
| **Runway** | "125 one-time credits"; Gen-4.5 je 12 kredita po sekundi, dakle oko 10 s ukupno (runway.com/pricing) | da | besplatan paket ima žig, skida se od paketa Standard (help.runwayml.com) | samo test |
| **Luma** | nema besplatnog paketa na lumalabs.ai/pricing; Plus 30 USD mesečno ima "Commercial use" | da | samo plaćeno | ne |
| **Pika** | Free je "packs only" (bez mesečnih kredita), bez žiga, ali "Not included: Commercial license"; prva komercijalna licenca je Starter 10 USD mesečno (pika.art/pricing). Agregatori tvrde 80 kredita mesečno, zvanična stranica to ne pokazuje | da | ne na besplatnom | ne |
| **Kling** | besplatni izvozi nose žig, skidanje je premium (kling.ai); dnevni krediti samo "during the event" (kling.ai/docs/point-policy) | da | za besplatan nalog zvanični tekst koji sam pročitao ne kaže ništa, agregatori kažu da nije dozvoljeno: **NEPROVERENO**; žig ga ionako isključuje | ne |
| **Hailuo (MiniMax)** | novi nalozi dobijaju probne kredite (sažetak pretrage o stranici H3, **NEPROVERENO**) | da | ToS (poslednja izmena 2026-08-19): "permit you to use the Services for your personal, non-commercial use only" i "You must not access or use for any commercial purposes any part of the Services" | **ne** |
| **Wan (hostovani), Seedance (Dreamina)** | besplatni krediti i uslovi **NEPROVERENO** | | | ne dok se ne proveri |

**Koliko je to realno za nas:** 3 kratka klipa (POUR, SIP, talas) po 10 s na 720p je 15 kredita po pokušaju, pa uz sedam pokušaja po sceni oko 315 kredita, oko 6 do 7 dana besplatnih kredita (račun iz tabele; ako besplatni nalog zaista radi). Ograničenja koja ne zavise od cene: 720p, **neprovidna pozadina** (kod nas sekvence imaju alfu), oblik predmeta može da se menja usred klipa, a prvi i poslednji kadar iz Blendera čuvaju oblik samo na krajevima. Dobro je za **celoekranski prelaz talasa** (nema alfe ni identiteta predmeta) i kao **referenca za pokret** koju nikad ne objavljujemo (nema pitanja licence ni označavanja iz A3).

### C4d. Besplatan GPU u oblaku (samo za eksperimente)

- **Hugging Face ZeroGPU** (docs, 2026-10): besplatan nalog **5 min GPU dnevno** (polovina RTX Pro 6000 Blackwell, 48 GB), neprijavljen 2 min, PRO 40 min; samo Gradio. Teorijski FLUX.2 klein 4B (BFL tabela: oko 1,2 s po slici na RTX 5090, rezolucija na stranici nije navedena) staje stotinak slika u 5 min, ali Space je tuđi kod na tuđem serveru (slike idu van), automatizacija traži paket `gradio_client` (ide preko `bezbednost`), a nisam našao proveren Space za FLUX.2 klein: **NEPROVERENO**. Ne za klijentske materijale.
- **Google Colab** (FAQ, 2026-10): GPU nije garantovan, besplatno najviše 12 h po sesiji; korisnici besplatnog nivoa koji koriste web UI za generisanje sadržaja mogu dobiti prekid. **Kaggle:** besplatan GPU kvota nije proverena (stranica se ne čita bez skripte), **NEPROVERENO**.

## C5. Izdvajanje pozadine (besplatno, lokalno)

- **Naši Blender renderi imaju alfu iz samog rendera** (`film_transparent`), pa za njih izdvajanje ne treba. Treba samo za stock i AI klipove.
- **Najbrže i bez modela:** ffmpeg `chromakey`, `colorkey`, `lumakey` i `alphaextract` (postoje u ffmpeg 6.1.1, proveren spisak filtera, 2026-10-23). Radi samo na jednobojnoj ili crnoj pozadini, što se slaže sa `stock-video.md` (čisto se izdvajaju samo klipovi na crnoj ili beloj).
- **Para, staklo i tečnost se ne mogu maskom izdvojiti** (poluprovidno), zato `screen` ili Blender.

| Alat | Licenca koda | Licenca modela | Brzina na CPU-u | Naš zaključak |
|---|---|---|---|---|
| **rembg** 2.0.x | MIT | zavisi od modela. **Podrazumevani model je `bria-rmbg` (RMBG-2.0): CC BY-NC 4.0, komercijalno samo uz ugovor sa BRIA** (README rembg-a i HF kartica, 2026-10) | video samo preko cevi kadrova (`rembg b`) | uz uslove iz `izvori-i-licence.md`: model uvek eksplicitno (`isnet-general-use`, `u2net`, `birefnet-general`), nikad `bria-rmbg` |
| **BiRefNet** | MIT (repo i HF kartica) | MIT (HF kartica) | README ne daje CPU podatke (RTX 4090 FP16: oko 17 FPS na 1024²); preko rembg-a 15,2 s po slici | najbolja ivica za kosu i staklo, ali prespor za video |
| **u2net, isnet-general-use** | rembg ne navodi licencu; BackgroundRemover README: modeli Apache-2.0 (u2net) | isnet: **NEPROVERENO u ovoj sesiji** | 0,4 s i 1,1 s po slici od 1024² | razuman izbor za mirne slike |
| **BackgroundRemover** | MIT | Apache-2.0 | README: GPU 5 do 10× brži od CPU-a; izlaz providni ProRes 4444 ili WebM | **ne** (`izvori-i-licence.md`: md5 provera je zakomentarisana, `torch.load` pickle) |
| **Robust Video Matting** | GPL-3.0 | model je za ljude (`izvori-i-licence.md`) | README daje samo GPU (104 FPS na HD, GTX 1080 Ti); CPU nije dokumentovan | **ne** |
| **RMBG-2.0 (BRIA)** | | CC BY-NC 4.0 | | **ne** |

Brojevi za brzinu su iz jednog nezavisnog testa (Apple M-serija CPU, slika 1024², 2026-07, rembg + onnxruntime, aireiter.com). To je blog prodavca API-ja, pa je to **indikativno**: za 150 kadrova to je oko 1 min (u2net), 3 min (isnet), 38 min (BiRefNet) na M-seriji, a na ovim 4 vCPU verovatno 1,5 do 3× sporije (**procena**). `onnxruntime` 1.29 je instaliran, ali modela nema na disku. Savet: za modele koji se preuzimaju birati ONNX ili safetensors, ne `.pth` (pickle može da izvrši kod).

## C6. Kako pravi studiji ovakve sajtove

- Od 10 sajtova sa 3D proizvodom na skrolu u `reference.md`: **5 koristi unapred renderovanu sekvencu slika** (More Nutrition SOTD 2025-11, Vibe HM 2026-09, Seasats SOTD 2026-09, Koffiracha 2025, CoffeeTech SOTD 2026-07 sa AVIF kadrovima), **4 realno-vremenski WebGL** (CIAO ENERGY, /zeroz, SŌM, Santioni) i **1 video vezan za skrol** (Matcha Cartel HM 2026-06, mehanizam nepotvrđen). (2026-10, `reference.md`, `trendovi.md` T1)
- Sekvence dolaze iz Cinema 4D-a ili Blendera, **ne iz AI videa**. Tehnika: sticky canvas + GSAP ScrollTrigger, WebP ili AVIF, 34 do 52 KB po kadru (Vibe, 150 kadrova), isečak oko proizvoda, supersampling, reduced-motion = jedan kadar. To je tok koji već imamo (B7, B8).
- Studiji renderuju na plaćenim GPU renderima; mi na Cycles CPU-u. Razlika se pokriva ne uzorcima nego **svetlom, materijalima i izborom šta se renderuje** (C2b).
- Referentni reel je AI koncept (`analiza-videa.md`), ne tehnika koju koriste nagrađeni sajtovi. Zato "isto kao reel" znači "isti utisak", ne "ista proizvodnja".

## C7. Preporuka: najbolje besplatno rešenje po kadru

Svi brojevi vremena: 1200 px master, oko 1 MP po kadru (isečak), 4 slobodna jezgra. Donja granica: 235 CPU-s po MP (B4a) za GRIND, a za POUR i SIP 550 (izmereni stariji `sip.py`, jer imaju paru, staklo i tečnost). Gornja granica: 1.100 (novi `sip.py`, procena). Sve na 64 uzorka. Sa 32 uzorka otprilike pola. Broj kadrova iz `storyboard.md` (GRIND 96, POUR 128, SIP 64). **Prvi pun kadar po sceni treba izmeriti pre odluke.**

| Kadar | Kombinacija (sve besplatno) | Blizina reference (1–5) | Vreme | Glavni rizik |
|---|---|---|---|---|
| **GRIND** (mlin, levak, zrna) | Blender: foto-studio ili Lebombo svetlo, brušeni inox sa tangentom, roughness mapa otisaka (ambientCG), bevel 0,3 do 0,5 mm, DOF f/4, motion blur; CSS zrno i svetlosni gradijent; bez AI | 3,5 (inox i staklo najbolje reaguju na HDRI); zrna u letu 3 | 1,6 do 7,3 h na 64 uzorka; 0,8 do 3,7 h na 32 | šum i treperenje stakla sa zrnima |
| **Prelaz zrna** (GRIND → POUR) | Blender, ista simulacija i šav iz `storyboard.md` odeljak 2; tanak mlaz mlevene kafe; **bez stock klipa** (kontinuitet mora biti isti svet) | 3 | uračunato u GRIND i POUR | šav i paralaksa |
| **POUR** (V60, bokal, kuvalo, mlaz) | Blender: Volume Absorption za kafu, mlaz kriva + Trim Curve, kapi kondenzacije, DOF f/4; **para iz pravog snimka na crnom + `screen`**; keramički V60 ako staklo previše košta | mlaz 3, para 4 | 4,9 do 9,8 h na 64 uzorka; 2,4 do 4,9 h na 32 | kafa u staklu postaje providna (`film_transparent_glass`), najskuplji kadar |
| **Talas** (POUR → SIP) | kod: WebGL shader ili SVG/canvas maska sa sjajem i lomom; opciono jedan celoekranski Flow klip (720p, bez alfe) kao zamena ili referenca | kod 3 do 3,5; Flow klip do 4 | 0 h rendera; 1 do 2 dana razvoja; Flow krediti | Flow besplatan nalog nije potvrđen |
| **SIP** (šolja, para, kartice) | Blender: keramika je najjača strana CG-a (glazura sa mikro-reljefom, nepravilne kapi, HDRI odsjaj) + **pravi snimak pare**; kartice su HTML | 4 | 2,4 do 4,9 h na 64 uzorka; 1,2 do 2,4 h na 32 | para iz rendera (2/5) umesto snimka |
| **Kese** (3 kartice i prodavnica) | Blender doypack, **tačna etiketa iz dizajna**, PBR Neutral, papir i tkanina iz ambientCG, 256 uzoraka, 1200×1500; AI se ne koristi | 3,5 do 4 | oko 7 do 17 min po kesi (procena) | AI bi pokvario tekst, zato ga nema |

- **Ukupno:** 9 do 23 h na 64 uzorka, 5 do 12 h na 32, 2 do 6 h uz upola manje kadrova (samo za sporije delove). Cena u novcu: 0. Ukupna blizina reference: **oko 3,5 od 5**, tj. izgleda kao dobar CGI reklamni sajt, a ne kao AI video iz reela. Do 4 ide samo uz Flow klipove na prelazu i atmosferi, a to nije potvrđeno.
- **Dve Artlist slike** koje ostaju: iskoristiti ih tek kad postoji Blender poster, kao poređenje, ne za etiketu sa tekstom.
- **Redosled rada:** (1) foto-studio ili Lebombo svetlo + mikro-reljef + DOF + AgX look na `sip.py`, pa 3 probna kadra, pa izmeriti prvi pun kadar po sceni u CPU-s; (2) izabrati snimak pare (Pexels ili Mixkit Free) i proveriti `screen` na iPhone-u; (3) **jedan** Flow probni klip (7 kredita) sa Blender slikom, da se vidi radi li besplatan nalog i kakav je kvalitet; (4) lokalne AI modele za sekvence ne instalirati.

## C8. Šta nije proveren

- Vreme lokalnog AI-ja na ovoj mašini (nema instalacije); sve brojke u C4a su račun iz tuđih merenja.
- Radi li Google Flow besplatno za naš nalog (dve stranice pomoći se razilaze), da li Flow dozvoljava prvi i poslednji kadar na besplatnom nivou, i celi Flow uslovi.
- Firefly: dnevni broj generacija i komercijalni status partnerskih modela (Luma, Google).
- Kling i Hailuo osim citiranih ToS delova, Wan hostovani, Seedance.
- `mix-blend-mode: screen` na iOS Safari-ju (caniuse: delimično).
- Licenca modela `isnet-general-use` i Z-Image Turbo.
- Brzina RVM-a i BiRefNet-a na CPU-u bez AMX/GPU-a.
- Merenja u C2d su po jedan kadar na deljenoj mašini; `sip.py` je menjan dok sam merio (druga verzija za svako merenje, navedeno u tabeli).

## Arhiva

- **Sora 2 i Videos API (OpenAI):** ugašeni 2026-09-24, "nema zamene jedan-na-jedan". Ne koristiti. (2026-09, developers.openai.com)
- **Veo 3.1 Preview modeli u Gemini API-ju** (`veo-3.1-generate-preview`, `-fast-`, `-lite-`): ugašeni 2026-10-22. Veo 3 (`veo-3.0-*`): zastareo. Migracija: Gemini Omni Flash ili GA Veo 3.1 na Vertex-u. (2026-10, ai.google.dev)
- **`gemini-2.5-flash-image`:** ugašen 2026-10-02, zamena Nano Banana 2 Lite. (2026-10, ai.google.dev)
- **Filmic** (Blender): zastareo, zamenjen AgX-om (a za proizvode postoji Khronos PBR Neutral). (2026-10, Blender Manual)
- **Blender 4.2 LTS:** podrška istekla jula 2026. (2026-10, blender.org)
- **Luma Ray 2 / `ray-flash-2`** (stariji API na docs.lumalabs.ai): zamenjen Ray 3.2 na docs.agents.lumalabs.ai. (2026-10, docs.lumalabs.ai)
