## Nemi hat das Wort
**U jednoj rečenici:** Pikselni lik Nemi stane pred mikrofon da progovori, ali je *stumm*: umesto glasa iz usta izađe oblačić koji govori sličicama, a jedina reč koju na kraju „kaže" je nemistudio.at.

**Potpisni trenutak:** Nemi širom otvori usta, zvuk potpuno nestane i reč *Wort* se slovo po slovo izbriše sa ekrana, a onda iz usta izađe oblačić koji se naduva u pravi sajt.

**Raspoloženje:** tiho · duhovito · pozorišno · ink `#0b0b0c` (soba), ink-2 `#121315` (mutan zid), bone `#efeae2` (bina, oblačić), bone-2 `#e4ddd2` (senke bine), signal `#ff5a24` (prsten mikrofona, ključna reč, srce). Svetlo: jedan tvrd reflektor odozgo kao na praznoj sceni, slabo narandžasto kontrasvetlo. Zvuk: prve 2,5 s bez muzike (samo sobni šum, „tok" po mikrofonu i udah, pa prava tišina), zatim otkucaj srca postaje bit od 120 BPM, bez melodije. Fontovi: Geist, Instrument Serif kurziv (ključna reč), Geist Mono (titlovi u zagradama, adresa).

**Tok (30 fps, udarac na 15 kadrova).** Sav tekst je u pojasu x 80–900 px i y 200–1500 px (dole 20 % i desnih 12 % su slobodni). Nemi stoji levo od sredine, a oblačić ne prelazi x 900. „nemistudio.at" stoji sitno (Mono) gore levo, ispod trake platforme, svih 10 s. Tako je adresa uvek na ekranu, a spoj petlje ostaje čist.

| s | Slika · kamera · prelaz | Tekst (DE) | Zvuk |
|---|---|---|---|
| 0–1 | Krupni plan: Nemi pred voksel mikrofonom, pikseli krupni kao kocke. Udahne i na 0,5 s širom otvori usta. | Od prvog kadra: „Nemi hat das *Wort*." Kad se usta otvore, *Wort* se briše unazad kao backspace i ostaje kursor. Titl: „[Stille]" | drugi „tok", udah, pa na 0,5 s tvrd rez u tišinu (jedini pokret bez zvuka, namerno) |
| 1–2,5 | Kamera se povlači i diže: mala voksel bina u mraku, reflektor, mutan zid. Iz usta iskoči oblačić sa tri tačkice kao „kuca…". | Reč po reč na udarac: „Nemi heißt auf Serbisch *stumm*." | tišina do 1,5 s, meko „pop", tri tiha tika |
| 2,5–5 | Umesto reči u oblačiću se na udarce poređaju ikonice: slika, strelice koje se vrte, srce koje kuca. Kamera polako prilazi. | Titl prevodi: „[Bild] [Bewegung] [Gefühl]" | Nemijev „glas" su zvuci ikonica: škljocaj, fijuk, otkucaj. Srce se ponavlja i prelazi u bit. |
| 5–7 | Oblačić se naduva u pikselnim koracima preko ekrana, a pikselni mozaik pokrije rez. Unutra je pravi snimak nemistudio.at na telefonu: skrol i otkrivanje teksta. | Gore: „Websites, die *ohne Worte* sprechen." | pun bit, fijuk, tik na svaki korak skrola |
| 7–9 | Oblačić se skupi nazad do Nemija na bini. Nemi pokaže na njega. | U oblačiću: „nemistudio.at". Gore: „Reden? *Gern.*" Titl: „Erstgespräch · 30 Min. · kostenlos" | bit stane, udarac kad adresa padne, mali tres |
| 9–10 | Tekst se raspadne u piksele, oblačić se uvuče u usta, kamera se vrati u krupni plan, Nemi kucne mikrofon. Poslednji kadar je isti kao prvi. | na 9,7 s ponovo „Nemi hat das *Wort*." | sobni šum, prvi „tok", pa petlja |

**Materijal po programu (početnik, ukupno ≈ 7,5 h):**
- **MagicaVoxel (≈ 1 h):** samo tri modela. Bina 48×32×6 voksela (bone, narandžasta ivica), mikrofon na stalku i zadnji zid sa tri rampa-svetla. Izvoz u OBJ.
- **Pixelorama (≈ 2 h):** Nemi 32×48 px u 11 kadrova: stoji 2, kucka 2, udah 3, otvorena usta 1, zatvara 1, pokazuje 2. Oblačić sa repom: „pop" u 3 kadra i tačkice u 6. Tri ikonice 24×24 (slika 1, strelice 4, srce 2). Paleta je samo 5 boja brenda.
- **Blender (≈ 2 h):** uvoz OBJ, tekstura „Closest" da pikseli ostanu oštri. Nemi je ravan sa sekvencom slika na bini, uvek okrenut kameri. Jedan reflektor i kontrasvetlo, mutan je samo zid. Kamera ima 4 ključa: krupno → široko, prilaženje, mir, široko → krupno. EEVEE, 1080×1920, 300 kadrova, oko 15 min rendera.
- **Remotion (≈ 2,5 h):** Blender render je podloga. Preko njega idu oblačić, ikonice i adresa kao pikselizovani PNG. Za tekst se koriste `TekstURitmu` i `PikselniPrelaz`, uz brisanje reči i naduvavanje u koracima. Snimak ekrana sajta na 390 px traje oko 15 min. Zvuk: postojeći beat, whoosh, tick i hit, plus tri nova napravljena ffmpeg-om kao u `sfx.sh` (tok mikrofona, škljocaj, srce), ništa skinuto. Fontovi idu lokalno; ako ih nema u repou, prvo `bezbednost`.

**Rizik i kako ga izbeći:** ko gleda bez zvuka ne čuje tišinu, pa gag može da prođe nezapaženo. Zato tišina mora da se vidi. Brisanje reči *Wort* i titl „[Stille]" padaju tačno na otvorena usta, a prazan oblačić sa tačkicama stoji bar 1 s. Pre objave 3–5 ljudi pogleda prve 2 s na telefonu bez zvuka i kaže šta je videlo. Sa zvukom tišina je prava digitalna tišina, ali najviše 1 s, da ne liči na grešku.

**Zašto baš Nemi:** ime znači „stumm", a sajt kaže „Websites, die ohne Worte sprechen: mit Bild, Bewegung und Gefühl". Reklama to izvodi doslovno: slika, pokret i srce su rečenica, a sajt je dokaz. Sve tvrdnje su iz brief-a; tačne reči za „Erstgespräch… kostenlos" `tekstopisac` usklađuje sa sajtom. EN: „Nemi has the *floor*." (briše se *floor*).

**Inspiracija (princip, ne kopija):**
- Analizirani reel iz brief-a (Instagram, 15. 10. 2026): reč po reč na udarac, pikselni mozaik, voksel soba sa mutnom pozadinom, pikselni vodič.
- ITV „Silent Ad Break", [ScreenVoice/egta](https://www.screenvoice.cz/en/case-studies-en/when-silence-speaks-louder/) (case study 22. 2. 2026, datum emitovanja nije naveden): tišina kao događaj, a povratak zvuka kao otkrovenje. Kod nas srce prelazi u bit.
- FCB Chicago „Caption with Intention", Grand Prix Design i Digital Craft ([Cannes Lions](https://www.canneslions.com/news/cannes-lions-announces-2025-winners-across-entertainment-and-craft-tracks), [Reel Chicago](https://reelchicago.com/article/cannes-lions-fcb-chicago-wins-two-grand-prix-awards/), jun 2025, stariji od 12 meseci, druga branša): titl nosi zvuk i ton. Odatle titlovi u zagradama kao Nemijev glas.
- Amanita Design, druga branša (igre). [Gematsu, april 2026](https://www.gematsu.com/2026/04/phonopolis-launches-may-20) potvrđuje da su njihove ranije igre počivale na neverbalnoj komunikaciji. Odatle princip rečenice od sličica u oblačiću (rebus). Da su to bile sličice u oblačićima je opšte znanje, ne iz tog izvora.
