import {
	AbsoluteFill,
	continueRender,
	delayRender,
	Img,
	interpolate,
	random,
	spring,
	staticFile,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

// Boje sa nemistudio.at
export const N = {
	ink: '#0b0b0c',
	ink2: '#121315',
	bone: '#efeae2',
	signal: '#ff5a24',
	plava: '#3fd6c6',
};
export const SANS = "'Inter Display', 'Inter', sans-serif";
export const SERIF = "'Instrument Serif', serif";
export const MONO = "'JetBrains Mono', monospace";

// Instrument Serif (kurziv) za istaknute reči, kao na sajtu; render čeka dok se font ne učita.
const cekaj = delayRender('Instrument Serif');
const font = new FontFace('Instrument Serif', `url(${staticFile('fonts/instrument-serif-italic.woff2')})`, {style: 'italic'});
font
	.load()
	.then(() => {
		document.fonts.add(font);
		continueRender(cekaj);
	})
	.catch(() => continueRender(cekaj));

export const blenderKadar = (b: number) => staticFile(`wuerfel/render/${String(b).padStart(4, '0')}.png`);

// ---------------------------------------------------------------- tekst koji iskoči i nestane
export type Deo = {t: string; istaknuto?: boolean};

export const Iskace: React.FC<{delovi: Deo[]; od: number; do: number; y: number; velicina?: number; glitch?: boolean}> = ({
	delovi,
	od,
	do: kraj,
	y,
	velicina = 104,
	glitch = false,
}) => {
	const f = useCurrentFrame();
	const {fps} = useVideoConfig();
	if (f < od || f > kraj) return null;
	const izlaz = interpolate(f, [kraj - 8, kraj], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	// glitch: prvih 6 kadrova reči drhte i razdvajaju se boje
	const g = glitch ? interpolate(f, [od, od + 6], [1, 0], {extrapolateRight: 'clamp'}) : 0;
	return (
		<div
			style={{
				position: 'absolute',
				top: y,
				left: 90,
				right: 160,
				display: 'flex',
				flexWrap: 'wrap',
				justifyContent: 'center',
				alignItems: 'baseline',
				columnGap: velicina * 0.26,
				perspective: 900,
				opacity: 1 - izlaz,
				transform: `translateY(${-izlaz * 40}px) scale(${1 - izlaz * 0.08})`,
				filter: `blur(${izlaz * 8}px)`,
			}}
		>
			{delovi.map((d, i) => {
				const p = spring({frame: f - od - i * 3, fps, config: {damping: 12, stiffness: 190, mass: 0.6}});
				const dx = g > 0 ? (random(`gx${i}${f}`) - 0.5) * 40 * g : 0;
				return (
					<span
						key={i}
						style={{
							display: 'inline-block',
							fontFamily: d.istaknuto ? SERIF : SANS,
							fontStyle: d.istaknuto ? 'italic' : 'normal',
							fontWeight: d.istaknuto ? 400 : 800,
							fontSize: d.istaknuto ? velicina * 1.18 : velicina,
							lineHeight: 1.05,
							letterSpacing: d.istaknuto ? '-0.01em' : '-0.03em',
							color: d.istaknuto ? N.signal : N.bone,
							opacity: Math.min(1, p * 2),
							transform: `translateX(${dx}px) rotateX(${(1 - p) * 85}deg) scale(${1 + (1 - p) * 0.5})`,
							textShadow: g > 0 ? `${6 * g}px 0 ${N.signal}, ${-6 * g}px 0 ${N.plava}` : '0 10px 40px rgba(0,0,0,0.45)',
						}}
					>
						{d.t}
					</span>
				);
			})}
		</div>
	);
};

// ---------------------------------------------------------------- pikselni lik iz Pixelorama-e
export const Lik: React.FC<{kadar: number; x: number; y: number; razmera?: number; okrenut?: boolean}> = ({
	kadar,
	x,
	y,
	razmera = 10,
	okrenut = false,
}) => (
	<div style={{position: 'absolute', left: x, top: y, width: 16 * razmera, height: 18 * razmera}}>
		<div
			style={{
				position: 'absolute',
				left: '15%',
				right: '15%',
				bottom: -razmera,
				height: razmera * 2,
				borderRadius: '50%',
				background: 'rgba(0,0,0,0.45)',
				filter: 'blur(4px)',
			}}
		/>
		<Img
			src={staticFile(`wuerfel/lik_${kadar}.png`)}
			style={{
				width: '100%',
				height: '100%',
				imageRendering: 'pixelated',
				transform: okrenut ? 'scaleX(-1)' : undefined,
			}}
		/>
	</div>
);

// ---------------------------------------------------------------- CSS 3D kocka (6 strana)
export const Kocka3D: React.FC<{velicina: number; rx: number; ry: number}> = ({velicina: s, rx, ry}) => {
	const strane: [string, string][] = [
		[`translateZ(${s / 2}px)`, N.signal],
		[`rotateY(180deg) translateZ(${s / 2}px)`, '#c8441c'],
		[`rotateY(90deg) translateZ(${s / 2}px)`, '#e04e1f'],
		[`rotateY(-90deg) translateZ(${s / 2}px)`, '#d9481c'],
		[`rotateX(90deg) translateZ(${s / 2}px)`, '#ff8a5c'],
		[`rotateX(-90deg) translateZ(${s / 2}px)`, '#a83612'],
	];
	return (
		<div style={{width: s, height: s, perspective: 1200}}>
			<div
				style={{
					position: 'relative',
					width: s,
					height: s,
					transformStyle: 'preserve-3d',
					transform: `rotateX(${rx}deg) rotateY(${ry}deg)`,
				}}
			>
				{strane.map(([t, b], i) => (
					<div
						key={i}
						style={{
							position: 'absolute',
							inset: 0,
							background: b,
							transform: t,
							boxShadow: 'inset 0 0 0 2px rgba(0,0,0,0.12)',
							backfaceVisibility: 'hidden',
						}}
					/>
				))}
			</div>
		</div>
	);
};

// ---------------------------------------------------------------- pikselni mozaik preko celog ekrana
export const Mozaik: React.FC<{trajanje: number}> = ({trajanje}) => {
	const f = useCurrentFrame();
	const kol = 9;
	const red = 16;
	const v = 120;
	const pola = Math.floor(trajanje / 2);
	const boje = [N.signal, N.bone, N.ink, N.ink2, N.signal];
	const polja = [];
	for (let i = 0; i < kol * red; i++) {
		// pojavljuju se od dna ka vrhu, pa nestaju istim redom
		const r = Math.floor(i / kol);
		const ulaz = Math.floor(((red - 1 - r) / red) * (pola - 2) + random(`u${i}`) * 3);
		const izlaz = pola + 1 + Math.floor(((red - 1 - r) / red) * (pola - 2) + random(`i${i}`) * 3);
		if (f < ulaz || f >= izlaz) continue;
		polja.push(
			<div
				key={i}
				style={{
					position: 'absolute',
					left: (i % kol) * v,
					top: r * v,
					width: v,
					height: v,
					background: boje[Math.floor(random(`b${i}`) * boje.length)],
				}}
			/>,
		);
	}
	return <AbsoluteFill>{polja}</AbsoluteFill>;
};

// ---------------------------------------------------------------- glitch na slici iz Blender-a
export const GlitchSlika: React.FC<{src: string; jacina: number}> = ({src, jacina}) => {
	const f = useCurrentFrame();
	const trake = 10;
	return (
		<AbsoluteFill>
			{Array.from({length: trake}, (_, i) => {
				const dx = (random(`t${i}${f}`) - 0.5) * 160 * jacina;
				return (
					<AbsoluteFill key={i} style={{clipPath: `inset(${(i / trake) * 100}% 0 ${100 - ((i + 1) / trake) * 100}% 0)`}}>
						<Img src={src} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', transform: `translateX(${dx + 18 * jacina}px)`, opacity: 0.8, filter: 'sepia(1) saturate(6) hue-rotate(-30deg)', mixBlendMode: 'screen'}} />
						<Img src={src} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', transform: `translateX(${dx - 18 * jacina}px)`, opacity: 0.8, filter: 'sepia(1) saturate(6) hue-rotate(140deg)', mixBlendMode: 'screen'}} />
						<Img src={src} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', transform: `translateX(${dx}px)`}} />
					</AbsoluteFill>
				);
			})}
		</AbsoluteFill>
	);
};
