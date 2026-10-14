/* ---------- showroom ---------- */
const cfgMinis = [$('#cfgDesk .ms'), $('#cfgPhone .ms')];
const st = { i: 0, sty: null, acc: 0, name: '' };
const cur = () => {
  const d = IND[st.i];
  return { ind: d, sty: st.sty || d.style, acc: SW[st.acc], name: st.name.trim() || d.name };
};
const indBox = $('#cfgInd'), styBox = $('#cfgSty'), colBox = $('#cfgCol');
indBox.innerHTML = IND.map((d, i) => '<button class="chip" type="button" data-i="' + i + '" aria-pressed="false">' + d.label + '</button>').join('');
styBox.innerHTML = Object.keys(STY).map((k) => '<button class="chip" type="button" data-s="' + k + '" aria-pressed="false">' + STY[k] + '</button>').join('');
colBox.innerHTML = SW.map((c, i) => c
  ? '<button class="sw" type="button" data-c="' + i + '" style="--c:' + c + '" aria-pressed="false" aria-label="' + c + '"></button>'
  : '<button class="sw sw--auto" type="button" data-c="0" aria-pressed="false" aria-label="{{Farbe des Stils||Style colour}}">A</button>').join('');
const fInd = $('#fInd');
fInd.insertAdjacentHTML('beforeend', IND.map((d) => '<option value="' + d.id + '">' + d.label + '</option>').join('') + '<option value="other">{{Andere Branche||Other industry}}</option>');

let autoOn = !RM, autoTimer = 0, cfgVisible = false;
function syncUI(running) {
  const c = cur();
  $$('.chip', indBox).forEach((b) => { const on = +b.dataset.i === st.i; b.setAttribute('aria-pressed', on); b.classList.remove('run'); if (on && running) { void b.offsetWidth; b.classList.add('run'); } });
  $$('.chip', styBox).forEach((b) => b.setAttribute('aria-pressed', b.dataset.s === c.sty));
  $$('.sw', colBox).forEach((b) => b.setAttribute('aria-pressed', +b.dataset.c === st.acc));
}
function updateCfg(fade) {
  const c = cur();
  if (fade && !RM) {
    cfgMinis.forEach((m) => m.classList.add('fade'));
    setTimeout(() => { cfgMinis.forEach((m) => { renderMini(m, c); m.classList.remove('fade'); }); }, 200);
  } else cfgMinis.forEach((m) => renderMini(m, c));
  syncUI(autoOn);
}
cfgMinis.forEach((m) => { setK(m, 1); m.classList.add('is-live'); });
updateCfg(false);
const stopAuto = () => { if (!autoOn) return; autoOn = false; clearInterval(autoTimer); syncUI(false); };
function startAuto() {
  clearInterval(autoTimer);
  if (!autoOn) return;
  syncUI(true);
  autoTimer = setInterval(() => { if (!cfgVisible || document.hidden) return; st.i = (st.i + 1) % IND.length; updateCfg(true); }, 3600);
}
if ('IntersectionObserver' in window) new IntersectionObserver((e) => {
  cfgVisible = e[0].isIntersecting;
  if (cfgVisible && autoOn) startAuto(); else clearInterval(autoTimer);
}, { threshold: .25 }).observe($('#cfg'));
$('.cfg-ctrl').addEventListener('pointerdown', stopAuto);
$('.cfg-ctrl').addEventListener('keydown', stopAuto);
indBox.addEventListener('click', (e) => { const b = e.target.closest('.chip'); if (!b) return; stopAuto(); emit('tick'); st.i = +b.dataset.i; updateCfg(true); });
styBox.addEventListener('click', (e) => { const b = e.target.closest('.chip'); if (!b) return; stopAuto(); emit('tick'); st.sty = b.dataset.s; updateCfg(true); });
colBox.addEventListener('click', (e) => { const b = e.target.closest('.sw'); if (!b) return; stopAuto(); emit('tick'); st.acc = +b.dataset.c; updateCfg(false); });
$('#cfgName').addEventListener('input', (e) => { stopAuto(); st.name = e.target.value; updateCfg(false); });
$('#cfgShuffle').addEventListener('click', () => {
  stopAuto();
  st.i = Math.floor(Math.random() * IND.length);
  const keys = Object.keys(STY); st.sty = keys[Math.floor(Math.random() * keys.length)];
  st.acc = Math.floor(Math.random() * SW.length);
  updateCfg(true);
});
$('#cfgAsk').addEventListener('click', () => {
  stopAuto();
  const c = cur();
  fInd.value = c.ind.id;
  if (st.name.trim()) $('#fCo').value = st.name.trim();
  $('#fMsg').value = decode('{{Hallo Nemi, mir gefällt das Konzept „||Hi Nemi, I like the “}}' + STY[c.sty] + '{{“ für ||” concept for }}' + c.ind.label + ' (' + c.name + '){{. Können wir darüber sprechen?||. Can we talk about it?}}');
  goTo('#kontakt');
  setTimeout(() => $('#fName').focus({ preventScroll: true }), 1400);
});
