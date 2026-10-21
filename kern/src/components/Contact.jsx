import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useLang } from '../i18n.jsx';
import { SplitReveal, Magnetic, Arrow } from './fx.jsx';
import { scrollToHash } from '../hooks/useSmoothScroll.js';

/* Kraj strane: providan presek u kom se 3D znak ponovo slaže oko jezgra */
export function Outro() {
  const { t } = useLang();
  return (
    <section className="outro" id="outro">
      <div className="wrap outro-inner">
        <p className="label"><b>●</b> {t.contact.label}</p>
        <SplitReveal as="h2" className="h-display outro-title" lines={[t.contact.title[0], <span className="serif accent" key="s">{t.contact.title[1]}</span>]} />
        <Magnetic>
          <a className="btn btn-accent" href="#contact" onClick={(e) => { e.preventDefault(); scrollToHash('#contact'); }}>{t.nav.contact}<Arrow /></a>
        </Magnetic>
      </div>
    </section>
  );
}

export default function Contact() {
  const { t } = useLang();
  const c = t.contact;
  const [state, setState] = useState('idle');
  const [type, setType] = useState(0);
  const [error, setError] = useState('');
  const submit = (e) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    if (!f.get('name')?.toString().trim() || !/\S+@\S+\.\S+/.test(f.get('email') || '') || !f.get('message')?.toString().trim()) {
      setError(c.required);
      return;
    }
    setError('');
    setState('sending');
    // pregled: forma još nigde ne šalje (vidi NAPREDAK.md), samo pokazuje potvrdu
    setTimeout(() => setState('done'), 900);
  };
  return (
    <section className="contact section solid" id="contact">
      <div className="wrap contact-grid">
        <div className="contact-side">
          <SplitReveal className="h1" lines={[c.title[0], c.title[1]]} />
          <p className="lead">{c.lead}</p>
        </div>
        <div className="contact-form-wrap">
          <AnimatePresence mode="wait">
            {state !== 'done' ? (
              <motion.form key="form" className="contact-form" onSubmit={submit} noValidate initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -20 }}>
                <div className="field-row">
                  <label className="field"><input name="name" placeholder=" " autoComplete="name" /><span>{c.name}</span></label>
                  <label className="field"><input name="email" type="email" placeholder=" " autoComplete="email" /><span>{c.email}</span></label>
                </div>
                <label className="field"><input name="company" placeholder=" " autoComplete="organization" /><span>{c.company}</span></label>
                <fieldset className="chips">
                  <legend className="label">{c.type}</legend>
                  {c.types.map((tp, i) => (
                    <label key={tp} className={`chip${type === i ? ' is-on' : ''}`}>
                      <input type="radio" name="type" value={tp} checked={type === i} onChange={() => setType(i)} />{tp}
                    </label>
                  ))}
                </fieldset>
                <label className="field"><textarea name="message" rows="4" placeholder=" " /><span>{c.message}</span></label>
                {error && <p className="form-error" role="alert">{error}</p>}
                <Magnetic strength={0.2}>
                  <button className="btn btn-accent" type="submit" disabled={state === 'sending'}>{state === 'sending' ? c.sending : c.send}<Arrow /></button>
                </Magnetic>
              </motion.form>
            ) : (
              <motion.div key="done" className="contact-done" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }} role="status">
                <svg viewBox="0 0 52 52" className="done-check" aria-hidden="true"><circle cx="26" cy="26" r="24" /><path d="M15 27l7 7 15-16" /></svg>
                <h3 className="h2">{c.thanks}</h3>
                <p className="lead">{c.thanksText}</p>
                <button className="btn btn-ghost" type="button" onClick={() => setState('idle')}>{c.again}</button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
