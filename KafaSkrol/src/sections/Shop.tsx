// STUB iz Z1 (doradu radi Z9): prodavnica „Find your cup" sa filterima, mrežom i blokom o dostavi.
import { ProductCard } from '../components/ProductCard'
import { products } from '../content/products'
import { shop } from '../content/shop'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'

export function Shop() {
  const { tx } = useLang()
  return (
    <section id="find-your-cup" aria-labelledby="t-shop" className="scroll-mt-header bg-bg px-gutter py-s9 text-text">
      <h2 id="t-shop" className="type-display m-0 text-h2 leading-none">{tx(shop.title)}</h2>
      <p className="mt-s3 max-w-[34rem] text-muted">{tx(shop.subtitle)}</p>
      <p className="text-small text-muted">{tx(site.demo)}</p>
      <div className="mt-s6 grid grid-cols-2 gap-s4 lg:grid-cols-3">
        {products.map((p) => (
          <ProductCard key={p.slug} product={p} />
        ))}
      </div>
    </section>
  )
}
