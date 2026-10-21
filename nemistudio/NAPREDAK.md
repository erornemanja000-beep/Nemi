# Nemi Studio: novi sajt (nemistudio.at)

Pregled uživo: https://erornemanja000-beep.github.io/Nemi/nemistudio/
(`?intro=0` preskače uvodni film, `?intro=1` ga uvek pušta, `?lang=en` engleski)

## v3: „sajt u sajtu u sajtu“
1. **Uvodni film** (23 s, montaža po uzoru na reel @ibanez_nick): oko → zenica se širi → istorija u brzim rezovima (−40.000 … 1991) → „Menschen wollen gesehen werden.“ → branše → „Die meisten Websites schweigen.“ → nemi. Desktop 16:9, telefon 9:16, DE i EN. Dugmad „Ton an“ i „Überspringen“, pušta se jednom po poseti.
2. **Početak**: laptop na stolu, zamućen, preko njega „Websites, in die man eintaucht.“ Skrol: kamera izoštri, pa uleti u ekran laptopa.
3. Na ekranu je **pravi sajt** (ne slika): kad ekran popuni prozor, to je sajt Café Mila i skroluje se dalje normalno.
4. Na kraju svakog sajta: novi uređaj sa sledećim sajtom na ekranu, opet zum unutra.
   - Café Mila (krem/espresso, Fraunces): karta sa cenama i slikom koja prati miš, galerija, recenzije, radno vreme, rezervacija.
   - Kanzlei Aurum (teget/zlato, Cormorant): brojke, rečenica koja se pali reč po reč, oblasti prava (harmonika), advokati, citat, koraci, forma.
   - Puls Studio (crno/limeta, Anton): ukrštene trake, raspored po danima, treneri, brojevi, cene.
   - Hotel Alba (lan/žalfija, Bodoni): traka za rezervaciju, sobe u lukovima, spa krug koji se otvara, doručak, lokacija.
5. **Povratni zum**: hotel je jedan od četiri prozora → „Vier Branchen. Vier Stimmen.“ → Leistungen, Ablauf, FAQ, Kontakt.
6. Stalna Nemi traka dole: koji je sajt na ekranu (01/04 …), pregled svih, DE/EN, „Projekt starten“.

Na telefonu su uređaji telefoni (na stolu, u ruci), pa se ekran poklapa sa uspravnim prikazom.

## Kako radi zum
`src/components/Portal.jsx`: hero sledećeg sajta se iscrta u veličini prozora i homografijom (matrix3d) smesti u ekran uređaja. Skrol pomera celu scenu drugom homografijom dok uglovi ekrana ne postanu uglovi prozora; tada je sajt ravan i oštar.
Ekrani su isečeni iz snimaka sa zelenim ekranom: `python3 tools/portals.py <folder-sa-mp4> <izlaz>` (daje .webp sa providnim ekranom i `portals.json` sa uglovima).

## Materijal (sve besplatno)
- Video: Mixkit (Mixkit Stock Video Free License). Hero: cafe 41858, law 23222, gym 52088, hotel 4196. Uređaji: 48285, 52076, 44737, 9584, 100069, 42621, 8839, 100079.
- Fotografije: Unsplash (preuzimanja zabeležena preko Unsplash API-ja), `public/img/`.
- Muzika u uvodu: Mixkit 543.
- Uvodni film: `python3 tools/intro_film.py <klipovi> <slike> <izlaz.mp4> [--format reel] [--lang en] --music <mp3>`.

## Pokretanje
```
npm install
npm run dev
npm run build && python3 build_pages.py <gh-pages-folder>
```

## Otvoreno
- Impressum/Datenschutz: fale ime, adresa, UID i hosting (označeno narandžasto na stranicama).
- Formular otvara e-mail program (mailto); kad se zna hosting, može pravo slanje (npr. Netlify Forms).
- Forme u koncept-sajtovima ne šalju ništa (piše „Konzept-Demo“).
- Sledeće branše (zanat, zubar, frizer, restoran): isti obrazac, novi uređaj + novi sajt.
- `noindex` je uključen dok je ovo pregled.
