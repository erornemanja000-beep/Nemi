// Dev harness (Z7), samo u `npm run dev` na /dev/chapters: tri sloja od 100vh (telefon 100svh) sa
// data-chapter i svim statičnim delovima poglavlja na mestu, za poređenje sa mockup-1440.png i
// mockup-390.png. Sive kutije stoje gde će biti platna sekvenci (Z5/Z12): desktop po merama
// predmeta iz dizajn.md (mlin 440×810, kuvalo ~490, dripper sa bokalom 380×560, šolja 520×470),
// telefon u scenama od 28, 30 i 31 rem (mockup.html). Jezik se menja preko konteksta (dole levo).
import { useEffect, useRef } from 'react'
import { chapters } from '../content/chapters'
import type { ChapterId } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { setActiveChapter } from '../lib/chapterStore'
import { BackWord } from '../story/BackWord'
import { ChapterNav } from '../story/ChapterNav'
import { ChapterText } from '../story/ChapterText'
import { SceneBackdrop } from '../story/SceneBackdrop'
import { SipCards } from '../story/SipCards'
import { Sparkle } from '../story/Sparkle'

/** Mesta predmeta iz mockup.html (.obj--*): telefon u px scene, desktop u % sloja. */
const objects: Record<ChapterId, { label: string; className: string }[]> = {
  grind: [
    {
      label: 'Mühle 440 × 810',
      className:
        'bottom-0 left-1/2 w-[14.5rem] -translate-x-[38%] aspect-[440/810] desk:bottom-[10%] desk:left-[46.5%] desk:w-[min(30.5vw,27.5rem)] desk:translate-x-0',
    },
  ],
  pour: [
    {
      label: 'Kessel ~490',
      className: 'top-0 left-[calc(50%-6px)] w-[18.75rem] aspect-[600/420] desk:top-[max(4.1rem,7.4%)] desk:left-[calc(52%-.68vw)] desk:w-[min(34vw,30.6rem)]',
    },
    {
      label: 'Dripper + Karaffe 380 × 560',
      className: 'top-[15.5rem] left-1/2 w-[11.875rem] -translate-x-1/2 aspect-[380/560] desk:top-[49%] desk:left-[52%] desk:w-[min(26.4vw,23.75rem)]',
    },
  ],
  sip: [
    {
      label: 'Tasse 520 × 470',
      className: 'top-[4.5rem] left-[4%] w-[15.5rem] aspect-[520/470] desk:top-[37%] desk:left-[37.5%] desk:w-[min(36vw,32.5rem)]',
    },
  ],
}

function DevObjects({ chapter }: { chapter: ChapterId }) {
  return (
    <>
      {/* telefon: okvir platna = cela scena */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 border-2 border-dashed border-placeholder-line desk:hidden" />
      {objects[chapter].map((o) => (
        <div
          key={o.label}
          aria-hidden="true"
          className={`absolute z-(--z-object) grid place-items-center rounded-md border-2 border-dashed border-placeholder-line bg-placeholder/80 ${o.className}`}
        >
          <span className="rounded-pill bg-pp-paper px-[10px] py-[6px] font-label text-micro font-bold tracking-[.08em] text-pp-ink uppercase shadow-soft">
            Platno · {o.label}
          </span>
        </div>
      ))}
    </>
  )
}

export default function DevChapters() {
  const { lang, setLang } = useLang()
  const root = useRef<HTMLDivElement>(null)

  // boje headera prate sloj pod linijom headera (isto kao Story stub; pravu logiku piše Z12)
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
      setActiveChapter(id === 'grind' || id === 'pour' || id === 'sip' ? id : 'page')
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
      setActiveChapter('grind')
    }
  }, [])

  return (
    <main id="main">
      <div ref={root}>
        {chapters.items.map((chapter) => (
          <section key={chapter.id} id={chapter.id} data-chapter={chapter.id} aria-labelledby={`t-${chapter.id}`} className="ch-layer">
            <SceneBackdrop chapter={chapter.id} />
            <ChapterText chapter={chapter} />
            <div className="ch-stage">
              <BackWord chapter={chapter.id} />
              <DevObjects chapter={chapter.id} />
              {chapter.id === 'sip' && <Sparkle />}
            </div>
            {chapter.id === 'sip' && <SipCards />}
            <ChapterNav current={chapter.id} />
          </section>
        ))}
      </div>

      {/* sledeća sekcija na kremu, kao najava u mockup-u */}
      <div className="bg-pp-cream px-gutter py-s7 text-center text-pp-ink">
        <p className="m-0 font-label text-small text-pp-mute">DevChapters (Z7) · kraj priče</p>
      </div>

      {/* dev panel: jezik preko LangContext-a */}
      <div className="fixed bottom-s4 left-s4 z-[60] flex items-center gap-s1 rounded-pill bg-pp-ink-deep p-s1 pl-s4 text-pp-cream-light shadow-float">
        <span className="font-label text-micro font-bold tracking-[.08em] uppercase">Dev · Z7</span>
        {(['en', 'de'] as const).map((l) => (
          <button
            key={l}
            type="button"
            aria-pressed={lang === l}
            onClick={() => setLang(l)}
            className="grid size-tap cursor-pointer place-items-center rounded-full border-0 bg-transparent font-label text-label font-bold uppercase text-pp-cream-light aria-pressed:bg-pp-cream-light aria-pressed:text-pp-ink-deep"
          >
            {l}
          </button>
        ))}
      </div>
    </main>
  )
}
