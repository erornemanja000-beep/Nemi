# Scena: "Mali svet na tanjiru" (palačinka)

End frame: `frames/palacinka_end_16x9.png`
Start frame: napraviti u AI programu za slike (prompt dole), pa ga koristiti kao start.
Kling slika → video, 16:9, 10 s, najviši kvalitet.

## 1. Start frame (prompt za sliku, uz originalnu fotografiju kao referencu)

```
The same yellow rectangular plate on the same dark grey table, same camera angle and lighting as the reference photo, but with only a plain golden rolled crepe in the middle. No sauce, no chocolate, no whipped cream, no ice cream, no cherry, no toppings. Clean, appetizing, photorealistic food photography.
```

## 2. Video prompt

```
Magical photorealistic dessert commercial, a tiny enchanted world on a plate, warm golden afternoon light, shallow depth of field, macro food detail, soft sparkles in the air. Slow cinematic camera: a low-angle macro view that slowly arcs around the plate and gently pushes in, then settles exactly into the final framing of the end image.

0-1s: a plain golden rolled crepe lies on a yellow rectangular plate on a dark table. Tiny golden sparkles float above it.
1-3s: two glossy ribbons, one of white caramel and one of milk chocolate, fly in through the air like shiny magical chains, wrap around the crepe several times as if holding it tight, then soften and melt into thick, glossy drizzle lines dripping down its sides.
2.5-4s: dark chocolate shavings rain down from above like little autumn leaves and settle on both ends of the crepe.
3.5-5.5s: a tiny cute squirrel made of glossy milk chocolate runs across the plate, leaps onto the top of the crepe, curls up into a ball and smoothly transforms into a striped chocolate wafer bar lying across the crepe.
5-7s: in the front right corner of the plate a miniature snowy mountain rises up, then its snow gently softens and swirls into a fluffy mound of whipped cream.
6.5-8s: a tiny cherry tree sprouts on top of the whipped cream mountain and blossoms, one shiny red cherry drops from its branch and lands on top of the cream with a soft bounce, the little tree dissolves into pink sparkles.
7.5-9s: at the back of the plate a small snowball rolls in and turns into a scoop of chocolate ice cream that settles beside the crepe.
9-10s: everything settles into the final image: the crepe with caramel and chocolate drizzle, chocolate shavings, the chocolate wafer bar, the chocolate ice cream scoop and the whipped cream with the cherry. A few golden sparkles fade.

Whimsical but realistic, smooth transformations, satisfying, mouth-watering, premium, 4K.
```

## Negativni prompt

```
people, hands, legs, feet, background people, cartoon style, 3D animation look, plastic look, creepy creature, deformed animal, extra animals, multiple squirrels, messy plate, spilled sauce, melting mess, different plate, different table, extra food, extra desserts, text, logos, brand names, watermark, morphing crepe, flicker, fast cuts, jump cuts, shaky camera, oversaturated, low quality, blurry
```

---

# Podeljeno na dva klipa po 10 s (negativno je ubačeno u prompt kao "Avoid:")

Deo 1: start = prazna palačinka (korak 1), bez end frame-a.
Deo 2: start = poslednji kadar dela 1, end = `frames/palacinka_end_16x9.png`.

## Deo 1

