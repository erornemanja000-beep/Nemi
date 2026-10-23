// Zvezdica u SIP-u (mockup .sparkle): treperi 2400 ms (--dur-twinkle), u reduced motion stoji.
// Položaj u sceni je u chapters.css (.ch-stage .sparkle).
import { Icon } from '../components/Icon'
import './chapters.css'

export function Sparkle({ className = '' }: { className?: string }) {
  return (
    <div aria-hidden="true" className={`sparkle ${className}`}>
      <Icon name="sparkle" className="sparkle__icon" />
    </div>
  )
}
