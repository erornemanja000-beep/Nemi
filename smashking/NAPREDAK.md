# Smash King: novi sajt (beleška o napretku)

Klijent: Smash King, Viktor-Adler-Markt 53/54, 1100 Wien (Sezai Özyer e.U.).
Stari sajt: smash-king-burger.at · Instagram: @smashking_burger.
Princip: kao reel „CHAR & CO.“ (kebab koji se na skrol rastavlja i slaže), samo za smash burger i bolje.

## Šta sajt radi (redom)
1. **Smash** (`#smash`): ruka u crnoj rukavici presom spljošti meso na ploči, skrolom se vrti 121 kadar.
   Reč „SMASH!“ se spljošti tačno u trenutku udara (oko 35 % skrola), pozlati se, ekran se strese, lete varnice.
2. **King** (`#king`): eksplodirani burger sa oznakama sastojaka → slaže se → kruna pada na burger (196 kadrova).
3. **Karte**: 7 burgera (lista + velika slika na kompjuteru, karusel kartica na telefonu), deal-ovi, Fries,
   Fingerfood, Pinsa & Pasta, Süßes/Soßen/Getränke. Bez cena (dogovor), napomena da su cene u lokalu i na platformama.
4. **Versprechen**: 100 % Rind, Buns, Saucen, Halal.
5. **Besuch**: adresa, U1 Keplerplatz, radno vreme sa „otvoreno sada“ (bečko vreme), mapa tek na klik (DSGVO),
   Wolt / Lieferando / foodora.
6. Instagram, footer sa WebGL vatrom (prema „Shader Fire“ sa 21st.dev), Impressum & Datenschutz.
   Dugme „Bestellen“ otvara izbor: Wolt, Lieferando, foodora, poziv, ruta. DE podrazumevano, EN dugmetom.

## Fajlovi
| Putanja | Šta je |
|---|---|
| `src/index.html`, `src/impressum.html` | stranice |
| `src/assets/sk.css`, `src/assets/sk.js` | izgled i sva animacija (bez biblioteka) |
| `src/assets/seq/smash`, `src/assets/seq/king` | WebP kadrovi, `d` = kompjuter, `m` = telefon |
| `src/assets/img/menu/*` | tamne studijske fotke jela (AI, napravljene iz njihovih Wolt fotki) |
| `src/assets/img/` | logo (njihov), wordmark u krem boji, enterijer i terasa (njihove fotke), dim (Unsplash) |
| `izvor/` | AI klipovi i ključne slike u punoj veličini |
| `netlify.toml` | Netlify projekat sa „Base directory“ = `smashking`, objavljuje `src` |

## Kako se kadrovi prave ponovo
```
python3 scripts/smashking/frames.py smash smashking/izvor/smash.mp4 smashking/src/assets/seq/smash
python3 scripts/smashking/frames.py king  smashking/izvor/slaganje.mp4 smashking/izvor/kruna.mp4 smashking/src/assets/seq/king
```

## AI (Artlist, Kling 3.0 + Nano Banana Pro)
Smash (8 s, 1080p), slaganje (8 s, 1:1, početni = eksplozija, krajnji = gotov burger),
kruna (5 s, 1:1, početni = gotov burger, krajnji = burger sa krunom), 7 burgera + 3 kategorije.
Prva verzija smash klipa imala je sivu polugu iznad prese, zamenjena je verzijom sa rukom.

## Linkovi
- Pregled (claude.ai Artifact, privatno, deli se preko Share): https://claude.ai/artifact/CAx6Fp8aYaWViyXgvx1fUv
  Pravi se sa `python3 smashking/build_artifact.py <folder>` (King samo u jednom skupu kadrova, mapa kao link).
- Netlify projekat `smashking-entwurf` napravljen, objava odbijena: „account credit usage exceeded“.
  Kad se krediti obnove: Base directory `smashking`, publish `src` (vidi `netlify.toml`).
- Figma (9 ekrana + stil): https://www.figma.com/design/FBLu10uyr2iMg8G1QmI2QF
- Canva prezentacija za klijenta (DE): https://canva.link/z0ozech46fvkv9w
- Artlist: potrošeno oko 5.460 kredita (6 slika, 4 videa, 10 fotki jela).

## Proveriti sa klijentom
- **Radno vreme**: na starom sajtu tri verzije (Mo–Sa 11:30–21 / So –23; Mo–Sa –23 / So –21; schema 9–17).
  Trenutno: Mo–Sa 11:30–23:00, So 11:30–21:00 (`HOURS` u `sk.js` + tekst u `index.html`).
- **Halal**: istaknuto po njihovim #halal objavama; potvrditi da važi za sve meso.
- **Schüler-Deal** (Hamburger + Pommes + Eistee): da li još važi i po kojoj ceni.
- **Cene**: namerno nisu na sajtu; Wolt cene (npr. Cheeseburger 11 €) su cene dostave.
- **Impressum**: broj u Firmenbuch-u (na starom sajtu „FNXXXXX“), telefon (01 6067467, u starom Impressumu piše 6057467).
- Fotke jela su AI prikazi njihovih burgera; za finalnu verziju po želji prave fotke.
