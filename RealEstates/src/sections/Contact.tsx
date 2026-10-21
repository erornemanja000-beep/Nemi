import { useLayoutEffect, useRef, useState } from 'react'
import { MagneticButton } from '../components/ui/MagneticButton'
import { useLang } from '../i18n/LangContext'
import { gsap, prefersReducedMotion } from '../lib/motion'

type Errors = Partial<Record<'name' | 'email' | 'message', string>>

const field = 'w-full border-b bg-transparent py-4 text-lg outline-none transition-colors placeholder:text-sand-muted/80 focus:border-ember'

export function Contact() {
  const { t } = useLang()
  const root = useRef<HTMLElement>(null)
  const [errors, setErrors] = useState<Errors>({})
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent'>('idle')
  const success = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    if (prefersReducedMotion()) return
    const ctx = gsap.context(() => {
      // the CTA headline grows from small to full width as it scrolls in
      gsap.fromTo('.cta-big', { scale: 0.55, opacity: 0.2 }, { scale: 1, opacity: 1, ease: 'none', scrollTrigger: { trigger: '.cta-big', start: 'top 95%', end: 'top 30%', scrub: 0.6 } })
      gsap.from('.contact-field', { y: 30, opacity: 0, stagger: 0.07, duration: 1, scrollTrigger: { trigger: '.contact-form', start: 'top 85%' } })
    }, root)
    return () => ctx.revert()
  }, [])

  const validate = (d: FormData): Errors => {
    const e: Errors = {}
    if (String(d.get('name') ?? '').trim().length < 2) e.name = t.contact.errors.name
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(d.get('email') ?? '').trim())) e.email = t.contact.errors.email
    if (String(d.get('message') ?? '').trim().length < 10) e.message = t.contact.errors.message
    return e
  }

  const submit = (ev: React.FormEvent<HTMLFormElement>) => {
    ev.preventDefault()
    const form = ev.currentTarget
    const e = validate(new FormData(form))
    setErrors(e)
    const first = Object.keys(e)[0]
    if (first) {
      form.querySelector<HTMLElement>(`[name="${first}"]`)?.focus()
      return
    }
    setStatus('sending')
    // No backend in the demo; on Netlify add `data-netlify="true"` to the form to receive submissions.
    window.setTimeout(() => {
      setStatus('sent')
      form.reset()
      requestAnimationFrame(() => {
        if (!success.current || prefersReducedMotion()) return
        gsap.fromTo(success.current, { clipPath: 'inset(0 100% 0 0)' }, { clipPath: 'inset(0 0% 0 0)', duration: 1.2, ease: 'expo.inOut' })
        gsap.from(success.current.querySelectorAll('.ok-pop'), { y: 30, opacity: 0, stagger: 0.1, delay: 0.5 })
      })
    }, 900)
  }

  const err = (k: keyof Errors) =>
    errors[k] ? (
      <p id={`err-${k}`} role="alert" className="mt-2 text-sm text-ember">
        {errors[k]}
      </p>
    ) : null

  return (
    <section ref={root} id="contact" aria-labelledby="contact-title" className="gutter section-y relative overflow-hidden">
      <div className="breath bottom-[-20%] left-[20%] h-[60vw] w-[60vw] bg-ember/70" />
      <div className="breath right-[-10%] top-[0%] h-[40vw] w-[40vw] bg-dusk" style={{ animationDelay: '-6s' }} />
      <p className="eyebrow relative">{t.contact.eyebrow}</p>
      <h2 id="contact-title" className="cta-big display relative mt-8 origin-left text-[17vw] leading-[0.88] md:text-[11vw]">
        {t.contact.big}
      </h2>
      <div className="relative mt-16 grid gap-12 md:mt-24 md:grid-cols-[1fr_1.4fr] md:gap-[6vw]">
        <p className="max-w-sm text-lg leading-relaxed text-sand/80">{t.contact.lead}</p>
        {status === 'sent' ? (
          <div ref={success} role="status" className="rounded-[2px] bg-sand p-8 text-ink md:p-12">
            <p className="ok-pop font-serif text-6xl">✓</p>
            <p className="ok-pop mt-6 font-serif text-3xl leading-snug md:text-4xl">{t.contact.success}</p>
            <button onClick={() => setStatus('idle')} className="ok-pop mt-8 text-sm underline underline-offset-4">{t.contact.again}</button>
          </div>
        ) : (
          <form name="contact" onSubmit={submit} noValidate className="contact-form grid gap-6 md:grid-cols-2">
            <div className="contact-field">
              <label htmlFor="c-name" className="sr-only">{t.contact.name}</label>
              <input id="c-name" name="name" autoComplete="name" placeholder={t.contact.name} aria-invalid={!!errors.name} aria-describedby={errors.name ? 'err-name' : undefined} className={`${field} ${errors.name ? 'border-ember' : 'border-sand/25'}`} />
              {err('name')}
            </div>
            <div className="contact-field">
              <label htmlFor="c-email" className="sr-only">{t.contact.email}</label>
              <input id="c-email" name="email" type="email" autoComplete="email" placeholder={t.contact.email} aria-invalid={!!errors.email} aria-describedby={errors.email ? 'err-email' : undefined} className={`${field} ${errors.email ? 'border-ember' : 'border-sand/25'}`} />
              {err('email')}
            </div>
            <div className="contact-field">
              <label htmlFor="c-phone" className="sr-only">{t.contact.phone}</label>
              <input id="c-phone" name="phone" type="tel" autoComplete="tel" placeholder={t.contact.phone} className={`${field} border-sand/25`} />
            </div>
            <div className="contact-field">
              <label htmlFor="c-budget" className="sr-only">{t.contact.budget}</label>
              <select id="c-budget" name="budget" defaultValue="" className={`${field} border-sand/25 [color-scheme:dark]`}>
                <option value="" disabled>{t.contact.budget}</option>
                {t.contact.budgets.map((b) => (
                  <option key={b}>{b}</option>
                ))}
              </select>
            </div>
            <div className="contact-field md:col-span-2">
              <label htmlFor="c-message" className="sr-only">{t.contact.message}</label>
              <textarea id="c-message" name="message" rows={3} placeholder={t.contact.message} aria-invalid={!!errors.message} aria-describedby={errors.message ? 'err-message' : undefined} className={`${field} resize-none ${errors.message ? 'border-ember' : 'border-sand/25'}`} />
              {err('message')}
            </div>
            <div className="contact-field md:col-span-2">
              <MagneticButton type="submit" disabled={status === 'sending'}>{status === 'sending' ? t.contact.sending : t.contact.send}</MagneticButton>
            </div>
          </form>
        )}
      </div>
    </section>
  )
}
