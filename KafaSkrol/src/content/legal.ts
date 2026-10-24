// Pravne stranice kao demo stub i stranica Credits (tekstovi.md, Z3 tačke 2 i 3). Sadržaj se ne izmišlja:
// svaka stranica ima isti uvod i spisak onoga što bi stajalo u pravom projektu. Stavka bez teksta i linka
// dobija čip legal.missing („not in demo"); [FEHLT] se na stranici ne prikazuje doslovno.
// Tipovi LegalEntry i LegalPageContent su u types.ts.
import type { L, LegalEntry, LegalPageContent } from './types.ts'
import { asset } from '../config/site.ts'
import { shop } from './shop.ts'

/** Zajedničko za svih šest stranica (Z3 tačka 3). */
export const legal = {
  /** Untertitel / Subtitle; isto je `intro` svake stranice. */
  intro: { en: 'Concept / demo — not a real shop.', de: 'Konzept / Demo — kein echter Shop.' } satisfies L,
  text: {
    en: "In a real shop, this page holds the full legal text. We don't make up legal details, so here you only see what it would cover.",
    de: 'Im echten Shop steht hier der vollständige Rechtstext. Rechtliche Angaben erfinden wir nicht. Hier siehst du nur, was dazugehört.',
  } satisfies L,
  listTitle: { en: 'What goes here', de: 'Was hier hingehört' } satisfies L,
  /** čip uz stavku koje u demou nema */
  missing: { en: 'not in demo', de: 'nicht in der Demo' } satisfies L,
  back: { label: { en: 'Back to the start', de: 'Zurück zur Startseite' } satisfies L, href: '/' },
}

function page(p: Omit<LegalPageContent, 'intro' | 'items'>): LegalPageContent {
  return {
    ...p,
    intro: legal.intro,
    items: { en: p.entries.map((e) => e.title.en), de: p.entries.map((e) => e.title.de) },
  }
}

const t = (en: string, de: string): LegalEntry => ({ title: { en, de } })

