# clipper: bezbednosni pregled alata

Pregled: `bezbednost`, 23. 11. 2026. Ništa nije instalirano ni pokrenuto. Paketi su preuzeti samo kao podaci,
da bi se pročitao kod i proverili heševi. Korisnik radi na Mac-u (Apple Silicon), a rezervna mašina je
iznajmljeni Linux server.

## Presude

| Alat | Presuda | Verzija (izlazak) | Licenca | Telemetrija |
|---|---|---|---|---|
| yt-dlp (PyPI, u venv-u) | **uz uslove** | 2026.10.26 (26. 10. 2026) | Unlicense | nema |
| yt-dlp samostalni binarni fajl | ne koristiti (PyPI je bolji izbor) | isto | GPLv3+ (paket u celini) | nema |
| faster-whisper (i na Mac-u) | **uz uslove**, preporuka za transkript | 1.2.1 (31. 10. 2025) | MIT | HF Hub, isključuje se |
| whisper.cpp (Homebrew, Metal) | **uz uslove**, samo kao rezerva | 1.9.5 (6. 10. 2026) | MIT | nema |
| mlx-whisper | **odbijeno** za sada | 0.4.3 (29. 8. 2025) | MIT | HF Hub |
| openai-whisper | **odbijeno** (ne treba nam) | 20250625 (26. 6. 2025) | MIT | nema |
| streamlink (PyPI, u venv-u) | **uz uslove** | 8.6.3 (29. 10. 2026) | BSD-2-Clause | nema |
| Twitch chat: IRC preko socket-a | **uz uslove** | bez paketa | – | – |
| YouTube chat: Data API v3 | **uz uslove**, preporuka | REST API | – | Google vidi pozive |
| chat-downloader | **odbijeno** | 0.2.8 (3. 9. 2023) | MIT | nema |
| Homebrew | **uz uslove** (analitika isključena) | trenutna | BSD-2-Clause | da, isključuje se |
| `brew install ffmpeg-full` | **uz uslove** | 9.1 | GPL-3.0+ | nema |
| `brew install ffmpeg` (obični) | **odbijeno za clipper**: nema libass | 9.1 | GPL-3.0+ | nema |
| `brew install python@3.14` | **odobreno** | 3.14.10 | PSF | nema |
| yt-dlp / streamlink preko brew-a | ne, nego pip u venv-u (brew samo kao rezerva) | 2026.10.26 / 8.6.3 | – | – |

Ukupno: **SAMO UZ OVE USLOVE.** Za sve zakucane verzije OSV.dev 23. 11. 2026 ne prijavljuje poznate
ranjivosti. Sve su starije od dve nedelje.

## Zajednički uslovi (važe za sve alate)

1. **Jedan venv** `clipper/.venv` na Python-u 3.14 iz Homebrew-a. Instalira se samo iz zaključanih lista u
   Prilogu, sa `--require-hashes --only-binary=:all:`. Sva tri alata mogu u isti venv (provereno dry-run-om).
   Nikad `pip install -U`, `--pre`, nightly ni master kanal.
2. **Nadogradnja** ide samo preko `bezbednost`-a: nova lista heševa i pravilo dve nedelje. Jedini izuzetak je
   yt-dlp kad YouTube prestane da radi. I tada se uzima stabilno izdanje, uz brz pregled. Sam README za yt-dlp
   kaže da je `stable` „often stale and prone to external breakage” (README, deo UPDATE, tag 2026.10.26).
3. **Promenljive okruženja** (u `clipper/.venv/bin/activate` ili `~/.zprofile`):
   `HF_HUB_DISABLE_TELEMETRY=1`, `HF_HUB_DISABLE_IMPLICIT_TOKEN=1`, `HF_HUB_DISABLE_UPDATE_CHECK=1`,
   `DO_NOT_TRACK=1`, `PIP_DISABLE_PIP_VERSION_CHECK=1`, `HOMEBREW_NO_ANALYTICS=1`, `HOMEBREW_NO_AUTO_UPDATE=1`.
   Posle preuzimanja modela dodaje se i `HF_HUB_OFFLINE=1`.
4. **Bez naloga i kolačića.** Ne koriste se `--cookies-from-browser`, `--cookies`, `--username`/`--password`,
   `--netrc*` ni `--twitch-api-header "Authorization=OAuth …"`. Kolačić ili token iz browsera daje pun pristup
   nalogu. Oba alata su već imala propuste sa curenjem kolačića (yt-dlp CVE-2023-35934 i CVE-2026-50019).
5. **Lični podaci (DSGVO, CLAUDE.md pravilo 7).** Iz chata se čuvaju samo vreme i broj poruka, bez korisničkih
   imena. Tekst poruka se čuva samo kratko, ako je potreban za ključne reči.
6. **Git.** Sve što ne ide u git treba dodati u `clipper/.gitignore`: `.venv/`, `modeli/`, `snimci/`, `chat/`
   (sada su tu samo `ulaz/`, `izlaz/`, `*.part`). Model ima 1,6 do 3 GB, a chat sadrži lične podatke.

## 1. yt-dlp

**PyPI ili binarni fajl.** Uzimamo PyPI wheel u venv-u:
- wheel ima samo kod pod Unlicense licencom. PyInstaller binarni fajlovi sadrže i GPLv3+ kod
  (README, „Licensing”);
- wheel ima PyPI attestaciju: napravio ga je `yt-dlp/yt-dlp`, `release.yml` (PyPI Integrity API, 23. 11. 2026);
- samonadogradnja je u wheel-u isključena: `yt_dlp/version.py:7-9` sadrži `VARIANT = 'pip'` i
  `UPDATE_HINT = 'You installed yt-dlp with pip …; Use that to update'`, pa `-U` samo ispiše poruku;
- sve zavisnosti su zakucane pomoću dodataka `[default,pin]` iz samog paketa.

