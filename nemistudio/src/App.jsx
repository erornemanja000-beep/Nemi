import { useEffect, useState } from 'react';
import { initScroll, scrollToY } from './scroll.js';
import { start as startFrames } from './film/frames.js';
import Film from './film/Film.jsx';
import { Nav, Pill, Preloader } from './components/Chrome.jsx';
import { Services, Showroom, Process, Faq, Contact, Footer } from './components/Sections.jsx';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export default function App() {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    scrollToY(0, true);
    initScroll();
    startFrames();
  }, []);
  useEffect(() => {
    if (!ready) return;
    document.documentElement.classList.add('is-ready');
    ScrollTrigger.refresh();
    // deep links (#kontakt) after the layout settles
    if (location.hash) setTimeout(() => { const el = document.querySelector(location.hash); if (el) scrollToY(el.offsetTop, true); }, 300);
  }, [ready]);
  return (
    <>
      <Preloader onDone={() => setReady(true)} />
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
