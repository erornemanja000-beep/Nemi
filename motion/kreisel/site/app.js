// KREISEL: ceo sajt je jedna vremenska linija od 8,5 s koju pokreće skrol.
// Isti raspored koristi Blender (produkt.py), pa se 3D proizvod i tekst poklapaju.
(() => {
  const TRAJANJE = 8.5;
  const FPS = 30;
  const KADROVA = 255;
  const smanjeno = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const e = (x) => {
    x = Math.min(Math.max(x, 0), 1);
    return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  };

  const seiten = document.getElementById("seiten");
  const platno = document.getElementById("produkt");
  const ctx = platno.getContext("2d");
  const punkte = [...document.querySelectorAll(".punkte li")];

  // elementi koji se otkrivaju: [selektor, početak (s), trajanje (s), kraj (s ili null)]
  const otkrivanja = [
    [".seite-2 .eyebrow", 1.9, 0.5, null],
    [".fuss-links", 2.2, 0.5, null],
    [".et-1", 3.45, 0.3, 4.15],
    [".et-2", 3.6, 0.3, 4.15],
    [".et-3", 3.75, 0.3, 4.15],
    [".kopf-3", 4.9, 0.6, null],
    [".sorten", 5.3, 0.5, null],
    [".karte", 5.45, 0.5, null],
    [".knopf-gold", 5.7, 0.5, null],
  ].map(([sel, od, traje, kraj]) => {
    const el = document.querySelector(sel);
    el.classList.add("otkri");
    return { el, od, traje, kraj };
  });
  const riesig = document.querySelector(".riesig");

  // bildsekvenca iz Blender-a
  const slike = [];
  const ucitane = [];
  for (let i = 1; i <= KADROVA; i++) {
    const img = new Image();
    img.src = `../render/produkt/${String(i).padStart(4, "0")}.png`;
    slike.push(img);
    ucitane.push(img.decode().catch(() => {}));
  }
  window.kreiselSpreman = Promise.all(ucitane).then(() => document.fonts.ready);

  let poslednji = -1;
  function crtaj(t) {
    const i = Math.min(KADROVA - 1, Math.max(0, Math.round(t * FPS)));
    const img = slike[i];
    if (i === poslednji || !img.complete || img.naturalWidth === 0) return;
    ctx.clearRect(0, 0, platno.width, platno.height);
    ctx.drawImage(img, 0, 0, platno.width, platno.height);
    poslednji = i;
  }

  function postavi(t) {
    const pomak = innerHeight * (e((t - 1.4) / 1.2) + e((t - 4.2) / 1.2));
    seiten.style.transform = `translate3d(0, ${-pomak}px, 0)`;
    crtaj(t);

    for (const o of otkrivanja) {
      let p = smanjeno ? 1 : e((t - o.od) / o.traje);
      if (o.kraj !== null && !smanjeno) p *= 1 - e((t - o.kraj) / 0.25);
      o.el.style.setProperty("--p", p.toFixed(3));
    }
    // veliki naslov: prvo kao senka, pa pun
    const r = smanjeno ? 1 : e((t - 2.0) / 0.75);
    riesig.style.opacity = (0.14 + 0.86 * r).toFixed(3);
    riesig.style.letterSpacing = `${(0.04 * (1 - r) - 0.01).toFixed(3)}em`;

    const sekcija = Math.round(pomak / innerHeight);
    punkte.forEach((li, k) => li.classList.toggle("an", k === sekcija));
  }

  function poSkrolu() {
    const max = document.documentElement.scrollHeight - innerHeight;
    postavi((scrollY / Math.max(1, max)) * TRAJANJE);
  }

  addEventListener("scroll", () => requestAnimationFrame(poSkrolu), { passive: true });
  addEventListener("resize", poSkrolu);
  slike[0].addEventListener("load", poSkrolu);
  poSkrolu();

  // za snimanje videa (kreisel/snimi_sajt.mjs): postavi tačno vreme bez skrola
  window.kreiselPostavi = (t) => {
    poslednji = -1;
    postavi(t);
  };
})();
