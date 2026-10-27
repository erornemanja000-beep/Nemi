# AI alati za slike i video

Poslednja provera: 2026-10-27
Vodi: `trend-skaut`. Prvo punjenje baze. Čita `prompt-slike`, `prompt-video`, `mediji`.

## Kako čitati

- **Izvor:** zvanična dokumentacija, cenovnik, uslovi ili blog proizvođača. Influenseri nisu korišćeni. Blog proizvođača je zvaničan izvor za specifikaciju, ali je reklama za kvalitet; tvrdnje o kvalitetu nisu dokaz.
- **NEPROVERENO** = postoji samo u reklami, kod trećeg provajdera, u sažetku pretrage ili nisam mogao da pročitam zvaničnu stranicu.
- **Hrana, enterijer, proizvodi:** nijedan zvanični izvor koji sam čitao ne tvrdi da je alat najbolji za fotorealističnu hranu, enterijer ili proizvod. „Najbolji za hranu" je zato **NEPROVERENO** za svaki alat. Izbor se mora testirati našim kadrovima (vidi odeljak 6).
- Svi iznosi su u USD bez PDV-a ako nije drugačije navedeno. Cene se menjaju; pre plaćanja koristiti Artlist-ov izračun cene (`get_generation_cost`), kako propisuje `studio/rekreacija-reel/prompt.md`.
- Čitao sam 2026-10-27. Mnoge stranice nemaju datum; tamo piše „bez datuma".

## 1. Pregled (video)

| Alat | Trajanje | Rezolucija | Početni + završni kadar | 9:16 | Cena | Status izvora |
|---|---|---|---|---|---|---|
| **Gemini Omni 1.1 Flash** (Google) | nije navedeno za tekst-u-video; produžetak 3–10 s do ukupno 40 s | 360p, 720p (izvorno), 1080p i 4K (**uvećano**) | DA (dve slike u `input`) | DA | ~$0,10/s na 720p | zvanično (ai.google.dev) |
| **FLUX 3 Video** (Black Forest Labs, preview) | 5–20 s (v2v 5–15 s), 24 fps | `hd` (podrazumevano), `fhd`, `qhd`, `uhd` do 3840×2176 | DA, do 10 kadrova | DA | krediti, 1 kredit = $0,01; iznosi nisu čitljivi | zvanično (docs.bfl.ml) |
| **Luma Ray 3.2** | API: 5 ili 10 s; objava: do 20 s | API: 540p, 720p, 1080p; HDR/EXR na 720p i 1080p | DA (`start_frame`, `end_frame`), do 64 kadra | DA | iznosi nisu čitljivi | zvanično (docs.agents.lumalabs.ai, lumalabs.ai) |
| **MiniMax H3** | 4–15 s, 24 fps | 768P ili 2K | DA (`first_frame`, `last_frame`) | prema ulaznoj slici | pay-as-you-go, iznosi nisu čitljivi | zvanično (platform.minimax.io) |
| **Kling 4.0** | 3–30 s | 720p, 1080p, 4K; 10-bit HDR na 1080p/4K | DA, do 10 ključnih kadrova | ne navodi se | po planu/kreditima | blog proizvođača, najava „u oktobru" |
| **Seedance 2.5** (ByteDance) | tvrdnje: 30 s (Artlist) ili 4–30 s (treći provajderi) | tvrdnje: 480p/720p (treći provajderi) | tvrdnje: DA | ne navodi se | nije čitljivo | **NEPROVERENO** (zvanična stranica nije čitljiva) |
| **Runway Gen-4.5** | nije čitljivo | nije čitljivo | nije čitljivo | nije čitljivo | $0,12/s (API) | delimično (docs.dev.runwayml.com) |

Slike: vidi odeljak 3.

## 2. Platforma: Artlist (naš glavni put)

- **Šta je:** pretplata na slike, video, glas i muziku; „100+ modela" (nazivi se vide u izboru: Veo, Nano Banana, Kling, Seedance, ElevenLabs, GPT Image, Lyria). Sve modele pokreće treća strana, ne Artlist. (2026-10, artlist.io/pricing)
- **Planovi za AI (bez PDV-a, izvor bez datuma):** (2026-10, artlist.io/pricing)

