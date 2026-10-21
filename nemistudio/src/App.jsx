import { useEffect, useState } from 'react';
import { initScroll, scrollToY, stop, resume } from './scroll.js';
import { start as startFrames } from './film/frames.js';
import Film from './film/Film.jsx';
import { Nav, Pill, Preloader } from './components/Chrome.jsx';
import Intro, { shouldPlayIntro } from './components/Intro.jsx';
import { Services, Showroom, Process, Faq, Contact, Footer } from './components/Sections.jsx';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export default function App() {
  const [loaded, setLoaded] = useState(false);
  const [intro] = useState(shouldPlayIntro);
  const [introDone, setIntroDone] = useState(!intro);
  const ready = loaded && introDone;
  useEffect(() => {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    scrollToY(0, true);
    initScroll();
    startFrames();
  }, []);
  // no scrolling while the intro plays
  useEffect(() => { (introDone ? resume : stop)(); }, [introDone]);
  useEffect(() => {
    if (!ready) return;
    document.documentElement.classList.add('is-ready');
    ScrollTrigger.refresh();
    // deep links (#kontakt) after the layout settles
    if (location.hash) setTimeout(() => { const el = document.querySelector(location.hash); if (el) scrollToY(el.offsetTop, true); }, 300);
  }, [ready]);
  return (
    <>
      <Preloader onDone={() => setLoaded(true)} />
      {intro && !introDone && <Intro onDone={() => setIntroDone(true)} />}
      <Nav />
      <main>
        <Film ready={ready} />
        <Services />
        <Showroom />
        <Process />
        <Faq />
        <Contact />
      </main>
      <Footer />
      <Pill />
    </>
  );
}
