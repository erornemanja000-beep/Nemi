// All copy, German first. `*word*` marks the italic accent word of a headline, or a key word in body text.
// Every string is { de, en }; L(x) picks the active language.

export const NAV = [
  { id: 'showroom', de: 'Showroom', en: 'Showroom' },
  { id: 'sinn', de: 'Sechster Sinn', en: 'Sixth sense' },
  { id: 'leistungen', de: 'Leistungen', en: 'Services' },
  { id: 'ablauf', de: 'Ablauf', en: 'Process' },
  { id: 'faq', de: 'FAQ', en: 'FAQ' },
  { id: 'kontakt', de: 'Kontakt', en: 'Contact' },
];

export const UI = {
  start: { de: 'Projekt starten', en: 'Start a project' },
  call: { de: 'Erstgespräch · 30 Min · kostenlos', en: 'First call · 30 min · free' },
  skip: { de: 'Überspringen', en: 'Skip' },
  sound: { de: 'Ton an', en: 'Sound on' },
  mute: { de: 'Ton aus', en: 'Sound off' },
  play: { de: 'Film abspielen', en: 'Play the film' },
  replay: { de: 'Intro ansehen', en: 'Watch the intro' },
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

// The opening: the first device on the desk, before the camera dives in
export const OPEN = {
  eye: { de: 'Nemi Studio · Webdesign aus Österreich', en: 'Nemi Studio · web design from Austria' },
  h: { de: ['Websites, die', 'man *spürt*.'], en: ['Websites you', 'can *feel*.'] },
  p: {
    de: 'Riechen, fühlen, sehen, hören. Und der *sechste Sinn*. Scroll in den Bildschirm.',
    en: 'Smell, touch, sight, sound. And the *sixth sense*. Scroll into the screen.',
  },
  scroll: { de: 'Scrollen', en: 'Scroll' },
};

export const PORTAL = {
  next: { de: 'Nächster Sinn', en: 'Next sense' },
  enter: { de: 'Scroll, um einzutreten', en: 'Scroll to enter' },
};

export const BAR = {
  concept: { de: 'Sinn', en: 'Sense' },
  index: { de: 'Übersicht', en: 'Index' },
  start: { de: 'Nemi Studio', en: 'Nemi Studio' },
};

export const OUTRO = {
  eye: { de: 'Showroom', en: 'Showroom' },
  h: { de: ['Das war kein Film.', 'Das waren *Websites*.'], en: ['That wasn’t a film.', 'Those were *websites*.'] },
  p: {
    de: 'Vier Branchen, vier Sinne. So kann sich *deine Website* anfühlen. Jede Branche klingt anders, und genau diesen *Ton* finden wir.',
    en: 'Four industries, four senses. This is how *your website* can feel. Every industry sounds different, and we find exactly that *tone*.',
  },
  open: { de: 'Ansehen', en: 'View' },
};

export const SIXTH = {
  eye: { de: 'Der sechste Sinn', en: 'The sixth sense' },
  h: {
    de: 'Eine Website, die weiß, was du suchst, *bevor* du fragst.',
    en: 'A website that knows what you are looking for *before* you ask.',
  },
  p: {
    de: 'Nemi heißt auf Serbisch „*stumm*“. Wir bauen Websites, die *ohne Worte* sprechen: mit Bild, Bewegung und Gefühl.',
    en: 'Nemi is Serbian for “*silent*”. We build websites that speak *without words*: with image, motion and feeling.',
  },
};

export const INDUSTRIES = {
  de: ['Café & Gastronomie', 'Kanzlei & Beratung', 'Fitness & Sport', 'Hotel & Tourismus', 'Handwerk & Bau', 'Gesundheit & Praxis', 'Handel & Shop'],
  en: ['Café & hospitality', 'Law & consulting', 'Fitness & sport', 'Hotel & tourism', 'Trades & construction', 'Health & practice', 'Retail & shop'],
};

export const SERVICES = {
  eye: { de: 'Leistungen', en: 'Services' },
  h: { de: ['Alles, was deine Website', 'zum *Sprechen* bringt.'], en: ['Everything that makes', 'your website *speak*.'] },
  items: [
    { n: '01', img: 'w/cafe/1/d/15.webp', t: { de: 'Scroll-Storytelling', en: 'Scroll storytelling' }, d: { de: 'Deine Seite erzählt beim Scrollen eine *Geschichte*. Jede Bewegung führt zum nächsten Schritt.', en: 'Your page tells a *story* as people scroll. Every movement leads to the next step.' } },
    { n: '02', img: 'w/cafe/4/d/15.webp', t: { de: 'Animation & Effekte', en: 'Animation & effects' }, d: { de: 'Übergänge, Hover-Effekte, Text-Reveals und 3D, die sich *hochwertig* anfühlen und nie stören.', en: 'Transitions, hover effects, text reveals and 3D that feel *premium* and never get in the way.' } },
    { n: '03', img: 'w/hotel/2/d/15.webp', t: { de: 'Bild, Video & KI', en: 'Images, video & AI' }, d: { de: 'Passende Fotos, Videos und KI-Visuals. Ausgewählt, bearbeitet oder *neu erstellt* für deine Marke.', en: 'The right photos, video and AI visuals. Chosen, edited or *created* for your brand.' } },
    { n: '04', img: 'w/law/4/d/15.webp', t: { de: 'Texte & Mehrsprachig', en: 'Copy & multilingual' }, d: { de: 'Klare Texte auf Deutsch, Englisch und weiteren Sprachen. Sauber übersetzt und *für Google* eingerichtet.', en: 'Clear copy in German, English and more. Properly translated and set up *for Google*.' } },
    { n: '05', img: 'w/gym/2/d/15.webp', t: { de: 'Schnell & auffindbar', en: 'Fast & findable' }, d: { de: 'Schlanker Code, *kurze Ladezeiten* und SEO-Grundlagen ab dem ersten Tag.', en: 'Lean code, *short loading times* and SEO basics from day one.' } },
    { n: '06', img: 'w/hotel/5/d/15.webp', t: { de: 'Hosting & Betreuung', en: 'Hosting & care' }, d: { de: 'Domain, Hosting und Änderungen aus einer Hand. Du hast immer *denselben Ansprechpartner*.', en: 'Domain, hosting and updates from one place. You always talk to *the same person*.' } },
  ],
};

export const PROCESS = {
  eye: { de: 'Ablauf', en: 'Process' },
  h: { de: ['Vom ersten Gespräch', 'bis *online*.'], en: ['From the first call', 'to *launch*.'] },
  steps: [
    { t: { de: 'Kennenlernen', en: 'Getting to know you' }, d: { de: 'Ein Gespräch, 30 Minuten, *kostenlos*. Du erzählst von deinem Unternehmen, wir *hören zu* und stellen die richtigen Fragen.', en: 'One call, 30 minutes, *free*. You tell us about your business, we *listen* and ask the right questions.' } },
    { t: { de: 'Konzept', en: 'Concept' }, d: { de: 'Moodboard, Schriften, Farben und ein erster Entwurf. Du siehst die Richtung, *bevor* eine Zeile Code entsteht.', en: 'Moodboard, typefaces, colours and a first draft. You see the direction *before* a single line of code.' } },
    { t: { de: 'Gestaltung & Entwicklung', en: 'Design & build' }, d: { de: 'Wir bauen deine Website *von Grund auf*, ohne Baukasten. Über einen Vorschau-Link siehst du *jeden Fortschritt*.', en: 'We build your website *from scratch*, without templates. A preview link shows you *every step*.' } },
    { t: { de: 'Launch & Betreuung', en: 'Launch & care' }, d: { de: 'Domain, Hosting, Google. Wir bringen alles online und *bleiben* auch danach für dich da.', en: 'Domain, hosting, Google. We take everything live and *stay with you* afterwards.' } },
  ],
};

export const FACTS = [
  { v: { de: 'Dein', en: 'Your' }, u: { de: 'Tempo', en: 'pace' }, d: { de: 'Zeitplan *je nach Projekt*, gemeinsam festgelegt', en: 'timeline depends on *the project*, set together' } },
  { v: '0', u: { de: 'Baukasten', en: 'templates' }, d: { de: 'jede Seite ist *eigener Code*', en: 'every page is *hand-written code*' } },
  { v: '30', u: { de: 'Minuten', en: 'minutes' }, d: { de: 'Erstgespräch, *kostenlos*', en: 'first call, *free of charge*' } },
  { v: 'DE·EN', u: '', d: { de: 'und weitere Sprachen', en: 'and more languages' } },
];

export const FAQ = {
  eye: { de: 'FAQ', en: 'FAQ' },
  h: { de: ['Gute', '*Fragen*.'], en: ['Good', '*questions*.'] },
  p: { de: 'Deine Frage ist nicht dabei? *Schreib uns* einfach.', en: 'Your question isn’t here? Just *write to us*.' },
  items: [
    { q: { de: 'Was kostet eine Website?', en: 'How much does a website cost?' }, a: { de: 'Das hängt vom Umfang ab. Nach dem ersten Gespräch bekommst du ein klares Angebot mit *Fixpreis*, ohne versteckte Kosten.', en: 'It depends on the scope. After the first call you get a clear, *fixed-price* quote with no hidden costs.' } },
    { q: { de: 'Wie lange dauert es?', en: 'How long does it take?' }, a: { de: 'Das hängt *vom Projekt* ab: vom Umfang, von den Inhalten und davon, wann Texte und Bilder bereitstehen. Den Zeitplan legen wir im Erstgespräch gemeinsam fest, und über einen Vorschau-Link siehst du jeden Fortschritt.', en: 'It depends on *the project*: its scope, the content and when texts and images are ready. We set the timeline together in the first call, and a preview link shows you every step.' } },
    { q: { de: 'Für welche Branchen arbeitet ihr?', en: 'Which industries do you work for?' }, a: { de: 'Für *alle*. Ob Café, Kanzlei, Werkstatt oder Hotel: Jede Branche hat ihre eigene Sprache, und genau die finden wir für dich.', en: '*All* of them. Café, law firm, workshop or hotel, every industry has its own language, and we find the right one for you.' } },
    { q: { de: 'Was brauche ich von meiner Seite?', en: 'What do I need to provide?' }, a: { de: 'Vor allem *dein Wissen* über dein Unternehmen. Logo, Texte und Fotos sind willkommen. Was fehlt, organisieren wir.', en: 'Mostly *your knowledge* of your business. Logo, texts and photos are welcome. Whatever is missing, we take care of.' } },
    { q: { de: 'Kann ich später Inhalte ändern lassen?', en: 'Can I have content changed later?' }, a: { de: 'Ja. Öffnungszeiten, Preise oder neue Bilder ändern wir *schnell* für dich, auf Wunsch im Rahmen einer monatlichen Betreuung.', en: 'Yes. We update opening hours, prices or new images *quickly*, on request as part of a monthly care plan.' } },
    { q: { de: 'Funktioniert die Website auch am Handy?', en: 'Does the website work on phones?' }, a: { de: 'Ja. Wir gestalten *zuerst für das Handy* und testen auf allen gängigen Geräten. Animationen passen sich an und respektieren die Einstellung für reduzierte Bewegung.', en: 'Yes. We design *for phones first* and test on all common devices. Animations adapt and respect the reduced-motion setting.' } },
  ],
};

export const CONTACT = {
  eye: { de: 'Kontakt', en: 'Contact' },
  h: { de: ['Lass uns deiner Marke', 'eine *Stimme* geben.'], en: ['Let’s give your brand', 'a *voice*.'] },
  p: { de: 'Erzähl uns kurz von deinem Vorhaben. Wir melden uns *persönlich* bei dir, meist *am selben Tag*.', en: 'Tell us briefly about your project. We’ll get back to you *personally*, usually *the same day*.' },
  mail: 'nemistudio7@gmail.com',
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
    de: 'Videos: Mixkit (Mixkit Stock Video Free License) und Coverr (Coverr License). Fotos im Intro: Unsplash (Unsplash License). Musik im Intro: Mixkit.',
    en: 'Video: Mixkit (Mixkit Stock Video Free License) and Coverr (Coverr License). Intro photos: Unsplash (Unsplash License). Intro music: Mixkit.',
  },
};
