// Pretplata i Probierset (skica: sekcija 8, „jedan red"; telefon: dve kartice jedna ispod druge).
// #subscription: dve opcije, uslovi, poklon (3/6/12) i dva demo dugmeta. Klik ne šalje ništa, nego
// menja demo red ispod dugmadi u poruku iz sadržaja (role="status"), jer globalni Toast zna samo „added".
// #tasting-set: opis i cena seta (400 g) i „Add tasting set" (addToCart sam prikazuje toast).
// Sve cene se računaju iz centi (format.ts): oznake {price} {was} {unit} {shipping} {p3} {p6} {p12}.
import { Fragment, useState, type ReactNode } from 'react'
import { Button } from '../components/Button'
import { fill } from '../config/site'
import { productBySlug } from '../content/products'
import { giftPriceCents, sections, subscriptionPriceCents } from '../content/sections'
import { shop } from '../content/shop'
import { useLang } from '../i18n/LangContext'
import { addToCart } from '../lib/cart'
import { formatPrice, formatUnitPrice, NBSP } from '../lib/format'
import { useReveal } from '../lib/reveal'
import './sections.css'

const sub = sections.subscription
const set = sections.tastingSet

/** Primer „Your coffee" (On Repeat 250 g) i pakovanje seta (400 g), iz products.ts. */
const exampleCents = productBySlug(sub.example.product)?.sizes.find((s) => s.grams === sub.example.grams)?.priceCents ?? null
const setSize = productBySlug(set.product)?.sizes[0] ?? null

/** Tekst sa oznakama {key}: oznake iz `nodes` postaju React čvorovi, ostale menja fill() ({brand}…). */
function withNodes(text: string, nodes: Record<string, ReactNode>): ReactNode[] {
  return text.split(/(\{\w+\})/g).map((part, i) => {
    const key = /^\{(\w+)\}$/.exec(part)?.[1]
    if (key && key in nodes) return <Fragment key={i}>{nodes[key]}</Fragment>
    return fill(part)
  })
}

const strong = (text: string) => <strong className="whitespace-nowrap font-extrabold">{text}</strong>
const nowrap = (text: string) => <span className="whitespace-nowrap">{text}</span>

type Notice = 'start' | 'gift' | null

export function Subscription() {
  const { lang, tx } = useLang()
  const reveal = useReveal<HTMLDivElement>()
  const [notice, setNotice] = useState<Notice>(null)
  const price = (cents: number) => formatPrice(cents, lang)

  const optionNodes: Record<(typeof sub.options)[number]['id'], Record<string, ReactNode>> = {
    yours:
      exampleCents === null
        ? {}
        : {
            price: strong(price(subscriptionPriceCents(exampleCents))),
            was: nowrap(price(exampleCents)),
            unit: nowrap(formatUnitPrice(subscriptionPriceCents(exampleCents), sub.example.grams, lang)),
          },
    surprise: {
      price: strong(price(sub.surprise.priceCents)),
      unit: nowrap(formatUnitPrice(sub.surprise.priceCents, sub.surprise.grams, lang)),
      shipping: nowrap(price(shop.shipping.feeCents)),
    },
  }

  return (
    <section id="subscription" aria-labelledby="t-subscription" className="scroll-mt-header bg-bg px-gutter py-s8 text-text md:py-s9">
      <div ref={reveal} className="mx-auto grid max-w-site items-start gap-s5 lg:grid-cols-[7fr_5fr] lg:gap-s6">
        {/* ---------- Pretplata ---------- */}
        <article data-reveal className="rounded-card bg-surface p-s5 shadow-soft md:p-s6">
          <h2 id="t-subscription" className="type-display m-0 text-h2 leading-none">{tx(sub.title)}</h2>
          <p className="mt-s3 mb-0 font-bold">{tx(sub.subtitle)}</p>

          <ul className="mt-s5 mb-0 grid list-none gap-s4 p-0 md:grid-cols-2">
            {sub.options.map((option) => (
              <li key={option.id} className="rounded-md border border-line p-s4">
                <h3 className="m-0 flex flex-wrap items-center gap-s2 text-h3 font-extrabold">
                  {tx(option.title)}
                  {option.id === 'yours' && (
                    // isti broj stoji u tekstu opcije („You save 10 %"), pa je čip samo ukras
                    <span aria-hidden="true" className="rounded-pill border border-accent-text px-s2 py-[3px] font-label text-label leading-none font-bold text-accent-text">
                      −{sub.discountPercent}{NBSP}%
                    </span>
                  )}
                </h3>
                <p className="mt-s2 mb-0 text-small">{withNodes(tx(option.text), optionNodes[option.id])}</p>
              </li>
            ))}
          </ul>

          <p className="mt-s4 mb-0 text-small text-muted">{tx(sub.terms)}</p>
          <p className="mt-s3 mb-0 text-small">
            {withNodes(tx(sub.gift.text), {
              p3: strong(price(giftPriceCents(3))),
              p6: strong(price(giftPriceCents(6))),
              p12: strong(price(giftPriceCents(12))),
            })}
          </p>

          <div className="mt-s5 flex flex-wrap items-center gap-s3">
            <Button onClick={() => setNotice('start')}>{tx(sub.buttons.start)}</Button>
            <Button variant="outline" onClick={() => setNotice('gift')}>
              {tx(sub.buttons.gift)}
            </Button>
          </div>
          {/* demo red; posle klika ista linija kaže da ništa nije naručeno (čita se preko role="status") */}
          <p role="status" className={`mt-s3 mb-0 text-small ${notice ? 'font-bold' : 'text-muted'}`}>
            {tx(notice ? sub.toast[notice] : sub.demo)}
          </p>
        </article>

        {/* ---------- Probierset ----------
            id je na omotaču, ne na kartici sa data-reveal: pomeraj od 16 px pre pojavljivanja bi
            pomerio i cilj sidra #tasting-set */}
        <div id="tasting-set" className="scroll-mt-header">
          <article data-reveal aria-labelledby="t-tasting-set" className="rounded-card bg-surface p-s5 shadow-soft md:p-s6">
            <h2 id="t-tasting-set" className="type-display m-0 text-h2 leading-none">
              <span className="md:hidden">{tx(set.titleShort)}</span>
              <span className="max-md:hidden">{tx(set.title)}</span>
            </h2>
            <p className="mt-s3 mb-0 font-bold">{tx(set.subtitle)}</p>
            {setSize && (
              <>
                <p className="mt-s4 mb-0">
                  {withNodes(tx(set.text), {
                    price: <strong className="whitespace-nowrap text-[1.25rem] font-extrabold">{price(setSize.priceCents)}</strong>,
                    unit: nowrap(formatUnitPrice(setSize.priceCents, setSize.grams, lang)),
                  })}
                </p>
                <Button className="mt-s5" onClick={() => addToCart(set.product, setSize.grams, null)}>
                  {tx(set.button)}
                </Button>
              </>
            )}
          </article>
        </div>
      </div>
    </section>
  )
}