```
Magical photorealistic dessert commercial, a tiny enchanted world on a plate, warm golden afternoon light, shallow depth of field, macro food detail, soft golden sparkles in the air. Slow cinematic camera: a low-angle macro view that slowly arcs around the plate and gently pushes in.

0-2s: a plain golden rolled crepe lies on a yellow rectangular plate on a dark table. Tiny golden sparkles float above it.
2-5s: two glossy ribbons, one of white caramel and one of milk chocolate, fly in through the air like shiny magical chains, wrap around the crepe several times as if holding it tight, then soften and melt into thick, glossy drizzle lines dripping down its sides.
5-6.5s: dark chocolate shavings rain down from above like little autumn leaves and settle on both ends of the crepe.
6.5-9s: a tiny cute squirrel made of glossy milk chocolate runs across the plate, leaps onto the top of the crepe, curls up into a ball and smoothly transforms into a striped chocolate wafer bar lying across the crepe.
9-10s: the camera settles on the crepe with the caramel and chocolate drizzle, the chocolate shavings and the chocolate wafer bar. The rest of the plate stays empty.

Whimsical but realistic, smooth transformations, satisfying, mouth-watering, premium, 4K.

Avoid: people, hands, legs, background people, cartoon style, 3D animation look, plastic look, creepy or deformed animal, extra animals, multiple squirrels, whipped cream, ice cream, cherry, messy plate, spilled sauce, different plate, different table, extra food, text, logos, brand names, watermark, flicker, jump cuts, shaky camera, oversaturated, blurry.
```

## Deo 2

```
Magical photorealistic dessert commercial, a tiny enchanted world on a plate, warm golden afternoon light, shallow depth of field, macro food detail, soft golden sparkles in the air. The crepe with caramel and chocolate drizzle, chocolate shavings and the chocolate wafer bar stays exactly the same the whole time. Slow cinematic camera that continues gently around the plate and settles exactly into the final framing of the end image.

0-3s: in the front right corner of the plate a miniature snowy mountain rises up from the plate, then its snow gently softens and swirls into a fluffy mound of whipped cream.
3-6s: a tiny cherry tree sprouts on top of the whipped cream mountain and blossoms, one shiny red cherry drops from its branch and lands on top of the cream with a soft bounce, then the little tree dissolves into pink sparkles.
6-8.5s: at the back of the plate a small snowball rolls in and turns into a scoop of chocolate ice cream that settles beside the crepe.
8.5-10s: everything settles into the final image: the crepe with drizzle, chocolate shavings and the wafer bar, the chocolate ice cream scoop and the whipped cream with the cherry. A few golden sparkles fade.

Whimsical but realistic, smooth transformations, satisfying, mouth-watering, premium, 4K.

Avoid: people, hands, legs, background people, cartoon style, 3D animation look, plastic look, changing the crepe, moving the wafer bar, extra cherries, extra scoops, messy plate, melting mess, different plate, different table, extra food, text, logos, brand names, watermark, flicker, jump cuts, shaky camera, oversaturated, blurry.
```

---

# Deo 1, popravljena verzija (AI je pravio svoju palačinku)

Uzrok: pokret kamere + mnogo dešavanja bez end frame-a → AI "izmisli" novu palačinku.
Rešenje: kamera skoro mirna, manje dešavanja, i (preporuka) end frame kao sidro.

## Srednji kadar (end frame za deo 1), u programu za slike, ulaz = originalna fotografija

```
Edit this photo: remove only the chocolate wafer bar, the chocolate shavings, the whipped cream and the cherry. Keep the crepe, the light caramel and chocolate drizzle lines, the chocolate ice cream scoop, the yellow plate, the table, the camera angle and the lighting exactly the same. Photorealistic.
```

## Video prompt, deo 1 (10 s)

Start = prazna palačinka · End = srednji kadar (ako postoji) · 16:9, 10 s

