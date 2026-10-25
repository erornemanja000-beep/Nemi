# Prompt: rekreacija analiziranog reel-a (struktura 1:1, sadržaj Nemi Studio)

Kopiraj sve ispod linije u novu Claude Code sesiju u repou `Nemi`.

---

Napravi video od 2:00 koji kadar po kadar prati strukturu, ritam, prelaze i efekte reel-a koji smo analizirali
(Instagram, @miftahul_islam_efaz, 15. 10. 2026, 1280×720, 30 fps, 119,96 s, 65 rezova). Sadržaj je naš:
tekst, likovi i brend su Nemi Studio. Pravilo iz CLAUDE.md: od reference uzimamo princip, ne kopiju. Zato
nema njegovog imena, njegovih likova (detektiv sa šeširom), njegovog teksta, Instagram profila ni tuđih logoa.

## Pravila
- Prati CLAUDE.md: `planer` deli posao u talase, `programer`/`animator`/`mediji` rade svako na svojim fajlovima, na kraju `tester`, `recenzent` i `bezbednost`. Commit i push posle svakog talasa.
- Činjenice o Nemi Studio samo iz `studio/nemi-reklama/brief.md`. Nema izmišljenih brojeva (klijenti, „viral", „top tržišta").
- Novi npm paket ili program: prvo `bezbednost`. Blender 5.2.3 LTS je već odobren: skini `blender-5.2.3-linux-x64.tar.xz` sa download.blender.org/release/Blender5.2/, proveri SHA-256 iz `blender-5.2.3.sha256`, raspakuj u scratchpad. Ovde nema GPU-a: koristi Cycles na CPU, a EEVEE ne radi.
- Plaćene stvari (Artlist slike, video, glas i muzika): prvo `get_generation_cost`, pa me pitaj pre generisanja.
- Tekst na ekranu je na nemačkom, sa „du" obraćanjem, kao na nemistudio.at.

## Tehnika
- Remotion u `motion/` (već instaliran, 4.0.538, pravila u `motion/README.md`). Nova kompozicija `Reel`: 1920×1080, 30 fps, 3600 kadrova. Svaka scena je svoj fajl `motion/src/reel/S01_….tsx`, a `Reel.tsx` ih slaže po vremenima iz tabele.
- Ponovo koristi `motion/src/wuerfel/delovi.tsx`: `Iskace` (tekst reč po reč), `Mozaik` (pikselni prelaz), `GlitchSlika`, `Kocka3D`, `Lik`. Proširi ih, ne pravi duplikate.
- Voksel sobe se prave kao `motion/wuerfelwelt/voxel_welt.py` (Python → `.vox` za MagicaVoxel + Blender skripta → PNG kadrovi u `motion/public/reel/<scena>/`).
- Da bi render bio izvodljiv bez GPU-a, Blender renderuje samo kadrove gde se kamera stvarno kreće kroz 3D. Gde se kamera samo blago pomera, renderuj 1 do 3 sloja kao statične PNG slike (pozadina, likovi, prednji plan), pa ih u Remotion-u pomeraj kao 2,5D paralaksu sa DOF zamućenjem. Pregledni renderi idu na 50 %, finalni na 100 %.
- Pikselni likovi se crtaju kao `motion/wuerfelwelt/lik.py` (PIL, sprite sheet za Pixelorama).
- Fotografije i ilustracije (svemir, sunce, mesec, mutni sto, kafić, oblaci): prvo Unsplash konektor (B&W svemir, sunce, mesec, mutna radna soba; čuvaj autora za potpis), a za ilustracije Artlist `generate_image` posle odobrenja. Tunel od oblaka može i kao Blender volumetrija.
- Zvuk: ffmpeg sinteza kao u `motion/sfx.sh` (whoosh, pop, tick, glitch, hit, chime, kucanje tastature). Muzika: Artlist `search_music` (synthwave/arcade, oko 128 BPM). Ako preuzimanje ne prođe, koristi sintetizovani ritam. Glas (po želji): Artlist `generate_voiceover` na nemačkom, tekst = tekst na ekranu, posle odobrenja cene.

