# motion: video iz koda (Remotion)

Probni projekat za učenje: animacije se pišu u React-u, a Remotion ih renderuje u MP4.
Iste tehnike (tekst u ritmu, prelazi, brojači, glitch) posle idu na sajtove preko GSAP-a.

## Komande

```
cd motion
npm ci --ignore-scripts                          # instalacija tačnih verzija iz package-lock.json
npx --no-install remotion studio                 # pregled u browseru, sa tajmlajnom
npx --no-install remotion render Probni out/probni.mp4
```

Zvučni efekti u `public/sfx/` su napravljeni ffmpeg-om (`./sfx.sh`), ništa nije skinuto sa interneta.
U cloud okruženju render koristi postojeći Chromium (`remotion.config.ts`), a na računaru Remotion skida svoj Chrome.

## Šta je u probnom klipu (`src/`)

| Fajl | Tehnika |
|---|---|
| `scene/TekstURitmu.tsx` | reči ulaze na osminu takta, ključna reč pada iz 3D na udarac, blesak i trešenje |
| `scene/PikselniPrelaz.tsx` | ekran se pokrije kvadratima, rez je dok je sve pokriveno |
| `scene/Brojac.tsx` | brojač sa trakom nivoa i reč koja se dešifruje iz 0 i 1 |
| `scene/Glitch.tsx` | RGB split i pomerene trake |
| `Probni.tsx` | redosled scena, ritam (120 BPM, udarac na 15 kadrova) i zvuk |

## Bezbednost (pregled `bezbednost`, 25. 10. 2026)

Remotion 4.0.538 je odobren uz uslove. Ne pokretati:

- `npx create-video@latest` (instalira bez `--ignore-scripts`)
- `remotion upgrade` ni skill `remotion-upgrade`; nova verzija ide opet kroz `bezbednost`
- `npx remotion skills add` (uzima skill-ove sa najnovijeg commita i šalje telemetriju)
- `--license-key` (šalje podatke o upotrebi na remotion.pro)
- Studio na deljenoj mreži (sluša na svim adresama)

`npm audit` prijavljuje `zod` 4.5.4 (zagušenje memorije kad se proverava ogroman ulaz). Ostaje tako,
jer Remotion traži tačno tu verziju, a ovde zod proverava samo naše propse, ne tuđi ulaz.
Sa 4.6.6 render radi, ali Remotion upozorava na nesaglasne verzije.

Licenca: besplatno, i komercijalno, za jednu osobu ili firmu do 3 ljudi (računaju se i spoljni saradnici).
Od 4 ljudi treba Company License.

HyperFrames je odbijen za sada: telemetrija je podrazumevano uključena, sam se nadograđuje,
a njegov skill šalje zahteve korisnika na javni kanal. HeyGen konektor: ne.