```
Photorealistic dessert commercial, macro food photography, warm soft daylight, shallow depth of field. Locked camera, almost static, only a very slow, subtle push-in. One single crepe that never changes: the same golden-brown rolled crepe with the same shape, size, color and position on the same yellow rectangular plate on the same dark table during the whole video.

0-1.5s: the plain rolled crepe rests on the plate, tiny golden sparkles float in the air.
1.5-5s: a thin glossy stream of light caramel sauce appears in the air and draws long zigzag lines across the crepe from left to right, like thin shiny ribbons wrapping around it, the lines run down over the top and drip down the sides of the crepe.
5-7.5s: a thin stream of milk chocolate sauce draws finer zigzag lines between the caramel lines, also wrapping over the crepe and dripping down its sides, a few small drops land on the plate.
7.5-9.5s: a round scoop of chocolate ice cream gently drops from above onto the plate behind the left half of the crepe, lands with a soft small bounce and settles.
9.5-10s: everything is still: the crepe with caramel and chocolate drizzle and the chocolate ice cream scoop behind it.

Smooth, satisfying, mouth-watering, premium, 4K.

Avoid: new crepe, replacing the crepe, changing crepe shape or size, folded crepe, multiple crepes, crepe moving, camera orbit, big camera movement, whipped cream, cherry, chocolate bar, chocolate shavings, extra toppings, extra food, messy plate, sauce splashing everywhere, people, hands, legs, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry, oversaturated.
```

---

# Deo 1, finalno: prazna palačinka → prelivi kao lanci + mrvice (10 s)

Start: `frames/palacinka_prazna_16x9.png`. End: najbolje bez end frame-a (slika sa belom pozadinom kvari pozadinu).
Ako se pravi end frame, u programu za slike ulaz = prazna palačinka:

```
Edit this photo: add glossy light caramel zigzag drizzle lines and thinner milk chocolate drizzle lines across the top of the crepe, dripping down its sides, with a few small chocolate drops on the plate, and a pile of chocolate shavings on both ends of the crepe. Keep the same crepe, the same yellow plate, the same dark grey table and dark background, the same camera angle and the same natural daylight. Do not change or remove the background.
```

## Video prompt

```
Photorealistic dessert commercial filmed on location, macro food photography, natural soft daylight, shallow depth of field. The scene is exactly the start image: the same golden rolled crepe on the same yellow rectangular plate with brown rim, standing on the same dark grey metal table, with the same dark blurred cafe background. The background, the table, the plate and the crepe stay exactly the same during the whole video. Locked camera, almost static, only a very slow subtle push-in.

0-1.5s: the plain crepe rests on the plate, a few tiny golden sparkles float in the air.
1.5-4.5s: from the left side of the frame, several glossy ribbons of light caramel sauce fly in through the air like shiny liquid chains. They wrap around the crepe one after another in diagonal loops, tighten gently as if holding the crepe, then soften and settle into thick glossy zigzag drizzle lines across the top, dripping down the sides.
4.5-7s: from the right side, thinner ribbons of milk chocolate sauce fly in the same way, like delicate dark chains, wrap around the crepe between the caramel lines, then relax into fine glossy chocolate drizzle lines dripping down the sides, a few small chocolate drops fall onto the plate.
7-9s: small curled chocolate shavings rain down from above like little autumn leaves, bouncing slightly, and pile up on both ends of the crepe, left and right, leaving the middle with only the drizzle.
9-10s: everything is still: the same crepe on the same plate and table, covered with caramel and chocolate drizzle and chocolate shavings on both ends.

Smooth, satisfying, mouth-watering, premium, warm, 4K.

Avoid: white background, studio background, plain background, removing the background, changing the table, changing the plate, new crepe, replacing the crepe, changing crepe shape or size, multiple crepes, crepe moving, camera orbit, big camera movement, ice cream, whipped cream, cherry, chocolate bar, extra food, messy plate, sauce splashing everywhere, people, hands, legs, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry, oversaturated.
```

---

# Deo 1, TAČNO kao druga slika (brza verzija)

Start: `frames/palacinka_prazna_16x9.png` · End: `frames/palacinka_prelivi_16x9.png`
(druga slika sa vraćenom tamnom pozadinom, prelivi i mrvice netaknuti). 16:9, 5 s.

