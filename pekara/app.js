// Krume · Konzept: der Bildlauf im Hero ist die Nacht in der Backstube (04:00 → 07:00).
(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const hero = document.querySelector('.hero');
  const oven = document.querySelector('.hero__oven');
  const steps = [...document.querySelectorAll('.hero__steps li')];
  const clocks = [...document.querySelectorAll('[data-clock]')];
  const hint = document.querySelector('.hero__hint');

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
  // die Uhr trifft genau die Zeiten der Schritte im Text (04:00, 05:30, 06:40, 07:00)
  const ZEIT = [[0, 240], [.25, 330], [.45, 400], [.62, 420], [1, 420]];
  const uhr = p => {
    let i = 1; while (i < ZEIT.length - 1 && p > ZEIT[i][0]) i++;
    const [p0, m0] = ZEIT[i - 1], [p1, m1] = ZEIT[i];
    const min = Math.floor((m0 + (m1 - m0) * clamp((p - p0) / (p1 - p0)) + 1e-6) / 5) * 5;
    return String(Math.floor(min / 60)).padStart(2, '0') + ':' + String(min % 60).padStart(2, '0');
  };

  let heroP = 0;
  function frame() {
    const span = hero.offsetHeight - innerHeight;
    const p = span > 0 ? clamp((scrollY - hero.offsetTop) / span) : 1;
    heroP = p;
    const door = smooth(.16, .55, p);
    // am Ende wächst die Ofenöffnung über den ganzen Bildschirm
    const cover = 2.4 * Math.max(innerWidth / oven.offsetWidth, innerHeight / oven.offsetHeight);
    const z = smooth(.68, .97, p);
    hero.style.setProperty('--door', door.toFixed(4));
    hero.style.setProperty('--warm', smooth(.08, .7, p).toFixed(4));
    hero.style.setProperty('--zoom', (1 + z * z * (cover - 1)).toFixed(4));
    hero.style.setProperty('--hell', smooth(.9, 1, p).toFixed(4));
    hero.style.setProperty('--aus', smooth(.72, .82, p).toFixed(4));
    const t = uhr(p);
    clocks.forEach(c => { if (c.textContent !== t) c.textContent = t; });
    let jetzt = -1;
    steps.forEach((li, i) => { const on = p >= +li.dataset.from; li.classList.toggle('on', on); if (on) jetzt = i; });
    steps.forEach((li, i) => li.classList.toggle('jetzt', i === jetzt));
    hint.classList.toggle('weg', p > .03);
  }

  if (!reduce) {
    let wartet = false;
    const plan = () => { if (!wartet) { wartet = true; requestAnimationFrame(() => { wartet = false; frame(); }); } };
    addEventListener('scroll', plan, {passive: true});
    addEventListener('resize', plan);
    frame();
  } else {
    steps.forEach(li => li.classList.add('on'));
  }

  /* ---------- Mehlstaub im Licht des Ofens ---------- */
  const cv = document.querySelector('.hero__mehl');
  if (!reduce && cv.getContext) {
    const ctx = cv.getContext('2d');
    const dpr = Math.min(devicePixelRatio || 1, 2);
    let w = 0, h = 0, laeuft = false, sichtbar = true;
    const staub = Array.from({length: innerWidth < 600 ? 40 : 75}, () => ({x: Math.random(), y: Math.random(), r: .5 + Math.random() * 1.8, v: .00015 + Math.random() * .0005, ph: Math.random() * 6.28}));
    const groesse = () => { w = cv.clientWidth; h = cv.clientHeight; cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); };
    groesse();
    addEventListener('resize', groesse);
    const zeichne = ts => {
      if (!sichtbar || heroP >= .98) { laeuft = false; return; }
      ctx.clearRect(0, 0, w, h);
      const r = oven.getBoundingClientRect(), ox = r.left + r.width / 2, oy = r.top + r.height / 2;
      const licht = .15 + smooth(.16, .55, heroP) * .85;
      for (const s of staub) {
        s.y -= s.v; if (s.y < -.02) { s.y = 1.02; s.x = Math.random(); }
        const x = (s.x + Math.sin(ts / 2400 + s.ph) * .012) * w, y = s.y * h;
        const nah = 1 - clamp(Math.hypot(x - ox, y - oy) / (Math.max(w, h) * .55));
        ctx.globalAlpha = (.08 + nah * .7) * licht;
        ctx.fillStyle = nah > .35 ? '#ffc58a' : '#eadbc4';
        ctx.beginPath(); ctx.arc(x, y, s.r, 0, 6.283); ctx.fill();
      }
      requestAnimationFrame(zeichne);
    };
    const starte = () => { if (!laeuft) { laeuft = true; requestAnimationFrame(zeichne); } };
    new IntersectionObserver(([e]) => { sichtbar = e.isIntersecting; if (sichtbar) starte(); }).observe(hero);
    addEventListener('scroll', () => { if (heroP < .98) starte(); }, {passive: true});
    starte();
  }

  /* ---------- Einblenden beim Scrollen ---------- */
  const karten = document.querySelectorAll('.schritt, .laib');
  if (reduce || !('IntersectionObserver' in window)) karten.forEach(k => k.classList.add('da'));
  else {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('da'); io.unobserve(e.target); } }), {threshold: .15});
    karten.forEach((k, i) => { k.style.transitionDelay = (i % 4) * 90 + 'ms'; io.observe(k); });
  }

  /* ---------- Vorbestellen (Konzept: nichts wird verschickt) ---------- */
  const form = document.getElementById('vorForm');
  form.addEventListener('submit', e => {
    e.preventDefault();
    const f = form.elements, danke = form.querySelector('.vor__danke');
    const name = f.namedItem('name').value.trim();
    if (!name) { danke.textContent = 'Bitte gib deinen Namen an, damit wir das Sackerl beschriften können.'; f.namedItem('name').focus(); return; }
    const menge = clamp(parseInt(f.namedItem('menge').value, 10) || 1, 1, 40);
    danke.textContent = `Danke, ${name}! ${menge} × ${f.namedItem('brot').value} liegen morgen ab 6:30 für dich bereit. (Konzept: hier käme die Bestellung bei der Bäckerei an.)`;
  });
})();