| Plan | Mesečno | Godišnje (po mesecu) | Krediti/mesec | Slike | Video |
|---|---|---|---|---|---|
| AI Starter | $19,99 | $11,99 | 16.500 | do 1.650 | do 103 |
| AI Core | $39,99 | $23,99 | 40.000 | do 4.000 | do 250 |
| AI Creator | $69,99 | $41,67 | 80.000 | do 8.000 | do 500 |
| Custom Business | kontakt | kontakt | po dogovoru | | |

  „Do" brojeva zavisi od modela. Core i Creator imaju „unlimited generations on select models". Godišnje plaćanje označeno kao „Save 40%".
- **Modeli za video na Artlist-u** (specifikacije kako ih Artlist navodi; to nije potvrda proizvođača). (2026-10, artlist.io/ai/video-generator)
  - Seedance 2.5: 30 s u jednom prolazu, uskladjen zvuk.
  - Kling 4.0: 30 s, 1080p, početni i završni kadar plus do 8 srednjih, stereo. (Kling blog potvrđuje do 10 ključnih kadrova, što odgovara.)
  - Gemini Omni 1.1 Flash: do 4K, kontrola prvog i poslednjeg kadra.
  - Wan 3.0: 30 s, do 1080p, zvuk. Luma Ray 3.2: 20 s, 1080p HDR, do 16 ključnih kadrova. MiniMax H3: 5–15 s, do 2K, stereo zvuk (**kod H3 Artlist ne navodi početni/završni kadar, a MiniMax dokumentacija navodi**; proveriti da li Artlist-ov izbornik nudi oba).
  - Veo 3.1 (do 8 s za Lite), Kling 3.0 (3–15 s), Hailuo 2.3 varijante, Grok Video 1.5 (15 s), LTX 2.5, Flux 3 (20 s), HappyHorse 1.0/1.1, Seedance 2.0 varijante.
