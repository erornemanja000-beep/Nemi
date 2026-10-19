/* Freiraum Premium – „Ein Tag im Freiraum“: Tageszeit, Lichtscheibe, Rauch, Partikel, Bildfolgen und Kapitel,
   alles hängt an der Scrollposition. */
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
      'nav.morgen': 'Morgen', 'nav.kueche': 'Küche', 'nav.spiel': 'Spielraum', 'nav.abend': 'Abend', 'nav.pizza': 'Pizza', 'nav.bar': 'Bar',
      'nav.jahre': '18 Jahre', 'scroll': 'Scrollen', 'cta.reserve': 'Tisch reservieren', 'cta.menu': 'Speisekarte', 'cta.allmenu': 'Ganze Speisekarte',
      'h.eyebrow': 'Mariahilfer Straße 117 · <b>seit 2008</b>', 'h.title': 'Ein Tag im <em>Freiraum.</em>',
      'h.lead': 'Vom ersten Röstraum-Espresso am Morgen bis zum letzten Drink um 2 – scroll dich durch unseren Tag.',
      'h.jump': 'Spring ins Jetzt',
      'c.eyebrow': 'Röstraum · <b>unsere hauseigene Rösterei</b>', 'c.title': 'Guten Morgen, <em>Wien.</em>',
      'c.lead': 'Jeder Espresso beginnt bei uns in der eigenen Rösterei – dunkel, samtig, Mo–Sa ab 8 und So ab 9 Uhr.',
      'b2.eyebrow': 'Frühstück · <b>täglich bis 17 Uhr</b>', 'b2.title': 'Frühstück, <em>so lange</em> du willst.',
      'b2.lead': 'Signature Boxes, Pancakes, Bowls – und Eier, wie du sie magst.',
      'c.b1': 'Schinken, Emmentaler, weiches Ei, Kornspitz', 'c.b2': 'Mini Rösti, Spiegelei, Speck, Avocado', 'c.b3': 'Falafel, Hummus, Ajvar, Oliven',
      'm.s1': 'Mitten auf der Mahü', 'm.s2': 'Gäste bei Feiern', 'm.s3': 'Tage die Woche geöffnet', 'm.s4': 'Gerichte & Drinks auf der Karte',
      'k.eyebrow': 'Mittag · Küche bis <b>21:45</b>', 'k.title': 'One World <em>Kitchen.</em>',
      'k.lead': 'Wir bringen die ganze Welt nach Wien – von Wiener Schnitzel bis Falafel-Bowl, von Sous-vide-Ente bis Tacos zum Teilen.',
      'k.d1': 'mit Grillgemüse und Salsa-Dip', 'k.d2': 'San-Marzano-Tomaten, knusprige Garnelen', 'k.d3': 'Kirschsauce, knusprige Polenta',
      'k.d4': 'Stracciatella di bufala, Rucola, Rinderschinken', 'k.n5': 'Tapas zum Teilen', 'k.d5': 'Tacos, Patatas Bravas, Garnelen-Tempura', 'k.p5': 'ab 4,9',
      'k.d6': 'Blattsalate, Schafskäse, Walnüsse', 'k.d7': 'flüssiger Schokokern, Himbeereis',
      's.eyebrow': 'Spielraum im Freiraum · <b>täglich 9–18 Uhr</b>', 's.title': 'Ihr genießt. <em>die Kinder</em> toben.',
      's.lead': 'Rutsche, Bällebad und Trampolin – direkt hinter der Glaswand. Ihr esst in Ruhe, die Kleinen sind in Sichtweite. RIO passt auf.',
      's.cta': 'Spielraum entdecken', 's.party': 'Kindergeburtstag',
      'fl.eyebrow': 'Golden Hour · <b>Mariahilfer Straße</b>', 'fl.title': 'Ab jetzt wird\'s <em>Bar.</em>', 'fl.lead': 'Lichter an, Musik lauter – der Freiraum wechselt in den Abend.',
      'n1.eyebrow': 'Golden Hour · <b>ab 17 Uhr</b>', 'n1.title': 'Zeit für <em>Drinks.</em>', 'n1.lead': 'Signature Cocktails, hausgemachte Sirups und Sprizz in allen Farben.',
      'd.p1': 'Rose Secco, Pfirsich, Gurke, Rosmarin', 'd.p2': 'Gin, Aperol, Maracuja, Ananas', 'd.p3': 'Gin, Erdbeer-Bitter, Feige', 'd.p4': 'alkoholfrei · Ananas, Maracuja, Ginger Ale',
      'd.p5': 'Prosecco, Maracuja, Basilikum', 'd.p6': 'Prosecco, Granatapfel, Minze',
      'n2.eyebrow': 'Jeden Donnerstag · <b>Ladies Night</b>', 'n2.title': 'Freiraum <em>Sprizz.</em>',
      'n2.lead': 'Rose Secco, Pfirsich, Gurke, Rosmarin – unser Signature-Sprizz. Und donnerstags geht das erste Glas Prosecco auf uns.',
      'n3.eyebrow': 'Pizzastation · <b>Holzofen</b>', 'n3.title': 'Echtes <em>Feuer.</em>', 'n3.lead': 'Naturhefe-Sauerteig, Caputo-Manitoba-Mehl, mindestens 48 Stunden Reifezeit.',
      'n3.p3': 'Burrata, gelbe Cherrytomaten, Basilikumpesto',
      'p.eyebrow': 'Ohne Filter · <b>echte Clips aus unserer Pizzastation</b>', 'p.title': 'Vom Teig <em>zum</em> Feuer.',
      'p.s1h': 'Teig', 'p.s1': 'Naturhefe-Sauerteig aus Caputo-Manitoba-Mehl, jeden Tag von Hand geformt.',
      'p.s2h': 'Belag', 'p.s2': 'Was draufkommt, kommt frisch: Trüffel, Prosciutto, Fior di Latte.',
      'p.s3h': 'Ofen', 'p.s3': 'Rein in den Holzofen – direkt vor deinen Augen, hinter der Glasscheibe.',
      'p.s4h': 'Feuer', 'p.s4': 'Mindestens 48 Stunden Reifezeit, dann ein paar Minuten echtes Feuer. Mehr braucht es nicht.',
      'p.s5h': 'Genuss', 'p.s5': 'Burrata und Basilikum zum Schluss – und ab an deinen Tisch.',
      'p.sunday': 'Pizza Sunday · jeden Sonntag 14–22 Uhr · ausgewählte Pizzen 9,90 €', 'p.m': 'Teig,Belag,Ofen,Feuer,Genuss',
      'b.eyebrow': 'Freitag &amp; Samstag <b>bis 2 Uhr</b>', 'b.title': 'Bar &amp; <em>Beats.</em>',
      'b.lead': 'Wenn\'s draußen dunkel wird, wird\'s bei uns laut: DJ-Abende, Halloween – und am 20.11. feiern wir 18 Jahre Freiraum. Ein paar unserer Lieblinge von Instagram, tippen für Ton.',
      'b.follow': '8.952 Follower', 'b.press': 'Bekannt aus <b style="font-size:20px">heute.at</b>', 'b.ig': 'Folge uns auf Instagram ↗',
      'r.tap': 'Tippen für Ton', 'r.on': 'Ton an',
      'e.eyebrow': 'Feiern &amp; Events', 'e.guests': 'Gäste<br>bis zu', 'e.title': 'Euer Fest. <em>unser</em> Freiraum.',
      'e.lead': 'Ganzes Lokal oder eigener Bereich, Set-Menü, Buffet oder à la carte, mit DJ oder Lounge Music. Wir kümmern uns um alles.',
      'e.t1': 'Hochzeit', 'e.t2': 'Firmenfeier', 'e.t3': 'Geburtstag', 'e.t4': 'Weihnachtsfeier', 'e.t5': 'Kindergeburtstag →', 'e.lbl': 'Der Saal · Mariahilfer Straße 117',
      'f.title': 'Eure Feier <em>anfragen.</em>', 'f.lead': 'Unverbindlich – wir melden uns innerhalb von 24 Stunden.',
      'f.anlass': 'Anlass', 'f.other': 'Etwas anderes', 'f.datum': 'Wunschdatum', 'f.gaeste': 'Gäste', 'f.bereich': 'Bereich', 'f.b1': 'Eigener Bereich', 'f.b2': 'Ganzes Lokal', 'f.b3': 'Weiß ich noch nicht',
      'f.essen': 'Essen', 'f.e1': 'Set-Menü', 'f.e2': 'Buffet', 'f.e3': 'À la carte', 'f.e4': 'Fingerfood & Tapas', 'f.musik': 'Musik', 'f.m3': 'Keine',
      'f.name': 'Name', 'f.tel': 'Telefon', 'f.mail': 'E-Mail', 'f.msg': 'Nachricht', 'f.msgph': 'Erzählt uns kurz von eurer Feier …',
      'f.ds': 'Ich bin einverstanden, dass meine Angaben zur Bearbeitung der Anfrage gespeichert werden (<a href="datenschutz.html">Datenschutz</a>).', 'f.send': 'Anfrage senden',
      'j.eyebrow': '00:00 · 20.11.2026', 'j.title': 'Jahre <em>Freiraum.</em>', 'j.lead': 'Am 20. November werden wir volljährig. Feiert mit uns – wir zählen schon.',
      'j.past': 'Danke für 18 Jahre Freiraum – auf die nächsten!', 'j.d': 'Tage', 'j.h': 'Stunden', 'j.m': 'Minuten', 'j.s': 'Sekunden',
      'v.eyebrow': 'Besuch · <b>U3 Zieglergasse</b>', 'v.title': 'Komm <em>vorbei.</em>', 'v.route': 'Route ↗',
      'v.addr': '<b>Mariahilfer Straße 117</b>, 1060 Wien · U3 Zieglergasse / U6 Westbahnhof',
      'v.venue': 'Lokal', 'v.kitchen': 'Küche', 'v.pizza': 'Pizza', 'v.spiel': 'Spielraum', 'v.open': 'offen', 'v.closed': 'zu',
      'v.h.venue': 'Mo 8–23 · Di–Do 8–24 · Fr–Sa 8–2 · So 9–23', 'v.h.kitchen': 'täglich bis 21:45', 'v.h.pizza': 'ab 11 Uhr', 'v.h.spiel': 'täglich 9–18',
      'ft.visit': 'Besuch', 'ft.hours': 'Öffnungszeiten', 'ft.contact': 'Kontakt', 'ft.more': 'Mehr', 'ft.h': 'Mo 8–23 · Di–Do 8–24<br>Fr–Sa 8–2 · So 9–23<br>Küche bis 21:45',
      'ft.legal': 'Impressum & Datenschutz', 'ft.draft': 'Entwurf · nemistudio',
      'zen.alt': 'Reservierung über Zenchef. Lieber telefonisch? <a href="tel:+4315969600">+43 1 596 96 00</a>',
    },
    en: {
      'nav.morgen': 'Morning', 'nav.kueche': 'Kitchen', 'nav.spiel': 'Spielraum', 'nav.abend': 'Evening', 'nav.pizza': 'Pizza', 'nav.bar': 'Bar',
      'nav.jahre': '18 years', 'scroll': 'Scroll', 'cta.reserve': 'Book a table', 'cta.menu': 'Menu', 'cta.allmenu': 'Full menu',
      'h.eyebrow': 'Mariahilfer Straße 117 · <b>since 2008</b>', 'h.title': 'A day at <em>Freiraum.</em>',
      'h.lead': 'From the first Röstraum espresso in the morning to the last drink at 2 am – scroll through our day.',
      'h.jump': 'Jump to now',
      'c.eyebrow': 'Röstraum · <b>our own roastery</b>', 'c.title': 'Good morning, <em>Vienna.</em>',
      'c.lead': 'Every espresso starts in our own roastery – dark, velvety, Mon–Sat from 8 and Sun from 9 am.',
      'b2.eyebrow': 'Breakfast · <b>daily until 5 pm</b>', 'b2.title': 'Breakfast, <em>as long</em> as you like.',
      'b2.lead': 'Signature boxes, pancakes, bowls – and eggs the way you like them.',
      'c.b1': 'ham, Emmental, soft egg, Kornspitz', 'c.b2': 'mini rösti, fried egg, bacon, avocado', 'c.b3': 'falafel, hummus, ajvar, olives',
      'm.s1': 'Right on the Mahü', 'm.s2': 'guests at parties', 'm.s3': 'days a week', 'm.s4': 'dishes & drinks on the menu',
      'k.eyebrow': 'Lunch · kitchen until <b>9:45 pm</b>', 'k.title': 'One World <em>Kitchen.</em>',
      'k.lead': 'We bring the whole world to Vienna – from Wiener Schnitzel to falafel bowls, from sous-vide duck to tacos for sharing.',
      'k.d1': 'with grilled vegetables and salsa dip', 'k.d2': 'San Marzano tomatoes, crispy prawns', 'k.d3': 'cherry sauce, crispy polenta',
      'k.d4': 'stracciatella di bufala, rocket, bresaola', 'k.n5': 'Tapas for sharing', 'k.d5': 'tacos, patatas bravas, prawn tempura', 'k.p5': 'from 4.9',
      'k.d6': 'leaf salad, feta, walnuts', 'k.d7': 'molten chocolate, raspberry ice cream',
      's.eyebrow': 'Spielraum at Freiraum · <b>daily 9 am–6 pm</b>', 's.title': 'You relax. <em>the kids</em> play.',
      's.lead': 'Slide, ball pit and trampoline – right behind the glass wall. You eat in peace, the little ones stay in sight. RIO keeps watch.',
      's.cta': 'Discover the Spielraum', 's.party': 'Kids\' birthday',
      'fl.eyebrow': 'Golden hour · <b>Mariahilfer Straße</b>', 'fl.title': 'From now on it\'s <em>bar time.</em>', 'fl.lead': 'Lights on, music up – Freiraum switches into the evening.',
      'n1.eyebrow': 'Golden hour · <b>from 5 pm</b>', 'n1.title': 'Time for <em>drinks.</em>', 'n1.lead': 'Signature cocktails, homemade syrups and sprizz in every colour.',
      'd.p1': 'rosé secco, peach, cucumber, rosemary', 'd.p2': 'gin, Aperol, passion fruit, pineapple', 'd.p3': 'gin, strawberry bitter, fig', 'd.p4': 'alcohol-free · pineapple, passion fruit, ginger ale',
      'd.p5': 'prosecco, passion fruit, basil', 'd.p6': 'prosecco, pomegranate, mint',
      'n2.eyebrow': 'Every Thursday · <b>Ladies Night</b>', 'n2.title': 'Freiraum <em>Sprizz.</em>',
      'n2.lead': 'Rosé secco, peach, cucumber, rosemary – our signature sprizz. And on Thursdays the first glass of prosecco is on us.',
      'n3.eyebrow': 'Pizza station · <b>wood-fired oven</b>', 'n3.title': 'Real <em>fire.</em>', 'n3.lead': 'Natural sourdough, Caputo Manitoba flour, proofed for at least 48 hours.',
      'n3.p3': 'burrata, yellow cherry tomatoes, basil pesto',
      'p.eyebrow': 'No filter · <b>real clips from our pizza station</b>', 'p.title': 'From dough <em>to</em> fire.',
      'p.s1h': 'Dough', 'p.s1': 'Natural sourdough with Caputo Manitoba flour, shaped by hand every day.',
      'p.s2h': 'Toppings', 'p.s2': 'What goes on top goes on fresh: truffle, prosciutto, fior di latte.',
      'p.s3h': 'Oven', 'p.s3': 'Into the wood-fired oven – right in front of you, behind the glass.',
      'p.s4h': 'Fire', 'p.s4': 'At least 48 hours of proofing, then a few minutes of real fire. That is all it takes.',
      'p.s5h': 'Enjoy', 'p.s5': 'Burrata and basil to finish – and straight to your table.',
      'p.sunday': 'Pizza Sunday · every Sunday 2–10 pm · selected pizzas €9.90', 'p.m': 'Dough,Toppings,Oven,Fire,Enjoy',
      'b.eyebrow': 'Friday &amp; Saturday <b>until 2 am</b>', 'b.title': 'Bar &amp; <em>Beats.</em>',
      'b.lead': 'When it gets dark outside, it gets loud in here: DJ nights, Halloween – and on 20 Nov we celebrate 18 years of Freiraum. A few favourites from Instagram, tap for sound.',
      'b.follow': '8,952 followers', 'b.press': 'Featured on <b style="font-size:20px">heute.at</b>', 'b.ig': 'Follow us on Instagram ↗',
      'r.tap': 'Tap for sound', 'r.on': 'Sound on',
      'e.eyebrow': 'Parties &amp; events', 'e.guests': 'guests<br>up to', 'e.title': 'Your party. <em>our</em> Freiraum.',
      'e.lead': 'The whole venue or your own area, set menu, buffet or à la carte, with a DJ or lounge music. We take care of everything.',
      'e.t1': 'Wedding', 'e.t2': 'Company party', 'e.t3': 'Birthday', 'e.t4': 'Christmas party', 'e.t5': 'Kids\' birthday →', 'e.lbl': 'The hall · Mariahilfer Straße 117',
      'f.title': 'Plan your <em>party.</em>', 'f.lead': 'No obligation – we reply within 24 hours.',
      'f.anlass': 'Occasion', 'f.other': 'Something else', 'f.datum': 'Preferred date', 'f.gaeste': 'Guests', 'f.bereich': 'Area', 'f.b1': 'Own area', 'f.b2': 'Whole venue', 'f.b3': 'Not sure yet',
      'f.essen': 'Food', 'f.e1': 'Set menu', 'f.e2': 'Buffet', 'f.e3': 'À la carte', 'f.e4': 'Finger food & tapas', 'f.musik': 'Music', 'f.m3': 'None',
      'f.name': 'Name', 'f.tel': 'Phone', 'f.mail': 'Email', 'f.msg': 'Message', 'f.msgph': 'Tell us a little about your party …',
      'f.ds': 'I agree that my details are stored to process this request (<a href="datenschutz.html">privacy</a>).', 'f.send': 'Send request',
      'j.eyebrow': 'Midnight · 20 Nov 2026', 'j.title': 'Years of <em>Freiraum.</em>', 'j.lead': 'On 20 November we come of age. Celebrate with us – we are already counting.',
      'j.past': 'Thank you for 18 years of Freiraum – here is to the next!', 'j.d': 'days', 'j.h': 'hours', 'j.m': 'minutes', 'j.s': 'seconds',
      'v.eyebrow': 'Visit · <b>U3 Zieglergasse</b>', 'v.title': 'Come <em>by.</em>', 'v.route': 'Directions ↗',
      'v.addr': '<b>Mariahilfer Straße 117</b>, 1060 Vienna · U3 Zieglergasse / U6 Westbahnhof',
      'v.venue': 'Venue', 'v.kitchen': 'Kitchen', 'v.pizza': 'Pizza', 'v.spiel': 'Spielraum', 'v.open': 'open', 'v.closed': 'closed',
      'v.h.venue': 'Mon 8–23 · Tue–Thu 8–24 · Fri–Sat 8–2 · Sun 9–23', 'v.h.kitchen': 'daily until 21:45', 'v.h.pizza': 'from 11 am', 'v.h.spiel': 'daily 9–18',
      'ft.visit': 'Visit', 'ft.hours': 'Opening hours', 'ft.contact': 'Contact', 'ft.more': 'More', 'ft.h': 'Mon 8–23 · Tue–Thu 8–24<br>Fri–Sat 8–2 · Sun 9–23<br>Kitchen until 21:45',
      'ft.legal': 'Imprint & privacy', 'ft.draft': 'Draft · nemistudio',
      'zen.alt': 'Booking via Zenchef. Prefer to call? <a href="tel:+4315969600">+43 1 596 96 00</a>',
    },
  });

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
  function drawFit(g, im, mode) {
    if (!im) return;
    const cw = g.canvas.width, ch = g.canvas.height, ir = im.naturalWidth / im.naturalHeight, cr = cw / ch;
    let w, h;
    if (mode === 'contain' ? ir < cr : ir > cr) { h = ch; w = ch * ir; } else { w = cw; h = cw / ir; }
    g.drawImage(im, (cw - w) / 2, (ch - h) / 2, w, h);
  }
  // Ein Canvas folgt einer Bildfolge; der Bildindex gleitet weich zum Ziel
  class Player {
    constructor(cv, seq, opts = {}) { this.cv = cv; this.seq = seq; this.cur = 0; this.target = 0; this.drawn = ''; this.mode = opts.mode || 'cover'; this.shadow = opts.shadow || null; }
    tick(force) {
      this.cur += (this.target - this.cur) * (FR.reduced ? 1 : 0.22);
      if (Math.abs(this.target - this.cur) < 0.02) this.cur = this.target;
      const im = this.seq.nearest(this.cur);
      const key = im ? im.src : '';
      if (!force && key === this.drawn) return;
      const g = fitCanvas(this.cv); g.clearRect(0, 0, this.cv.width, this.cv.height);
      if (this.shadow) { g.shadowColor = this.shadow; g.shadowBlur = 50 * DPR; g.shadowOffsetY = 26 * DPR; }
      drawFit(g, im, this.mode); g.shadowColor = 'transparent'; this.drawn = key;
    }
  }

  /* ---------------- Geometrie ---------------- */
  const sections = $$('main > section, footer.foot');
  const chapters = sections.filter((s) => s.dataset.ch);
  let geo = [];
  function measure() {
    W = innerWidth; H = innerHeight; MOBILE = W <= 860;
    sizeGallery();
    geo = sections.map((s) => { const r = s.getBoundingClientRect(); return { el: s, top: r.top + scrollY, h: r.height }; });
  }
  const geoOf = (el) => geo.find((x) => x.el === el);
  const progressOf = (el) => { const g = geoOf(el); if (!g) return 0; return clamp((scrollY - g.top) / Math.max(1, g.h - H)); };

  /* ---------------- Tageszeit: Farben pro Kapitel ---------------- */
  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const FX = ['motes', 'embers', 'bubbles', 'sparkle', 'gold', 'bokeh', 'neon'];
  const T = (bg1, bg2, glow, o = {}) => ({ bg1: hex(bg1), bg2: hex(bg2), glow: hex(glow), accent: o.accent ? hex(o.accent) : null,
    moon: o.moon || 0, neon: o.neon || 0, dsc: o.dsc ?? 1, dop: o.dop ?? 1, dy: o.dy || 0, fx: Object.assign(Object.fromEntries(FX.map((k) => [k, 0])), o.fx || {}) });
  // Unterzustände nach Fortschritt im Kapitel: [ab, Zustand]
  const THEME = {
    dan: [[0, T('#f8f1e7', '#f3dcc5', '#ffd08a', { dop: .95, fx: { motes: .7 } })],
          [.14, T('#f7efe4', '#f2d6bd', '#ffc977', { dop: 1, fx: { motes: .5 } })],
          [.58, T('#f8f3ea', '#f5e4c9', '#ffe2a0', { dop: 1, dsc: 1.06, fx: { motes: .5 } })]],
    manifest: [[0, T('#f5f3ec', '#e9efe5', '#fff0c8', { dop: 0, dsc: .8 })]],
    kueche: [[0, T('#f2f6f1', '#dcebe1', '#fff1c9', { dop: 0, dsc: .8, accent: '#3d7a5c' })]],
    spielraum: [[0, T('#eaf4fb', '#bcdcf2', '#fff6d6', { accent: '#2f74b0', fx: { sparkle: 1 } })]],
    flip: [[0, T('#f6d9b2', '#f4b07a', '#ffb468', { accent: '#b4532a', dsc: 1 })],
           [.42, T('#ec9a6c', '#8a4560', '#ff7a3d', { dsc: 1.05, dy: .22, fx: { bokeh: .3 } })],
           [.72, T('#3b2347', '#1d1430', '#ff6a3d', { dop: .35, dy: .48, fx: { bokeh: 1 } })],
           [1, T('#120d1f', '#26172e', '#ff9a52', { dop: 0, dy: .6, moon: 1, fx: { bokeh: .8 } })]],
    nacht: [[0, T('#110b19', '#3a1c25', '#ff9a52', { moon: 1, fx: { bubbles: .7, bokeh: .2 } })],
            [.44, T('#0e0b1e', '#2b1d4c', '#caa8ff', { moon: 1, neon: .2, fx: { neon: .6 } })],
            [.66, T('#130a06', '#3a160a', '#ff7a2f', { moon: 1, fx: { embers: 1 } })]],
    pizza: [[0, T('#120a06', '#2a1208', '#ffb36b', { moon: 1, dsc: 1.13, fx: { embers: .4 } })]],
    bar: [[0, T('#0b0a1c', '#1d1840', '#8b5cf6', { neon: 1, dsc: .8, dop: .9, fx: { neon: 1 } })]],
    feiern: [[0, T('#0b0d18', '#1f2741', '#efd29a', { moon: 1, dsc: .6, dop: 0 })]],
    anfrage: [[0, T('#0b0d18', '#1f2741', '#efd29a', { moon: 1, dsc: .6, dop: 0 })]],
    jahre: [[0, T('#0c0b14', '#1e1726', '#d9b46a', { moon: 1, dsc: .7, dop: .55, fx: { gold: 1 } })]],
    besuch: [[0, T('#07090f', '#121a30', '#f3e2c0', { moon: 1, dsc: .6, dop: 0 })]],
    foot: [[0, T('#07090f', '#121a30', '#f3e2c0', { moon: 1, dsc: .5, dop: 0 })]],
  };
  function mix(a, b, t) {
    const L = (x, y) => x.map((v, i) => lerp(v, y[i], t));
    const o = { bg1: L(a.bg1, b.bg1), bg2: L(a.bg2, b.bg2), glow: L(a.glow, b.glow), moon: lerp(a.moon, b.moon, t), neon: lerp(a.neon, b.neon, t),
      dsc: lerp(a.dsc, b.dsc, t), dop: lerp(a.dop, b.dop, t), dy: lerp(a.dy, b.dy, t), fx: {} };
    o.accent = a.accent || b.accent ? L(a.accent || a.glow, b.accent || b.glow) : null;
    if (!a.accent && b.accent) o.accent = L(a.glow, b.accent); if (a.accent && !b.accent) o.accent = L(a.accent, b.glow);
    if (!a.accent && !b.accent) o.accent = null;
    FX.forEach((k) => (o.fx[k] = lerp(a.fx[k], b.fx[k], t)));
    return o;
  }
  function themeAt(el, p) {
    const key = el.id || (el.classList.contains('foot') ? 'foot' : '');
    const list = THEME[key] || THEME.foot;
    if (key === 'pizza') return pizzaTheme(list[0][1], p);
    let i = 0; while (i < list.length - 1 && p >= list[i + 1][0]) i++;
    const cur = list[i][1], nxt = list[i + 1];
    if (!nxt) return cur;
    if (key === 'flip') return mix(cur, nxt[1], smooth(clamp((p - list[i][0]) / (nxt[0] - list[i][0]))));
    const span = 0.06; // weich überblenden kurz vor dem nächsten Unterzustand
    return mix(cur, nxt[1], smooth(clamp((p - (nxt[0] - span)) / span)));
  }
  const lum = (c) => (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255;
  const NAVY = hex('#1f2741'), CREAM = hex('#efe6d6'), DAY_ACC = hex('#b0652f');
  const rgb = (c) => `rgb(${c.map((v) => Math.round(v)).join(',')})`;
  let sky = null, isNight = false;
  function blendSky() {
    const yc = scrollY + H * 0.5, Z = H * 0.45;
    let i = geo.findIndex((g) => yc >= g.top && yc < g.top + g.h);
    if (i < 0) i = yc < (geo[0] ? geo[0].top : 0) ? 0 : geo.length - 1;
    const g = geo[i]; const p = progressOf(g.el);
    let st = themeAt(g.el, p);
    const dEnd = g.top + g.h - yc, dStart = yc - g.top;
    if (dEnd < Z && geo[i + 1]) st = mix(st, themeAt(geo[i + 1].el, 0), 0.5 * (1 - dEnd / Z));
    else if (dStart < Z && geo[i - 1]) st = mix(st, themeAt(geo[i - 1].el, 1), 0.5 * (1 - dStart / Z));
    sky = st;
    const L = lum(st.bg1.map((v, k) => (v + st.bg2[k]) / 2));
    const t = smooth(clamp((L - 0.32) / 0.22));           // 0 = dunkel, 1 = hell
    isNight = t < 0.5;
    const fg = CREAM.map((v, k) => lerp(v, NAVY[k], t));
    const acc = st.accent || DAY_ACC.map((v, k) => lerp(st.glow[k], v, t));
    const rs = document.documentElement.style;
    rs.setProperty('--bg1', rgb(st.bg1)); rs.setProperty('--bg2', rgb(st.bg2)); rs.setProperty('--fg', rgb(fg));
    rs.setProperty('--glow', rgb(st.glow)); rs.setProperty('--accent', rgb(st.accent ? st.accent : acc));
    rs.setProperty('--moon', st.moon.toFixed(3)); rs.setProperty('--neon', st.neon.toFixed(3));
    rs.setProperty('--dsc', st.dsc.toFixed(3)); rs.setProperty('--dop', st.dop.toFixed(3)); rs.setProperty('--dy', (st.dy * H).toFixed(1) + 'px');
    if (themeMeta) themeMeta.content = rgb(st.bg1);
    return i;
  }
  const themeMeta = $('meta[name="theme-color"]');

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
        float m=smoothstep(1.25,.15,d);
        gl_FragColor=vec4(c*(.7+.6*f),wisp*m*k*.55);}`;
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
      draw(t, col, strength, night) {
        if (t - last < 33) return; last = t;
        const sc = MOBILE ? 0.22 : 0.3, w = Math.round(W * sc), h = Math.round(H * sc);
        if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; gl.viewport(0, 0, w, h); }
        cv.style.mixBlendMode = night ? 'screen' : 'normal';
        gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        if (strength < 0.01) return;
        gl.uniform2f(U.r, w, h); gl.uniform1f(U.t, t / 1000); gl.uniform3f(U.c, col[0] / 255, col[1] / 255, col[2] / 255);
        gl.uniform2f(U.a, MOBILE ? 0.5 : 0.63, 1 - (MOBILE ? 0.68 : 0.53)); gl.uniform1f(U.k, strength);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      },
    };
  })();

  /* ---------------- Partikel ---------------- */
  const fx = (function () {
    const cv = $('#fx'), g = cv.getContext('2d'); const P = [];
    const emitAt = { x: 0, y: 0, on: false };
    function resize() { cv.width = W * DPR; cv.height = H * DPR; }
    function anchor() { const s = Math.min(MOBILE ? W * 0.84 : H * 0.70, MOBILE ? H * 0.42 : W * 0.42); return { x: (MOBILE ? 0.5 : 0.63) * W, y: (MOBILE ? 0.68 : 0.53) * H, s }; }
    const R = Math.random;
    function spawn(kind) {
      const a = anchor(), r = a.s / 2;
      if (kind === 'motes') P.push({ k: kind, x: R() * W, y: R() * H, vx: (R() - 0.5) * 0.12, vy: -0.04 - R() * 0.1, r: 0.8 + R() * 2, life: 1, dl: 0.0016 + R() * 0.002 });
      if (kind === 'embers') { const ang = R() * Math.PI * 2; P.push({ k: kind, x: a.x + Math.cos(ang) * r * 0.9, y: a.y + Math.sin(ang) * r * 0.9 + r * 0.2, vx: (R() - 0.5) * 0.6, vy: -0.6 - R() * 1.4, r: 0.8 + R() * 1.8, life: 1, dl: 0.006 + R() * 0.008 }); }
      if (kind === 'bubbles') P.push({ k: kind, x: a.x + (R() - 0.5) * r * 1.2, y: a.y + r * (0.3 + R() * 0.6), vx: 0, vy: -0.35 - R() * 0.6, r: 1 + R() * 3.2, life: 1, dl: 0.004 + R() * 0.004, ph: R() * 6 });
      if (kind === 'gold') P.push({ k: kind, x: R() * W, y: -10, vx: (R() - 0.5) * 0.4, vy: 0.4 + R() * 0.8, r: 1 + R() * 2.4, life: 1, dl: 0.002 + R() * 0.002, rot: R() * 6, vr: (R() - 0.5) * 0.1 });
      if (kind === 'bokeh') P.push({ k: kind, x: R() * W, y: H * (0.45 + R() * 0.6), vx: (R() - 0.5) * 0.08, vy: -0.08 - R() * 0.15, r: 10 + R() * 34, life: 1, dl: 0.0014 + R() * 0.0018, hue: R() });
      if (kind === 'neon') P.push({ k: kind, x: R() * W, y: R() * H, vx: (R() - 0.5) * 0.2, vy: (R() - 0.5) * 0.2, r: 0.8 + R() * 1.6, life: 1, dl: 0.006 + R() * 0.006, hue: R() });
      if (kind === 'sparkle' && emitAt.on) P.push({ k: kind, x: emitAt.x + (R() - 0.5) * 30, y: emitAt.y + (R() - 0.5) * 30, vx: (R() - 0.5) * 0.5, vy: 0.2 + R() * 0.6, r: 0.8 + R() * 2.2, life: 1, dl: 0.012 + R() * 0.01 });
    }
    const RATE = { motes: 0.35, embers: 1.6, bubbles: 0.9, gold: 0.7, sparkle: 2.4, bokeh: 0.25, neon: 0.6 };
    function step(t, w, night) {
      if (FR.reduced) return;
      for (const k in RATE) { let c = (w[k] || 0) * RATE[k] * (MOBILE ? 0.6 : 1); while (c > 0) { if (R() < Math.min(1, c)) spawn(k); c -= 1; } }
      g.setTransform(DPR, 0, 0, DPR, 0, 0); g.clearRect(0, 0, W, H);
      for (let i = P.length - 1; i >= 0; i--) {
        const p = P[i]; p.life -= p.dl; p.x += p.vx; p.y += p.vy;
        if (p.k === 'embers') p.vx += (R() - 0.5) * 0.08;
        if (p.k === 'bubbles') p.x += Math.sin(t / 400 + p.ph) * 0.25;
        if (p.life <= 0 || p.y < -60 || p.y > H + 60) { P.splice(i, 1); continue; }
        const fade = Math.min(1, p.life * 3) * Math.min(1, (1 - p.life) * 8);
        if (p.k === 'motes') { g.fillStyle = night ? `rgba(255,240,215,${0.35 * fade})` : `rgba(196,140,70,${0.32 * fade})`; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); }
        else if (p.k === 'embers') { g.fillStyle = `rgba(255,${140 + R() * 60 | 0},60,${0.9 * fade})`; g.shadowColor = '#ff7a2f'; g.shadowBlur = 8; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); g.shadowBlur = 0; }
        else if (p.k === 'bubbles') { g.strokeStyle = `rgba(255,235,210,${0.55 * fade})`; g.lineWidth = 0.8; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.stroke(); }
        else if (p.k === 'gold') { p.rot += p.vr; g.fillStyle = `rgba(240,205,130,${0.8 * fade})`; g.save(); g.translate(p.x, p.y); g.rotate(p.rot); g.fillRect(-p.r, -p.r * 0.4, p.r * 2, p.r * 0.8); g.restore(); }
        else if (p.k === 'bokeh') { const c = p.hue < 0.6 ? '255,190,110' : '255,140,90'; const gr = g.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r); gr.addColorStop(0, `rgba(${c},${0.28 * fade})`); gr.addColorStop(0.7, `rgba(${c},${0.12 * fade})`); gr.addColorStop(1, `rgba(${c},0)`); g.fillStyle = gr; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); }
        else if (p.k === 'neon') { const c = p.hue < 0.5 ? '160,120,255' : '90,150,255'; g.fillStyle = `rgba(${c},${0.8 * fade})`; g.shadowColor = `rgb(${c})`; g.shadowBlur = 10; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); g.shadowBlur = 0; }
        else if (p.k === 'sparkle') { g.fillStyle = night ? `rgba(255,255,255,${fade})` : `rgba(255,214,120,${fade})`; g.shadowColor = night ? '#bfe4ff' : '#ffcf6a'; g.shadowBlur = 10; g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); g.shadowBlur = 0; }
      }
    }
    return { resize, step, emitAt };
  })();

  /* ---------------- Durchgehende Animationen: Morgen und Abend ---------------- */
  function seqSection(el, cv, base, segs, shadow) {
    const count = +el.dataset.count, steps = el.dataset.steps.split(',').map((s) => s.split('-').map(Number));
    const seq = new Seq(base, count), player = new Player(cv, seq, { mode: 'contain', shadow });
    // segs: [[p0, p1, Schritt], …] – Bildfolge eines Klips läuft zwischen p0 und p1, dazwischen steht sie
    const target = (p) => {
      let f = steps[segs[0][2]][0];
      for (const [p0, p1, s] of segs) { const [a, b] = steps[s]; if (p >= p0) f = a + clamp((p - p0) / (p1 - p0)) * (b - a); }
      return f;
    };
    return { el, seq, player, target };
  }
  function layers(sec, p) {
    const ls = $$('.layer', sec); let cur = 0;
    ls.forEach((l, i) => { if (p >= +l.dataset.at) cur = i; });
    ls.forEach((l, i) => { l.classList.toggle('on', i === cur); l.classList.toggle('gone', i < cur); });
    return cur;
  }
  let DAN, NACHT, started = false;
  function renderSeqSection(S, t) {
    if (!S) return;
    const g = geoOf(S.el); if (!g) return;
    if (scrollY + H < g.top - H || scrollY > g.top + g.h + H) return;
    const p = progressOf(S.el);
    if (started) layers(S.el, p);
    S.player.target = S.target(p); S.player.tick();
    const st = $('.stage', S.el); if (st && !FR.reduced) st.style.transform = `translateY(${Math.sin(t / 1600) * 5}px)`;
  }

  /* ---------------- 16:59 → 17:00 ---------------- */
  const flipSec = $('#flip'), flipDigits = $$('#flipclock .d');
  let flipped = null;
  function setFlip(on) {
    if (flipped === on) return; flipped = on;
    const digits = on ? ['1', '7', '0', '0'] : ['1', '6', '5', '9'];
    flipDigits.forEach((d, i) => {
      const b = $('b', d); if (b.textContent === digits[i]) return;
      d.classList.remove('flip'); void d.offsetWidth; d.classList.add('flip');
      setTimeout(() => (b.textContent = digits[i]), 300);
    });
    $('#flipTitle').classList.toggle('in', on); $('#flipLead').classList.toggle('in', on);
  }
  function renderFlip() {
    const g = geoOf(flipSec); if (!g || scrollY + H < g.top || scrollY > g.top + g.h) return;
    setFlip(progressOf(flipSec) > 0.46);
  }

  /* ---------------- Manifest ---------------- */
  const marqs = $$('.marq'), manifest = $('#manifest');
  function renderManifest() {
    const g = geoOf(manifest); if (!g) return;
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
    const g = geoOf(hz); if (!g || scrollY + H < g.top || scrollY > g.top + g.h) return;
    const p = clamp((progressOf(hz) - 0.06) / 0.9), dist = +hz.dataset.dist || 0;
    track.style.transform = `translate3d(${-p * dist}px,0,0)`;
    let best = 0, bd = 1e9;
    cards.forEach((c, i) => {
      const r = c.getBoundingClientRect(), cx = r.left + r.width / 2, rel = (cx - W / 2) / W;
      c.querySelector('img').style.transform = `translate3d(${rel * -40}px,0,0) scale(1.06)`;
      const d = Math.abs(cx - W / 2); if (d < bd) { bd = d; best = i; }
    });
    $('#kCount').textContent = String(best + 1).padStart(2, '0') + ' / ' + String(cards.length).padStart(2, '0');
  }

  /* ---------------- Spielraum ---------------- */
  const spiel = $('#spielraum'), rio = $('#rio');
  function bez(p0, p1, p2, p3, t) { const u = 1 - t; return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3; }
  function renderSpiel() {
    const g = geoOf(spiel); if (!g) return;
    const vis = scrollY + H > g.top && scrollY < g.top + g.h;
    const p = progressOf(spiel);
    const a = { x: (MOBILE ? 0.5 : 0.63) * W, y: (MOBILE ? 0.68 : 0.53) * H, s: Math.min(MOBILE ? W * 0.84 : H * 0.70, MOBILE ? H * 0.42 : W * 0.42) };
    const t = clamp((p - 0.02) / 0.96);
    const X = MOBILE ? [-0.3 * a.s, a.x - a.s * 0.5, a.x + a.s * 0.3, W + a.s * 0.3] : [a.x - a.s * 0.62, a.x - a.s * 0.62, a.x + a.s * 0.1, W + a.s * 0.25];
    const Y = MOBILE ? [a.y + a.s * 0.3, a.y - a.s * 0.75, a.y + a.s * 0.45, a.y - a.s * 0.6] : [H + a.s * 0.25, a.y - a.s * 0.25, a.y - a.s * 0.95, a.y - a.s * 0.2];
    const x = bez(...X, t), y = bez(...Y, t), x2 = bez(...X, Math.min(1, t + 0.01)), y2 = bez(...Y, Math.min(1, t + 0.01));
    const ang = Math.atan2(y2 - y, x2 - x) * 180 / Math.PI, rw = a.s * 0.42;
    rio.style.transform = `translate3d(${x - rw / 2}px,${y - rw * 0.65}px,0) rotate(${clamp(ang * 0.35, -25, 25)}deg)`;
    fx.emitAt.on = vis && t > 0 && t < 1; fx.emitAt.x = x; fx.emitAt.y = y + rw * 0.1;
    if (!vis) return;
    $$('.pola', spiel).forEach((el, i) => { el.style.translate = `0 ${(p - 0.5) * (i ? -60 : 60)}px`; });
    $$('#clouds i').forEach((el, i) => { el.style.transform = `translate3d(${(p - 0.3) * (i % 2 ? -1 : 1) * (40 + i * 25)}%,0,0)`; });
  }

  /* ---------------- Vom Teig zum Feuer (echte Clips) ---------------- */
  const pizzaSec = $('#pizza');
  const PIZZA = { count: 206, steps: [{ from: 0, to: 25 }, { from: 26, to: 46 }, { from: 47, to: 92 }, { from: 93, to: 162 }, { from: 163, to: 205 }] };
  const STEP_GLOW = ['#f6e2bf', '#f8d2a0', '#ff9b52', '#ff7a2f', '#ffc47f'];
  let pizzaSeq, pizzaPlayer, pizzaStep = -1;
  function pizzaLocal(p) { const n = PIZZA.steps.length, x = clamp(p * 1.04 - 0.02) * n; const i = Math.min(n - 1, Math.floor(x)); return { i, lp: x - i }; }
  function pizzaTheme(base, p) {
    const { i, lp } = pizzaLocal(p), s = Object.assign({}, base, { fx: Object.assign({}, base.fx) });
    const a = hex(STEP_GLOW[i]), b = hex(STEP_GLOW[Math.min(4, i + 1)]), t = smooth(clamp((lp - 0.7) / 0.3));
    s.glow = a.map((v, k) => lerp(v, b[k], t));
    s.fx.embers = i === 2 || i === 3 ? 1 : i === 4 ? 0.3 : 0.1;
    return s;
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
    const g = geoOf(pizzaSec); if (!g || scrollY + H < g.top - H || scrollY > g.top + g.h + H) return;
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

  /* ---------------- Feiern, Besuch, 18 Jahre ---------------- */
  const feiern = $('#feiern'), besuch = $('#besuch');
  let salaPlayer, fasadaPlayer;
  function renderFeiern() {
    const g = geoOf(feiern); if (!g || scrollY + H < g.top || scrollY > g.top + g.h) return;
    const p = progressOf(feiern);
    if (salaPlayer) { salaPlayer.target = clamp(p * 1.08) * 79; salaPlayer.tick(); }
    $('#n350').textContent = Math.round(ease(clamp(p / 0.55)) * 350);
  }
  function renderBesuch() {
    const g = geoOf(besuch); if (!g || scrollY + H < g.top || scrollY > g.top + g.h) return;
    if (fasadaPlayer) { fasadaPlayer.target = clamp(progressOf(besuch) * 1.1) * 79; fasadaPlayer.tick(); }
  }
  function buildHours() {
    const v = FR.vienna();
    const rows = [['venue', 'v.venue', 'v.h.venue'], ['kitchen', 'v.kitchen', 'v.h.kitchen'], ['pizza', 'v.pizza', 'v.h.pizza'], ['spielraum', 'v.spiel', 'v.h.spiel']];
    $('#hours').innerHTML = rows.map(([k, l, h]) => { const o = FR.isOpen(k, v); return `<div><span>${FR.t(l)}</span><span>${FR.t(h)}</span><em class="${o ? '' : 'c'}">${FR.t(o ? 'v.open' : 'v.closed')}</em></div>`; }).join('');
  }
  const jahre = $('#jahre'), n18 = $('#n18');
  const BDAY = Date.parse('2026-11-20T00:00:00+01:00');
  function countdown() {
    const ms = BDAY - Date.now(), cells = $$('#cd b');
    if (ms <= 0) { $('#cd').style.display = 'none'; $('#jLead').textContent = FR.t('j.past'); return; }
    const s = Math.floor(ms / 1000);
    [Math.floor(s / 86400), Math.floor(s / 3600) % 24, Math.floor(s / 60) % 60, s % 60].forEach((v, i) => (cells[i].textContent = i ? String(v).padStart(2, '0') : v));
  }
  function renderJahre() {
    const g = geoOf(jahre); if (!g) return;
    n18.style.backgroundPosition = `0 ${(clamp((scrollY + H * 0.85 - g.top) / (g.h * 0.75)) * 100).toFixed(1)}%`;
  }

  /* ---------------- Uhr, Navigation, Index ---------------- */
  const nav = $('#nav'), bar = $('#progress'), nextBtn = $('#next'), clockEl = $('#clock span');
  const hhmm = (x) => { x = ((x % 24) + 24) % 24; const h = Math.floor(x), m = Math.floor((x - h) * 60); return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0'); };
  function dayTime() {
    const yc = scrollY + H * 0.5;
    let i = geo.findIndex((g) => yc >= g.top && yc < g.top + g.h); if (i < 0) i = yc < geo[0].top ? 0 : geo.length - 1;
    const g = geo[i], d = g.el.dataset, t0 = +(d.t0 || 0), t1 = +(d.t1 || t0);
    if (g.el === flipSec) return progressOf(flipSec) > 0.46 ? 17 : 16 + 59 / 60;
    return lerp(t0, t1, clamp((yc - g.top) / g.h));
  }
  function buildIndex() {
    $('#index').innerHTML = chapters.map((c) => `<li><a href="#${c.id}" data-id="${c.id}"><span>${FR.t(c.dataset.label)}</span>${c.dataset.ch}<i></i></a></li>`).join('');
  }
  function go(el, extra = 0) {
    const g = geoOf(el); if (!g) return;
    scrollTo({ top: g.top + 2 + extra, behavior: FR.reduced ? 'auto' : 'smooth' });
  }
  let curCh = -1, lastClock = '';
  function renderNav() {
    nav.classList.toggle('solid', scrollY > 40);
    const max = document.documentElement.scrollHeight - H, pr = clamp(scrollY / Math.max(1, max));
    bar.style.transform = `scaleX(${pr})`;
    nextBtn.style.setProperty('--p', pr.toFixed(3));
    const c = hhmm(dayTime()); if (c !== lastClock) { clockEl.textContent = c; lastClock = c; }
    const yc = scrollY + H * 0.5; let ci = 0;
    chapters.forEach((ch, i) => { const g = geoOf(ch); if (g && yc >= g.top) ci = i; });
    if (ci !== curCh) {
      curCh = ci; const id = chapters[ci].id;
      $$('#index a').forEach((a) => a.classList.toggle('on', a.dataset.id === id));
      $$('.nav ul a').forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + id));
    }
    nextBtn.classList.toggle('up', pr > 0.985);
    const meta = $('#dan .meta'); if (meta) meta.style.opacity = scrollY > H * 0.6 ? 0 : 1;
  }
  nextBtn.addEventListener('click', () => {
    if (nextBtn.classList.contains('up')) { scrollTo({ top: 0, behavior: 'smooth' }); return; }
    const yc = scrollY + 4; const nx = chapters.find((c) => { const g = geoOf(c); return g && g.top > yc + 2; });
    if (nx) go(nx); else scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]'); if (!a) return;
    const el = document.getElementById(a.getAttribute('href').slice(1)); if (!el) return;
    e.preventDefault(); closeMenu(); go(el);
  });
  // „Spring ins Jetzt“: zum Kapitel, das zur aktuellen Wiener Uhrzeit passt
  function jetztTarget() {
    const v = FR.vienna(), h = v.hf;
    if (h >= 2 && h < 8) return [besuch, 0];
    if (h < 11) return [$('#dan'), 0.3];
    if (h < 14) return [hz, 0];
    if (h < 17) return [spiel, 0];
    if (h < 19) return [$('#nacht'), 0.1];
    if (h < 22) return [pizzaSec, 0];
    return [$('#bar'), 0];
  }
  $('#jetztBtn').addEventListener('click', () => {
    const [el, f] = jetztTarget(), g = geoOf(el); if (!g) return;
    scrollTo({ top: g.top + Math.max(0, g.h - H) * f + 2, behavior: 'smooth' });
  });
  function updateJetztT() { const v = FR.vienna(); $('#jetztT').textContent = String(v.h).padStart(2, '0') + ':' + String(v.m).padStart(2, '0'); }
  const menu = $('#menu');
  function closeMenu() { menu.classList.remove('open'); }
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

  function reveal() {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in'); io.unobserve(e.target);
      const c = e.target.querySelector('[data-count]'); if (c) countUp(c);
    }), { rootMargin: '0px 0px -12% 0px' });
    $$('.rv:not(.in)').forEach((el) => io.observe(el));
  }

  /* ---------------- Loader ---------------- */
  async function loader(firstJobs) {
    const cv = $('#loaderLogo'), g = cv.getContext('2d'), pct = $('#pct');
    let sk = null; try { sk = await FR.json('shared/svg/logo-skeleton.json'); } catch (e) { sk = null; }
    const pts = [];
    if (sk) {
      const sc = cv.width / sk.viewBox[2];
      const paths = sk.paths.slice().sort((a, b) => Math.min(...a.map((p) => p[0])) - Math.min(...b.map((p) => p[0])));
      paths.forEach((pl) => pl.forEach((p, i) => pts.push({ x: p[0] * sc, y: p[1] * sc, r: Math.max(1.5, p[2] * sc * 0.55), first: i === 0 })));
      if (sk.dot) pts.push({ x: sk.dot[0] * sc, y: sk.dot[1] * sc, r: sk.dot[2] * sc * 0.7, first: true, dot: true });
    }
    const jobs = [document.fonts ? document.fonts.ready : Promise.resolve(), ...firstJobs];
    let done = 0; jobs.forEach((j) => j.then(() => done++));
    const t0 = performance.now(); let shown = 0, drawn = 0;
    g.strokeStyle = g.fillStyle = '#1f2741'; g.lineCap = g.lineJoin = 'round';
    await new Promise((resolve) => {
      (function frame(t) {
        const real = done / jobs.length, minT = clamp((t - t0) / 1700), maxT = clamp((t - t0) / 6000);
        const target = Math.max(maxT, Math.min(real, minT));
        shown += (target - shown) * 0.12; if (target >= 1 && shown > 0.995) shown = 1;
        pct.textContent = Math.round(shown * 100) + ' %';
        const upto = Math.floor(shown * pts.length);
        for (; drawn < upto; drawn++) {
          const p = pts[drawn], q = pts[drawn - 1];
          if (p.dot) { g.beginPath(); g.arc(p.x, p.y, p.r, 0, 7); g.fill(); continue; }
          if (q && !p.first && !q.dot) { g.lineWidth = p.r + q.r; g.beginPath(); g.moveTo(q.x, q.y); g.lineTo(p.x, p.y); g.stroke(); }
        }
        if (shown >= 1) return resolve();
        requestAnimationFrame(frame);
      })(t0);
    });
    await new Promise((r) => setTimeout(r, 250));
    $('#loader').classList.add('done');
    setTimeout(() => $('#loader').remove(), 1400);
  }

  /* ---------------- Start ---------------- */
  FR.applyLang(); splitAll(); buildDial(); buildHours(); buildIndex();
  REELS.forEach((r) => reelCard(r, $('#reels')));
  reelCard({ v: 'reel-eventlocation', likes: 155, comments: 10, cap: 'Die perfekte Eventlocation in Wien? Hast du gerade gefunden!' }, $('#eventReel'));
  FR.bindForm($('#eventForm'), 'event');
  FR.updateJetzt(); setInterval(FR.updateJetzt, 4000);
  updateJetztT(); setInterval(updateJetztT, 15000);
  countdown(); setInterval(countdown, 1000);
  $$('#dan .layer').forEach((l) => l.classList.remove('on'));

  DAN = seqSection($('#dan'), $('#danCv'), 'assets/seq/dan', [[0.12, 0.53, 0], [0.6, 0.94, 1]], 'rgba(90,60,30,.22)');
  NACHT = seqSection($('#nacht'), $('#nachtCv'), 'assets/seq/noc', [[0.05, 0.40, 0], [0.48, 0.9, 1]], null);
  pizzaSeq = new Seq('assets/seq/pizza', PIZZA.count);
  pizzaPlayer = new Player($('#pizzaCv'), pizzaSeq);
  const salaSeq = new Seq('shared/seq/sala', 80), fasadaSeq = new Seq('shared/seq/fasada', 80);
  salaPlayer = new Player($('#salaCv'), salaSeq); fasadaPlayer = new Player($('#fasadaCv'), fasadaSeq);
  const first = []; for (let i = 0; i < 30; i++) first.push(DAN.seq.load(i));
  loader(first).then(() => {
    started = true;
    loadSeq(DAN.seq);
    setTimeout(() => { loadSeq(NACHT.seq); loadSeq(pizzaSeq); }, 1500);
    setTimeout(() => { loadSeq(salaSeq); loadSeq(fasadaSeq); }, 4000);
  });

  measure(); fx.resize(); reveal();
  addEventListener('resize', () => { measure(); fx.resize(); [DAN.player, NACHT.player, pizzaPlayer, salaPlayer, fasadaPlayer].forEach((pl) => pl.tick(true)); buildDial(); });
  addEventListener('load', measure);
  if (document.fonts) document.fonts.ready.then(measure);

  (function loop(t) {
    blendSky();
    renderNav();
    renderSeqSection(DAN, t); renderSeqSection(NACHT, t);
    renderManifest(); renderGallery(); renderSpiel(); renderFlip(); renderPizza(); renderFeiern(); renderBesuch(); renderJahre();
    if (sky) {
      const k = isNight ? lerp(0.35, 1, sky.dop) : 0.18 * sky.dop;
      smoke && smoke.draw(t, isNight ? sky.glow : [190, 140, 90], k, isNight);
      fx.step(t, sky.fx, isNight);
    }
    requestAnimationFrame(loop);
  })(0);
})();
