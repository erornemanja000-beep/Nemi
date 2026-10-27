// Koreografija scene, 7 poglavlja (studio/pekara/skice/mapa-skrola.md, smer 3 „Ein Fenster brennt").
//
// Sve je vezano za u: omekšan položaj kamere na krivoj (camera.js), isti broj kao udeo skrola u
// kamera.json. Zato kriška, prozori, testo i peć idu tačno uz kameru i unazad i unapred (scrub),
// a inercija kamere važi i za njih. Bez autoplay-a; same od sebe idu samo blage stvari u shaderu
// (dim, treperenje prozora i lampi, brašno) i kratki odgovori na dodir (activeBread, knock).
//
//   1  0–.09      04:00 noć, svetli samo pekara, dim, lampe ugašene, jak tilt-shift
//   2  .09–.25    lampe se pale jedna po jedna (trepere), prazan tramvaj prolazi, nebo tek malo svetlije
//   3  .25–.42    ulica: kriška se izvlači (u_izvuci) pa spušta kroz dasku (u_spusti), puf brašna
//   4  .42–.60    Teig: testo se mesi pa naraste · Zeit: korpe rastu · Ofen: vrata, žar iz otvora
//                 preplavi ~40% kadra (emisija, topla vinjeta, bloom), pa pretapanje u svetlo ka izlogu
//   5  .60–.72    izlog: hlebovi uveličani, aktivni izlazi napred; izlog i bloom stišani zbog teksta;
//                 kriška se vraća na mesto pre .72 (od u_napolju iz kamera.json)
//   6  .72–.88    talas prozora od pekare, lampe se gase, noć → dan, figure sa kesama ka vratima;
//                 upaljeni prozori ostaju upaljeni (nema gašenja unazad) do kraja poglavlja 7
//   7  .88–1      dan i blur iza forme; tek u futeru nebo pada u veče i opet svetli samo pekara
//
// Telefon: lakše (bez bloom-a i DOF-a u rendereru, 3 figure, hleb samo skalom, slabiji žar i brašno).

import gsap from 'gsap';

const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const S = (a, b, x) => {
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};
const lin = (a, b, x) => clamp01((x - a) / (b - a));

const BREAD_BIG = 1.35; // hlebovi su prave veličine; u kadru izloga se uveličaju
const BLOOM = 0.42; // samo izlog, žar, prozori i farovi prelaze prag (renderer.js)

