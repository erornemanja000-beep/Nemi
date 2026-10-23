// Rute (plan, Interfejs 8) i globalni delovi: Header, ChatBubble, CartDrawer, Toast, Grain.
// BrowserRouter (ne HashRouter), da sidra u meniju rade kao obični linkovi; Netlify i vite preview
// vraćaju index.html za svaku rutu. Footer je zajednički za početnu, pravne stranice i Credits
// (raspored WithFooter); dev harness-i ga nemaju.
import { lazy, Suspense, useEffect } from 'react'
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom'
import { CartDrawer } from './components/CartDrawer'
import { ChatBubble } from './components/ChatBubble'
import { Grain } from './components/Grain'
import { Header } from './components/Header'
import { Toast } from './components/Toast'
import { legalPages } from './content/legal'
import { LangProvider } from './i18n/LangContext'
import { refreshAfterFonts, startSmoothScroll, stopSmoothScroll } from './lib/motion'
import Credits from './pages/Credits'
import Home from './pages/Home'
import Legal from './pages/Legal'
import ProductModal from './pages/ProductModal'
import { REDUCED_QUERY } from './lib/useMedia'
import { Footer } from './sections/Footer'

// Dev harness-i: lenjo, samo u `npm run dev` (u produkciji ih build izbacuje).
const DevSeq = import.meta.env.DEV ? lazy(() => import('./pages/DevSeq')) : null
const DevWave = import.meta.env.DEV ? lazy(() => import('./pages/DevWave')) : null
const DevChapters = import.meta.env.DEV ? lazy(() => import('./pages/DevChapters')) : null

/** Stranica, pa footer (posle <main>; modal proizvoda je u Outlet-u početne, iznad footera u DOM-u). */
function WithFooter() {
  return (
    <>
      <Outlet />
      <Footer />
    </>
  )
}

export default function App() {
  useEffect(() => {
    startSmoothScroll()
    refreshAfterFonts()
    // reduced motion uključen dok je stranica otvorena: Lenis se gasi
    const mql = window.matchMedia(REDUCED_QUERY)
    const onChange = () => (mql.matches ? stopSmoothScroll() : startSmoothScroll())
    mql.addEventListener('change', onChange)
    return () => mql.removeEventListener('change', onChange)
  }, [])

  return (
    <LangProvider>
      <BrowserRouter>
        <Header />
        <Routes>
          <Route element={<WithFooter />}>
            <Route path="/" element={<Home />}>
              <Route path="p/:slug" element={<ProductModal />} />
            </Route>
            {/* key na Legal: prelaz sa jedne pravne stranice na drugu (link u footeru) montira stranicu
                iznova, pa PageMeta ponovo skoči na vrh i fokusira H1 */}
            {legalPages.map((p) => (
              <Route key={p.slug} path={`/${p.slug}`} element={<Legal key={p.slug} slug={p.slug} />} />
            ))}
            <Route path="/credits" element={<Credits />} />
          </Route>
          {DevSeq && <Route path="/dev/seq" element={<Suspense><DevSeq /></Suspense>} />}
          {DevWave && <Route path="/dev/wave" element={<Suspense><DevWave /></Suspense>} />}
          {DevChapters && <Route path="/dev/chapters" element={<Suspense><DevChapters /></Suspense>} />}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <ChatBubble />
        <CartDrawer />
        <Toast />
        <Grain />
      </BrowserRouter>
    </LangProvider>
  )
}
