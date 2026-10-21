import * as THREE from 'three';

// Canvas `font` ne razume CSS promenljive, zato ovde stoje prava imena fontova
export const FONTS = {
  sans: "'Inter Tight Variable', 'Helvetica Neue', Arial, sans-serif",
  serif: "'Instrument Serif', Georgia, serif",
  mono: "'JetBrains Mono', Menlo, monospace",
};

/* Veliki natpis iza staklenog znaka: staklo ga lomi, pa je deo scene, ne HTML-a */
export function wordmarkTexture(text = 'KERN') {
  const W = 2048;
  const H = 640;
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const ctx = c.getContext('2d');
  let size = 560;
  do {
    ctx.font = `600 ${size}px ${FONTS.sans}`;
    size -= 10;
  } while (ctx.measureText(text).width > W * 0.96 && size > 80);
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#ffffff';
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${-size * 0.04}px`;
  ctx.fillText(text, W / 2, H / 2 + size * 0.04);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}

/* Meki sjaj oko jezgra (aditivni sprite) */
export function glowTexture() {
  const S = 256;
  const c = document.createElement('canvas');
  c.width = S; c.height = S;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S / 2);
  g.addColorStop(0, 'rgba(255,200,150,1)');
  g.addColorStop(0.18, 'rgba(255,120,60,.55)');
  g.addColorStop(0.45, 'rgba(255,91,36,.16)');
  g.addColorStop(1, 'rgba(255,91,36,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, S, S);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ---------------- Konceptni sajtovi za galeriju ----------------
   Svaki projekat je „sajt“: fotka + navigacija + naslov u svom stilu,
   nacrtano u canvas pa korišćeno kao tekstura na zakrivljenoj ploči. */
const THEMES = {
  aurel: { font: FONTS.serif, weight: '400', italic: false, ink: '#f6eee2', accent: '#d8b98a', shade: [0, .55], align: 'left', upper: false,
    nav: ['Rooms', 'Dining', 'Spa', 'Stories'], head: ['Stay a little', 'longer.'], cta: 'Book your stay', brand: 'HAUS AUREL' },
  rebhang: { font: FONTS.serif, weight: '400', italic: true, ink: '#fbf3e4', accent: '#e9c46a', shade: [.1, .6], align: 'left', upper: false,
    nav: ['Wines', 'Estate', 'Visit', 'Shop'], head: ['Wines from', 'the slope.'], cta: 'Shop the vintage', brand: 'Rebhang' },
  lumen: { font: FONTS.sans, weight: '300', italic: false, ink: '#15302e', accent: '#1f8a7a', shade: [0, 0], light: true, align: 'left', upper: false,
    nav: ['Treatments', 'Team', 'Prices', 'Contact'], head: ['Calm care,', 'bright smiles.'], cta: 'Book an appointment', brand: 'Praxis Lumen' },
  atrium: { font: FONTS.sans, weight: '500', italic: false, ink: '#ffffff', accent: '#9fc3ff', shade: [.25, .7], align: 'left', upper: true,
    nav: ['Services', 'Industries', 'Insights', 'Careers'], head: ['Clarity for', 'growing', 'companies.'], cta: 'Talk to an advisor', brand: 'ATRIUM' },
  ostwind: { font: FONTS.sans, weight: '700', italic: true, ink: '#ffffff', accent: '#e4ff1a', shade: [.15, .65], align: 'left', upper: true,
    nav: ['Bikes', 'Configure', 'Rides', 'Service'], head: ['Ride the', 'east wind.'], cta: 'Build your bike', brand: 'OSTWIND' },
  morgengold: { font: FONTS.serif, weight: '400', italic: false, ink: '#fff4e0', accent: '#f0b44c', shade: [.05, .6], align: 'left', upper: false,
    nav: ['Bread', 'Pastry', 'Pre-order', 'Find us'], head: ['Baked before', 'sunrise.'], cta: 'Pre-order for tomorrow', brand: 'Morgengold' },
};

function cover(ctx, img, W, H) {
  const r = Math.max(W / img.width, H / img.height);
  const w = img.width * r;
  const h = img.height * r;
  ctx.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

export function drawSite(canvas, img, theme) {
  const T = THEMES[theme];
  const W = canvas.width;
  const H = canvas.height;
  const u = W / 1600; // sve mere su zadate za širinu 1600
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, W, H);
  if (img) cover(ctx, img, W, H);
  else { ctx.fillStyle = '#1c1c1f'; ctx.fillRect(0, 0, W, H); }

  // zatamnjenje za čitljivost (svetla tema dobija svetli veo levo)
  if (T.light) {
    const g = ctx.createLinearGradient(0, 0, W * 0.75, 0);
    g.addColorStop(0, 'rgba(250,250,247,.88)');
    g.addColorStop(1, 'rgba(250,250,247,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  } else {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, `rgba(8,8,10,${T.shade[0] + 0.25})`);
    g.addColorStop(0.35, `rgba(8,8,10,${T.shade[0]})`);
    g.addColorStop(1, `rgba(8,8,10,${T.shade[1] + 0.2})`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const s = ctx.createLinearGradient(0, 0, W * 0.8, 0);
    s.addColorStop(0, 'rgba(8,8,10,.45)');
    s.addColorStop(1, 'rgba(8,8,10,0)');
    ctx.fillStyle = s; ctx.fillRect(0, 0, W, H);
  }

  const pad = 64 * u;
  ctx.fillStyle = T.ink;
  ctx.textBaseline = 'alphabetic';

  // navigacija
  ctx.font = `${T.italic ? 'italic ' : ''}${T.upper ? 600 : 500} ${34 * u}px ${T.font}`;
  if ('letterSpacing' in ctx) ctx.letterSpacing = T.upper ? `${4 * u}px` : '0px';
  ctx.fillText(T.brand, pad, pad + 26 * u);
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';
  ctx.font = `500 ${21 * u}px ${FONTS.sans}`;
  ctx.globalAlpha = 0.86;
  let x = W - pad - 190 * u;
  for (let i = T.nav.length - 1; i >= 0; i--) {
    const w = ctx.measureText(T.nav[i]).width;
    x -= w + 38 * u;
    ctx.fillText(T.nav[i], x + 38 * u, pad + 22 * u);
  }
  ctx.globalAlpha = 1;
  // dugme u navigaciji
  roundRect(ctx, W - pad - 170 * u, pad - 8 * u, 170 * u, 52 * u, 26 * u);
  ctx.fillStyle = T.accent; ctx.fill();
  ctx.fillStyle = T.light ? '#ffffff' : '#0b0b0c';
  ctx.font = `600 ${19 * u}px ${FONTS.sans}`;
  ctx.textAlign = 'center';
  ctx.fillText(T.light ? 'Book' : 'Menu', W - pad - 85 * u, pad + 24 * u);
  ctx.textAlign = 'left';

  // naslov
  const lines = T.head.map((l) => (T.upper ? l.toUpperCase() : l));
  let size = (T.upper ? 120 : 150) * u;
  ctx.font = `${T.italic ? 'italic ' : ''}${T.weight} ${size}px ${T.font}`;
  const widest = Math.max(...lines.map((l) => ctx.measureText(l).width));
  if (widest > W * 0.66) size *= (W * 0.66) / widest;
  ctx.font = `${T.italic ? 'italic ' : ''}${T.weight} ${size}px ${T.font}`;
  if ('letterSpacing' in ctx) ctx.letterSpacing = `${-size * (T.font === FONTS.sans ? 0.04 : 0.01)}px`;
  const lh = size * (T.upper ? 0.95 : 1.0);
  const top = H - pad * 2.6 - lh * (lines.length - 1) - 90 * u;
  ctx.fillStyle = T.ink;
  lines.forEach((l, i) => ctx.fillText(l, pad, top + i * lh));
  if ('letterSpacing' in ctx) ctx.letterSpacing = '0px';

  // tekst i dugme ispod naslova
  const by = H - pad - 54 * u;
  ctx.font = `600 ${21 * u}px ${FONTS.sans}`;
  const cw = ctx.measureText(T.cta).width + 64 * u;
  roundRect(ctx, pad, by - 4 * u, cw, 60 * u, 30 * u);
  ctx.fillStyle = T.accent; ctx.fill();
  ctx.fillStyle = T.light ? '#ffffff' : '#0b0b0c';
  ctx.fillText(T.cta, pad + 32 * u, by + 34 * u);
  ctx.fillStyle = T.ink;
  ctx.globalAlpha = 0.7;
  ctx.font = `500 ${18 * u}px ${FONTS.mono}`;
  ctx.textAlign = 'right';
  ctx.fillText('↓ scroll', W - pad, by + 34 * u);
  ctx.textAlign = 'left';
  ctx.globalAlpha = 1;
}
