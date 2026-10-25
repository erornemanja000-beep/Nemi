# WACH. Cold Brew: probna reklama (Instagram / TikTok)

Izmišljeni brend, samo za probu. Format 9:16 (1080×1920), 12 s, 30 fps. Tekst na nemačkom.
Kod koji pravi video: `scripts/wach_reklama/` (`reklama.html` je animacija, `render.js` snima kadrove, `zvuk.py` pravi zvuk).

## Priča u jednoj rečenici
Ponedeljak ujutru, budilnik zvoni, a ti tražiš još 5 minuta. Onda s neba padne limenka WACH. i svet postane boja.

## Kadar po kadar
| Vreme | Slika | Tekst | Zvuk |
|---|---|---|---|
| 0.0–1.0 | Tamnoplava noć, zvezde. Veliki sat `06:59` lagano „diše". | „Montag." pada odozgo i odskoči (koralna) | tiha noćna podloga |
| 1.0–2.0 | Cifre se 3D preklope u `07:00`. Sat se trese, oko njega iskaču slova BRRR. | BRRR! | pištanje budilnika |
| 2.0–2.3 | Dugme SNOOZE se utisne (squash) i sat nestane. | SNOOZE | klik |
| 2.3–4.0 | Pospano lice (zatvorene oči), Zzz lebdi nagore. Slova teksta jedno po jedno klonu i padaju, kao da zaspe. | „Noch 5 Minuten…" | hrkanje |
| 4.0–4.5 | Limenka WACH. pada sa vrha ekrana. | — | zvižduk pada |
| 4.5 | Udar: limenka se spljošti i odskoči dva puta, talas ide od dna limenke, ekran se krugom oboji u narandžasto. | — | BOOM + početak ritma (120 BPM) |
| 5.0–8.0 | Limenka se vrti u 3D i lebdi. Na svaki takt menja se boja pozadine (narandžasta → pink → limeta → narandžasta) i prskaju kapi kafe. Reči se smenjuju 3D okretom. | „Augen auf." → „Kopf an." → „Los geht's." | whoosh na svaku promenu, pop na reči |
| 8.0–10.5 | Pozadina tamna kafa sa toplim sjajem. Kocke leda (prave 3D kocke) padaju, odskaču i prevrću se oko limenke. | „WACH." veliki logo, „Cold Brew", „Null Zucker. Voller Kick." | zvonjava leda |
| 10.5–12.0 | Dugme „Jetzt probieren →" iskače sa odskokom, ispod je @wach.coldbrew, završni blesak. | CTA | završni akord |

Boje: noć `#0E1430`, narandžasta `#FF7A1A`, pink `#FF3D7F`, limeta `#C6F432`, kafa `#2B1B14`, krem `#FFF4E6`.
Font: Inter Display Black (naslovi), Inter Display SemiBold (podnaslovi).
Sigurne zone za Instagram/TikTok: nema teksta u gornjih 200 px, donjih 320 px i desnih 140 px.

## Prompt za AI video program (EN, jedan klip po delu)
Isti tok, ako hoćeš da probaš u Kling / Seedance / Veo. Tekstove dodaj posle u montaži, jer AI ne piše tekst pouzdano.

**Klip 1 (0–4 s):** Vertical 9:16, night bedroom mood, deep navy background with soft stars. A large glowing retro digital alarm clock in the center shows 06:59, flips to 07:00 with a 3D flip of the digits, then shakes violently while ringing. Camera static, slight push-in. A hand presses a big snooze button, the clock fades. A cute sleepy cartoon face with closed eyes, floating Zzz. Playful 3D motion-graphics style, soft shadows, clean shapes, Pixar-like lighting.

**Klip 2 (4–8 s):** Vertical 9:16. A sleek matte orange aluminium coffee can labelled "WACH." falls from the top of frame and lands center with exaggerated squash and stretch, bouncing twice. On impact a circular shockwave floods the background with bright orange. The can spins in 3D, floating. Coffee droplets burst outward in slow motion. The background color changes on the beat: orange, hot pink, lime green. Bold, punchy, commercial motion graphics, crisp studio lighting, high contrast.

**Klip 3 (8–12 s):** Vertical 9:16. Hero product shot: the can rotating slowly on a dark espresso-brown background with warm rim light. Translucent ice cubes fall from above, bounce and tumble around the can, condensation droplets on the can. Ends with a gentle push-in and a soft light flash. Premium beverage commercial, macro detail, shallow depth of field.

**Negativni prompt:** text, letters, watermark, logo distortion, extra cans, deformed can, blurry, low quality, flicker, jitter, warped hands, cluttered background.
