/* ---------- services demos ---------- */
const dots = $('#dots');
dots.innerHTML = Array.from({ length: 55 }, (_, i) => '<i style="--d:' + ((i % 11) + Math.floor(i / 11)) + '"></i>').join('');
const dotEls = $$('i', dots);
if (FINE && !RM) {
  dots.parentElement.addEventListener('pointermove', (e) => {
    dots.classList.add('hot');
    dotEls.forEach((d) => {
      const r = d.getBoundingClientRect();
      const k = Math.max(0, 1 - Math.hypot(e.clientX - r.left - 4, e.clientY - r.top - 4) / 110);
      d.style.transform = 'scale(' + (1 + k * 2.2).toFixed(2) + ')';
      d.style.background = k > .35 ? 'var(--blue)' : '';
    });
  });
  dots.parentElement.addEventListener('pointerleave', () => { dots.classList.remove('hot'); dotEls.forEach((d) => { d.style.transform = ''; d.style.background = ''; }); });
}
const typed = $('#aiTyped');
typed.style.setProperty('--n', typed.textContent.length);
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .4 });
  $$('.demo').forEach((d) => io.observe(d));
} else $$('.demo').forEach((d) => d.classList.add('in'));
