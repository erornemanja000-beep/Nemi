// Freiraum – Team-Bereich: Anfragen lesen & bearbeiten
//   GET  (Authorization: Bearer <TEAM_PASSWORD>)            -> { ok, bookings, blocked }
//   POST (Authorization: Bearer ...) { action, id, status, note, date }
//   GET  ?action=confirm|decline&id=..&sig=..  (Link aus der E-Mail, ohne Passwort, HMAC-geprüft)
//        -> kleine Seite mit einem Knopf; erst der Klick (POST) ändert den Status,
//           damit Mail-Scanner/Link-Vorschauen nichts versehentlich bestätigen.
import { getStore } from '@netlify/blobs';
import { createHash, createHmac, timingSafeEqual } from 'node:crypto';

const STATUS = ['neu', 'bestaetigt', 'abgelehnt'];
const ACTION_STATUS = { confirm: 'bestaetigt', decline: 'abgelehnt' };
const BLOCKED = '_blocked';
const DATE = /^\d{4}-\d{2}-\d{2}$/;

const json = (data, status = 200) => Response.json(data, { status });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const sha = (s) => createHash('sha256').update(String(s)).digest();
const same = (a, b) => timingSafeEqual(sha(a), sha(b));
export const sign = (id, action, secret) => createHmac('sha256', secret).update(id + action).digest('hex');
export const verify = (id, action, sig, secret) => !!(secret && id && sig && ACTION_STATUS[action]) && same(sign(id, action, secret), sig);

export function authorized(req) {
  const pw = process.env.TEAM_PASSWORD || 'freiraum2026';
  const m = /^Bearer\s+(.+)$/i.exec(req.headers.get('authorization') || '');
  return !!m && same(m[1].trim(), pw);
}

const store = () => getStore({ name: 'bookings', consistency: 'strong' });

async function listAll(s) {
  const { blobs } = await s.list();
  const keys = blobs.map((b) => b.key).filter((k) => !k.startsWith('_')).sort().reverse(); // Schlüssel beginnen mit Date.now()
  const bookings = (await Promise.all(keys.map((k) => s.get(k, { type: 'json' })))).filter(Boolean);
  const blocked = (await s.get(BLOCKED, { type: 'json' })) || [];
  return { bookings, blocked };
}

async function update(s, id, patch) {
  const b = await s.get(id, { type: 'json' });
  if (!b) return null;
  const next = { ...b, ...patch, updatedAt: new Date().toISOString() };
  await s.setJSON(id, next);
  return next;
}

