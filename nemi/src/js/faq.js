/* ---------- faq ---------- */
$('#qa').addEventListener('click', (e) => {
  const q = e.target.closest('.qa-q'); if (!q) return;
  const li = q.closest('li'), open = !li.classList.contains('open');
  li.classList.toggle('open', open); q.setAttribute('aria-expanded', open);
  setTimeout(() => hasG && ScrollTrigger.refresh(), 520);
});