Binarni fajl (`yt-dlp_macos`) sadrži sopstveni Python i zavisnosti, a nadograđuje se samo kad se pokrene
`-U` ili `--update-to`. Nadogradnja proverava SHA-256 iz `SHA2-256SUMS` istog izdanja (`yt_dlp/update.py:459, 531`),
ali ne proverava GPG potpis. GPG provera je ručna (README, „Release Files”). Uz `--update-to drugi/repo` README
upozorava: „there is no verification done for binaries from different repositories”.

**Šta šalje spolja.** U kodu nisam našao telemetriju. Zahtevi idu ka sajtu, a izuzeci su:
- `-U` šalje zahtev ka `api.github.com`;
- `--remote-components ejs:github|ejs:npm` preuzima JS sa GitHub-a ili npm-a. To je podrazumevano isključeno
  i ne treba, jer je `yt-dlp-ejs` već u listi.

Upozorenje „starije od 90 dana” računa se lokalno.

**Deno.** YouTube traži izvršavanje JS izazova. yt-dlp za to pokreće deno 2.9.8 iz venv-a, bez ikakvih
`--allow-*` dozvola (`--no-prompt --no-remote --no-config`, `yt_dlp/extractor/youtube/jsc/_builtin/deno.py:38-39, 102`).
Deno wheel ima attestaciju od `denoland/deno_pypi`. Sve prijavljene ranjivosti deno-a iz 2026. ispravljene su
pre verzije 2.9.8 (OSV, crates.io).

**CVE i incidenti** (OSV/GHSA, stanje 23. 11. 2026). Ništa ne pogađa verziju 2026.10.26:
- `--exec` ubacivanje komandi: CVE-2023-40581, CVE-2024-22423, GHSA-69qj-pvh9-c5wg (ispravljeno u 2026.6.9);
- opasni nastavci imena fajlova: CVE-2024-38519 i zaobilaženje CVE-2026-50023 (2026.6.9);
- `--netrc-cmd`: CVE-2026-26331 (2026.02.21);
- aria2c sa manifestima: CVE-2026-50574 (2026.6.9);
- `--write-link`: CVE-2026-55404 (2026.7.4);
- curenje kolačića: CVE-2023-35934, CVE-2026-50019.

Lanac snabdevanja: lažni paket **`yt-api-dlp`** (MAL-2026-6754, OSV, 4. 7. 2026). To je kopija yt-dlp-a koja
preuzima i pokreće skriptu. Instalira se samo tačno ime `yt-dlp`, iz liste sa heševima.

**Ne sme se pokretati:** `-U`, `--update`, `--update-to`, `--exec`, `--netrc-cmd`, `--downloader aria2c`,
`--write-link` i ostali `--write-*-link`, `--compat-options allow-unsafe-exec-expansion`,
`--cookies-from-browser`, `--remote-components`, dodaci (`--plugin-dirs`), nightly i master kanal.
yt-dlp sam učitava `yt-dlp.conf` iz trenutnog foldera i dodatke iz podrazumevanih foldera (README, „Configuration”,
„Plugins”). Zato se uvek dodaju `--ignore-config --no-plugin-dirs`.

## 2. Transkript: faster-whisper (preporuka, i na Mac-u)

**Zavisnosti** (zakucane, Prilog B):

| Paket | Verzija | Licenca |
|---|---|---|
| ctranslate2 | 4.8.5 | MIT |
| av (PyAV, nosi sopstveni FFmpeg i x264/x265) | 19.0.2 | BSD-3 |
| tokenizers | 0.23.3 | Apache-2.0 |
| onnxruntime (VAD) | 1.31.1 | MIT |
| huggingface-hub | 2.4.0 | Apache-2.0 |
| hf-xet | 1.8.0 | Apache-2.0 |
| httpx2 i httpcore2 | 2.16.0 | BSD-3 |

`httpx2` nije greška u kucanju. To je Pydantic-ov fork httpx-a, a huggingface-hub ga koristi od verzije 2.0.0
(24. 9. 2026; PyPI metapodaci, httpx2.pydantic.dev, Gentoo i Fedora paketi). faster-whisper nema PyPI
attestaciju, ali je repo aktivan (commit-ovi do 12. 11. 2026, GitHub, provereno 23. 11. 2026).

**Model.** `WhisperModel("turbo")` zove `huggingface_hub.snapshot_download` (`faster_whisper/utils.py:11-31, 49-116`).
Alias `turbo` vodi na `mobiuslabsgmbh/…`, a to danas preusmerava (HTTP 307) na
`dropbox-dash/faster-whisper-large-v3-turbo`, jer je organizacija promenila vlasnika. Zato se ne koristi alias.
Model se preuzima jednom, po tačnom imenu repoa i commit-u, a heš se proveri:

| Model | Repo @ revision | `model.bin` SHA-256 | Veličina |
|---|---|---|---|
| large-v3-turbo (preporuka za Mac) | `dropbox-dash/faster-whisper-large-v3-turbo` @ `0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf` (fajlovi modela od 8. 10. 2024, kasnije menjan samo README) | `e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da` | 1,6 GB |
| large-v3 (bolji kvalitet, sporiji) | `Systran/faster-whisper-large-v3` @ `edaa852ec7e145841d8ffdb056a99866b5f0a478` | `69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1` | 3,1 GB |

`model.bin` je CTranslate2 format, a ne pickle, pa učitavanje ne izvršava kod. VAD model je deo wheel-a
(`faster_whisper/assets/silero_vad_v6.onnx`), pa se ništa ne preuzima.

