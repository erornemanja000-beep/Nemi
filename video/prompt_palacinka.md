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
