/* Freiraum – gemeinsame Laufzeit: Sprache, Wiener Zeit, „Jetzt“, Farben nach Tageszeit,
   Ton (WebAudio, erst nach Klick), Navigation/Footer, Reveal, Demo-Panel, Weihnachts-Look, Formulare. */
(function () {
  'use strict';
  const FR = (window.FR = window.FR || {});
  const qs = new URLSearchParams(location.search);
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  FR.store = store;
  FR.reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  FR.touch = matchMedia('(hover: none), (pointer: coarse)').matches;

  /* ---------------- Sprache ---------------- */
  const DICT = { de: {}, en: {} };
  FR.lang = (qs.get('lang') || store.get('fr-lang', '') || 'de') === 'en' ? 'en' : 'de';   // Deutsch ist Standard
  FR.i18n = {
    add(d) { for (const l of ['de', 'en']) Object.assign(DICT[l], d[l] || {}); },
    t(key) { return DICT[FR.lang][key] ?? DICT.de[key] ?? key; },
  };
  FR.t = FR.i18n.t;
  FR.applyLang = function (root) {
    root = root || document;
    document.documentElement.lang = FR.lang;
    root.querySelectorAll('[data-i18n]').forEach((el) => { const v = FR.t(el.dataset.i18n); if (v !== el.dataset.i18n) el.textContent = v; });
    root.querySelectorAll('[data-i18n-html]').forEach((el) => { const v = FR.t(el.dataset.i18nHtml); if (v !== el.dataset.i18nHtml) el.innerHTML = v; });
    root.querySelectorAll('[data-i18n-ph]').forEach((el) => { el.placeholder = FR.t(el.dataset.i18nPh); });
    root.querySelectorAll('[data-i18n-aria]').forEach((el) => { el.setAttribute('aria-label', FR.t(el.dataset.i18nAria)); });
    document.querySelectorAll('.lang').forEach((b) => b.querySelectorAll('span').forEach((s) => s.classList.toggle('on', s.dataset.l === FR.lang)));
    document.dispatchEvent(new CustomEvent('fr:lang', { detail: FR.lang }));
  };
  FR.setLang = function (l) { FR.lang = l; store.set('fr-lang', l); FR.applyLang(); FR.updateJetzt && FR.updateJetzt(); };

  FR.i18n.add({
    de: {
      'nav.menu': 'Speisekarte', 'nav.spiel': 'Spielraum', 'nav.feiern': 'Feiern', 'nav.besuch': 'Besuch', 'nav.reserve': 'Reservieren',
      'nav.sound': 'Ton an/aus', 'nav.open': 'Menü öffnen', 'nav.close': 'Menü schließen', 'nav.home': 'Start',
      'foot.visit': 'Besuch', 'foot.hours': 'Öffnungszeiten', 'foot.contact': 'Kontakt', 'foot.more': 'Mehr',
      'foot.addr': 'Mariahilfer Straße 117<br>1060 Wien', 'foot.h1': 'Mo 8–23 · Di–Do 8–24', 'foot.h2': 'Fr–Sa 8–2 · So 9–23',
      'foot.h3': 'Küche bis 21:45', 'foot.imprint': 'Impressum', 'foot.privacy': 'Datenschutz', 'foot.team': 'Team-Login',
      'foot.tag': 'World Kitchen & Social Space · seit 2008',
      'draft': 'Entwurf · nemistudio',
      'j.closed': 'Geschlossen · ab {t} geöffnet', 'j.breakfast': 'Jetzt: Frühstück bis 17:00', 'j.kitchen': 'Jetzt: Küche bis 21:45',
      'j.bar': 'Jetzt: Bar bis {t}', 'j.ladies': 'Heute: Ladies Night', 'j.pizzasun': 'Heute: Pizza Sunday · 9,90 €',
      'j.spiel': 'Spielraum offen bis 18:00', 'j.open': 'Geöffnet',
      'form.sent': 'Danke! Deine Anfrage ist bei uns angekommen. Wir melden uns so schnell wie möglich.',
      'form.err': 'Ups, das hat nicht geklappt. Bitte ruf uns an: +43 1 596 96 00',
      'demo.time': 'Tageszeit', 'demo.season': 'Saison', 'demo.lang': 'Sprache', 'demo.xmas': 'Weihnachten', 'demo.now': 'Jetzt',
    },
    en: {
      'nav.menu': 'Menu', 'nav.spiel': 'Spielraum', 'nav.feiern': 'Events', 'nav.besuch': 'Visit', 'nav.reserve': 'Book a table',
      'nav.sound': 'Sound on/off', 'nav.open': 'Open menu', 'nav.close': 'Close menu', 'nav.home': 'Home',
      'foot.visit': 'Visit', 'foot.hours': 'Opening hours', 'foot.contact': 'Contact', 'foot.more': 'More',
      'foot.addr': 'Mariahilfer Straße 117<br>1060 Vienna', 'foot.h1': 'Mon 8–23 · Tue–Thu 8–24', 'foot.h2': 'Fri–Sat 8–2 · Sun 9–23',
      'foot.h3': 'Kitchen until 21:45', 'foot.imprint': 'Imprint', 'foot.privacy': 'Privacy', 'foot.team': 'Team login',
      'foot.tag': 'World Kitchen & Social Space · since 2008',
      'draft': 'Draft · nemistudio',
      'j.closed': 'Closed · opens {t}', 'j.breakfast': 'Now: breakfast until 5 pm', 'j.kitchen': 'Now: kitchen until 9:45 pm',
      'j.bar': 'Now: bar until {t}', 'j.ladies': 'Tonight: Ladies Night', 'j.pizzasun': 'Today: Pizza Sunday · €9.90',
      'j.spiel': 'Spielraum open until 6 pm', 'j.open': 'Open',
      'form.sent': 'Thank you! Your request has reached us. We will get back to you as soon as possible.',
      'form.err': 'Oops, that did not work. Please call us: +43 1 596 96 00',
      'demo.time': 'Time of day', 'demo.season': 'Season', 'demo.lang': 'Language', 'demo.xmas': 'Christmas', 'demo.now': 'Now',
    },
  });

  /* ---------------- Wiener Zeit & Öffnungszeiten ---------------- */
  const fmt = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Vienna', weekday: 'short', hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric', hour12: false });
  const DOW = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 0 };
  FR.vienna = function () {
    const p = Object.fromEntries(fmt.formatToParts(new Date()).map((x) => [x.type, x.value]));
    let h = +p.hour % 24, m = +p.minute, dow = DOW[p.weekday];
    const fake = store.get('fr-demo-hour', '');
    if (fake !== '') { h = +fake; m = 0; }
    const fakeDow = store.get('fr-demo-dow', '');
    if (fakeDow !== '') dow = +fakeDow;
    return { h, m, dow, day: +p.day, month: +p.month, year: +p.year, hf: h + m / 60 };
  };
  // Lokal: [Wochentag 0=So] -> [auf, zu] in Stunden (zu > 24 = nach Mitternacht)
  FR.hours = {
    venue: { 0: [9, 23], 1: [8, 23], 2: [8, 24], 3: [8, 24], 4: [8, 24], 5: [8, 26], 6: [8, 26] },
    kitchen: { 0: [9, 21.75], 1: [8, 21.75], 2: [8, 21.75], 3: [8, 21.75], 4: [8, 21.75], 5: [8, 21.75], 6: [8, 21.75] },
    pizza: { 0: [11, 21.75], 1: [11, 21.75], 2: [11, 21.75], 3: [11, 21.75], 4: [11, 21.75], 5: [11, 22.75], 6: [11, 22.75] },
    spielraum: { 0: [9, 18], 1: [9, 18], 2: [9, 18], 3: [9, 18], 4: [9, 18], 5: [9, 18], 6: [9, 18] },
  };
  const clock = (x) => { x = ((x % 24) + 24) % 24; const h = Math.floor(x), m = Math.round((x - h) * 60); return h + ':' + String(m).padStart(2, '0'); };
  FR.clock = clock;
  FR.isOpen = function (kind, v) {
    v = v || FR.vienna();
    const today = FR.hours[kind][v.dow], y = FR.hours[kind][(v.dow + 6) % 7];
    if (v.hf >= today[0] && v.hf < today[1]) return true;
    return y[1] > 24 && v.hf < y[1] - 24; // nach Mitternacht vom Vortag
  };
  FR.status = function () {
    const v = FR.vienna(), msgs = [];
    if (!FR.isOpen('venue', v)) {
      const next = FR.hours.venue[v.hf < 12 ? v.dow : (v.dow + 1) % 7][0];
      return { open: false, msgs: [FR.t('j.closed').replace('{t}', clock(next))] };
    }
    if (v.hf < 17 && FR.isOpen('kitchen', v)) msgs.push(FR.t('j.breakfast'));
    else if (FR.isOpen('kitchen', v)) msgs.push(FR.t('j.kitchen'));
    else {
      const today = FR.hours.venue[v.dow], y = FR.hours.venue[(v.dow + 6) % 7];
      const close = v.hf < 6 ? y[1] : today[1];
      msgs.push(FR.t('j.bar').replace('{t}', clock(close)));
    }
    if (v.dow === 0 && v.hf >= 11 && v.hf < 22) msgs.push(FR.t('j.pizzasun'));
    if (v.dow === 4 && v.hf >= 12) msgs.push(FR.t('j.ladies'));
    if (FR.isOpen('spielraum', v)) msgs.push(FR.t('j.spiel'));
    return { open: true, msgs };
  };
  let jIdx = 0;
  FR.updateJetzt = function () {
    const s = FR.status();
    document.querySelectorAll('[data-jetzt]').forEach((el) => {
      el.classList.toggle('closed', !s.open);
      const t = el.querySelector('.t') || el;
      t.textContent = s.msgs[jIdx % s.msgs.length];
    });
    jIdx++;
  };

  /* ---------------- Farben nach Tageszeit ---------------- */
  const P = [
    { h: 6, bg: '#efe9f2', bg2: '#d9def2', fg: '#1f2741', accent: '#6287cd' },
    { h: 8, bg: '#f6efe6', bg2: '#f3d9c6', fg: '#1f2741', accent: '#6287cd' },
    { h: 10.5, bg: '#eef0f8', bg2: '#c7d1ec', fg: '#1f2741', accent: '#6287cd' },
    { h: 12, bg: '#f2f8f3', bg2: '#e2f3e9', fg: '#1f2741', accent: '#3f8f6a' },
    { h: 15, bg: '#f1e8de', bg2: '#e7d7c6', fg: '#2a2230', accent: '#b07a4f' },
    { h: 17, bg: '#f7d2ae', bg2: '#f2b27a', fg: '#2b1a14', accent: '#e8743b' },
    { h: 18.5, bg: '#f1c6cf', bg2: '#e9aeda', fg: '#2b1a2a', accent: '#c2457a' },
    { h: 20, bg: '#7d6aa6', bg2: '#5b3a6e', fg: '#fbf7ff', accent: '#f2b27a' },
    { h: 22, bg: '#151229', bg2: '#1b1840', fg: '#ecebff', accent: '#8b5cf6' },
    { h: 26, bg: '#0f0d1f', bg2: '#141233', fg: '#ecebff', accent: '#3b82f6' },
  ];
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, t) => { const x = hex(a), y = hex(b); return '#' + x.map((v, i) => Math.round(v + (y[i] - v) * t).toString(16).padStart(2, '0')).join(''); };
  FR.palette = function (h) {
    if (h < P[0].h) h = P[0].h;
    if (h > P[P.length - 1].h) h = P[P.length - 1].h;
    let i = 0; while (i < P.length - 2 && h > P[i + 1].h) i++;
    const a = P[i], b = P[i + 1], t = Math.min(1, Math.max(0, (h - a.h) / (b.h - a.h)));
    // Textfarbe nach echtem Kontrast zum Hintergrund (kein Grau beim Übergang)
    const bg = mix(a.bg, b.bg, t), lum = hex(bg).map((v) => { v /= 255; return v <= 0.04 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
    const L = 0.2126 * lum[0] + 0.7152 * lum[1] + 0.0722 * lum[2], dark = L < 0.22;
    const fg = dark ? '#f6f4ff' : (hex(a.fg).reduce((s, v) => s + v, 0) > 600 ? b.fg : a.fg);
    return { bg, bg2: mix(a.bg2, b.bg2, t), fg, accent: mix(a.accent, b.accent, t), dark };
  };
  FR.applyPhase = function (h, el) {
    const p = FR.palette(h), s = (el || document.documentElement).style;
    s.setProperty('--bg', p.bg); s.setProperty('--bg2', p.bg2); s.setProperty('--fg', p.fg); s.setProperty('--accent', p.accent);
    s.setProperty('--muted', p.dark ? 'rgba(236,235,255,.66)' : 'rgba(31,39,65,.62)');
    s.setProperty('--line', p.dark ? 'rgba(255,255,255,.14)' : 'rgba(31,39,65,.14)');
    return p;
  };

  /* ---------------- Ton ----------------
     Effekte und Ambiente sind entfernt (Wunsch des Kunden). Reels haben ihren eigenen Ton per Tippen.
     FR.sound bleibt als leeres Objekt, damit Seiten-Code nicht bricht. */
  const S = (FR.sound = { enabled: false, ambName: '' });
  S.base = (document.querySelector('meta[name="fr-assets"]') || {}).content || 'assets/';
  ['unlock', 'load', 'preload', 'play', 'ambient', 'duck', 'setEnabled'].forEach((k) => (S[k] = () => Promise.resolve(null)));

  /* ---------------- Navigation & Footer ---------------- */
  const ICON = {
    sound: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 10v4h4l5 4V6L8 10H4z"/><path class="w1" d="M16 9.5a3.5 3.5 0 0 1 0 5"/><path class="w2" d="M18.5 7a7 7 0 0 1 0 10"/></svg>',
    burger: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  };
  FR.ICON = ICON;
  FR.logo = (cls = '') => `<span class="logo-mask ${cls}" role="img" aria-label="frei raum"></span>`;
  const style = document.createElement('style');
  const LOGO = window.FR_LOGO_URI || S.base + 'svg/logo-freiraum.svg';
  style.textContent = `.logo-mask{display:inline-block;aspect-ratio:2421/641;height:30px;background:currentColor;-webkit-mask:url("${LOGO}") center/contain no-repeat;mask:url("${LOGO}") center/contain no-repeat}
`;
  document.head.appendChild(style);

  FR.mountChrome = function (opts = {}) {
    const home = opts.home || 'index.html';
    const L = (href, key, id) => `<li><a href="${href}" data-i18n="${key}" ${opts.active === id ? 'aria-current="page"' : ''}></a></li>`;
    const nav = document.createElement('header');
    nav.className = 'nav' + (opts.solid ? ' solid' : '');
    nav.innerHTML = `
      <a class="brand" href="${home}" aria-label="frei raum – Start">${FR.logo()}</a>
      <ul class="links">
        ${L('speisekarte.html', 'nav.menu', 'menu')}${L('spielraum.html', 'nav.spiel', 'spiel')}
        ${L(home + '#feiern', 'nav.feiern', 'feiern')}${L(home + '#besuch', 'nav.besuch', 'besuch')}
      </ul>
      <div class="tools">
        <span class="chip jetzt" data-jetzt><span class="dot"></span><span class="t"></span></span>
        <button class="lang" type="button" aria-label="Sprache / Language"><span data-l="de">DE</span> / <span data-l="en">EN</span></button>
        <a class="btn btn-sm" href="${home}#besuch" data-reserve data-i18n="nav.reserve"></a>
        <button class="icon-btn burger" data-i18n-aria="nav.open">${ICON.burger}</button>
      </div>`;
    document.body.prepend(nav);
    const ov = document.createElement('div');
    ov.className = 'menu-overlay'; ov.setAttribute('aria-hidden', 'true');
    ov.innerHTML = `<button class="icon-btn close" data-i18n-aria="nav.close" style="border-color:rgba(255,255,255,.3);color:#fff">${ICON.close}</button>
      <a class="big" href="${home}" data-i18n="nav.home"></a>
      <a class="big" href="speisekarte.html" data-i18n="nav.menu"></a>
      <a class="big" href="spielraum.html" data-i18n="nav.spiel"></a>
      <a class="big" href="${home}#feiern" data-i18n="nav.feiern"></a>
      <a class="big" href="${home}#besuch" data-i18n="nav.besuch"></a>
      <div class="foot"><span class="chip" data-jetzt><span class="dot"></span><span class="t"></span></span>
        <button class="lang" type="button" style="color:#fff"><span data-l="de">DE</span> / <span data-l="en">EN</span></button>
        <a class="btn btn-light btn-sm" href="tel:+4315969600">+43 1 596 96 00</a></div>`;
    document.body.appendChild(ov);
    const open = (o) => { ov.classList.toggle('open', o); ov.setAttribute('aria-hidden', o ? 'false' : 'true'); document.body.style.overflow = o ? 'hidden' : ''; };
    nav.querySelector('.burger').onclick = () => open(true);
    ov.querySelector('.close').onclick = () => open(false);
    ov.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => open(false)));
    document.querySelectorAll('.lang').forEach((b) => (b.onclick = () => FR.setLang(FR.lang === 'de' ? 'en' : 'de')));
    if (opts.footer !== false) {
      const f = document.createElement('footer');
      f.className = 'footer';
      f.innerHTML = `<div class="wrap">
        <div class="big-logo">${FR.logo('').replace('height:30px', '')}</div>
        <div class="cols">
          <div><h4 data-i18n="foot.visit"></h4><p data-i18n-html="foot.addr"></p><p><a href="https://maps.google.com/?q=Freiraum+Mariahilfer+Stra%C3%9Fe+117+Wien" target="_blank" rel="noopener">Google Maps ↗</a></p></div>
          <div><h4 data-i18n="foot.hours"></h4><p data-i18n="foot.h1"></p><p data-i18n="foot.h2"></p><p data-i18n="foot.h3"></p></div>
          <div><h4 data-i18n="foot.contact"></h4><p><a href="tel:+4315969600">+43 1 596 96 00</a></p><p><a href="mailto:info@freiraum117.at">info@freiraum117.at</a></p><p><a href="https://www.instagram.com/freiraumwien/" target="_blank" rel="noopener">@freiraumwien ↗</a></p></div>
          <div><h4 data-i18n="foot.more"></h4><p><a href="speisekarte.html" data-i18n="nav.menu"></a></p><p><a href="spielraum.html" data-i18n="nav.spiel"></a></p></div>
        </div>
        <div class="legal"><span>© 2026 Freiraum · <span data-i18n="foot.tag"></span></span>
          <span><a href="datenschutz.html#impressum" data-i18n="foot.imprint"></a> · <a href="datenschutz.html" data-i18n="foot.privacy"></a></span></div>
      </div>`;
      f.querySelector('.big-logo .logo-mask').style.cssText = 'height:auto;width:100%';
      (opts.footerParent || document.body).appendChild(f);
    }
    const badge = document.createElement('div');
    badge.className = 'draft-badge'; badge.dataset.i18n = 'draft';
    document.body.appendChild(badge);
    // Nav: ab etwas Scroll mit Hintergrund
    if (!opts.solid) {
      const onS = () => nav.classList.toggle('solid', scrollY > (opts.solidAfter ?? 40));
      addEventListener('scroll', onS, { passive: true }); onS();
    }
    FR.applyLang(); FR.updateJetzt(); setInterval(FR.updateJetzt, 5000);
    if (!FR.touch) FR.cursor();
    FR.reveal();
    if (qs.get('demo') === '1' || store.get('fr-demo', '') === '1') FR.demoPanel();
    FR.xmas();
    return nav;
  };

  /* ---------------- Reveal ---------------- */
  FR.splitWords = function (el) {
    if (el.dataset.split) return;
    el.dataset.split = '1';
    const walk = (node) => {
      [...node.childNodes].forEach((n) => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((w) => {
            if (!w) return;
            if (/^\s+$/.test(w)) { frag.appendChild(document.createTextNode(w)); return; }
            const o = document.createElement('span'); o.className = 'w';
            const i = document.createElement('span'); i.textContent = w; o.appendChild(i); frag.appendChild(o);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && !n.classList.contains('w')) walk(n);
      });
    };
    walk(el);
    el.querySelectorAll('.w>span').forEach((s, i) => (s.style.transitionDelay = i * 60 + 'ms'));
  };
  FR.reveal = function (root) {
    root = root || document;
    const els = root.querySelectorAll('.rv:not(.in), .words:not(.in)');
    els.forEach((el) => el.classList.contains('words') && FR.splitWords(el));
    if (!('IntersectionObserver' in window)) { els.forEach((el) => el.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
    els.forEach((el) => io.observe(el));
  };

  /* ---------------- Cursor ---------------- */
  FR.cursor = function () {
    const c = document.createElement('div'); c.className = 'cursor'; document.body.appendChild(c);
    let x = -50, y = -50, cx = x, cy = y;
    addEventListener('pointermove', (e) => { x = e.clientX; y = e.clientY; c.classList.toggle('big', !!e.target.closest('a,button,[data-hover],input,select,textarea,label')); }, { passive: true });
    (function loop() { cx += (x - cx) * 0.25; cy += (y - cy) * 0.25; c.style.transform = `translate(${cx}px,${cy}px)`; requestAnimationFrame(loop); })();
  };

  /* ---------------- Weihnachts-Look ---------------- */
  FR.isXmas = function () {
    const f = store.get('fr-xmas', '');
    if (f !== '') return f === '1';
    const v = FR.vienna();
    return (v.month === 11 && v.day >= 15) || v.month === 12 || (v.month === 1 && v.day <= 6);
  };
  let snowRAF = 0;
  FR.xmas = function () {
    const on = FR.isXmas();
    document.documentElement.classList.toggle('xmas', on);
    document.dispatchEvent(new CustomEvent('fr:xmas', { detail: on }));
    let cv = document.querySelector('canvas.snow');
    if (!on || FR.reduced) { if (cv) cv.remove(); cancelAnimationFrame(snowRAF); return; }
    if (cv) return;
    cv = document.createElement('canvas'); cv.className = 'snow'; document.body.appendChild(cv);
    const g = cv.getContext('2d'); let W, H; const flakes = [];
    const rs = () => { W = cv.width = innerWidth * devicePixelRatio; H = cv.height = innerHeight * devicePixelRatio; };
    rs(); addEventListener('resize', rs);
    for (let i = 0; i < 70; i++) flakes.push({ x: Math.random(), y: Math.random(), r: 0.6 + Math.random() * 1.8, s: 0.2 + Math.random() * 0.5, d: Math.random() * 6 });
    (function loop(t) {
      g.clearRect(0, 0, W, H); g.fillStyle = 'rgba(255,255,255,.85)';
      flakes.forEach((f) => { f.y += f.s / 900; if (f.y > 1.02) f.y = -0.02; const x = (f.x + Math.sin(t / 2400 + f.d) * 0.01) * W; g.beginPath(); g.arc(x, f.y * H, f.r * devicePixelRatio, 0, 7); g.fill(); });
      snowRAF = requestAnimationFrame(loop);
    })(0);
  };

  /* ---------------- Demo-Panel ---------------- */
  FR.demoPanel = function () {
    store.set('fr-demo', '1');
    const d = document.createElement('div'); d.className = 'demo-panel';
    const hours = ['', '8', '12', '15', '17', '22'];
    const cur = store.get('fr-demo-hour', '');
    d.innerHTML = `<b data-i18n="demo.time"></b><div class="row">${hours.map((h) => `<button data-h="${h}" class="${cur === h ? 'on' : ''}">${h ? h + ':00' : FR.t('demo.now')}</button>`).join('')}</div>
      <b data-i18n="demo.season"></b><div class="row"><button data-x="1" class="${store.get('fr-xmas', '') === '1' ? 'on' : ''}" data-i18n="demo.xmas"></button><button data-x="" class="${store.get('fr-xmas', '') === '' ? 'on' : ''}">Auto</button></div>
      <b data-i18n="demo.lang"></b><div class="row"><button data-l2="de">DE</button><button data-l2="en">EN</button><button data-close>×</button></div>`;
    document.body.appendChild(d);
    d.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      if ('h' in b.dataset) { store.set('fr-demo-hour', b.dataset.h); d.querySelectorAll('[data-h]').forEach((x) => x.classList.toggle('on', x === b)); FR.updateJetzt(); document.dispatchEvent(new CustomEvent('fr:demo', { detail: { hour: b.dataset.h } })); }
      if ('x' in b.dataset) { store.set('fr-xmas', b.dataset.x); d.querySelectorAll('[data-x]').forEach((x) => x.classList.toggle('on', x === b)); FR.xmas(); }
      if (b.dataset.l2) FR.setLang(b.dataset.l2);
      if ('close' in b.dataset) { store.set('fr-demo', ''); d.remove(); }
    });
    FR.applyLang(d);
  };

  /* ---------------- Formulare / Buchungen ---------------- */
  FR.submit = async function (type, data) {
    const body = JSON.stringify({ type, ...data, lang: FR.lang, sentAt: new Date().toISOString() });
    let r = null;
    try { r = await fetch('/.netlify/functions/booking', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body }); } catch (e) { r = null; }
    if (r && r.ok) return r.json();
    if (r && ![404, 405, 501].includes(r.status)) return { ok: false };   // Server lehnt ab → Fehlermeldung zeigen
    {
      // Demo ohne Server: lokal speichern, damit /team es trotzdem zeigt
      const list = JSON.parse(store.get('fr-demo-bookings', '[]'));
      const item = { id: 'local-' + Date.now(), status: 'neu', ...JSON.parse(body) };
      list.unshift(item); store.set('fr-demo-bookings', JSON.stringify(list));
      return { ok: true, id: item.id, local: true };
    }
  };
  FR.bindForm = function (form, type, onDone) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const data = Object.fromEntries(new FormData(form).entries());
      const btn = form.querySelector('[type=submit]'); if (btn) btn.disabled = true;
      const res = await FR.submit(type, data);
      if (btn) btn.disabled = false;
      const ok = document.createElement('div'); ok.className = 'form-ok'; ok.textContent = res.ok ? FR.t('form.sent') : FR.t('form.err');
      form.replaceWith(ok);
      onDone && onDone(res, ok);
    });
  };

  FR.json = (url) => fetch(url).then((r) => r.json()).catch((e) => {
    const d = window.FR_DATA && window.FR_DATA[url];
    if (d) return d;
    throw e;
  });
})();
