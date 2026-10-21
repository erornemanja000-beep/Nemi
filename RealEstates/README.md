# Vista Estates — premium real-estate site with 3D scroll

A concept website for **Vista Estates**, a fictional luxury real-estate agency (villas, penthouses, residences on the fictional *Costa Aurea*). While you scroll, the camera flies around a 3D villa, light shifts from noon to sunset, and you walk in through the glass doors. Every section after that has its own motion.

> All listings, prices, agents and reviews are made up. The brand is fictional.

## Run it

```bash
npm install
npm run dev        # http://localhost:5173
```

## Build

```bash
npm run build      # type-checks and outputs a static site to dist/
npm run preview    # serve dist/ locally
```

`dist/` is fully static, and `base: './'` plus `HashRouter` mean it works from any sub-path:

- **Netlify:** build command `npm run build`, publish directory `RealEstates/dist` (base directory `RealEstates`).
- **GitHub Pages:** publish the contents of `dist/` (for example with an Actions workflow, or by pushing `dist/` to a `gh-pages` branch).

## Stack

Vite · React · TypeScript · Tailwind CSS v4 · GSAP + ScrollTrigger · Lenis · Three.js + React Three Fiber.

## What's on the page

| # | Section | Effect |
|---|---------|--------|
| 0 | Loader | SVG logo draws itself, the real loading percentage counts up, and a two-panel curtain opens |
| 1 | Hero (420 vh, sticky) | Procedural Three.js villa. The camera follows a spline (orbit → approach → through the sliding doors), the sun moves from noon to below the horizon, interior lights and the pool glow at dusk. The title reveals word by word from a mask, with parallax layers and chapter captions |
| 2 | Numbers | Counters and gold rules that draw in |
| 3 | Featured properties | Pinned horizontal scroll (vertical on phones), cards with 3D tilt + shine, details pop on hover. A click opens a deep-linkable modal (`#/property/<slug>`) with a gallery, a self-drawing floor plan and a "Schedule a viewing" form |
| 4 | Neighbourhoods | Sticky list, photos swapped with clip-path masks, and a stylised SVG coast map with pulsing pins |
| 5 | Process | Timeline line drawn by scroll, steps pop in |
| 6 | Walkthrough | Pinned CSS-3D corridor of interior photos you "walk" through |
| 7 | Mortgage calculator | Four sliders, a tweened monthly payment and a principal/interest ring |
| 8 | Team | Grayscale → colour, clip-path reveal, magnetic call/email buttons |
| 9 | Reviews | Two opposing marquees, pause on hover |
| 10 | Contact + CTA | Headline scales with scroll. The form has validation and an animated success state (no backend — add `data-netlify="true"` to receive submissions on Netlify) |
| 11 | Footer | Giant "VISTA" letters rise from a mask, photo credits, plus a `/credits` page |

Global: custom cursor (dot + ring with labels), page-transition curtain, film grain, breathing gradients, rolling-label micro-interactions, EN/DE switch.

**Performance & accessibility.**
- The 3D chunk is lazy-loaded and pauses rendering when it is off screen.
- Phones get a lighter scene: no shadows, lower DPR, cheaper glass.
- Photos are WebP in two sizes (`-sm` 828 px / `-lg` 1920 px; portraits 480/900) via `srcset`.
- `prefers-reduced-motion` replaces the 3D scene with a photo, turns off Lenis and pinning, and leaves only fades.
- Alt text everywhere, focus styles, a skip link, and a focus-trapped modal that closes with Esc.

Checked with Playwright at 390 px and 1440 px (normal and reduced motion): no console errors, no horizontal overflow (`scripts/shots.mjs`).

## Connectors & sources

