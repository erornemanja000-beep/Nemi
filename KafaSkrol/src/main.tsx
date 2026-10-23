import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// index.css (Tailwind) ide pre App-a: tako se redosled slojeva (theme, base, components, utilities) zada
// pre CSS-a komponenti, pa preflight (base) ne pregazi njihov @layer components
import './index.css'
import App from './App'

// priča meri pozicije od vrha; posle ponovnog učitavanja stranica počinje odozgo (kao RealEstates)
if ('scrollRestoration' in history) history.scrollRestoration = 'manual'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
