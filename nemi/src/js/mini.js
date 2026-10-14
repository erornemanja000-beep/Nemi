/* ---------- the preview template ---------- */
const miniHTML = (phone) => '<div class="ms' + (phone ? ' ms--phone' : '') + '" data-style="warm">' +
  '<div class="ms-media"><img alt="" decoding="async"></div>' +
  '<header class="ms-nav"><span class="ms-logo"><i class="ms-mark"></i><span class="t ms-name"></span></span>' +
  (phone ? '<span class="ms-burger"><i></i><i></i></span>' : '<nav class="ms-menu"><span class="t"></span><span class="t"></span><span class="t"></span></nav><span class="ms-cta"><span class="t"></span></span>') +
  '</header><div class="ms-copy"><p class="ms-eye"><span class="t"></span></p><h3 class="ms-title"><span class="t"></span></h3>' +
  '<p class="ms-sub"><span class="t"></span></p><div class="ms-btns"><span class="ms-btn"><span class="t"></span></span><span class="ms-more"><span class="t"></span></span></div></div>' +
  '<ul class="ms-feats"><li><b>01</b><span class="t"></span></li><li><b>02</b><span class="t"></span></li><li><b>03</b><span class="t"></span></li></ul></div>';

const minis = $$('[data-mini]').map((scr) => {
  scr.insertAdjacentHTML('afterbegin', miniHTML(scr.dataset.mini === 'phone'));
  const ms = scr.querySelector('.ms');
  const w = scr.dataset.mini === 'phone' ? 390 : 1280;
  const fit = () => scr.style.setProperty('--s', (scr.clientWidth / w).toFixed(4));
  fit();
  if (window.ResizeObserver) new ResizeObserver(fit).observe(scr);
  return ms;
});

function renderMini(ms, s) {
  const d = s.ind;
  ms.dataset.style = s.sty;
  if (s.acc) { ms.style.setProperty('--p-acc', s.acc); ms.style.setProperty('--p-on', onColor(s.acc)); }
  else { ms.style.removeProperty('--p-acc'); ms.style.removeProperty('--p-on'); }
  const set = (sel, txt) => { const el = ms.querySelector(sel); if (el) el.textContent = decode(txt); };
  set('.ms-name', s.name);
  ms.querySelectorAll('.ms-menu .t').forEach((el, i) => { el.textContent = decode(d.nav[i]); });
  set('.ms-cta .t', d.cta);
  set('.ms-eye .t', d.eye);
  set('.ms-title .t', d.h);
  set('.ms-sub .t', d.p);
  set('.ms-btn .t', d.b);
  set('.ms-more .t', MORE);
  ms.querySelectorAll('.ms-feats .t').forEach((el, i) => { el.textContent = decode(d.f[i]); });
  const img = ms.querySelector('img');
  if (img.getAttribute('src') !== d.img) img.src = d.img;
  const dev = ms.closest('.dev');
  const url = dev && dev.querySelector('.url-text');
  if (url) url.textContent = slug(s.name) + TLD;
  const tag = dev && dev.querySelector('.dev-tag');
  if (tag) tag.textContent = decode(d.label);
}
const setK = (ms, k) => ['--k-txt', '--k-img', '--k-col'].forEach((p) => ms.style.setProperty(p, k));
const stateOf = (i, extra) => Object.assign({ ind: IND[i], sty: IND[i].style, acc: null, name: IND[i].name }, extra || {});