**Telemetrija.** faster-whisper sam ne šalje ništa. huggingface-hub u User-Agent stavlja verzije, a dok je
telemetrija uključena i verziju torch-a i ime AI agenta koji ga pokreće (`huggingface_hub/utils/_headers.py:183-189`).
To gasi `HF_HUB_DISABLE_TELEMETRY=1` ili `DO_NOT_TRACK=1` (`constants.py:244-248`). Posle preuzimanja
`HF_HUB_OFFLINE=1` blokira svaki poziv.

**Ne sme se pokretati:**
- `hf skills add` ili `hf skills update`: upisuju u `.claude/skills` ili `~/.claude/skills`
  (`huggingface_hub/constants.py:231-234`). To je izmena konfiguracije Claude-a, za koju treba pregled i korisnik.
- `tiny-agents`: pokreće MCP agente koji izvršavaju alate.
- `hf auth login`: model je javan, token ne treba.
- `ct2-*-converter` i `pip install faster-whisper[conversion]`: povlače torch i transformers.

**Mac.** CTranslate2 4.8.5 radi na CPU-u. MPS (Metal) postoji tek od 4.9.0 (10. 11. 2026), kao „experimental”
(CHANGELOG CTranslate2), i mlađi je od dve nedelje. onnxruntime 1.31.1 ima wheel samo za macOS 14+ na arm64,
pa Intel Mac nije pokriven ovom listom.

### Poređenje za Apple Silicon

| | faster-whisper (CPU) | whisper.cpp (Metal) | mlx-whisper (MLX) |
|---|---|---|---|
| Instalacija | pip, venv, heševi | `brew install whisper.cpp` (1.9.5) | pip, uz torch, numba, scipy, tiktoken |
| Vreme po reči | stabilno (`word_timestamps=True`) | README: „Word-level timestamp (experimental)”, `-ml 1` | da (port openai `timing.py`) |
| Brzina | CPU, najsporiji od tri | GPU (Metal), README: „inference runs fully on the GPU via Metal” | GPU |
| Model | HF, zakucan commit, CT2 format | HF `ggerganov/whisper.cpp`, GGML `.bin`, SHA-256 na HF | HF `mlx-community`, `snapshot_download` bez `revision` (`mlx_whisper/load_models.py:18-20`), ceo repo |
| Istorija ranjivosti | nema poznatih (OSV) | učitavač modela: CVE-2026-10298 (≤1.8.2), CVE-2026-110810 (≤1.9.4, ispravljeno u 1.9.5; NVD i Debian tracker) | nema poznatih |
| Ostalo | isti kod na Linux serveru | C++ parser modela je čest izvor grešaka | wheel sadrži tri ugnježdene kopije `build/lib/…`; poslednje izdanje 8/2025; torch je u zavisnostima, a kod ga ne uvozi pri transkripciji |

**Preporuka: faster-whisper.** Žuta reč u titlu zavisi od tačnog vremena svake reči, a tu je faster-whisper
najzreliji. Isti kod radi i na serveru, sve je zakucano, a za isečke od 30 do 75 s Metal nije potreban.

Ako se na Mac-u celi višesatni snimci pokažu prespori (to `tester` meri, nisam merio), uvodi se whisper.cpp iz
Homebrew-a samo za grub prolaz i traženje trenutaka. Model mora imati proveren heš:
`ggerganov/whisper.cpp` @ `5359861c739e955e79d9a303bcbc70fb988958b1`, `ggml-large-v3-turbo.bin`,
SHA-256 `1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69`. Model se preuzima
`hf_hub_download`-om iz venv-a, a ne skriptom `download-ggml-model.sh`. Konačne reči za klip i tada daje
faster-whisper, na kratkom isečku.

mlx-whisper ne preporučujem: zavisi od torch-a, ne može da zakuca reviziju modela i ima neuredno pakovan wheel.
openai-whisper ne treba: povlači torch i spor je na CPU-u. On ipak proverava SHA-256 modela
(`whisper/__init__.py:57-90`) i učitava ga sa `weights_only=True` (`:150-151`).

## 3. streamlink (snimanje Twitch live-a)

- **Izvor:** 8.6.3, PyPI attestacija `streamlink/streamlink`, `release.yml`. Od 8.5.0 GitHub izdanja su
  nepromenljiva, akcije su zakucane na commit, a izdanja se grade iz `uv.lock`-a (CHANGELOG 8.5.0). Zavisnosti
  u Prilogu C su iz njihovog `uv.lock`-a za tag 8.6.3, osim Windows-only `cffi`/`pycparser`.
- **pycryptodome 4.2.0:** grana 4.x postoji od 14. 10. 2026, isti autor i zvanični changelog. streamlink 8.6.3
  izričito dozvoljava `<5`.
- **CVE:** CVE-2026-44353 (`file://` u HLS/DASH, ispravljeno u 8.4.0), CVE-2026-92164 (preusmerenje na
  `file://`, 8.6.0), GHSA-j7pf-m7gx-jr33 (`file://` u DASH `Location`, 8.6.2). 8.6.3 nije pogođen.
- **Telemetrija:** nema. Twitch plugin koristi javni Client-ID Twitch web plejera (`streamlink/plugins/twitch.py:348`).
- **Ne sme se pokretati:** dodaci iz podrazumevanog foldera. Na Mac-u je to
  `~/Library/Application Support/streamlink/plugins`, koji se učitava sam (`streamlink_cli/constants.py:33-41`),
  pa se uvek dodaju `--no-plugin-sideloading` i `--no-config`. Zabranjeni su i `--plugin-dir(s)`,
  `--twitch-api-header` sa OAuth tokenom, `--http-cookie`, `--player*` i `--player-external-http`
  (otvara HTTP server). Snima se samo sa `-o` u fajl.
- **YouTube live** snima yt-dlp (`--live-from-start`), a ne streamlink.

## 4. Chat

