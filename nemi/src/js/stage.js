/* ---------- stage: the opening film (hero pin) ----------
   one pinned section, one scrubbed timeline. Beats (progress 0..1):
   .00-.08 device untilts, copy leaves          .06-.26 sketch -> words -> image -> colour
   .29-.37 device zooms to cover the screen     .365-.395 blue wipe hands over to the full-screen layer
   .45-.51 iris cut to the second industry      .56-.62 slice cut to the third
   .65-.69 zoom-blur into the type montage      .68-.86 eight hard cuts, speeding up
   .86-.90 "and every other industry"           .90-.95 wall of 12 concepts rises   .96-1 wall flies off */
document.documentElement.classList.toggle('rm', RM || !hasG);
const heroMinis = minis.filter((m) => m.closest('.hero-stage'));
heroMinis.forEach((m) => renderMini(m, stateOf(0)));
const steps = $$('#steps li');
const full = $('#stgFull');
const layA = $('.stg-a', full), layB = $('.stg-b', full);
const msA = $('.ms', layA), msB = $('.ms', layB);
const tagA = $('.stg-tag', layA), tagB = $('.stg-tag', layB);
const cards = $$('.stg-card', full);
const CONCEPT = '{{Konzept||Concept}}';
const byId = (id) => IND.findIndex((d) => d.id === id);
const fullShow = (ms, tag, id) => {
  const i = byId(id);
  renderMini(ms, stateOf(i));
  setK(ms, 1); ms.classList.add('is-live');
  tag.textContent = decode(CONCEPT + ' · ' + IND[i].label);
};
fullShow(msA, tagA, 'cafe');
fullShow(msB, tagB, 'law');

// keep every montage word on one line inside the screen
const fitWords = () => cards.forEach((c) => {
  const w = $('.stg-word', c);
  if (!w || c.classList.contains('c9')) return;
  w.style.fontSize = '';
  const max = c.clientWidth - 2 * Math.max(16, innerWidth * .04);
  const fs = parseFloat(getComputedStyle(w).fontSize);
  if (w.scrollWidth > max && max > 0) w.style.fontSize = Math.floor(fs * max / w.scrollWidth) + 'px';
});

// wall tiles load after the page is idle
const loadWall = () => $$('.stg-wall img[data-src]', full).forEach((im) => { im.src = im.dataset.src; im.removeAttribute('data-src'); });

let stepIdx = 0, cardIdx = -1, aId = 'cafe';
function setCard(i) {
  if (i === cardIdx) return;
  cardIdx = i;
  cards.forEach((c, k) => c.classList.toggle('on', k === i));
  if (i < 0) return;
  emit('cut', { kind: 'hard' });
  const c = cards[i];
  if (hasG && !RM) {
    G.fromTo($('.stg-word', c), { yPercent: 14, opacity: 0 }, { yPercent: 0, opacity: 1, duration: .38, ease: 'power3.out', overwrite: true });
    G.fromTo($('.stg-sub', c) || {}, { opacity: 0 }, { opacity: 1, duration: .3, delay: .12, overwrite: true });
    const flash = $('.stg-flash', c);
    if (flash) G.fromTo(flash, { opacity: .95 }, { opacity: 0, duration: .45, ease: 'power2.out' });
  }
}
const BEATS = [.38, .45, .56, .645];
let lastP = 0;
function filmProgress(p, ms) {
  BEATS.forEach((b) => { if ((lastP < b) !== (p < b)) emit('cut', { kind: 'scene' }); });
  lastP = p;
  const s = p < .1 ? 0 : p < .15 ? 1 : p < .2 ? 2 : p < .27 ? 3 : 4;
  if (s !== stepIdx) { stepIdx = s; steps.forEach((li, i) => li.classList.toggle('on', i === s)); }
  ms.classList.toggle('is-live', p > .25);
  if (p > .02) document.documentElement.classList.add('spoke');
  const want = p < .59 ? 'cafe' : 'auto';
  if (want !== aId) { aId = want; fullShow(msA, tagA, want); }
  let ci = -1;
  if (p >= .675 && p < .86) ci = Math.min(7, Math.floor(8 * Math.pow((p - .675) / .185, 1.45)));
  else if (p >= .86) ci = 8;
  setCard(ci);
}

