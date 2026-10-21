// Everything a visitor reads comes from public/content.json, so the site can be
// re-branded for a client without touching code. This file only turns it into HTML.

export type Villa = {
  id: 'kyma' | 'lefka' | 'pefko' | 'selene'
  name: string
  location: string
  year: string
  status: string
  area: string
  bedrooms: string
  plot: string
  summary: string
}

export type Content = {
  brand: { name: string; descriptor: string; established: string; region: string }
  nav: { label: string; target: string }[]
  cta: string
  intro: {
    eyebrow: string
    lead: string
    scrollHint: string
    plotLabel: string
    plotCoordinates: string
    plotLine: string
    buildFrom: number
    buildTo: number
  }
  villas: Villa[]
  manifesto: { label: string; before: string; accent: string; after: string; columns: { title: string; text: string }[] }
  index: { label: string; title: string }
  process: { label: string; title: string; steps: { title: string; text: string; duration: string }[] }
  plan: { label: string; title: string; stats: { value: number; suffix: string; label: string }[] }
  contact: {
    label: string
    title: string
    text: string
    email: string
    phone: string
    address: string
    formTitle: string
    formFields: { name: string; email: string; message: string }
    formButton: string
    formThanks: string
  }
  footer: { note: string }
}

/** Still images per villa id: the hover preview in the list and the poster before frames load. */
export const VILLA_IMAGE: Record<Villa['id'], string> = {
  kyma: './media/img/kyma',
  lefka: './media/img/lefka',
  pefko: './media/img/pefko',
  selene: './media/img/selene',
}

export async function loadContent(): Promise<Content> {
  const res = await fetch('./content.json', { cache: 'no-cache' })
  return res.json()
}

const esc = (s: string | number) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]!)

const pad = (n: number) => String(n).padStart(2, '0')

/** Splits text into masked lines/words so titles can slide up out of a clip. */
const maskedWords = (text: string) =>
  text
    .split(/\s+/)
    .map((w) => `<span class="mask"><span class="mask__in">${esc(w)}</span></span>`)
    .join(' ')

function villaTitle(v: Villa, i: number, total: number) {
  return `
    <div class="vt" data-villa="${v.id}">
      <p class="vt__index mono"><span class="vt__num">${pad(i + 1)}</span> / ${pad(total)} &nbsp;—&nbsp; ${esc(v.location)}</p>
      <h2 class="vt__name">${v.name
        .split(/\s+/)
        .map((w) => `<span class="mask"><span class="mask__in">${esc(w)}</span></span>`)
        .join('')}</h2>
      <div class="vt__foot">
        <p class="vt__summary">${esc(v.summary)}</p>
        <ul class="vt__meta mono">
          <li>${esc(v.year)}</li><li>${esc(v.area)}</li><li>${esc(v.bedrooms)}</li><li>${esc(v.status)}</li>
        </ul>
      </div>
    </div>`
}