**Twitch, anonimni IRC: uz uslove.** `justinfan<broj>` **nije u zvaničnoj dokumentaciji**.
dev.twitch.tv/docs/chat/irc (provereno 23. 11. 2026) traži User Access Token i preporučuje EventSub. Anonimnu
prijavu opisuju samo forum za Twitch programere i biblioteke (twitch-irc, go-twitch-irc). To je *prijavljeno*,
nije zvanično, i može prestati da radi bez najave. Uslovi za naš socket kod:
- samo `irc.chat.twitch.tv:6697` preko TLS-a (`ssl.create_default_context()`, provera hosta), nikad 6667;
- ime kanala se proverava sa `^[a-z0-9_]{3,25}$` pre `JOIN`, da CR/LF ne ubaci IRC komandu;
- na `PING` se odgovara `PONG` istim tekstom, inače Twitch prekida vezu (zvanična dokumentacija);
- linija ima ograničenu dužinu, dekodira se sa `errors="replace"`, a sadržaj nikad ne ide u `eval` ili shell;
- veza se ponovo otvara sa sve dužom pauzom;
- čuvaju se samo vreme i broj poruka, bez korisničkih imena;
- ako prestane da radi, zvanični put je EventSub sa tokenom u env promenljivoj. To pre upotrebe ide na pregled.

**YouTube: Data API v3 (preporuka) umesto `chat-downloader`.**
- `liveChatMessages.list` i `streamList` koštaju po 5 jedinica, a podrazumevana kvota je 10.000 jedinica dnevno
  (developers.google.com, 23. 11. 2026). To je oko 2.000 poziva, odnosno oko 2,8 h jednog streama pri pozivu na
  5 s. `streamList` šalje poruke čim stignu, pa troši manje poziva. Poštuje se `pollingIntervalMillis`.
- Ključ ide samo u env promenljivu `YOUTUBE_API_KEY`, bez rezervne vrednosti u kodu. U Google Cloud-u se
  ograniči samo na YouTube Data API v3, a na serveru i na IP adresu.
- Dokumentacija ne kaže da li je za tuđ javni chat dovoljan API ključ ili treba OAuth. To je *prijavljeno* u
  zajednici i proverava se prvim testom.

`chat-downloader` 0.2.8 je odbijen:
- nema izdanja više od 3 godine;
- čita interni YouTube API (`/youtubei/v1/live_chat/…`, `chat_downloader/sites/youtube.py:455`);
- Twitch chat čita preko **nešifrovanog** porta 6667 (`chat_downloader/sites/twitch.py:57, 69`);
- nema attestaciju.

Ako treba chat posle streama, yt-dlp već ume `--write-subs --sub-langs live_chat`. On takođe čita interni API,
ali ne traži nov paket.

## 5. Mac: Homebrew