## Vizuelni jezik (važi za ceo video)
- **Boje:** ink `#0b0b0c`, bone `#efeae2`, signal narandžasta `#ff5a24`, tamnocrvena `#8f1512` za pozadine, tirkizna `#3fd6c6` za cifre i kod, zlatna `#f2c14e` za upitnike i sjaj.
- **Fontovi:** Inter Display 800–900 i Inter 300 (zamena za Geist), Instrument Serif kurziv za istaknute reči (`motion/public/fonts/`), JetBrains Mono za oznake, kod i brojače. Za krupne reči uzmi usku, debelu varijantu (Inter Display Black sa `font-stretch` ili skalom 0,85 po širini).
- **Tekst u ritmu:** svaka reč ulazi na osminu takta (oko 7–8 kadrova). Obične reči su tanke i bele, ključna reč je krupna, crvena ili narandžasta i velikim slovima, a jedna reč u rečenici ide u serif kurzivu. Ulaz: rotateX 80° → 0, scale 1,4 → 1, blur 8 → 0, sa oprugom. Izlaz: blur i nestajanje za 6–8 kadrova. Ključne reči imaju RGB glitch 4–6 kadrova. Pre nekih reči 3–5 kadrova trepere cifre („0110", „101") pa se pretvore u reč (scramble). Tekst se mestimično kuca slovo po slovo, sa kursorom i crvenim blokom označavanja.
- **Prelazi (ovim redom se ponavljaju):** pikselni mozaik od crvenih, belih i crnih kvadrata (najčešći, oko 10 puta); beli blesak 2–4 kadra; zamućenje u pokretu (whip); RGB glitch sa pomerenim trakama; zum kroz ekran monitora u sledeću scenu; beli „portal" koji se otvori iz centra.
- **Likovi (naši, originalni):**
  - **Nemi:** pikselni lik, tamna kapa i krem šal preko usta, jer je „stumm". Animacije: stoji, pokazuje, maše, ruke gore, raspadne se u piksele i ponovo sastavi.
  - **Kocko:** narandžasta voksel kocka sa nožicama i malim šeširom, pomoćnik („Werkstatt").
  - Oba imaju senku na podu, blago se njišu na mestu i trepću.
- **Prostori:** voksel soba sa crvenim okruglim tepihom, policama, ekranima na zidu i biljkom u saksiji; voksel radni sto (pogled odozgo i spreda: monitor, lampa, tastatura, stolica); voksel biblioteka sa toplim lampicama; tamni pod sa tirkiznom mrežom (Tron); crno-beli svemir. Uvek blaga dubinska oštrina (DOF) i spori pomak kamere.
- **Zvuk:** svaki pokret ima svoj zvuk. Tekst = pop ili tick, prelaz = whoosh, glitch = digitalni šum, kucanje = klik tastera, brojač = brzi tikovi, ključna reč = udarac. Rez uvek pada na udarac muzike.

## Scene (vremena prate original, sekunde)

| # | Vreme | Šta se vidi | Tekst na ekranu (naš) | Prelaz na kraju |
|---|---|---|---|---|
| 1 | 0,0–2,75 | Prvi kadar je kratak blesak sa izokrenutim bojama. Zatim radni sto sa monitorom i lampom na zelenom brdu pod oblacima (ilustracija), a na monitoru nemistudio.at. Kamera ulazi u ekran, sajt se skroluje i kursor klikne. | „Dieses Video" / „wurde nie" / **GEFILMT.** (krupno, crveno, nakošeno 3D, kursor ga klikne) | zum u ekran, pa pikselni mozaik u narandžasto |
| 2 | 2,75–7,75 | Narandžasti gradijent. Nemi skakuće, raspada se u piksele i sastavlja, gleda kroz lupu. Zlatni upitnici iskaču. | „Alle fragen" / „dasselbe:" (krupno) / „Welches *Programm*?" → na crvenoj pozadini **FALSCHE FRAGE.**, „Programm?" precrtano crvenom linijom i zaokruženo | beli blesak, pa whip |
| 3 | 8,0–11,0 | Crna scena, iza mutan sto u crvenom svetlu, tanak crveni krug. Tekst se kuca. Oko teksta iskaču nalepnice (🔥 ❤️ 🎬 ✨ 💬) i crvene iskre. | „Weil das kein Programm allein macht." → „Nicht *allein*." u isprekidanim crvenim zagradama | rez |
| 4 | 11,0–13,2 | Mutna fotografija radne sobe (topli bokeh). Kocko ulazi i drži lupu. | „Ein Klick auf" / „*cooles*" / **VIDEO** (glitch) | rez na crno |
| 5 | 13,25–15,0 | Crno. Traka od generičkih šablon-sličica leti u 3D luku preko ekrana. | „UND DU BEKOMMST" / **BAUKASTEN.** | pikselni mozaik |
| 6 | 15,0–18,75 | Voksel biblioteka. Nemi u krupnom planu: prvo crvena silueta, pa se pojavi. Ikonica klapne. | „Der *Unterschied*?" / „Eine" / **REGIE.** / „Sein Name:" / **NEMI.** | rez |
| 7 | 18,75–22,0 | Voksel sto odozgo, kamera se spušta u pogled spreda. Na monitoru se kuca fajl `nemi-regeln.md` (u levom panelu folderi `refs`, `sfx`, `fonts`): „# So bauen wir Websites / 1. Erst die Geschichte, dann der Stil / 2. Jede Bewegung hat einen Grund / 3. Zuerst fürs Handy / 4. Schnell laden / 5. Jedes Detail zweimal prüfen / > Gefühl: ohne Worte." | „Und er hat seine" / „*Regeln*" / „aufgeschrieben." | pikselni mozaik |
| 8 | 22,25–24,5 | Isti sto. Na monitoru je neutralni čet (bez tuđih logoa): poruka „Mach ein Video, das man spürt" i prikačen `nemi-regeln.md`, pa odgovor „Lese deine Regeln…". Nemi i Kocko iskoče pored stola. | „Gleiche" / „*Werkzeuge*," / „andere" / **REGIE.** | beli blesak |
| 9 | 24,75–28,0 | Isti sto iza stolice. Na monitoru je ovaj isti video (rekurzija, pa pikselni zum). Ikonica zvučnika. | kucano: „Und dieses Video, das du gerade siehst?" / krupno 3D: „*gerade* jetzt?" / „Gemacht mit genau" / na podu u perspektivi: **diesen Regeln,** | pikselni mozaik |
| 10 | 28,5–32,0 | Nemi u krupnom planu u biblioteci. Traka nivoa od 12 polja puni se do „MAX". | „Das heißt:" / „auch *deine* Website" / „kann sich" / **SO ANFÜHLEN.** | beli fade |
| 11 | 32,5–35,0 | Ilustracija: topao kafić noću, ljudi za laptopima, grad kroz prozore. Kamera se lagano približava. | „Das erste Gespräch:" / brojač 0 → **30** „Minuten" / „*kostenlos*." | rez na crno |
| 12 | 35,25–37,75 | Crno. Lebde kartice video-plejera (`dieses_video.mp4`) sa prethodnim scenama i skrol trakom. | „Und dieses Video?" / „Ist schon der" / **BEWEIS.** (crveni sjaj) | whip |
| 13 | 38,0–39,75 | Tunel od oblaka sa plavom svetlošću. Kocko leti kroz njega, lupa svetli. | „Also:" / **LOS GEHT'S.** (zlatni 3D sjaj) | beli portal iz centra |
| 14 | 40,0–46,0 | Crno-beli svemir: galaksija, pa površina sunca izbliza. Polje za unos teksta, kuca se poruka, klik na strelicu (beli prasak), pa talas čestica. Na kraju se mesec slaže od tačaka. | kucano: „Aber zuerst," / „eine Sache musst du sehen." / „→ Denn ohne sie" / „funktioniert *nichts* davon." | rez |
| 15 | 46,0–52,25 | Voksel soba sa crvenim tepihom: Nemi i Kocko, holografska oznaka „ZAUBERKNOPF" lebdi. Zatim crvena knjiga „BAUKASTEN €€€" na postolju. Oznake sa linijama: „NEMI / REGIE", „KOCKO / WERKSTATT". Pre reči trepere cifre. | „Es gibt keinen" / **ZAUBERKNOPF.** / „Gab es *nie*." / „Und" / **NEIN,** / „wir verkaufen dir" / „keinen *Baukasten*." | pikselni mozaik |
| 16 | 52,75–55,25 | Tamni pod sa mrežom. Rastu tamnotirkizni stubovi, Nemi stoji na najvišem crvenom stubu koji raste. | „Wir bauen" / „von *Grund auf*." / **OHNE VORLAGE.** | pikselni mozaik |
| 17 | 55,75–62,25 | Crveni tepih. Lebdi dokument (pergament sa crvenom trakom), pa sleti na postolje. | „Du bekommst" / **ETWAS BESSERES.** / „Ein Angebot mit" / „*Fixpreis*." / „Und ehrlich: nicht nur" / ~~WEBSITE~~ / „ein ganzes *Gefühl*." | rez |
| 18 | 62,5–70,0 | Crno sa mrežom. Kocko u centru. Brojač 100 → **0** „versteckte Kosten". Iskaču ikonice čula: nos, ruka, oko, uvo i sijalica. | „Denn das Gefühl" / **IST** / „die Website." / „Websites," / „die man *spürt*." | pikselni mozaik |
| 19 | 70,5–80,0 | Voksel soba. Nemi hoda, a za njim se isprekidanom linijom nižu ikonice: Text, Fotos, Video, Animation, Sprachen, Google, Hosting. Zatim se sve slože u telefon. | „Kein Baukasten," / „ein ganzes" / **TEAM** / „in *einem* Studio." | pikselni mozaik |
| 20 | 80,75–82,25 | Crno. Kocko maše. | „Und das sagt dir" / **KEINER:** (scramble cifara) | rez |
| 21 | 82,5–88,75 | Voksel kancelarija: monitor sa kodom (`seite_v1.tsx` … `v6`, brojevi linija 2500+, linije kao obojene trake). | „Für jede Seite" / „machen wir" / **ALLES** / „selbst." / „Jedes" / **SYSTEM.** / „Jede" / **REGEL.** / „Jeden" / **FEINSCHLIFF.** (ikonica ključa) | rez |
| 22 | 89,0–91,0 | Mreža. Kartice „Vorschau v1…v6" se šire u lepezu. | „Über einen Vorschau-Link" / „siehst du *jeden* Schritt." | pikselni mozaik |
| 23 | 91,25–96,0 | Voksel sto. Na monitoru tajmlajn (`startseite_v6`: intro / übergang / ende, „whoosh −6 dB"), a izmene se vide uživo. | „Diesen" / **ÜBERGANG** / „schärfen." / „Das Bild" / **HELLER.** / „Den Text einen Takt" / **LÄNGER.** | rez |
| 24 | 96,25–99,0 | Crveni tepih, Nemi drži dokument. | „Und all das" / „passiert" / **FÜR DICH.** | crveni pikselni mozaik |
| 25 | 99,25–108,0 | Mreža. Tirkizni okvir se puni sa 4 trake (crvena, bela, tirkizna, žuta). Procenti rastu 22 → 54 → 71 → 100 %. Krupni plan: Nemi pokazuje u kameru. Ikonice sijalica, srce i beleška. | „Das Studio" / „macht den *Rest*." / „Was es braucht?" / **DICH.** / „Dein *Wissen*." / „Deine *Idee*." / „Dein *Gefühl*." | glitch |
| 26 | 108,75–111,0 | Crveni tepih, Nemi i Kocko. | „Wir machen" / „die *harte* Arbeit," / „damit du es nicht musst." | rez |
| 27 | 111,25–120,0 | Završna kartica preko mutne sobe, Nemi pokazuje na nju. Oznaka „WEITER ZU TEIL 2". | **Schreib uns** / polje u koje se kuca „ERSTGESPRÄCH" / „30 Min · kostenlos" / pa kartica „nemistudio.at · Fixpreis-Angebot" sa strelicom nadole | kraj, loop na kadar 1 |

## Redosled rada
1. `planer`: talasi i podela fajlova po scenama. Likovi i sobe idu prvi, jer ih koriste mnoge scene.
2. Talas 1: likovi (`lik.py` za Nemi i Kocko), voksel sobe (`.vox`), Blender skripte, zvukovi, fotografije i ilustracije (posle odobrenja).
3. Talas 2: scene 1–9. Talas 3: scene 10–18. Talas 4: scene 19–27. Svaku scenu prvo renderuj na 50 % i pošalji mi kontakt-sheet (4 kadra u sekundi) pre finalnog rendera.
4. Finalni render na 1920×1080, pa po želji verzija 1080×1920 za Reels i TikTok (tekst u bezbednim zonama).
5. `tester`, `recenzent` i `bezbednost`, pa commit i push.
