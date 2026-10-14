/* ---------- statement ---------- */
function splitWords(el) {
  const out = [];
  [...el.childNodes].forEach((node) => {
    if (node.nodeType === 3) {
      const frag = document.createDocumentFragment();
      node.textContent.split(/(\s+)/).forEach((part) => {
        if (!part) return;
        if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
        const s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s); out.push(s);
      });
      node.replaceWith(frag);
    } else if (node.nodeType === 1) { node.classList.add('w'); out.push(node); }
  });
  return out;
}
const say = $('#sayBig');
const sayWords = splitWords(say);
if (hasG && !RM) {
  const css = getComputedStyle(document.documentElement);
  const ink = css.getPropertyValue('--ink').trim(), blue = css.getPropertyValue('--blue').trim();
  G.to(sayWords, {
    color: (i, el) => el.classList.contains('b') ? blue : ink, stagger: .06, ease: 'none',
    scrollTrigger: { trigger: say, start: 'top 82%', end: 'bottom 52%', scrub: true }
  });
} else {
  sayWords.forEach((w) => { w.style.color = w.classList.contains('b') ? 'var(--blue)' : 'var(--ink)'; });
}
const forWord = $('#forWord');
let wi = 0, forVisible = false;
if ('IntersectionObserver' in window) new IntersectionObserver((e) => { forVisible = e[0].isIntersecting; }).observe(forWord);
if (!RM) setInterval(() => {
  if (!forVisible || document.hidden) return;
  wi = (wi + 1) % WORDS.length;
  const swap = () => { forWord.textContent = decode(WORDS[wi][0]); forWord.className = 'for-in ' + WORDS[wi][1]; };
  if (!hasG) { swap(); return; }
  G.to(forWord, { yPercent: -110, duration: .32, ease: 'power2.in', onComplete: () => {
    swap(); G.fromTo(forWord, { yPercent: 110 }, { yPercent: 0, duration: .55, ease: 'power3.out' });
  } });
}, 1600);
