import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Img } from '../components/ui/Img'
import { SplitText } from '../components/ui/SplitText'
import { photos, unsplashPhoto, unsplashProfile, type PhotoName } from '../data/photos'
import { useLang } from '../i18n/LangContext'
import { Footer } from '../sections/Footer'

const tools = [
  ['Curated Design', 'Research: Base Habitation, Neria Katz, Lue Studio, Oratory', 'https://curated.design'],
  ['21st.dev', 'Component patterns: Hero Scrub, Vertical Cut Reveal, Property Preview Card, Scroll Timeline, Testimonials Marquee, Magnetic Button, 3D Animation', 'https://21st.dev'],
  ['OriginKit', 'Cursor references (Text Button Cursor, Circle Cursor)', 'https://www.originkit.dev'],
  ['Unsplash', 'All photography', 'https://unsplash.com/?utm_source=vista_estates&utm_medium=referral'],
  ['Canva', 'Logo concept and Open Graph image', 'https://www.canva.com'],
  ['Three.js · React Three Fiber · GSAP · Lenis', '3D scene and motion', 'https://threejs.org'],
]

export default function Credits() {
  const { t } = useLang()
  useEffect(() => {
    window.dispatchEvent(new Event('vista:reveal'))
  }, [])
  return (
    <>
      <main id="main" className="gutter pb-24 pt-36">
        <Link to="/" className="eyebrow hover:text-sand">← {t.credits.back}</Link>
        <SplitText as="h1" text={t.credits.title} className="display mt-8 text-7xl md:text-[10vw]" />
        <p className="mt-6 max-w-lg text-lg text-sand/80">{t.credits.lead}</p>
        <ul className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {(Object.keys(photos) as PhotoName[]).map((name) => {
            const p = photos[name]
            return (
              <li key={name}>
                <a href={unsplashPhoto(p.id)} target="_blank" rel="noreferrer" className="group block" data-cursor="Open">
                  <div className="aspect-[4/3] overflow-hidden rounded-[2px] bg-stone-900">
                    <Img name={name} sizes="(min-width: 1024px) 24vw, 46vw" className="h-full w-full object-cover transition-transform duration-1000 group-hover:scale-105" />
                  </div>
                </a>
                <p className="mt-3 text-sm">
                  {t.credits.photo}{' '}
                  <a href={unsplashProfile(p.user)} target="_blank" rel="noreferrer" className="underline decoration-sand/30 underline-offset-4 hover:text-ember">{p.author}</a>
                </p>
              </li>
            )
          })}
        </ul>
        <h2 className="eyebrow mt-24">{t.credits.tools}</h2>
        <ul className="mt-6 divide-y divide-sand/10 border-y border-sand/10">
          {tools.map(([name, what, href]) => (
            <li key={name} className="grid gap-2 py-5 md:grid-cols-[1fr_2fr]">
              <a href={href} target="_blank" rel="noreferrer" className="font-serif text-2xl hover:text-ember">{name} ↗</a>
              <span className="text-sand/70">{what}</span>
            </li>
          ))}
        </ul>
      </main>
      <Footer />
    </>
  )
}