export const legalPages: LegalPageContent[] = [
  page({
    slug: 'impressum',
    title: { en: 'Imprint', de: 'Impressum' },
    docTitle: { en: 'Imprint | {brand}', de: 'Impressum | {brand}' },
    entries: [
      t('Company name (as registered)', 'Firma (laut Firmenbuch)'),
      t('Address for service', 'Ladungsfähige Anschrift'),
      t('Email and phone', 'E-Mail und Telefon'),
      t('Company register number and court', 'Firmenbuchnummer und Firmenbuchgericht'),
      t('VAT ID (UID)', 'UID-Nummer'),
      t('Supervisory authority', 'Aufsichtsbehörde'),
      t('Chamber membership', 'Kammerzugehörigkeit'),
      t('Applicable rules (Trade Regulation Act, GewO)', 'Anwendbare Rechtsvorschriften (GewO)'),
      t('Disclosure under § 25 Media Act', 'Offenlegung nach § 25 MedienG'),
      t('Out-of-court dispute resolution', 'Außergerichtliche Streitbeilegung'),
    ],
  }),
  page({
    slug: 'datenschutz',
    title: { en: 'Privacy policy', de: 'Datenschutz' },
    docTitle: { en: 'Privacy policy | {brand}', de: 'Datenschutz | {brand}' },
    // demo red (tačan danas, po planu): forme ne šalju ništa, jezik i korpa ostaju u pregledaču
    body: {
      en: "In this demo, forms don't send anything. Language and cart stay in your browser.",
      de: 'In dieser Demo senden Formulare nichts ab. Sprache und Warenkorb bleiben in deinem Browser.',
    },
    entries: [
      t('Controller', 'Verantwortlicher'),
      t('Purposes of processing', 'Zwecke der Verarbeitung'),
      { title: { en: 'Cookies and local storage', de: 'Cookies und lokale Speicherung' }, href: '/cookies' },
      t('Newsletter and withdrawing consent', 'Newsletter und Widerruf der Einwilligung'),
      t('Your rights', 'Deine Rechte'),
      t('Complaints to the Data Protection Authority', 'Beschwerde bei der Datenschutzbehörde'),
      // [FEHLT: Hosting (Netlify) und Server-Logs] (Z3)
      t('Hosting and server logs', 'Hosting und Server-Logs'),
    ],
  }),
  page({
    slug: 'agb',
    title: { en: 'Terms', de: 'AGB' },
    docTitle: { en: 'Terms | {brand}', de: 'AGB | {brand}' },
    // na 390 px dugačka reč samo u podnaslovu, uz hyphens: auto i lang="de"
    subtitle: { en: 'Terms and conditions', de: 'Allgemeine Geschäftsbedingungen' },
    entries: [
      t('Terms and conditions', 'Allgemeine Geschäftsbedingungen'),
      t('How the contract is made: steps to your order', 'Wie der Vertrag zustande kommt: Schritte bis zur Bestellung'),
      t('Whether the contract text is stored', 'Ob der Vertragstext gespeichert wird'),
      t('Spotting and fixing input errors', 'Eingabefehler erkennen und korrigieren'),
      t('Contract languages', 'Vertragssprachen'),
      t('Subscription: term and cancellation', 'Abo: Laufzeit und Kündigung'),
    ],
  }),
  page({
    slug: 'versand',
    title: { en: 'Shipping & payment', de: 'Versand & Zahlung' },
    docTitle: { en: 'Shipping & payment | {brand}', de: 'Versand & Zahlung | {brand}' },
    entries: [
      // demo tekst iz prodavnice (tekstovi.md, „Dostava")
      { title: { en: 'Shipping in Austria', de: 'Versand in Österreich' }, text: shop.shippingInfo.parts.delivery },
      { title: { en: 'Pickup at the café', de: 'Abholung im Café' }, text: shop.shippingInfo.parts.pickup },
      // [FEHLT: Zahlungsarten], [FEHLT: Versand nach Deutschland & EU]; u pravom projektu ne smeju biti prazni (FAGG § 8 Abs 3)
      t('Payment methods', 'Zahlungsarten'),
      t('Shipping to Germany and the EU', 'Versand nach Deutschland & in die EU'),
    ],
  }),
  page({
    slug: 'widerruf',
    title: { en: 'Right of withdrawal', de: 'Widerrufsrecht' },
    docTitle: { en: 'Right of withdrawal | {brand}', de: 'Widerrufsrecht | {brand}' },
    entries: [
      t('Withdrawal information', 'Widerrufsbelehrung'),
      t('Model withdrawal form (unchanged)', 'Muster-Widerrufsformular (unverändert)'),
      t('Exceptions', 'Ausnahmen'),
      {
        // cilj dugmeta „Vertrag widerrufen" iz footera
        title: { en: 'Withdraw online', de: 'Online widerrufen' },
        text: {
          en: "Demo: there's no contract here to withdraw from. In a real shop, you'd fill in your withdrawal here and send it.",
          de: 'Demo: Hier gibt es keinen Vertrag zum Widerrufen. Im echten Shop füllst du hier deinen Widerruf aus und schickst ihn ab.',
        },
        // onemogućeno dugme; obe formulacije su NEPROVERENE na EUR-Lex-u (Direktiva 2011/83/EU, čl. 11a(3); Z3 tačka 6)
        action: { en: 'Confirm withdrawal', de: 'Widerruf bestätigen' },
      },
    ],
  }),
  page({
    slug: 'cookies',
    title: { en: 'Cookies', de: 'Cookies' },
    docTitle: { en: 'Cookies | {brand}', de: 'Cookies | {brand}' },
    // svoj tekst umesto zajedničkog legal.text; ključevi moraju da budu isti kao storageKeys u
    // src/config/site.ts (proverava check-content.ts)
    bodyReplacesText: true,
    body: {
      en: "This demo doesn't use cookies. Your language and cart are saved only in your browser (localStorage) and are never sent to us. There are two entries: kafa-lang (language) and kafa-cart (cart). To remove them, clear this site's data in your browser.",
      de: 'Diese Demo verwendet keine Cookies. Sprache und Warenkorb werden nur in deinem Browser gespeichert (localStorage) und nicht an uns geschickt. Es sind zwei Einträge: kafa-lang (Sprache) und kafa-cart (Warenkorb). Löschen kannst du sie, indem du die Websitedaten dieser Seite in deinem Browser löschst.',
    },
    entries: [
      t('Cookie list and consent, if payment or other services are added', 'Cookie-Liste und Einwilligung, falls Zahlungs- oder andere Dienste dazukommen'),
    ],
  }),
]

/**
 * Stranica /credits (Z3 tačka 2). Autor, link i licenca fotografija su u media.ts (photo.credit),
 * a snimka pare u media.ts (steamCredit). Ovde su natpisi i opis svake fotografije po jeziku.
 */
