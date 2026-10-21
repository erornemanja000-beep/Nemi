import { useEffect, useLayoutEffect, useRef } from 'react'
import { HashRouter, Route, Routes, useLocation } from 'react-router-dom'
import { Cursor } from './components/ui/Cursor'
import { Logo } from './components/ui/Logo'
import { LangProvider } from './i18n/LangContext'
import { gsap, prefersReducedMotion, ScrollTrigger, scrollToTarget, startSmoothScroll } from './lib/motion'
import Credits from './pages/Credits'
import Home from './pages/Home'
import { PropertyModal } from './sections/PropertyModal'
import { Nav } from './sections/Nav'

/** Curtain that wipes away whenever the visitor moves between pages (not when a property modal opens). */
function PageTransition() {
  const { pathname } = useLocation()
  const page = pathname.startsWith('/property') ? '/' : pathname
  const curtain = useRef<HTMLDivElement>(null)
  const first = useRef(true)

  useLayoutEffect(() => {
    if (first.current) {
      first.current = false
      return
    }
    scrollToTarget(0, true)
    requestAnimationFrame(() => ScrollTrigger.refresh())
    if (prefersReducedMotion() || !curtain.current) return
    gsap.timeline()
      .set(curtain.current, { yPercent: 0, autoAlpha: 1 })
      .from(curtain.current.querySelector('svg'), { opacity: 0, y: 20, duration: 0.5 })
      .to(curtain.current, { yPercent: -100, duration: 1.1, ease: 'expo.inOut', delay: 0.15 })
      .set(curtain.current, { autoAlpha: 0 })
  }, [page])

  return (
    <div ref={curtain} aria-hidden="true" className="invisible fixed inset-0 z-[95] flex items-center justify-center bg-stone-900 text-sand">
      <Logo withWord={false} className="h-16 w-16" />
    </div>
  )
}

export default function App() {
  useEffect(() => {
    startSmoothScroll()
  }, [])

  return (
    <LangProvider>
      <HashRouter>
        <Nav />
        <PageTransition />
        <Routes>
          <Route path="/" element={<Home />}>
            <Route path="property/:slug" element={<PropertyModal />} />
          </Route>
          <Route path="/credits" element={<Credits />} />
          <Route path="*" element={<Home />} />
        </Routes>
        <Cursor />
        <div className="grain" aria-hidden="true" />
      </HashRouter>
    </LangProvider>
  )
}
