// Fotografija iz media.ts: <img srcset sizes> sa width i height (bez skoka rasporeda), lenjo učitana.
// Dok fajl ne postoji (ready: false), crta obojenu kutiju iste razmere i ne šalje zahtev.
import type { ImgHTMLAttributes } from 'react'
import { media } from '../content/media'
import { useLang } from '../i18n/LangContext'

type Props = {
  id: string
  /** npr. „(min-width: 64rem) 40vw, 100vw" */
  sizes?: string
  /** prvi ekran: eager + fetchpriority high */
  priority?: boolean
  className?: string
} & Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet' | 'alt' | 'width' | 'height' | 'sizes' | 'className'>

export function Photo({ id, sizes = '100vw', priority = false, className = '', ...rest }: Props) {
  const { tx } = useLang()
  const photo = media.photos[id]
  if (!photo) return null
  const { sm, lg } = photo
  if (!photo.ready) {
    return (
      <span
        role="img"
        aria-label={tx(photo.alt)}
        className={`block bg-placeholder ${className}`}
        style={{ aspectRatio: `${lg.width} / ${lg.height}` }}
      />
    )
  }
  return (
    <img
      src={lg.src}
      srcSet={`${sm.src} ${sm.width}w, ${lg.src} ${lg.width}w`}
      sizes={sizes}
      width={lg.width}
      height={lg.height}
      alt={tx(photo.alt)}
      loading={priority ? 'eager' : 'lazy'}
      fetchPriority={priority ? 'high' : 'auto'}
      decoding="async"
      className={className}
      {...rest}
    />
  )
}
