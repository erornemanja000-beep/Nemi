// Kontakt (skica: sekcija 10). Levo naslov, podnaslov, demo adresa, telefon i e-mail, radno vreme,
// dani prženja, cupping, adresa za firme i dugme „Write to us" (mailto). Desno apstraktna „mapa"
// (SVG, aria-hidden, bez pravih ulica i podataka) i KONTAKT-1 sa čipom „Symbolbild" i natpisom.
// Sve je izmišljeno za demo (sections.ts). Telefon i e-mail su samo u src/config/site.ts.
// Telefon: tekst, pa mapa, pa fotografija.
import { Button } from '../components/Button'
import { Photo } from '../components/Photo'
import { brand, fill } from '../config/site'
import { media } from '../content/media'
import { sections } from '../content/sections'
import { useLang } from '../i18n/LangContext'
import './sections.css'

const contact = sections.contact
const photo = media.photos[contact.photo]

const link = 'inline-flex min-h-tap items-center underline underline-offset-[3px] hover:text-accent-text'

/** Apstraktna mapa četvrti: blokovi, ulice i oznaka mesta. Ukras, ne nosi informaciju (adresa je u tekstu). */
function ContactMap() {
  return (
    <div aria-hidden="true" className="ct-map aspect-[4/3] md:aspect-[4/5]">
      <svg viewBox="0 0 400 500" preserveAspectRatio="xMidYMid slice" focusable="false">
        {/* blokovi */}
        <path className="ct-map__block" d="M-10 -10h130l-18 120H-10z" />
        <path className="ct-map__block" d="M150 -10h110l-12 112H134z" />
        <path className="ct-map__block" d="M290 -10h120v132H276z" />
        <path className="ct-map__block" d="M-10 140h106l-14 110H-10z" />
        <path className="ct-map__green" d="M128 132h116l-10 96H116z" />
        <path className="ct-map__block" d="M272 152h138v104H262z" />
        <path className="ct-map__block" d="M-10 282h94l-12 98H-10z" />
        <path className="ct-map__block" d="M112 258h118l-10 118H98z" />
        <path className="ct-map__block" d="M258 286h152v94H250z" />
        <path className="ct-map__block" d="M-10 410h76l-8 100H-10z" />
        <path className="ct-map__block" d="M94 406h120l-6 104H86z" />
        <path className="ct-map__block" d="M240 410h170v100H234z" />
        {/* ulice: široka (gore levo → dole desno) i dve poprečne */}
        <path className="ct-map__edge" strokeWidth="30" d="M-20 236C110 250 240 266 420 270" />
        <path className="ct-map__street" strokeWidth="26" d="M-20 236C110 250 240 266 420 270" />
        <path className="ct-map__street" strokeWidth="14" d="M136 -20 96 520" />
        <path className="ct-map__street" strokeWidth="14" d="M270 -20 240 520" />
        <path className="ct-map__street" strokeWidth="10" d="M-20 124 420 140" />
        <path className="ct-map__street" strokeWidth="10" d="M-20 394 420 398" />
        {/* oznaka mesta */}
        <circle className="ct-map__halo" cx="182" cy="350" r="34" />
        <path className="ct-map__pin" d="M182 366c-15-18-24-31-24-43a24 24 0 0 1 48 0c0 12-9 25-24 43Z" />
        <circle className="ct-map__pin-dot" cx="182" cy="323" r="8" />
      </svg>
    </div>
  )
}

export function Contact() {
  const { tx } = useLang()
  const email = fill(contact.email)
  const phone = fill(contact.phone.value)
  // „For offices and restaurants: {wholesale}": adresa je link
  const [wholesaleBefore, wholesaleAfter = ''] = tx(contact.wholesale).split('{wholesale}')

  return (
    <section id="contact" aria-labelledby="t-contact" className="scroll-mt-header bg-surface px-gutter py-s8 text-text md:py-s9">
      <div className="mx-auto grid max-w-site gap-s7 lg:grid-cols-[5fr_6fr] lg:gap-s8">
        <div>
          <h2 id="t-contact" className="type-display m-0 text-h2 leading-none">{tx(contact.title)}</h2>
          <p className="mt-s3 mb-0 font-bold">{tx(contact.subtitle)}</p>

          <address className="mt-s5 not-italic">
            <p className="m-0">
              {contact.address.line} <span className="text-small text-muted">{tx(contact.address.note)}</span>
            </p>
            <p className="m-0 flex flex-wrap items-center gap-x-s4">
              <span>
                <a href={brand.phoneHref} className={link}>
                  {phone}
                </a>{' '}
                <span className="text-small text-muted">{tx(contact.phone.note)}</span>
              </span>
              <a href={`mailto:${email}`} className={link}>
                {email}
              </a>
            </p>
          </address>

          <h3 className="type-eyebrow mt-s6 mb-0">{tx(contact.hours.label)}</h3>
          <dl className="mt-s3 mb-0 max-w-[26rem]">
            {contact.hours.rows.map((row) => (
              <div key={row.days.en} className="flex justify-between gap-s4 border-t border-line-strong py-s2">
                <dt>{tx(row.days)}</dt>
                <dd className="m-0 text-right font-bold">{tx(row.time)}</dd>
              </div>
            ))}
          </dl>

          <p className="mt-s5 mb-0 md:text-small">{tx(contact.roasting)}</p>
          <p className="mt-s2 mb-0 md:text-small">
            <strong>{tx(contact.cuppingLabel)}:</strong> {tx(contact.cupping)}
          </p>
          <p className="mt-s1 mb-s5 md:text-small">
            {wholesaleBefore}
            <a href={`mailto:${brand.wholesale}`} className={link}>
              {brand.wholesale}
            </a>
            {wholesaleAfter}
          </p>
          <Button href={fill(contact.cta.href)}>{tx(contact.cta.label)}</Button>
        </div>

        <div className="grid content-start gap-s5 md:grid-cols-2 md:gap-s4">
          <ContactMap />
          {photo && (
            <figure className="m-0">
              <div className="relative">
                <Photo
                  id={photo.id}
                  sizes="(min-width: 64rem) 24vw, (min-width: 48rem) 45vw, 100vw"
                  className="block aspect-[4/5] h-auto w-full rounded-card object-cover"
                />
                {photo.caption && (
                  // isti natpis je na početku figcaption-a, pa čitač čita samo njega
                  <span aria-hidden="true" className="type-label absolute top-s3 left-s3 rounded-pill bg-btn px-s3 py-s2 text-btn-text">
                    {tx(photo.caption)}
                  </span>
                )}
              </div>
              <figcaption className="mt-s2 text-small text-muted">{tx(contact.photoCaption)}</figcaption>
            </figure>
          )}
        </div>
      </div>
    </section>
  )
}
