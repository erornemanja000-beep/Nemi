# Brief: koncept-sajt za bečku pekaru „Krume"

Maketa za buduće klijente (pekare u Beču). Pekara je izmišljena: ime, radno vreme i hlebovi su primer, ne podaci pravog lokala. Na sajtu dole stoji „Konzept · Nemi Studio". Tekstovi na sajtu su na nemačkom.

## Ideja
**„Bevor Wien aufwacht."** Sajt počinje u 4 ujutru, u mraku pekare. Dok se skroluje, sat ide od 04:00 do 07:00: testo se mesi, ulazi u peć, kora pucketa, a kad se otvore vrata radnje, ekran postaje topao i svetao kao jutro. Potpisni trenutak: vrata peći se otvore i topla narandžasta svetlost preplavi stranicu.

## Raspoloženje
- Tiho, toplo, zanatski. Brašno u vazduhu, para, kora koja puca.
- Boje: noć `#14110f`, kora `#7a4a24`, žar `#e8792b`, testo `#eadbc4`, brašno `#f6f1e7`.
- Svetlo: jedan topao izvor (peć ili lampa nad stolom), duboke senke, bez hladnog plavog svetla osim kroz prozor pre zore.

## Sekcije
1. **04:00** – mrak, sjaj peći, naslov „Bevor Wien aufwacht, backen wir."
2. **Teig. Zeit. Ofen.** – tri koraka zanata.
3. **Brot des Tages** – Kaisersemmel, Mohnwecken, Laugenbrezel, Roggenlaib. (Prvo je pisalo Mohnflesserl i Salzstangerl; promenjeno da odgovara fotografijama koje su za sada na sajtu.)
4. **07:00** – radnja se otvara: radno vreme (primer: Di–Sa 6:30–14:00), „Vorbestellen".

## Zadatak za Codex
Codex za to vreme piše promptove i spisak materijala. Piše **samo** u fajl `studio/pekara/promptovi/codex.md`, ništa drugo ne menja i ništa ne preuzima. Format promptova uzima iz `.claude/agents/prompt-slike.md` i `.claude/agents/prompt-video.md`.

1. **AI slike (6 kom.):** početni i završni kadar za hero (04:00 mrak → 07:00 jutro), po jedna slika za svaki od 4 hleba. Isti stil, svetlo, objektiv i boje kao gore. Uz svaki prompt negativni prompt i format (16:9 za desktop i 9:16 za telefon).
2. **AI video (2 kom.):** a) hero: testo → peć → hleb, sa pokretom kamere i početnim i završnim kadrom; b) brašno u vazduhu, usporeno, u petlji. Uz svaki prompt rezervna, jednostavnija verzija.
3. **Besplatan materijal:** fontovi (licenca OFL, za self-hosting), teksture i HDRI (npr. Poly Haven), zvukovi (pucketanje kore, peć). Uz svaku stavku link, licencu i datum provere. Ako nešto nije provereno, označi **NEPROVERENO**.
