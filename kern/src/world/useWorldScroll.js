import { useEffect } from 'react';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { world, setSceneVisible } from './state.js';

// Preseci na strani pomeraju 3D svet: manifest = ulazak u jezgro, radovi = galerija, kraj = znak se slaže
export function useWorldScroll(ready, onActive) {
  useEffect(() => {
    if (!ready) return undefined;
    let topVisible = true;
    let outroVisible = false;
    const sync = () => {
      world.outroMode = outroVisible && !topVisible;
      setSceneVisible(topVisible || outroVisible);
    };
    const t = [
      ScrollTrigger.create({
        trigger: '#manifesto', start: 'top bottom', end: 'bottom bottom',
        onUpdate: (s) => { world.dive = s.progress; },
      }),
      ScrollTrigger.create({
        trigger: '#work', start: 'top bottom', end: 'top top',
        onUpdate: (s) => { world.workIn = s.progress; },
      }),
      ScrollTrigger.create({
        trigger: '#work', start: 'top top', end: 'bottom bottom',
        onUpdate: (s) => {
          world.work = s.progress;
          world.workRange = [s.start, s.end];
          onActive?.(Math.round(s.progress * (world.count - 1)));
        },
        onRefresh: (s) => { world.workRange = [s.start, s.end]; },
      }),
      // posle radova puni preseci pokrivaju scenu, pa se ona ne crta
      ScrollTrigger.create({
        trigger: '#work', start: 'bottom top',
        onEnter: () => { topVisible = false; sync(); },
        onLeaveBack: () => { topVisible = true; sync(); },
      }),
      ScrollTrigger.create({
        trigger: '#outro', start: 'top bottom', end: 'bottom top',
        onToggle: (s) => { outroVisible = s.isActive; sync(); },
      }),
      ScrollTrigger.create({
        trigger: '#outro', start: 'top bottom', end: 'center center',
        onUpdate: (s) => { world.outro = s.progress; },
      }),
    ];
    ScrollTrigger.refresh();
    return () => t.forEach((x) => x.kill());
  }, [ready, onActive]);
}
