/* ---------- finale: credits, starring line, iris into the contact band ---------- */
const finName = $('#finName');
const DEFAULT_STAR = finName.textContent;
on('name', (name) => { finName.textContent = (name || '').trim() || DEFAULT_STAR; });
if (hasG && !RM) {
  $$('.fin-row, .fin-title').forEach((el) => {
    G.fromTo(el, { y: 40, opacity: .15 }, { y: 0, opacity: 1, ease: 'none', scrollTrigger: { trigger: el, start: 'top 95%', end: 'top 60%', scrub: true } });
  });
  const dot = $('.fin-dot'), star = $('.fin-star'), iris = $('.fin-iris');
  // a crisp circle (clip-path) opens from the full stop until it covers the screen; the contact band below is the same blue
  const at = () => {
    const d = dot.getBoundingClientRect(), s = star.getBoundingClientRect();
    return { x: d.left + d.width / 2 - s.left, y: d.top + d.height / 2 - s.top, r: d.width / 2 };
  };
  const circle = (big) => () => {
    const p = at();
    const r = big ? Math.hypot(Math.max(p.x, star.clientWidth - p.x), Math.max(p.y, star.clientHeight - p.y)) + 2 : p.r;
    return 'circle(' + r.toFixed(1) + 'px at ' + p.x.toFixed(1) + 'px ' + p.y.toFixed(1) + 'px)';
  };
  G.timeline({ scrollTrigger: { id: 'finale', trigger: star, start: 'top top', end: '+=85%', pin: true, scrub: .5, invalidateOnRefresh: true,
    onEnter: () => emit('cut', { kind: 'iris' }) } })
    .fromTo('.fin-star-l', { autoAlpha: 1 }, { autoAlpha: 0, duration: .2 }, .25)
    .fromTo(iris, { clipPath: circle(false) }, { clipPath: circle(true), duration: .75, ease: 'power2.in' }, .25);
}
