/* Freiraum Premium – Bühne: Mond, Rauch, Partikel, Bildfolgen und Kapitel, alles am Scrollen. */
(function () {
  'use strict';
  const FR = window.FR;
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = (t) => 1 - Math.pow(1 - t, 3);
  const smooth = (t) => t * t * (3 - 2 * t);
  const DPR = Math.min(devicePixelRatio || 1, 2);
  let W = innerWidth, H = innerHeight, MOBILE = W <= 860;
  const SET = () => (MOBILE ? 'm' : 'd');

  /* ---------------- Texte ---------------- */
  FR.i18n.add({
    de: {
      'nav.start': 'Start', 'nav.pizza': 'Pizza', 'nav.kueche': 'Küche', 'nav.kaffee': 'Kaffee', 'nav.drinks': 'Drinks', 'nav.bar': 'Bar',
      'nav.jahre': '18 Jahre', 'scroll': 'Scrollen', 'cta.reserve': 'Tisch reservieren', 'cta.menu': 'Speisekarte', 'cta.allmenu': 'Ganze Speisekarte', 'cta.drinks': 'Alle Drinks',
      'h.eyebrow': 'World Kitchen &amp; Social Space · <b>seit 2008</b>', 'h.title': 'Die ganze Welt. <em>mitten</em> in Wien.',
      'h.lead': 'Pizza aus dem Holzofen, Frühstück bis 17 Uhr, Cocktails bis spät – auf der Mariahilfer Straße 117.',
      'p.eyebrow': '02 — Pizzastation · <b>Holzofen</b>', 'p.title': 'Vom Teig <em>zum</em> Feuer.',
      'p.s1h': 'Teig', 'p.s1': 'Naturhefe-Sauerteig aus Caputo-Manitoba-Mehl, jeden Tag von Hand geformt.',
      'p.s2h': 'Belag', 'p.s2': 'Was draufkommt, kommt frisch: Trüffel, Prosciutto, Fior di Latte.',
      'p.s3h': 'Ofen', 'p.s3': 'Rein in den Holzofen – direkt vor deinen Augen, hinter der Glasscheibe.',
      'p.s4h': 'Feuer', 'p.s4': 'Mindestens 48 Stunden Reifezeit, dann ein paar Minuten echtes Feuer. Mehr braucht es nicht.',
      'p.s5h': 'Genuss', 'p.s5': 'Burrata und Basilikum zum Schluss – und ab an deinen Tisch.',
      'p.sunday': 'Pizza Sunday · jeden Sonntag 14–22 Uhr · ausgewählte Pizzen 9,90 €',
      'p.m': 'Teig,Belag,Ofen,Feuer,Genuss',
      'm.s1': 'Mitten auf der Mahü', 'm.s2': 'Gäste bei Feiern', 'm.s3': 'Tage die Woche geöffnet', 'm.s4': 'Gerichte & Drinks auf der Karte',
      'k.eyebrow': '03 — Küche bis <b>21:45</b>', 'k.title': 'One World <em>Kitchen.</em>',
      'k.lead': 'Wir bringen die ganze Welt nach Wien – von Wiener Schnitzel bis Falafel-Bowl, von Sous-vide-Ente bis Tacos zum Teilen.',
      'k.d1': 'mit Grillgemüse und Salsa-Dip', 'k.d2': 'San-Marzano-Tomaten, knusprige Garnelen', 'k.d3': 'Kirschsauce, knusprige Polenta',
      'k.d4': 'Stracciatella di bufala, Rucola, Rinderschinken', 'k.n5': 'Tapas zum Teilen', 'k.d5': 'Tacos, Patatas Bravas, Garnelen-Tempura', 'k.p5': 'ab 4,9',
      'k.d6': 'Blattsalate, Schafskäse, Walnüsse',
      'c.eyebrow1': '04 — Röstraum · <b>ab 8 Uhr</b>', 'c.title1': 'Dein Moment. <em>jeden</em> Morgen.',
      'c.lead1': 'Kaffee aus unserem eigenen Röstraum – Espresso, Cappuccino, Caffè Latte. Und Zeit, ihn zu genießen.',
      'c.eyebrow2': 'Frühstück · <b>täglich bis 17 Uhr</b>', 'c.title2': 'Frühstück, <em>so lange</em> du willst.',
      'c.lead2': 'Signature Boxes, Pancakes, Bowls und Eier, wie du sie magst.',
      'c.b1': 'Schinken, Emmentaler, weiches Ei, Kornspitz', 'c.b2': 'Mini Rösti, Spiegelei, Speck, Avocado', 'c.b3': 'Falafel, Hummus, Ajvar, Oliven',
      'c.eyebrow3': 'Desserts · <b>hausgemacht</b>', 'c.title3': 'Das süße <em>Ende.</em>',
      'c.lead3': 'Choco Lava mit flüssigem Kern, Cheesecake, Tiramisu mit Röstraum-Espresso.',
      'c.d1': 'flüssiger Schokokern, Himbeereis', 'c.d2': 'Beeren, Karamell oder Pistazie', 'c.d3': 'Mascarpone, Röstraum Espresso',
      'd.eyebrow1': '05 — Golden Hour · <b>ab 17 Uhr</b>', 'd.title1': 'Zeit für <em>Drinks.</em>', 'd.lead1': 'Sprizz, Negroni, Passion Touch – und kleine Teller zum Teilen.',
      'd.p1': 'Rose Secco, Pfirsich, Gurke, Rosmarin', 'd.p2': 'Gin, Aperol, Maracuja, Ananas', 'd.p3': 'Gin, Erdbeer-Bitter, Feige',
      'd.eyebrow2': 'Jeden <b>Donnerstag</b>', 'd.title2': 'Ladies <em>Night.</em>', 'd.lead2': 'Lounge Music, gute Gesellschaft – und das erste Glas Prosecco geht auf uns.',
      'b.eyebrow': '06 — Freitag &amp; Samstag <b>bis 2 Uhr</b>', 'b.title': 'Bar &amp; <em>Beats.</em>',
      'b.lead': 'Wenn\'s draußen dunkel wird, wird\'s bei uns laut: DJ-Abende, Halloween – und am 20.11. feiern wir 18 Jahre Freiraum. Ein paar unserer Lieblinge von Instagram, tippen für Ton.',
      'b.follow': '8.952 Follower', 'b.press': 'Bekannt aus <b style="font-size:20px">heute.at</b>', 'b.ig': 'Folge uns auf Instagram ↗',
      'r.tap': 'Tippen für Ton', 'r.on': 'Ton an',
      's.eyebrow': '07 — Spielraum im Freiraum · <b>täglich 9–18 Uhr</b>', 's.title': 'Ihr genießt. <em>die Kinder</em> toben.',
      's.lead': 'Rutsche, Bällebad und Trampolin – direkt hinter der Glaswand. Ihr esst in Ruhe, die Kleinen sind in Sichtweite. RIO passt auf.',
      's.cta': 'Spielraum entdecken', 's.party': 'Kindergeburtstag',
      'e.eyebrow': '08 — Feiern &amp; Events', 'e.guests': 'Gäste<br>bis zu', 'e.title': 'Euer Fest. <em>unser</em> Freiraum.',
      'e.lead': 'Ganzes Lokal oder eigener Bereich, Set-Menü, Buffet oder à la carte, mit DJ oder Lounge Music. Wir kümmern uns um alles.',
      'e.t1': 'Hochzeit', 'e.t2': 'Firmenfeier', 'e.t3': 'Geburtstag', 'e.t4': 'Weihnachtsfeier', 'e.t5': 'Kindergeburtstag →', 'e.lbl': 'Der Saal · Mariahilfer Straße 117',
      'f.title': 'Eure Feier <em>anfragen.</em>', 'f.lead': 'Unverbindlich – wir melden uns innerhalb von 24 Stunden.',
      'f.anlass': 'Anlass', 'f.other': 'Etwas anderes', 'f.datum': 'Wunschdatum', 'f.gaeste': 'Gäste', 'f.bereich': 'Bereich', 'f.b1': 'Eigener Bereich', 'f.b2': 'Ganzes Lokal', 'f.b3': 'Weiß ich noch nicht',
      'f.essen': 'Essen', 'f.e1': 'Set-Menü', 'f.e2': 'Buffet', 'f.e3': 'À la carte', 'f.e4': 'Fingerfood & Tapas', 'f.musik': 'Musik', 'f.m3': 'Keine',
      'f.name': 'Name', 'f.tel': 'Telefon', 'f.mail': 'E-Mail', 'f.msg': 'Nachricht', 'f.msgph': 'Erzählt uns kurz von eurer Feier …',
      'f.ds': 'Ich bin einverstanden, dass meine Angaben zur Bearbeitung der Anfrage gespeichert werden (<a href="datenschutz.html">Datenschutz</a>).', 'f.send': 'Anfrage senden',
      'j.eyebrow': '09 — 20.11.2026', 'j.title': 'Jahre <em>Freiraum.</em>', 'j.lead': 'Am 20. November werden wir volljährig. Feiert mit uns – wir zählen schon.',
      'j.past': 'Danke für 18 Jahre Freiraum – auf die nächsten!', 'j.d': 'Tage', 'j.h': 'Stunden', 'j.m': 'Minuten', 'j.s': 'Sekunden',
      'v.eyebrow': '10 — Besuch · <b>U3 Zieglergasse</b>', 'v.title': 'Komm <em>vorbei.</em>', 'v.route': 'Route ↗',
      'v.addr': '<b>Mariahilfer Straße 117</b>, 1060 Wien · U3 Zieglergasse / U6 Westbahnhof',
      'v.venue': 'Lokal', 'v.kitchen': 'Küche', 'v.pizza': 'Pizza', 'v.spiel': 'Spielraum', 'v.open': 'offen', 'v.closed': 'zu',
      'v.h.venue': 'Mo 8–23 · Di–Do 8–24 · Fr–Sa 8–2 · So 9–23', 'v.h.kitchen': 'täglich bis 21:45', 'v.h.pizza': 'ab 11 Uhr', 'v.h.spiel': 'täglich 9–18',
      'ft.visit': 'Besuch', 'ft.hours': 'Öffnungszeiten', 'ft.contact': 'Kontakt', 'ft.more': 'Mehr', 'ft.h': 'Mo 8–23 · Di–Do 8–24<br>Fr–Sa 8–2 · So 9–23<br>Küche bis 21:45',
      'ft.legal': 'Impressum & Datenschutz', 'ft.draft': 'Entwurf · nemistudio',
      'zen.alt': 'Reservierung über Zenchef. Lieber telefonisch? <a href="tel:+4315969600">+43 1 596 96 00</a>',
    },
    en: {
      'nav.start': 'Start', 'nav.pizza': 'Pizza', 'nav.kueche': 'Kitchen', 'nav.kaffee': 'Coffee', 'nav.drinks': 'Drinks', 'nav.bar': 'Bar',
      'nav.jahre': '18 years', 'scroll': 'Scroll', 'cta.reserve': 'Book a table', 'cta.menu': 'Menu', 'cta.allmenu': 'Full menu', 'cta.drinks': 'All drinks',
      'h.eyebrow': 'World Kitchen &amp; Social Space · <b>since 2008</b>', 'h.title': 'The whole world. <em>right</em> in Vienna.',
      'h.lead': 'Wood-fired pizza, breakfast until 5 pm, cocktails until late – on Mariahilfer Straße 117.',
      'p.eyebrow': '02 — Pizza station · <b>wood-fired oven</b>', 'p.title': 'From dough <em>to</em> fire.',
      'p.s1h': 'Dough', 'p.s1': 'Natural sourdough with Caputo Manitoba flour, shaped by hand every day.',
      'p.s2h': 'Toppings', 'p.s2': 'What goes on top goes on fresh: truffle, prosciutto, fior di latte.',
      'p.s3h': 'Oven', 'p.s3': 'Into the wood-fired oven – right in front of you, behind the glass.',
      'p.s4h': 'Fire', 'p.s4': 'At least 48 hours of proofing, then a few minutes of real fire. That is all it takes.',
      'p.s5h': 'Enjoy', 'p.s5': 'Burrata and basil to finish – and straight to your table.',
      'p.sunday': 'Pizza Sunday · every Sunday 2–10 pm · selected pizzas €9.90',
      'p.m': 'Dough,Toppings,Oven,Fire,Enjoy',
      'm.s1': 'Right on the Mahü', 'm.s2': 'guests at parties', 'm.s3': 'days a week', 'm.s4': 'dishes & drinks on the menu',
      'k.eyebrow': '03 — Kitchen until <b>9:45 pm</b>', 'k.title': 'One World <em>Kitchen.</em>',
      'k.lead': 'We bring the whole world to Vienna – from Wiener Schnitzel to falafel bowls, from sous-vide duck to tacos for sharing.',
      'k.d1': 'with grilled vegetables and salsa dip', 'k.d2': 'San Marzano tomatoes, crispy prawns', 'k.d3': 'cherry sauce, crispy polenta',
      'k.d4': 'stracciatella di bufala, rocket, bresaola', 'k.n5': 'Tapas for sharing', 'k.d5': 'tacos, patatas bravas, prawn tempura', 'k.p5': 'from 4.9',
      'k.d6': 'leaf salad, feta, walnuts',
      'c.eyebrow1': '04 — Röstraum · <b>from 8 am</b>', 'c.title1': 'Your moment. <em>every</em> morning.',
      'c.lead1': 'Coffee from our own Röstraum – espresso, cappuccino, caffè latte. And time to enjoy it.',
      'c.eyebrow2': 'Breakfast · <b>daily until 5 pm</b>', 'c.title2': 'Breakfast, <em>as long</em> as you like.',
      'c.lead2': 'Signature boxes, pancakes, bowls and eggs the way you like them.',
      'c.b1': 'ham, Emmental, soft egg, Kornspitz', 'c.b2': 'mini rösti, fried egg, bacon, avocado', 'c.b3': 'falafel, hummus, ajvar, olives',
      'c.eyebrow3': 'Desserts · <b>homemade</b>', 'c.title3': 'The sweet <em>ending.</em>',
      'c.lead3': 'Choco lava with a molten centre, cheesecake, tiramisu with Röstraum espresso.',
      'c.d1': 'molten chocolate, raspberry ice cream', 'c.d2': 'berries, caramel or pistachio', 'c.d3': 'mascarpone, Röstraum espresso',
      'd.eyebrow1': '05 — Golden hour · <b>from 5 pm</b>', 'd.title1': 'Time for <em>drinks.</em>', 'd.lead1': 'Sprizz, Negroni, Passion Touch – and small plates to share.',
      'd.p1': 'rosé secco, peach, cucumber, rosemary', 'd.p2': 'gin, Aperol, passion fruit, pineapple', 'd.p3': 'gin, strawberry bitter, fig',
      'd.eyebrow2': 'Every <b>Thursday</b>', 'd.title2': 'Ladies <em>Night.</em>', 'd.lead2': 'Lounge music, good company – and the first glass of prosecco is on us.',
      'b.eyebrow': '06 — Friday &amp; Saturday <b>until 2 am</b>', 'b.title': 'Bar &amp; <em>Beats.</em>',
      'b.lead': 'When it gets dark outside, it gets loud in here: DJ nights, Halloween – and on 20 Nov we celebrate 18 years of Freiraum. A few favourites from Instagram, tap for sound.',
      'b.follow': '8,952 followers', 'b.press': 'Featured on <b style="font-size:20px">heute.at</b>', 'b.ig': 'Follow us on Instagram ↗',
      'r.tap': 'Tap for sound', 'r.on': 'Sound on',
      's.eyebrow': '07 — Spielraum at Freiraum · <b>daily 9 am–6 pm</b>', 's.title': 'You relax. <em>the kids</em> play.',
      's.lead': 'Slide, ball pit and trampoline – right behind the glass wall. You eat in peace, the little ones stay in sight. RIO keeps watch.',
      's.cta': 'Discover the Spielraum', 's.party': 'Kids\' birthday',
      'e.eyebrow': '08 — Parties &amp; events', 'e.guests': 'guests<br>up to', 'e.title': 'Your party. <em>our</em> Freiraum.',
      'e.lead': 'The whole venue or your own area, set menu, buffet or à la carte, with a DJ or lounge music. We take care of everything.',
      'e.t1': 'Wedding', 'e.t2': 'Company party', 'e.t3': 'Birthday', 'e.t4': 'Christmas party', 'e.t5': 'Kids\' birthday →', 'e.lbl': 'The hall · Mariahilfer Straße 117',
      'f.title': 'Plan your <em>party.</em>', 'f.lead': 'No obligation – we reply within 24 hours.',
      'f.anlass': 'Occasion', 'f.other': 'Something else', 'f.datum': 'Preferred date', 'f.gaeste': 'Guests', 'f.bereich': 'Area', 'f.b1': 'Own area', 'f.b2': 'Whole venue', 'f.b3': 'Not sure yet',
      'f.essen': 'Food', 'f.e1': 'Set menu', 'f.e2': 'Buffet', 'f.e3': 'À la carte', 'f.e4': 'Finger food & tapas', 'f.musik': 'Music', 'f.m3': 'None',
      'f.name': 'Name', 'f.tel': 'Phone', 'f.mail': 'Email', 'f.msg': 'Message', 'f.msgph': 'Tell us a little about your party …',
      'f.ds': 'I agree that my details are stored to process this request (<a href="datenschutz.html">privacy</a>).', 'f.send': 'Send request',
      'j.eyebrow': '09 — 20 Nov 2026', 'j.title': 'Years of <em>Freiraum.</em>', 'j.lead': 'On 20 November we come of age. Celebrate with us – we are already counting.',
      'j.past': 'Thank you for 18 years of Freiraum – here is to the next!', 'j.d': 'days', 'j.h': 'hours', 'j.m': 'minutes', 'j.s': 'seconds',
      'v.eyebrow': '10 — Visit · <b>U3 Zieglergasse</b>', 'v.title': 'Come <em>by.</em>', 'v.route': 'Directions ↗',
      'v.addr': '<b>Mariahilfer Straße 117</b>, 1060 Vienna · U3 Zieglergasse / U6 Westbahnhof',
      'v.venue': 'Venue', 'v.kitchen': 'Kitchen', 'v.pizza': 'Pizza', 'v.spiel': 'Spielraum', 'v.open': 'open', 'v.closed': 'closed',
      'v.h.venue': 'Mon 8–23 · Tue–Thu 8–24 · Fri–Sat 8–2 · Sun 9–23', 'v.h.kitchen': 'daily until 21:45', 'v.h.pizza': 'from 11 am', 'v.h.spiel': 'daily 9–18',
      'ft.visit': 'Visit', 'ft.hours': 'Opening hours', 'ft.contact': 'Contact', 'ft.more': 'More', 'ft.h': 'Mon 8–23 · Tue–Thu 8–24<br>Fri–Sat 8–2 · Sun 9–23<br>Kitchen until 21:45',
      'ft.legal': 'Imprint & privacy', 'ft.draft': 'Draft · nemistudio',
      'zen.alt': 'Booking via Zenchef. Prefer to call? <a href="tel:+4315969600">+43 1 596 96 00</a>',
    },
  });

  /* ---------------- Wörter aufteilen (nach jedem Sprachwechsel neu) ---------------- */
  function splitAll() {
    $$('.split').forEach((el) => { delete el.dataset.split; FR.splitWords(el); el.querySelectorAll('.w>span').forEach((s, i) => (s.style.transitionDelay = i * 55 + 'ms')); });
  }
  document.addEventListener('fr:lang', () => { splitAll(); buildDial(); buildHours(); buildIndex(); reels.forEach((r) => r.label()); });

  /* ---------------- Bildfolgen ---------------- */
  class Seq {
    constructor(base, count) { this.base = base; this.count = count; this.imgs = new Array(count); this.loaded = new Array(count).fill(false); this.set = SET(); }
    src(i) { return `${this.base}/${this.set}/${String(i + 1).padStart(4, '0')}.webp`; }
    load(i) {
      if (this.imgs[i]) return this.imgs[i].p;
      const im = new Image(); im.decoding = 'async';
      im.p = new Promise((res) => { im.onload = () => { this.loaded[i] = true; res(im); }; im.onerror = () => res(null); });
      im.src = this.src(i); this.imgs[i] = im; return im.p;
    }
    nearest(i) {
      i = Math.round(clamp(i, 0, this.count - 1));
      if (this.loaded[i]) return this.imgs[i];
      for (let d = 1; d < this.count; d++) { if (this.loaded[i - d]) return this.imgs[i - d]; if (this.loaded[i + d]) return this.imgs[i + d]; }
      return null;
    }
  }
  const Q = []; let active = 0;
  function enqueue(seq, from, to, step = 1) { for (let i = from; i <= to; i += step) Q.push([seq, i]); pump(); }
  function pump() { while (active < 6 && Q.length) { const [s, i] = Q.shift(); if (s.imgs[i]) continue; active++; s.load(i).then(() => { active--; pump(); }); } }
  function loadSeq(seq) { enqueue(seq, 0, seq.count - 1, 6); enqueue(seq, 0, seq.count - 1, 2); enqueue(seq, 1, seq.count - 1, 2); }
  function fitCanvas(cv) {
    const r = cv.getBoundingClientRect(), w = Math.round(r.width * DPR), h = Math.round(r.height * DPR);
    if (w && h && (cv.width !== w || cv.height !== h)) { cv.width = w; cv.height = h; }
    return cv.getContext('2d');
  }
  function drawCover(g, im, scale = 1, oy = 0.5) {
    if (!im) return;
    const cw = g.canvas.width, ch = g.canvas.height, ir = im.naturalWidth / im.naturalHeight, cr = cw / ch;
    let w, h; if (ir > cr) { h = ch; w = ch * ir; } else { w = cw; h = cw / ir; }
    w *= scale; h *= scale;
    g.drawImage(im, (cw - w) / 2, (ch - h) * oy, w, h);
  }
  // Ein Canvas, das einer Bildfolge folgt; der Bildindex gleitet weich zum Ziel
  class Player {
    constructor(cv, seq, opts = {}) { this.cv = cv; this.seq = seq; this.cur = 0; this.target = 0; this.drawn = -1; this.scale = opts.scale || 1; this.oy = opts.oy ?? 0.5; }
    tick(force) {
      this.cur += (this.target - this.cur) * (FR.reduced ? 1 : 0.22);
      if (Math.abs(this.target - this.cur) < 0.02) this.cur = this.target;
      const im = this.seq.nearest(this.cur);
      const key = im ? im.src : '';
      if (!force && key === this.drawn) return;
      const g = fitCanvas(this.cv); g.clearRect(0, 0, this.cv.width, this.cv.height);
      drawCover(g, im, this.scale, this.oy); this.drawn = key;
    }
  }

  /* ---------------- Kapitel & Scroll-Geometrie ---------------- */
  const sections = $$('main > section, footer.foot');
  const chapters = sections.filter((s) => s.dataset.ch);
  let geo = [];
  function measure() {
    W = innerWidth; H = innerHeight; MOBILE = W <= 860;
    sizeGallery();
    geo = sections.map((s) => { const r = s.getBoundingClientRect(); return { el: s, top: r.top + scrollY, h: r.height }; });
  }
  const progressOf = (el) => { const g = geo.find((x) => x.el === el); if (!g) return 0; return clamp((scrollY - g.top) / Math.max(1, g.h - H)); };

  /* Farbe/Größe des Mondes zwischen Kapiteln mischen */
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const FX = ['flour', 'embers', 'steam', 'bubbles', 'sparkle', 'gold'];
  function stateOf(el) {
    const s = { glow: hex(el.dataset.glow || '#f3e2c0'), dsc: +(el.dataset.dsc || 1), dop: +(el.dataset.dop || 1), fx: {} };
    FX.forEach((k) => (s.fx[k] = el.dataset.fx === k ? 1 : 0));
    if (el.id === 'pizza') pizzaState(s);
    if (el.id === 'feiern' || el.id === 'besuch') s.dsc = 0.6;
    return s;
  }
  function mix(a, b, t) {
    const o = { glow: a.glow.map((v, i) => lerp(v, b.glow[i], t)), dsc: lerp(a.dsc, b.dsc, t), dop: lerp(a.dop, b.dop, t), fx: {} };
    FX.forEach((k) => (o.fx[k] = lerp(a.fx[k], b.fx[k], t)));
    return o;
  }
  let sky = null;
  function blendSky() {
    const yc = scrollY + H * 0.5, Z = H * 0.5;
    let i = geo.findIndex((g) => yc >= g.top && yc < g.top + g.h);
    if (i < 0) i = yc < (geo[0] ? geo[0].top : 0) ? 0 : geo.length - 1;
    const g = geo[i]; let st = stateOf(g.el);
    const dEnd = g.top + g.h - yc, dStart = yc - g.top;
    if (dEnd < Z && geo[i + 1]) st = mix(st, stateOf(geo[i + 1].el), 0.5 * (1 - dEnd / Z));
    else if (dStart < Z && geo[i - 1]) st = mix(st, stateOf(geo[i - 1].el), 0.5 * (1 - dStart / Z));
    sky = st;
    const rs = document.documentElement.style;
    rs.setProperty('--glow', `rgb(${st.glow.map((v) => Math.round(v)).join(',')})`);
    rs.setProperty('--dsc', st.dsc.toFixed(3));
    rs.setProperty('--dop', st.dop.toFixed(3));
    return i;
  }

  /* ---------------- Rauch (WebGL) ---------------- */
  const smoke = (function () {
    const cv = $('#smoke'); if (FR.reduced) { cv.remove(); return null; }
    const gl = cv.getContext('webgl', { premultipliedAlpha: false, antialias: false, alpha: true });
    if (!gl) { cv.remove(); return null; }
    const vs = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
    const fs = `precision mediump float;uniform vec2 r;uniform float t;uniform vec3 c;uniform vec2 a;uniform float k;
      float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
      float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
      float fbm(vec2 p){float v=0.,s=.5;for(int i=0;i<5;i++){v+=s*n(p);p=p*2.03+vec2(1.7,9.2);s*=.5;}return v;}
      void main(){vec2 uv=gl_FragCoord.xy/r;vec2 p=uv*vec2(r.x/r.y,1.)*2.2;
        vec2 q=vec2(fbm(p+vec2(0.,t*.05)),fbm(p+vec2(5.2,1.3)-t*.04));
        vec2 w=vec2(fbm(p+3.*q+vec2(1.7,9.2)+t*.03),fbm(p+3.*q+vec2(8.3,2.8)-t*.02));
        float f=fbm(p+3.5*w);
        float wisp=smoothstep(.52,.95,f)*smoothstep(.1,.7,length(w));
        float d=distance(uv*vec2(r.x/r.y,1.),a*vec2(r.x/r.y,1.));
        float m=smoothstep(1.25,.15,d)*(1.-smoothstep(.0,.22,d)*.0);
        float al=wisp*m*k*.55;
        gl_FragColor=vec4(c*(.7+.6*f),al);}`;
    const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; };
    const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { cv.remove(); return null; }
    gl.useProgram(pr);
    const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    const U = { r: gl.getUniformLocation(pr, 'r'), t: gl.getUniformLocation(pr, 't'), c: gl.getUniformLocation(pr, 'c'), a: gl.getUniformLocation(pr, 'a'), k: gl.getUniformLocation(pr, 'k') };
    gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    let last = 0;
    return {
      draw(t, col, strength) {
        if (t - last < 33) return; last = t;  // ~30 fps genügt für Rauch
        const sc = MOBILE ? 0.22 : 0.3, w = Math.round(W * sc), h = Math.round(H * sc);
        if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; gl.viewport(0, 0, w, h); }
        gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        if (strength < 0.01) return;
        const ax = MOBILE ? 0.5 : 0.63, ay = 1 - (MOBILE ? 0.68 : 0.53);
        gl.uniform2f(U.r, w, h); gl.uniform1f(U.t, t / 1000); gl.uniform3f(U.c, col[0] / 255, col[1] / 255, col[2] / 255);
        gl.uniform2f(U.a, ax, ay); gl.uniform1f(U.k, strength);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      },
    };
  })();

  /* ---------------- Partikel ---------------- */
  const fx = (function () {
    const cv = $('#fx'), g = cv.getContext('2d'); const P = [];
    const emitAt = { x: 0, y: 0, on: false };
    function resize() { cv.width = W * DPR; cv.height = H * DPR; }
    function anchor() { const as = Math.min(MOBILE ? W * 0.8 : H * 0.70, MOBILE ? H * 0.4 : W * 0.42); return { x: (MOBILE ? 0.5 : 0.63) * W, y: (MOBILE ? 0.68 : 0.53) * H, s: as }; }
    function spawn(kind) {
      const a = anchor(), r = a.s / 2;
      if (kind === 'flour') P.push({ k: kind, x: Math.random() * W, y: Math.random() * H, vx: (Math.random() - 0.5) * 0.15, vy: -0.05 - Math.random() * 0.12, r: 0.6 + Math.random() * 1.6, life: 1, dl: 0.0018 + Math.random() * 0.002 });
      if (kind === 'embers') { const ang = Math.random() * Math.PI * 2; P.push({ k: kind, x: a.x + Math.cos(ang) * r * 1.02, y: a.y + Math.sin(ang) * r * 1.02 + r * 0.2, vx: (Math.random() - 0.5) * 0.6, vy: -0.6 - Math.random() * 1.4, r: 0.8 + Math.random() * 1.8, life: 1, dl: 0.006 + Math.random() * 0.008 }); }
      if (kind === 'bubbles') P.push({ k: kind, x: a.x + (Math.random() - 0.5) * r * 1.2, y: a.y + r * (0.3 + Math.random() * 0.6), vx: 0, vy: -0.35 - Math.random() * 0.6, r: 1 + Math.random() * 3.2, life: 1, dl: 0.004 + Math.random() * 0.004, ph: Math.random() * 6 });
      if (kind === 'gold') P.push({ k: kind, x: Math.random() * W, y: -10, vx: (Math.random() - 0.5) * 0.4, vy: 0.4 + Math.random() * 0.8, r: 1 + Math.random() * 2.4, life: 1, dl: 0.002 + Math.random() * 0.002, rot: Math.random() * 6, vr: (Math.random() - 0.5) * 0.1 });
      if (kind === 'sparkle' && emitAt.on) P.push({ k: kind, x: emitAt.x + (Math.random() - 0.5) * 30, y: emitAt.y + (Math.random() - 0.5) * 30, vx: (Math.random() - 0.5) * 0.5, vy: 0.2 + Math.random() * 0.6, r: 0.8 + Math.random() * 2.2, life: 1, dl: 0.012 + Math.random() * 0.01 });
    }
    const RATE = { flour: 0.5, embers: 1.6, bubbles: 0.9, gold: 0.7, sparkle: 2.4 };
    function step(t, w) {
      if (FR.reduced) return;
      for (const k in RATE) { const n = (w[k] || 0) * RATE[k] * (MOBILE ? 0.6 : 1); let c = n; while (c > 0) { if (Math.random() < Math.min(1, c)) spawn(k); c -= 1; } }
      g.setTransform(DPR, 0, 0, DPR, 0, 0); g.clearRect(0, 0, W, H);
      for (let i = P.length - 1; i >= 0; i--) {
        const p = P[i]; p.life -= p.dl; p.x += p.vx; p.y += p.vy;
        if (p.k === 'embers') { p.vx += (Math.random() - 0.5) * 0.08; }
        if (p.k === 'bubbles') { p.x += Math.sin(t / 400 + p.ph) * 0.25; }
        if (p.life <= 0 || p.y < -20 || p.y > H + 20) { P.splice(i, 1); continue; }
        const fade = Math.min(1, p.life * 3) * Math.min(1, (1 - p.life) * 8);
        if (p.k === 'flour') { g.fillStyle = `rgba(255,248,235,${0.35 * fade})`; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); }
        else if (p.k === 'embers') { g.fillStyle = `rgba(255,${140 + Math.random() * 60 | 0},60,${0.9 * fade})`; g.shadowColor = '#ff7a2f'; g.shadowBlur = 8; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); g.shadowBlur = 0; }
        else if (p.k === 'bubbles') { g.strokeStyle = `rgba(255,235,210,${0.55 * fade})`; g.lineWidth = 0.8; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.stroke(); }
        else if (p.k === 'gold') { p.rot += p.vr; g.fillStyle = `rgba(240,205,130,${0.8 * fade})`; g.save(); g.translate(p.x, p.y); g.rotate(p.rot); g.fillRect(-p.r, -p.r * 0.4, p.r * 2, p.r * 0.8); g.restore(); }
        else if (p.k === 'sparkle') { g.fillStyle = `rgba(255,255,255,${fade})`; g.shadowColor = '#bfe4ff'; g.shadowBlur = 10; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); g.shadowBlur = 0; }
      }
    }
    return { resize, step, emitAt };
  })();

  /* ---------------- Hero ---------------- */
  const hero = $('#start'), heroObj = $('#heroObj');
  function renderHero(t) {
    const p = progressOf(hero);
    const rot = p * 160 + (FR.reduced ? 0 : t * 0.004);
    const bob = FR.reduced ? 0 : Math.sin(t / 1400) * 8;
    const s = 1 - p * 0.18;
    heroObj.style.transform = `translate3d(0,${bob + p * H * 0.08}px,0) rotate(${rot}deg) scale(${s})`;
    heroObj.style.opacity = (1 - clamp((p - 0.82) / 0.18)).toFixed(3);
    const layer = $('.layer', hero); layer.classList.toggle('gone', p > 0.62);
  }
  function buildDots() {
    const d = $('#heroDots'); d.innerHTML = '';
    chapters.slice(0, 5).forEach((c, i) => { const b = document.createElement('button'); b.setAttribute('aria-label', c.dataset.ch); if (!i) b.className = 'on'; b.onclick = () => go(c); d.appendChild(b); });
  }

  /* ---------------- Vom Teig zum Feuer ---------------- */
  const pizzaSec = $('#pizza');
  const PIZZA = { count: 206, steps: [{ id: 'teig', from: 0, to: 25 }, { id: 'belag', from: 26, to: 46 }, { id: 'ofen', from: 47, to: 92 }, { id: 'feuer', from: 93, to: 162 }, { id: 'genuss', from: 163, to: 205 }] };
  const STEP_GLOW = ['#f6e2bf', '#f8d2a0', '#ff9b52', '#ff7a2f', '#ffc47f'];
  let pizzaSeq, pizzaPlayer, pizzaStep = -1;
  function pizzaLocal(p) { const n = PIZZA.steps.length, x = clamp(p * 1.04 - 0.02) * n; const i = Math.min(n - 1, Math.floor(x)); return { i, lp: x - i }; }
  function pizzaState(s) {
    const { i, lp } = pizzaLocal(progressOf(pizzaSec));
    const a = hex(STEP_GLOW[i]), b = hex(STEP_GLOW[Math.min(4, i + 1)]), t = smooth(clamp((lp - 0.7) / 0.3));
    s.glow = a.map((v, k) => lerp(v, b[k], t));
    s.fx.embers = i === 2 || i === 3 ? 1 : i === 4 ? 0.3 : 0;
    s.fx.flour = i < 2 ? 0.8 : 0;
  }
  function buildDial() {
    const g = $('#dialMarks'), names = FR.t('p.m').split(',');
    g.innerHTML = names.map((n, i) => {
      const a = (i / names.length) * Math.PI * 2 - Math.PI / 2, x = 50 + Math.cos(a) * 46, y = 50 + Math.sin(a) * 46;
      const tx = 50 + Math.cos(a) * 50.6, ty = 50 + Math.sin(a) * 50.6;
      return `<circle class="tick" cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r=".9"/><text x="${tx.toFixed(2)}" y="${ty.toFixed(2)}"><title>${n}</title>${String(i + 1).padStart(2, '0')}</text>`;
    }).join('');
  }
  function renderPizza() {
    const p = progressOf(pizzaSec), { i, lp } = pizzaLocal(p), st = PIZZA.steps[i];
    if (pizzaPlayer) { pizzaPlayer.target = st.from + clamp(lp * 1.1) * (st.to - st.from); pizzaPlayer.tick(); }
    $('#dialBar').style.strokeDashoffset = (100 - clamp(p * 1.04 - 0.02) * 100).toFixed(2);
    if (i !== pizzaStep) {
      $$('#steps .step').forEach((el, k) => { el.classList.toggle('on', k === i); el.classList.toggle('gone', k < i); });
      $$('#dialMarks .tick').forEach((el, k) => el.classList.toggle('on', k <= i));
      $$('#dialMarks text').forEach((el, k) => el.classList.toggle('on', k === i));
      pizzaStep = i;
    }
  }

  /* ---------------- Manifest ---------------- */
  const marqs = $$('.marq'), manifest = $('#manifest');
  function renderManifest() {
    const g = geo.find((x) => x.el === manifest); if (!g) return;
    const rel = scrollY + H - g.top; if (rel < -200 || rel > g.h + H + 200) return;
    marqs.forEach((m) => { const sp = +m.dataset.speed; m.style.transform = `translate3d(${(sp > 0 ? -40 : 0) + sp * rel * 0.035}vw,0,0)`; });
  }
  function countUp(el) {
    const to = +el.dataset.count, from = to > 1000 ? 1990 : 0, t0 = performance.now(), D = 1600;
    (function f(t) { const k = ease(clamp((t - t0) / D)); el.textContent = Math.round(lerp(from, to, k)); if (k < 1) requestAnimationFrame(f); })(t0);
  }

  /* ---------------- Küche (horizontal) ---------------- */
  const hz = $('#kueche'), track = $('#track'), cards = $$('.card', track);
  function sizeGallery() { const dist = Math.max(0, track.scrollWidth - innerWidth); hz.style.height = innerHeight + dist + 'px'; hz.dataset.dist = dist; }
  function renderGallery() {
    const p = clamp((progressOf(hz) - 0.06) / 0.9), dist = +hz.dataset.dist || 0;
    track.style.transform = `translate3d(${-p * dist}px,0,0)`;
    let best = 0, bd = 1e9;
    cards.forEach((c, i) => {
      const r = c.getBoundingClientRect(), cx = r.left + r.width / 2, rel = (cx - W / 2) / W;
      const im = c.querySelector('img'); im.style.transform = `translate3d(${rel * -40}px,0,0) scale(1.06)`;
      const d = Math.abs(cx - W / 2); if (d < bd) { bd = d; best = i; }
    });
    $('#kCount').textContent = String(best + 1).padStart(2, '0') + ' / ' + String(cards.length).padStart(2, '0');
  }

  /* ---------------- Gepinnte Ebenen (Kaffee, Drinks) ---------------- */
  function layers(sec, p) {
    const ls = $$('.layer', sec); let cur = 0;
    ls.forEach((l, i) => { if (p >= +l.dataset.at) cur = i; });
    ls.forEach((l, i) => { l.classList.toggle('on', i === cur); l.classList.toggle('gone', i < cur); });
    return cur;
  }
  const kaffee = $('#kaffee'), coffeeObj = $('#coffeeObj'), coffeeStage = $('#coffeeStage');
  function renderKaffee(t) {
    const p = progressOf(kaffee), cur = layers(kaffee, p);
    coffeeStage.classList.toggle('swap', cur === 2);
    $('.steam', coffeeStage).style.opacity = cur === 2 ? 0 : 0.55;
    const bob = FR.reduced ? 0 : Math.sin(t / 1600) * 6;
    coffeeObj.style.transform = `translate3d(0,${bob}px,0) rotate(${-14 + p * 36}deg) scale(${0.94 + Math.sin(p * Math.PI) * 0.06})`;
  }
  const drinks = $('#drinks'), drinkObj = $('#drinkObj');
  function renderDrinks(t) {
    const p = progressOf(drinks); layers(drinks, p);
    const sway = FR.reduced ? 0 : Math.sin(t / 1800) * 3;
    drinkObj.style.transform = `translate3d(0,${Math.sin(t / 1300) * 7 - p * 20}px,0) rotate(${sway - 4 + p * 8}deg)`;
  }

  /* ---------------- Reels ---------------- */
  const IG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg>';
  const CM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M20 12a8 8 0 0 1-11.6 7.1L4 20l1-4A8 8 0 1 1 20 12z"/></svg>';
  const REELS = [
    { v: 'reel-wer-zahlt', likes: 202, comments: 30, cap: 'Wer zahlt bei euch das Essen im Restaurant? 👀' },
    { v: 'reel-18-jahre', likes: 45, comments: 5, cap: '🎂 18 YEARS OF FREIRAUM! Wir werden volljährig …' },
    { v: 'reel-tapas', likes: 28, comments: 3, cap: 'Feierabend heißt bei uns: kleine Teller, große Genüsse 🍢🥂' },
  ];
  const reels = [];
  function reelCard(r, host) {
    const el = document.createElement('div'); el.className = 'reel';
    el.innerHTML = `<video muted loop playsinline preload="none" poster="shared/video/${r.v}.jpg" src="shared/video/${r.v}.mp4"></video>
      <div class="top"><span class="av">${FR.logo()}</span><b>freiraumwien</b><span class="snd"></span></div>
      <div class="bot"><span class="cnt"><span>${IG}${r.likes}</span><span>${CM}${r.comments}</span></span><span class="txt">${r.cap}</span></div>`;
    host.appendChild(el);
    const v = el.querySelector('video'), snd = el.querySelector('.snd');
    const o = { el, v, label() { snd.textContent = v.muted ? FR.t('r.tap') : FR.t('r.on'); } };
    el.addEventListener('click', () => {
      const on = v.muted; reels.forEach((x) => { x.v.muted = true; x.label(); });
      v.muted = !on; if (!v.muted) v.play().catch(() => {}); o.label();
    });
    o.label(); reels.push(o);
    new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) v.play().catch(() => {}); else { v.pause(); v.muted = true; o.label(); } }), { threshold: 0.35 }).observe(el);
  }

  /* ---------------- Spielraum ---------------- */
  const spiel = $('#spielraum'), rio = $('#rio');
  function bez(p0, p1, p2, p3, t) { const u = 1 - t; return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3; }
  function renderSpiel() {
    const p = progressOf(spiel), r = progressOf(spiel) > 0 || scrollY + H > (geo.find((g) => g.el === spiel) || {}).top;
    const a = { x: (MOBILE ? 0.5 : 0.63) * W, y: (MOBILE ? 0.68 : 0.53) * H, s: Math.min(MOBILE ? W * 0.8 : H * 0.70, MOBILE ? H * 0.4 : W * 0.42) };
    const t = clamp((p - 0.02) / 0.96);
    const X = MOBILE ? [-0.3 * a.s, a.x - a.s * 0.5, a.x + a.s * 0.3, W + a.s * 0.3] : [a.x - a.s * 0.62, a.x - a.s * 0.62, a.x + a.s * 0.1, W + a.s * 0.25];
    const Y = MOBILE ? [a.y + a.s * 0.3, a.y - a.s * 0.75, a.y + a.s * 0.45, a.y - a.s * 0.6] : [H + a.s * 0.25, a.y - a.s * 0.25, a.y - a.s * 0.95, a.y - a.s * 0.2];
    const x = bez(...X, t), y = bez(...Y, t), x2 = bez(...X, Math.min(1, t + 0.01)), y2 = bez(...Y, Math.min(1, t + 0.01));
    const ang = Math.atan2(y2 - y, x2 - x) * 180 / Math.PI;
    const rw = a.s * 0.42;
    rio.style.transform = `translate3d(${x - rw / 2}px,${y - rw * 0.65}px,0) rotate(${clamp(ang * 0.35, -25, 25)}deg)`;
    fx.emitAt.on = r && t > 0 && t < 1; fx.emitAt.x = x; fx.emitAt.y = y + rw * 0.1;
    $$('.pola', spiel).forEach((el, i) => { el.style.translate = `0 ${(p - 0.5) * (i ? -60 : 60)}px`; });
    $$('#clouds i').forEach((el, i) => { el.style.transform = `translate3d(${(p - 0.3) * (i % 2 ? -1 : 1) * (40 + i * 25)}%,0,0)`; });
  }

  /* ---------------- Feiern & Besuch (Bogen mit Bildfolge) ---------------- */
  const feiern = $('#feiern'), besuch = $('#besuch');
  let salaPlayer, fasadaPlayer;
  function renderFeiern() {
    const p = progressOf(feiern);
    if (salaPlayer) { salaPlayer.target = clamp(p * 1.08) * 79; salaPlayer.tick(); }
    $('#n350').textContent = Math.round(ease(clamp(p / 0.55)) * 350);
  }
  function renderBesuch() {
    const p = progressOf(besuch);
    if (fasadaPlayer) { fasadaPlayer.target = clamp(p * 1.1) * 79; fasadaPlayer.tick(); }
  }
  function buildHours() {
    const v = FR.vienna();
    const rows = [['venue', 'v.venue', 'v.h.venue'], ['kitchen', 'v.kitchen', 'v.h.kitchen'], ['pizza', 'v.pizza', 'v.h.pizza'], ['spielraum', 'v.spiel', 'v.h.spiel']];
    $('#hours').innerHTML = rows.map(([k, l, h]) => { const o = FR.isOpen(k, v); return `<div><span>${FR.t(l)}</span><span>${FR.t(h)}</span><em class="${o ? '' : 'c'}">${FR.t(o ? 'v.open' : 'v.closed')}</em></div>`; }).join('');
  }

  /* ---------------- 18 Jahre ---------------- */
  const jahre = $('#jahre'), n18 = $('#n18');
  const BDAY = Date.parse('2026-11-20T00:00:00+01:00');
  function countdown() {
    const ms = BDAY - Date.now(), cells = $$('#cd b');
    if (ms <= 0) { $('#cd').style.display = 'none'; $('#jLead').textContent = FR.t('j.past'); return; }
    const s = Math.floor(ms / 1000);
    [Math.floor(s / 86400), Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60].forEach((v, i) => (cells[i].textContent = i ? String(v).padStart(2, '0') : v));
  }
  function renderJahre() {
    const g = geo.find((x) => x.el === jahre); if (!g) return;
    const k = clamp((scrollY + H * 0.85 - g.top) / (g.h * 0.75));
    n18.style.backgroundPosition = `0 ${(k * 100).toFixed(1)}%`;
  }

  /* ---------------- Navigation ---------------- */
  const nav = $('#nav'), bar = $('#progress'), nextBtn = $('#next');
  function buildIndex() {
    $('#index').innerHTML = chapters.map((c) => `<li><a href="#${c.id}" data-id="${c.id}"><span>${FR.t(c.dataset.label)}</span>${c.dataset.ch}<i></i></a></li>`).join('');
  }
  function go(el) {
    const g = geo.find((x) => x.el === el); if (!g) return;
    let y = g.top; if (el.id === 'kueche' || el.classList.contains('pin')) y += 2;
    scrollTo({ top: y, behavior: FR.reduced ? 'auto' : 'smooth' });
  }
  let curCh = -1;
  function renderNav(si) {
    nav.classList.toggle('solid', scrollY > 40);
    const max = document.documentElement.scrollHeight - H, pr = clamp(scrollY / Math.max(1, max));
    bar.style.transform = `scaleX(${pr})`;
    nextBtn.style.setProperty('--p', pr.toFixed(3));
    const yc = scrollY + H * 0.5; let ci = 0;
    chapters.forEach((c, i) => { const g = geo.find((x) => x.el === c); if (g && yc >= g.top) ci = i; });
    if (ci !== curCh) {
      curCh = ci; const id = chapters[ci].id;
      $$('#index a').forEach((a) => a.classList.toggle('on', a.dataset.id === id));
      $$('.nav ul a').forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + id));
      $$('#heroDots button').forEach((b, i) => b.classList.toggle('on', i === Math.min(ci, 4)));
    }
    nextBtn.classList.toggle('up', pr > 0.985);
  }
  nextBtn.addEventListener('click', () => {
    if (nextBtn.classList.contains('up')) { scrollTo({ top: 0, behavior: 'smooth' }); return; }
    const yc = scrollY + 4; const nx = chapters.find((c) => { const g = geo.find((x) => x.el === c); return g && g.top > yc + 2; });
    if (nx) go(nx); else scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const el = document.getElementById(a.getAttribute('href').slice(1)); if (!el) return;
    e.preventDefault(); closeMenu(); go(el);
  });
  const menu = $('#menu');
  function closeMenu() { menu.classList.remove('open'); document.body.style.overflow = ''; }
  $('#burger').onclick = () => { menu.classList.add('open'); $$('a.big', menu).forEach((a, i) => (a.style.transitionDelay = 0.08 + i * 0.05 + 's')); };
  $('#menuClose').onclick = closeMenu;
  $$('.lang span').forEach((s) => (s.onclick = () => FR.setLang(s.dataset.l)));

  /* Zenchef erst auf Klick */
  const zen = $('#zen');
  document.addEventListener('click', (e) => {
    if (!e.target.closest('[data-reserve]')) return;
    const f = $('iframe', zen); if (!f.src) f.src = f.dataset.src + FR.lang;
    closeMenu(); zen.classList.add('open');
  });
  $('#zenClose').onclick = () => zen.classList.remove('open');
  zen.addEventListener('click', (e) => { if (e.target === zen) zen.classList.remove('open'); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape') { zen.classList.remove('open'); closeMenu(); } });

  /* Cursor und leichte Maus-Parallaxe */
  if (!FR.touch) {
    FR.cursor();
    addEventListener('pointermove', (e) => {
      const rs = document.documentElement.style;
      rs.setProperty('--mx', ((e.clientX / W - 0.5) * 2).toFixed(3)); rs.setProperty('--my', ((e.clientY / H - 0.5) * 2).toFixed(3));
    }, { passive: true });
  }

  /* Einblenden beim Scrollen */
  function reveal() {
    const els = $$('.rv:not(.in)');
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in'); io.unobserve(e.target);
      const c = e.target.querySelector('[data-count]'); if (c) countUp(c);
    }), { rootMargin: '0px 0px -12% 0px' });
    els.forEach((el) => io.observe(el));
  }

  /* ---------------- Loader ---------------- */
  async function loader() {
    const cv = $('#loaderLogo'), g = cv.getContext('2d'), pct = $('#pct');
    let sk = null; try { sk = await FR.json('shared/svg/logo-skeleton.json'); } catch (e) { sk = null; }
    let pts = [];
    if (sk) {
      const sc = cv.width / sk.viewBox[2];
      const paths = sk.paths.slice().sort((a, b) => Math.min(...a.map((p) => p[0])) - Math.min(...b.map((p) => p[0])));
      paths.forEach((pl) => pl.forEach((p, i) => pts.push({ x: p[0] * sc, y: p[1] * sc, r: Math.max(1.5, p[2] * sc * 0.55), first: i === 0 })));
      if (sk.dot) pts.push({ x: sk.dot[0] * sc, y: sk.dot[1] * sc, r: sk.dot[2] * sc * 0.7, first: true, dot: true });
    }
    const jobs = [];
    const img = (src) => new Promise((r) => { const i = new Image(); i.onload = i.onerror = () => r(); i.src = src; });
    jobs.push(document.fonts ? document.fonts.ready : Promise.resolve());
    jobs.push(img('assets/cut/pizza.webp'));
    for (let i = 0; i < 24; i++) jobs.push(pizzaSeq.load(i));
    let done = 0; jobs.forEach((j) => j.then(() => done++));
    const t0 = performance.now(); let shown = 0, drawn = 0;
    g.strokeStyle = g.fillStyle = '#efe6d6'; g.lineCap = g.lineJoin = 'round';
    await new Promise((resolve) => {
      (function frame(t) {
        const real = done / jobs.length, minT = clamp((t - t0) / 1700), maxT = clamp((t - t0) / 5000);
        const target = Math.max(maxT, Math.min(real, minT));
        shown += (target - shown) * 0.12; if (target >= 1 && shown > 0.995) shown = 1;
        pct.textContent = Math.round(shown * 100) + ' %';
        const upto = Math.floor(shown * pts.length);
        for (; drawn < upto; drawn++) {
          const p = pts[drawn], q = pts[drawn - 1];
          if (p.dot) { g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); continue; }
          if (q && !p.first && !q.dot) { g.lineWidth = (p.r + q.r); g.beginPath(); g.moveTo(q.x, q.y); g.lineTo(p.x, p.y); g.stroke(); }
        }
        if (shown >= 1) return resolve();
        requestAnimationFrame(frame);
      })(t0);
    });
    await new Promise((r) => setTimeout(r, 250));
    $('#loader').classList.add('done');
    setTimeout(() => $('#loader').remove(), 1400);
    $('.layer', hero).classList.add('on');
  }

  /* ---------------- Start ---------------- */
  FR.applyLang(); splitAll(); buildDial(); buildHours(); buildIndex(); buildDots();
  REELS.forEach((r) => reelCard(r, $('#reels')));
  reelCard({ v: 'reel-eventlocation', likes: 155, comments: 10, cap: 'Die perfekte Eventlocation in Wien? Hast du gerade gefunden!' }, $('#eventReel'));
  FR.bindForm($('#eventForm'), 'event');
  FR.updateJetzt(); setInterval(FR.updateJetzt, 4000);
  countdown(); setInterval(countdown, 1000);
  $('.layer', hero).classList.remove('on');

  pizzaSeq = new Seq('assets/seq/pizza', PIZZA.count);
  pizzaPlayer = new Player($('#pizzaCv'), pizzaSeq);
  const salaSeq = new Seq('shared/seq/sala', 80), fasadaSeq = new Seq('shared/seq/fasada', 80);
  salaPlayer = new Player($('#salaCv'), salaSeq); fasadaPlayer = new Player($('#fasadaCv'), fasadaSeq);
  loader().then(() => { loadSeq(pizzaSeq); setTimeout(() => { loadSeq(salaSeq); loadSeq(fasadaSeq); }, 2500); });

  measure(); fx.resize(); reveal();
  addEventListener('resize', () => { measure(); fx.resize(); [pizzaPlayer, salaPlayer, fasadaPlayer].forEach((pl) => pl.tick(true)); buildDial(); });
  addEventListener('load', measure);
  if (document.fonts) document.fonts.ready.then(measure);

  let lastSi = -1;
  (function loop(t) {
    const si = blendSky();
    renderNav(si);
    renderHero(t); renderPizza(); renderManifest(); renderGallery(); renderKaffee(t); renderDrinks(t);
    renderSpiel(); renderFeiern(); renderBesuch(); renderJahre();
    if (sky) {
      const smokeK = (lerp(0.35, 1, sky.dop)) * (sky.fx.sparkle ? 0.4 : 1);
      smoke && smoke.draw(t, sky.glow, smokeK);
      fx.step(t, sky.fx);
    }
    if (si !== lastSi) { lastSi = si; }
    requestAnimationFrame(loop);
  })(0);
})();
