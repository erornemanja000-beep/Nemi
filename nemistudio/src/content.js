// All copy, German first. `*word*` marks the one italic accent word of a headline.
// Every string is { de, en }; L(x) picks the active language.

export const NAV = [
  { id: 'film', de: 'Film', en: 'Film' },
  { id: 'leistungen', de: 'Leistungen', en: 'Services' },
  { id: 'showroom', de: 'Showroom', en: 'Showroom' },
  { id: 'ablauf', de: 'Ablauf', en: 'Process' },
  { id: 'faq', de: 'FAQ', en: 'FAQ' },
  { id: 'kontakt', de: 'Kontakt', en: 'Contact' },
];

export const UI = {
  start: { de: 'Projekt starten', en: 'Start a project' },
  call: { de: 'Erstgespräch · 30 Min · kostenlos', en: 'First call · 30 min · free' },
  skip: { de: 'Film überspringen', en: 'Skip the film' },
  scroll: { de: 'Scrollen', en: 'Scroll' },
  silent: { de: 'Stumm', en: 'Silent' },
  live: { de: 'Laut', en: 'Live' },
  concept: { de: 'Konzept', en: 'Concept' },
  menu: { de: 'Menü', en: 'Menu' },
  close: { de: 'Schließen', en: 'Close' },
  showroom: { de: 'Showroom ansehen', en: 'See the showroom' },
  hint: { de: 'Maus bewegen: Farbe geben', en: 'Move the mouse to add colour' },
  loading: { de: 'Der Film lädt', en: 'Loading the film' },
};

export const INTRO = {
  word: 'nemi',
  phon: { de: '[ˈnɛmi] · serbisch · stumm, ohne Stimme', en: '[ˈnɛmi] · Serbian · silent, without a voice' },
  prologue: {
    eye: { de: '00:00 — Prolog', en: '00:00 — Prologue' },
    h: { de: ['Die meisten Websites', '*schweigen*.'], en: ['Most websites', 'stay *silent*.'] },
    p: {
      de: 'Ein Logo, die Öffnungszeiten, ein Kontaktformular. Und dann: Stille.',
      en: 'A logo, the opening hours, a contact form. And then: silence.',
    },
  },
  voice: { de: ['Wir geben ihnen', 'eine *Stimme*.'], en: ['We give them', 'a *voice*.'] },
  day: {
    eye: { de: '06:58 — Ein Tag in deiner Stadt', en: '06:58 — A day in your city' },
    h: { de: ['Acht Branchen.', 'Ein *Studio*.'], en: ['Eight industries.', 'One *studio*.'] },
    p: {
      de: 'Webdesign, Motion und Content aus Österreich. Für Cafés, Kanzleien, Werkstätten und jede andere Branche.',
      en: 'Web design, motion and content from Austria. For cafés, law firms, workshops and every other industry.',
    },
  },
};

