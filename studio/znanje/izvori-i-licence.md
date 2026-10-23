# Besplatni izvori: licence i bezbedno preuzimanje

Poslednja provera: 2026-10-23 (`bezbednost`). Vodi direktor, a dopunjuje se posle svake nove provere.

## Ishodi

| Izvor / alat | Licenca | Ishod | Ključni uslovi |
|---|---|---|---|
| **Poly Haven** (HDRI, teksture, modeli) | CC0 | **preporučeno** | samo HDRI `.hdr`/`.exr`, teksture `.jpg`/`.png`, modeli **glTF** (`.gltf` + `.bin` + `.jpg`); ne `.blend`, FBX, USD, MTLX; md5 i veličina iz `api.polyhaven.com/files/<id>`; fajlovi samo sa `dl.polyhaven.org`; ne koristiti njihove sličice (nisu CC0) |
| **ambientCG** (PBR teksture) | CC0 | uz uslove | ZIP nema nezavisni heš; pre raspakivanja izlistati, uzeti samo ravne `.jpg`/`.png` |
| **Pexels** (foto, video) | Pexels License | uz uslove | sme da se menja; **sirovi fajlovi ne idu u javni repo** (zabrana „standalone" distribucije); bez prepoznatljivih ljudi i brendova u kadru |
| **Pixabay** | Content License | uz uslove | isto kao Pexels; zabranjena komercijalna upotreba brendova u kadru „u vezi sa robom i uslugama" |
| **Mixkit** (samo *Free* licenca) | Stock Video Free License | uz uslove | sirovi fajlovi ne u repo; ručno preuzimanje, bez botova; *Restricted* licenca nije za klijente |
| **Coverr** | Coverr License | uz uslove, poslednji izbor | uslovi se mogu menjati, katalog je pomešan sa Shutterstock-om; uzimati samo stavke sa jasnom Coverr licencom |
| **Unsplash** | Unsplash License | uz uslove | licenca dozvoljava izmenu; API smernice traže hotlink i `download_location`, pa birati i preuzimati ručno sa unsplash.com i hostovati kod nas |
| **rembg 2.0.86** (izdvajanje pozadine) | MIT; modeli različito | uz uslove | samo u posebnom venv-u, sa Pillow 13.0.0; model **uvek eksplicitno**: `isnet-general-use`, `u2net`, `birefnet-general(-lite)`; **nikad** `bria-rmbg` (nekomercijalan, a od 2.0.80 je podrazumevani!), `withoutbg`, `atlascloud` (šalju slike na tuđe servere); bez `[cli]` i servera; proveriti md5 modela pre učitavanja |
| backgroundremover | — | ne | md5 provera zakomentarisana, `torch.load` pickle |
| Robust Video Matting | GPL-3.0 | ne | model je za ljude |
| SDXL Turbo (lokalni img2img) | Stability Community License | uz uslove, samo procena | prihod < 1 M USD + registracija; `diffusers` ≥ 0.38, `torch` ≥ 2.6, samo safetensors, offline |
| FLUX.1 schnell | Apache-2.0 | ne na ovoj mašini | ne staje u 15 GB RAM-a |

## Pravila za repo

- Izvorni stock i CC0 fajlovi idu u `studio/<projekat>/izvori/`. Taj folder je u `.gitignore` i ne objavljuje se.
- U repo i na sajt idu samo **izvedeni** rezultati: maskirane, kolor-korigovane i kadrirane WebP sekvence.
- Za svaki izvor u repou stoji manifest `studio/<projekat>/izvori.md`: URL stavke, autor, licenca sa datumom, datum preuzimanja i sha256.

## Bezbedna obrada tuđih fajlova

- **ffmpeg** u kontejneru nema bezbednosne zakrpe (Ubuntu 6.1.1, poslednji USN 2026-10-12). Tuđe snimke dekodirati samo izolovano:
  `unshare -rn ffmpeg -v error -protocol_whitelist file -f mov -i <fajl> …`. Nikad `.m3u8`.
- **Pillow** 12.3.0 u sistemu ima 39 objavljenih ranjivosti, ispravljeno u 13.0.0. Za tuđe slike koristiti venv sa `pillow==13.0.0` i `Image.open(p, formats=['JPEG','PNG','WEBP'])`.
- Svaki preuzeti fajl ide u nov, prazan folder. Proveri magic bytes (MP4 `ftyp`, PNG, JPEG) pre obrade.
