// Zrno filma: fiksni sloj sa statičnim SVG šumom (data-URI, 3–5 %), overlay na desktopu, a na
// telefonu obično mešanje (jeftinije, merenje u izveštaju Z7). Stil je .film-grain u chapters.css.
// Gasi se sa features.grain u src/config/site.ts.
import { features } from '../config/site'
import '../story/chapters.css'

export function Grain() {
  if (!features.grain) return null
  return <div aria-hidden="true" className="film-grain" />
}