// The eight chapters of the film, in the order of the day.
export const CHAPTERS = [
  {
    id: 'cafe', seq: 'cafe', time: '07:12',
    label: { de: 'Café & Bäckerei', en: 'Café & bakery' },
    h: { de: ['Duft kann man nicht googeln.', 'Deine *Website* schon.'], en: ['You can’t google a smell.', 'Your *website*, you can.'] },
    p: {
      de: 'Speisekarte, Öffnungszeiten und Tischreservierung. So warm wie der erste Espresso des Tages.',
      en: 'Menu, opening hours and table booking. As warm as the first espresso of the day.',
    },
    card: {
      name: 'Café Mila', url: 'cafe-mila.at', style: 'warm',
      nav: { de: ['Karte', 'Über uns', 'Besuch'], en: ['Menu', 'About', 'Visit'] },
      cta: { de: 'Reservieren', en: 'Book a table' },
      eye: { de: 'Frühstück · Brot · Kuchen', en: 'Breakfast · bread · cakes' },
      h: { de: 'Kaffee, der nach Zuhause schmeckt.', en: 'Coffee that tastes like home.' },
      b: { de: 'Speisekarte ansehen', en: 'See the menu' },
      f: { de: ['Täglich frisch', 'Sonnige Terrasse', 'Online reservieren'], en: ['Fresh every day', 'Sunny terrace', 'Book online'] },
    },
  },
  {
    id: 'craft', seq: 'craft', time: '09:40',
    label: { de: 'Handwerk & Bau', en: 'Trades & construction' },
    h: { de: ['Handarbeit,', 'die man *online* sieht.'], en: ['Craftsmanship', 'you can *see* online.'] },
    p: {
      de: 'Referenzen, Werkstatt und Angebot auf einen Blick. Damit der nächste Auftrag nicht beim Nachbarn landet.',
      en: 'Projects, workshop and quote request at a glance, so the next job doesn’t go to the competitor next door.',
    },
    card: {
      name: { de: 'Tischlerei Eiche', en: 'Oak Joinery' }, url: 'tischlerei-eiche.at', style: 'wood',
      nav: { de: ['Leistungen', 'Referenzen', 'Werkstatt'], en: ['Services', 'Work', 'Workshop'] },
      cta: { de: 'Angebot', en: 'Get a quote' },
      eye: { de: 'Möbel · Küchen · Treppen', en: 'Furniture · kitchens · stairs' },
      h: { de: 'Handgemacht. Für Generationen.', en: 'Handmade. For generations.' },
      b: { de: 'Referenzen ansehen', en: 'View our work' },
      f: { de: ['Maßanfertigung', 'Eigene Werkstatt', 'Montage vor Ort'], en: ['Made to measure', 'Own workshop', 'Fitted on site'] },
    },
  },
  {
    id: 'dent', seq: 'dent', time: '11:05',
    label: { de: 'Arzt & Zahnarzt', en: 'Doctor & dentist' },
    h: { de: ['Vertrauen beginnt', 'vor dem *Termin*.'], en: ['Trust starts', 'before the *appointment*.'] },
    p: {
      de: 'Ruhige Gestaltung, klare Leistungen und Online-Termine. Auch für Angstpatienten.',
      en: 'Calm design, clear treatments and online booking. Anxious patients included.',
    },
    card: {
      name: 'Praxis am Park', url: 'praxis-am-park.at', style: 'clear',
      nav: { de: ['Leistungen', 'Team', 'Anfahrt'], en: ['Treatments', 'Team', 'Directions'] },
      cta: { de: 'Termin', en: 'Appointment' },
      eye: { de: 'Zahnmedizin', en: 'Dentistry' },
      h: { de: 'Gesund lächeln. Ohne Angst.', en: 'Healthy smiles. No fear.' },
      b: { de: 'Termin vereinbaren', en: 'Make an appointment' },
      f: { de: ['Online-Termin', 'Angstpatienten willkommen', 'Alle Kassen'], en: ['Online booking', 'Anxious patients welcome', 'All insurers'] },
    },
  },
  {
    id: 'law', seq: 'law', time: '14:30',
    label: { de: 'Kanzlei & Beratung', en: 'Law & consulting' },
    h: { de: ['Seriös heißt nicht', '*langweilig*.'], en: ['Serious doesn’t', 'mean *boring*.'] },
    p: {
      de: 'Kompetenz zeigen, ohne Fachchinesisch. Mit einer Website, die Mandanten in Ruhe überzeugt.',
      en: 'Show expertise without the jargon, with a website that quietly convinces clients.',
    },
    card: {
      name: { de: 'Kanzlei Aurum', en: 'Aurum Legal' }, url: 'kanzlei-aurum.at', style: 'noble',
      nav: { de: ['Rechtsgebiete', 'Anwälte', 'Kontakt'], en: ['Practice areas', 'Lawyers', 'Contact'] },
      cta: { de: 'Erstberatung', en: 'Consultation' },
      eye: { de: 'Rechtsanwälte', en: 'Attorneys at law' },
      h: { de: 'Klarheit in schwierigen Fragen.', en: 'Clarity in difficult questions.' },
      b: { de: 'Erstberatung anfragen', en: 'Request a consultation' },
      f: { de: ['Familienrecht', 'Arbeitsrecht', 'Vertragsrecht'], en: ['Family law', 'Employment law', 'Contract law'] },
    },
  },
  {
    id: 'fit', seq: 'fit', time: '17:15',
    label: { de: 'Fitness & Sport', en: 'Fitness & sport' },
    h: { de: ['Motivation,', 'die *mitzieht*.'], en: ['Energy that', '*pulls you in*.'] },
    p: {
      de: 'Kursplan live, Probetraining mit einem Klick und Bilder, die schon beim Scrollen den Puls heben.',
      en: 'Live class schedule, one-click free trial and visuals that raise the pulse while you scroll.',
    },
    card: {
      name: 'Puls Studio', url: 'puls-studio.at', style: 'bold',
      nav: { de: ['Kurse', 'Preise', 'Coaches'], en: ['Classes', 'Pricing', 'Coaches'] },
      cta: { de: 'Probetraining', en: 'Free trial' },
      eye: { de: 'Kraft · Ausdauer · Mobility', en: 'Strength · cardio · mobility' },
      h: { de: 'Stärker als gestern.', en: 'Stronger than yesterday.' },
      b: { de: 'Gratis testen', en: 'Try it free' },
      f: { de: ['Kursplan live', 'Personal Training', 'App-Check-in'], en: ['Live schedule', 'Personal training', 'App check-in'] },
    },
  },
  {
    id: 'barber', seq: 'barber', time: '19:20',
    label: { de: 'Friseur & Beauty', en: 'Hair & beauty' },
    h: { de: ['Stil, der', '*gebucht* wird.'], en: ['Style that', 'gets *booked*.'] },
    p: {
      de: 'Termine rund um die Uhr, Preise ohne Rätselraten und ein Auftritt, der zum Laden passt.',
      en: 'Bookings around the clock, prices without guesswork and a look that matches the shop.',
    },
    card: {
      name: 'Ferro Barbershop', url: 'ferro-barber.at', style: 'barber',
      nav: { de: ['Leistungen', 'Team', 'Preise'], en: ['Services', 'Team', 'Prices'] },
      cta: { de: 'Termin buchen', en: 'Book now' },
      eye: { de: 'Schnitt · Bart · Pflege', en: 'Cut · beard · care' },
      h: { de: 'Frisch geschnitten. In 30 Sekunden gebucht.', en: 'Fresh cut. Booked in 30 seconds.' },
      b: { de: 'Termin buchen', en: 'Book an appointment' },
      f: { de: ['Online-Termin', 'Bartpflege', 'Gutscheine'], en: ['Online booking', 'Beard care', 'Gift cards'] },
    },
  },
  {
    id: 'food', seq: 'food', time: '20:45',
    label: { de: 'Restaurant', en: 'Restaurant' },
    h: { de: ['Der Tisch ist', 'schon *reserviert*.'], en: ['The table is', 'already *booked*.'] },
    p: {
      de: 'Speisekarte, Weinbegleitung und Reservierung ohne Anruf. Der Hunger kommt beim Scrollen.',
      en: 'Menu, wine pairing and reservations without a phone call. Appetite comes with scrolling.',
    },
    card: {
      name: 'Osteria Lume', url: 'osteria-lume.at', style: 'dinner',
      nav: { de: ['Menü', 'Weine', 'Über uns'], en: ['Menu', 'Wines', 'About'] },
      cta: { de: 'Reservieren', en: 'Reserve' },
      eye: { de: 'Saisonale Küche', en: 'Seasonal kitchen' },
      h: { de: 'Ein Abend, über den man spricht.', en: 'An evening people talk about.' },
      b: { de: 'Tisch reservieren', en: 'Book a table' },
      f: { de: ['Saisonale Karte', 'Weinbegleitung', 'Private Dining'], en: ['Seasonal menu', 'Wine pairing', 'Private dining'] },
    },
  },
  {
    id: 'hotel', seq: 'hotel', time: '23:10',
    label: { de: 'Hotel & Ferienwohnung', en: 'Hotel & holiday homes' },
    h: { de: ['Ankommen,', 'bevor man *anreist*.'], en: ['Arrive', 'before you *travel*.'] },
    p: {
      de: 'Zimmer, die man spürt, bevor man sie betritt. Und Direktbuchung ohne Provision an Plattformen.',
      en: 'Rooms you can feel before you walk in. And direct booking without paying commission to platforms.',
    },
    card: {
      name: 'Hotel Alba', url: 'hotel-alba.at', style: 'linen',
      nav: { de: ['Zimmer', 'Erleben', 'Lage'], en: ['Rooms', 'Experience', 'Location'] },
      cta: { de: 'Buchen', en: 'Book' },
      eye: { de: 'Boutique-Hotel', en: 'Boutique hotel' },
      h: { de: 'Ankommen und durchatmen.', en: 'Arrive and breathe.' },
      b: { de: 'Verfügbarkeit prüfen', en: 'Check availability' },
      f: { de: ['Direkt buchen', 'Frühstück inklusive', 'Spa & Garten'], en: ['Book direct', 'Breakfast included', 'Spa & garden'] },
    },
  },
];

