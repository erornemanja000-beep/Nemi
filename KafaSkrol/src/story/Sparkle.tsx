// STUB iz Z1 (doradu radi Z7): zvezdica koja treperi (2400 ms), u reduced motion stoji.
import { Icon } from '../components/Icon'

export function Sparkle({ className = '' }: { className?: string }) {
  return <Icon name="sparkle" className={`text-pp-crema ${className}`} />
}
