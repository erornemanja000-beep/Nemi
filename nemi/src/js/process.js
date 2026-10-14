/* ---------- process stack ---------- */
if (hasG && !RM) {
  const cards = $$('.proc-card');
  cards.forEach((card, i) => {
    if (i === cards.length - 1) return;
    G.to(card, { scale: .93, ease: 'none', scrollTrigger: { trigger: cards[i + 1], start: 'top bottom', end: 'top 30%', scrub: true } });
  });
}

// the dark band opens like a screen: rounded inset frame -> full width
if (hasG && !RM) G.fromTo('.proc', { clipPath: 'inset(0% 3.5% 0% 3.5% round 44px)' }, { clipPath: 'inset(0% 0% 0% 0% round 0px)', ease: 'none',
  scrollTrigger: { trigger: '.proc', start: 'top bottom', end: 'top 15%', scrub: true } });
