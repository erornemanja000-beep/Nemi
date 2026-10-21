import type { ImgHTMLAttributes } from 'react'
import { img } from '../../lib/img'
import { photos, type PhotoName } from '../../data/photos'

type Props = { name: PhotoName; sizes?: string; eager?: boolean } & Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet' | 'alt'>

export function Img({ name, sizes = '100vw', eager = false, className = '', ...rest }: Props) {
  const portrait = name.startsWith('agent')
  return (
    <img
      {...img(name, portrait)}
      sizes={sizes}
      alt={photos[name].alt}
      loading={eager ? 'eager' : 'lazy'}
      decoding="async"
      className={className}
      {...rest}
    />
  )
}