export const credits = {
  title: { en: 'Credits & licenses', de: 'Quellen & Lizenzen' } satisfies L,
  /** link u footeru */
  link: { en: 'Credits', de: 'Quellen & Lizenzen' } satisfies L,
  docTitle: { en: 'Credits & licenses | {brand}', de: 'Quellen & Lizenzen | {brand}' } satisfies L,
  subtitle: {
    en: 'Who made the photos, video and fonts.',
    de: 'Wer die Fotos, das Video und die Schriften gemacht hat.',
  } satisfies L,
  text: {
    en: "Photos, video and fonts on this concept site come from free sources. The photo and video licenses don't ask for credit, but we give it anyway. The fonts are under the SIL Open Font License, and the license texts are linked below.",
    de: 'Fotos, Video und Schriften auf dieser Konzeptseite stammen aus freien Quellen. Für Fotos und Video verlangen die Lizenzen keine Nennung, wir nennen sie trotzdem. Die Schriften stehen unter der SIL Open Font License, die Lizenztexte findest du unten.',
  } satisfies L,
  back: legal.back,
  columns: {
    photo: { en: 'Photo', de: 'Foto' } satisfies L,
    author: { en: 'Author', de: 'Urheber' } satisfies L,
    source: { en: 'Source', de: 'Quelle' } satisfies L,
    license: { en: 'License', de: 'Lizenz' } satisfies L,
    /** opciona kolona */
    usedIn: { en: 'Used in', de: 'Verwendet in' } satisfies L,
  },
  /** napomena iznad tabele */
  note: {
    en: 'All photos are color-adjusted for this site, some are cropped.',
    de: 'Alle Fotos sind für diese Seite farblich angepasst, manche zugeschnitten.',
  } satisfies L,
  /** Redovi tabele po id-ju fotografije iz media.photos; link u koloni „Source" je photo.credit.url. */
  photos: {
    'shop-1': {
      photo: { en: 'Coffee beans in glass jars', de: 'Kaffeebohnen in Gläsern' },
      usedIn: { en: 'Shop', de: 'Shop' },
      source: 'Unsplash',
    },
    'shop-bg-1': {
      photo: { en: 'Heap of coffee beans', de: 'Häufchen Kaffeebohnen' },
      usedIn: { en: 'Shop background', de: 'Shop-Hintergrund' },
      source: 'Unsplash',
    },
    'shop-bg-2': {
      photo: { en: 'Scattered coffee beans', de: 'Verstreute Kaffeebohnen' },
      usedIn: { en: 'Shop background', de: 'Shop-Hintergrund' },
      source: 'Unsplash',
    },
    'onama-1': {
      photo: { en: "Beans in a roaster's cooling tray", de: 'Bohnen im Kühlsieb' },
      usedIn: { en: 'About', de: 'Über uns' },
      source: 'Unsplash',
    },
    'onama-2': {
      photo: { en: 'Stirring arm in roasted beans', de: 'Rührarm in gerösteten Bohnen' },
      usedIn: { en: 'About', de: 'Über uns' },
      source: 'Unsplash',
    },
    'guide-1': {
      photo: { en: 'Beans on a scale', de: 'Bohnen auf der Waage' },
      usedIn: { en: 'Brew guide, step 1', de: 'Zubereitung, Schritt 1' },
      source: 'Unsplash',
    },
    'guide-2': {
      photo: { en: 'Dripper on a scale', de: 'Handfilter auf der Waage' },
      usedIn: { en: 'Brew guide, step 2', de: 'Zubereitung, Schritt 2' },
      source: 'Unsplash',
    },
    'kontakt-1': {
      photo: { en: 'Café courtyard in Vienna (illustrative photo)', de: 'Gastgarten in Wien (Symbolbild)' },
      usedIn: { en: 'Visit', de: 'Kontakt' },
      source: 'Pexels',
    },
  } satisfies Record<string, { photo: L; usedIn: L; source: string }>,
  /**
   * Dodatak koloni „Used in" za fotografiju koja privremeno stoji u koraku 3 Brew guide-a
   * (sections.brewGuide.sipStandIn); nestaje kad je SIP pravi render.
   */
  standIn: { en: 'Brew guide, step 3 (until the render is in)', de: 'Zubereitung, Schritt 3 (bis das Rendering da ist)' } satisfies L,
  /** Red o snimku pare; autor, originalni naslov (ne prevodi se), link i licenca su media.steamCredit. */
  steam: {
    photo: { en: 'Steam over a cup (video, edited)', de: 'Dampf über einer Tasse (Video, bearbeitet)' } satisfies L,
    usedIn: { en: 'Pour, Sip', de: 'Pour, Sip' } satisfies L,
    source: 'Mixkit',
    note: {
      en: 'Cropped, background removed, looped, no sound.',
      de: 'Zugeschnitten, Hintergrund entfernt, als Endlosschleife, ohne Ton.',
    } satisfies L,
  },
  fonts: {
    text: {
      en: 'Fonts: Archivo, Fraunces and Figtree, under the SIL Open Font License, Version 1.1. © The Archivo Project Authors, The Fraunces Project Authors, The Figtree Project Authors.',
      de: 'Schriften: Archivo, Fraunces und Figtree, unter der SIL Open Font License, Version 1.1. © The Archivo Project Authors, The Fraunces Project Authors, The Figtree Project Authors.',
    } satisfies L,
    /** „License text: Archivo · Fraunces · Figtree" (linkovi su `files`) */
    linksLabel: { en: 'License text:', de: 'Lizenztext:' } satisfies L,
    files: [
      { name: 'Archivo', href: asset('/licenses/OFL-Archivo.txt') },
      { name: 'Fraunces', href: asset('/licenses/OFL-Fraunces.txt') },
      { name: 'Figtree', href: asset('/licenses/OFL-Figtree.txt') },
    ],
  },
  renders: {
    text: {
      en: '3D scenes and coffee bags: our own renders, made in Blender.',
      de: '3D-Szenen und Packungen: eigene Renderings, gemacht mit Blender.',
    } satisfies L,
    /** dodatak dok bilo koji seq.json ima placeholder: true */
    placeholder: {
      en: 'Until the final renders are in, you see placeholders.',
      de: 'Bis die fertigen Renderings da sind, siehst du Platzhalter.',
    } satisfies L,
  },
}
