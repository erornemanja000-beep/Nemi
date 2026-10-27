// Krume · Konzept: der Bildlauf im Hero ist die Nacht in der Backstube (04:00 → 07:00).
(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const feinerZeiger = matchMedia('(hover: hover) and (pointer: fine)').matches;

  const hero = document.querySelector('.hero');
  const ofenBox = document.querySelector('.hero__ofen');
  const ofen = document.querySelector('.ofen');
  const steps = [...document.querySelectorAll('.hero__steps li')];
  const clocks = [...document.querySelectorAll('[data-clock]')];

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
    // am Ende wächst die Ofenöffnung über den ganzen Bildschirm
    const cover = 2.4 * Math.max(innerWidth / ofenBox.offsetWidth, innerHeight / ofenBox.offsetHeight);
    const z = smooth(.68, .97, p);
    hero.style.setProperty('--door', smooth(.16, .55, p).toFixed(4));
    hero.style.setProperty('--warm', smooth(.08, .7, p).toFixed(4));
    hero.style.setProperty('--zoom', (1 + z * z * (cover - 1)).toFixed(4));
    hero.style.setProperty('--hell', smooth(.9, 1, p).toFixed(4));
    hero.style.setProperty('--aus', smooth(.72, .82, p).toFixed(4));
    const t = uhr(p);
    clocks.forEach(c => { if (c.textContent !== t) c.textContent = t; });
    let jetzt = -1;
    steps.forEach((li, i) => { const on = p >= +li.dataset.from; li.classList.toggle('on', on); if (on) jetzt = i; });
    steps.forEach((li, i) => li.classList.toggle('jetzt', i === jetzt));
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

  /* ---------- Neigen mit dem Zeiger: Ofen und Sackerl drehen sich leicht zur Maus ---------- */
  // x und y sind die Zeigerposition relativ zur Mitte des Elements, je von -1 bis 1
  // gibt {rx, ry} in Grad zurück: rx dreht um die waagrechte Achse (oben/unten), ry um die senkrechte (links/rechts)
  function neigung(x, y, max) {
    // TODO(human): Zeigerposition in eine Drehung übersetzen. Solange hier 0 steht, bleiben Ofen und Sackerl still.
    return {rx: 0, ry: 0};
  }
  const folgen = (flaeche, ziel, max, setzen) => {
    if (reduce || !feinerZeiger) return;
    flaeche.addEventListener('pointermove', e => {
      const r = ziel.getBoundingClientRect();
      const x = clamp((e.clientX - (r.left + r.width / 2)) / (innerWidth / 2), -1, 1);
      const y = clamp((e.clientY - (r.top + r.height / 2)) / (innerHeight / 2), -1, 1);
      setzen(neigung(x, y, max), x, y);
    });
    flaeche.addEventListener('pointerleave', () => setzen({rx: 0, ry: 0}, 0, 0));
  };
  folgen(hero, ofenBox, 14, ({rx, ry}, x, y) => {
    ofen.style.setProperty('--tx', ry.toFixed(2) + 'deg');
    ofen.style.setProperty('--ty', rx.toFixed(2) + 'deg');
    // das Brot im Ofen liegt tiefer und wandert gegen die Drehung, so wirkt der Ofen hohl
    ofen.style.setProperty('--px', (-x * 14).toFixed(1) + 'px');
    ofen.style.setProperty('--py', (-y * 10).toFixed(1) + 'px');
  });

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
      const r = ofenBox.getBoundingClientRect(), ox = r.left + r.width / 2, oy = r.top + r.height / 2;
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

  /* ---------- Einblenden beim Scrollen: Überschrift, dann Text, dann der Rest ---------- */
  const teile = document.querySelectorAll('[data-auf]');
  if (reduce || !('IntersectionObserver' in window)) teile.forEach(t => t.classList.add('da'));
  else {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('da'); io.unobserve(e.target); } }), {threshold: .15});
    document.querySelectorAll('section').forEach(s => s.querySelectorAll('[data-auf]').forEach((t, i) => { t.style.transitionDelay = Math.min(i, 5) * 80 + 'ms'; io.observe(t); }));
  }

  /* ---------- Brot des Tages: die Vitrine zeigt die Zeile unter dem Zeiger ---------- */
  const zeilen = [...document.querySelectorAll('.laib__zeile')];
  const vitrine = [...document.querySelectorAll('.brot__vitrine img')];
  const zeige = i => {
    zeilen.forEach((z, j) => z.setAttribute('aria-pressed', String(i === j)));
    vitrine.forEach((b, j) => b.classList.toggle('an', i === j));
  };
  zeilen.forEach((z, i) => {
    z.addEventListener('pointerenter', () => zeige(i));
    z.addEventListener('focus', () => zeige(i));
    z.addEventListener('click', () => zeige(i));
  });

  /* ---------- Vorbestellen: das Sackerl zeigt, was im Formular steht (Konzept: nichts wird verschickt) ---------- */
  const form = document.getElementById('vorForm');
  const sack = document.querySelector('.sack');
  const koerper = sack.querySelector('.sack__koerper');
  const feld = n => form.elements.namedItem(n);
  const stempel = n => sack.querySelector(`[data-sack="${n}"]`);
  // der gezackte Rand, wie mit der Schere geschnitten
  const zacken = Array.from({length: 15}, (_, i) => `${((i / 14) * 100).toFixed(2)}% ${i % 2 ? 0 : 1.2}em`).join(', ');
  koerper.style.setProperty('--zacken', `polygon(0 100%, ${zacken}, 100% 100%)`);

  const menge = () => clamp(parseInt(feld('menge').value, 10) || 1, 1, 40);
  const fuelle = () => {
    stempel('name').textContent = feld('name').value.trim() || 'Für dich';
    stempel('inhalt').textContent = `${menge()} × ${feld('brot').value}`;
    sack.classList.remove('zu');
  };
  form.addEventListener('input', fuelle);
  form.addEventListener('submit', e => {
    e.preventDefault();
    const danke = form.querySelector('.vor__danke');
    const name = feld('name').value.trim();
    if (!name) { danke.textContent = 'Bitte gib deinen Namen an, damit wir das Sackerl beschriften können.'; feld('name').focus(); return; }
    fuelle();
    sack.classList.add('zu');
    danke.textContent = `Danke, ${name}! ${menge()} × ${feld('brot').value} liegen morgen ab 6:30 für dich bereit. (Konzept: hier käme die Bestellung bei der Bäckerei an.)`;
  });
  folgen(document.getElementById('vorbestellen'), koerper, 18, ({rx, ry}) => {
    koerper.style.setProperty('--sx', (-8 + rx).toFixed(2) + 'deg');
    koerper.style.setProperty('--sy', (-28 + ry).toFixed(2) + 'deg');
  });
})();
