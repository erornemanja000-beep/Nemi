// STUB iz Z1 (doradu radi Z9): kartica proizvoda u prodavnici.
import type { Product } from '../content/types'
import { useLang } from '../i18n/LangContext'
import { Price } from './Price'

type Props = { product: Product }

export function ProductCard({ product }: Props) {
  const { tx } = useLang()
  const size = product.sizes[0]
  const cents = size?.priceCents ?? product.priceCents
  return (
    <article className="rounded-card bg-surface p-s4">
      <h3 className="m-0 text-h3 font-extrabold">{tx(product.name)}</h3>
      <p className="mt-s2 mb-s3 text-small text-muted">{tx(product.description)}</p>
      {cents != null && <Price cents={cents} grams={size?.grams} showGrams={!!size} className="text-muted" amountClassName="text-[1.25rem] font-extrabold text-text" />}
    </article>
  )
}
