# Villa Showcase — scroll-driven demo site for real-estate clients

A cinematic one-page site for a (fictional) builder of coastal villas. While you scroll,
the camera flies down from the coast to an empty plot, the villa rises out of the ground,
then three more villas follow, ending inside a living room at night.

All pictures and video were generated with AI. The brand **OSTRIA** and every villa,
address and number on the page are made up, so the site can be shown as a concept to
any client.

## Re-brand it for a client (no coding)

Everything a visitor reads lives in **`public/content.json`**:

| Field | What it changes |
|---|---|
| `brand.name` | Logo, giant title on the first screen, footer, browser tab |
| `intro` | Small text on the first screen, plot label, construction years |
| `villas[].name`, `location`, `year`, `status`, `area`, `bedrooms`, `summary` | Each villa's title and details (keep the `id` values as they are) |
| `manifesto`, `process`, `plan` | Texts in the middle sections |
| `contact` | Email, phone, address, form labels |
| `footer.note` | Small line at the bottom |

Save the file and reload the page. In a built site (`dist/`) you can edit
`dist/content.json` directly, no rebuild needed.

### German version

The German text lives in **`public/content.de.json`** (same fields, plus `lang`, `locale`
and the small `ui` labels). Run it with `npm run dev:de`; build it with `npm run build:de`,
which writes to `dist-de/` and loads `content.de.json` (see `.env.de`). Another language
works the same way: copy the file, translate it, add an `.env.<lang>` with
`VITE_CONTENT=content.<lang>.json` and build with `--mode <lang>`.

Long words in the big titles are shrunk automatically so they never overflow.

## Run it

```bash
npm install
npm run dev        # http://localhost:5173
```

## Build

```bash
npm run build      # outputs a static site to dist/
npm run preview    # serve dist/ locally
```

`dist/` uses relative paths, so it works from any folder: GitHub Pages, Netlify
(base directory `VillaShowcase`, publish directory `VillaShowcase/dist`), or straight
from a laptop.

## How it works

- `public/media/seq/<clip>/001.jpg …` — each AI video exported as 80 frames. A `<canvas>`
  paints the frame that matches the scroll position (`src/sequence.ts`). Frames load
  coarse-first (every 8th, then every 4th …) so a clip is usable before it is complete.
- `public/media/img/` — stills used as posters, previews and section images.
- `src/main.ts` — GSAP ScrollTrigger timelines for each scene, Lenis smooth scrolling.
- `src/content.ts` — turns `content.json` into the page markup.
- `src/style.css` — layout and type. Fonts: Archivo (expanded), Instrument Serif, IBM Plex Mono.

## Swapping the imagery

Replace a clip by exporting new frames into the same folder with the same names
(`001.jpg` … `080.jpg`, 1280 px wide) and update `public/media/seq/manifest.json` if the
count changes. Stills in `public/media/img/` can be replaced 1:1 (same file names).
