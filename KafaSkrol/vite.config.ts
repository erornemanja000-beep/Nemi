import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig, type Plugin } from 'vite'
import { brand, fill } from './src/config/site.ts'
import { chapters } from './src/content/chapters.ts'
import { media } from './src/content/media.ts'
import { site } from './src/content/site.ts'

// Isti CSP i X-Robots-Tag kao u netlify.toml: uskladiti sa netlify.toml.
const securityHeaders = {
  'X-Robots-Tag': 'noindex, nofollow, noarchive',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Content-Security-Policy':
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; " +
    "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
}

/** Isti upit kao DESKTOP_QUERY u src/lib/useMedia.ts. */
const DESKTOP_QUERY = '(min-width: 64rem) and (min-height: 600px)'

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

/**
 * Upisuje u index.html ime brenda i SEO (EN) iz src/config/site.ts i src/content/site.ts, i pravi
 * <noscript> (skriven H1, tri poglavlja na EN, GRIND poster, demo red). index.html zato nema brend.
 */
function siteHtml(): Plugin {
  const title = fill(site.seo.title.en)
  const description = fill(site.seo.description.en)
  const head = [
    `<title>${esc(title)}</title>`,
    `<meta name="description" content="${esc(description)}" />`,
    `<meta property="og:type" content="website" />`,
    `<meta property="og:site_name" content="${esc(brand.name)}" />`,
    `<meta property="og:title" content="${esc(title)}" />`,
    `<meta property="og:description" content="${esc(description)}" />`,
  ].join('\n    ')

  const poster = media.seq.grind.poster
  const grindAlt = chapters.items[0].alt.en
  const noscript = [
    '<noscript>',
    '      <div class="noscript">',
    `        <h1 class="sr-only">${esc(fill(site.h1.en))}</h1>`,
    '        <picture>',
    `          <source media="${DESKTOP_QUERY}" srcset="${poster.d.src}" width="${poster.d.width}" height="${poster.d.height}" />`,
    `          <img src="${poster.m.src}" width="${poster.m.width}" height="${poster.m.height}" alt="${esc(grindAlt)}" />`,
    '        </picture>',
    ...chapters.items.map((c) => `        <h2>${esc(c.title.en)}</h2>\n        <p>${esc(fill(c.text.en))}</p>`),
    `        <p class="noscript__demo">${esc(fill(site.demo.en))}</p>`,
    '      </div>',
    '    </noscript>',
  ].join('\n')

  return {
    name: 'kafa-site-html',
    transformIndexHtml: {
      order: 'pre',
      handler(html) {
        for (const mark of ['<!--site-head-->', '<!--site-noscript-->']) {
          if (!html.includes(mark)) throw new Error(`index.html: nema oznake ${mark}`)
        }
        // predučitavanje u index.html mora da ima iste putanje postera kao media.ts (LCP)
        for (const src of [poster.d.src, poster.m.src]) {
          if (!html.includes(`href="${src}"`)) throw new Error(`index.html: predučitavanje ne odgovara media.ts (${src})`)
        }
        return html.replace('<!--site-head-->', head).replace('<!--site-noscript-->', noscript)
      },
    },
  }
}

export default defineConfig({
  base: '/',
  plugins: [siteHtml(), react(), tailwindcss()],
  build: {
    rolldownOptions: {
      output: {
        // isto što i manualChunks u RealEstates: gsap i lenis u zaseban chunk „motion"
        codeSplitting: {
          groups: [{ name: 'motion', test: /node_modules[\\/](gsap|lenis)[\\/]/ }],
        },
      },
    },
  },
  preview: {
    headers: securityHeaders,
  },
})
