// Pojavljivanje pri ulasku u ekran (mapa-skrola: fade + 16 px, razmak 60 ms).
// Upotreba:
//   const ref = useReveal<HTMLDivElement>()
//   <div ref={ref}><article data-reveal>…</article><article data-reveal>…</article></div>
// Elementi sa data-reveal (i sam kontejner, ako ga ima) dobijaju .reveal-pending dok ne uđu u
// ekran, pa .reveal-in sa --reveal-delay. Novi elementi (npr. posle filtera) se hvataju sami.
// U reduced motion ništa se ne skriva. Klase su u src/index.css.
import { useEffect, useRef } from 'react'
import { isReducedMotion } from './useMedia'

const STAGGER_MS = 60
const MAX_STAGGER = 8 // posle 8 elemenata razmak se više ne povećava

export function useReveal<T extends HTMLElement>() {
  const ref = useRef<T>(null)

  useEffect(() => {
    const root = ref.current
    if (!root || isReducedMotion() || typeof IntersectionObserver === 'undefined') return

    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).map((e) => e.target as HTMLElement)
        // redosled u DOM-u, da razmak ide sleva nadesno i odozgo nadole
        visible.sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1))
        visible.forEach((el, i) => {
          io.unobserve(el)
          el.style.setProperty('--reveal-delay', `${Math.min(i, MAX_STAGGER) * STAGGER_MS}ms`)
          el.classList.remove('reveal-pending')
          el.classList.add('reveal-in')
        })
      },
      { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
    )

    const arm = () => {
      const items = root.matches('[data-reveal]') ? [root] : []
      items.push(...root.querySelectorAll<HTMLElement>('[data-reveal]'))
      for (const el of items) {
        if (el.classList.contains('reveal-in') || el.classList.contains('reveal-pending')) continue
        el.classList.add('reveal-pending')
        io.observe(el)
      }
    }
    arm()
    const mo = new MutationObserver(arm)
    mo.observe(root, { childList: true, subtree: true })

    return () => {
      mo.disconnect()
      io.disconnect()
      // posle odjave sve ostaje vidljivo
      root.querySelectorAll('.reveal-pending').forEach((el) => el.classList.remove('reveal-pending'))
      root.classList.remove('reveal-pending')
    }
  }, [])

  return ref
}
