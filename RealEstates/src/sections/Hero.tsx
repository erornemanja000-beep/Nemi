import { lazy, Suspense, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Img } from '../components/ui/Img'
import { MagneticButton } from '../components/ui/MagneticButton'
import { SplitText } from '../components/ui/SplitText'
import { useLang } from '../i18n/LangContext'
import { gsap, scrollToTarget } from '../lib/motion'
import { useIsMobile, useReducedMotion } from '../lib/useReducedMotion'

const HeroScene = lazy(() => import('../components/three/HeroScene'))

function hasWebGL() {
  try {
    const c = document.createElement('canvas')
    return !!(c.getContext('webgl2') || c.getContext('webgl'))
  } catch {
    return false
  }
}

export function Hero({ onSceneReady }: { onSceneReady: () => void }) {
  const { t } = useLang()
  const reduced = useReducedMotion()
  const mobile = useIsMobile()
  const [webgl] = useState(hasWebGL)
  const use3D = webgl && !reduced
  const section = useRef<HTMLElement>(null)
  const progress = useRef(0)
  const pointer = useRef({ x: 0, y: 0 })
  const [active, setActive] = useState(true)

  useEffect(() => {
    if (!use3D) onSceneReady()
  }, [use3D, onSceneReady])

  // pause rendering when the hero is off screen
  useEffect(() => {
    const el = section.current
    if (!el) return
    const io = new IntersectionObserver(([e]) => setActive(e.isIntersecting), { rootMargin: '100px' })
    io.observe(el)
    return () => io.disconnect()
  }, [])

  useEffect(() => {
    if (mobile || reduced) return
    const move = (e: PointerEvent) => {
      pointer.current.x = (e.clientX / window.innerWidth - 0.5) * 2
      pointer.current.y = -(e.clientY / window.innerHeight - 0.5) * 2
    }
    window.addEventListener('pointermove', move)
    return () => window.removeEventListener('pointermove', move)
  }, [mobile, reduced])

  useLayoutEffect(() => {
    if (!use3D) return
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        defaults: { ease: 'none' },
        scrollTrigger: {
          trigger: section.current,
          start: 'top top',
          end: 'bottom bottom',
          scrub: 0.6,
          onUpdate: (self) => (progress.current = self.progress),
        },
      })
      // parallax layers drift at different speeds, intro copy leaves first
      tl.to('.hero-intro', { yPercent: -60, opacity: 0, duration: 0.22 }, 0.02)
        .to('.hero-cue', { opacity: 0, duration: 0.1 }, 0.05)
        .to('.hero-layer-slow', { yPercent: -40, duration: 1 }, 0)
        .to('.hero-layer-fast', { yPercent: -160, duration: 1 }, 0)
        .fromTo('.hero-sun', { yPercent: -40, opacity: 1 }, { yPercent: 160, opacity: 0.2, duration: 1 }, 0)
      gsap.utils.toArray<HTMLElement>('.hero-chapter').forEach((el, i) => {
        const at = [0.26, 0.5, 0.74][i]
        tl.fromTo(el, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.06 }, at).to(el, { opacity: 0, y: -40, duration: 0.06 }, at + 0.15)
      })
      tl.fromTo('.hero-fade', { opacity: 0 }, { opacity: 1, duration: 0.08 }, 0.92)
      tl.fromTo('.hero-progress', { scaleY: 0 }, { scaleY: 1, duration: 1 }, 0)
    }, section)
    return () => ctx.revert()
  }, [use3D])

  // intro copy appears once the loader curtain opens
  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      gsap.set('.hero-reveal', { opacity: 0, y: 24 })
      const play = () => gsap.to('.hero-reveal', { opacity: 1, y: 0, duration: 1.2, stagger: 0.12, delay: 0.6 })
      window.addEventListener('vista:reveal', play, { once: true })
      return () => window.removeEventListener('vista:reveal', play)
    }, section)
    return () => ctx.revert()
  }, [])

  const coords = '43°30′N  16°26′E'

  return (
    <section ref={section} id="top" aria-label="Vista Estates" className={`relative ${use3D ? (mobile ? 'h-[340svh]' : 'h-[420vh]') : 'h-[100svh]'}`}>
      <div className="sticky top-0 h-[100svh] overflow-hidden">
        {use3D ? (
          <div className="absolute inset-0">
            <Suspense fallback={null}>
              <HeroScene progress={progress} pointer={pointer} active={active} lite={mobile} onReady={onSceneReady} />
            </Suspense>
          </div>
        ) : (
          <Img name="villa-cypress" eager className="absolute inset-0 h-full w-full object-cover" fetchPriority="high" />
        )}

        {/* readability gradients */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-ink/55 via-transparent to-ink/70" />
        <div className="pointer-events-none absolute inset-y-0 left-0 w-2/3 bg-gradient-to-r from-ink/50 to-transparent" />

        {/* parallax ornaments */}
        <div aria-hidden="true" className="hero-layer-slow pointer-events-none absolute right-[10%] top-[30%] hidden md:block">
          <div className="hero-sun h-28 w-28 rounded-full bg-ember/80 blur-2xl" />
        </div>
        <div aria-hidden="true" className="hero-layer-fast eyebrow pointer-events-none absolute right-[var(--gutter)] top-[16%] hidden text-right md:block">
          <div>{coords}</div>
          <div className="mt-2 text-sand/50">Costa Aurea — 06:12 PM</div>
        </div>

        <div className="hero-intro gutter absolute inset-x-0 bottom-0 pb-[14svh] md:pb-[16vh]">
          <p className="hero-reveal eyebrow mb-6 text-sand/80">Vista Estates · Costa Aurea</p>
          <SplitText
            as="h1"
            text={t.hero.title}
            trigger="manual"
            delay={0.25}
            italicWords={[3]}
            className="display max-w-[14ch] text-[15vw] text-sand md:text-[8.5vw]"
          />
          <div className="mt-8 flex flex-col gap-6 md:mt-10 md:flex-row md:items-end md:justify-between">
            <p className="hero-reveal max-w-md text-base leading-relaxed text-sand/80 md:text-lg">{t.hero.lead}</p>
            <div className="hero-reveal flex items-center gap-4">
              <MagneticButton onClick={() => scrollToTarget('#properties')}>{t.hero.cta}</MagneticButton>
            </div>
          </div>
        </div>

        {use3D &&
          t.hero.chapters.map((c, i) => (
            <div key={c} aria-hidden="true" className="hero-chapter gutter pointer-events-none absolute inset-x-0 top-1/2 -translate-y-1/2 opacity-0">
              <p className="eyebrow text-ember">0{i + 1} / 03</p>
              <p className="display mt-3 text-[13vw] text-sand md:text-[7vw]">{c}</p>
            </div>
          ))}

        {use3D && (
          <>
            <div aria-hidden="true" className="absolute right-[var(--gutter)] top-1/2 hidden h-40 w-px -translate-y-1/2 bg-sand/20 md:block">
              <div className="hero-progress h-full w-full origin-top bg-ember" />
            </div>
            <div className="hero-reveal hero-cue eyebrow absolute bottom-6 left-1/2 flex -translate-x-1/2 flex-col items-center gap-3">
              <span>{t.hero.scroll}</span>
              <span className="relative block h-10 w-px overflow-hidden bg-sand/20">
                <span className="absolute inset-x-0 top-0 h-1/2 animate-[scrollcue_1.8s_ease-in-out_infinite] bg-sand" />
              </span>
            </div>
          </>
        )}
        <div className="hero-fade pointer-events-none absolute inset-0 bg-ink opacity-0" />
      </div>
      <style>{`@keyframes scrollcue{0%{transform:translateY(-100%)}100%{transform:translateY(200%)}}`}</style>
    </section>
  )
}
