// Copy of the four concept websites. Brands, people and reviews are invented for the showroom.
// Every string is { de, en }; `*word*` marks the italic accent of a headline.

export const CAFE = {
  brand: 'Mila',
  sub: { de: 'Café · Bäckerei · Wien 7', en: 'Café · bakery · Vienna 7' },
  nav: { de: ['Karte', 'Über uns', 'Besuch'], en: ['Menu', 'About', 'Visit'] },
  cta: { de: 'Tisch reservieren', en: 'Book a table' },
  eye: { de: 'Neubaugasse 12 · seit 2009', en: 'Neubaugasse 12 · since 2009' },
  h: { de: ['Kaffee,', '*langsam* gemacht.'], en: ['Coffee,', 'made *slowly*.'] },
  p: {
    de: 'Frühstück bis 14 Uhr, Brot aus dem eigenen Ofen und der beste Platz am Fenster.',
    en: 'Breakfast until 2 pm, bread from our own oven and the best seat by the window.',
  },
  menuBtn: { de: 'Karte ansehen', en: 'See the menu' },
  open: { de: 'Heute geöffnet · 7:00–19:00', en: 'Open today · 7 am – 7 pm' },
  ring: { de: 'FRISCH GEBACKEN · JEDEN MORGEN · ', en: 'BAKED FRESH · EVERY MORNING · ' },
  marquee: {
    de: ['Croissant', 'Pain au chocolat', 'Zimtschnecke', 'Sauerteigbrot', 'Flat White', 'Chai Latte', 'Topfengolatsche'],
    en: ['Croissant', 'Pain au chocolat', 'Cinnamon roll', 'Sourdough', 'Flat white', 'Chai latte', 'Quark pastry'],
  },
  menu: {
    eye: { de: 'Die Karte', en: 'The menu' },
    h: { de: ['Alles aus der', 'eigenen *Backstube*.'], en: ['Everything from', 'our own *bakery*.'] },
    p: {
      de: 'Bohnen aus einer kleinen Wiener Rösterei, Milch vom Bauernhof, Butter statt Kompromiss.',
      en: 'Beans from a small Vienna roastery, milk from the farm, butter instead of compromise.',
    },
    cats: [
      {
        t: { de: 'Kaffee', en: 'Coffee' },
        items: [
          { n: 'Espresso', p: '2,60', img: 'cafe' },
          { n: { de: 'Wiener Melange', en: 'Viennese melange' }, p: '3,90', img: 'cafe' },
          { n: 'Flat White', p: '4,20', img: 'cafe' },
          { n: { de: 'Hafer-Cappuccino', en: 'Oat cappuccino' }, p: '4,40', img: 'cafe' },
          { n: 'Chai Latte', p: '4,60', img: 'cafe' },
        ],
      },
      {
        t: { de: 'Frühstück', en: 'Breakfast' },
        items: [
          { n: { de: 'Mila-Frühstück', en: 'Mila breakfast' }, d: { de: 'Gebäck, Butter, Marmelade, Ei, Kaffee', en: 'Pastry, butter, jam, egg, coffee' }, p: '12,80', img: 'cafe-croissants2' },
          { n: { de: 'Sauerteig & Avocado', en: 'Sourdough & avocado' }, d: { de: 'mit pochiertem Ei', en: 'with a poached egg' }, p: '11,50', img: 'cafe-room' },
          { n: 'Porridge', d: { de: 'Birne, Walnuss, Honig', en: 'Pear, walnut, honey' }, p: '8,90', img: 'cafe-interior' },
          { n: 'Shakshuka', d: { de: 'mit warmem Brot', en: 'with warm bread' }, p: '12,40', img: 'cafe-room' },
        ],
      },
      {
        t: { de: 'Gebäck', en: 'Pastries' },
        items: [
          { n: { de: 'Butter-Croissant', en: 'Butter croissant' }, p: '3,20', img: 'cafe-croissant' },
          { n: 'Pain au chocolat', p: '3,60', img: 'cafe-painchoc' },
          { n: { de: 'Zimtschnecke', en: 'Cinnamon roll' }, p: '3,90', img: 'cafe-croissants2' },
          { n: { de: 'Topfengolatsche', en: 'Quark pastry' }, p: '3,50', img: 'cafe-pastries' },
        ],
      },
    ],
  },
  about: {
    eye: { de: 'Über uns', en: 'About' },
    h: { de: ['Ein Ort zum', '*Bleiben*.'], en: ['A place', 'to *stay*.'] },
    p: {
      de: 'Mila ist das Wohnzimmer der Neubaugasse. Wir backen ab vier Uhr früh, damit um sieben alles duftet. Lange Tische, gutes Licht und niemand, der dich zum Gehen drängt.',
      en: 'Mila is the living room of Neubaugasse. We start baking at four in the morning so everything smells right at seven. Long tables, good light and nobody rushing you out.',
    },
    pics: [
      { img: 'cafe-interior', c: { de: 'Der lange Tisch', en: 'The long table' } },
      { img: 'cafe-room', c: { de: 'Fensterplatz', en: 'Window seat' } },
      { img: 'cafe-pastries', c: { de: 'Heute aus dem Ofen', en: 'Out of the oven today' } },
      { img: 'cafe-croissant', c: { de: 'Sonntag, 9 Uhr', en: 'Sunday, 9 am' } },
    ],
    facts: [
      { v: '04:00', t: { de: 'geht der Ofen an', en: 'the oven goes on' } },
      { v: '58', t: { de: 'Plätze, drinnen und draußen', en: 'seats, inside and out' } },
      { v: '0', t: { de: 'Fertigteige', en: 'ready-made doughs' } },
    ],
  },
  reviews: {
    eye: { de: 'Gäste', en: 'Guests' },
    items: [
      { q: { de: 'Das Croissant ist so gut, dass ich jetzt jeden Samstag quer durch die Stadt fahre.', en: 'The croissant is so good I now cross the whole city every Saturday.' }, a: 'Lena M.' },
      { q: { de: 'Endlich ein Café, in dem man mit dem Laptop willkommen ist und trotzdem Ruhe hat.', en: 'Finally a café where your laptop is welcome and it is still quiet.' }, a: 'Jakob R.' },
      { q: { de: 'Die Melange schmeckt wie bei meiner Oma. Nur der Ausblick ist besser.', en: 'The melange tastes like my grandmother’s. Only the view is better.' }, a: 'Sabine K.' },
    ],
  },
  visit: {
    eye: { de: 'Besuch', en: 'Visit' },
    h: { de: ['Komm', '*vorbei*.'], en: ['Come', '*by*.'] },
    hours: [
      { d: { de: 'Montag – Freitag', en: 'Monday – Friday' }, t: '7:00 – 19:00' },
      { d: { de: 'Samstag', en: 'Saturday' }, t: '8:00 – 18:00' },
      { d: { de: 'Sonntag & Feiertag', en: 'Sunday & holidays' }, t: '9:00 – 17:00' },
    ],
    addr: ['Neubaugasse 12', '1070 Wien'],
    way: { de: 'U3 Neubaugasse · 2 Minuten zu Fuß', en: 'U3 Neubaugasse · 2 minutes on foot' },
    form: {
      t: { de: 'Tisch reservieren', en: 'Book a table' },
      date: { de: 'Datum', en: 'Date' },
      time: { de: 'Uhrzeit', en: 'Time' },
      ppl: { de: 'Personen', en: 'Guests' },
      send: { de: 'Anfragen', en: 'Request' },
    },
  },
  foot: { de: '© 2026 Café Mila · Ein Konzept von Nemi Studio', en: '© 2026 Café Mila · A concept by Nemi Studio' },
};