- **Instalacija.** Zvanično je `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  (docs.brew.sh/Installation). To je `curl | bash` sa `HEAD`-a, koji po našim pravilima ne pokrećemo naslepo.
  Bolje je koristiti `.pkg` sa github.com/Homebrew/brew/releases/latest i pre pokretanja proveriti potpis.
  Druga mogućnost je preuzeti `install.sh`, pročitati ga, pa pokrenuti.
- **Uslovi Homebrew-a.** Traži macOS 15 (Sequoia) ili noviji. Na Apple Silicon-u je prefiks `/opt/homebrew`.
  Docs kažu da nema bezbednosnih garancija ako u prefiks mogu da pišu korisnici kojima se ne veruje.
- **Analitika.** Šalje se u InfluxDB, bez ID-a korisnika i IP polja (docs.brew.sh/Analytics, 23. 11. 2026).
  Homebrew prikaže obaveštenje pre nego što je uključi. Isključuje se sa `export HOMEBREW_NO_ANALYTICS=1`
  **pre instalacije** i `brew analytics off`, a provera je `brew analytics state`.
- **`HOMEBREW_NO_AUTO_UPDATE=1`.** `brew install` inače prvo sam povuče najnovije formule, mimo pravila dve
  nedelje. Nadogradnja je svesna: `brew update`, pa `brew outdated`, pa `brew upgrade <formula>`.
- **ffmpeg i libass.** Obični `brew install ffmpeg` (9.1) **nema libass ni freetype/fontconfig**. Zavisnosti su
  samo dav1d, lame, libvmaf, libvpx, openssl@4, opus, sdl2-compat, svt-av1, x264, x265 i xz, a u
  `Formula/f/ffmpeg.rb:71-96` nema `--enable-libass` (formulae.brew.sh i homebrew-core, 23. 11. 2026). Zato
  `ass=` filter u `clipper/split.py:228` ne bi radio. Treba **`brew install ffmpeg-full`** (9.1): ima libass,
  freetype, fontconfig, harfbuzz i x264.
  - ffmpeg-full je *keg-only*, pa nije u PATH-u i mora se dodati ručno (komande ispod).
  - Ima oko 46 zavisnosti (između ostalih tesseract, libssh, zeromq), pa je i površina za napad veća.
    Daje mu se samo lokalni fajl, nikad tuđ URL.
  - Verzija 9.1 je novija od 6.1, sa kojom je clipper pisan, pa `tester` treba da proveri `split.py`.
- **Python.** `brew install python@3.14` (3.14.10). Homebrew-ov Python ne dozvoljava `pip` van venv-a, što
  nama i odgovara.
- **yt-dlp i streamlink preko brew-a.** Formule postoje (yt-dlp 2026.10.26 sa deno-om i curl-impersonate-om,
  streamlink 8.6.3). Obe su na `python@3.15`, a resursi su sa PyPI-ja sa SHA-256 u formuli.
  - **Prednost:** jedna komanda.
  - **Mana:** `brew upgrade` i automatsko osvežavanje odmah uzimaju najnoviju verziju, starija se ne može
    instalirati (`brew pin` samo zamrzava), a na serveru bi bila druga verzija.
  - **Odluka:** pip u venv-u sa heševima. Brew samo kao rezerva za yt-dlp, uz `brew pin yt-dlp`. Ne instalira
    se oba odjednom, jer se onda ne zna koji je u PATH-u.

## 6. Uslovi korišćenja (činjenice, odluku donosi korisnik)

**YouTube Terms of Service** („Dated: December 15, 2023”, youtube.com/t/terms, učitano 23. 11. 2026).
Pod „You are not allowed to” stoji:
- „access, reproduce, download, distribute, … or otherwise use any part of the Service or any Content except”
  ako je to izričito omogućeno funkcijom Servisa ili „with prior written permission from YouTube and, if
  applicable, the respective rights holders”;
- „access the Service using any automated means (such as robots, botnets or scrapers)”, osim javnih
  pretraživača po robots.txt ili uz pisanu dozvolu;
- „circumvent, disable, fraudulently engage with, or otherwise interfere with any part of the Service”;
- „collect or harvest any information that might identify a person (for example, usernames or faces)”.

Licenca drugim korisnicima važi „only as enabled by a feature of the Service (such as video playback or embeds)”.
Činjenica o alatu: yt-dlp rešava YouTube-ove JS izazove pomoću EJS (yt-dlp wiki „EJS”).

**Twitch Terms of Service** („Last modified on 08/12/2026”, legal.twitch.com, učitano 23. 11. 2026):
- deo 7 (License): licenca je „for your personal use or internal business use only”. Zabranjeni su „(d) use
  of any data mining, robots, or similar data gathering or extraction methods” i „(e) downloading (except page
  caching) of any portion of the Twitch Services, the Materials, … except as expressly permitted”.
  „Materials” ne obuhvata User Content, odnosno same streamove;
- deo 8(a): drugi korisnici dobijaju prava nad tuđim sadržajem samo „if features that give other Twitch users
  the ability to use or share your User Content off of Twitch are turned on”;
- deo 10 (Prohibited Conduct), tačka xi: pristup „by means of any robot, spider, scraper, crawler, or other
  automated means for any purpose”.

Autorska prava strimera su posebno pitanje (vidi README, „Rizik”). Dozvola strimera, npr. kroz kampanju, nije
isto što i dozvola platforme.

## 7. Komande za instalaciju (Mac, Apple Silicon)

Fajlovi `clipper/zahtevi/*.txt` još ne postoje. Direktor ih pravi iz Priloga, doslovno, posle odobrenja korisnika.

```sh
# 0) jednom, PRE Homebrew-a
cat >> ~/.zprofile <<'X'
export HOMEBREW_NO_ANALYTICS=1 HOMEBREW_NO_AUTO_UPDATE=1
export HF_HUB_DISABLE_TELEMETRY=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 HF_HUB_DISABLE_UPDATE_CHECK=1
export DO_NOT_TRACK=1 PIP_DISABLE_PIP_VERSION_CHECK=1
X
source ~/.zprofile
# Homebrew .pkg sa github.com/Homebrew/brew/releases/latest; pre otvaranja:
pkgutil --check-signature ~/Downloads/Homebrew-*.pkg   # očekuje se Developer ID Installer, Homebrew
brew analytics off && brew analytics state

# 1) sistemski alati
brew install python@3.14 ffmpeg-full
export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"     # dodati i u ~/.zprofile
ffmpeg -hide_banner -filters | grep -w ass              # mora da ispiše red sa "ass"

# 2) venv i paketi (iz korena repoa)
/opt/homebrew/bin/python3.14 -m venv clipper/.venv
source clipper/.venv/bin/activate
python -m pip install --require-hashes --only-binary=:all: \
  -r clipper/zahtevi/yt-dlp.txt -r clipper/zahtevi/whisper.txt -r clipper/zahtevi/streamlink.txt
python -m pip check

# 3) model (jednom), pa provera heša
python - <<'PY'
from huggingface_hub import snapshot_download
snapshot_download("dropbox-dash/faster-whisper-large-v3-turbo",
    revision="0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf",
    local_dir="clipper/modeli/faster-whisper-large-v3-turbo",
    allow_patterns=["config.json", "preprocessor_config.json", "model.bin", "tokenizer.json", "vocabulary.*"])
PY
shasum -a 256 clipper/modeli/faster-whisper-large-v3-turbo/model.bin
# mora: e76620f83d5f5b69efd3d87e3dc180c1bd21df9fbebacfd4335e5e1efcc018da
export HF_HUB_OFFLINE=1
```

Upotreba, uvek sa ovim zastavicama:

```sh
yt-dlp --ignore-config --no-plugin-dirs --no-update --no-remote-components \
  --js-runtimes "deno:clipper/.venv/bin/deno" --restrict-filenames \
  -P clipper/ulaz -o "%(id)s.%(ext)s" --write-subs --write-auto-subs --sub-langs en --sub-format vtt URL

streamlink --no-config --no-plugin-sideloading \
  -o "clipper/snimci/kanal-{time:%Y%m%d-%H%M%S}.ts" https://www.twitch.tv/KANAL best
```

U Python-u se model učitava iz lokalnog foldera:
`WhisperModel("clipper/modeli/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8")`,
a transkribuje sa `word_timestamps=True, vad_filter=True`.

Linux server koristi iste liste (manylinux x86_64, Python 3.13 ili 3.14). ffmpeg iz distribucije mora imati
filter `ass`. Za Windows ili Linux aarch64 liste se prave ponovo.

## Napomena posle prve upotrebe (direktor, 23. 11. 2026)

Zakucani faster-whisper 1.2.1 poziva `av.open(..., metadata_errors="ignore")`, a zakucani av 19.0.2 tu opciju više
nema (`TypeError`). Paketi se ne menjaju: `clipper/transkript.py` dekodira zvuk ffmpeg-om i Whisper-u daje niz
uzoraka, pa se av za dekodiranje ne koristi. Model je preuzet po tačnom commit-u i heš se poklopio.

## 8. Nalazi u postojećem kodu

- **NISKO, `clipper/alati.py:25`:** poruka kaže „Mac: brew install ffmpeg”, a taj ffmpeg nema libass, pa
  korisnik odmah pada na proveri u `:28-29`. Ispravka: „Mac: brew install ffmpeg-full (pa dodati
  `$(brew --prefix ffmpeg-full)/bin` u PATH)”.
- **NISKO, `clipper/README.md:23`:** piše „Python 3.10+”, a yt-dlp 2026.10.26 traži Python 3.11 ili noviji
  (PyPI `requires_python`). Ispravka: „Python 3.14 (Homebrew)”.
- **NISKO, `clipper/.gitignore`:** nedostaju `.venv/`, `modeli/`, `snimci/` i `chat/`. Rizik je commit modela
  od nekoliko GB ili chat logova sa korisničkim imenima.

## Šta je provereno

- PyPI JSON i PyPI Integrity (attestacije); OSV.dev za sve zakucane pakete; čitanje koda iz preuzetih wheel-ova
  (yt-dlp, faster-whisper, huggingface-hub, streamlink, mlx-whisper, chat-downloader, openai-whisper).
- Rezolucija zavisnosti bez instalacije: `pip --dry-run --only-binary=:all:` za macOS arm64 i Linux x86_64,
  Python 3.13 i 3.14, svih 12 kombinacija u `--require-hashes` režimu.
- Stvarno preuzimanje 48 macOS wheel-ova sa proverom heševa (118 MB). Nijedan nema `.pth` fajl, a pretraga za
  zamaskiranim kodom (`exec`/`eval` nad base64/zlib/marshal, dugi base64) nije našla ništa.
- Izvori (svi učitani 23. 11. 2026):
  - zvanični dokumenti projekata: yt-dlp README (tag 2026.10.26) i wiki „EJS”; streamlink CHANGELOG i `uv.lock`
    (tag 8.6.3); CHANGELOG-ovi CTranslate2, PyAV, pycryptodome i filelock; whisper.cpp README v1.9.5 i stranica
    izdanja;
  - Hugging Face API (repoi modela i commit-ovi);
  - Homebrew: formulae.brew.sh, homebrew-core formule, docs.brew.sh (Installation, Analytics);
  - uslovi i dokumentacija platformi: YouTube ToS, Twitch ToS, dev.twitch.tv (IRC), developers.google.com
    (YouTube Data API).
- GitHub API je u ovoj sesiji bio blokiran. GHSA podaci su uzeti preko OSV-a, a stranice sa savetima u
  repoima nisam otvarao direktno.
- Nijedna stranica nije tražila da se nešto pokrene.

## Prilog: zaključane liste (macOS arm64 i Linux x86_64, Python 3.13 i 3.14)

Heševi su sa PyPI-ja (23. 11. 2026) za sve wheel fajlove koji odgovaraju ovim platformama. Za Windows ili
aarch64 lista se pravi ponovo. Uz svaku nadogradnju liste pravi `bezbednost`.

### Prilog A: `clipper/zahtevi/yt-dlp.txt`

```text
# yt-dlp 2026.10.26 + yt-dlp-ejs 0.8.0 + deno 2.9.8; pregled bezbednost 23. 11. 2026
brotli==1.2.1 \
    --hash=sha256:264fd5b200f6f6170cb551a4b9fcaabf8aa846ddaefe72db4d5f49f9d3743df9 \
    --hash=sha256:a84e0ae14d1efe782a9f143021c4e01d5ed986a140fe5070505cc5978eaf0592 \
    --hash=sha256:a998857af4fcd19920bdf5f30f0f1a23f38472a703d33e49168cd4fd32438377 \
    --hash=sha256:b8b2fc7901b31d5885f26521cf2d74feccdc126a272ba1d879b7545bb25468bc
certifi==2026.10.23 \
    --hash=sha256:e9b54de76e530bb6cf0ccd036787103acb58fd42ba930ea8bf948ddbaa2f61d1
charset-normalizer==3.5.2 \
    --hash=sha256:1c50fe28bbc2ced33386f298650d91218076c05420e6cbd790b913adc41659e7 \
    --hash=sha256:34276fd796040bf0993ab33a369aa572e6979c7aab225a88893667ad8eac8f7a \
    --hash=sha256:4275811936e2f06feff5e598fb42a1b7ae852da8e39605211892b56b81a34efd \
    --hash=sha256:6045373d5a89a5ec71afde535db987ca28e76dfa276c2d4c818265b375d4b055 \
    --hash=sha256:7218e8f32b0956cfcd048fd42d9d5779809745ca1d86113ca56f66e7ae1549c4 \
    --hash=sha256:b6b751274acb69d77b3323d6b7dbaa3c7fdfc1eb829b7eb61d262f32e1af9685 \
    --hash=sha256:fcff63213e8e6e47770541a4607175404f47cbb3ebea7b6058cc82d524a0e424
deno==2.9.8 \
    --hash=sha256:b1d1318e7deda8efd593aefa8b565a827fe71cf83aeff09d3a5ceb047444ca18 \
    --hash=sha256:b82eac91d3e3f6fe37d94a12f833550e05029274cb9020b1e3f0f61e1678dc24
idna==3.20 \
    --hash=sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
mutagen==1.48.1 \
    --hash=sha256:4f077fe87d3fc7fba259aa63d8c026b18382ca6a42ef37c61e16f1b1b5b82fe7
pycryptodomex==3.24.1 \
    --hash=sha256:9b94a8c647c1f80b4c82c7ac9642dda94a71abbb4efa29ad652c410ad7a39879 \
    --hash=sha256:9bb353c764c144a9fc03302ef3763ad0c3e75bc7ca41f445cc98455f36da6c59
requests==2.34.2 \
    --hash=sha256:2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0
urllib3==2.8.0 \
    --hash=sha256:0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3
websockets==17.3 \
    --hash=sha256:018fab26140ce221c3853454a608e4e7004f4f10641cb97819dcd5b917bb2e99 \
    --hash=sha256:52a2ca6f401fb49a8d5d9e0e48ade5f58f1bdda33132907b0e4e3b702628fa4e \
    --hash=sha256:8dbb3862aa649de95660b6337d97101977f160b5b354d07b82fe309874d2c8bc \
    --hash=sha256:bc8fd230ef013951900c1fda100eebe4a4b1b407dde2a44186995042dda2c628 \
    --hash=sha256:dc2b495a92b3971966bf102e73589f950db3ec1ca6713265355ce7771d97b199 \
    --hash=sha256:de2c12555bf05546f3ee75733f2c81de70aab7f530e86d0d2162b0ddcb3c39ae \
    --hash=sha256:fe7a168d805c8a7bf1c2de55b7ab2bc958586bfd88d0e87235a92cac66b590a7
yt-dlp[default,pin,deno,pin-deno]==2026.10.26 \
    --hash=sha256:a05c5b5d8562f7e8a62f5334348b406af4930d56d3a65f8021d14af0e22339ae
yt-dlp-ejs==0.8.0 \
    --hash=sha256:79300e5fca7f937a1eeede11f0456862c1b41107ce1d726871e0207424f4bdb4
```

### Prilog B: `clipper/zahtevi/whisper.txt`

```text
# faster-whisper 1.2.1 i zavisnosti; pregled bezbednost 23. 11. 2026
anyio==4.16.0 \
    --hash=sha256:c66ae634e0b8228396b801741beb3294326d4b6102f7bba4041c0dfb58c29026
av==19.0.2 \
    --hash=sha256:9c1da7aad0fa6c13b4a5c1e7985be0d13f8526a96284573acaf3d55ead6d3fe8 \
    --hash=sha256:b0dff6dfcc6ff9944fbbff15bc4ee2d90a2c1695d493bdea96e86f48823e9feb
click==8.5.1 \
    --hash=sha256:8bb5376d2006950386f8c6427613334a2acadc5f559cb80e638d00b4df957e37
ctranslate2==4.8.5 \
    --hash=sha256:19499d132075e2c07a5158718323b085160b228791734c66f2e49a815b6dfe43 \
    --hash=sha256:870964b5fcedf156c7efc0a4c7cd192d10cce5e0668751999238b587a20c49d4 \
    --hash=sha256:97fe1ffa5bb9576051502da62324bd59d14d7334f18b79f6529a7a317ab35416 \
    --hash=sha256:b9efe6d3a4a3bda42ac579c461d073985dc9d2796773d13a95d7d26018363807
faster-whisper==1.2.1 \
    --hash=sha256:79a66ad50688c0b794dd501dc340a736992a6342f7f95e5811be60b5224a26a7
filelock==4.2.10 \
    --hash=sha256:9479aaeb4db20b5a53e3da28493edd24720b66b8a0b84030aa56ccdf243d6857
flatbuffers==25.12.19 \
    --hash=sha256:7634f50c427838bb021c2d66a3d1168e9d199b0607e6329399f04846d42e20b4
fsspec==2026.9.0 \
    --hash=sha256:8dd6e646e99ea382bd85f97a45e6b526a442d79423a7dc673f1e2756d05fcb5f
h11==0.16.0 \
    --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
hf-xet==1.8.0 \
    --hash=sha256:29dab7c904cd1914a0439c6e1306c12c7497c8bd32290fbe563ebf51ca4b6d6d \
    --hash=sha256:3e8934784425781f0f779b91044df441f3a7af4dab47375d7e3aeaecbb8eecb4
httpcore2==2.16.0 \
    --hash=sha256:5c4358319f2602d984ad93182c9fee5160f22e9da7babdda870a5e7c4e2dc34f
httpx2==2.16.0 \
    --hash=sha256:fd2c5d7909e8d86fe92d53020c310ca0e4e431b838c207c5754b9bbf0308d49a
huggingface-hub==2.4.0 \
    --hash=sha256:42ecfd93ede47bdd333daebbf66a32d7bfe2e18752754fe4d2d4f98a0179d801
idna==3.20 \
    --hash=sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
numpy==2.5.4 \
    --hash=sha256:6d6a71b9d9a97c03633aa12565ef2825ffa036cc1d99cfd50dacf0f128af4fe2 \
    --hash=sha256:6ffa07666f8da0eef81d149934a626d0d95fbd6838432a33e66245423a9062c0 \
    --hash=sha256:7415db95818b39ec475a5eea54d9e3b6bc83e3912158e46da3438cdce399804d \
    --hash=sha256:956555e0603a4d38019ae6925711cb9dc43195c076a928accf7ea5d50bddfe53 \
    --hash=sha256:d549420b8858885cea8838a727842249218b9c1da24dd517e25c9c7a948310a3 \
    --hash=sha256:ffa6ce09a1c6a08e9667dd9c97aa0b14184e8d18f2a14b78b2a2328c9147f076
onnxruntime==1.31.1 \
    --hash=sha256:74a6a52994616c4d18b33db1e13c226333a70a6ba07480a5cab9c2a50dff1430 \
    --hash=sha256:8536ac43682caa7492c46d6cfd4c3c8db288dcf0619508431a22170b670ee1d0 \
    --hash=sha256:c20d7f15d84427db070b163f78c2c7146cc93edd6113fa7327671259a24184fe \
    --hash=sha256:e4ad067d36e2220218e085d7223283b2ee1bc73d887e811fd14d21cf901a11ee
packaging==26.3 \
    --hash=sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
protobuf==7.36.2 \
    --hash=sha256:89f23aa53c24553a2416fd4fd1ec06f74fa42b14b546d8883128813f775bbfd2 \
    --hash=sha256:bdb3a345d48db958e6ce1f18e508beb0cc981d64f24088427549c866cd039f1e \
    --hash=sha256:cbc70b17ee27e28894c7fee8bb04be1abead49e936bc70eb60052531eee2079e
pyyaml==6.0.3 \
    --hash=sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6 \
    --hash=sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1 \
    --hash=sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310 \
    --hash=sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5
tokenizers==0.23.3 \
    --hash=sha256:376851d22bcf9d650a5c3090bb83e6cf9e895fbf0595369fa4cd43c1f69b5f87 \
    --hash=sha256:68649e97d5b43c44c031d8d848874a6eecae8f8fe40ea989aa777a5a83aca716
tqdm==4.70.1 \
    --hash=sha256:c293e525e6fef9c20e8728fd4612df02a0aa31bb5fe91ecd93e123b1b7bffa73
truststore==0.10.5 \
    --hash=sha256:9aaaedaefaf06d8b206278cf8b5012bc897f485a874503501e12d776df78951c
typing-extensions==4.16.0 \
    --hash=sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8
```

### Prilog C: `clipper/zahtevi/streamlink.txt`

```text
# streamlink 8.6.3, verzije iz njihovog uv.lock (tag 8.6.3); pregled bezbednost 23. 11. 2026
attrs==26.1.0 \
    --hash=sha256:c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309
certifi==2026.10.23 \
    --hash=sha256:e9b54de76e530bb6cf0ccd036787103acb58fd42ba930ea8bf948ddbaa2f61d1
charset-normalizer==3.5.2 \
    --hash=sha256:1c50fe28bbc2ced33386f298650d91218076c05420e6cbd790b913adc41659e7 \
    --hash=sha256:34276fd796040bf0993ab33a369aa572e6979c7aab225a88893667ad8eac8f7a \
    --hash=sha256:4275811936e2f06feff5e598fb42a1b7ae852da8e39605211892b56b81a34efd \
    --hash=sha256:6045373d5a89a5ec71afde535db987ca28e76dfa276c2d4c818265b375d4b055 \
    --hash=sha256:7218e8f32b0956cfcd048fd42d9d5779809745ca1d86113ca56f66e7ae1549c4 \
    --hash=sha256:b6b751274acb69d77b3323d6b7dbaa3c7fdfc1eb829b7eb61d262f32e1af9685 \
    --hash=sha256:fcff63213e8e6e47770541a4607175404f47cbb3ebea7b6058cc82d524a0e424
h11==0.16.0 \
    --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
idna==3.20 \
    --hash=sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
isodate==0.7.2 \
    --hash=sha256:28009937d8031054830160fce6d409ed342816b543597cece116d966c6d99e15
lxml==6.1.3 \
    --hash=sha256:2bec13085dc8ef48a3fe62f7dfcacfeda2c785cdf19cc8eeda2bb9ed081da165 \
    --hash=sha256:3a48093cdb058a93af842ede9703520e810b05dcd0fc6d7190a06376c3bfb6bd \
    --hash=sha256:a7eb78ba28b187e1e9203a55c60fcf70df2d22cb205fe6d51b9383d6097419f0 \
    --hash=sha256:b477912f42c5c33405a10c759d22f80cf5af043ae02d95b9d8e5e5bc555739ed \
    --hash=sha256:c6c0c13128a32eb04a51357e56a094e13aa8e6d3d1884de2e9ae923f6915e1a8 \
    --hash=sha256:d85dfab42dd672f87a7f76e9de7172962aee69fa12044f0d6e1a23cbd53fb80e
outcome==1.3.0.post0 \
    --hash=sha256:e771c5ce06d1415e356078d3bdd68523f284b4ce5419828922b6871e65eda82b
pycountry==26.2.16 \
    --hash=sha256:115c4baf7cceaa30f59a4694d79483c9167dbce7a9de4d3d571c5f3ea77c305a
pycryptodome==4.2.0 \
    --hash=sha256:3e430168f767ecec60c1f850df4abbd0b9f94786b9cc8041a00e976f6d5190c6 \
    --hash=sha256:76777686de3a354c41710727988c2284448d5db9bd82e5ddb9a9b6710d17d9df
pysocks==1.7.1 \
    --hash=sha256:2725bd0a9925919b9b51739eea5f9e2bae91e83288108a9ad338b2e3a4435ee5
requests==2.34.2 \
    --hash=sha256:2a0d60c172f83ac6ab31e4554906c0f3b3588d37b5cb939b1c061f4907e278e0
sniffio==1.3.1 \
    --hash=sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2
sortedcontainers==2.4.0 \
    --hash=sha256:a163dcaede0f1c021485e957a39245190e74249897e2ae4b2aa38595db237ee0
streamlink==8.6.3 \
    --hash=sha256:8279fe4207f49c6a53db0787e9d47ff0e2953a0ac79bbbc1e59ac1a5e586ed6c
trio==0.34.0 \
    --hash=sha256:6c7c9f49917694dcdcd5f67abd168df5599eca480d61f29854d17a61a75c2f05
trio-websocket==0.12.2 \
    --hash=sha256:df605665f1db533f4a386c94525870851096a223adcb97f72a07e8b4beba45b6
urllib3==2.8.0 \
    --hash=sha256:0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3
websocket-client==1.9.2 \
    --hash=sha256:e1a673830a9c7bfa47b1cd3d5e4178f4c9651d80a4eab02c9c23a1c3ec6250ce
wsproto==1.3.2 \
    --hash=sha256:61eea322cdf56e8cc904bd3ad7573359a242ba65688716b0710a5eb12beab584
```
