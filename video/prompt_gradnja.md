# Promptovi za AI program (video → video)

Ubaci video kao referencu (video to video / reference video / restyle) i
nalepi prompt. Ako program prima najviše 10 s, koristi delove:
`gradnja_deo1.mp4` (0:00–0:08,5) i `gradnja_deo2.mp4` (0:08,5–0:17,4).

Podešavanja: ista dužina kao ulazni video; "structure" / "reference strength"
visoko (0.8–0.9), "creativity" / "motion" nisko. Tako program zadrži pokrete
i izgled lokala, a doda realizam.

## Ceo video (17 s)

```
Photorealistic cinematic video of a small ice cream shop facade building itself piece by piece, like satisfying Lego construction. Static locked camera, straight frontal view, warm golden hour sunlight, soft blush pink and pistachio green tones, magical but realistic. Keep the building, the shop, the layout, the colors and the timing exactly as in the reference video. Only make it more realistic: real 3D depth, realistic materials and glass, soft shadows, realistic weight and physics.

0.0-0.6s: a closed beige window panel on a soft pink facade.
0.6-2.0s: a soft pink glow appears in the center of the panel, the panel cracks into Lego-like bricks that burst outward from the center and tumble down.
1.8-3.0s: a white window frame assembles piece by piece, each piece drops from above and snaps into place with a small bounce and a puff of dust: bottom frame, left side, right side, top, middle post, sash bars.
3.0-4.0s: light glints across the new glass, warm pink light glows inside.
4.4-5.5s: the window and the wall below it crumble into bricks from top to bottom and fall away.
5.4-6.6s: a tall glass storefront assembles: left door frame, right frame, top beam, two vertical posts, bottom sill, each dropping in with a crisp bounce.
6.7-7.6s: the glass door swings open, a white gelato display counter drops inside, then its curved glass top clicks on.
8.4s: finished storefront with an empty display counter.
8.7-9.6s: one extra post dissolves into golden sparkles, the interior turns soft pink, four ceiling lights switch on one by one.
9.7-10.7s: three menu boards drop onto the back wall, the coffee bar and the left counter rise up, a COFFEE TIME neon sign flickers on, a drinks fridge slides in from the right.
11.0s: a new gelato display counter drops in with a strong impact and fills with colorful gelato.
11.7-12.1s: the green DON'S eisdiele logo with a french bulldog pops onto the counter, a pink sticker and a small mascot pop in.
13.2-14.2s: large dark grey letters D, O, N, apostrophe, S drop one by one onto the wall above the entrance, each landing with a bounce and sparkles.
15.5-17.4s: a light sweep runs across the DON'S sign, golden sparkles drift, the finished ice cream shop.

Every landing has a small camera shake, soft dust and gold-pink sparkles. Fast satisfying rhythm: bam, bam, bam.
```

## Deo 1 (gradnja_deo1.mp4, 8,5 s)

```
Photorealistic cinematic video of a shop window building itself piece by piece, like satisfying Lego construction. Static locked camera, straight frontal view, warm golden hour sunlight, soft blush pink tones, magical but realistic. Keep the building, the layout, the colors and the timing exactly as in the reference video. Only make it more realistic: real 3D depth, realistic materials and glass, soft shadows, realistic weight and physics.

0.0-0.6s: a closed beige window panel on a soft pink facade.
0.6-2.0s: a soft pink glow appears in the center of the panel, the panel cracks into Lego-like bricks that burst outward from the center and tumble down.
1.8-3.0s: a white window frame assembles piece by piece, each piece drops from above and snaps into place with a small bounce and a puff of dust: bottom frame, left side, right side, top, middle post, sash bars.
3.0-4.0s: light glints across the new glass, warm pink light glows inside.
4.4-5.5s: the window and the wall below it crumble into bricks from top to bottom and fall away.
5.4-6.6s: a tall glass storefront assembles: left door frame, right frame, top beam, two vertical posts, bottom sill, each dropping in with a crisp bounce.
6.7-7.6s: the glass door swings open, a white gelato display counter drops inside, then its curved glass top clicks on.
7.6-8.5s: the finished storefront with an empty display counter, calm.

Every landing has a small camera shake, soft dust and gold-pink sparkles. Fast satisfying rhythm: bam, bam, bam.
```

## Deo 2 (gradnja_deo2.mp4, 8,9 s)

```
Photorealistic cinematic video of an ice cream shop interior filling up piece by piece, then the shop sign appears, like satisfying Lego construction. Static locked camera, straight frontal view, warm golden hour sunlight, soft blush pink and pistachio green tones, magical but realistic. Keep the building, the shop, the layout, the colors and the timing exactly as in the reference video. Only make it more realistic: real 3D depth, realistic materials and glass, soft shadows, realistic weight and physics.

0.0-0.2s: a glass storefront with an empty white display counter.
0.2-1.1s: one extra post dissolves into golden sparkles, the interior turns soft pink, four ceiling lights switch on one by one.
1.2-2.2s: three menu boards drop onto the back wall, the coffee bar and the left counter rise up, a COFFEE TIME neon sign flickers on, a drinks fridge slides in from the right.
2.5s: a new gelato display counter drops in with a strong impact and fills with colorful gelato.
3.2-3.6s: the green DON'S eisdiele logo with a french bulldog pops onto the counter, a pink sticker and a small mascot pop in.
4.7-5.7s: large dark grey letters D, O, N, apostrophe, S drop one by one onto the wall above the entrance, each landing with a bounce and sparkles.
7.0-8.9s: a light sweep runs across the DON'S sign, golden sparkles drift, the finished ice cream shop.

Every landing has a small camera shake, soft dust and gold-pink sparkles. Fast satisfying rhythm: bam, bam, bam.
```

## Negativni prompt (isti za sve)

```
different building, changed facade, different shop, different layout, different interior, extra windows, extra doors, extra objects, people, customers, workers, hands, faces, cranes, tools, cars, wrong letters, misspelled sign, extra text, random logos, distorted architecture, warped lines, bending walls, melting building, morphing, flickering, camera movement, zoom, pan, tilt, slow motion, long pauses, cartoon style, oversaturated colors, low quality, blurry
```
