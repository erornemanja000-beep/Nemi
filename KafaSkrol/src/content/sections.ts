// Sekcije ispod prodavnice: pretplata, Probierset, O nama, Brew guide, Kontakt, footer (tekstovi.md sa dopunama Z3).
// Cene u tekstu su oznake koje popunjava sekcija (fill/tf), da se Grundpreis uvek računa:
//   {price} formatPrice, {was} formatPrice stare cene, {unit} formatUnitPrice, {shipping} formatPrice dostave,
//   {p3} {p6} {p12} formatPrice(giftPriceCents(n)). Tačan izlaz proverava scripts/check-content.ts.
import type { L, Link } from './types.ts'
import { legalPages } from './legal.ts'
import { productBySlug } from './products.ts'
import { shop } from './shop.ts'

/** Pretplata (tekstovi.md). Brojevi iz kojih se računaju cene u tekstovima. */
const subscriptionNumbers = {
  /** popust na svaku isporuku „Your coffee" */
  discountPercent: 10,
  /** primer u tekstu „Your coffee": On Repeat 250 g */
  example: { product: 'on-repeat', grams: 250 },
  /** „Surprise me": 2 × 250 g po isporuci, plus dostava iz shop.shipping */
  surprise: { priceCents: 3800, grams: 500 },
  /** poklon: broj isporuka „Surprise me", dostava je uračunata */
  giftDeliveries: [3, 6, 12],
}

/** Cena sa popustom pretplate, u centima (On Repeat 1350 → 1215). */
export function subscriptionPriceCents(cents: number): number {
  return Math.round((cents * (100 - subscriptionNumbers.discountPercent)) / 100)
}

/** Poklon: (cena „Surprise me" + dostava) × broj isporuka, u centima (3 → 12750). */
export function giftPriceCents(deliveries: number): number {
  return (subscriptionNumbers.surprise.priceCents + shop.shipping.feeCents) * deliveries
}

const tastingSet = productBySlug('tasting-set')
if (!tastingSet) throw new Error('sections.ts: nema proizvoda tasting-set u products.ts')

/** Link u footeru; `short` je kraći natpis za 390 px. */
type FooterLink = Link & { short?: L }

