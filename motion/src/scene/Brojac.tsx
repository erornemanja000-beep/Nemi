import {AbsoluteFill, Easing, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, FONT} from '../theme';
import {Oznaka, Pozadina, Zvuk} from '../ui';

// Tehnika 3: brojač sa trakom nivoa, pa reč koja se "dešifruje" iz nula i jedinica (scramble).
const CILJ = 600;
const SEGMENTI = 12;
const POCETAK = 6;
const KRAJ = 46;
const REC = 'KADROVA';

const vrednost = (f: number) =>
	interpolate(f, [POCETAK, KRAJ], [0, CILJ], {
		easing: Easing.out(Easing.cubic),
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

const popunjeno = (f: number) => Math.floor((vrednost(f) / CILJ) * SEGMENTI);

// kadrovi u kojima se puni novi segment trake: tu ide klik
const KLIKOVI: number[] = [];
for (let f = POCETAK; f <= KRAJ; f++) {
	if (popunjeno(f) > popunjeno(f - 1)) KLIKOVI.push(f);
}

export const Brojac: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	const v = vrednost(f);
	const pun = popunjeno(f);
	const skok = spring({frame: f - KRAJ, fps, config: {damping: 9, stiffness: 200}});

	const slova = REC.split('').map((slovo, j) => {
		const resenoNa = KRAJ + 2 + j * 2;
		if (f < KRAJ - 2) return {s: ' ', reseno: false};
		if (f >= resenoNa) return {s: slovo, reseno: true};
		// menja se na svaka 2 kadra da bi oko stiglo da vidi cifre
		return {s: random(`${j}-${Math.floor(f / 2)}`) > 0.5 ? '1' : '0', reseno: false};
	});

	const podnaslov = interpolate(f, [64, 72], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill>
			<Pozadina />
			<AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
				<div
					style={{
						fontFamily: FONT.mono,
						fontWeight: 800,
						fontSize: 300,
						lineHeight: 1,
						color: pun === SEGMENTI ? C.red : C.white,
						// kad stigne do cilja, broj "skoči" pa se slegne
						transform: `scale(${f >= KRAJ ? 1 + 0.12 * (1 - skok) : 1})`,
						fontVariantNumeric: 'tabular-nums',
					}}
				>
					{Math.round(v)}
				</div>
				<div style={{display: 'flex', gap: 10, marginTop: 28}}>
					{Array.from({length: SEGMENTI}, (_, i) => (
						<div
							key={i}
							style={{
								width: 52,
								height: 26,
								border: `3px solid ${i < pun ? C.red : 'rgba(244,239,232,0.25)'}`,
								background: i < pun ? C.red : 'transparent',
							}}
						/>
					))}
				</div>
				<div
					style={{
						display: 'flex',
						gap: 6,
						marginTop: 46,
						fontFamily: FONT.mono,
						fontWeight: 700,
						fontSize: 92,
						letterSpacing: '0.08em',
					}}
				>
					{slova.map((x, j) => (
						<span key={j} style={{color: x.reseno ? C.white : C.teal, minWidth: 62, textAlign: 'center'}}>
							{x.s}
						</span>
					))}
				</div>
				<div
					style={{
						marginTop: 24,
						fontFamily: FONT.thin,
						fontWeight: 300,
						fontSize: 44,
						color: C.white,
						opacity: podnaslov * 0.8,
					}}
				>
					= 20 sekundi videa na 30 fps
				</div>
			</AbsoluteFill>
			<Oznaka tekst="02 / BROJAČ + SCRAMBLE" />
			{KLIKOVI.map((k) => (
				<Zvuk key={k} fajl="tick.wav" od={k} jacina={0.35} />
			))}
			<Zvuk fajl="hit.wav" od={KRAJ} jacina={0.7} />
		</AbsoluteFill>
	);
};
