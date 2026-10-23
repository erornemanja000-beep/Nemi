// O nama (skica: sekcija 9a). Levo dve fotografije (ONAMA-1 veća, ONAMA-2 manja preko njenog
// donjeg desnog ugla), desno naslov, podnaslov, tekst, demo red i dugme na #contact.
// Parallax (mapa-skrola): fotografije klize najviše 40 px dok sekcija prolazi kroz ekran, samo na
// desktopu i bez reduced motion (gsap.matchMedia sam vraća stanje kad se upit promeni). Pomera se
// omotač sa data-parallax (transform), a zaobljenje i senka su na unutrašnjem elementu.
// Telefon: fotografije iznad teksta, bez parallax-a. Tekst se pojavljuje preko reveal.ts.
import { useLayoutEffect, useRef } from 'react'
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'
import { gsap } from '../lib/motion'
import { useReveal } from '../lib/reveal'
import { DESKTOP_QUERY } from '../lib/useMedia'
import './sections.css'

const about = sections.about
const [photoMain, photoSmall] = about.photos

/** Pomeraj u px na svaku stranu (ukupno 2 × vrednost, najviše 40 px). */
const PARALLAX = { main: 8, small: 20 }

export function About() {
  const { tx, tf } = useLang()
  const root = useRef<HTMLElement>(null)
  const reveal = useReveal<HTMLDivElement>()

  useLayoutEffect(() => {
    const section = root.current
    if (!section) return
    const mm = gsap.matchMedia()
    mm.add(`${DESKTOP_QUERY} and (prefers-reduced-motion: no-preference)`, () => {
      section.querySelectorAll<HTMLElement>('[data-parallax]').forEach((el) => {
        const shift = Number(el.dataset.parallax) || 0
        gsap.fromTo(
          el,
          { y: shift },
          { y: -shift, ease: 'none', scrollTrigger: { trigger: section, start: 'top bottom', end: 'bottom top', scrub: true } },
        )
      })
    })
    return () => mm.revert()
  }, [])

  return (
    <section ref={root} id="about" aria-labelledby="t-about" className="scroll-mt-header bg-surface px-gutter py-s8 text-text md:py-s9">
      <div className="mx-auto grid max-w-site items-center gap-s7 lg:grid-cols-[6fr_5fr] lg:gap-s8">
        {/* fotografije: ONAMA-2 je u drugom redu i negativnom marginom prelazi preko ONAMA-1 */}
        <div className="grid grid-cols-12">
          <div data-parallax={PARALLAX.main} className="about-photo col-span-10 col-start-1">
            <Photo
              id={photoMain}
              sizes="(min-width: 64rem) 46vw, 84vw"
              className="block aspect-[828/806] h-auto w-full rounded-card object-cover shadow-soft"
            />
          </div>
          <div data-parallax={PARALLAX.small} className="about-photo relative col-span-6 col-start-7 -mt-[26%]">
            <Photo
              id={photoSmall}
              sizes="(min-width: 64rem) 28vw, 50vw"
              className="block aspect-[3/2] h-auto w-full rounded-card border-4 border-surface object-cover shadow-float"
            />
          </div>
        </div>

        <div ref={reveal}>
          <div data-reveal>
            <h2 id="t-about" className="type-display m-0 text-section leading-none">{tx(about.title)}</h2>
            <p className="mt-s3 mb-0 font-bold">{tx(about.subtitle)}</p>
            <p className="mt-s4 mb-0 max-w-[34rem]">{tf(about.text)}</p>
            <p className="mt-s5 mb-s5 max-w-[34rem] border-t border-dashed border-line-strong pt-s3 text-muted md:text-small">{tx(about.demo)}</p>
            <Button href={about.cta.href}>{tx(about.cta.label)}</Button>
          </div>
        </div>
      </div>
    </section>
  )
}
