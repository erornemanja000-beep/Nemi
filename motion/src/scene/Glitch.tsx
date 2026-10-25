import {AbsoluteFill, interpolate, random, useCurrentFrame} from 'remotion';
import {C, FONT} from '../theme';
import {Oznaka, Pozadina, Zvuk} from '../ui';

// Tehnika 4: glitch. Crvena i tirkizna kopija se razilaze (RGB split), a vodoravne trake se pomeraju.
const TEKST = 'GOTOVO.';
const TRAKE = 7;
export const UDARI_GLITCHA = [0, 35];

const jacina = (f: number) => {
	if (f < 10) return 1 - f / 10;
	if (f >= 35 && f < 41) return 1;
	return 0;
};

const stil: React.CSSProperties = {
	position: 'absolute',
	left: 0,
	right: 0,
	textAlign: 'center',
	fontFamily: FONT.heavy,
	fontWeight: 900,
	fontSize: 300,
	lineHeight: 1,
	letterSpacing: '-0.03em',
	whiteSpace: 'nowrap',
};

export const Glitch: React.FC = () => {
	const f = useCurrentFrame();
	const g = jacina(f);
	const pomak = (kljuc: string) => (random(`${kljuc}${f}`) - 0.5) * 2;
	const kraj = interpolate(f, [50, 60], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

	const sloj = (boja: string, dx: number, dodatak: React.CSSProperties = {}) =>
		Array.from({length: g > 0 ? TRAKE : 1}, (_, i) => {
			const vrh = (i / TRAKE) * 100;
			const dno = 100 - ((i + 1) / TRAKE) * 100;
			const trakaDx = g > 0 ? pomak(`traka${i}`) * 90 * g : 0;
			return (
				<div
					key={i}
					style={{
						...stil,
						...dodatak,
						color: boja,
						transform: `translateX(${dx + trakaDx}px)`,
						clipPath: g > 0 ? `inset(${vrh}% 0 ${dno}% 0)` : undefined,
					}}
				>
					{TEKST}
				</div>
			);
		});

	return (
		<AbsoluteFill>
			<Pozadina />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
				<div style={{position: 'relative', width: '100%', height: 300}}>
					{/* crvena uvek ide desno, tirkizna levo, da se obe boje vide sa strane belog teksta */}
					{g > 0 && sloj(C.red, (14 + Math.abs(pomak('r')) * 22) * g, {opacity: 0.95})}
					{g > 0 && sloj(C.teal, -(14 + Math.abs(pomak('t')) * 22) * g, {opacity: 0.95})}
					{sloj(C.white, 0)}
				</div>
			</AbsoluteFill>
			<Oznaka tekst="03 / GLITCH" />
			<AbsoluteFill style={{background: C.black, opacity: kraj}} />
			{UDARI_GLITCHA.map((u) => (
				<Zvuk key={u} fajl="glitch.wav" od={u} jacina={0.8} />
			))}
		</AbsoluteFill>
	);
};
