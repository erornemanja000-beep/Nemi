/* ---------- process stack ---------- */
if (hasG && !RM) {
  const cards = $$('.proc-card');
  cards.forEach((card, i) => {
    if (i === cards.length - 1) return;
    G.to(card, { scale: .93, ease: 'none', scrollTrigger: { trigger: cards[i + 1], start: 'top bottom', end: 'top 30%', scrub: true } });
  });
}
