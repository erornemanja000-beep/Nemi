// STUB iz Z1 (doradu radi Z12): tri statična bloka od 100vh sa posterima. Pravu priču (sticky scena,
// sekvence, talas, kartice) piše Z12. Slojevi već imaju konačne id-jeve, klase i data-chapter.
import { useEffect, useRef } from 'react'
import { chapters } from '../content/chapters'
import { media } from '../content/media'
import type { Chapter } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { setActiveChapter } from '../lib/chapterStore'
import { DESKTOP_QUERY } from '../lib/useMedia'
import { BackWord } from './BackWord'
import { ChapterText } from './ChapterText'

function Poster({ chapter, priority }: { chapter: Chapter; priority: boolean }) {
  const { tx } = useLang()
  const seq = media.seq[chapter.id]
  const { d, m } = seq.poster
  if (!seq.ready) {
    return <div role="img" aria-label={tx(chapter.alt)} className="aspect-[4/5] w-[min(80vw,28rem)] rounded-card bg-placeholder" />
  }
  return (
    <picture>
      <source media={DESKTOP_QUERY} srcSet={d.src} width={d.width} height={d.height} />
      <img
        src={m.src}
        width={m.width}
        height={m.height}
        alt={tx(chapter.alt)}
        fetchPriority={priority ? 'high' : 'auto'}
        loading={priority ? 'eager' : 'lazy'}
        decoding="async"
        className="h-auto max-h-[80svh] w-auto"
      />
    </picture>
  )
}

export function Story() {
  const root = useRef<HTMLDivElement>(null)

  // header prati sloj koji je pod linijom headera; ispod priče je 'page' (Z12 ovo radi u svom ScrollTrigger-u)
  useEffect(() => {
    const el = root.current
    if (!el) return
    const layers = [...el.querySelectorAll<HTMLElement>('[data-chapter]')]
    let frame = 0
    const update = () => {
      frame = 0
      const line = (document.querySelector('header')?.getBoundingClientRect().height ?? 64) / 2
      const layer = layers.find((s) => {
        const r = s.getBoundingClientRect()
        return r.top <= line && r.bottom > line
      })
      const id = layer?.dataset.chapter
      if (id === 'grind' || id === 'pour' || id === 'sip') setActiveChapter(id)
      else setActiveChapter(el.getBoundingClientRect().bottom <= line ? 'page' : 'grind')
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update)
    }
    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll)
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [])

  return (
    <div id="top" ref={root}>
      {chapters.items.map((chapter, i) => (
        <section
          key={chapter.id}
          id={chapter.id}
          data-chapter={chapter.id}
          aria-labelledby={`t-${chapter.id}`}
          className={`layer-${chapter.id} relative flex min-h-svh flex-col gap-s7 overflow-hidden bg-bg px-gutter pt-[calc(var(--header-h)+var(--space-5))] pb-s8 text-text lg:flex-row lg:items-center lg:justify-between lg:pl-inset`}
        >
          <BackWord chapter={chapter.id} className="absolute bottom-s5 left-[3%] z-(--z-word) lg:text-backword-xl" />
          <ChapterText chapter={chapter} className="lg:w-measure" />
          <div className="relative z-(--z-object) flex justify-center lg:flex-1">
            <Poster chapter={chapter} priority={i === 0} />
          </div>
        </section>
      ))}
    </div>
  )
}
