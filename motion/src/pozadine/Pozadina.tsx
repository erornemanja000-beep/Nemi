import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {
	CX,
	CY,
	DEBLJINA,
	type Dogadjaj,
	hes,
	polozaj,
	prng,
	R,
	SIRINA,
	simulacija,
	UZORAKA,
	VISINA,
} from './simulacija';

// Gornja polovina uspravnog klipa (1080 × 960): „kuglice u krugu".
// Sve se čita iz unapred izračunate simulacije, pa je svaki kadar isti bez obzira na redosled rendera.

export type PozadinaProps = {seed: number};

const TRAG = 10; // uzoraka u tragu (≈ 5 kadrova)
const RP = R + DEBLJINA / 2; // poluprečnik na kome se crta prsten

const luk = (r: number, a0: number, a1: number) => {
	const x0 = CX + Math.cos(a0) * r;
	const y0 = CY + Math.sin(a0) * r;
	const x1 = CX + Math.cos(a1) * r;
	const y1 = CY + Math.sin(a1) * r;
	const veliki = a1 - a0 > Math.PI ? 1 : 0;
	return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 ${veliki} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
};

const izblendaj = (t: number, trajanje: number) => Math.max(0, 1 - t / trajanje);

const Dogadjaji: React.FC<{d: Dogadjaj[]; f: number; boje: string[]}> = ({d, f, boje}) => {
	const elementi: React.ReactNode[] = [];
	for (let i = 0; i < d.length; i++) {
		const e = d[i];
		const t = f - e.t;
		if (t < 0 || t > 40) continue;
		const kljuc = `${e.tip}-${i}`;
		if (e.tip === 'izlaz' && t <= 22) {
			// varnice na mestu izlaska + talas
			const rnd = prng(hes(e.t, e.x));
			const boja = boje[e.boja];
			const a = izblendaj(t, 22);
			for (let j = 0; j < 9; j++) {
				const ugao = e.ugao + (rnd() - 0.5) * 1.6;
				const brzina = 7 + rnd() * 9;
				const r = (3 + rnd() * 4) * a;
				elementi.push(
					<circle
						key={`${kljuc}-${j}`}
						cx={e.x + Math.cos(ugao) * brzina * t}
						cy={e.y + Math.sin(ugao) * brzina * t + 0.25 * t * t}
						r={r}
						fill={boja}
						opacity={a}
					/>,
				);
			}
			elementi.push(
				<circle key={`${kljuc}-t`} cx={e.x} cy={e.y} r={10 + t * 4} fill="none" stroke={boja} strokeWidth={4 * a} opacity={a * 0.8} />,
			);
		} else if (e.tip === 'rodjenje' && t <= 12) {
			const a = izblendaj(t, 12);
			elementi.push(
				<circle key={kljuc} cx={CX} cy={CY} r={8 + t * 5} fill="none" stroke={boje[e.boja]} strokeWidth={3 * a} opacity={a * 0.7} />,
			);
		} else if (e.tip === 'puls' && t <= 20) {
			const a = izblendaj(t, 20);
			elementi.push(<circle key={kljuc} cx={CX} cy={CY} r={30 + t * 19} fill="none" stroke="#ffffff" strokeWidth={6 * a} opacity={a * 0.5} />);
		} else if (e.tip === 'reset') {
			// prasak: talasi u svim bojama i krhotine prstena
			const a = izblendaj(t, 40);
			boje.forEach((b, j) => {
				const tt = t - j * 3;
				if (tt < 0) return;
				elementi.push(
					<circle key={`${kljuc}-w${j}`} cx={CX} cy={CY} r={RP + tt * 16} fill="none" stroke={b} strokeWidth={14 * a} opacity={a} />,
				);
			});
			const rnd = prng(hes(e.t, 99));
			for (let j = 0; j < 18; j++) {
				const a0 = e.ugao + (j / 18) * Math.PI * 2 + rnd() * 0.1;
				const duzina = 0.22 + rnd() * 0.12;
				const pomak = t * (9 + rnd() * 8);
				const r = RP + pomak;
				elementi.push(
					<path
						key={`${kljuc}-k${j}`}
						d={luk(r, a0, a0 + duzina)}
						fill="none"
						stroke={boje[j % boje.length]}
						strokeWidth={DEBLJINA * (0.6 + 0.4 * a)}
						strokeLinecap="round"
						opacity={a}
					/>,
				);
			}
		}
	}
	return <>{elementi}</>;
};

