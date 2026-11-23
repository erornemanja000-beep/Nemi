// „Kuglice u krugu": cela simulacija se izračuna unapred, čistom funkcijom seed → stanja za sve kadrove.
// Remotion renderuje kadrove van redosleda i u više tabova, pa kadar samo čita gotovo stanje.
// Nema Math.random, nema stanja između kadrova, korak je fiksan (6 koraka po kadru).
// Fajl nema importe, da može da se pokrene i u Node-u za proveru (node simulacija.ts).

export const SIRINA = 1080;
export const VISINA = 960;
export const FPS = 30;
export const TRAJANJE = 90 * FPS;

export const CX = 540;
export const CY = 492;
export const R = 392; // unutrašnja ivica prstena (fizika); prsten se crta spolja od nje
export const DEBLJINA = 14;
export const MAX_KUGLICA = 60;
export const UZORAKA = 2; // uzoraka položaja po kadru, za glatke tragove

const KORACI = 6; // fizičkih koraka po kadru
const KORACI_PO_UZORKU = KORACI / UZORAKA;
const DT = 1 / (FPS * KORACI);
const G = 720; // px/s²
const V_MIN = 820; // posle udara u zid kuglica ima bar ovoliko (ne zamire)
const V_MAX = 1450;
const TRENJE_ZIDA = 0.05; // koliko okretanje prstena povuče kuglicu
const OMEGA0 = 0.95; // rad/s na početku ciklusa
const PREDROLA = 45; // kadrova pre kadra 0, da prvi kadar već ima pokret i tragove

// trajanja u kadrovima
export const GRADNJA = 24; // prsten se iscrtava
export const PRASAK = 30; // posle reseta, pre nove gradnje
export const KRITICNO = 18; // pun prsten, pa prasak
export const KASNJENJE_RODJENJA = 4;
const PAS = 4.2 * FPS; // najduže bez događaja
const MAX_CIKLUS = 32 * FPS;

export type Paleta = {ime: string; boje: string[]; pozadina: string};

// Neonske boje na skoro crnoj podlozi (beli tekst sa crnom konturom ostaje čitljiv preko svega).
export const PALETE: Paleta[] = [
	{ime: 'neon', boje: ['#ff2bd6', '#00e5ff', '#8b5cff', '#ffe14d', '#39ff88'], pozadina: '#07050f'},
	{ime: 'lava-led', boje: ['#ff3b3b', '#ff9a1f', '#ffe14d', '#00d2ff', '#5b7cff'], pozadina: '#0a0507'},
	{ime: 'kiselina', boje: ['#b6ff00', '#00ffa3', '#00c8ff', '#ff00e6', '#fff200'], pozadina: '#03080a'},
	{ime: 'zalazak', boje: ['#ff6a00', '#ff1f6b', '#c13bff', '#3df2ff', '#ffd23f'], pozadina: '#0a0510'},
	{ime: 'aurora', boje: ['#00ffd5', '#00a2ff', '#8a5cff', '#ff4fd8', '#b8ff3b'], pozadina: '#03070d'},
	{ime: 'bombona', boje: ['#ff5cf4', '#ffd000', '#00f0ff', '#ff4d6d', '#6bff6b'], pozadina: '#08050c'},
];

export type Kuglica = {
	id: number;
	r: number;
	boja: number; // indeks u paleti
	od: number; // globalni indeks prvog uzorka (kadar * UZORAKA)
	do: number; // indeks posle poslednjeg uzorka
	xy: Float32Array; // x, y za svaki uzorak od `od`
};

export type Dogadjaj =
	| {tip: 'izlaz'; t: number; x: number; y: number; ugao: number; boja: number}
	| {tip: 'rodjenje'; t: number; boja: number}
	| {tip: 'okret'; t: number}
	| {tip: 'puls'; t: number}
	| {tip: 'reset'; t: number; ugao: number}
	| {tip: 'gradnja'; t: number};

export type Simulacija = {
	seed: number;
	paleta: Paleta;
	otvor: Float32Array; // pola širine otvora (rad) po kadru
	kuglice: Kuglica[];
	dogadjaji: Dogadjaj[]; // poređani po t (kadar, može biti razlomak)
	ugao: Float32Array; // sredina otvora po kadru
	prsten: Float32Array; // 1 = ceo prsten, 0..1 = gradnja, 0 = razbijen
	napetost: Float32Array; // broj kuglica u krugu / MAX_KUGLICA
	kriticno: Float32Array; // 0..1 pred reset
	ciklus: Uint8Array;
};