```
Fast, punchy photorealistic dessert commercial, macro food photography, natural soft daylight, shallow depth of field, dark blurred cafe background. The video starts exactly on the start image and ends exactly on the end image: the same rolled crepe on the same yellow plate, and the final drizzle and chocolate shavings must look exactly like in the end image. The background never changes. Camera almost static with a slight push-in.

0-0.5s: the plain rolled crepe on the plate.
0.5-2s: fast: glossy ribbons of cream-colored white chocolate sauce shoot in from the left side and wrap quickly around the crepe in several tight loops like shiny chains, snapping into place.
1.5-3s: fast: thinner ribbons of milk chocolate sauce shoot in from the right side and wrap quickly around the crepe between the white lines, then all ribbons instantly relax into the exact drizzle pattern of the end image, dripping down the sides, with the same few chocolate drops on the plate.
3-4.2s: chocolate shavings burst out from inside both open ends of the crepe like a small confetti pop, fly up briefly and land in piles on the left and right ends exactly as in the end image.
4.2-5s: everything settles and holds still exactly on the end image.

Quick satisfying rhythm, smooth, mouth-watering, premium, 4K.

Avoid: white background, studio background, background change, new crepe, changing crepe shape, different drizzle pattern, caramel color, extra sauces, sprinkles, ice cream, whipped cream, cherry, chocolate bar, extra food, messy splashes, slow motion, long pauses, camera orbit, people, hands, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry.
```

---

# Deo 1, spirala (beli sleva, čokoladni zdesna) + mrvice tačno kao na slici

Start: `frames/palacinka_prazna_16x9.png` · End: `frames/palacinka_prelivi_16x9.png` · 16:9, 5 s

```
Photorealistic dessert commercial, macro food photography, natural soft daylight, shallow depth of field, dark blurred cafe background. The video starts exactly on the start image and ends exactly on the end image. The crepe, the plate, the table and the background never change. Locked camera, almost static.

0-0.5s: the plain rolled crepe on the yellow plate.
0.5-3s: two glossy sauce streams appear at the same time: a cream-colored white chocolate stream starts at the left end of the crepe and a milk chocolate stream starts at the right end of the crepe. They wrap around the crepe in tight spirals, the white one moving from left to right and the chocolate one moving from right to left, coiling around it like ribbons, crossing each other in the middle.
3-3.8s: the spirals soften and settle into exactly the drizzle pattern of the end image, dripping down the sides of the crepe, with the same few chocolate drops on the plate.
3.8-4.5s: the chocolate shavings appear in place on the left and right ends of the crepe, softly fading in exactly where they are in the end image, exactly the same shape, size, color and amount as in the end image.
4.5-5s: everything holds still exactly on the end image.

Smooth, fast, satisfying, mouth-watering, premium, 4K.

Avoid: new chocolate shavings, different shavings, sprinkles, chocolate chips, flying shavings, sauce coming from outside the frame, white background, background change, new crepe, changing crepe shape, different drizzle pattern, caramel color, extra sauces, ice cream, whipped cream, cherry, chocolate bar, extra food, messy splashes, slow motion, camera orbit, people, hands, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry.
```

Sigurnost za dalje kadrove: u CapCut-u stavi end frame sliku na sam kraj klipa (0,3 s crossfade),
i za start sledećeg dela koristi `palacinka_prelivi_16x9.png`, ne poslednji kadar videa.

---

# Deo 1, lebdeća palačinka (prelivi oko nje, pad na tanjir, mrvice kao mravi)

Start: `frames/palacinka_prazna_16x9.png` · End: `frames/palacinka_prelivi_16x9.png` · 16:9, 10 s

