import { useEffect, useRef, useState } from 'react';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { initScroll, scrollToY, stop, resume } from './scroll.js';
import { useLang } from './i18n.jsx';
import { OPEN, PORTAL } from './content.js';
import { WORLDS, FILM_VH } from './worlds.js';
import { NemiBar, VideoIntro, ReplayButton, shouldPlayIntro } from './components/Chrome.jsx';
import { Words, Rich } from './components/Reveal.jsx';
import Portal from './components/Portal.jsx';
import WorldFilm from './components/WorldFilm.jsx';
import Outro from './components/Outro.jsx';
import { Sixth, Services, Process, Faq, Contact, Footer } from './components/Sections.jsx';

// the first screen: Nemi's line over the desk, before the camera dives into the laptop
function Opening({ ready }) {
  const { L } = useLang();
  return (
    <div className={`opening rv${ready ? ' on' : ''}`}>
      <p className="eye"><span className="dot" />{L(OPEN.eye)}</p>
      <h1 className="h-xxl"><Words lines={L(OPEN.h)} /></h1>
      <p className="lead"><Rich text={L(OPEN.p)} /></p>
      <div className="open-row">
        <span className="open-cue" aria-hidden="true"><i />{L(OPEN.scroll)}</span>
        <ReplayButton />
      </div>
    </div>
  );
}

// the caption on every later device: which sense lives in this screen
function Next({ i }) {
  const { L } = useLang();
  const w = WORLDS[i];
  return (
    <div className="next">
      <span className="next-n">0{i + 1}<small>/04</small></span>
      <p className="eye">{L(PORTAL.next)}</p>
      <b className="next-name">{L(w.sense)}</b>
      <em className="next-l">{L(w.name)}</em>
      <span className="open-cue" aria-hidden="true"><i />{L(PORTAL.enter)}</span>
    </div>
  );
}

function World({ w, i, introDone }) {
  const progress = useRef({ p: 0, q: 0, visible: false });
  return (
    <div className="site-wrap" data-site={i + 1}>
      <Portal
        id={w.id} device={w.device} label={w.id} film={FILM_VH} progress={progress}
        caption={i === 0 ? <Opening ready={introDone} /> : <Next i={i} />} dim={i === 0}
      >
        <WorldFilm world={w} progress={progress} index={i} />
      </Portal>
    </div>
  );
}

export default function App() {
  const [intro, setIntro] = useState(shouldPlayIntro);
  const [introDone, setIntroDone] = useState(!intro);
  const [run, setRun] = useState(0);
  // "Intro ansehen": back to the top and play the film again
  useEffect(() => {
    const again = () => { scrollToY(0, true); setRun((r) => r + 1); setIntro(true); setIntroDone(false); };
    addEventListener('nemi:intro', again);
    return () => removeEventListener('nemi:intro', again);
  }, []);
  useEffect(() => {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    scrollToY(0, true);
    initScroll();
  }, []);
  // no scrolling while the film plays
  useEffect(() => {
    (introDone ? resume : stop)();
    if (!introDone) return;
    document.documentElement.classList.add('is-ready');
    ScrollTrigger.refresh();
    if (location.hash && !run) setTimeout(() => { const el = document.querySelector(location.hash); if (el) scrollToY(el.getBoundingClientRect().top + scrollY, true); }, 300);
  }, [introDone]);
  return (
    <>
      {intro && !introDone && <VideoIntro key={run} onDone={() => setIntroDone(true)} />}
      <main id="top">
        {WORLDS.map((w, i) => <World w={w} i={i} key={w.id} introDone={introDone} />)}
        <Outro />
        <div data-site="0">
          <Sixth />
          <Services />
          <Process />
          <Faq />
          <Contact />
        </div>
      </main>
      <Footer />
      <NemiBar show={introDone} />
    </>
  );
}
