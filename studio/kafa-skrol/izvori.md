# Izvori medija: Kafa skrol

`mediji`, 23.10.2026. Pravila su u `studio/znanje/izvori-i-licence.md`. Sirovi fajlovi su u `studio/kafa-skrol/izvori/` (gitignored, ne objavljuju se). U `KafaSkrol/public/media/` idu samo izvedeni fajlovi.

Ponovno pravljenje izvedenih fajlova (iz foldera `scripts/kafa/`, venv `~/.venvs/media` sa `pillow==13.0.0`):

```
# para (obe petlje)
SRC=studio/kafa-skrol/izvori/steam/mixkit-43935/mixkit-43935-4k.mp4
OUT=KafaSkrol/public/media/steam
~/.venvs/media/bin/python -I scripts/kafa/steam_loop.py $SRC $OUT steam-cup-a --crop 870 0 1980 1090 --width 1200 --black 4
~/.venvs/media/bin/python -I scripts/kafa/steam_loop.py $SRC $OUT steam-cup-b --crop 660 0 1740 1090 --width 1000 --start 100 --frames 120 --xfade 24 --black 4 --gain 2.6
# fotografije (sve)
~/.venvs/media/bin/python -I scripts/kafa/photos.py studio/kafa-skrol/izvori/photos KafaSkrol/public/media/photos
```

## Licence (provera 23.10.2026)

