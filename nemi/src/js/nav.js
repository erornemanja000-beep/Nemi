/* ---------- nav, menu, legal ---------- */
const nav = $('#nav'), burger = $('#burger'), menu = $('#menu');
const setMenu = (open) => {
  menu.classList.toggle('open', open); burger.setAttribute('aria-expanded', open);
  nav.classList.toggle('on-dark', open || nav.dataset.band === 'dark');
  if (lenis) open ? lenis.stop() : lenis.start();
};
burger.addEventListener('click', () => setMenu(!menu.classList.contains('open')));
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]'); if (!a) return;
  const id = a.getAttribute('href'); if (id.length < 2) return;
  e.preventDefault(); setMenu(false); goTo(id);
});
const setBand = (band) => {
  nav.dataset.band = band;
  nav.classList.toggle('on-dark', band === 'dark' || menu.classList.contains('open'));
  nav.classList.toggle('on-blue', band === 'blue');
};
if (hasG) {
  $$('[data-band]').forEach((sec) => ScrollTrigger.create({ trigger: sec, start: 'top 40px', end: 'bottom 40px',
    onToggle: (self) => { if (self.isActive) setBand(sec.dataset.band); } }));
  ScrollTrigger.create({ start: 24, onToggle: (self) => nav.classList.toggle('is-scrolled', self.isActive) });
}
addEventListener('scroll', () => { if (scrollY > 8) document.documentElement.classList.add('spoke'); }, { passive: true, once: true });
const legal = $('#legal');
$$('[data-legal]').forEach((b) => b.addEventListener('click', () => {
  if (!legal.showModal) return;
  legal.showModal(); if (lenis) lenis.stop();
  const sec = document.getElementById(b.dataset.legal);
  legal.scrollTop = sec ? sec.offsetTop - 20 : 0;
}));
$('#legalClose').addEventListener('click', () => legal.close());
legal.addEventListener('close', () => { if (lenis) lenis.start(); });
legal.addEventListener('click', (e) => { if (e.target === legal) legal.close(); });

/* ---------- cursor ---------- */
if (FINE && !RM && hasG) {
  const cur2 = $('#cursor');
  const qx = G.quickTo(cur2, 'x', { duration: .35, ease: 'power3' }), qy = G.quickTo(cur2, 'y', { duration: .35, ease: 'power3' });
  addEventListener('pointermove', (e) => { cur2.classList.add('on'); qx(e.clientX); qy(e.clientY); }, { passive: true });
  document.addEventListener('pointerover', (e) => cur2.classList.toggle('big', !!e.target.closest('a,button,input,select,textarea,.dev')));
  document.addEventListener('pointerleave', () => cur2.classList.remove('on'));
}
