// Početna: skriven H1, pa priča i sekcije redom (plan, Z1 tačka 16). Modal proizvoda (/p/:slug) je <Outlet />.
import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'
import { scrollToTarget } from '../lib/motion'
import { About } from '../sections/About'
import { BrewGuide } from '../sections/BrewGuide'
import { Contact } from '../sections/Contact'
import { Footer } from '../sections/Footer'
import { Shop } from '../sections/Shop'
import { Subscription } from '../sections/Subscription'
import { Story } from '../story/Story'

export default function Home() {
  const { tf } = useLang()

  // otvaranje sa sidrom (/#find-your-cup, /?brew=filter#find-your-cup): pregledač traži sidro pre
  // nego što React nacrta stranicu, pa se do njega skače posle prvog crtanja
  // (samo pri otvaranju; kasnije klikove na sidra vodi pregledač ili Lenis)
  useEffect(() => {
    const target = decodeURIComponent(window.location.hash.slice(1))
    if (!target) return
    const id = requestAnimationFrame(() => {
      const el = document.getElementById(target)
      if (el) scrollToTarget(el, true)
    })
    return () => cancelAnimationFrame(id)
  }, [])

  return (
    <>
      <main id="main">
        <h1 className="sr-only">{tf(site.h1)}</h1>
        <Story />
        <Shop />
        <Subscription />
        <About />
        <BrewGuide />
        <Contact />
      </main>
      <Footer />
      <Outlet />
    </>
  )
}