```
Magical photorealistic dessert commercial, macro food photography, natural soft daylight, shallow depth of field, the same dark blurred cafe background and dark grey table during the whole video. Locked camera, almost static. The video starts exactly on the start image and ends exactly on the end image.

0-1.5s: the plain rolled crepe slowly lifts off the yellow plate and floats in the air about a hand's width above it, gently rotating around its long axis, golden sparkles around it.
1.5-5s: while the crepe floats and slowly rotates, a glossy cream-colored white chocolate sauce stream comes from the left and a glossy milk chocolate sauce stream comes from the right. They wind around the whole crepe in spirals, all the way around it (over, under and around), the white one moving from left to right and the chocolate one from right to left, wrapping it completely like ribbons.
5-6s: the two spirals meet in the middle and merge, then settle into exactly the drizzle pattern of the end image on top of the crepe, dripping down its sides.
6-6.8s: the crepe suddenly drops back onto the yellow plate, landing with a soft bounce in exactly the same position as in the end image, a few chocolate drops land on the plate.
6.8-9s: chocolate shavings march in across the plate like tiny ants in two neat lines, one line from the left and one from the right, climb up onto the two ends of the crepe and settle into piles, ending with exactly the same shavings, shape, size, color and amount as in the end image.
9-10s: everything holds still exactly on the end image.

Smooth, satisfying, playful but realistic, mouth-watering, premium, 4K.

Avoid: real ants, insects, legs on the shavings, creepy, different shavings, sprinkles, chocolate chips, white background, background change, different table, new crepe, changing crepe shape or size, unrolling crepe, different drizzle pattern, caramel color, extra sauces, ice cream, whipped cream, cherry, chocolate bar, extra food, messy splashes, camera orbit, people, hands, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry.
```

---

# Deo 1, lebdeća palačinka v2 (bez reči "ants", mrvice klize u kolonama)

Start: `frames/palacinka_prazna_16x9.png` · End: `frames/palacinka_prelivi_16x9.png` · 16:9, 10 s

```
Magical photorealistic dessert commercial, macro food photography, natural soft daylight, shallow depth of field, the same dark blurred cafe background and dark grey table during the whole video. Locked camera, almost static. The video starts exactly on the start image and ends exactly on the end image.

0-1.5s: the plain rolled crepe slowly lifts off the yellow plate and floats in the air about a hand's width above it, gently rotating around its long axis, golden sparkles around it.
1.5-5s: while the crepe floats and slowly rotates, a glossy cream-colored white chocolate sauce stream comes from the left and a glossy milk chocolate sauce stream comes from the right. They wind around the whole crepe in spirals, all the way around it, the white one moving from left to right and the chocolate one from right to left, wrapping it completely like ribbons.
5-6s: the two spirals meet in the middle and merge, then settle into exactly the drizzle pattern of the end image on top of the crepe, dripping down its sides.
6-6.8s: the crepe suddenly drops back onto the yellow plate, landing with a soft bounce in exactly the same position as in the end image, a few chocolate drops land on the plate.
6.8-9s: small curled milk chocolate shavings, glossy brown chocolate curls exactly like in the end image, slide and tumble across the yellow plate in two neat rows, one row from the left edge of the plate and one row from the right edge, like a tiny chocolate parade. They hop up onto the two ends of the crepe and settle into piles of chocolate shavings, ending with exactly the same chocolate shavings, shape, size, color and amount as in the end image.
9-10s: everything holds still exactly on the end image.

Smooth, satisfying, playful but realistic, mouth-watering, premium, 4K.

Avoid: insects, bugs, ants, beetles, any living creatures, legs, eyes, faces, creepy, different shavings, sprinkles, chocolate chips, white background, background change, different table, new crepe, changing crepe shape or size, unrolling crepe, different drizzle pattern, caramel color, extra sauces, ice cream, whipped cream, cherry, chocolate bar, extra food, messy splashes, camera orbit, people, hands, text, logos, watermark, cartoon, CGI look, morphing, flicker, jump cuts, blurry.
```

---

# Deo 2: mrvice, sladoled, čokoladica, šlag i trešnja

Start: III (palačinka sa prelivima, kapi čokolade na tanjiru) · End: finalna slika (`frames/palacinka_end_16x9.png` ili tvoja 1920×1080) · 16:9, 10 s

