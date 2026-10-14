/* ---------- footer wordmark ---------- */
const word = $('#word'), letters = $$('#word > span');
let wordVisible = false;
if ('IntersectionObserver' in window) new IntersectionObserver((e) => { wordVisible = e[0].isIntersecting; }).observe(word);
const shape = (l, k) => { l.style.fontWeight = Math.round(260 + k * 540); l.style.fontStretch = (75 + k * 25).toFixed(1) + '%'; };
if (FINE && !RM) {
  addEventListener('pointermove', (e) => {
    if (!wordVisible) return;
    letters.forEach((l) => {
      const r = l.getBoundingClientRect();
      shape(l, Math.max(0, 1 - Math.abs(e.clientX - (r.left + r.width / 2)) / (innerWidth * .32)));
    });
  }, { passive: true });
} else if (hasG && !RM) {
  ScrollTrigger.create({ trigger: word, start: 'top bottom', end: 'bottom bottom', scrub: true,
    onUpdate: (self) => letters.forEach((l, i) => shape(l, Math.max(0, 1 - Math.abs(self.progress * 3 - i)))) });
}
