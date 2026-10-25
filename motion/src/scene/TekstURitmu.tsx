import {AbsoluteFill, interpolate, random, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {C, FONT} from '../theme';
import {Oznaka, Pozadina, Zvuk} from '../ui';

// Tehnika 1: reči ulaze jedna po jedna, na osminu takta; ključna reč pada tačno na udarac.
const OBICNE = [
	{tekst: 'Svaki', od: 8},
	{tekst: 'rez', od: 15},
	{tekst: 'pada', od: 23},
	{tekst: 'na', od: 30},
];
const KLJUCNA = {tekst: 'UDARAC.', od: 45};

export const TekstURitmu: React.FC = () => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();

	// ključna reč: pad iz 3D (rotateX) sa malo odskoka
	const k = spring({frame: f - KLJUCNA.od, fps, config: {damping: 11, stiffness: 170, mass: 0.6}});
	const blesak = interpolate(f, [KLJUCNA.od, KLJUCNA.od + 1, KLJUCNA.od + 7], [0, 0.45, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	// trešenje kamere 7 kadrova posle udarca
	const t = f - KLJUCNA.od;
	const snaga = t >= 0 && t < 7 ? 1 - t / 7 : 0;
	const dx = (random(`x${f}`) - 0.5) * 28 * snaga;
	const dy = (random(`y${f}`) - 0.5) * 18 * snaga;

	// na kraju scene sve lagano raste dok prelaz ne pokrije ekran
	const izlaz = interpolate(f, [85, 105], [1, 1.08], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

	return (
		<AbsoluteFill>
			<Pozadina />
			<AbsoluteFill
				style={{
					alignItems: 'center',
					justifyContent: 'center',
					perspective: 1400,
					transform: `translate(${dx}px, ${dy}px) scale(${izlaz})`,
				}}
			>
				<div style={{display: 'flex', gap: 30, marginBottom: 10}}>
					{OBICNE.map((r) => {
						const p = spring({frame: f - r.od, fps, config: {damping: 200}, durationInFrames: 10});
						return (
							<span
								key={r.tekst}
								style={{
									fontFamily: FONT.thin,
									fontWeight: 300,
									fontSize: 96,
									color: C.white,
									opacity: p,
									transform: `translateY(${(1 - p) * 40}px)`,
									filter: `blur(${(1 - p) * 10}px)`,
								}}
							>
								{r.tekst}
							</span>
						);
					})}
				</div>
				<div
					style={{
						fontFamily: FONT.heavy,
						fontWeight: 900,
						fontSize: 270,
						lineHeight: 1,
						letterSpacing: '-0.03em',
						color: C.red,
						opacity: Math.min(1, k * 3),
						transform: `rotateX(${interpolate(k, [0, 1], [80, 0])}deg) scale(${interpolate(k, [0, 1], [1.8, 1])}) rotateY(${Math.sin(f / 18) * 6}deg)`,
						textShadow: `0 18px 60px rgba(229, 50, 45, 0.35)`,
					}}
				>
					{KLJUCNA.tekst}
				</div>
			</AbsoluteFill>
			<AbsoluteFill style={{background: C.white, opacity: blesak}} />
			<Oznaka tekst="01 / TEKST U RITMU" />
			{OBICNE.map((r) => (
				<Zvuk key={r.tekst} fajl="tick.wav" od={r.od} jacina={0.5} />
			))}
			<Zvuk fajl="hit.wav" od={KLJUCNA.od} />
		</AbsoluteFill>
	);
};
