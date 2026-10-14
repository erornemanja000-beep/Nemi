/* ---------- contact ---------- */
const mailBtn = $('#mailCopy'), mailAddr = $('#mailAddr');
mailBtn.addEventListener('click', () => {
  const done = () => { mailBtn.textContent = '{{Kopiert||Copied}}'; setTimeout(() => { mailBtn.textContent = '{{Kopieren||Copy}}'; }, 1800); };
  const select = () => { const r = document.createRange(); r.selectNodeContents(mailAddr); const s = getSelection(); s.removeAllRanges(); s.addRange(r); };
  if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(mailAddr.textContent).then(done, select);
  else select();
});
const form = $('#brief'), status = $('#formStatus');
const say2 = (msg, cls) => { status.textContent = msg; status.className = 'form-status ' + (cls || ''); };
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (form.website.value) { say2('{{Danke!||Thank you!}}', 'ok'); return; }
  const need = [form.name, form.email, form.message];
  need.forEach((f) => f.classList.toggle('bad', !f.value.trim()));
  const mailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.value.trim());
  form.email.classList.toggle('bad', !mailOk);
  if (need.some((f) => !f.value.trim()) || !mailOk) { say2('{{Bitte fülle Name, eine gültige E-Mail und deine Nachricht aus.||Please fill in your name, a valid email and your message.}}', 'err'); return; }
  const key = form.dataset.web3forms, ep = form.dataset.endpoint;
  if (!key && !ep) { say2('{{Vorschau: Das Formular ist hier noch nicht verbunden. Schreib uns bitte an hallo@nemistudio.at.||Preview: the form isn’t connected here yet. Please email hallo@nemistudio.at.}}'); return; }
  const btn = form.querySelector('[type=submit]'); btn.disabled = true;
  try {
    let res;
    if (key) {
      const fd = new FormData(form); fd.append('access_key', key); fd.append('subject', '{{Neue Anfrage über die Website||New enquiry from the website}}');
      res = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd, headers: { Accept: 'application/json' } });
    } else {
      res = await fetch(ep, { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(new FormData(form)).toString() });
    }
    if (!res.ok) throw new Error(res.status);
    say2('{{Danke! Deine Anfrage ist angekommen. Wir melden uns bald.||Thank you! Your request has arrived. We’ll be in touch soon.}}', 'ok');
    form.reset();
  } catch (err) {
    say2('{{Das hat nicht geklappt. Bitte schreib uns direkt an hallo@nemistudio.at.||That didn’t work. Please email us directly at hallo@nemistudio.at.}}', 'err');
  } finally { btn.disabled = false; }
});