export const Pozadina: React.FC<PozadinaProps> = ({seed}) => {
	const f = useCurrentFrame();
	const sim = simulacija(seed);
	const {boje, pozadina} = sim.paleta;

	const ugao = sim.ugao[f];
	const otvor = sim.otvor[f];
	const prsten = sim.prsten[f];
	const napetost = sim.napetost[f];
	const kriticno = sim.kriticno[f];

	// boja prstena polako prelazi kroz paletu; pred prasak treperi u belo
	const bojaPrstena = boje[Math.floor(f / 45) % boje.length];
	const treptaj = kriticno > 0 ? (Math.floor(f / 2) % 2 === 0 ? 1 : 0) : 0;
	const tresenje = kriticno * 7;
	const pomakX = tresenje * Math.sin(f * 2.1);
	const pomakY = tresenje * Math.cos(f * 2.7);

	// blesak posle reseta
	let blesak = 0;
	let okret = 0;
	for (const e of sim.dogadjaji) {
		const t = f - e.t;
		if (t < 0) break;
		if (e.tip === 'reset' && t <= 10) blesak = Math.max(blesak, 0.55 * (1 - t / 10));
		if (e.tip === 'okret' && t <= 10) okret = Math.max(okret, 1 - t / 10);
	}

	const s = f * UZORAKA;
	const sjaj = 0.18 + napetost * 0.35;

	// prsten: pun luk bez otvora; u gradnji se iscrtava u smeru kazaljke
	const pocetak = ugao + otvor;
	const punLuk = Math.PI * 2 - otvor * 2;
	const luka = prsten > 0 ? luk(RP, pocetak, pocetak + punLuk * Math.min(1, prsten)) : null;
	const sirinaPrstena = DEBLJINA * (1 + okret * 0.6);

	return (
		<AbsoluteFill style={{backgroundColor: pozadina}}>
			<svg width={SIRINA} height={VISINA} viewBox={`0 0 ${SIRINA} ${VISINA}`}>
				<defs>
					<radialGradient id="sjaj">
						<stop offset="0%" stopColor={bojaPrstena} stopOpacity={sjaj} />
						<stop offset="70%" stopColor={bojaPrstena} stopOpacity={sjaj * 0.25} />
						<stop offset="100%" stopColor={bojaPrstena} stopOpacity={0} />
					</radialGradient>
				</defs>
				<circle cx={CX} cy={CY} r={RP * 1.25} fill="url(#sjaj)" />

				<g transform={`translate(${pomakX.toFixed(2)} ${pomakY.toFixed(2)})`}>
					{luka ? (
						<>
							<path d={luka} fill="none" stroke={bojaPrstena} strokeWidth={sirinaPrstena * 3.2} opacity={0.12} strokeLinecap="round" />
							<path d={luka} fill="none" stroke={bojaPrstena} strokeWidth={sirinaPrstena * 1.9} opacity={0.25} strokeLinecap="round" />
							<path
								d={luka}
								fill="none"
								stroke={treptaj ? '#ffffff' : bojaPrstena}
								strokeWidth={sirinaPrstena}
								strokeLinecap="round"
							/>
						</>
					) : null}
					{prsten > 0 && prsten < 1 ? (
						<circle
							cx={CX + Math.cos(pocetak + punLuk * prsten) * RP}
							cy={CY + Math.sin(pocetak + punLuk * prsten) * RP}
							r={DEBLJINA * 1.2}
							fill="#ffffff"
							opacity={0.9}
						/>
					) : null}

					{sim.kuglice.map((k) => {
						const sada = polozaj(k, s);
						if (!sada) return null;
						const boja = boje[k.boja];
						const tacke: string[] = [];
						for (let i = TRAG; i >= 0; i--) {
							const p = polozaj(k, s - i);
							if (p) tacke.push(`${p[0].toFixed(1)},${p[1].toFixed(1)}`);
						}
						return (
							<g key={k.id}>
								{tacke.length > 1 ? (
									<polyline
										points={tacke.join(' ')}
										fill="none"
										stroke={boja}
										strokeWidth={k.r * 1.3}
										strokeLinecap="round"
										strokeLinejoin="round"
										opacity={0.28}
									/>
								) : null}
								<circle cx={sada[0]} cy={sada[1]} r={k.r * 1.9} fill={boja} opacity={0.18} />
								<circle cx={sada[0]} cy={sada[1]} r={k.r} fill={boja} />
								<circle cx={sada[0] - k.r * 0.3} cy={sada[1] - k.r * 0.35} r={k.r * 0.32} fill="#ffffff" opacity={0.55} />
							</g>
						);
					})}

					<Dogadjaji d={sim.dogadjaji} f={f} boje={boje} />
				</g>
			</svg>
			{blesak > 0 ? <AbsoluteFill style={{backgroundColor: '#ffffff', opacity: blesak}} /> : null}
		</AbsoluteFill>
	);
};