export const sections = {
  subscription: {
    title: { en: 'Never run out of beans', de: 'Nie mehr ohne Bohnen' } satisfies L,
    subtitle: { en: 'Fresh from the roastery, every 2 or 4 weeks.', de: 'Frisch aus der Rösterei, alle 2 oder 4 Wochen.' } satisfies L,
    options: [
      {
        id: 'yours',
        title: { en: 'Your coffee', de: 'Dein Kaffee' },
        // {price} = subscriptionPriceCents(cena primera), {was} = cena primera, {unit} = Grundpreis cene sa popustom
        text: {
          en: 'Pick any coffee and grind, 1 to 3 bags of 250\u00a0g, every 2 or 4 weeks. You save 10\u00a0% on every delivery. For example, On Repeat for {price} instead of {was} ({unit}).',
          de: 'Wähle Kaffee und Mahlgrad, 1 bis 3 Packungen à 250\u00a0g, alle 2 oder 4 Wochen. Du sparst 10\u00a0% bei jeder Lieferung. Zum Beispiel On Repeat um {price} statt {was} ({unit}).',
        },
      },
      {
        id: 'surprise',
        title: { en: 'Surprise me', de: 'Überrasch mich' },
        // {price} = surprise.priceCents, {unit} = Grundpreis za surprise.grams, {shipping} = shop.shipping.feeCents
        text: {
          en: "Every 4 weeks we send two different coffees we're excited about, 2 × 250\u00a0g, with a card on how to brew them. {price} per delivery ({unit}), plus {shipping} shipping.",
          de: 'Alle 4 Wochen schicken wir dir zwei verschiedene Kaffees, die uns gerade begeistern, 2 × 250\u00a0g, mit einer Karte zur Zubereitung. {price} pro Lieferung ({unit}), zzgl. {shipping} Versand.',
        },
      },
    ] satisfies { id: 'yours' | 'surprise'; title: L; text: L }[],
    /** Pravila otkaza po FAGG su NIJE POTVRĐENO (brief), proverava klijent. */
    terms: {
      en: "Pause, skip or cancel before any delivery. You'll see price and rhythm again before you pay.",
      de: 'Pausieren, überspringen oder kündigen geht vor jeder Lieferung. Preis und Rhythmus siehst du vor dem Bezahlen noch einmal.',
    } satisfies L,
    gift: {
      text: {
        en: 'As a gift: 3, 6 or 12 deliveries of Surprise me, paid once, ends by itself. 3 deliveries {p3}, 6 deliveries {p6}, 12 deliveries {p12}, shipping included in the price.',
        de: 'Als Geschenk: 3, 6 oder 12 Lieferungen „Überrasch mich“, einmal bezahlt, endet von selbst. 3 Lieferungen {p3}, 6 Lieferungen {p6}, 12 Lieferungen {p12}, Versand im Preis enthalten.',
      } satisfies L,
    },
    buttons: {
      start: { en: 'Start a subscription', de: 'Abo starten' } satisfies L,
      gift: { en: 'Give as a gift', de: 'Verschenken' } satisfies L,
    },
    /** red ispod oba dugmeta (Z3) */
    demo: { en: 'Demo: nothing is ordered or paid here.', de: 'Demo: Hier wird nichts bestellt oder bezahlt.' } satisfies L,
    toast: {
      start: { en: 'This is a demo, so no subscription was started.', de: 'Das ist eine Demo, es wurde kein Abo abgeschlossen.' } satisfies L,
      gift: { en: 'This is a demo, so no gift was ordered.', de: 'Das ist eine Demo, es wurde kein Geschenk bestellt.' } satisfies L,
    },
    ...subscriptionNumbers,
  },

  tastingSet: {
    title: { en: 'Not sure yet? Try four.', de: 'Noch unsicher? Probier vier.' } satisfies L,
    /** telefon */
    titleShort: { en: 'Try four.', de: 'Probier vier.' } satisfies L,
    subtitle: { en: 'Tasting set: 4 × 100\u00a0g filter coffee', de: 'Probierset: 4 × 100\u00a0g Filterkaffee' } satisfies L,
    /** opis seta iz products.ts + cena: {price} i {unit} iz prve veličine seta (400 g) */
    text: {
      en: `${tastingSet.description.en} {price} ({unit}), incl. VAT, plus shipping.`,
      de: `${tastingSet.description.de} {price} ({unit}), inkl. MwSt., zzgl. Versand.`,
    } satisfies L,
    product: tastingSet.slug,
    /** addToCart(product, 400, null) */
    button: { en: 'Add tasting set', de: 'Probierset in den Warenkorb' } satisfies L,
  },

  about: {
    title: { en: 'A roastery with chairs', de: 'Eine Rösterei mit Sesseln' } satisfies L,
    subtitle: { en: 'Small roastery, café up front.', de: 'Kleine Rösterei, vorne ein Café.' } satisfies L,
    text: {
      en: "{brand} is a small roastery with a café in Vienna's 7th district. Our roaster sits right behind the counter, so you can watch the beans turn brown while your coffee cools. In Vienna you stay as long as your cup lasts, often longer. We're fine with that. On every bag you'll find the farm, the altitude, the process and the day we roasted it.",
      de: '{brand} ist eine kleine Rösterei mit Café im 7. Bezirk. Die Röstmaschine steht gleich hinter der Theke: Du siehst, wie die Bohnen braun werden, während dein Kaffee abkühlt. In Wien bleibt man sitzen, solange die Tasse reicht, oft länger. Uns ist das recht. Auf jeder Packung stehen Farm, Höhe, Aufbereitung und der Tag, an dem wir geröstet haben.',
    } satisfies L,
    demo: { en: 'Concept: the brand, café and farms are made up.', de: 'Konzept: Marke, Café und Farmen sind erfunden.' } satisfies L,
    cta: { label: { en: 'Visit the café', de: 'Zum Café' }, href: '#contact' } satisfies Link,
    /** id-jevi iz media.photos */
    photos: ['onama-1', 'onama-2'],
  },

  brewGuide: {
    title: { en: 'Three steps, three minutes', de: 'Drei Schritte, drei Minuten' } satisfies L,
    /** telefon */
    titleShort: { en: '3 steps, 3 minutes', de: '3 Schritte, 3 Minuten' } satisfies L,
    subtitle: {
      en: 'Pour-over for one big cup: 18\u00a0g coffee, 288\u00a0g water (1:16), 93\u00a0°C.',
      de: 'Handfilter für eine große Tasse: 18\u00a0g Kaffee, 288\u00a0g Wasser (1:16), 93\u00a0°C.',
    } satisfies L,
    need: {
      label: { en: 'You need', de: 'Du brauchst' } satisfies L,
      text: {
        en: 'Dripper, paper filter, scale, kettle, timer.',
        de: 'Handfilter, Papierfilter, Waage, Wasserkocher, Timer.',
      } satisfies L,
    },
    /** `photo` je id iz media.photos; korak 3 koristi SIP poster (media.seq.sip.poster, alt iz chapters SIP). */
    steps: [
      {
        id: 'grind',
        title: { en: 'Grind', de: 'Mahlen' },
        text: {
          en: 'Grind 18\u00a0g of coffee medium-fine, about like table salt. Rinse the paper filter with hot water and pour that water away.',
          de: '18\u00a0g Kaffee mittelfein mahlen, etwa wie Speisesalz. Den Papierfilter mit heißem Wasser ausspülen und das Wasser weggießen.',
        },
        photo: 'guide-1',
      },
      {
        id: 'pour',
        title: { en: 'Pour', de: 'Aufgießen' },
        text: {
          en: 'Start the timer. Pour 50\u00a0g of water at 93\u00a0°C and let it bloom for 45 seconds. Then pour slowly in circles until the scale shows 288\u00a0g.',
          de: 'Timer starten. 50\u00a0g Wasser mit 93\u00a0°C aufgießen und 45 Sekunden aufquellen lassen. Dann langsam in Kreisen gießen, bis die Waage 288\u00a0g zeigt.',
        },
        photo: 'guide-2',
      },
      {
        id: 'sip',
        title: { en: 'Sip', de: 'Genießen' },
        text: {
          en: "Let it drip through. At about 3:00 it's done. Swirl the carafe once and pour.",
          de: 'Durchlaufen lassen. Nach etwa 3:00 ist er fertig. Kanne einmal schwenken und einschenken.',
        },
        photo: null,
      },
    ] satisfies { id: 'grind' | 'pour' | 'sip'; title: L; text: L; photo: string | null }[],
    tip: {
      label: { en: 'Tip', de: 'Tipp' } satisfies L,
      text: { en: 'Too sour? Grind finer. Too bitter? Grind coarser.', de: 'Zu sauer? Feiner mahlen. Zu bitter? Gröber mahlen.' } satisfies L,
    },
    recommendation: {
      en: 'Works well with Guji, Nyeri and Tarrazú Honey.',
      de: 'Passt gut zu Guji, Nyeri und Tarrazú Honey.',
    } satisfies L,
    cta: { label: { en: 'Shop filter coffee', de: 'Filterkaffee ansehen' }, href: '/?brew=filter#find-your-cup' } satisfies Link,
  },

  /** Sve ovde (adresa, radno vreme, dani prženja, cupping, telefon) je izmišljeno za demo (tekstovi.md). */
  contact: {
    title: { en: 'Come by', de: 'Komm vorbei' } satisfies L,
    subtitle: {
      en: 'Café, beans to go and cupping in 1070 Vienna.',
      de: 'Café, Bohnen zum Mitnehmen und Cupping in 1070 Wien.',
    } satisfies L,
    address: {
      /** demo adresa, ista na oba jezika */
      line: 'Röstergasse 18, 1070 Wien',
      note: { en: "(Demo address, this street doesn't exist.)", de: '(Demo-Adresse, diese Straße gibt es nicht.)' } satisfies L,
    },
    hours: {
      label: { en: 'Café', de: 'Café' } satisfies L,
      /** u jednom redu: redovi spojeni sa „ · " (tekstovi.md) */
      rows: [
        { days: { en: 'Mon–Fri', de: 'Mo–Fr' }, time: { en: '8:00–18:00', de: '8–18 Uhr' } },
        { days: { en: 'Sat', de: 'Sa' }, time: { en: '9:00–17:00', de: '9–17 Uhr' } },
        { days: { en: 'Sun & public holidays', de: 'Sonn- und Feiertag' }, time: { en: 'closed', de: 'geschlossen' } },
      ] satisfies { days: L; time: L }[],
    },
    roasting: {
      en: 'We roast on Tuesdays and Fridays. Come by in the morning and watch.',
      de: 'Wir rösten dienstags und freitags. Komm am Vormittag vorbei und schau zu.',
    } satisfies L,
    cupping: {
      en: 'First Saturday of the month, 10:00, €29 per person. Book by email.',
      de: 'Jeden ersten Samstag im Monat, 10 Uhr, €\u00a029 pro Person. Anmeldung per Mail.',
    } satisfies L,
    cuppingLabel: { en: 'Cupping', de: 'Cupping' } satisfies L,
    /** {email} = brand.email; domen .example je rezervisan */
    email: '{email}',
    /** {phone} = brand.phone (tel: link je brand.phoneHref) */
    phone: { value: '{phone}', note: { en: '(Demo)', de: '(Demo)' } satisfies L },
    wholesale: {
      en: 'For offices and restaurants: {wholesale}',
      de: 'Für Büros und Gastro: {wholesale}',
    } satisfies L,
    cta: { label: { en: 'Write to us', de: 'Schreib uns' }, href: 'mailto:{email}' } satisfies Link,
    /** id iz media.photos; čip „Symbolbild" je photo.caption */
    photo: 'kontakt-1',
    /** figcaption ispod fotografije (Z3, 1b) */
    photoCaption: {
      en: 'Illustrative photo: a café courtyard in Vienna. Not our café.',
      de: 'Symbolbild: Gastgarten in einem Wiener Innenhof. Nicht unser Café.',
    } satisfies L,
  },

  footer: {
    columns: [
      {
        title: { en: 'Shop', de: 'Shop' },
        links: [
          { label: { en: 'Coffee', de: 'Kaffee' }, href: '#find-your-cup' },
          { label: { en: 'Equipment', de: 'Zubehör' }, href: '#find-your-cup' },
          { label: { en: 'Subscription', de: 'Abo' }, href: '#subscription' },
          { label: { en: 'Tasting set', de: 'Probierset' }, href: '#tasting-set' },
        ],
      },
      {
        title: { en: '{brand}', de: '{brand}' },
        links: [
          { label: { en: 'About', de: 'Über uns' }, href: '#about' },
          { label: { en: 'Brew guide', de: 'Zubereitung' }, href: '#brew-guide' },
          { label: { en: 'Café & contact', de: 'Café & Kontakt' }, href: '#contact' },
          {
            label: { en: 'Wholesale', de: 'Für Büros & Gastro' },
            short: { en: 'Wholesale', de: 'Für Firmen' },
            href: '#contact',
          },
        ],
      },
      {
        title: { en: 'Legal', de: 'Rechtliches' },
        // natpis je naslov stranice; „Cookies" umesto „Cookie settings" po predlogu Z3 (podešavanja ne postoje)
        links: legalPages.map((p) => ({ label: p.title, href: `/${p.slug}` })),
      },
    ] satisfies { title: L; links: FooterLink[] }[],
    /** Dugme za opoziv (FAGG § 13a). EN je NEPROVERENO na EUR-Lex-u (Direktiva (EU) 2023/2673; Z3 tačka 6). */
    withdraw: { label: { en: 'Withdraw from contract here', de: 'Vertrag widerrufen' }, href: '/widerruf' } satisfies Link,
    /** Obeleženo mesto za zvanični Gewährleistungslabel (otvoreno pitanje 8). */
    guarantee: {
      text: {
        en: 'Placeholder: in a real shop, the official notice on the legal guarantee goes here, unchanged and in color.',
        de: 'Platzhalter: Im echten Shop steht hier der offizielle Hinweis zur gesetzlichen Gewährleistung, unverändert und in Farbe.',
      } satisfies L,
      /** 390 px */
      short: { en: 'Placeholder · Legal guarantee notice', de: 'Platzhalter · Gewährleistungshinweis' } satisfies L,
      aria: { en: 'Placeholder for the legal guarantee notice', de: 'Platzhalter für den Gewährleistungshinweis' } satisfies L,
    },
    newsletter: {
      title: { en: 'New coffees, once a month', de: 'Neue Kaffees, einmal im Monat' } satisfies L,
      /** jedino obavezno polje */
      email: { en: 'Email', de: 'E-Mail' } satisfies L,
      /** kućica, nije unapred štiklirana; tekst saglasnosti proverava klijent */
      consent: {
        en: "Yes, I'd like to get the newsletter. I can unsubscribe at any time. More in the privacy policy.",
        de: 'Ja, ich möchte den Newsletter bekommen. Ich kann mich jederzeit abmelden. Mehr dazu im Datenschutz.',
      } satisfies L,
      button: { en: 'Sign up', de: 'Anmelden' } satisfies L,
      /** demo red; isto je i poruka posle ispravne prijave (nema mrežnog zahteva) */
      demo: { en: 'Demo: nothing is sent.', de: 'Demo: Es wird nichts verschickt.' } satisfies L,
      /** PREDLOG (nema u tekstovi.md): poruke greške za aria-describedby, potvrđuje tekstopisac. */
      errors: {
        email: { en: 'Please enter a valid email address.', de: 'Bitte gib eine gültige E-Mail-Adresse ein.' } satisfies L,
        consent: { en: 'Please tick the box to sign up.', de: 'Bitte setz das Häkchen, um dich anzumelden.' } satisfies L,
      },
    },
    copyright: { en: '© 2026 {brand} (Konzept / Concept)', de: '© 2026 {brand} (Konzept / Concept)' } satisfies L,
  },
}