export function init(bus, api) {
  const mob = !!api.mobile;
  const kr = { u_izvuci: [0.3, 0.35], u_spusti: [0.35, 0.385], u_prolaz: 0.39, u_napolju: 0.7, ...(api.kriskaData ?? {}) };
  // Povratak kriške: od u_napolju (kamera.json), gotov pre .72 (pre nego što kamera izađe iz
  // pekare i vidi procep). Prvo se podiže kroz dasku, pa klizne na mesto.
  const NAZAD_KRAJ = 0.716;
  const n0 = Math.max(0.61, Math.min(kr.u_napolju, NAZAD_KRAJ - 0.012));
  if (kr.u_napolju > NAZAD_KRAJ - 0.012) console.warn(`[krume] u_napolju ${kr.u_napolju} je kasno: kriška se vraća od ${n0.toFixed(3)}`);
  const nazadSpusti = [n0, n0 + (NAZAD_KRAJ - n0) * 0.55];
  const nazadIzvuci = [nazadSpusti[1], NAZAD_KRAJ];

  const fx = { knock: 0 };
  const bread = [0, 1, 2, 3].map(() => ({ v: 0 }));
  let dirty = true;
  let lastU = -1;
  let inCh5 = false;
  const mark = () => {
    dirty = true;
  };
  const breadTo = bread.map((b) => gsap.quickTo(b, 'v', { duration: 0.7, ease: 'power3.out', onUpdate: mark }));

  function apply(u) {
    // ---- vreme: noć → zora → jutro, pa veče u futeru
    const vece = S(0.965, 0.998, u); // futer
    const dan = (0.05 * S(0.11, 0.25, u) + 0.2 * S(0.6, 0.72, u) + 0.75 * S(0.745, 0.87, u)) * (1 - vece);
    api.vece(vece);
    api.dan(dan);
    // talas raste samo napred i drži 1 do futera (vece); gasi se tek uveče
    api.talas(S(0.745, 0.84, u) * (1 - vece));
    api.lampe(S(0.095, 0.145, u) * (1 - S(0.78, 0.845, u)));
    api.dim(1 - 0.3 * S(0.745, 0.87, u));

    // ---- 2: tramvaj (stalna brzina, ulazi i izlazi na ivicama daske)
    api.tramvaj(lin(0.105, 0.235, u));

    // ---- 3: kriška
    const izv = u < 0.6 ? S(kr.u_izvuci[0], kr.u_izvuci[1], u) : 1 - S(nazadIzvuci[0], nazadIzvuci[1], u);
    const sp = u < 0.6 ? S(kr.u_spusti[0], kr.u_spusti[1], u) : 1 - S(nazadSpusti[0], nazadSpusti[1], u);
    api.kriska(izv, sp);
    api.enterijer(u > 0.2 && u < 0.79);

    // ---- 4: Teig (mesi se dvaput pa naraste), Zeit (korpe), Ofen (vrata i žar)
    const m = S(0.42, 0.452, u);
    const mes = Math.sin(Math.PI * m * 2) ** 2 * (1 - S(0.448, 0.46, u));
    api.testo(mes, S(0.45, 0.472, u));
    api.korpe(S(0.48, 0.528, u));
    // Ofen (drži .545–.58): vrata se otvore, žar iz otvora preplavi kadar, na kraju koraka
    // pretapanje u toplo svetlo (sakriva put kamere do izloga), koje se otvara u poglavlje 5.
    const vrata = S(0.545, 0.56, u) * (1 - S(0.6, 0.635, u));
    api.pecVrata(vrata);
    api.zarEmisija(1 + 3 * vrata);
    api.pecSvetlo?.(vrata);
    const svetlo = S(0.574, 0.592, u) * (1 - S(0.598, 0.618, u));
    const zar = S(0.549, 0.568, u) * (1 - S(0.586, 0.602, u));
    api.zar(zar * (mob ? 0.55 : 0.62));
    api.svetlo(svetlo * 0.8);

    // ---- 5: hlebovi
    const c5 = S(0.595, 0.625, u) * (1 - S(0.715, 0.74, u));
    api.hlebovi(1 + (BREAD_BIG - 1) * c5, bread.map((b) => b.v * c5));
    if (c5 > 0 || inCh5) api.syncBreads();
    inCh5 = c5 > 0;
    // izlog stišan da se tekst čita; knock kratko pojača sjaj pekare
    api.izlog((1 - 0.45 * c5) * (1 + 1.3 * fx.knock));
    api.enterijerSvetlo(1 - 0.22 * c5);
    api.bloom(BLOOM * (1 - 0.6 * c5) + 0.4 * zar);

    // ---- 6: figure sa kesama
    api.figure(S(0.765, 0.875, u));

    // ---- brašno: puf kad se kriška izvuče, pa lebdi u pekari
    const puff = S(0.325, 0.355, u) * (1 - S(0.375, 0.4, u));
    const unutra = S(0.415, 0.44, u) * (1 - S(0.7, 0.725, u));
    api.brasnoMesto(u < 0.41 ? 'otvor' : 'sto');
    const k = mob ? 0.6 : 1;
    api.brasno(k * Math.max(0.8 * puff + 0.6 * fx.knock * (u < 0.42 ? 1 : 0), (u < 0.6 ? 0.75 : 0.35) * unutra));

    // ---- post: tilt-shift jak na maketi, slabiji na ulici, skoro nikakav unutra; blur iza forme
    const ulica = S(0.18, 0.25, u) * (1 - S(0.4, 0.42, u));
    const unutraK = S(0.39, 0.42, u) * (1 - S(0.72, 0.75, u));
    api.tilt(1 - Math.max(0.6 * ulica, 0.88 * unutraK));
    api.blur(0.8 * S(0.885, 0.925, u) * (1 - 0.6 * vece));
  }

  const offUpd = api.addUpdater(() => {
    const u = api.getU();
    if (!dirty && Math.abs(u - lastU) < 1e-6) return 0;
    lastU = u;
    dirty = false;
    apply(u);
    return 2;
  });

  // ---- aktivni hleb (skrol u pogl. 5 ili prevlačenje etiketa na telefonu)
  const setBread = (n) => {
    bread.forEach((_, i) => breadTo[i](i + 1 === n ? 1 : 0));
  };
  setBread(bus.get('activeBread') ?? 1);

  // ---- „Klopf ans Fenster.": izlog dvaput kratko zatreperi (kuc-kuc), uz mali puf brašna
  let knockTl = null;
  const onKnock = () => {
    knockTl?.kill();
    knockTl = gsap
      .timeline({ onUpdate: mark, onComplete: mark })
      .to(fx, { knock: 1, duration: 0.06, ease: 'power2.out' })
      .to(fx, { knock: 0.15, duration: 0.14, ease: 'power2.in' })
      .to(fx, { knock: 0.9, duration: 0.06, ease: 'power2.out' })
      .to(fx, { knock: 0, duration: 0.7, ease: 'power3.out' });
  };

  const offs = [bus.on('activeBread', setBread), bus.on('knock', onKnock)];

  apply(api.getU());
  lastU = api.getU();

  return {
    destroy() {
      offUpd();
      offs.forEach((f) => f());
      knockTl?.kill();
      bread.forEach((b) => gsap.killTweensOf(b));
      gsap.killTweensOf(fx);
    },
  };
}