- **Krediti po modelu:** članci centra za pomoć vraćaju 403 mom alatu. Iz sažetka pretrage, **NEPROVERENO**: Veo 3.1 250 kredita/s (720p/1080p bez zvuka), Hailuo 2.3 100 kredita/s (768p); Artlist je objavio smanjenje troška do 80 % na 46 varijanti (datum nisam pročitao), pa su ti brojevi možda zastareli. (2026-10, pretraga help.artlist.io i artlist.io/blog/artlist-credits-reduction)
- **Komercijalna upotreba (uslovi korišćenja Artlist-a, „Last update: October 14, 2026"):** (2026-10, artlist.io/help-center/privacy-terms/terms-of-use)
  - „Artlist does not claim ownership of Output" i „does not restrict your commercial use of such Output", uz poštovanje uslova i licence (odeljak 14.9.2).
  - AI sadržaj koji se daje kao Asset (npr. iz kataloga) podleže licenci; posle prestanka pretplate prava ističu osim kako licenca dozvoljava (4.2, 14.8).
  - Servis „nije usluga čuvanja"; Artlist može da obriše ulaze i izlaze u bilo kom trenutku; korisnik sam čuva kopije (14.13).
  - Izlaz „may not be protectable under intellectual property laws in all jurisdictions", Artlist ne garantuje originalnost ni da ne krši prava (14.10); „may not be unique" (14.16).
  - Korisnik je sam odgovoran za ulaz i upotrebu izlaza (14.5); opšta obaveza obeštećenja Artlist-a (odeljak 12).
  - Pravila o deepfake-u i maloletnicima upućuju na „Forbidden Uses" koje tekst nije sadržao: nisam ih pročitao (**NEPROVERENO**).
  - Besplatne probne generacije nisu licencirane za projekte i pravila o izlazu iz video-u-video zavisi od prava na izvorni snimak (sažetak pretrage artlist.io, **NEPROVERENO** u tekstu uslova). Custom Business plan: „Custom business license" i „Legal indemnification" (cenovnik).
  - Marketing Artlist-a: „cleared the moment you download it" je reklama, ne uslov. (2026-08, artlist.io/blog/best-ai-video-generator-with-commercial-licensing-in-2026)
- **Pravilo za nas:** svaki odobren izlaz odmah preuzeti i zapisati model, prompt, datum i plan u `studio/<projekat>/promptovi/`. Klijentske fotografije slati modelima tek posle provere uslova (vidi odeljak 5).
- **Šta Artlist loše radi:** ne tvrdim ništa; zvanično ne objavljuje ograničenja. Specifikacije su preuzete od proizvođača i mogu da kasne.

## 3. Alati po pojedinačno

### 3.1 Google Gemini Omni 1.1 Flash (zamena za Veo 3.1 u Gemini API-ju)
- **Važno:** „The Veo 3.1 Preview in the Gemini API has been shut down." Datum gašenja **2026-10-22**; prelaz na Gemini Omni Flash ili GA Veo modele na „Gemini Enterprise Agent Platform". Svaka skripta sa `veo-3.1-*-preview` nazivima više ne radi. (2026-10, ai.google.dev/gemini-api/docs/video, ažurirano 2026-10-22)
- **Model:** `gemini-omni-1.1-flash`; „fast, multimodal model for video generation and conversational video editing"; ulazi tekst, slike, audio, video. (2026-10, ai.google.dev/gemini-api/docs/omni)
- **Trajanje:** za tekst-u-video nije navedeno; produžetak „3–10 second continuation", ukupno do 40 s; uploadovani snimci za izmenu/produžetak do 10 s.
- **Rezolucija i format:** 360p, 720p (podrazumevano), „1080p output (upscaled)", „4K output (upscaled)"; 9:16 i 16:9 (podrazumevano 16:9). To znači da je izvorni izlaz 720p.
- **Početni i završni kadar:** DA, dve slike u `input` listi, prelaz se opisuje u promptu. Prema sažetku pretrage zvaničnog vodiča preporučuju se oznake `<FIRST_FRAME>` i `<LAST_FRAME>` (druga se koristi samo uz prvu): **NEPROVERENO** u mom čitanju, proveriti pri prvom korišćenju.
- **Reference:** više slika za subjekat (maksimum nije naveden); do 3 video klipa po 3 s.
- **Cena:** `gemini-omni-1.1-flash` $0,10/s na 720p (Standard), $17,50 po 1 M izlaznih tokena, 5.792 tokena po sekundi. Cene za 1080p/4K nisu navedene. (2026-10, ai.google.dev/gemini-api/docs/pricing, ažurirano 2026-10-26)
- **Komercijalna upotreba:** Gemini API Additional Terms (izmenjeno 2026-04-28, na snazi od 2026-03-23): „Google won't claim ownership over that content"; zabranjeno je koristiti usluge za razvoj konkurentskih modela; važi Prohibited Use Policy. Obeštećenje u pročitanom tekstu nije pomenuto: **NEPROVERENO**. Svi video snimci imaju nevidljiv **SynthID** vodeni žig. (2026-04, ai.google.dev/gemini-api/terms)
- **Zvanični saveti za promptove:** „In a single continuous shot" i „No scene cuts"; negativi u samom tekstu („No dialogue"), jer parametar za negativni prompt nije podržan; za izmene „Keep everything else the same"; vreme prirodnim jezikom („After 3 seconds") ili `[0-3s]`; tačan tekst koji treba da se vidi na ekranu napisati u promptu; tražiti detalje i konkretne pozadine. Zvuk se generiše sam; može se tražiti u promptu (npr. mirna muzika). Početna slika je „prvi kadar filma", mora biti oštra i dobro komponovana (Google Cloud vodič, sažetak pretrage). (2026-10, ai.google.dev/gemini-api/docs/omni)
- **Šta radi loše / ograničenja (zvanično):**
  - U EEA, Švajcarskoj i UK **izmena i produžetak uploadovanih snimaka nije dostupni**; slike maloletnika se ne mogu uploadovati; određene prepoznatljive osobe nisu podržane. Austrija je u EEA: za nas važi.
  - Produžetak samo dodaje na kraj (ne na početak ni u sredinu); nema uploada audio reference; „Voice editing is not supported"; nema „provisioned throughput".
  - „English (EN) is fully supported", ostali jezici nisu ocenjeni. Više videa u jednom promptu može da pokvari rezultat.
  - Rezolucije 1080p i 4K su uvećane, ne izvorne.

### 3.2 FLUX 3 Video i FLUX 3 Image (Black Forest Labs)
- **Status:** FLUX 3 Video je „preview", bez datuma izdanja. (2026-10, docs.bfl.ml/flux_3/flux3_overview.md)
- **Video:** režimi `t2v`, `i2v`, `v2v`; 5–20 s (v2v 5–15 s); 24 fps; rezolucije `hd` (podrazumevano), `fhd`, `qhd`, `uhd` do 3840×2176 za 16:9; omjeri 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, **9:16**, 9:21.
- **Početni i završni kadar:** DA kroz `i2v`: jedna slika = početni kadar, dve = početni i završni, do deset slika za storyboard; parovi `[sekunde, slika]` vezuju sliku za tačan trenutak; reference 1–10. Sinhronizovan zvuk (govor, lipsync, efekti, ambijent), `generate_audio` je podrazumevano uključen. „Draft" režim košta oko trećine pune renderovanja.
- **Slike (FLUX 3 Image):** do 10 referentnih slika, izlaz do 4K. Rezolucije u cenovniku: `768sq`, `1k`, `1.5k`, `2k`, `4k`. (2026-10, docs.bfl.ml/flux_3/flux3_image_overview.md i quick_start/pricing.md)
- **Cena:** krediti, „1 credit = $0.01 USD"; tabele sa iznosima nisu se učitale mom alatu: **NEPROVERENO** (https://bfl.ai/pricing). (2026-10, docs.bfl.ml/quick_start/pricing.md)
- **Komercijalna upotreba (uslovi, „Last Revised on August 1, 2026"):** „We claim no ownership rights" nad vašim sadržajem, uključujući izlaze (1.2a); komercijalna upotreba izlaza je dozvoljena kako uslovi navode (1.3e); zabranjeno je predstavljati AI sliku kao stvarnu fotografiju stvarnog događaja (1.3m) i trenirati druge modele na izlazu (1.3n). **BFL dobija široku, trajnu licencu na vaš ulaz, izlaz i zadatke radi razvoja proizvoda; odjava preko legal@blackforestlabs.ai** (1.2e). Posebni uslovi za API (Developer ToS, FLUX API Service Terms) nisu pročitani: **NEPROVERENO**. (2026-08, bfl.ai/legal/terms-of-service)
- **Zvanični saveti:** video-prompt ima pet elemenata: subjekat i radnja; kamera (static, push-in, handheld follow, overhead drift, rapid pan); scena i atmosfera; kvalitet pokreta (slow, abrupt, weightless, cinematic…); ograničenja kontinuiteta („što mora ostati isto"). Za početni+završni kadar: oba kadra neka budu povezana (isti subjekat, scena, kamera); „The wider the gap between start and end, the more freedom (and unpredictability) you hand the model"; redosled ključnih kadrova je vremenska linija; zahtevi sa 3+ kadra ili vremenskim oznakama traže izričit `duration`. Slike: subjekat, okruženje, stil, svetlo, kompozicija; ulazne slike zvati „image 1", „image 2"; opis stranice „Technical Parameters" pominje rad „bez negativnih promptova" (samu stranicu nisam čitao): **NEPROVERENO** da li negativni prompt radi, pa naši „Avoid:" nizovi možda nemaju efekta. (2026-10, docs.bfl.ml/guides)
- **Šta radi loše (zvanično):** veliki razmak između početnog i završnog kadra daje nepredvidiv rezultat; rezultat se čuva samo oko 2 sata („Result URLs are signed and expire about 2 hours after the job finishes"): preuzeti odmah; objavljen je samo `t2v`, `i2v`, `v2v`. Ostala ograničenja dokumentacija ne navodi.

### 3.3 Luma Ray 3.2
- **Izdanje:** 2026-06-09, prvi put kao API. Objava: „up to 20 seconds long at 1080p", „native HDR Generation and 16-bit EXR Export", „up to 16 keyframes within a single clip". (2026-06, lumalabs.ai/news/introducing-ray-3-2)
- **API dokumentacija (razlikuje se od objave):** trajanja **5 s i 10 s**; 540p, 720p, 1080p; omjeri **9:16**, 3:4, 1:1, 4:3, 16:9, 21:9; `video.start_frame` i `video.end_frame`; ključni kadrovi do **64** (`video.keyframes` + `video.keyframe_indexes`); HDR na 720p i 1080p, EXR izvoz (AP0/ACES2065-1) traži `hdr: true`; izlaz MP4, preuzimanje u roku od 1 h (presigned URL). Razlike (20 s/16 kadrova u objavi, 10 s/64 kadra u API-ju) nisam razrešio; za planiranje važi API dokumentacija. (2026-10, docs.agents.lumalabs.ai/guides/model)
- **Cena:** „Per-video rates are on the Pricing page", iznosi nisu čitljivi: **NEPROVERENO**.
- **Komercijalna upotreba (uslovi, ažurirano 2026-05-14):** „Customer owns and retains all right, title, and interest in and to the Output" (4.9.1); **komercijalno samo ako je izlaz napravljen tokom aktivne pretplate**; probni izlaz samo za internu procenu; Luma može da ugradi vodene žigove i zabranjeno je da se skidaju; zabrana deepfake-a; izlaz koji liči na osobu mora se javno označiti kao AI (4.8). **Luma dobija licencu da obrađuje izlaz i da trenira svoje AI modele** (za izlaz tokom aktivne pretplate: hostovanje, poboljšanje usluge i treniranje; za izlaz van aktivne pretplate: šira licenca, uključujući javno prikazivanje i izvedena dela). (2026-05, lumalabs.ai/legal/tos)
- **Zvanični saveti za promptove:** dokumentacija ne daje; jedini primer: „slow dolly shot through a misty greenhouse at sunrise".
- **Šta radi loše / ograničenja:** `loop` radi samo za `type: "video"` (kreiranje); video reframing podržava samo standardni dinamički opseg i odbija `start_frame`, `end_frame`, `loop`; audio se ne pominje. (2026-10, docs.agents.lumalabs.ai)
- **Prednost:** HDR/EXR za kolor korekciju u DaVinci/CapCut radnom toku (zvanična specifikacija).

### 3.4 MiniMax H3 (studio je ranije koristio MiniMax)
- **Modeli:** MiniMax-H3 („Next-gen open general-purpose multimodal video model"), 768P ili 2K, 4–15 s (celi brojevi), 24 fps; MiniMax-H3-Max (480P ili 768P, 5–15 s; dokumentacija kaže da ga je fal.ai naknadno obučio na H3). **Stariji (legacy): Hailuo 2.3, 2.3 Fast, 02.** (2026-10, platform.minimax.io/docs/guides/models-intro)
- **Početni i završni kadar:** DA, image-to-video prima 0, 1 ili 2 slike sa ulogama `first_frame` i `last_frame`; dimenzije obe slike 256–5760 px, odnos stranica 2:5 do 5:2. Za image-to-video odnos se uzima iz slike (adaptivno); za tekst-u-video `ratio` je obavezan. Reference: do 9 slika, 3 video klipa (do 15 s ukupno), 3 audio klipa (do 15 s ukupno), ukupno do 12 fajlova. Prompt do 7.000 znakova. 2K se dobija regeneracijom iz 768P polaznog videa. Obrada je asinhrona, proveravati na 10 s. (2026-10, platform.minimax.io/docs/guides/video-generation)
- **Cena:** „Pay-as-you-go API"; iznosi nisu na pročitanim stranicama: **NEPROVERENO**. Preko Artlist-a krediti (vidi odeljak 2).
- **Komercijalna upotreba:** pročitane stranice ne govore ništa: **NEPROVERENO**. Preko Artlist-a važi Artlist licenca.
- **Zvanični saveti:** za tekst-u-video, dodati komande kamere u uglastim zagradama, npr. `[pan]`, `[zoom]`, `[static]`, odmah posle ključnih opisa. Naš `video/prompt_radnja1.md` već ima verziju sa komandama kamere.
- **Ograničenja (zvanična):** gore navedene dimenzije, veličine (video 50 MB, slika 30 MB, audio 15 MB, telo zahteva 64 MB). Dokumentacija ne navodi slabosti modela.
- **Za studio:** ako su raniji klipovi (ruža, latica) rađeni u Hailuo 02 ili 2.3, nov model sa istim kadrovima je H3; proveriti u Artlist-u da li nudi i početni i završni kadar.

### 3.5 Kling 3.0 / 4.0 (studio koristi Kling za višekadarske klipove i O3 edit)
- **Izvor:** blog Kling-a (proizvođač), 2026-09-30, uporedna tabela. Najava: „The all-new Kling 4.0 will officially launch in October"; Kling 4.0 Flash ima ograničen rani pristup od 2026-09-28; stranica sama sebe protivreči o dostupnosti. Na Artlist-u je Kling 4.0 već izlistan (2026-10-27). (2026-09, kling.ai/blog/kling-4-vs-3)

| | Kling 3.0 | Kling 4.0 |
|---|---|---|
| Trajanje | 3–15 s | 3–30 s u jednom prolazu |
| Rezolucija | 720p/1080p/4K, 8-bit SDR | 720p/1080p/4K, 10-bit HDR na 1080p/4K |
| Zvuk | jedan kanal | stereo |
| Početni i završni kadar | DA | DA, do 10 ključnih kadrova |
| Reference | 7 slika; 1 video do 15 s | do 10 slika i 7 subjekata; do 5 videa, 30 s ukupno |
| Prompt | | do 8.000 tokena |

- **Cena:** Kling 3.0 u 4K: 30 kredita po sekundi (blog 2026-07-28). Planovi (prva pretplata): Basic $0, Standard $6,99 (660 kredita), Pro $25,99 (3.000), Premier $64,99 (8.000), Ultra $127,99 (26.000); obnova viša ($8,80 / $32,56 / $80,96 / $159,99). Cene za 720p/1080p i za 4.0 nisu navedene. (2026-07, kling.ai/blog/kling-video-3-0-credit-cost-guide)
- **Komercijalna upotreba direktno kod Kling-a:** nisam pročitao: **NEPROVERENO**. Preko Artlist-a važi Artlist licenca.
- **Zvanični saveti:** nisam pročitao zvanični vodič za promptove. Naši testirani promptovi su u `video/prompt_sorten.md` i `video/prompt_gradnja_multishot.md`.
- **Slabosti:** blog ne navodi ograničenja. Tvrdnje o „stable motion", „clearer text" i „narrative continuity" su reklama (**NEPROVERENO**).

### 3.6 Seedance 2.5 (ByteDance / BytePlus ModelArk)
- Zvanične stranice postoje (tutorial i prompt guide, tutorial ažuriran 2026-10-20) na `docs.byteplus.com/en/docs/ModelArk/2607688` i `.../seedance-2-5-prompt-guide`, ali moj alat vraća samo navigaciju bez teksta. **Sve ispod je NEPROVERENO.** (2026-10, docs.byteplus.com)
  - Artlist: 30 s u jednom prolazu, uskladjen zvuk, dijalog, muzika, efekti.
  - Treći provajderi (Sogni, Runware, Vercel, Cloudflare): 4–30 s, 24 fps, 480p/720p, režim prvi+poslednji kadar. Jedan provajder (Muapi) tvrdi 16 s i 4K; drugi navodi da BytePlus tabela ne navodi 4K.
- Preporuka: neko ko može da otvori BytePlus stranicu u browseru neka prepiše trajanje, rezoluciju, kadrove i uslove u ovaj fajl.

### 3.7 Runway (nepotpuno)
- Zvanična lista modela za API: Gen-4.5 (`gen4.5`, izdat 2026-02-10, $0,12/s), Gen-4 Turbo (`gen4_turbo`, 2025-04-04, $0,05/s), Aleph 2.0 (`aleph2`, 2026-06-02, $0,28/s, video-u-video sa „keyframe-guided control"), Act-Two ($0,05/s). Trajanja, rezolucije, početni/završni kadar i uslovi nisu na pročitanoj stranici: **NEPROVERENO**. Runway nije na Artlist-ovoj listi. Nije preporuka dok se ne pročita. (2026-10, docs.dev.runwayml.com/guides/models)

## 4. Slike (fotorealistična hrana, enterijer, proizvod)

### 4.1 Nano Banana (Google Gemini modeli za slike)
- **Modeli:** Nano Banana 2.1 (`gemini-nano-banana-2.1`, „primary high-efficiency workhorse"), Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`, najbrži i najjeftiniji, samo 1K), Nano Banana 2 (`gemini-3.1-flash-image`, prethodna generacija), Nano Banana Pro (`gemini-3-pro-image`, „premium choice for the most complex visual tasks"). Nano Banana (`gemini-2.5-flash-image`) je zastareo i gasi se 2026-10-02 (već isteklo). (2026-10, ai.google.dev/gemini-api/docs/image-generation i /pricing, ažurirano 2026-10-26)
- **Rezolucija:** 1K, 2K, 4K (veliko slovo K obavezno); 0,5K samo na Gemini 3.1 Flash Image. Odnosi uključuju 9:16 (potvrđeno za Lite, za 2.1 samo posredno). Do 14 referentnih slika ukupno (mapiranje po modelu izvedeno iz spljoštene tabele: proveriti).
- **Cena po slici (Standard):** 2.1: $0,0336 (1K), $0,0504 (2K), $0,113 (4K). 3.1 Flash Image: $0,067 (1K), $0,101 (2K), $0,151 (4K). Pro: $0,134 (1K/2K), $0,24 (4K). Batch otprilike pola cene.
- **Komercijalna upotreba:** Gemini API Additional Terms (vidi 3.1). Sve slike nose **SynthID** žig.
- **Zvanični saveti:** fotorealizam: „A photorealistic [vrsta kadra] of [subjekat] in [okruženje]", opisati svetlo, pa „[ugao kamere]" i „[tip objektiva]"; „The more specific you are, the more control you have". Proizvod: „A high-resolution, studio-lit product photograph of a [proizvod] on a [podloga]", „[osvetljenje, npr. three-point softbox]", ugao, „Ultra-realistic, with sharp focus on [detalj]", pa odnos stranica. Za tekst: napisati tačan tekst i opisati font („legible, stylized text for … menus"). Ostaviti prazan prostor za tekst. Za profesionalni rad vodič preporučuje Pro. Odeljak o hrani u pročitanom delu ne postoji. (2026-10, ai.google.dev/gemini-api/docs/image-generation)
- **Slabosti (zvanično):** Lite nije optimizovan za više referenci ni za višekratno uređivanje; razmišljanje (thinking) se uvek naplaćuje i ne može se isključiti na Gemini 3 modelima.

### 4.2 FLUX 3 Image i FLUX.2 (Black Forest Labs)
- Vidi 3.2. Do 10 referentnih slika, izlaz do 4K, ugrađen „grounding" (podrazumevano uključen). FLUX.2 „remains fully supported". Klein varijanta ima otvorene težine. Cene i API uslovi: **NEPROVERENO** (nisu čitljivi). (2026-10, docs.bfl.ml)

### 4.3 Nije pokriveno
GPT Image (na Artlist listi, bez čitanja zvanične dokumentacije), Midjourney, Seedream, Wan 3.0, Grok Video 1.5, LTX 2.5, HappyHorse: nisu čitani. Navedeni samo kao postoje na Artlist-u. (2026-10, artlist.io/ai/video-generator)

## 5. Pravila za nas (zaključci agenta)

1. **Klijentske fotografije i planovi:** Luma i BFL traže široku licencu na ulaz/izlaz i dozvoljavaju treniranje (BFL uz odjavu mejlom, Luma za plaćene planove kako uslovi navode). Pre slanja fotografija DON'S-a, Freiraum-a i sličnih: pitati klijenta ili proći kroz Artlist (čije uslove sam čitao samo delimično) i zabeležiti odluku. Proverava `bezbednost`.
2. **EEA ograničenje (Omni):** nema izmene ni produžetka uploadovanih snimaka u Austriji; slike sa maloletnicima ne.
3. **Označavanje AI sadržaja:** Google stavlja SynthID, Luma može da stavi vodeni žig i traži javno označavanje osoba. Obaveze označavanja u EU i Austriji nisam proveravao; to pripada `trziste`.
4. **Preuzimanje odmah:** BFL izlaz traje oko 2 sata, Luma 1 sat, Artlist može da briše. Preuzeti i arhivirati.
5. **Negativni prompt:** Omni ga ne podržava kao parametar (samo u tekstu), BFL vodič ga zaobilazi. Naši „Avoid:" nizovi u `video/prompt_*.md` verovatno rade samo kao tekst; u prvom testu proveriti da li smanjuju greške.
6. **Početni+završni kadar i kontinuitet:** potvrđeno u zvaničnim izvorima za Omni, FLUX 3, Luma, MiniMax H3, Kling. Zajednički savet: oba kadra neka dele subjekat, scenu i kameru; veliki razmak daje nepredvidiv rezultat (BFL).
7. **Izvorna rezolucija izlaza:** Omni 720p je izvorni (1080p/4K su uvećani); Luma 1080p; Kling 4.0 do 4K; FLUX 3 do 3840×2176.

## 6. Predlog testa (jer nema dokaza za hranu/enterijer/proizvod)

Zaključak agenta, nije izvor. Pre nego što se izabere jedan alat za projekat, ista 4 kadra sa postojećih `frames/` (kugla sladoleda, vitrina, izlog, lokal) i isti prompt kroz 3 alata (Kling 4.0 ili 3.0 preko Artlist-a, MiniMax H3, Omni 1.1 Flash ili FLUX 3 Video). Oceniti: tekstura sladoleda, odsjaj, tačnost slova na tabli, prava linija izloga, pomeranje kamere, da li se završni kadar poklapa sa slikom. Za slike isto: Nano Banana 2.1 i Pro naspram FLUX 3 Image. Kad Artlist-ova cena bude poznata (`get_generation_cost`), proceniti trošak po upotrebljivom kadru.

## Spisak NEPROVERENO (ukratko)

- Seedance 2.5: sve specifikacije (zvanična stranica nečitljiva).
- Kling 4.0: pun datum izlaska, cene, uslovi; reklamni opisi kvaliteta.
- Runway: trajanja, rezolucije, kadrovi, uslovi.
- FLUX 3: iznosi cena, API uslovi, da li negativni prompt radi.
- Luma: iznosi cena; razlika objava/API (20 s/16 kadrova prema 10 s/64).
- MiniMax: iznosi cena, uslovi komercijalne upotrebe.
- Artlist: krediti po modelu, „Forbidden Uses", pravila za probne generacije; da li izbornik za H3 nudi oba kadra.
- Omni: oznake `<FIRST_FRAME>`/`<LAST_FRAME>`, obeštećenje, cene 1080p/4K.
- Nijedan alat: tvrdnja da je „najbolji za hranu/enterijer/proizvod".

## Arhiva

- Veo 3.1 Preview u Gemini API-ju (`veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-lite-generate-preview`): ugašen 2026-10-22. (2026-10, ai.google.dev/gemini-api/docs/video)
- Nano Banana (`gemini-2.5-flash-image`): zastareo, gašenje 2026-10-02. (2026-10, ai.google.dev/gemini-api/docs/pricing)
