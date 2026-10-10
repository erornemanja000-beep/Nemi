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

---

# Kling O3 Video Edit (RADNJA-1)

Kling O3 video edit zadržava kameru, kadar i pokrete iz ubačenog snimka i menja
samo izgled. Zato ovde nema pokreta kamere u promptu: približavanje se radi u
CapCut-u (dole). Ulaz: RADNJA-1.mov (4,1 s, a Kling prima 3–10 s); izlaz je
iste dužine.

## Edit prompt

```
Edit @Video1: turn it into an ultra-realistic, high-end cinematic commercial shot. Keep exactly the same camera position, framing, timing and movement of every piece as in @Video1, the same building, the same window shape and the same colors. Only upgrade realism, materials and lighting.

Make the facade real blush pink plaster with fine texture, a dark metal gutter and real upper windows, lit by warm golden hour sunlight from the left with soft shadows and gentle volumetric light rays.
When the cream panel cracks, the cracks glow softly pink from inside.
The flying blocks are solid cream plaster blocks with real weight, chipped edges, rough texture and soft shadows, tumbling realistically and releasing fine dust that catches the sunlight.
The window frame pieces are glossy white aluminum profiles with sharp edges and soft reflections. Every time a piece lands it makes a tiny puff of dust and a short sparkle of light.
The glass panes are real glass with soft reflections of the street and the sky, and the light sweep across them looks like a real sun reflection.
Behind the glass: warm pink walls, a soft pink glow and realistic depth.
Add subtle floating dust particles and a few small golden sparkles in the air.

Style: premium ice cream brand commercial, 35mm lens, natural depth of field, soft film grain, high dynamic range, soft pastel colors (blush pink, cream, warm gold), photorealistic, 4K detail.
```

## Negativni prompt (ako postoji polje)

```
different building, changed layout, different window design, extra windows, extra doors, people, hands, workers, tools, scaffolding, plastic toy bricks, LEGO studs, text, logos, watermark, cartoon, CGI look, warped lines, bending walls, melting, morphing, flicker, camera drift, random camera movement, low resolution, blurry, oversaturated
```

## Približavanje kamere u CapCut-u (keyframe)

Na klipu koji Kling vrati, Scale + Position keyframe, kriva "Ease in/out":
- 0,0 s i 0,6 s: Scale 100%
- 2,0 s: Scale 115% (pomeri sliku tako da prozor ostane u sredini)
- 3,6 s: Scale 100% (vrati se u početni kadar)