export const FINALE = {
  eye: { de: '23:59 — Noch wach?', en: '23:59 — Still up?' },
  q: { de: ['Und dein', '*Geschäft*?'], en: ['And your', '*business*?'] },
  next: { de: ['Es ist das', '*nächste*.'], en: ['It’s the', '*next* one.'] },
  p: {
    de: 'Wir bauen Websites, die beim Scrollen erzählen. Von Grund auf, ohne Baukasten, für jede Branche.',
    en: 'We build websites that tell a story as you scroll. From scratch, without templates, for every industry.',
  },
};

export const MANIFEST = {
  lines: {
    de: ['Nemi heißt auf Serbisch „stumm“.', 'Wir haben den Namen gewählt,', 'weil wir das *Gegenteil* machen.'],
    en: ['Nemi is Serbian for “silent”.', 'We chose the name', 'because we do the *opposite*.'],
  },
  cols: [
    { k: { de: 'Bewegung', en: 'Motion' }, v: { de: 'Scroll-Storytelling, Übergänge und Effekte, die sich hochwertig anfühlen und nie stören.', en: 'Scroll storytelling, transitions and effects that feel premium and never get in the way.' } },
    { k: { de: 'Bild', en: 'Image' }, v: { de: 'Fotos, Video und KI-Visuals, ausgewählt, bearbeitet oder neu erstellt für deine Marke.', en: 'Photos, video and AI visuals, chosen, edited or created for your brand.' } },
    { k: { de: 'Klarheit', en: 'Clarity' }, v: { de: 'Ein Ziel pro Seite: dass Menschen anrufen, buchen oder vorbeikommen.', en: 'One goal per page: that people call, book or come by.' } },
  ],
};