function page(title, body, tone = '#1f2741') {
  const html = `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>${esc(title)} · Freiraum</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f7f4ee;font-family:Outfit,Helvetica,Arial,sans-serif;color:#1f2741;padding:20px;box-sizing:border-box}
.c{max-width:440px;width:100%;background:#fff;border-radius:24px;padding:34px 28px;text-align:center;box-shadow:0 18px 50px -18px rgba(15,19,32,.35)}
.b{font-size:13px;letter-spacing:.22em;text-transform:uppercase;color:#6b7186}.i{width:64px;height:64px;border-radius:50%;margin:18px auto;display:grid;place-items:center;background:${tone};color:#fff;font-size:30px}
h1{font-weight:600;font-size:26px;margin:0 0 8px}p{color:#5a6075;margin:0 0 6px}button,a.btn{display:inline-block;margin-top:18px;border:0;border-radius:999px;padding:15px 28px;font:inherit;font-weight:600;font-size:16px;background:${tone};color:#fff;text-decoration:none;cursor:pointer}</style></head>
<body><div class="c"><div class="b">frei raum · Team</div>${body}</div></body></html>`;
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

const fmtDate = (d) => (DATE.test(d || '') ? d.split('-').reverse().join('.') : d || '–');
const who = (b) => `${esc(b.child ? `${b.child}${b.age ? ` (${b.age})` : ''} · ` : '')}${esc(b.name || '')}`;

async function emailLink(req, url) {
  const isPost = req.method === 'POST';
  const p = isPost ? new URLSearchParams(await req.text()) : url.searchParams;
  const action = p.get('action'), id = p.get('id') || '', sig = p.get('sig') || '';
  if (!verify(id, action, sig, process.env.TEAM_SECRET)) return page('Link ungültig', '<div class="i">!</div><h1>Link ungültig</h1><p>Bitte im Team-Bereich bearbeiten.</p>', '#8a2433');
  const s = store();
  const b = await s.get(id, { type: 'json' });
  if (!b) return page('Nicht gefunden', '<div class="i">?</div><h1>Anfrage nicht gefunden</h1>', '#8a2433');
  const ok = action === 'confirm', tone = ok ? '#2f8f63' : '#b23a4b';
  const info = `<p><b>${who(b)}</b></p><p>${esc(fmtDate(b.date))}${b.time ? ' · ' + esc(b.time) : ''}${b.guests ? ' · ' + esc(b.guests) + ' Gäste' : ''}</p>`;
  if (!isPost) {
    const form = `<form method="post"><input type="hidden" name="action" value="${esc(action)}"><input type="hidden" name="id" value="${esc(id)}"><input type="hidden" name="sig" value="${esc(sig)}"><button>${ok ? 'Jetzt bestätigen' : 'Jetzt ablehnen'}</button></form>`;
    return page('Anfrage', `<div class="i">${ok ? '✓' : '×'}</div><h1>Anfrage ${ok ? 'bestätigen' : 'ablehnen'}?</h1>${info}${form}`, tone);
  }
  await update(s, id, { status: ACTION_STATUS[action] });
  return page(ok ? 'Bestätigt' : 'Abgelehnt', `<div class="i">${ok ? '✓' : '×'}</div><h1>Anfrage ${ok ? 'bestätigt' : 'abgelehnt'}</h1>${info}<p style="margin-top:12px">Bitte den Gast noch persönlich informieren.</p>`, tone);
}

export default async (req) => {
  const url = new URL(req.url);
  try {
    // Links aus der Benachrichtigungs-Mail
    if (url.searchParams.has('sig') || (req.method === 'POST' && (req.headers.get('content-type') || '').includes('application/x-www-form-urlencoded'))) {
      return await emailLink(req, url);
    }
    if (!['GET', 'POST'].includes(req.method)) return json({ ok: false, error: 'Method not allowed' }, 405);
    if (!authorized(req)) return json({ ok: false, error: 'Nicht angemeldet' }, 401);
    const s = store();
    if (req.method === 'GET') return json({ ok: true, ...(await listAll(s)) });

    let body;
    try { body = await req.json(); } catch { return json({ ok: false, error: 'Ungültiges JSON' }, 400); }
    const { action, id, status, note, date } = body || {};
    if (action === 'status') {
      if (!STATUS.includes(status)) return json({ ok: false, error: 'Status ungültig' }, 400);
      const b = await update(s, String(id || ''), { status });
      return b ? json({ ok: true, booking: b }) : json({ ok: false, error: 'Nicht gefunden' }, 404);
    }
    if (action === 'note') {
      if (typeof note !== 'string' || note.length > 4000) return json({ ok: false, error: 'Notiz ungültig' }, 400);
      const b = await update(s, String(id || ''), { note });
      return b ? json({ ok: true, booking: b }) : json({ ok: false, error: 'Nicht gefunden' }, 404);
    }
    if (action === 'block' || action === 'unblock') {
      if (!DATE.test(date || '')) return json({ ok: false, error: 'Datum ungültig' }, 400);
      const list = new Set((await s.get(BLOCKED, { type: 'json' })) || []);
      action === 'block' ? list.add(date) : list.delete(date);
      const blocked = [...list].sort();
      await s.setJSON(BLOCKED, blocked);
      return json({ ok: true, blocked });
    }
    return json({ ok: false, error: 'Unbekannte Aktion' }, 400);
  } catch (e) {
    console.error(e);
    return json({ ok: false, error: 'Serverfehler' }, 500);
  }
};