export const LAW = {
  brand: 'AURUM',
  sub: { de: 'Rechtsanwälte · Wien', en: 'Attorneys at law · Vienna' },
  nav: { de: ['Rechtsgebiete', 'Anwälte', 'Kanzlei', 'Kontakt'], en: ['Practice areas', 'Lawyers', 'Firm', 'Contact'] },
  cta: { de: 'Erstberatung', en: 'Consultation' },
  eye: { de: 'Schottenring 14 · 1010 Wien', en: 'Schottenring 14 · 1010 Vienna' },
  h: { de: ['Recht,', '*klar* gesprochen.'], en: ['Law,', '*clearly* spoken.'] },
  p: {
    de: 'Wirtschafts-, Arbeits- und Familienrecht für Unternehmen und Privatpersonen. Verständlich, diskret und mit einem klaren Plan.',
    en: 'Corporate, employment and family law for companies and private clients. Clear, discreet and with a plan.',
  },
  btn: { de: 'Erstberatung vereinbaren', en: 'Book a first consultation' },
  btn2: { de: 'Rechtsgebiete', en: 'Practice areas' },
  stats: [
    { v: 25, s: '+', t: { de: 'Jahre Erfahrung', en: 'years of experience' } },
    { v: 1800, s: '', t: { de: 'abgeschlossene Mandate', en: 'cases closed' } },
    { v: 4, s: '', t: { de: 'Sprachen · DE EN BKS IT', en: 'languages · DE EN BCS IT' } },
  ],
  statement: {
    h: { de: 'Wir übersetzen Paragraphen in *Entscheidungen*.', en: 'We translate paragraphs into *decisions*.' },
    p: {
      de: 'Gute Beratung beginnt mit Zuhören. Erst wenn wir Ihre Lage verstehen, sprechen wir über Wege, Risiken und Kosten, und zwar in Sätzen, die man ohne Jusstudium versteht.',
      en: 'Good advice starts with listening. Only once we understand your situation do we talk about options, risks and costs, in sentences you can follow without a law degree.',
    },
  },
  areas: {
    eye: { de: 'Rechtsgebiete', en: 'Practice areas' },
    items: [
      { t: { de: 'Wirtschaftsrecht', en: 'Corporate law' }, d: { de: 'Gründung, Gesellschaftsverträge, Übernahmen und laufende Beratung für Unternehmen jeder Größe.', en: 'Formation, shareholder agreements, acquisitions and ongoing advice for companies of every size.' } },
      { t: { de: 'Arbeitsrecht', en: 'Employment law' }, d: { de: 'Dienstverträge, Kündigungen und Betriebsvereinbarungen. Für Arbeitgeber und Arbeitnehmer.', en: 'Contracts, dismissals and works agreements. For employers and employees.' } },
      { t: { de: 'Familienrecht', en: 'Family law' }, d: { de: 'Scheidung, Obsorge und Unterhalt. Mit Fingerspitzengefühl und, wo möglich, ohne Gericht.', en: 'Divorce, custody and maintenance. With tact and, where possible, out of court.' } },
      { t: { de: 'Immobilienrecht', en: 'Real estate law' }, d: { de: 'Kauf, Miete, Wohnungseigentum und Bauträgerverträge, geprüft bevor Sie unterschreiben.', en: 'Purchase, lease, condominiums and developer contracts, checked before you sign.' } },
      { t: { de: 'Erbrecht', en: 'Inheritance law' }, d: { de: 'Testamente, Verlassenschaften und Schenkungen, damit Ihr Wille auch gilt.', en: 'Wills, estates and gifts, so that your wishes actually hold.' } },
      { t: { de: 'Vertragsrecht', en: 'Contract law' }, d: { de: 'Verträge, die halten, was sie versprechen. Entworfen, geprüft und verhandelt.', en: 'Contracts that keep their promises. Drafted, reviewed and negotiated.' } },
    ],
  },
  team: {
    eye: { de: 'Anwälte', en: 'Lawyers' },
    h: { de: ['Vier Menschen,', 'ein *Anspruch*.'], en: ['Four people,', 'one *standard*.'] },
    people: [
      { n: 'Dr. Markus Leitner', r: { de: 'Partner · Wirtschaftsrecht', en: 'Partner · corporate law' }, l: 'DE · EN', img: 'law-man' },
      { n: 'Mag. Elena Novak', r: { de: 'Partnerin · Familienrecht', en: 'Partner · family law' }, l: 'DE · BKS', img: 'law-woman2' },
      { n: 'Mag. Daniel Huber', r: { de: 'Arbeitsrecht', en: 'Employment law' }, l: 'DE · EN · IT', img: 'law-suit' },
      { n: 'Mag. Sophie Lang', r: { de: 'Immobilien- & Erbrecht', en: 'Real estate & inheritance' }, l: 'DE · EN', img: 'law-woman' },
    ],
  },
  quote: { de: 'Ein gutes Gespräch erspart oft einen langen *Prozess*.', en: 'A good conversation often saves a long *trial*.' },
  steps: [
    { t: { de: 'Erstgespräch', en: 'First meeting' }, d: { de: '30 Minuten, telefonisch oder in der Kanzlei. Danach wissen Sie, wo Sie stehen.', en: '30 minutes, by phone or at our office. Afterwards you know where you stand.' } },
    { t: { de: 'Strategie', en: 'Strategy' }, d: { de: 'Wir zeigen Optionen, Chancen und Kosten. Schriftlich und transparent.', en: 'We lay out options, chances and costs. In writing and transparent.' } },
    { t: { de: 'Umsetzung', en: 'Execution' }, d: { de: 'Wir verhandeln, verfassen und vertreten. Sie sind jederzeit informiert.', en: 'We negotiate, draft and represent. You are informed at every step.' } },
  ],
  contact: {
    eye: { de: 'Kontakt', en: 'Contact' },
    h: { de: ['Erstberatung', '*anfragen*.'], en: ['Request a', '*consultation*.'] },
    name: { de: 'Name', en: 'Name' },
    reach: { de: 'Telefon oder E-Mail', en: 'Phone or email' },
    area: { de: 'Rechtsgebiet', en: 'Practice area' },
    msg: { de: 'Ihr Anliegen, kurz', en: 'Your matter, briefly' },
    send: { de: 'Termin anfragen', en: 'Request an appointment' },
    hours: { de: 'Mo – Do 8:30 – 17:30 · Fr 8:30 – 14:00', en: 'Mon – Thu 8:30 – 17:30 · Fri 8:30 – 14:00' },
  },
  foot: { de: '© 2026 Aurum Rechtsanwälte · Ein Konzept von Nemi Studio', en: '© 2026 Aurum Attorneys · A concept by Nemi Studio' },
};