if (hasG) {
  const mm = G.matchMedia();
  mm.add({ desk: '(min-width: 821px)', mob: '(max-width: 820px)', rm: '(prefers-reduced-motion: reduce)' }, (ctx) => {
    const { desk, rm } = ctx.conditions;
    const dev = desk ? $('#heroDesk') : $('#heroPhone');
    const ms = dev.querySelector('.ms');
    if (rm) { setK(ms, 1); ms.classList.add('is-live'); loadWall(); return; }
    setK(ms, 0);
    stepIdx = 0; cardIdx = -1;
    renderMini(ms, stateOf(0));
    fitWords();
    // takeover: scale the device until its screen covers the viewport
    const scr = dev.querySelector('.dev-scr');
    const cover = () => Math.max(innerWidth / scr.offsetWidth, innerHeight / scr.offsetHeight) * 1.04;
    const coverY = () => {
      const top = parseFloat(getComputedStyle(dev).top) || innerHeight * .54;   // device centre (it is centred with yPercent -50)
      const shift = scr.offsetTop + scr.offsetHeight / 2 - dev.offsetHeight / 2; // screen centre below device centre (browser bar)
      return innerHeight / 2 - top - shift * cover();
    };
    const from = desk
      ? { xPercent: -50, yPercent: -50, x: () => innerWidth * .23, y: () => innerHeight * .02, rotationY: -26, rotationX: 9, rotationZ: 1.5, scale: .72 }
      : { xPercent: -50, yPercent: -50, x: 0, y: () => innerHeight * .5, rotationY: 0, rotationX: 16, rotationZ: 0, scale: .92 };
    const flat = { xPercent: -50, yPercent: -50, x: 0, y: 0, rotationY: 0, rotationX: 0, rotationZ: 0, scale: 1 };
    const wipe = $('.stg-wipe', full), slices = $$('.stg-slices i', full), cardsBox = $('.stg-cards', full);
    const wall = $('.stg-wall', full), wallIn = $('.stg-wall-in', full);
    const tl = G.timeline({
      defaults: { ease: 'none' },
      scrollTrigger: {
        id: 'stage', trigger: '.hero', start: 'top top', end: desk ? '+=460%' : '+=400%', pin: true, scrub: desk ? .6 : .35,
        anticipatePin: 1, invalidateOnRefresh: true, onUpdate: (self) => filmProgress(self.progress, ms),
        onRefresh: fitWords
      }
    });
    // every tween is a fromTo with explicit starts; later tweens on the same target use immediateRender:false
    tl.fromTo(dev, from, Object.assign({}, flat, { ease: 'power2.inOut', duration: .08 }), 0)
      .fromTo('.hero-copy', { y: 0, autoAlpha: 1 }, { y: desk ? -70 : -120, autoAlpha: 0, ease: 'power1.in', duration: .06 }, .01)
      .fromTo('.hint', { autoAlpha: 1 }, { autoAlpha: 0, duration: .03 }, 0)
      .fromTo(ms, { '--k-txt': 0 }, { '--k-txt': 1, duration: .07 }, .06)
      .fromTo(ms, { '--k-img': 0 }, { '--k-img': 1, duration: .06 }, .13)
      .fromTo(ms, { '--k-col': 0 }, { '--k-col': 1, duration: .07 }, .19)
      .fromTo('#steps', { autoAlpha: 1 }, { autoAlpha: 0, duration: .03 }, .29)
      .fromTo(dev, flat, Object.assign({}, flat, { scale: cover, y: coverY, ease: 'power2.in', duration: .08, immediateRender: false }), .29)
      .fromTo(wipe, { scaleX: 0, transformOrigin: '0% 50%' }, { scaleX: 1, duration: .015, ease: 'power2.in' }, .365)
      .fromTo(full, { autoAlpha: 0 }, { autoAlpha: 1, duration: .001 }, .38)
      .fromTo(dev, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, .381)
      .fromTo(wipe, { scaleX: 1, transformOrigin: '100% 50%' }, { scaleX: 0, duration: .015, ease: 'power2.out', immediateRender: false }, .38)
      .fromTo(layB, { clipPath: 'circle(0% at 50% 55%)', autoAlpha: 1 }, { clipPath: 'circle(76% at 50% 55%)', duration: .06, ease: 'power2.inOut' }, .45)
      .fromTo(slices, { scaleY: 0, transformOrigin: '50% 0%' }, { scaleY: 1, duration: .02, stagger: .004, ease: 'power2.in' }, .56)
      .fromTo(layB, { autoAlpha: 1 }, { autoAlpha: 0, duration: .001, immediateRender: false }, .59)
      .fromTo(slices, { scaleY: 1, transformOrigin: '50% 100%' }, { scaleY: 0, duration: .02, stagger: .004, ease: 'power2.out', immediateRender: false }, .592)
      .fromTo(layA, { scale: 1, filter: 'blur(0px)', autoAlpha: 1 }, { scale: 1.28, filter: 'blur(14px)', autoAlpha: 0, duration: .04, ease: 'power2.in' }, .645)
      .fromTo(cardsBox, { autoAlpha: 0 }, { autoAlpha: 1, duration: .015 }, .668)
      .fromTo(cardsBox, { autoAlpha: 1, scale: 1 }, { autoAlpha: 0, scale: .92, duration: .025, immediateRender: false }, .9)
      .fromTo(wall, { autoAlpha: 0 }, { autoAlpha: 1, duration: .01 }, .9)
      .fromTo(wallIn, { y: () => innerHeight * .7, rotationX: 28, scale: .86 }, { y: 0, rotationX: 0, scale: 1, duration: .05, ease: 'power3.out' }, .9)
      .fromTo(wallIn, { y: 0, rotationX: 0, rotationZ: 0, scale: 1 }, { y: () => -innerHeight * 1.25, rotationX: 55, rotationZ: -12, scale: .9, duration: .04, ease: 'power2.in', immediateRender: false }, .96)
      .fromTo('.stg-skip', { autoAlpha: 1 }, { autoAlpha: 0, duration: .02, immediateRender: false }, .95);
    // on phones the skip link shares the top edge with the hero copy, so it appears once the copy has left
    if (!desk) tl.fromTo('.stg-skip', { autoAlpha: 0 }, { autoAlpha: 1, duration: .02 }, .05);
    return () => { setK(ms, 1); renderMini(ms, stateOf(0)); setCard(-1); aId = 'cafe'; fullShow(msA, tagA, 'cafe'); };
  });
  setTimeout(loadWall, 1800);
  addEventListener('resize', fitWords);
} else {
  heroMinis.forEach((m) => { setK(m, 1); m.classList.add('is-live'); });
  loadWall();
}
