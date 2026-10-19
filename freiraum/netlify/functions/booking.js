// Freiraum – neue Anfrage speichern (Kindergeburtstag, Event, Tisch)
// POST /.netlify/functions/booking  { type, name, email|phone, ... }  ->  { ok:true, id }
import { getStore } from '@netlify/blobs';
import { createHmac } from 'node:crypto';

const TYPES = ['kindergeburtstag', 'event', 'tisch'];
const LONG = ['message', 'food', 'wishes', 'allergies', 'nachricht', 'notes'];
const SKIP = ['website', 'privacy', 'datenschutz', 'id', 'status', 'note', 'createdAt'];
const TYPE_LABEL = { kindergeburtstag: 'Kindergeburtstag', event: 'Event', tisch: 'Tisch' };
const LABELS = {
  date: 'Datum', time: 'Uhrzeit', child: 'Geburtstagskind', age: 'Alter wird', kids: 'Kinder', adults: 'Erwachsene',
  guests: 'Gäste', occasion: 'Anlass', motto: 'Motto / Deko', cake: 'Torte', food: 'Essen & Getränke',
  allergies: 'Allergien', message: 'Wünsche / Nachricht', company: 'Firma', name: 'Name', phone: 'Telefon', email: 'E-Mail', consent: 'Datenschutz akzeptiert',
};

const json = (data, status = 200) => Response.json(data, { status });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
export const sign = (id, action, secret) => createHmac('sha256', secret).update(id + action).digest('hex');

/** Prüft und bereinigt die Eingabe. Gibt { error } oder { data } zurück. */
export function validate(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) return { error: 'Ungültige Daten' };
  if (input.website) return { error: 'Spam' }; // Honeypot muss leer bleiben
  if (!TYPES.includes(input.type)) return { error: 'Unbekannter Anfrage-Typ' };
  const keys = Object.keys(input);
  if (keys.length > 40) return { error: 'Zu viele Felder' };
  const data = {};
  for (const k of keys) {
    if (SKIP.includes(k) || !/^[a-zA-Z][\w-]{0,39}$/.test(k)) continue;
    let v = input[k];
    if (typeof v === 'number' || typeof v === 'boolean') v = String(v);
    if (typeof v !== 'string') continue;
    v = v.trim();
    if (v.length > (LONG.includes(k) ? 2000 : 200)) return { error: `Feld „${k}“ ist zu lang` };
    if (v) data[k] = v;
  }
  if (!data.name || data.name.length < 2) return { error: 'Bitte Namen angeben' };
  if (!data.email && !data.phone) return { error: 'Bitte E-Mail oder Telefon angeben' };
  if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) return { error: 'E-Mail ungültig' };
  if (data.phone && !/^[\d\s+()/.-]{6,30}$/.test(data.phone)) return { error: 'Telefonnummer ungültig' };
  if (data.date && !/^\d{4}-\d{2}-\d{2}$/.test(data.date)) return { error: 'Datum ungültig' };
  if (!data.guests && (data.kids || data.adults)) data.guests = String((+data.kids || 0) + (+data.adults || 0));
  if (input.privacy || input.datenschutz) data.consent = 'ja';
  return { data };
}

function fmtDate(d) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d || '');
  return m ? `${m[3]}.${m[2]}.${m[1]}` : d || '–';
}