export const SERVICES = {
  eye: { de: 'Leistungen', en: 'Services' },
  h: { de: ['Alles, was deine Website', 'zum *Sprechen* bringt.'], en: ['Everything that makes', 'your website *speak*.'] },
  items: [
    { n: '01', img: 'city', t: { de: 'Scroll-Storytelling', en: 'Scroll storytelling' }, d: { de: 'Deine Seite erzählt beim Scrollen eine Geschichte. Jede Bewegung führt zum nächsten Schritt.', en: 'Your page tells a story as people scroll. Every movement leads to the next step.' } },
    { n: '02', img: 'cafe', t: { de: 'Animation & Effekte', en: 'Animation & effects' }, d: { de: 'Übergänge, Hover-Effekte, Text-Reveals und 3D, die sich hochwertig anfühlen und nie stören.', en: 'Transitions, hover effects, text reveals and 3D that feel premium and never get in the way.' } },
    { n: '03', img: 'food', t: { de: 'Bild, Video & KI', en: 'Images, video & AI' }, d: { de: 'Passende Fotos, Videos und KI-Visuals. Ausgewählt, bearbeitet oder neu erstellt für deine Marke.', en: 'The right photos, video and AI visuals. Chosen, edited or created for your brand.' } },
    { n: '04', img: 'law', t: { de: 'Texte & Mehrsprachig', en: 'Copy & multilingual' }, d: { de: 'Klare Texte auf Deutsch, Englisch und weiteren Sprachen. Sauber übersetzt und für Google eingerichtet.', en: 'Clear copy in German, English and more. Properly translated and set up for Google.' } },
    { n: '05', img: 'fit', t: { de: 'Schnell & auffindbar', en: 'Fast & findable' }, d: { de: 'Schlanker Code, kurze Ladezeiten und SEO-Grundlagen ab dem ersten Tag.', en: 'Lean code, short loading times and SEO basics from day one.' } },
    { n: '06', img: 'hotel', t: { de: 'Hosting & Betreuung', en: 'Hosting & care' }, d: { de: 'Domain, Hosting und Änderungen aus einer Hand. Du hast immer denselben Ansprechpartner.', en: 'Domain, hosting and updates from one place. You always talk to the same person.' } },
  ],
};

