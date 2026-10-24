# Grillbox: koncept-sajt (beleška o napretku)

Lokal: Grillbox, Simmeringer Hauptstraße 68–74 / Top GL1, 1110 Wien. Ćevapi, Pljeskavica, Hot Dog, Smash Burger.
Halal (oznaka „حلال BE HALAL!“ na njihovom logou), „est. 2025“, slogan „Fresh. Hot. Grilled!“.
Izvor podataka: njihova Wolt stranica (https://wolt.com/de/aut/vienna/restaurant/grillbox-simmering), viđeno 24. 10. 2026.
Postoje i na Lieferando-u (https://www.lieferando.at/speisekarte/grillbox-smash-burger-hot-dogs-cevape),
ali Lieferando blokira automatsko čitanje (403), pa odatle ništa nije preuzeto. Sopstveni sajt i Instagram nisu nađeni.

## Princip
Isti sajt kao Smash King (grana `gh-pages`, folder `smashking/`, najnovija verzija sa menijem koji stoji
i menja burger po burger na skrol). Dizajn, fontovi, boje, animacije i kod su isti. Promenjeno je:
- **Brend**: ime Grillbox, njihov logo (isečen u krug) umesto krune, „GRILLBOX“ kao tekst (Anton) umesto wordmark slike,
  ✦ umesto ♛ u meniju i karticama.
- **Druga animacija** (`#king`): samo prvih 121 kadar (burger se složi), kadrovi 122–196 sa krunom su izbačeni.
  `data-count="121"`, `data-keys` i `--len:400` podešeni tako da slaganje traje isto kao ranije, a poslednje poglavlje
  („Fresh. Hot. Grilled!“) stoji preko gotovog burgera.
- **Karta**: 10 jela sa Wolt-a (Ćevapi 5/10, Pljeskavica, Pljeskavica Käse, Käsekrainer, Käsekrainer Bacon,
  Classic/Bacon/Chilly/Double Smash), pa „Was zum Trinken“ (6 pića) i „Extras“ (Kajmak, Ajvar, Chilly Soße).
  Alergeni su izbačeni jer ih Wolt ne navodi.
- **Besuch**: adresa, Wolt radno vreme, telefon sa Wolt-a, Wolt i Lieferando (bez foodore), mapa na novoj adresi.
- **Instagram blok** je postao „Grillbox auf Wolt“ + Lieferando + Google „Bewerte uns“.
- Impressum ima prazna mesta `[bitte ergänzen]` (firma, email, UID, FN).

## Fajlovi
| Putanja | Šta je |
|---|---|
| `src/index.html`, `src/impressum.html` | stranice |
| `src/assets/sk.css`, `src/assets/sk.js` | isti kod kao Smash King, uz izmene gore (radno vreme sa Ruhetag-om u `HOURS`) |
| `src/assets/seq/smash`, `src/assets/seq/king` | isti kadrovi kao Smash King (king samo 0001–0121) |
| `src/assets/img/menu/*` | njihove Wolt fotke bez pozadine, kvadrat 1000 i 560 px, providno |
| `src/assets/img/` | logo (`emblem`), favicon, `og.jpg`, `cevapi-tamno`, `hotdog-tamno`, `grill-tisch` (pokrivač mape), dim (Unsplash, iz Smash King-a) |
| `izvor/wolt/` | originalne Wolt fotke i logo |
| `izvor/bez-pozadine/` | iste fotke bez pozadine (Artlist, Pixelcut Background Removal, 6 × 30 = 180 kredita) |
| `build_pages.py` | kopira `src/` u `<gh-pages>/grillbox/` i dodaje noindex |

Slike se prave ponovo sa `python3 scripts/grillbox/slike.py`.
Na Wolt-u su neke fotke iste: Ćevapi 5 i 10, obe Pljeskavice (i obična pokazuje fotku sa sirom), oba hot doga,
Classic i Chilly Smash. Sajt zato koristi 6 fotki za 10 jela; nove fotke od klijenta bi to rešile.
`og:image` je apsolutni link na GitHub Pages; pri pravoj objavi promeniti na pravi domen.

## Objava (GitHub Pages)
**Link za klijenta: https://erornemanja000-beep.github.io/Nemi/grillbox/**
```
git fetch origin gh-pages
git worktree add ../gh-pages gh-pages
python3 grillbox/build_pages.py ../gh-pages
cd ../gh-pages && git add grillbox && git commit -m "Grillbox: ..." && git push origin gh-pages
```
GitHub objavi za 1–2 minuta. Koren grane (`index.html`) i dalje vodi na Smash King.

## Proveriti sa klijentom
- **Cene** su sa Wolt-a (Classic Smash € 18,90 … Double € 21,90). Cene u lokalu su verovatno niže; ako daju kartu, zameniti.
  Napomena na sajtu je samo „Alle Preise in Euro inkl. MwSt.“
- **Radno vreme**: Wolt „Lieferzeiten“ (Mo Ruhetag, Di–So 11:00–22:00). Potvrditi da važi i za lokal (`HOURS` u `sk.js` + tekst u `index.html` i footeru).
- **Telefon** +43 665 67145295 je sa Wolt-a; potvrditi da je za goste.
- **Halal**: na logou piše „BE HALAL!“; potvrditi da važi i za Bacon (Käsekrainer Bacon, Bacon Smash) i Käsekrainer.
- **Ćevapi**: na sajtu „im Fladenbrot mit Zwiebeln“ (vidi se na fotki, na Wolt-u to ne piše). Na Wolt-u piše „Cevape“, na logou „Cevapi“; sajt koristi „Ćevapi“.
- **Alergeni**: nema ih na Wolt-u; od klijenta tražiti listu (A–R) da se vrate kao kod Smash King-a.
- **Impressum**: firma, email, UID, broj u Firmenbuch-u i sud (ako je firma upisana).
- **Datenschutz → Hosting** sada opisuje GitHub Pages (nacrt). Pri pravoj objavi upisati stvarni hosting i osnov prenosa u SAD.
- **Fotke**: Wolt fotke na sivoj pozadini, isečene. Za finalnu verziju po želji tamne AI fotke kao kod Smash King-a
  (oko 160 kredita po slici na Artlist-u, krediti se obnavljaju 9. 11.) ili prave fotke.
- **Animacije** su i dalje burger iz Smash King AI klipova (brioche, bez susama). Grillbox burger ima zemičku sa susamom;
  ako klijent želi, novi AI klipovi po njihovom burgeru.