| Licenca | Provereno | Šta važi za nas |
|---|---|---|
| **Mixkit Stock Video Free License** | stranica klipa 43935, 23.10.2026: „Download this free stock video clip for commercial or personal use, under the Mixkit Stock Video Free License." (ne *Restricted*) | komercijalno i nekomercijalno, izmene dozvoljene, bez obaveznog navođenja; ne prodavati neizmenjene kopije; sirovi fajl ne u repo |
| **Unsplash License** | [unsplash.com/license](https://unsplash.com/license), 23.10.2026 | besplatno, komercijalno, izmene dozvoljene, navođenje nije obavezno; ne prodavati bez bitne izmene; ne pokriva brendove, prepoznatljive ljude, umetnička dela na slici |
| **Pexels License** | [pexels.com/license](https://www.pexels.com/license/), 23.10.2026 | besplatno, komercijalno, izmene dozvoljene, navođenje nije obavezno; ne sugerisati da ljudi ili brendovi preporučuju proizvod; ne prodavati neizmenjene kopije |

## A. Para (`KafaSkrol/public/media/steam/`)

### Izvor: Mixkit 43935, „Demonstration video of a steaming cup of coffee"

| Polje | Vrednost |
|---|---|
| Stranica | https://mixkit.co/free-stock-video/demonstration-video-of-a-steaming-cup-of-coffee-43935/ |
| Autor | Mixkit (stranica ne navodi pojedinačnog autora, profil `/@mixkit/`) |
| Licenca | Mixkit Stock Video Free License, provereno 23.10.2026 |
| Preuzeto | 23.10.2026, jedan fajl, `https://assets.mixkit.co/videos/43935/43935-2160.mp4` (isti fajl koji daje dugme „Download", `content-disposition: ...-43935-4k.mp4`) |
| Fajl | `studio/kafa-skrol/izvori/steam/mixkit-43935/mixkit-43935-4k.mp4`, 45 393 784 B, H.264 3840×2160, 24000/1001 fps, 10,39 s, 249 kadrova, magic bytes `ftyp` |
| sha256 | `e530a00119a76b5500bd16dbd0f51a1cf77f0a2aa3ce32c846448a6bcd65b105` |
| Sadržaj | tamna šolja na tanjiriću, zrna, kriška limuna i cimet, nema logotipa ni ljudi; za pare se koristi samo gornji deo kadra iznad ivice šolje |

Obrada: `unshare -rn ffmpeg -protocol_whitelist file -f mov` (crop + smanjenje, sirovi RGB kadrovi), ploča pozadine = minimum po pikselu svih zamućenih kadrova (para samo posvetli piksel), para = kadar minus ploča (smeđa pozadina i vinjeta postaju čista crna), levels (crna tačka 4, pojačanje 2,2 / 2,6), blago topla boja (krem), meka ivica u crno sa sve četiri strane, petlja 120 kadrova + 24 kadra preliva, bez zvuka.

Izvedeni fajlovi:

| Fajl | Format | Rezolucija | Trajanje | Veličina | Isečak izvora |
|---|---|---|---|---|---|
| `steam/steam-cup-a.webm` | VP9, yuv420p, bt709 tv | 1200×660 | 5,00 s, 24 fps | 227 394 B | x 870, y 0, 1980×1090; kadrovi 0–143 (stub pare, vrtlog) |
| `steam/steam-cup-a.mp4` | H.264 high, faststart | 1200×660 | 5,00 s, 24 fps | 473 278 B | isto |
| `steam/steam-cup-a-seq/000.webp … 029.webp` | WebP q72, 30 kadrova (svaki 4. kadar petlje) | 1200×660 | | ~165 KB ukupno | isto |
| `steam/steam-cup-b.webm` | VP9 | 1000×626 | 5,00 s, 24 fps | 304 880 B | x 660, y 0, 1740×1090; kadrovi 100–243 (tanka, lenja para) |
| `steam/steam-cup-b.mp4` | H.264 high, faststart | 1000×626 | 5,00 s, 24 fps | 794 894 B | isto |
| `steam/steam-cup-b-seq/000.webp … 029.webp` | WebP q72, 30 kadrova | 1000×626 | | ~220 KB ukupno | isto |

Upotreba: `mix-blend-mode: screen` (ili `lighten`) na tamnoj pozadini, ivice su već utopljene u crno. Izvor je jedan klip, pa su A i B isti vazduh iz dva dela snimka (B se može okrenuti `scaleX(-1)`).

### Preuzeto pa odbačeno (fajlovi obrisani iz `izvori/`)

| Klip | Zašto |
|---|---|
| Pexels 9694807, cottonbro studio, „Footage of smoke against black background" (1920×1080, 25 fps, 39 s) | gust dim koji ispunjava ceo kadar, nije para iznad šolje; posle `screen` izgleda kao magla u pravougaoniku |
| Pexels 19036346, Liudmyla Shalimova, „A black background with smoke coming out of it" (1440×2560, 30 fps, 9 s) | gust stub dima, plav ton, od 5. s veliki beli oblak (nije petlja) |
| Pexels 855414, Pixabay, „Cup Of Coffee On Top Of Coffee Beans" (1920×1080, 25 fps, 10,6 s) | pozadina (bokeh) se pomera, pa posle oduzimanja ostaju fleke, a u isečku je i ivica šolje |

Na stranici Pexels 855414 licenca piše „Free" sa vezom na stranicu Creative Commons slika (nije proveravano dalje, klip nije upotrebljen).

## B. Fotografije (`KafaSkrol/public/media/photos/`)

Sve fotografije su preuzete 23.10.2026 ručno sa CDN-a (Unsplash `images.unsplash.com/<foto>?w=2400&q=85&fm=jpg`, Pexels `images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&w=2400`), bez Unsplash API-ja. Svaka je u svom folderu, magic bytes `ff d8 ff` (JPEG) provereni. Autor, naslov i datum su sa stranica fotografija (provera istraživača `fotografije.md`, 23.10.2026). Svaka fotografija je pregledana u punoj rezoluciji (pregled + pločice).

Izvedeni fajlovi: WebP kvalitet 78, ICC pretvoren u sRGB, kolor korekcija ka paleti tokena (tople bele, crno → `#1B150D`, belo → `#F4EEE4`, zelenilo prigušeno gde je bilo). Veličine kao u RealEstates: pejzaž `-sm` 828 / `-lg` 1920 px, uspravno `-sm` 480 / `-lg` 900 px.

| Mesto | Izvedeni fajlovi (`-sm`, `-lg`) | Izvor (ID iz `fotografije.md`) | Autor, stranica | Licenca | sha256 izvornog fajla | Isečak i napomena |
|---|---|---|---|---|---|---|
| Prodavnica, glavna | `shop-1` (480×600, 900×1125; 26 KB, 66 KB) | SHOP-1, `photo-1550608751-d38ee4dd799a`, 2400×3000 | Clint Bustrillos, [unsplash.com/photos/clear-glass-jar-filled-with-coffee-bean-lot-XgVHdER_fG4](https://unsplash.com/photos/clear-glass-jar-filled-with-coffee-bean-lot-XgVHdER_fG4) (2019) | Unsplash License, 23.10.2026 | `7123bb914fbe81955e1981d12b0ed5ef24498544f082b8c6f6f81f71bc311e95` | ceo kadar; tegle sa zrnima, bez natpisa, brenda i ljudi (proveren pun kadar) |
| Prodavnica, pozadina 1 | `shop-bg-1` (480×720, 900×1350; 17 KB, 41 KB) | ZRNA-2, `photo-1736813133035-6baf4762fd3d`, 2400×3600 | Cemrecan Yurtman, [unsplash.com/photos/a-pile-of-coffee-beans-on-a-white-background-G4RS0NGIS8I](https://unsplash.com/photos/a-pile-of-coffee-beans-on-a-white-background-G4RS0NGIS8I) (14.1.2025) | Unsplash License, 23.10.2026 | `f74c33e077cef9f53593ed7ace40cdade60a3c3612cabdb71dcf93482103ead5` | ceo kadar; pozadina podešena na krem `#E6DDCE` (ivice R 226–229, G 216–222, B 200–207), gomila zrna gore |
| Prodavnica, pozadina 2 | `shop-bg-2` (828×778, 1920×1805; 42 KB, 179 KB) | ZRNA-1, `photo-1587049016823-69ef9d68bd44`, 2400×2400 | Mockup Graphics, [unsplash.com/photos/brown-coffee-beans-on-white-surface-m7ijvnNGaV0](https://unsplash.com/photos/brown-coffee-beans-on-white-surface-m7ijvnNGaV0) (2020) | Unsplash License, 23.10.2026 | `7535bd027341ce6712fddbe4b3067a7f3acba44babb0ef213cc334ee9837544c` | gornjih 94 % (donji svetlosivi rub odsečen); pozadina na krem `#E6DDCE`; rasuta zrna odozgo |
| O nama | `onama-1` (828×806, 1920×1868; 116 KB, 367 KB) | ONAMA-1, `photo-1777383504831-d0f3c6e0486e`, 2400×3593 | Khanh Do, [unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-QrrFbQp085M](https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-QrrFbQp085M) (28.4.2026) | Unsplash License, 23.10.2026 | `98c9efd837577be942f38de4c22958d4e3b2e4fc9bb23b03761a60982a939fd5` | odozgo odsečeno 35 % (žuti stub koji je van palete); bubanj, zrna, mešalica, bez ljudi i natpisa |
| O nama | `onama-2` (828×552, 1920×1280; 43 KB, 120 KB) | ONAMA-2, `photo-1773118360501-00f979fd9322`, 2400×1600 | Ichsan Chairul, [unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-machine-iwcZmTKFo0w](https://unsplash.com/photos/freshly-roasted-coffee-beans-in-a-roaster-machine-iwcZmTKFo0w) (10.3.2026) | Unsplash License, 23.10.2026 | `346fe45305d62adc1b8381ba1467c95bc69057dac7ba72221b595057bbd2b8c9` | ceo kadar; horizontalan baner, bez ljudi i natpisa |
| Brew guide, korak 1 | `guide-1` (828×501, 1920×1162; 19 KB, 55 KB) | GUIDE-1, `photo-1753091122032-ddfb454849cc?w=4000`, 4000×2667 (Display P3 → sRGB) | User_Pascal, [unsplash.com/photos/coffee-beans-are-being-weighed-on-a-digital-scale-dZAb0Km1ELY](https://unsplash.com/photos/coffee-beans-are-being-weighed-on-a-digital-scale-dZAb0Km1ELY) (21.7.2025) | Unsplash License, 23.10.2026 | `e140d40805c1943405a051586df0c347657a21f29aa74d568d87b1d93a5e25e4` | isečak x 23–77 %, y 11–60 %: posuda sa zrnima na vagi. Odsečeni su natpis „normcore" na displeju vage, logo mlina gore desno i utisnuti natpis ispod posude. Preuzeto na `w=4000` da isečak ima ≥ 1920 px. |
| Brew guide, korak 2 | `guide-2` (828×745, 1776×1599; 29 KB, 218 KB) | GUIDE-2, `photo-1676600475896-dbf8ddd44f1d`, 2400×1599 | Jason An, [unsplash.com/photos/a-cup-of-coffee-sitting-on-top-of-a-scale-S9QYhiZ0tFE](https://unsplash.com/photos/a-cup-of-coffee-sitting-on-top-of-a-scale-S9QYhiZ0tFE) (2023) | Unsplash License, 23.10.2026 | `1de5f92235d43a46cbd8e9f0cbb38d1b7892cc3adbd773377658e4b3b46b0c0e` | zdesna 74 % kadra; levo odsečen mlin sa zlatnim znakom. Dripper, vaga (displej bez brenda), kašika. Na levom rubu ostaje mali deo srebrne drške mlina, bez natpisa. |
| Kontakt (**Symbolbild**) | `kontakt-1` (480×716, 900×1342; 36 KB, 86 KB) | **KONTAKT-2** (zamena za KONTAKT-1), Pexels 16862543, 2400×3578 | Anna Holodna, [pexels.com/photo/view-of-an-empty-cafe-patio-16862543](https://www.pexels.com/photo/view-of-an-empty-cafe-patio-16862543/) (17.5.2023, Beč), profil [pexels.com/@holodna](https://www.pexels.com/@holodna/) | Pexels License, 23.10.2026 | `bc1ff9b5309dd2018e38dae38fd65d2a55b5d3d68e06741ebe02b47b7d4c6fa4` | ceo kadar; dvorište bečkog kafića posle kiše, bez ljudi i čitljivih natpisa (na suncobranu je cedulja sa nečitljivim sitnim tekstom). **Uz sliku obavezno „Symbolbild" / „Symbolfoto"**: stvaran lokal, a naša adresa je izmišljena. |

### Pregledano pa odbačeno (fajlovi obrisani iz `izvori/`)

| Fotografija | Zašto |
|---|---|
| KONTAKT-1 (Unsplash, Sára Sedlmajerová, `photo-1765045038226-43d7cd5cfd29`) | u punoj rezoluciji se na menijima na stolovima čita natpis lokala („OBERLAA", stvaran bečki lanac), gost sa naočarima je delimično vidljiv u profilu, još troje ljudi u dubini, slika u ramu na zidu (umetničko delo koje licenca ne pokriva) |
| KONTAKT-6 (Unsplash, Keghan Crossland, `photo-1567880905822-56f8e06fe630`) | gost na visokoj stolici i drugo lice u odrazu prozora; lokacija nije potvrđena kao Beč |
| SHOP-2 (Unsplash, Zachary Delorenzo, `photo-1635304901720-898524afa099`) | donji deo ima limenke sa čitljivim etiketama čajeva (BAO ZHONG, MOONLIGHT JASMINE, USDA Organic); i posle isecanja gornjeg dela boje (hladno bela i zelenilo) se ne uklapaju u paletu ni posle korekcije; zamenjena slikom ZRNA-1 |
| GUIDE-1 u punom kadru | čitljiv natpis „normcore" na displeju vage i delimičan logo mlina; zato je ostao samo isečak iznad vage (vidi gore) |
| GUIDE-3 (ruka sa tetovažom, Chemex) | nije ni preuzet: ruka i tetovaža |

## Otvorena pitanja

- Fotografije nisu preuzete preko Unsplash API-ja, pa nije poslat `download_location` (vidi `fotografije.md`, uslov 1 i 2). Ako direktor želi da prati API pravilo, treba ga poslati za 7 Unsplash fotografija.
- Mixkit Terms zabranjuju masovno preuzimanje botovima. Preuzet je jedan fajl jednim `curl` pozivom na isti CDN link koji koristi dugme „Download", bez petlje.
- Kontakt fotografija je stvarno bečko dvorište. Pre objave proveriti sa direktorom da li je „Symbolbild" oznaka dovoljna.