// mulberry32: mali PRNG sa 32-bitnim stanjem, isti rezultat u svakom tabu
export const prng = (seme: number) => {
	let a = seme >>> 0;
	return () => {
		a = (a + 0x6d2b79f5) >>> 0;
		let t = a;
		t = Math.imul(t ^ (t >>> 15), t | 1);
		t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
};

export const hes = (...brojevi: number[]) => {
	let h = 0x811c9dc5;
	for (const b of brojevi) {
		h = Math.imul(h ^ (Math.floor(b * 1000) | 0), 0x01000193);
		h ^= h >>> 13;
	}
	return h >>> 0;
};

const PI2 = Math.PI * 2;
const omotaj = (a: number) => {
	let x = (a + Math.PI) % PI2;
	if (x < 0) x += PI2;
	return x - Math.PI;
};

type Telo = {
	k: Kuglica;
	x: number;
	y: number;
	vx: number;
	vy: number;
	m: number;
	stanje: 'u' | 'van' | 'leti'; // u krugu, izašla kroz otvor, odbačena praskom
	uzorci: number[];
};

const izracunaj = (seed: number): Simulacija => {
	const rnd = prng(hes(seed, 7));
	const paleta = PALETE[hes(seed, 3) % PALETE.length];
	const brojBoja = paleta.boje.length;
	let sledecaBoja = Math.floor(rnd() * brojBoja);
	// otvor je širok dok je kuglica malo i sužava se kako ih ima više (napetost raste, rast ostaje ujednačen)
	const otvorUzak = 0.27 + rnd() * 0.04;
	const otvorSirok = otvorUzak + 0.2;
	let otvor = otvorSirok;

	const ugao = new Float32Array(TRAJANJE);
	const otvori = new Float32Array(TRAJANJE);
	const prsten = new Float32Array(TRAJANJE);
	const napetost = new Float32Array(TRAJANJE);
	const kriticno = new Float32Array(TRAJANJE);
	const ciklus = new Uint8Array(TRAJANJE);
	const dogadjaji: Dogadjaj[] = [];
	const kuglice: Kuglica[] = [];
	const tela: Telo[] = [];

	let k = -PREDROLA * KORACI; // globalni fizički korak
	let zapisano = k / KORACI_PO_UZORKU - 1; // poslednji zapisani uzorak

	let faza: 'gradi' | 'igra' | 'kriticno' | 'prasak' = 'igra';
	let ugaoOtvora = rnd() * PI2;
	let smer = rnd() < 0.5 ? -1 : 1;
	let omega = smer * OMEGA0;
	let pocetakCiklusa = -PREDROLA;
	let pocetakGradnje = 0;
	let tReset = 0;
	let zadnjiDogadjaj = 0;
	let sledeciOkret = 7 * FPS + rnd() * 4 * FPS;
	let brojCiklusa = 0;
	let pasNaizmenicno = rnd() < 0.5;
	const naCekanju: number[] = []; // vremena kad treba roditi po dve kuglice

	const uKrugu = () => {
		let n = 0;
		for (const b of tela) if (b.stanje === 'u') n++;
		return n;
	};

	const rodi = (t: number, koliko: number) => {
		const a = rnd() * PI2;
		const brzina = 380 + rnd() * 260;
		for (let i = 0; i < koliko; i++) {
			const ai = a + i * Math.PI + (rnd() - 0.5) * 0.6;
			const r = 13 + rnd() * 4;
			const boja = sledecaBoja++ % brojBoja;
			const kug: Kuglica = {id: kuglice.length, r, boja, od: zapisano + 1, do: 0, xy: new Float32Array(0)};
			kuglice.push(kug);
			tela.push({
				k: kug,
				x: CX + Math.cos(ai) * (r + 1),
				y: CY + Math.sin(ai) * (r + 1),
				vx: Math.cos(ai) * brzina,
				vy: Math.sin(ai) * brzina,
				m: r * r,
				stanje: 'u',
				uzorci: [],
			});
			dogadjaji.push({tip: 'rodjenje', t, boja});
		}
	};

	const okret = (t: number) => {
		smer = -smer;
		dogadjaji.push({tip: 'okret', t});
		zadnjiDogadjaj = t;
	};

	const puls = (t: number) => {
		for (const b of tela) {
			if (b.stanje !== 'u') continue;
			const dx = b.x - CX;
			const dy = b.y - CY;
			const d = Math.hypot(dx, dy) || 1;
			b.vx += (dx / d) * 420;
			b.vy += (dy / d) * 420 - 120;
		}
		dogadjaji.push({tip: 'puls', t});
		zadnjiDogadjaj = t;
	};

	const reset = (t: number) => {
		for (const b of tela) {
			if (b.stanje !== 'u') continue;
			const dx = b.x - CX;
			const dy = b.y - CY;
			const d = Math.hypot(dx, dy);
			const a = d > 4 ? Math.atan2(dy, dx) : rnd() * PI2;
			const s = 900 + rnd() * 700;
			b.vx = Math.cos(a) * s + b.vx * 0.3;
			b.vy = Math.sin(a) * s + b.vy * 0.3;
			b.stanje = 'leti';
		}
		naCekanju.length = 0;
		dogadjaji.push({tip: 'reset', t, ugao: ugaoOtvora});
		zadnjiDogadjaj = t;
	};

	rodi(-PREDROLA, 2);

	const kraj = TRAJANJE * KORACI;
	for (; k < kraj; k++) {
		const t = k / KORACI; // vreme u kadrovima

		// 1) zapis stanja (pre koraka)
		if (k % KORACI_PO_UZORKU === 0) {
			for (const b of tela) b.uzorci.push(b.x, b.y);
			zapisano = k / KORACI_PO_UZORKU;
			if (k % KORACI === 0 && t >= 0) {
				ugao[t] = ugaoOtvora;
				otvori[t] = otvor;
				prsten[t] =
					faza === 'prasak' ? 0 : faza === 'gradi' ? Math.min(1, Math.max(0, (t - pocetakGradnje) / GRADNJA)) : 1;
				napetost[t] = uKrugu() / MAX_KUGLICA;
				kriticno[t] = faza === 'kriticno' ? 1 - (tReset - t) / KRITICNO : 0;
				ciklus[t] = brojCiklusa;
			}
		}

		// 2) faze ciklusa
		if (faza === 'kriticno' && t >= tReset) {
			reset(t);
			faza = 'prasak';
		} else if (faza === 'prasak' && t >= tReset + PRASAK) {
			faza = 'gradi';
			pocetakGradnje = t;
			brojCiklusa++;
			ugaoOtvora = rnd() * PI2;
			smer = rnd() < 0.5 ? -1 : 1;
			omega = smer * OMEGA0;
			dogadjaji.push({tip: 'gradnja', t});
		} else if (faza === 'gradi' && t >= pocetakGradnje + GRADNJA) {
			faza = 'igra';
			pocetakCiklusa = t;
			zadnjiDogadjaj = t;
			sledeciOkret = t + 7 * FPS + rnd() * 4 * FPS;
			rodi(t, 2);
		}

		if (faza === 'igra') {
			while (naCekanju.length > 0 && naCekanju[0] <= t) {
				naCekanju.shift();
				const n = uKrugu();
				rodi(t, Math.min(2, MAX_KUGLICA - n));
				if (n + 2 >= MAX_KUGLICA) {
					faza = 'kriticno';
					tReset = t + KRITICNO;
					break;
				}
			}
			if (faza === 'igra') {
				if (t >= sledeciOkret) {
					okret(t);
					sledeciOkret = t + 8 * FPS + rnd() * 4 * FPS;
				} else if (t - zadnjiDogadjaj > PAS) {
					if (pasNaizmenicno) puls(t);
					else okret(t);
					pasNaizmenicno = !pasNaizmenicno;
				}
				if (t - pocetakCiklusa > MAX_CIKLUS) {
					faza = 'kriticno';
					tReset = t + KRITICNO;
				}
			}
		}

		// 3) prsten se okreće; brzina raste sa napetošću, promena smera je meka
		const nap = uKrugu() / MAX_KUGLICA;
		const cilj = smer * OMEGA0 * (1 + 1.3 * nap);
		omega += (cilj - omega) * Math.min(1, DT * 4);
		otvor = otvorUzak + (otvorSirok - otvorUzak) * (1 - nap) * (1 - nap);
		ugaoOtvora = omotaj(ugaoOtvora + omega * DT);

		// 4) kretanje
		for (const b of tela) {
			b.vy += G * DT;
			b.x += b.vx * DT;
			b.y += b.vy * DT;
		}

		// 5) sudari kuglica u krugu (elastični, masa ~ r²)
		for (let i = 0; i < tela.length; i++) {
			const a = tela[i];
			if (a.stanje !== 'u') continue;
			for (let j = i + 1; j < tela.length; j++) {
				const b = tela[j];
				if (b.stanje !== 'u') continue;
				const dx = b.x - a.x;
				const dy = b.y - a.y;
				const rr = a.k.r + b.k.r;
				const d2 = dx * dx + dy * dy;
				if (d2 >= rr * rr || d2 === 0) continue;
				const d = Math.sqrt(d2);
				const nx = dx / d;
				const ny = dy / d;
				const ukupno = a.m + b.m;
				const preklop = rr - d;
				a.x -= nx * preklop * (b.m / ukupno);
				a.y -= ny * preklop * (b.m / ukupno);
				b.x += nx * preklop * (a.m / ukupno);
				b.y += ny * preklop * (a.m / ukupno);
				const rel = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny;
				if (rel < 0) {
					const imp = (-2 * rel) / (1 / a.m + 1 / b.m);
					a.vx -= (imp / a.m) * nx;
					a.vy -= (imp / a.m) * ny;
					b.vx += (imp / b.m) * nx;
					b.vy += (imp / b.m) * ny;
				}
			}
		}

		// 6) prsten: odbijanje ili izlazak kroz otvor
		for (const b of tela) {
			if (b.stanje !== 'u') continue;
			const dx = b.x - CX;
			const dy = b.y - CY;
			const gr = R - b.k.r;
			const d2 = dx * dx + dy * dy;
			if (d2 <= gr * gr) continue;
			const d = Math.sqrt(d2);
			const fi = Math.atan2(dy, dx);
			const razlika = omotaj(fi - ugaoOtvora);
			const prolaz = otvor - (b.k.r / R) * 0.55;
			if (Math.abs(razlika) < prolaz && (faza === 'igra' || faza === 'kriticno')) {
				b.stanje = 'van';
				dogadjaji.push({
					tip: 'izlaz',
					t,
					x: CX + Math.cos(fi) * (R + DEBLJINA / 2),
					y: CY + Math.sin(fi) * (R + DEBLJINA / 2),
					ugao: fi,
					boja: b.k.boja,
				});
				zadnjiDogadjaj = t;
				if (faza === 'igra') naCekanju.push(t + KASNJENJE_RODJENJA);
				continue;
			}
			const nx = dx / d;
			const ny = dy / d;
			b.x = CX + nx * gr;
			b.y = CY + ny * gr;
			const vn = b.vx * nx + b.vy * ny;
			if (vn > 0) {
				b.vx -= 2 * vn * nx;
				b.vy -= 2 * vn * ny;
				const tx = -ny;
				const ty = nx;
				const vt = b.vx * tx + b.vy * ty;
				const dv = (omega * R - vt) * TRENJE_ZIDA;
				b.vx += tx * dv;
				b.vy += ty * dv;
				const s = Math.hypot(b.vx, b.vy);
				const nova = Math.min(V_MAX, Math.max(V_MIN, s));
				if (s > 0) {
					b.vx *= nova / s;
					b.vy *= nova / s;
				}
			}
		}

		// 7) kuglice van ekrana nestaju
		for (let i = tela.length - 1; i >= 0; i--) {
			const b = tela[i];
			if (b.stanje === 'u') continue;
			if (b.x < -80 || b.x > SIRINA + 80 || b.y > VISINA + 80 || b.y < -700) {
				b.k.xy = Float32Array.from(b.uzorci);
				tela.splice(i, 1);
			}
		}
	}

	for (const b of tela) {
		b.k.do = b.k.od + b.uzorci.length / 2;
		b.k.xy = Float32Array.from(b.uzorci);
	}
	for (const kug of kuglice) {
		// tačan kraj prema broju zapisanih uzoraka
		kug.do = kug.od + kug.xy.length / 2;
	}
	dogadjaji.sort((a, b) => a.t - b.t);

	return {seed, paleta, otvor: otvori, kuglice, dogadjaji, ugao, prsten, napetost, kriticno, ciklus};
};

// Keš po modulu: svaki tab računa simulaciju jednom po seed-u.
const kes = new Map<number, Simulacija>();
export const simulacija = (seed: number): Simulacija => {
	const postoji = kes.get(seed);
	if (postoji) return postoji;
	const nova = izracunaj(seed);
	kes.set(seed, nova);
	return nova;
};

// Položaj kuglice u globalnom uzorku s (ili null ako tada ne postoji).
export const polozaj = (k: Kuglica, s: number): [number, number] | null => {
	if (s < k.od || s >= k.do) return null;
	const i = (s - k.od) * 2;
	return [k.xy[i], k.xy[i + 1]];
};
