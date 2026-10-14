/* ---------- hero ---------- */
const heroMinis = minis.filter((m) => m.closest('.hero'));
const HERO_SEQ = [0, 8, 4, 6];
heroMinis.forEach((m) => renderMini(m, stateOf(0)));
const steps = $$('#steps li');
let heroIdx = 0, stepIdx = 0;
function swapHero(ms, i) {
  const wipe = ms.parentElement.querySelector('.wipe');
  const apply = () => renderMini(ms, stateOf(HERO_SEQ[i]));
  if (!hasG || RM || !wipe) { apply(); return; }
  G.killTweensOf(wipe);
  G.timeline().set(wipe, { transformOrigin: 'left center' }).to(wipe, { scaleX: 1, duration: .26, ease: 'power2.in' })
    .add(() => { apply(); emit('cut', { kind: 'wipe' }); }).set(wipe, { transformOrigin: 'right center' }).to(wipe, { scaleX: 0, duration: .36, ease: 'power2.out' });
}
function heroProgress(p, ms) {
  const s = p < .17 ? 0 : p < .34 ? 1 : p < .48 ? 2 : p < .64 ? 3 : 4;
  if (s !== stepIdx) { stepIdx = s; steps.forEach((li, i) => li.classList.toggle('on', i === s)); }
  ms.classList.toggle('is-live', p > .6);
  const tag = ms.closest('.dev').querySelector('.dev-tag');
  tag.classList.toggle('show', p > .64);
  const i = p < .7 ? 0 : p < .8 ? 1 : p < .9 ? 2 : 3;
  if (i !== heroIdx) { heroIdx = i; swapHero(ms, i); }
  if (p > .02) document.documentElement.classList.add('spoke');
}
if (hasG) {
  const mm = G.matchMedia();
  mm.add({ desk: '(min-width: 821px)', mob: '(max-width: 820px)', rm: '(prefers-reduced-motion: reduce)' }, (ctx) => {
    const { desk, rm } = ctx.conditions;
    const dev = desk ? $('#heroDesk') : $('#heroPhone');
    const ms = dev.querySelector('.ms');
    if (rm) { setK(ms, 1); ms.classList.add('is-live'); return; }
    setK(ms, 0);
    heroIdx = 0; stepIdx = 0;
    renderMini(ms, stateOf(0));
    const from = desk
    ? { xPercent: -50, yPercent: -50, x: () => innerWidth * .23, y: () => innerHeight * .02, rotationY: -26, rotationX: 9, rotationZ: 1.5, scale: .72 }
    : { xPercent: -50, yPercent: -50, x: 0, y: () => innerHeight * .34, rotationY: 0, rotationX: 16, rotationZ: 0, scale: .92 };
  const tl = G.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: {
        trigger: '.hero', start: 'top top', end: desk ? '+=250%' : '+=210%', pin: true, scrub: .6, anticipatePin: 1,
        invalidateOnRefresh: true, onUpdate: (self) => heroProgress(self.progress, ms)
      }
    });
    // fromTo everywhere: explicit start values, so a refresh never records a half-animated state as the start
  tl.fromTo(dev, from, { xPercent: -50, yPercent: -50, x: 0, y: 0, rotationY: 0, rotationX: 0, rotationZ: 0, scale: 1, ease: 'power2.inOut', duration: .3 }, 0)
    .fromTo('.hero-copy', { y: 0, autoAlpha: 1 }, { y: desk ? -70 : -120, autoAlpha: 0, ease: 'power1.in', duration: .18 }, .02)
    .fromTo('.hint', { autoAlpha: 1 }, { autoAlpha: 0, duration: .06 }, 0)
    .fromTo(ms, { '--k-txt': 0 }, { '--k-txt': 1, duration: .15 }, .19)
    .fromTo(ms, { '--k-img': 0 }, { '--k-img': 1, duration: .13 }, .34)
    .fromTo(ms, { '--k-col': 0 }, { '--k-col': 1, duration: .14 }, .48)
    .to({}, { duration: .38 }, .62);
  return () => { setK(ms, 1); renderMini(ms, stateOf(0)); };
  });
} else {
  heroMinis.forEach((m) => { setK(m, 1); m.classList.add('is-live'); });
}