export const SHOWROOM = {
  eye: { de: 'Showroom', en: 'Showroom' },
  h: { de: ['Acht Branchen.', 'Acht *Stimmen*.'], en: ['Eight industries.', 'Eight *voices*.'] },
  p: {
    de: 'Konzepte aus dem Film: so könnte deine Website aussehen. Jede Branche hat ihre eigene Sprache, und genau die finden wir.',
    en: 'Concepts from the film: this is how your website could look. Every industry has its own language, and we find it.',
  },
};

export const PROCESS = {
  eye: { de: 'Ablauf', en: 'Process' },
  h: { de: ['Vom ersten Gespräch', 'bis *online*.'], en: ['From the first call', 'to *launch*.'] },
  steps: [
    { t: { de: 'Kennenlernen', en: 'Getting to know you' }, d: { de: 'Ein Gespräch, 30 Minuten, kostenlos. Du erzählst von deinem Unternehmen, wir hören zu und stellen die richtigen Fragen.', en: 'One call, 30 minutes, free. You tell us about your business, we listen and ask the right questions.' } },
    { t: { de: 'Konzept', en: 'Concept' }, d: { de: 'Moodboard, Schriften, Farben und ein erster Entwurf. Du siehst die Richtung, bevor eine Zeile Code entsteht.', en: 'Moodboard, typefaces, colours and a first draft. You see the direction before a single line of code.' } },
    { t: { de: 'Gestaltung & Entwicklung', en: 'Design & build' }, d: { de: 'Wir bauen deine Website von Grund auf, ohne Baukasten. Über einen Vorschau-Link siehst du jeden Fortschritt.', en: 'We build your website from scratch, without templates. A preview link shows you every step.' } },
    { t: { de: 'Launch & Betreuung', en: 'Launch & care' }, d: { de: 'Domain, Hosting, Google. Wir bringen alles online und bleiben auch danach für dich da.', en: 'Domain, hosting, Google. We take everything live and stay with you afterwards.' } },
  ],
};

export const FACTS = [
  { v: '2–3', u: { de: 'Wochen', en: 'weeks' }, d: { de: 'bis eine One-Page-Website online ist', en: 'until a one-page website is live' } },
  { v: '0', u: { de: 'Baukasten', en: 'templates' }, d: { de: 'jede Seite ist eigener Code', en: 'every page is hand-written code' } },
  { v: '30', u: { de: 'Minuten', en: 'minutes' }, d: { de: 'Erstgespräch, kostenlos', en: 'first call, free of charge' } },
  { v: 'DE·EN', u: '', d: { de: 'und weitere Sprachen', en: 'and more languages' } },
];