```
Magical photorealistic dessert commercial, macro food photography, natural soft daylight, shallow depth of field. The video starts exactly on the start image and ends exactly on the end image. The crepe with its white chocolate and milk chocolate drizzle stays exactly the same the whole time. Smooth camera: starting from the close view of the start image, the camera slowly pulls back and settles exactly into the framing of the end image, with the same dark grey table and dark background as the end image. The toppings arrive one by one with a satisfying rhythm, each with a soft bounce and a few golden sparkles.

0-2s: small curled milk chocolate shavings rain down from above like little autumn leaves and settle in piles on both ends of the crepe, exactly like in the end image. The chocolate drops on the plate stay as small drizzle spots.
2-4s: a scoop of chocolate ice cream drops from above onto the plate behind the left half of the crepe, lands with a soft squish and settles exactly where it is in the end image.
4-6s: a striped milk chocolate wafer bar spins down from above and lands diagonally on top of the crepe, exactly in the position of the end image.
6-8s: in the front right corner of the plate a fluffy swirl of whipped cream rises up like a little snowy mountain and settles into the whipped cream mound of the end image.
8-9.2s: one glossy red cocktail cherry drops from above onto the top of the whipped cream, bounces once and stops.
9.2-10s: everything holds still exactly on the end image.

Smooth, satisfying, playful but realistic, mouth-watering, premium, 4K.

Avoid: changing the crepe, changing the drizzle, new crepe, insects, creatures, animals, faces, multiple cherries, multiple chocolate bars, extra scoops, sprinkles, chocolate chips, brand names, text, logos, watermark, melting mess, messy splashes, white background, different plate, extra food, people, hands, cartoon, CGI look, morphing, flicker, jump cuts, shaky camera, blurry, oversaturated.
```

---

# Deo 2 v2: "Mali svet na tanjiru" (animirano)

Start: III · End: finalna slika · 16:9, 10 s

```
Magical photorealistic dessert commercial, a tiny enchanted world on a plate, macro food photography, natural soft daylight, shallow depth of field, soft golden sparkles in the air. The video starts exactly on the start image and ends exactly on the end image. The crepe with its white chocolate and milk chocolate drizzle stays exactly the same the whole time. Smooth camera: from the close view of the start image the camera slowly pulls back and settles exactly into the framing of the end image, with the same dark grey table and dark background as the end image.

0-2s: a gentle breeze blows small curled milk chocolate shavings in like autumn leaves, they swirl around the crepe and settle in piles on both ends, exactly like in the end image.
2-4s: a tiny cute squirrel made of glossy milk chocolate runs across the plate, leaps onto the top of the crepe, curls into a ball and smoothly transforms into the striped chocolate wafer bar lying diagonally on the crepe, exactly in the position of the end image.
4-6s: in the front right corner of the plate a miniature snowy mountain rises up, then its snow softens and swirls into the fluffy whipped cream mound of the end image.
6-7.5s: a tiny cherry tree sprouts on top of the whipped cream mountain and blossoms, one glossy red cherry drops from its branch onto the top of the cream with a soft bounce, then the little tree dissolves into pink sparkles.
7.5-9s: behind the left half of the crepe a small snowball rolls in and turns into the scoop of chocolate ice cream of the end image.
9-10s: everything holds still exactly on the end image, a few golden sparkles fade.

Whimsical but realistic, smooth transformations, satisfying, mouth-watering, premium, 4K.

Avoid: changing the crepe, changing the drizzle, new crepe, real squirrel with fur, creepy or deformed animal, extra animals, multiple squirrels, insects, the squirrel staying at the end, multiple cherries, multiple chocolate bars, extra scoops, sprinkles, brand names, text, logos, watermark, melting mess, messy splashes, white background, different plate, extra food, people, hands, cartoon, 3D animation look, CGI look, morphing crepe, flicker, jump cuts, shaky camera, blurry, oversaturated.
```
