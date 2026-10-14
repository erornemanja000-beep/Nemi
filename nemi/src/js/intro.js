/* ---------- intro ---------- */
function splitChars(el) {
  const out = [];
  const walk = (node) => {
    [...node.childNodes].forEach((n) => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        [...n.textContent].forEach((ch) => {
          if (ch === ' ') { frag.appendChild(document.createTextNode(' ')); return; }
          const s = document.createElement('span'); s.className = 'ch'; s.textContent = ch; frag.appendChild(s); out.push(s);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1) walk(n);
    });
  };
  walk(el);
  return out;
}
function intro() {
  document.documentElement.classList.add('ready');
  if (!hasG || RM) return;
  const chars = splitChars($('.hero-h'));
  G.from(chars, { yPercent: 118, duration: 1.15, ease: 'expo.out', stagger: .03, delay: .05 });
  G.from(['.hero-eye', '.hero-sub', '.hero-cta', '.nav'], { y: 16, opacity: 0, duration: .9, ease: 'power3.out', stagger: .08, delay: .3, clearProps: 'transform,opacity' });
  G.from('.hero-stage', { opacity: 0, duration: 1.4, ease: 'power2.out', delay: .25 });
}
const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
Promise.race([fontsReady, new Promise((r) => setTimeout(r, 2500))]).then(() => {
  intro();
  if (hasG) ScrollTrigger.refresh();
});
setTimeout(() => IND.forEach((d) => { const im = new Image(); im.src = d.img; }), 2500);