- **Curated Design.** Research with `search_sites` / `search_sections` / `plan_page` for "luxury real estate", "architecture studio 3d scroll", "luxury hotel interior", "interior design", "editorial serif" and more. References used for structure and rhythm only (no copy or branding): Base Habitation (hero + language switch), Neria Katz Portfolio (dark catalogue, stats, reviews), Lue Studio and Oratory Design Studio (footer, review layout). `get_design_system` returned no design.md yet for these sites, so the tokens are an original synthesis.
- **21st.dev.** Patterns researched with `search` and rebuilt on GSAP to fit the palette, because component source is paid:
  - [Hero Scrub](https://21st.dev/@jean.duthil13/components/hero-scrub) (pinned scrubbed hero)
  - [3D Animation](https://21st.dev/@dhileepkumargm/components/3d-animation) (3D corridor)
  - [Property Preview Card](https://21st.dev/@shadcnspace/components/card-02) and [3D Flip Card](https://21st.dev/@shadcnspace/components/card-14) (property cards)
  - [Vertical Cut Reveal](https://21st.dev/@danielpetho/components/vertical-cut-reveal) and [Reveal Text](https://21st.dev/@paceui/components/reveal-text) (split text)
  - [Scroll animated timeline](https://21st.dev/@ibrandify/components/scroll-timeline)
  - [Testimonials Marquee](https://21st.dev/@shadcnspace/components/marquee-01)
  - [Magnetic Button](https://21st.dev/@mohammadshehadeh/components/magnetic-button)
- **OriginKit.** Searched with `search`. The [Text Button Cursor](https://www.originkit.dev/components/text-button-cursor) and [Circle Cursor](https://www.originkit.dev/components/circle-cursor) were the references for the custom cursor; their source is paid, so the cursor here is original.
- **Unsplash.** 23 photos found with `search_photos` and fetched with `download_asset`, then converted to WebP by `scripts/fetch-photos.mjs` (list in `scripts/photos.json`).
- **Canva.** Logo concept (`public/brand/logo-canva.webp`, redrawn as SVG for the animated loader/favicon) and Open Graph image (`public/brand/og.jpg`).
- **3D.** No suitable house model on 21st.dev/OriginKit, so the villa is procedural geometry in React Three Fiber (`src/components/three`).

### Photo credits (Unsplash)

- [Avi Werde](https://unsplash.com/@aviwerde) — [photo](https://unsplash.com/photos/hHz4yrvxwlA)
- [Frames For Your Heart](https://unsplash.com/@framesforyourheart) — [photo](https://unsplash.com/photos/mR1CIDduGLc), [photo](https://unsplash.com/photos/2d4lAQAlbDA)
- [Florian Schmidinger](https://unsplash.com/@fensterschmidinger) — [photo](https://unsplash.com/photos/b_79nOqf95I)
- [Salman Saqib](https://unsplash.com/@salmansaqib) — [photo](https://unsplash.com/photos/z6UAWpQAhXs)
- [Tobias Wilden](https://unsplash.com/@tobiasw) — [photo](https://unsplash.com/photos/4453DIQWtsQ)
- [Marlene Céline Nordvik](https://unsplash.com/@zarlinaa) — [photo](https://unsplash.com/photos/5q1KnUjtjaM)
- [Francesca Tosolini](https://unsplash.com/@fromitaly) — [photo](https://unsplash.com/photos/tHkJAMcO3QE)
- [Blvck Paris](https://unsplash.com/@blvckparis) — [photo](https://unsplash.com/photos/ckBxIZmpXJE)
- [KKY](https://unsplash.com/@kkykkky) — [photo](https://unsplash.com/photos/h30xW8X5CP4)
- [Vangel Dimo](https://unsplash.com/@vangeldimo) — [photo](https://unsplash.com/photos/qFbauOaA9UY)
- [Aalo Lens](https://unsplash.com/@aalolens) — [photo](https://unsplash.com/photos/Ez7fz5mavj0)
- [Medea Dzagnidze](https://unsplash.com/@medeadza) — [photo](https://unsplash.com/photos/1jy1WNfqHos)
- [Valton Myrtaj](https://unsplash.com/@valtonmyrtaj) — [photo](https://unsplash.com/photos/mmAo_lkAOiY)
- [Mike Chavarri](https://unsplash.com/@mikechv) — [photo](https://unsplash.com/photos/kZokA2VTKn4)
- [Daniel R.](https://unsplash.com/@misterjackdaniel) — [photo](https://unsplash.com/photos/y2HU2cdyGBg), [photo](https://unsplash.com/photos/2-0pjPRny4k)
- [Hugh Whyte](https://unsplash.com/@opixels) — [photo](https://unsplash.com/photos/KIfVGXf6Kzc)
- [Venti Views](https://unsplash.com/@ventiviews) — [photo](https://unsplash.com/photos/ZvMx2yxg_N0)
- [Aleksandra Sapozhnikova](https://unsplash.com/@rruprrup) — [photo](https://unsplash.com/photos/E5iwKLsLdyY)
- [Eric Ardito](https://unsplash.com/@ericardito) — [photo](https://unsplash.com/photos/MFYc1q-rV8k)
- [Christina @ wocintechchat.com](https://unsplash.com/@wocintechchat) — [photo](https://unsplash.com/photos/0Zx1bDv5BNY)
- [Phạm Duy Quang](https://unsplash.com/@phamduyquang) — [photo](https://unsplash.com/photos/QGr6H7pri-Q)

## Structure

```
src/
  components/three/   HeroScene (camera rig, sky, lights) · Villa (procedural model)
  components/ui/      Cursor · SplitText · MagneticButton · Counter · Logo · Img
  sections/           Loader · Nav · Hero · Stats · Featured · PropertyModal · Locations · Process · Walkthrough · Mortgage · Team · Reviews · Contact · Footer
  pages/              Home · Credits
  data/               content.ts (fictional listings, agents, reviews) · photos.ts (credits)
  i18n/               EN/DE strings + context
  lib/                GSAP/Lenis setup, media queries, image helpers
scripts/              fetch-photos.mjs · photos.json · shots.mjs (Playwright QA)
```
