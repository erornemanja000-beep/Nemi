// STUB iz Z1 (doradu radi Z9): modal proizvoda na /p/:slug, preko početne. Nepoznat slug vodi na /.
import { Link, Navigate, useParams } from 'react-router-dom'
import { Icon } from '../components/Icon'
import { buttonClass } from '../components/Button'
import { products } from '../content/products'
import { site } from '../content/site'
import { useLang } from '../i18n/LangContext'

export default function ProductModal() {
  const { slug } = useParams()
  const { tx } = useLang()
  const product = products.find((p) => p.slug === slug)
  if (!product) return <Navigate to="/" replace />
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="product-title" className="fixed inset-0 z-(--z-chat) grid place-items-center bg-[rgb(27_21_13/.5)] p-gutter" data-lenis-prevent>
      <div className="w-[min(100%,40rem)] rounded-card bg-surface p-s6 text-text shadow-float">
        <div className="flex justify-end">
          <Link to="/" aria-label={tx(site.aria.close)} className={buttonClass('icon')}>
            <Icon name="close" />
          </Link>
        </div>
        <h2 id="product-title" className="type-display m-0 text-h2 leading-none">{tx(product.name)}</h2>
        <p>{tx(product.description)}</p>
      </div>
    </div>
  )
}