export const GYM = {
  brand: 'PULS',
  sub: { de: 'Studio · Linz', en: 'Studio · Linz' },
  nav: { de: ['Kurse', 'Coaches', 'Preise'], en: ['Classes', 'Coaches', 'Pricing'] },
  cta: { de: 'Probetraining', en: 'Free trial' },
  h: { de: ['STÄRKER', 'ALS GESTERN.'], en: ['STRONGER', 'THAN YESTERDAY.'] },
  p: {
    de: 'Kraft, Boxen und HIIT in kleinen Gruppen. 24/7 geöffnet, mit Coaches, die deinen Namen kennen.',
    en: 'Strength, boxing and HIIT in small groups. Open 24/7, with coaches who know your name.',
  },
  live: { de: 'Jetzt: HIIT mit Mira · noch 4 Plätze', en: 'Now: HIIT with Mira · 4 spots left' },
  btn: { de: 'Gratis testen', en: 'Try it free' },
  btn2: { de: 'Kursplan', en: 'Schedule' },
  marquee: { de: ['KRAFT', 'BOXEN', 'HIIT', 'MOBILITY', 'AUSDAUER'], en: ['STRENGTH', 'BOXING', 'HIIT', 'MOBILITY', 'ENDURANCE'] },
  plan: {
    h: { de: 'KURSPLAN', en: 'SCHEDULE' },
    days: { de: ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'], en: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
    spots: { de: 'Plätze frei', en: 'spots left' },
    full: { de: 'Warteliste', en: 'Waitlist' },
    book: { de: 'Buchen', en: 'Book' },
  },
  classes: ['Power Lift', 'HIIT 45', 'Box Club', 'Mobility Flow', 'Core & Cardio', 'Kettlebell'],
  coaches: {
    h: { de: 'COACHES', en: 'COACHES' },
    items: [
      { n: 'Mira', r: { de: 'HIIT & Ausdauer', en: 'HIIT & endurance' }, q: { de: '„Die letzte Wiederholung zählt doppelt.“', en: '“The last rep counts twice.”' }, img: 'gym-box' },
      { n: 'Luka', r: { de: 'Kraft & Technik', en: 'Strength & technique' }, q: { de: '„Erst sauber, dann schwer.“', en: '“Clean first, heavy later.”' }, img: 'gym-coach' },
      { n: 'Jonas', r: { de: 'Boxen & Athletik', en: 'Boxing & athletics' }, q: { de: '„Hände hoch, Kopf frei.“', en: '“Hands up, head clear.”' }, img: 'gym-b' },
    ],
  },
  nums: [
    { v: '24/7', t: { de: 'geöffnet', en: 'open' } },
    { v: '1.200', t: { de: 'm² Trainingsfläche', en: 'm² training floor' } },
    { v: '40+', t: { de: 'Kurse pro Woche', en: 'classes a week' } },
    { v: '12', t: { de: 'Coaches', en: 'coaches' } },
  ],
  prices: {
    h: { de: 'PREISE', en: 'PRICING' },
    per: { de: '/ Monat', en: '/ month' },
    note: { de: 'Monatlich kündbar · keine Anmeldegebühr', en: 'Cancel monthly · no joining fee' },
    pop: { de: 'Beliebt', en: 'Popular' },
    pick: { de: 'Wählen', en: 'Choose' },
    tiers: [
      { n: 'Basic', v: '29', f: { de: ['Gerätefläche 24/7', 'App-Check-in', '1 Einführungstraining'], en: ['Gym floor 24/7', 'App check-in', '1 intro session'] } },
      { n: 'Plus', v: '49', hot: true, f: { de: ['Alles aus Basic', 'Alle Kurse', 'Sauna'], en: ['Everything in Basic', 'All classes', 'Sauna'] } },
      { n: 'Unlimited', v: '69', f: { de: ['Alles aus Plus', '2 Personal Trainings / Monat', 'Handtuch & Getränke'], en: ['Everything in Plus', '2 personal sessions / month', 'Towel & drinks'] } },
    ],
  },
  end: { de: ['DEIN ERSTES TRAINING', 'GEHT AUF UNS.'], en: ['YOUR FIRST SESSION', 'IS ON US.'] },
  endBtn: { de: 'Probetraining buchen', en: 'Book a free trial' },
  foot: { de: '© 2026 Puls Studio · Ein Konzept von Nemi Studio', en: '© 2026 Puls Studio · A concept by Nemi Studio' },
};

export const HOTEL = {
  brand: 'ALBA',
  sub: { de: 'Hotel am Wolfgangsee', en: 'Hotel on Lake Wolfgang' },
  nav: { de: ['Zimmer', 'Spa', 'Genuss', 'Lage'], en: ['Rooms', 'Spa', 'Dining', 'Location'] },
  cta: { de: 'Buchen', en: 'Book' },
  eye: { de: 'Boutique-Hotel · 12 Zimmer · Salzkammergut', en: 'Boutique hotel · 12 rooms · Salzkammergut' },
  h: { de: ['Ankommen.', '*Durchatmen.*'], en: ['Arrive.', '*Breathe.*'] },
  book: {
    in: { de: 'Anreise', en: 'Arrival' },
    out: { de: 'Abreise', en: 'Departure' },
    guests: { de: 'Gäste', en: 'Guests' },
    inV: { de: 'Fr, 14. Nov', en: 'Fri, 14 Nov' },
    outV: { de: 'So, 16. Nov', en: 'Sun, 16 Nov' },
    gV: { de: '2 Erwachsene', en: '2 adults' },
    go: { de: 'Verfügbarkeit prüfen', en: 'Check availability' },
  },
  intro: {
    h: { de: ['Zwölf Zimmer, ein See', 'und *kein* Grund zur Eile.'], en: ['Twelve rooms, one lake', 'and *no* reason to hurry.'] },
    p: {
      de: 'Alba ist ein altes Seehaus, behutsam erneuert. Holz, Leinen und Stein, morgens Nebel über dem Wasser und abends ein Glas Grüner Veltliner auf dem Steg.',
      en: 'Alba is an old lake house, gently renewed. Wood, linen and stone, mist over the water in the morning and a glass of Grüner Veltliner on the jetty at night.',
    },
  },
  rooms: {
    eye: { de: 'Die Zimmer', en: 'The rooms' },
    h: { de: ['Jedes Zimmer', 'eine *Aussicht*.'], en: ['Every room', 'a *view*.'] },
    from: { de: 'ab', en: 'from' },
    night: { de: '/ Nacht', en: '/ night' },
    items: [
      { n: { de: 'Seezimmer', en: 'Lake room' }, d: { de: '28 m² · Balkon zum See', en: '28 m² · balcony on the lake' }, v: '240', img: 'hotel-robe' },
      { n: { de: 'Steinzimmer', en: 'Stone room' }, d: { de: '32 m² · Natursteinbad', en: '32 m² · natural stone bath' }, v: '270', img: 'hotel-stone' },
      { n: { de: 'Atelier-Suite', en: 'Atelier suite' }, d: { de: '45 m² · Wohnbereich', en: '45 m² · living area' }, v: '360', img: 'hotel-wine' },
      { n: { de: 'Gartenzimmer', en: 'Garden room' }, d: { de: '26 m² · Terrasse', en: '26 m² · terrace' }, v: '220', img: 'hotel-pool' },
    ],
  },
  spa: {
    eye: { de: 'Spa', en: 'Spa' },
    h: { de: ['Spa am', '*Wasser*.'], en: ['Spa by', 'the *water*.'] },
    p: {
      de: 'Finnische Sauna, Dampfbad und ein beheizter Außenpool, der bis in den November 30 Grad hat. Danach: Bademantel, Tee, Stille.',
      en: 'Finnish sauna, steam bath and a heated outdoor pool that stays at 30 degrees into November. Then: bathrobe, tea, silence.',
    },
  },
  dine: {
    eye: { de: 'Genuss', en: 'Dining' },
    h: { de: ['Frühstück', 'bis *elf*.'], en: ['Breakfast', 'until *eleven*.'] },
    p: {
      de: 'Regional, saisonal und ohne Buffet-Hektik. Eier vom Bauern am Hang, Brot aus der Dorfbäckerei, Saibling aus dem See.',
      en: 'Regional, seasonal and without buffet rush. Eggs from the farm up the hill, bread from the village bakery, char from the lake.',
    },
    list: {
      de: ['Frühstück 7:30 – 11:00', 'Abendmenü Donnerstag bis Samstag', '80 Weine aus Österreich'],
      en: ['Breakfast 7:30 – 11:00', 'Dinner menu Thursday to Saturday', '80 Austrian wines'],
    },
  },
  where: {
    eye: { de: 'Lage', en: 'Location' },
    items: [
      { v: '50', u: 'min', t: { de: 'vom Flughafen Salzburg', en: 'from Salzburg airport' } },
      { v: '3', u: 'min', t: { de: 'zum eigenen Bootssteg', en: 'to our own jetty' } },
      { v: '12', u: { de: 'Zimmer', en: 'rooms' }, t: { de: 'nie mehr Gäste als Ruhe', en: 'never more guests than calm' } },
    ],
  },
  end: {
    h: { de: ['Direkt buchen,', '*besser* schlafen.'], en: ['Book direct,', 'sleep *better*.'] },
    p: {
      de: 'Bestpreis, späte Abreise und ein Glas Sekt zur Begrüßung. Nur bei Buchung über unsere Website.',
      en: 'Best price, late check-out and a glass of sparkling wine on arrival. Only when you book on our website.',
    },
  },
  foot: { de: '© 2026 Hotel Alba · Ein Konzept von Nemi Studio', en: '© 2026 Hotel Alba · A concept by Nemi Studio' },
};
