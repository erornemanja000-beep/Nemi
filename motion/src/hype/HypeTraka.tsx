import {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';

// Donji pojas klipa (1080 × 532): noćna vožnja (naš AI snimak) + brzinomer „HYPE" čija kazaljka prati
// jačinu glasa streamera. Vrednosti (0–1 po kadru) računa clipper/hype.py iz zvuka klipa.

export type HypeProps = {
	vrednosti: number[]; // izglađena jačina glasa, 0–1, jedna vrednost po kadru
	video: string; // putanja u motion/public (staticFile)
	oznaka: string; // tekst ispod broja, npr. "HYPE"
};

export const HYPE_SIRINA = 1080;
export const HYPE_VISINA = 532;

const CX = 540;
const CY = 292;
const R = 196;
const A0 = 150; // stepeni, 0 = desno, u smeru kazaljke (SVG)
const RASPON = 240;
const LAMPICE = 15;

const rad = (a: number) => (a * Math.PI) / 180;
const tacka = (a: number, r: number) => [CX + Math.cos(rad(a)) * r, CY + Math.sin(rad(a)) * r] as const;
const luk = (a0: number, a1: number, r: number) => {
	const [x0, y0] = tacka(a0, r);
	const [x1, y1] = tacka(a1, r);
	return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`;
};
const boja = (h: number) => (h < 0.5 ? '#39ff88' : h < 0.8 ? '#ffe14d' : '#ff3b5c');

const useFont = () => {
	const [handle] = useState(() => delayRender('font'));
	useEffect(() => {
		const f = new FontFace('InterBlack', `url(${staticFile('clipper/Inter-Black.otf')})`);
		f.load()
			.then((ff) => {
				document.fonts.add(ff);
				continueRender(handle);
			})
			.catch(() => continueRender(handle));
	}, [handle]);
};

export const HypeTraka: React.FC<HypeProps> = ({vrednosti, video, oznaka}) => {
	useFont();
	const f = useCurrentFrame();
	const h = vrednosti.length ? vrednosti[Math.min(f, vrednosti.length - 1)] : 0;
	const max = h > 0.85;
	const treptaj = max && f % 4 < 2;
	const tres = max ? 3 * Math.sin(f * 2.3) : 0;
	const ugao = A0 + RASPON * h;
	const [nx, ny] = tacka(ugao, R - 34);

	return (
		<AbsoluteFill style={{backgroundColor: '#05030a', overflow: 'hidden', fontFamily: 'InterBlack, Inter, sans-serif'}}>
			<AbsoluteFill style={{transform: `scale(${1.04 + 0.1 * h})`}}>
				<OffthreadVideo src={staticFile(video)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
			</AbsoluteFill>
			{/* spoj sa kamerom iznad i senka za čitljivost brzinomera */}
			<AbsoluteFill
				style={{
					background:
						'linear-gradient(to bottom, rgba(5,3,10,0.85) 0%, rgba(5,3,10,0.15) 22%, rgba(5,3,10,0.1) 60%, rgba(5,3,10,0.55) 100%)',
				}}
			/>
			<AbsoluteFill style={{background: `radial-gradient(circle at ${CX}px ${CY}px, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) ${R + 60}px)`}} />
			{max ? <AbsoluteFill style={{boxShadow: `inset 0 0 ${60 + 40 * h}px rgba(255,40,80,${treptaj ? 0.9 : 0.5})`}} /> : null}

			<svg width={HYPE_SIRINA} height={HYPE_VISINA} style={{position: 'absolute', transform: `translate(${tres}px, ${-tres}px)`}}>
				{/* LED lampice za menjanje brzine */}
				{Array.from({length: LAMPICE}, (_, i) => {
					const x = CX + (i - (LAMPICE - 1) / 2) * 52;
					const upaljena = i < Math.round(h * LAMPICE);
					const c = treptaj ? '#3df2ff' : i < 6 ? '#39ff88' : i < 11 ? '#ffe14d' : '#ff3b5c';
					return (
						<g key={i}>
							{upaljena ? <circle cx={x} cy={44} r={20} fill={c} opacity={0.35} /> : null}
							<circle cx={x} cy={44} r={12} fill={upaljena ? c : '#ffffff'} opacity={upaljena ? 1 : 0.12} />
						</g>
					);
				})}

				{/* skala */}
				<path d={luk(A0, A0 + RASPON, R)} fill="none" stroke="#ffffff" strokeOpacity={0.14} strokeWidth={18} strokeLinecap="round" />
				<path d={luk(A0 + RASPON * 0.8, A0 + RASPON, R + 22)} fill="none" stroke="#ff3b5c" strokeOpacity={0.8} strokeWidth={5} />
				{h > 0.005 ? (
					<>
						<path d={luk(A0, ugao, R)} fill="none" stroke={boja(h)} strokeOpacity={0.3} strokeWidth={40} strokeLinecap="round" />
						<path d={luk(A0, ugao, R)} fill="none" stroke={boja(h)} strokeWidth={18} strokeLinecap="round" />
					</>
				) : null}
				{Array.from({length: 11}, (_, i) => {
					const a = A0 + (RASPON * i) / 10;
					const [x0, y0] = tacka(a, R - 26);
					const [x1, y1] = tacka(a, R - (i % 2 === 0 ? 50 : 40));
					const [lx, ly] = tacka(a, R - 78);
					return (
						<g key={i}>
							<line x1={x0} y1={y0} x2={x1} y2={y1} stroke="#ffffff" strokeOpacity={0.8} strokeWidth={i % 2 === 0 ? 5 : 3} />
							{i % 2 === 0 && i > 0 && i < 10 ? (
								<text x={lx} y={ly + 9} fill="#ffffff" fillOpacity={0.75} fontSize={26} textAnchor="middle" fontFamily="InterBlack, Inter, sans-serif">
									{i * 20}
								</text>
							) : null}
						</g>
					);
				})}

				{/* kazaljka */}
				<line x1={CX} y1={CY} x2={nx} y2={ny} stroke={boja(h)} strokeOpacity={0.4} strokeWidth={16} strokeLinecap="round" />
				<line x1={CX} y1={CY} x2={nx} y2={ny} stroke="#ffffff" strokeWidth={7} strokeLinecap="round" />
				<circle cx={CX} cy={CY} r={18} fill="#ffffff" />
				<circle cx={CX} cy={CY} r={8} fill={boja(h)} />

				{/* broj */}
				<text
					x={CX}
					y={CY + 112}
					fill={treptaj ? '#3df2ff' : '#ffffff'}
					fontSize={88}
					textAnchor="middle"
					fontFamily="InterBlack, Inter, sans-serif"
					stroke="#000000"
					strokeWidth={6}
					paintOrder="stroke"
				>
					{Math.round(h * 200)}
				</text>
				<text x={CX} y={CY + 150} fill={boja(h)} fontSize={28} letterSpacing={6} textAnchor="middle" fontFamily="InterBlack, Inter, sans-serif">
					{max ? 'MAX ' + oznaka : oznaka}
				</text>
			</svg>
		</AbsoluteFill>
	);
};
