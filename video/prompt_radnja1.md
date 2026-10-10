# Prompt: RADNJA-1 (zid → prozor), filmska verzija sa pokretom kamere

Ulazni snimak: `RADNJA-1.mov` = prvih 4 s videa gradnje (zid puca u cigle, sklapa se prozor).

## Podešavanja

**Način A (najbolja kontrola): slika → video sa početnim i završnim kadrom**
- Start frame: `frames/video_c_end_frame.png` (isti kao prvi kadar RADNJA-1)
- End frame: `frames/lokal_faza_2.png` (gotov prozor)
- Format 16:9, dužina 6 s (može i 10 s), kvalitet najviši

**Način B: video → video (ubaciš RADNJA-1.mov)**
- "Structure / reference strength" oko 0.5–0.6. Na 0.8+ program zadrži mirnu kameru
  iz snimka i neće uraditi pokret.
- Ista dužina kao ulaz

Napravi 3–4 verzije i izaberi najbolju.

## Glavni prompt (6 s)

```
Ultra-realistic cinematic commercial shot of a pastel pink ice cream shop facade at golden hour, the shop window builds itself out of thin air. One continuous take, smooth professional camera movement, 35mm lens, shallow depth of field, soft film grain, warm golden sunlight from the left, gentle volumetric light rays, tiny dust particles and golden sparkles floating in the air. Keep the building exactly as in the reference: blush pink plaster facade, dark gutter, small upper windows, a closed cream window panel in a deep recess.

0-1s: static wide frontal shot of the closed cream panel. A soft pink glow pulses from its center and fine cracks spread outward in a neat brick pattern. The camera starts a slow push-in.
1-2.5s: the panel bursts into solid cream plaster blocks that fly outward toward the camera in elegant slow motion, tumbling and rotating with real weight, chipped edges catching the sunlight, puffs of fine dust. A few blocks pass very close to the lens with natural motion blur. The camera arcs slightly to the right at a low angle, revealing the depth of the recess and a warm pink glow inside the empty opening.
2.5-4s: glossy white window frame pieces fly in from above and from the sides and lock together one by one with crisp, satisfying snaps and small bounces: bottom rail, left and right sides, top header, center post. Each landing sends a tiny puff of dust and a sparkle of light along the edges. The camera glides back toward the front.
4-5s: two glass panes slide into place, a bright reflection sweeps across the glass, soft pink light switches on inside.
5-6s: the camera settles exactly back into the original wide frontal framing and holds still on the finished window while a few golden sparkles fade.

Premium, magical but believable, satisfying rhythm, high detail, 4K quality.
```

## Verzija sa komandama za kameru (MiniMax "Director" / camera control)

```
[Static shot] Wide frontal view of a pastel pink ice cream shop facade at golden hour, a closed cream window panel glows soft pink in the center and cracks into a neat brick pattern. [Push in, Truck right] The panel bursts into solid cream plaster blocks flying toward the camera in elegant slow motion with fine dust and golden sparkles, revealing a warm pink glowing opening. [Pull out] Glossy white window frame pieces fly in and lock together one by one with crisp snaps and small bounces, two glass panes slide in with a sweep of light, soft pink light turns on inside. [Static shot] The camera holds on the finished window in the original wide frontal framing. Ultra-realistic, cinematic, 35mm lens, shallow depth of field, warm golden hour light.
```

## Negativni prompt

```
people, hands, workers, construction tools, cranes, scaffolding, plastic toy bricks, LEGO studs, LEGO logo, cartoon, CGI look, video game look, different building, changed facade, extra windows, extra doors, wrong colors, text, letters, logos, watermark, warped architecture, bending lines, melting walls, morphing, flicker, jitter, shaky handheld camera, fast whip pan, sudden cuts, scene change, night, rain, overexposed, oversaturated, low resolution, blurry, noise
```

Napomena: reč "Lego" je namerno izbegnuta u promptu (piše "blocks"), jer AI tada
napravi prave plastične Lego kockice sa ispupčenjima.