/** Gleiche Gestaltung wie die „E-Mail-Vorschau“ in team.html */
export function emailHtml(b, links) {
  const rows = Object.entries(b)
    .filter(([k]) => !['id', 'type', 'status', 'note', 'createdAt', 'sentAt', 'lang', 'blockedDate'].includes(k))
    .map(([k, v]) => `<tr><td style="padding:8px 0;color:#6b7186;font-size:13px;width:38%;vertical-align:top">${esc(LABELS[k] || k)}</td><td style="padding:8px 0;font-size:15px;color:#1f2741;white-space:pre-wrap">${esc(k === 'date' ? fmtDate(v) : v)}</td></tr>`)
    .join('');
  const btn = (href, label, bg, fg) => `<a href="${esc(href)}" style="display:inline-block;padding:16px 30px;border-radius:999px;background:${bg};color:${fg};font-weight:700;font-size:16px;text-decoration:none;margin:6px">${label}</a>`;
  const actions = links
    ? `<div style="text-align:center;padding:0 0 14px;border-bottom:1px solid #eee9df;margin-bottom:8px">${btn(links.confirm, 'Bestätigen', '#1f2741', '#ffffff')}${btn(links.decline, 'Ablehnen', '#fde2e4', '#8a2433')}</div>`
    : `<p style="text-align:center;color:#6b7186;font-size:13px;margin:0 0 12px">Bestätigen oder ablehnen im Team-Bereich (team.html).</p>`;
  return `<!doctype html><html lang="de"><body style="margin:0;background:#f7f4ee;font-family:Helvetica,Arial,sans-serif">
<div style="max-width:560px;margin:0 auto;padding:28px 16px">
  <div style="background:#1f2741;color:#fff;border-radius:20px 20px 0 0;padding:26px 28px">
    <div style="font-size:12px;letter-spacing:.2em;text-transform:uppercase;opacity:.65">Neue Anfrage · Website</div>
    <div style="font-size:26px;font-weight:700;margin-top:6px">${esc(TYPE_LABEL[b.type] || b.type)} · ${esc(fmtDate(b.date))}</div>
    <div style="font-size:15px;opacity:.85;margin-top:4px">${esc(b.name || '')}${b.guests ? ' · ' + esc(b.guests) + ' Gäste' : ''}</div>
  </div>
  <div style="background:#fff;border-radius:0 0 20px 20px;padding:22px 28px 26px">
    ${actions}<table style="width:100%;border-collapse:collapse">${rows}</table>
  </div>
  <p style="text-align:center;color:#8a8f9f;font-size:12px;margin-top:18px">Freiraum · Mariahilfer Straße 117 · 1060 Wien</p>
</div></body></html>`;
}

async function notify(b) {
  const { RESEND_API_KEY, NOTIFY_TO, NOTIFY_FROM, TEAM_SECRET, URL: SITE } = process.env;
  if (!RESEND_API_KEY || !NOTIFY_TO) return; // nicht eingerichtet -> still überspringen
  const base = `${SITE || ''}/.netlify/functions/team`;
  const link = (a) => `${base}?action=${a}&id=${encodeURIComponent(b.id)}&sig=${sign(b.id, a, TEAM_SECRET)}`;
  const links = TEAM_SECRET ? { confirm: link('confirm'), decline: link('decline') } : null;
  const subject = `Neue Anfrage: ${TYPE_LABEL[b.type]} · ${fmtDate(b.date)} · ${b.child ? `${b.child}${b.age ? ` (${b.age})` : ''}` : b.name}`;
  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: NOTIFY_FROM || 'Freiraum Website <onboarding@resend.dev>',
        to: NOTIFY_TO.split(',').map((s) => s.trim()),
        reply_to: b.email || undefined,
        subject,
        html: emailHtml(b, links),
      }),
    });
  } catch (e) {
    console.error('Resend fehlgeschlagen', e);
  }
}

export default async (req) => {
  if (req.method !== 'POST') return json({ ok: false, error: 'Method not allowed' }, 405);
  const raw = await req.text();
  if (raw.length > 20000) return json({ ok: false, error: 'Zu groß' }, 400);
  let input;
  try { input = JSON.parse(raw); } catch { return json({ ok: false, error: 'Ungültiges JSON' }, 400); }
  const { error, data } = validate(input);
  if (error) return json({ ok: false, error }, 400);

  try {
    const store = getStore({ name: 'bookings', consistency: 'strong' });
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const blocked = (await store.get('_blocked', { type: 'json' })) || [];
    const booking = { id, ...data, status: 'neu', note: '', createdAt: new Date().toISOString() };
    if (data.date && blocked.includes(data.date)) booking.blockedDate = true;
    await store.setJSON(id, booking);
    await notify(booking);
    return json({ ok: true, id });
  } catch (e) {
    console.error(e);
    return json({ ok: false, error: 'Speichern fehlgeschlagen' }, 500);
  }
};