export function render(c: Content): string {
  const [kyma, ...rest] = c.villas
  const total = c.villas.length
  const year = new Date().getFullYear()

  return `
  <div class="loader" id="loader" aria-hidden="true">
    <div class="loader__mark">${esc(c.brand.name)}</div>
    <div class="loader__foot mono">
      <span>${esc(c.brand.descriptor)} · ${esc(c.brand.region)}</span>
      <span><span id="loader-pct">0</span>%</span>
    </div>
    <div class="loader__bar"><i id="loader-bar"></i></div>
  </div>

  <header class="hdr" id="hdr">
    <a class="hdr__logo" href="#top" aria-label="${esc(c.brand.name)} home">${esc(c.brand.name)}</a>
    <nav class="hdr__nav" aria-label="Main">
      ${c.nav.map((n) => `<a href="${esc(n.target)}">${esc(n.label)}</a>`).join('')}
    </nav>
    <a class="hdr__cta" href="#contact">${esc(c.cta)}<span aria-hidden="true">↗</span></a>
  </header>

  <aside class="rail mono" aria-hidden="true">
    <span class="rail__label">${esc(c.brand.established)}</span>
    <span class="rail__track"><i id="rail-fill"></i></span>
    <span class="rail__label" id="rail-pct">00</span>
  </aside>

  <main>
    <section class="stage stage--arrival" id="top" aria-label="Arrival">
      <div class="stage__sticky">
        <canvas class="stage__canvas" id="cv-arrival"></canvas>
        <div class="shade shade--top"></div>
        <div class="shade shade--bottom"></div>

        <div class="arrival__intro">
          <p class="eyebrow mono">${esc(c.intro.eyebrow)}</p>
          <p class="arrival__lead">${esc(c.intro.lead)}</p>
        </div>
        <h1 class="arrival__mark" data-fit>${esc(c.brand.name)}</h1>
        <p class="arrival__hint mono">${esc(c.intro.scrollHint)}<span class="arrival__hint-line"></span></p>

        <div class="arrival__plot">
          <p class="mono"><span class="pin"></span>${esc(c.intro.plotLabel)} &nbsp;·&nbsp; ${esc(c.intro.plotCoordinates)}</p>
          <p class="arrival__plotline">${maskedWords(c.intro.plotLine)}</p>
        </div>
        <p class="arrival__build mono">Construction <span id="build-year" data-to="${esc(c.intro.buildTo)}">${esc(c.intro.buildFrom)}</span> → ${esc(c.intro.buildTo)}</p>

        ${villaTitle(kyma, 0, total)}
      </div>
    </section>

    <section class="stage stage--villas" id="villas" aria-label="Villas">
      <div class="stage__sticky">
        ${rest
          .map((v) => `<div class="layer" data-layer="${v.id}"><canvas class="stage__canvas"></canvas></div>`)
          .join('')}
        <div class="shade shade--top"></div>
        <div class="shade shade--bottom"></div>
        ${rest.map((v, i) => villaTitle(v, i + 1, total)).join('')}
        <div class="stage__dim" id="villas-dim"></div>
      </div>
    </section>

    <section class="manifesto" id="atelier">
      <p class="label mono">${esc(c.manifesto.label)}</p>
      <p class="manifesto__text">
        ${c.manifesto.before
          .split(/\s+/)
          .map((w) => `<span class="w">${esc(w)}</span>`)
          .join(' ')}
        <span class="w w--accent">${esc(c.manifesto.accent)}</span>
        ${c.manifesto.after
          .split(/\s+/)
          .map((w) => `<span class="w">${esc(w)}</span>`)
          .join(' ')}
      </p>
      <div class="manifesto__cols">
        ${c.manifesto.columns
          .map(
            (col, i) => `
          <div class="col reveal">
            <p class="mono col__n">${pad(i + 1)}</p>
            <h3>${esc(col.title)}</h3>
            <p>${esc(col.text)}</p>
          </div>`,
          )
          .join('')}
      </div>
    </section>

    <section class="index" id="index">
      <div class="index__head">
        <p class="label mono">${esc(c.index.label)}</p>
        <h2 class="index__title">${maskedWords(c.index.title)}</h2>
      </div>
      <ol class="index__list">
        ${c.villas
          .map(
            (v, i) => `
          <li class="row" data-img="${VILLA_IMAGE[v.id]}-sm.jpg" data-target="${i === 0 ? '#top' : '#villas'}" data-villa-index="${i}">
            <span class="row__n mono">${pad(i + 1)}</span>
            <span class="row__name">${esc(v.name)}</span>
            <span class="row__loc">${esc(v.location)}</span>
            <span class="row__year mono">${esc(v.year)}</span>
            <span class="row__status mono">${esc(v.status)}</span>
            <span class="row__arrow" aria-hidden="true">→</span>
          </li>`,
          )
          .join('')}
      </ol>
      <div class="index__preview" aria-hidden="true"><img alt="" /></div>
    </section>

    <section class="process" id="process">
      <div class="process__media">
        <div class="process__frame">
          <img src="./media/img/model.jpg" alt="Architectural study model of a villa on its terrain" class="is-on" data-step-img="0" />
          <img src="./media/img/detail.jpg" alt="Limestone wall, bronze window frame and linen curtain" data-step-img="2" />
          <img src="./media/img/kyma.jpg" alt="Finished villa above the bay" data-step-img="3" />
        </div>
      </div>
      <div class="process__body">
        <p class="label mono">${esc(c.process.label)}</p>
        <h2 class="process__title">${maskedWords(c.process.title)}</h2>
        <ol class="steps">
          ${c.process.steps
            .map(
              (s, i) => `
            <li class="step" data-step="${i}">
              <p class="step__n mono">${pad(i + 1)}</p>
              <div>
                <h3>${esc(s.title)}</h3>
                <p>${esc(s.text)}</p>
                <p class="step__d mono">${esc(s.duration)}</p>
              </div>
            </li>`,
            )
            .join('')}
        </ol>
      </div>
    </section>

    <section class="stage stage--plan" aria-label="${esc(c.plan.label)}">
      <div class="stage__sticky">
        <canvas class="stage__canvas" id="cv-plan"></canvas>
        <div class="shade shade--full"></div>
        <div class="plan__cross" aria-hidden="true"><i class="plan__h"></i><i class="plan__v"></i><b class="plan__ring"></b></div>
        <div class="plan__copy">
          <p class="label mono">${esc(c.plan.label)}</p>
          <h2 class="plan__title">${maskedWords(c.plan.title)}</h2>
        </div>
        <dl class="plan__stats">
          ${c.plan.stats
            .map(
              (s) => `
            <div class="stat">
              <dt class="mono">${esc(s.label)}</dt>
              <dd><span class="stat__v" data-value="${s.value}">0</span>${esc(s.suffix)}</dd>
            </div>`,
            )
            .join('')}
        </dl>
        <p class="plan__scale mono"><span></span>20 m</p>
      </div>
    </section>

    <section class="contact" id="contact">
      <div class="contact__bg"><img src="./media/img/interior.jpg" alt="" /></div>
      <div class="contact__inner">
        <div class="contact__copy">
          <p class="label mono">${esc(c.contact.label)}</p>
          <h2 class="contact__title">${maskedWords(c.contact.title)}</h2>
          <p class="contact__text">${esc(c.contact.text)}</p>
          <dl class="contact__details">
            <div><dt class="mono">Email</dt><dd><a href="mailto:${esc(c.contact.email)}">${esc(c.contact.email)}</a></dd></div>
            <div><dt class="mono">Phone</dt><dd><a href="tel:${esc(c.contact.phone.replace(/\s+/g, ''))}">${esc(c.contact.phone)}</a></dd></div>
            <div><dt class="mono">Studio</dt><dd>${esc(c.contact.address)}</dd></div>
          </dl>
        </div>
        <form class="form" id="enquiry" novalidate>
          <p class="form__title">${esc(c.contact.formTitle)}</p>
          <label><span class="mono">${esc(c.contact.formFields.name)}</span><input name="name" autocomplete="name" required /></label>
          <label><span class="mono">${esc(c.contact.formFields.email)}</span><input name="email" type="email" autocomplete="email" required /></label>
          <label><span class="mono">${esc(c.contact.formFields.message)}</span><textarea name="message" rows="3"></textarea></label>
          <button type="submit">${esc(c.contact.formButton)}<span aria-hidden="true">→</span></button>
          <p class="form__thanks" role="status" hidden>${esc(c.contact.formThanks)}</p>
        </form>
      </div>
      <footer class="ftr">
        <p class="ftr__mark" data-fit>${esc(c.brand.name)}</p>
        <div class="ftr__row mono">
          <span>© ${year} ${esc(c.brand.name)} · ${esc(c.brand.established)}</span>
          <span>${esc(c.footer.note)}</span>
          <a href="#top">Back to top ↑</a>
        </div>
      </footer>
    </section>
  </main>`
}