export const FAQ = {
  eye: { de: 'FAQ', en: 'FAQ' },
  h: { de: ['Gute', '*Fragen*.'], en: ['Good', '*questions*.'] },
  p: { de: 'Deine Frage ist nicht dabei? Schreib uns einfach.', en: 'Your question isn’t here? Just write to us.' },
  items: [
    { q: { de: 'Was kostet eine Website?', en: 'How much does a website cost?' }, a: { de: 'Das hängt vom Umfang ab. Nach dem ersten Gespräch bekommst du ein klares Angebot mit Fixpreis, ohne versteckte Kosten.', en: 'It depends on the scope. After the first call you get a clear, fixed-price quote with no hidden costs.' } },
    { q: { de: 'Wie lange dauert es?', en: 'How long does it take?' }, a: { de: 'Eine One-Page-Website ist oft in zwei bis drei Wochen online. Größere Projekte brauchen länger, den Zeitplan legen wir gemeinsam fest.', en: 'A one-page website is often live in two to three weeks. Bigger projects take longer, and we set the schedule together.' } },
    { q: { de: 'Für welche Branchen arbeitet ihr?', en: 'Which industries do you work for?' }, a: { de: 'Für alle. Ob Café, Kanzlei, Werkstatt oder Hotel: Jede Branche hat ihre eigene Sprache, und genau die finden wir für dich.', en: 'All of them. Café, law firm, workshop or hotel, every industry has its own language, and we find the right one for you.' } },
    { q: { de: 'Was brauche ich von meiner Seite?', en: 'What do I need to provide?' }, a: { de: 'Vor allem dein Wissen über dein Unternehmen. Logo, Texte und Fotos sind willkommen. Was fehlt, organisieren wir.', en: 'Mostly your knowledge of your business. Logo, texts and photos are welcome. Whatever is missing, we take care of.' } },
    { q: { de: 'Kann ich später Inhalte ändern lassen?', en: 'Can I have content changed later?' }, a: { de: 'Ja. Öffnungszeiten, Preise oder neue Bilder ändern wir schnell für dich, auf Wunsch im Rahmen einer monatlichen Betreuung.', en: 'Yes. We update opening hours, prices or new images quickly, on request as part of a monthly care plan.' } },
    { q: { de: 'Funktioniert die Website auch am Handy?', en: 'Does the website work on phones?' }, a: { de: 'Ja. Wir gestalten zuerst für das Handy und testen auf allen gängigen Geräten. Animationen passen sich an und respektieren die Einstellung für reduzierte Bewegung.', en: 'Yes. We design for phones first and test on all common devices. Animations adapt and respect the reduced-motion setting.' } },
  ],
};

export const CONTACT = {
  eye: { de: 'Kontakt', en: 'Contact' },
  h: { de: ['Lass uns deiner Marke', 'eine *Stimme* geben.'], en: ['Let’s give your brand', 'a *voice*.'] },
  p: { de: 'Erzähl uns kurz von deinem Vorhaben. Wir melden uns persönlich bei dir, meist am selben Tag.', en: 'Tell us briefly about your project. We’ll get back to you personally, usually the same day.' },
  mail: 'hallo@nemistudio.at',
  direct: { de: 'Oder direkt per E-Mail', en: 'Or email us directly' },
  copy: { de: 'Kopieren', en: 'Copy' },
  copied: { de: 'Kopiert', en: 'Copied' },
  f: {
    name: { de: 'Name', en: 'Name' },
    email: { de: 'E-Mail', en: 'Email' },
    biz: { de: 'Unternehmen', en: 'Business' },
    ind: { de: 'Branche', en: 'Industry' },
    pick: { de: 'Bitte wählen', en: 'Please choose' },
    other: { de: 'Andere Branche', en: 'Another industry' },
    msg: { de: 'Worum geht es?', en: 'What’s it about?' },
    send: { de: 'Anfrage senden', en: 'Send request' },
    sent: { de: 'Danke! Dein E-Mail-Programm öffnet sich mit der fertigen Nachricht.', en: 'Thank you! Your email app opens with the message ready to send.' },
  },
};

export const FOOT = {
  big: { de: ['Bereit, laut', 'zu *werden*?'], en: ['Ready to', 'be *heard*?'] },
  legal: { de: 'Impressum', en: 'Legal notice' },
  privacy: { de: 'Datenschutz', en: 'Privacy' },
  credits: { de: 'Bildnachweis', en: 'Credits' },
  top: { de: 'Nach oben', en: 'Back to top' },
  creditText: {
    de: 'Videos im Film: Mixkit (Mixkit Stock Video Free License). Die Marken in den Konzepten sind erfunden.',
    en: 'Footage in the film: Mixkit (Mixkit Stock Video Free License). The brands in the concepts are fictional.',
  },
};
