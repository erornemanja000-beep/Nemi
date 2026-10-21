import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { gsap } from 'gsap';
import { LangProvider, useLang } from './i18n.jsx';
import { content } from './content.js';
import { useSmoothScroll, reducedMotion } from './hooks/useSmoothScroll.js';
import { world } from './world/state.js';
import { useWorldScroll } from './world/useWorldScroll.js';
import { Cursor } from './components/fx.jsx';
import Preloader from './components/Preloader.jsx';
import Nav from './components/Nav.jsx';
import Hero from './components/Hero.jsx';
import Manifesto from './components/Manifesto.jsx';
import Work, { pickProject } from './components/Work.jsx';
import Services from './components/Services.jsx';
import Scale from './components/Scale.jsx';
import Process from './components/Process.jsx';
import Packages from './components/Packages.jsx';
import Estimate from './components/Estimate.jsx';
import Faq from './components/Faq.jsx';
import Contact, { Outro } from './components/Contact.jsx';
import Footer from './components/Footer.jsx';

const Scene = lazy(() => import('./world/Scene.jsx'));
// vreme animacija ide po satu, i kad je jedan kadar spor (3D se prevodi u pozadini)
gsap.ticker.lagSmoothing(0);

function hasWebGL() {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch { return false; }
}

function Site() {
  const { t, lang } = useLang();
  const [ready, setReady] = useState(false);
  const [active, setActive] = useState(0);
  const webgl = useMemo(hasWebGL, []);

  useSmoothScroll(ready);
  useWorldScroll(ready && webgl, setActive);

  useEffect(() => {
    document.title = t.meta.title;
    document.querySelector('meta[name="description"]')?.setAttribute('content', t.meta.description);
  }, [t, lang]);

  useEffect(() => {
    document.documentElement.classList.toggle('is-loading', !ready);
  }, [ready]);

  const onLoaded = useCallback(() => {
    setReady(true);
    // znak se slaže oko jezgra čim zavesa krene gore
    gsap.to(world, { intro: 1, duration: reducedMotion() ? 0.01 : 2.4, ease: 'expo.out', delay: 0.15 });
  }, []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      {webgl && (
        <Suspense fallback={null}>
          <Scene projects={content.en.projects} onPick={pickProject} running={ready} />
        </Suspense>
      )}
      <Preloader onDone={onLoaded} />
      <Cursor />
      <Nav />
      <main id="main" className={webgl ? 'has-world' : 'no-world'}>
        <Hero ready={ready} />
        <Manifesto />
        <Work active={active} webgl={webgl} />
        <Services />
        <Scale />
        <Process />
        <Packages />
        <Estimate />
        <Faq />
        <Outro />
        <Contact />
      </main>
      <Footer />
      <div className="grain" aria-hidden="true" />
    </>
  );
}

export default function App() {
  return (
    <LangProvider>
      <Site />
    </LangProvider>
  );
}
