# clipper: uspravni klipovi streamera (TikTok, Shorts)

Pravi klipove 1080×1920 u split-screen formatu: **gore** pozadina koja drži pažnju (naša animacija iz
`motion/` ili snimak igre), **dole** isečak streamera. Na vrhu je udica (naslov), na spoju polovina su
titlovi koji se smenjuju po 2–3 reči, a reč koja se upravo izgovara je žuta. Zvuk je samo od streamera,
izjednačen na -14 LUFS (nivo za TikTok i Shorts).

Cilj do 19. 11. 2026 (izlazak GTA 6): nalog sa 10.000 pratilaca i 100.000 pregleda u 30 dana, da se
posle prijavi u TikTok Creator Rewards. Od 19. 11. isto se radi sa live streamova.

## Alati

| Fajl | Šta radi |
|---|---|
| `split.py` | od jednog isečka pravi gotov klip (ili PNG za brzu proveru rasporeda) |
| `momenti.py` | u dugom videu nalazi najglasnije trenutke (vrisak, smeh, galama) i predlaže isečke |
| `alati.py` | zajedničke funkcije: vreme, ffprobe, čitanje SRT/VTT titlova (i YouTube vremena po reči) |
| `pozadine/` | naše originalne pozadine (render iz `motion/`, kompozicija `Pozadina`) |
| `fontovi/` | Inter Black i Bold (OFL licenca, `LICENSE-Inter.txt`) |
| `BEZBEDNOST.md` | pregled alata za preuzimanje, transkript i snimanje live-a |
| `ulaz/`, `izlaz/` | izvorni videi i gotovi klipovi (ne idu u git) |

Treba samo Python 3.10+ i ffmpeg. Za preuzimanje i transkript (yt-dlp, Whisper) prvo pročitati
`BEZBEDNOST.md`.

## Kako se radi

```
# 1) nađi trenutke u dugom videu (reakcija, intro, stream)
python3 clipper/momenti.py clipper/ulaz/speed_reakcija.mp4 --duzina 45 --broj 8

# 2) brza provera rasporeda (PNG), pa pravi klip
python3 clipper/split.py --dole clipper/ulaz/speed_reakcija.mp4 --od 12:04 --do 12:49 \
    --naslov "Speed prvi put vidi GTA 6" --autor "@IShowSpeed" \
    --titlovi clipper/ulaz/speed_reakcija.en.vtt --traka --slika 3 --izlaz clipper/izlaz/proba.png
python3 clipper/split.py ...iste opcije bez --slika... --izlaz clipper/izlaz/speed_gta6_01.mp4

# ili sve odjednom (bez naslova, za pregled)
python3 clipper/momenti.py clipper/ulaz/speed.mp4 --napravi clipper/izlaz/speed --autor "@IShowSpeed"
```

Važne opcije za `split.py`:

- `--fokus 0.3`: kad se 16:9 seče na polovinu ekrana, pomera kadar ulevo (0) ili udesno (1), da lice ostane u kadru.
- `--isecak 0.72:0.05:0.26:0.3`: uzima samo deo izvora (x:y:širina:visina u delovima kadra), npr. kameru streamera u uglu igre.
- `--kadar ceo`: ceo kadar bez sečenja, na zamućenoj pozadini (dobro za široke scene).
- `--zamena`: streamer gore, pozadina dole.
- `--gore video.mp4 --gore-od 1:10`: tačno određena pozadina; bez toga se bira nasumično iz `pozadine/`.

## Da klip bude „naš" (TikTok i YouTube to proveravaju)

Samo prebačen isečak sa malom izmenom TikTok vodi kao neoriginalni sadržaj: lošije se širi i ne plaća se
u Creator Rewards. Zato svaki klip dobija bar dve od ovih stvari:

1. sopstvena udica na vrhu (ne naslov iz originalnog videa);
2. naša pozadina gore (ne tuđ Subway Surfers ili Minecraft snimak);
3. titlovi i montaža (rez na vrhunac, bez praznog hoda);
4. poređenje ili rang („3 streamera reaguju na isti trenutak", „Speed vs Kai");
5. naš komentar (tekst ili glas) koji objašnjava ili ocenjuje trenutak.

Rizik: autor može da prijavi klip zbog autorskih prava, a posle više prijava nalog se gasi. Zato su
isečci kratki, uvek je naveden autor (`--autor`), a prednost imaju streameri koji traže klipere
(kampanje na Whop Content Rewards i slično; tu je dozvola i plaćanje po pregledu).

Creator Rewards plaća samo videe duže od 1 minuta. Za rast su dobri klipovi od 30 do 60 s, a posle
prijema u program prave se verzije od 61 do 75 s.

## Sledeće

- Transkript sa vremenom po reči (Whisper), pa Claude iz transkripta bira trenutke i piše udice.
- Od 19. 11.: snimanje live-a (Twitch i YouTube) u delovima, merenje brzine chata (najbolji znak
  viralnog trenutka), klipovi 10–20 minuta posle trenutka.
- Pozadina od našeg GTA 6 snimka, ako postoji konzola.
