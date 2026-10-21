import { useCallback, useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Contact } from '../sections/Contact'
import { Featured } from '../sections/Featured'
import { Footer } from '../sections/Footer'
import { Hero } from '../sections/Hero'
import { Loader } from '../sections/Loader'
import { Locations } from '../sections/Locations'
import { Mortgage } from '../sections/Mortgage'
import { Process } from '../sections/Process'
import { Reviews } from '../sections/Reviews'
import { Stats } from '../sections/Stats'
import { Team } from '../sections/Team'
import { Walkthrough } from '../sections/Walkthrough'
import { ScrollTrigger } from '../lib/motion'

let introPlayed = false

export default function Home() {
  const [sceneReady, setSceneReady] = useState(false)
  const [loading, setLoading] = useState(!introPlayed)
  const onSceneReady = useCallback(() => setSceneReady(true), [])

  useEffect(() => {
    if (!introPlayed) return
    // returning from another page: skip the loader but still play the intro copy
    const id = requestAnimationFrame(() => window.dispatchEvent(new Event('vista:reveal')))
    return () => cancelAnimationFrame(id)
  }, [])

  useEffect(() => {
    const refresh = () => ScrollTrigger.refresh()
    window.addEventListener('load', refresh)
    return () => window.removeEventListener('load', refresh)
  }, [])

  return (
    <>
      {loading && (
        <Loader
          sceneReady={sceneReady}
          onDone={() => {
            introPlayed = true
            setLoading(false)
            ScrollTrigger.refresh()
          }}
        />
      )}
      <main>
        <Hero onSceneReady={onSceneReady} />
        <Stats />
        <Featured />
        <Locations />
        <Process />
        <Walkthrough />
        <Mortgage />
        <Team />
        <Reviews />
        <Contact />
      </main>
      <Footer />
      <Outlet />
    </>
  )
}
